#!/usr/bin/env python3
"""
CRDT Merge Engine for Cross-Codespace Synchronization
Conflict-free replicated data types for distributed agent results
"""

import time
import json
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib


class CRDTType(Enum):
    """CRDT operation types"""
    GSET = "g-set"           # Grow-only set
    GCOUNTER = "g-counter"   # Grow-only counter
    LWWREG = "lww-register"  # Last-write-wins register
    ORSET = "or-set"         # Observed-remove set


@dataclass
class VectorClock:
    """Vector clock for causal ordering"""
    clock: Dict[str, int] = field(default_factory=dict)
    
    def increment(self, node_id: str):
        """Increment clock for a node"""
        self.clock[node_id] = self.clock.get(node_id, 0) + 1
    
    def merge(self, other: 'VectorClock'):
        """Merge with another vector clock"""
        for node_id, timestamp in other.clock.items():
            self.clock[node_id] = max(self.clock.get(node_id, 0), timestamp)
    
    def happens_before(self, other: 'VectorClock') -> bool:
        """Check if this event happens before another"""
        return all(
            self.clock.get(k, 0) <= other.clock.get(k, 0)
            for k in set(self.clock.keys()) | set(other.clock.keys())
        ) and self.clock != other.clock
    
    def concurrent(self, other: 'VectorClock') -> bool:
        """Check if events are concurrent"""
        return not self.happens_before(other) and not other.happens_before(self)


@dataclass
class CRDTOperation:
    """CRDT operation"""
    op_id: str
    node_id: str
    crdt_type: CRDTType
    operation: str  # "add", "remove", "set", "increment"
    value: Any
    timestamp: float
    vector_clock: VectorClock
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "op_id": self.op_id,
            "node_id": self.node_id,
            "crdt_type": self.crdt_type.value,
            "operation": self.operation,
            "value": self.value,
            "timestamp": self.timestamp,
            "vector_clock": self.vector_clock.clock
        }


class GrowOnlySet:
    """
    G-Set: Grow-only set CRDT
    Operations: add
    Guarantees: Convergence, commutativity
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.elements: Set[str] = set()
        self.vector_clock = VectorClock()
    
    def add(self, element: str) -> CRDTOperation:
        """Add element to set"""
        self.elements.add(element)
        self.vector_clock.increment(self.node_id)
        
        op_id = hashlib.md5(f"{self.node_id}-{time.time()}-{element}".encode()).hexdigest()[:16]
        
        return CRDTOperation(
            op_id=op_id,
            node_id=self.node_id,
            crdt_type=CRDTType.GSET,
            operation="add",
            value=element,
            timestamp=time.time(),
            vector_clock=VectorClock(clock=self.vector_clock.clock.copy())
        )
    
    def merge(self, operations: List[CRDTOperation]):
        """Merge operations from other nodes"""
        for op in operations:
            if op.crdt_type == CRDTType.GSET and op.operation == "add":
                self.elements.add(op.value)
                self.vector_clock.merge(op.vector_clock)
    
    def query(self) -> Set[str]:
        """Query current state"""
        return self.elements.copy()


class GrowOnlyCounter:
    """
    G-Counter: Grow-only counter CRDT
    Operations: increment
    Guarantees: Convergence, commutativity
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.counts: Dict[str, int] = {}
        self.vector_clock = VectorClock()
    
    def increment(self, amount: int = 1) -> CRDTOperation:
        """Increment counter"""
        self.counts[self.node_id] = self.counts.get(self.node_id, 0) + amount
        self.vector_clock.increment(self.node_id)
        
        op_id = hashlib.md5(f"{self.node_id}-{time.time()}".encode()).hexdigest()[:16]
        
        return CRDTOperation(
            op_id=op_id,
            node_id=self.node_id,
            crdt_type=CRDTType.GCOUNTER,
            operation="increment",
            value=amount,
            timestamp=time.time(),
            vector_clock=VectorClock(clock=self.vector_clock.clock.copy())
        )
    
    def merge(self, operations: List[CRDTOperation]):
        """Merge operations from other nodes"""
        for op in operations:
            if op.crdt_type == CRDTType.GCOUNTER:
                node = op.node_id
                self.counts[node] = max(self.counts.get(node, 0), self.counts.get(node, 0) + op.value)
                self.vector_clock.merge(op.vector_clock)
    
    def query(self) -> int:
        """Query current value"""
        return sum(self.counts.values())


class LastWriteWinsRegister:
    """
    LWW-Register: Last-write-wins register CRDT
    Operations: set
    Guarantees: Convergence (bias to latest timestamp)
    """
    
    def __init__(self, node_id: str, initial_value: Any = None):
        self.node_id = node_id
        self.value = initial_value
        self.timestamp = 0.0
        self.vector_clock = VectorClock()
    
    def set(self, value: Any) -> CRDTOperation:
        """Set register value"""
        timestamp = time.time()
        self.value = value
        self.timestamp = timestamp
        self.vector_clock.increment(self.node_id)
        
        op_id = hashlib.md5(f"{self.node_id}-{timestamp}".encode()).hexdigest()[:16]
        
        return CRDTOperation(
            op_id=op_id,
            node_id=self.node_id,
            crdt_type=CRDTType.LWWREG,
            operation="set",
            value=value,
            timestamp=timestamp,
            vector_clock=VectorClock(clock=self.vector_clock.clock.copy())
        )
    
    def merge(self, operations: List[CRDTOperation]):
        """Merge operations from other nodes"""
        for op in operations:
            if op.crdt_type == CRDTType.LWWREG:
                # Take value with latest timestamp
                if op.timestamp > self.timestamp:
                    self.value = op.value
                    self.timestamp = op.timestamp
                self.vector_clock.merge(op.vector_clock)
    
    def query(self) -> Any:
        """Query current value"""
        return self.value


class CRDTMergeEngine:
    """
    CRDT Merge Engine for cross-codespace synchronization
    Handles multiple CRDT types and distributed state merging
    """
    
    def __init__(self, node_id: str = "codespace-1"):
        self.node_id = node_id
        self.crdts: Dict[str, Any] = {}
        self.operation_log: List[CRDTOperation] = []
    
    def create_gset(self, name: str) -> GrowOnlySet:
        """Create a grow-only set"""
        crdt = GrowOnlySet(self.node_id)
        self.crdts[name] = crdt
        return crdt
    
    def create_gcounter(self, name: str) -> GrowOnlyCounter:
        """Create a grow-only counter"""
        crdt = GrowOnlyCounter(self.node_id)
        self.crdts[name] = crdt
        return crdt
    
    def create_lww_register(self, name: str, initial_value: Any = None) -> LastWriteWinsRegister:
        """Create a last-write-wins register"""
        crdt = LastWriteWinsRegister(self.node_id, initial_value)
        self.crdts[name] = crdt
        return crdt
    
    def apply_operation(self, operation: CRDTOperation, crdt_name: str):
        """Apply an operation and log it"""
        if crdt_name in self.crdts:
            self.crdts[crdt_name].merge([operation])
        self.operation_log.append(operation)
    
    def merge_from_remote(self, remote_operations: List[Dict[str, Any]]):
        """Merge operations from remote codespace"""
        for op_dict in remote_operations:
            # Reconstruct operation
            op = CRDTOperation(
                op_id=op_dict["op_id"],
                node_id=op_dict["node_id"],
                crdt_type=CRDTType(op_dict["crdt_type"]),
                operation=op_dict["operation"],
                value=op_dict["value"],
                timestamp=op_dict["timestamp"],
                vector_clock=VectorClock(clock=op_dict["vector_clock"])
            )
            
            # Find matching CRDT and apply
            for name, crdt in self.crdts.items():
                if isinstance(crdt, GrowOnlySet) and op.crdt_type == CRDTType.GSET:
                    crdt.merge([op])
                elif isinstance(crdt, GrowOnlyCounter) and op.crdt_type == CRDTType.GCOUNTER:
                    crdt.merge([op])
                elif isinstance(crdt, LastWriteWinsRegister) and op.crdt_type == CRDTType.LWWREG:
                    crdt.merge([op])
            
            self.operation_log.append(op)
    
    def export_operations(self) -> List[Dict[str, Any]]:
        """Export operations for sync to other codespaces"""
        return [op.to_dict() for op in self.operation_log]
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state of all CRDTs"""
        state = {}
        for name, crdt in self.crdts.items():
            state[name] = crdt.query()
        return state
    
    def save_to_file(self, path: str):
        """Save operations to file"""
        with open(path, 'w') as f:
            json.dump(self.export_operations(), f, indent=2)
    
    def load_from_file(self, path: str):
        """Load operations from file"""
        with open(path, 'r') as f:
            operations = json.load(f)
        self.merge_from_remote(operations)


def main():
    """Test CRDT merge engine"""
    print("🔀 Testing CRDT Merge Engine\n")
    
    # Simulate two codespaces
    codespace1 = CRDTMergeEngine(node_id="codespace-1")
    codespace2 = CRDTMergeEngine(node_id="codespace-2")
    
    # Create CRDTs
    print("📊 Creating CRDTs...")
    
    # G-Set for agent results
    results1 = codespace1.create_gset("agent_results")
    results2 = codespace2.create_gset("agent_results")
    
    # G-Counter for task completion
    counter1 = codespace1.create_gcounter("tasks_completed")
    counter2 = codespace2.create_gcounter("tasks_completed")
    
    # LWW-Register for system status
    status1 = codespace1.create_lww_register("system_status", "idle")
    status2 = codespace2.create_lww_register("system_status", "idle")
    
    print("\n🔄 Performing operations...\n")
    
    # Codespace 1 operations
    print("Codespace 1:")
    results1.add("optimization_complete")
    results1.add("security_scan_ok")
    counter1.increment(2)
    status1.set("building_iso")
    print(f"  Results: {results1.query()}")
    print(f"  Counter: {counter1.query()}")
    print(f"  Status: {status1.query()}")
    
    # Codespace 2 operations
    print("\nCodespace 2:")
    results2.add("distillation_done")
    results2.add("kernel_compiled")
    counter2.increment(3)
    status2.set("testing")
    print(f"  Results: {results2.query()}")
    print(f"  Counter: {counter2.query()}")
    print(f"  Status: {status2.query()}")
    
    # Sync operations
    print("\n🔀 Synchronizing...\n")
    
    ops1 = codespace1.export_operations()
    ops2 = codespace2.export_operations()
    
    codespace1.merge_from_remote(ops2)
    codespace2.merge_from_remote(ops1)
    
    # Show merged state
    print("After sync:")
    print(f"\nCodespace 1 state:")
    state1 = codespace1.get_state()
    for key, value in state1.items():
        print(f"  {key}: {value}")
    
    print(f"\nCodespace 2 state:")
    state2 = codespace2.get_state()
    for key, value in state2.items():
        print(f"  {key}: {value}")
    
    # Verify convergence
    print("\n✅ Convergence check:")
    print(f"  Results match: {state1['agent_results'] == state2['agent_results']}")
    print(f"  Counters match: {state1['tasks_completed'] == state2['tasks_completed']}")
    print(f"  Status match: {state1['system_status'] == state2['system_status']}")
    
    # Save state
    print("\n💾 Saving to file...")
    codespace1.save_to_file("/tmp/crdt_sync.json")
    print("  Saved to /tmp/crdt_sync.json")


if __name__ == "__main__":
    main()
