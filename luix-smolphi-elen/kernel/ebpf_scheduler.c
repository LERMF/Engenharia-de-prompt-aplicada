// Linux 6.12-rc3 eBPF Task Injection Scheduler Hook
// Optimizes task scheduling for AI workload performance

#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

#define TASK_RUNNING 0
#define TASK_INTERRUPTIBLE 1

// Priority boost for AI agents
#define AI_AGENT_PRIO_BOOST 5
#define MAX_LATENCY_MS 30

struct task_info {
    __u32 pid;
    __u32 tgid;
    __u64 runtime_ns;
    __u64 vruntime;
    int prio;
    char comm[16];
};

// BPF maps for tracking tasks
struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 10240);
    __type(key, __u32);
    __type(value, struct task_info);
} task_map SEC(".maps");

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 256);
    __type(key, char[16]);
    __type(value, __u32);
} ai_agents SEC(".maps");

// Statistics
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 16);
    __type(key, __u32);
    __type(value, __u64);
} stats SEC(".maps");

enum stat_keys {
    STAT_TOTAL_SCHEDULES = 0,
    STAT_AI_TASK_BOOSTS = 1,
    STAT_LATENCY_VIOLATIONS = 2,
    STAT_CONTEXT_SWITCHES = 3,
};

// Helper to check if task is an AI agent
static __always_inline bool is_ai_agent(const char *comm) {
    // Check against known AI agent names
    if (__builtin_memcmp(comm, "gemini_driver", 13) == 0)
        return true;
    if (__builtin_memcmp(comm, "smollm_brain", 12) == 0)
        return true;
    if (__builtin_memcmp(comm, "langgraph", 9) == 0)
        return true;
    if (__builtin_memcmp(comm, "crewai", 6) == 0)
        return true;
    if (__builtin_memcmp(comm, "distillation", 12) == 0)
        return true;
    
    // Check dynamic registry
    __u32 *val = bpf_map_lookup_elem(&ai_agents, comm);
    return val != NULL;
}

// Update task statistics
static __always_inline void update_stat(__u32 key, __u64 increment) {
    __u64 *val = bpf_map_lookup_elem(&stats, &key);
    if (val)
        __sync_fetch_and_add(val, increment);
}

// Hook: task wakeup - boost priority for AI agents
SEC("tp/sched/sched_wakeup")
int handle_sched_wakeup(struct trace_event_raw_sched_wakeup *ctx) {
    __u32 pid = ctx->pid;
    
    struct task_info info = {};
    info.pid = pid;
    info.tgid = 0; // Will be filled by userspace
    info.runtime_ns = bpf_ktime_get_ns();
    
    // Get task comm
    bpf_get_current_comm(&info.comm, sizeof(info.comm));
    
    // Check if AI agent
    if (is_ai_agent(info.comm)) {
        // Boost priority
        info.prio = ctx->prio - AI_AGENT_PRIO_BOOST;
        
        update_stat(STAT_AI_TASK_BOOSTS, 1);
        
        // Store boosted info
        bpf_map_update_elem(&task_map, &pid, &info, BPF_ANY);
    }
    
    update_stat(STAT_TOTAL_SCHEDULES, 1);
    
    return 0;
}

// Hook: context switch - track latency
SEC("tp/sched/sched_switch")
int handle_sched_switch(struct trace_event_raw_sched_switch *ctx) {
    __u32 prev_pid = ctx->prev_pid;
    __u32 next_pid = ctx->next_pid;
    
    __u64 now = bpf_ktime_get_ns();
    
    // Update runtime for previous task
    struct task_info *prev_info = bpf_map_lookup_elem(&task_map, &prev_pid);
    if (prev_info) {
        __u64 runtime = now - prev_info->runtime_ns;
        prev_info->vruntime += runtime;
        
        // Check latency constraint (30ms)
        if (runtime > (MAX_LATENCY_MS * 1000000)) {
            update_stat(STAT_LATENCY_VIOLATIONS, 1);
        }
    }
    
    // Update runtime for next task
    struct task_info *next_info = bpf_map_lookup_elem(&task_map, &next_pid);
    if (next_info) {
        next_info->runtime_ns = now;
    }
    
    update_stat(STAT_CONTEXT_SWITCHES, 1);
    
    return 0;
}

// Hook: task fork - track AI agent children
SEC("tp/sched/sched_process_fork")
int handle_process_fork(struct trace_event_raw_sched_process_fork *ctx) {
    __u32 parent_pid = ctx->parent_pid;
    __u32 child_pid = ctx->child_pid;
    
    // If parent is AI agent, track child
    struct task_info *parent_info = bpf_map_lookup_elem(&task_map, &parent_pid);
    if (parent_info && is_ai_agent(parent_info->comm)) {
        struct task_info child_info = *parent_info;
        child_info.pid = child_pid;
        child_info.runtime_ns = bpf_ktime_get_ns();
        child_info.vruntime = 0;
        
        bpf_map_update_elem(&task_map, &child_pid, &child_info, BPF_ANY);
    }
    
    return 0;
}

// Hook: task exit - cleanup
SEC("tp/sched/sched_process_exit")
int handle_process_exit(struct trace_event_raw_sched_process_template *ctx) {
    __u32 pid = ctx->pid;
    bpf_map_delete_elem(&task_map, &pid);
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
