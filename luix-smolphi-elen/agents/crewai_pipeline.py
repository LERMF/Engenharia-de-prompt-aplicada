#!/usr/bin/env python3
"""
CrewAI-0.36.0 Pipeline-of-Pipelines with Gemini Driver
Multi-agent orchestration for LUIX-SMOLPHI-ELEN
"""

import asyncio
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import sys
import os

# Import local modules
sys.path.insert(0, os.path.dirname(__file__))
from gemini_driver import GeminiDriver, GeminiRequest
from smollm_brain import SmolLMBrain
from langgraph_checkpoint import CheckpointAsyncSQLite, Checkpoint


class AgentRole(Enum):
    """Agent role definitions"""
    OPTIMIZER = "optimizer"      # System optimization
    SECURITY = "security"        # CVE scanning, security
    BUILDER = "builder"          # ISO building
    MONITOR = "monitor"          # Performance monitoring
    DISTILLER = "distiller"      # Model distillation


@dataclass
class Task:
    """Agent task"""
    task_id: str
    description: str
    role: AgentRole
    priority: int = 1
    context: Optional[Dict[str, Any]] = None
    

@dataclass
class TaskResult:
    """Task execution result"""
    task_id: str
    role: AgentRole
    result: str
    success: bool
    latency_ms: float
    tokens_used: int
    checkpoint_id: Optional[str] = None


class Agent:
    """Individual AI agent with specific role"""
    
    def __init__(
        self,
        role: AgentRole,
        gemini_driver: GeminiDriver,
        smollm_brain: SmolLMBrain,
        checkpoint_db: CheckpointAsyncSQLite
    ):
        self.role = role
        self.gemini = gemini_driver
        self.smollm = smollm_brain
        self.checkpoint_db = checkpoint_db
        self.task_count = 0
    
    def _get_role_prompt(self) -> str:
        """Get role-specific system prompt"""
        prompts = {
            AgentRole.OPTIMIZER: "You are a Linux system optimizer. Focus on boot time, RAM usage, and performance.",
            AgentRole.SECURITY: "You are a security expert. Scan for CVEs, vulnerabilities, and security issues.",
            AgentRole.BUILDER: "You are an ISO builder specialist. Focus on minimal, reproducible builds.",
            AgentRole.MONITOR: "You are a system monitor. Track metrics, detect anomalies, report issues.",
            AgentRole.DISTILLER: "You are a model distillation expert. Transfer knowledge from large to small models."
        }
        return prompts.get(self.role, "You are a helpful AI assistant.")
    
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute a task using Gemini or SmolLM"""
        start_time = time.perf_counter()
        
        # Build prompt with role context
        role_context = self._get_role_prompt()
        full_context = f"{role_context}\n\nTask: {task.description}"
        if task.context:
            full_context += f"\nContext: {task.context}"
        
        # Decide whether to use Gemini or SmolLM
        use_smollm = self.gemini.should_fallback_to_smollm()
        
        if use_smollm:
            # Use SmolLM for simple tasks to save quota
            response = self.smollm.generate(task.description, context=role_context)
            result_text = response["text"]
            tokens_used = response["tokens"]
        else:
            # Use Gemini for complex reasoning
            request = GeminiRequest(
                prompt=task.description,
                context=full_context
            )
            response = await self.gemini.generate(request)
            result_text = response.text
            tokens_used = response.tokens_used
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        # Save checkpoint
        checkpoint = Checkpoint(
            checkpoint_id=f"{self.role.value}-{task.task_id}",
            agent_id=f"agent-{self.role.value}",
            state={
                "task_id": task.task_id,
                "result": result_text,
                "latency_ms": latency_ms,
                "tokens_used": tokens_used
            },
            timestamp=time.time(),
            metadata={"role": self.role.value, "priority": task.priority}
        )
        await self.checkpoint_db.save_checkpoint(checkpoint)
        
        self.task_count += 1
        
        return TaskResult(
            task_id=task.task_id,
            role=self.role,
            result=result_text,
            success=True,
            latency_ms=latency_ms,
            tokens_used=tokens_used,
            checkpoint_id=checkpoint.checkpoint_id
        )


class Pipeline:
    """Single pipeline of sequential tasks"""
    
    def __init__(self, name: str, tasks: List[Task]):
        self.name = name
        self.tasks = tasks
        self.results: List[TaskResult] = []
    
    async def execute(self, agent: Agent) -> List[TaskResult]:
        """Execute all tasks in pipeline"""
        print(f"  🔄 Executing pipeline: {self.name}")
        results = []
        
        for task in self.tasks:
            result = await agent.execute_task(task)
            results.append(result)
            print(f"    ✅ Task {task.task_id}: {result.latency_ms:.1f}ms, {result.tokens_used} tokens")
        
        self.results = results
        return results


class PipelineOfPipelines:
    """
    CrewAI Pipeline-of-Pipelines Architecture
    Orchestrates multiple pipelines with different agents
    """
    
    def __init__(self):
        self.pipelines: List[Pipeline] = []
        self.agents: Dict[AgentRole, Agent] = {}
        self.gemini: Optional[GeminiDriver] = None
        self.smollm: Optional[SmolLMBrain] = None
        self.checkpoint_db: Optional[CheckpointAsyncSQLite] = None
    
    async def initialize(self):
        """Initialize all components"""
        print("🚀 Initializing Pipeline-of-Pipelines...")
        
        # Initialize components
        self.gemini = GeminiDriver()
        await self.gemini.__aenter__()
        
        self.smollm = SmolLMBrain()
        
        self.checkpoint_db = CheckpointAsyncSQLite()
        await self.checkpoint_db.initialize()
        
        # Create agents for each role
        for role in AgentRole:
            self.agents[role] = Agent(
                role=role,
                gemini_driver=self.gemini,
                smollm_brain=self.smollm,
                checkpoint_db=self.checkpoint_db
            )
        
        print("✅ Initialization complete\n")
    
    async def shutdown(self):
        """Cleanup resources"""
        if self.checkpoint_db:
            await self.checkpoint_db.close()
        if self.gemini:
            await self.gemini.__aexit__(None, None, None)
    
    def add_pipeline(self, pipeline: Pipeline):
        """Add pipeline to orchestrator"""
        self.pipelines.append(pipeline)
    
    async def execute_all(self) -> Dict[str, Any]:
        """Execute all pipelines and aggregate results"""
        print("🔄 Executing all pipelines...\n")
        
        all_results = []
        total_latency = 0.0
        total_tokens = 0
        
        for pipeline in self.pipelines:
            # Determine which agent should handle this pipeline
            # For now, use first task's role
            role = pipeline.tasks[0].role
            agent = self.agents[role]
            
            results = await pipeline.execute(agent)
            all_results.extend(results)
            
            for result in results:
                total_latency += result.latency_ms
                total_tokens += result.tokens_used
        
        return {
            "pipelines_executed": len(self.pipelines),
            "tasks_completed": len(all_results),
            "total_latency_ms": total_latency,
            "total_tokens": total_tokens,
            "avg_latency_ms": total_latency / len(all_results) if all_results else 0,
            "results": all_results
        }


async def main():
    """Test Pipeline-of-Pipelines"""
    print("🎯 Testing CrewAI Pipeline-of-Pipelines\n")
    
    orchestrator = PipelineOfPipelines()
    await orchestrator.initialize()
    
    try:
        # Define pipelines
        
        # Pipeline 1: System Optimization
        optimization_pipeline = Pipeline(
            name="System Optimization",
            tasks=[
                Task(
                    task_id="opt-1",
                    description="List 3 ways to reduce Linux boot time under 5 seconds",
                    role=AgentRole.OPTIMIZER,
                    priority=1
                ),
                Task(
                    task_id="opt-2",
                    description="How to reduce idle RAM below 200MB?",
                    role=AgentRole.OPTIMIZER,
                    priority=1
                )
            ]
        )
        
        # Pipeline 2: Security Check
        security_pipeline = Pipeline(
            name="Security Audit",
            tasks=[
                Task(
                    task_id="sec-1",
                    description="What are the top 3 security considerations for a minimal Linux ISO?",
                    role=AgentRole.SECURITY,
                    priority=2
                )
            ]
        )
        
        # Pipeline 3: Build Process
        build_pipeline = Pipeline(
            name="ISO Build",
            tasks=[
                Task(
                    task_id="build-1",
                    description="What tools are needed for a reproducible ISO build?",
                    role=AgentRole.BUILDER,
                    priority=1
                )
            ]
        )
        
        # Add pipelines
        orchestrator.add_pipeline(optimization_pipeline)
        orchestrator.add_pipeline(security_pipeline)
        orchestrator.add_pipeline(build_pipeline)
        
        # Execute all
        summary = await orchestrator.execute_all()
        
        # Print summary
        print("\n" + "="*60)
        print("📊 EXECUTION SUMMARY")
        print("="*60)
        print(f"Pipelines executed: {summary['pipelines_executed']}")
        print(f"Tasks completed: {summary['tasks_completed']}")
        print(f"Total latency: {summary['total_latency_ms']:.1f}ms")
        print(f"Average latency: {summary['avg_latency_ms']:.1f}ms")
        print(f"Total tokens: {summary['total_tokens']}")
        
        # Show Gemini stats
        print("\n📈 Gemini Stats:")
        gemini_stats = orchestrator.gemini.get_stats()
        for key, value in gemini_stats.items():
            print(f"   {key}: {value}")
        
        # Show SmolLM stats
        print("\n📈 SmolLM Stats:")
        smollm_stats = orchestrator.smollm.get_stats()
        for key, value in smollm_stats.items():
            print(f"   {key}: {value}")
    
    finally:
        await orchestrator.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
