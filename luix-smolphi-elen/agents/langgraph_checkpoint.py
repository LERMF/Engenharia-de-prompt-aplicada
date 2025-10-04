#!/usr/bin/env python3
"""
LangGraph-0.12.0-rc CheckpointAsyncSQLite Implementation
Target: <30ms checkpoint latency
"""

import asyncio
import aiosqlite
import time
import json
import hashlib
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path
import os


@dataclass
class Checkpoint:
    """Agent state checkpoint"""
    checkpoint_id: str
    agent_id: str
    state: Dict[str, Any]
    timestamp: float
    parent_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CheckpointAsyncSQLite:
    """
    Ultra-fast async SQLite checkpointing for LangGraph
    Target: <30ms write latency
    """
    
    def __init__(self, db_path: str = "/var/lib/luix/checkpoints.db"):
        self.db_path = db_path
        self.db: Optional[aiosqlite.Connection] = None
        self.checkpoint_count = 0
        self.avg_write_latency_ms = 0.0
        self.avg_read_latency_ms = 0.0
        
        # Performance optimizations
        self.target_latency_ms = 30.0
        self.batch_size = 10
        self._write_buffer: List[Checkpoint] = []
    
    async def initialize(self):
        """Initialize database with optimized schema"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Connect with optimizations
        self.db = await aiosqlite.connect(self.db_path)
        
        # Enable WAL mode for concurrent reads/writes
        await self.db.execute("PRAGMA journal_mode=WAL")
        await self.db.execute("PRAGMA synchronous=NORMAL")  # Faster writes
        await self.db.execute("PRAGMA cache_size=-64000")   # 64MB cache
        await self.db.execute("PRAGMA temp_store=MEMORY")
        await self.db.execute("PRAGMA mmap_size=268435456") # 256MB mmap
        
        # Create optimized schema
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                checkpoint_id TEXT PRIMARY KEY,
                agent_id TEXT NOT NULL,
                state_json TEXT NOT NULL,
                timestamp REAL NOT NULL,
                parent_id TEXT,
                metadata_json TEXT,
                state_hash TEXT
            )
        """)
        
        # Create indexes for fast lookups
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent_timestamp 
            ON checkpoints(agent_id, timestamp DESC)
        """)
        
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_parent 
            ON checkpoints(parent_id)
        """)
        
        await self.db.commit()
    
    async def close(self):
        """Close database connection"""
        if self._write_buffer:
            await self.flush()
        if self.db:
            await self.db.close()
    
    def _generate_checkpoint_id(self, agent_id: str, timestamp: float) -> str:
        """Generate unique checkpoint ID"""
        data = f"{agent_id}-{timestamp}".encode()
        return hashlib.sha256(data).hexdigest()[:16]
    
    def _hash_state(self, state: Dict[str, Any]) -> str:
        """Generate hash of state for deduplication"""
        state_str = json.dumps(state, sort_keys=True)
        return hashlib.md5(state_str.encode()).hexdigest()
    
    async def save_checkpoint(self, checkpoint: Checkpoint) -> float:
        """
        Save checkpoint to database
        Returns: write latency in milliseconds
        """
        start_time = time.perf_counter()
        
        # Generate hash for deduplication
        state_hash = self._hash_state(checkpoint.state)
        
        # Prepare data
        state_json = json.dumps(checkpoint.state)
        metadata_json = json.dumps(checkpoint.metadata) if checkpoint.metadata else None
        
        # Insert checkpoint
        await self.db.execute("""
            INSERT OR REPLACE INTO checkpoints 
            (checkpoint_id, agent_id, state_json, timestamp, parent_id, metadata_json, state_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            checkpoint.checkpoint_id,
            checkpoint.agent_id,
            state_json,
            checkpoint.timestamp,
            checkpoint.parent_id,
            metadata_json,
            state_hash
        ))
        
        await self.db.commit()
        
        # Calculate latency
        latency_ms = (time.perf_counter() - start_time) * 1000
        
        # Update stats
        self.checkpoint_count += 1
        self.avg_write_latency_ms = (
            (self.avg_write_latency_ms * (self.checkpoint_count - 1) + latency_ms)
            / self.checkpoint_count
        )
        
        return latency_ms
    
    async def load_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """
        Load checkpoint from database
        Returns: checkpoint and read latency
        """
        start_time = time.perf_counter()
        
        async with self.db.execute("""
            SELECT checkpoint_id, agent_id, state_json, timestamp, parent_id, metadata_json
            FROM checkpoints
            WHERE checkpoint_id = ?
        """, (checkpoint_id,)) as cursor:
            row = await cursor.fetchone()
        
        latency_ms = (time.perf_counter() - start_time) * 1000
        self.avg_read_latency_ms = (
            (self.avg_read_latency_ms + latency_ms) / 2
        )
        
        if not row:
            return None
        
        return Checkpoint(
            checkpoint_id=row[0],
            agent_id=row[1],
            state=json.loads(row[2]),
            timestamp=row[3],
            parent_id=row[4],
            metadata=json.loads(row[5]) if row[5] else None
        )
    
    async def load_latest_checkpoint(self, agent_id: str) -> Optional[Checkpoint]:
        """Load most recent checkpoint for agent"""
        async with self.db.execute("""
            SELECT checkpoint_id, agent_id, state_json, timestamp, parent_id, metadata_json
            FROM checkpoints
            WHERE agent_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (agent_id,)) as cursor:
            row = await cursor.fetchone()
        
        if not row:
            return None
        
        return Checkpoint(
            checkpoint_id=row[0],
            agent_id=row[1],
            state=json.loads(row[2]),
            timestamp=row[3],
            parent_id=row[4],
            metadata=json.loads(row[5]) if row[5] else None
        )
    
    async def list_checkpoints(
        self, 
        agent_id: str, 
        limit: int = 10
    ) -> List[Checkpoint]:
        """List recent checkpoints for agent"""
        async with self.db.execute("""
            SELECT checkpoint_id, agent_id, state_json, timestamp, parent_id, metadata_json
            FROM checkpoints
            WHERE agent_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (agent_id, limit)) as cursor:
            rows = await cursor.fetchall()
        
        return [
            Checkpoint(
                checkpoint_id=row[0],
                agent_id=row[1],
                state=json.loads(row[2]),
                timestamp=row[3],
                parent_id=row[4],
                metadata=json.loads(row[5]) if row[5] else None
            )
            for row in rows
        ]
    
    async def flush(self):
        """Flush write buffer"""
        if self._write_buffer:
            await self.db.commit()
            self._write_buffer.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get checkpoint statistics"""
        return {
            "total_checkpoints": self.checkpoint_count,
            "avg_write_latency_ms": round(self.avg_write_latency_ms, 2),
            "avg_read_latency_ms": round(self.avg_read_latency_ms, 2),
            "target_latency_ms": self.target_latency_ms,
            "meets_target": self.avg_write_latency_ms < self.target_latency_ms,
            "db_path": self.db_path
        }


async def main():
    """Test checkpoint system"""
    print("🔄 Testing LangGraph CheckpointAsyncSQLite\n")
    
    # Initialize
    checkpoint_db = CheckpointAsyncSQLite("/tmp/test_checkpoints.db")
    await checkpoint_db.initialize()
    
    try:
        # Create test checkpoints
        agent_id = "gemini-agent-1"
        latencies = []
        
        for i in range(5):
            checkpoint = Checkpoint(
                checkpoint_id=checkpoint_db._generate_checkpoint_id(agent_id, time.time()),
                agent_id=agent_id,
                state={
                    "step": i,
                    "memory": f"state_{i}",
                    "context": ["item1", "item2", "item3"]
                },
                timestamp=time.time(),
                parent_id=None,
                metadata={"iteration": i, "phase": "test"}
            )
            
            latency = await checkpoint_db.save_checkpoint(checkpoint)
            latencies.append(latency)
            print(f"✅ Checkpoint {i+1} saved: {latency:.2f}ms")
        
        print(f"\n📊 Average write latency: {sum(latencies)/len(latencies):.2f}ms")
        
        # Load latest checkpoint
        print("\n📥 Loading latest checkpoint...")
        latest = await checkpoint_db.load_latest_checkpoint(agent_id)
        if latest:
            print(f"   Step: {latest.state['step']}")
            print(f"   Timestamp: {latest.timestamp}")
        
        # List all checkpoints
        print(f"\n📋 All checkpoints for {agent_id}:")
        checkpoints = await checkpoint_db.list_checkpoints(agent_id)
        for cp in checkpoints:
            print(f"   - {cp.checkpoint_id}: step {cp.state['step']}")
        
        # Show stats
        stats = checkpoint_db.get_stats()
        print(f"\n📊 Checkpoint Stats:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        if stats["meets_target"]:
            print("\n✅ Meeting <30ms target!")
        else:
            print(f"\n⚠️  Slower than target ({stats['avg_write_latency_ms']:.2f}ms vs 30ms)")
    
    finally:
        await checkpoint_db.close()
        # Cleanup test database
        import os
        if os.path.exists("/tmp/test_checkpoints.db"):
            os.remove("/tmp/test_checkpoints.db")


if __name__ == "__main__":
    asyncio.run(main())
