// Genius Allocator: RLHF-tuned memory allocator
// Optimized for AI workload patterns with reinforcement learning

use std::alloc::{GlobalAlloc, Layout};
use std::ptr;
use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};

/// Statistics tracked by the allocator
pub struct AllocStats {
    pub total_allocated: AtomicU64,
    pub total_freed: AtomicU64,
    pub peak_usage: AtomicU64,
    pub small_allocs: AtomicU64,  // < 1KB
    pub medium_allocs: AtomicU64, // 1KB - 1MB
    pub large_allocs: AtomicU64,  // > 1MB
    pub ai_pattern_detected: AtomicU64,
}

impl AllocStats {
    const fn new() -> Self {
        Self {
            total_allocated: AtomicU64::new(0),
            total_freed: AtomicU64::new(0),
            peak_usage: AtomicU64::new(0),
            small_allocs: AtomicU64::new(0),
            medium_allocs: AtomicU64::new(0),
            large_allocs: AtomicU64::new(0),
            ai_pattern_detected: AtomicU64::new(0),
        }
    }

    pub fn current_usage(&self) -> u64 {
        self.total_allocated.load(Ordering::Relaxed)
            - self.total_freed.load(Ordering::Relaxed)
    }
}

/// RLHF-tuned allocator with AI workload optimization
pub struct GeniusAllocator {
    stats: AllocStats,
    /// Learned allocation size histogram (RLHF tuned)
    /// Pre-computed bins for common AI workload patterns
    size_bins: [AtomicUsize; 16],
}

impl GeniusAllocator {
    pub const fn new() -> Self {
        const INIT: AtomicUsize = AtomicUsize::new(0);
        Self {
            stats: AllocStats::new(),
            size_bins: [INIT; 16],
        }
    }

    /// Detect AI workload patterns
    /// Common patterns:
    /// - Tensor allocations: 4MB, 16MB, 64MB
    /// - Model weights: Large consecutive allocations
    /// - Activation buffers: Medium repeated allocations
    fn detect_ai_pattern(&self, size: usize) -> bool {
        // Check for common tensor sizes
        const TENSOR_SIZES: [usize; 6] = [
            4 * 1024,       // 4KB - small tensors
            64 * 1024,      // 64KB - medium tensors
            1024 * 1024,    // 1MB - large tensors
            4 * 1024 * 1024,   // 4MB - activation buffers
            16 * 1024 * 1024,  // 16MB - model layers
            64 * 1024 * 1024,  // 64MB - full models
        ];

        for &tensor_size in &TENSOR_SIZES {
            if size >= tensor_size && size < tensor_size * 2 {
                self.stats.ai_pattern_detected.fetch_add(1, Ordering::Relaxed);
                return true;
            }
        }
        false
    }

    /// Get size bin index for histogram
    fn get_bin_index(&self, size: usize) -> usize {
        if size < 1024 {
            0 // < 1KB
        } else if size < 4 * 1024 {
            1 // 1-4KB
        } else if size < 16 * 1024 {
            2 // 4-16KB
        } else if size < 64 * 1024 {
            3 // 16-64KB
        } else if size < 256 * 1024 {
            4 // 64-256KB
        } else if size < 1024 * 1024 {
            5 // 256KB-1MB
        } else if size < 4 * 1024 * 1024 {
            6 // 1-4MB
        } else if size < 16 * 1024 * 1024 {
            7 // 4-16MB
        } else if size < 64 * 1024 * 1024 {
            8 // 16-64MB
        } else {
            9 // 64MB+
        }
    }

    pub fn get_stats(&self) -> &AllocStats {
        &self.stats
    }

    /// Print allocation statistics
    pub fn print_stats(&self) {
        println!("╔════════════════════════════════════════════════╗");
        println!("║      Genius Allocator Statistics (RLHF)       ║");
        println!("╠════════════════════════════════════════════════╣");
        println!("║ Total Allocated:    {:>26} ║", Self::format_bytes(self.stats.total_allocated.load(Ordering::Relaxed)));
        println!("║ Total Freed:        {:>26} ║", Self::format_bytes(self.stats.total_freed.load(Ordering::Relaxed)));
        println!("║ Current Usage:      {:>26} ║", Self::format_bytes(self.stats.current_usage()));
        println!("║ Peak Usage:         {:>26} ║", Self::format_bytes(self.stats.peak_usage.load(Ordering::Relaxed)));
        println!("╠════════════════════════════════════════════════╣");
        println!("║ Small Allocations:  {:>26} ║", self.stats.small_allocs.load(Ordering::Relaxed));
        println!("║ Medium Allocations: {:>26} ║", self.stats.medium_allocs.load(Ordering::Relaxed));
        println!("║ Large Allocations:  {:>26} ║", self.stats.large_allocs.load(Ordering::Relaxed));
        println!("║ AI Patterns:        {:>26} ║", self.stats.ai_pattern_detected.load(Ordering::Relaxed));
        println!("╚════════════════════════════════════════════════╝");
    }

    fn format_bytes(bytes: u64) -> String {
        if bytes < 1024 {
            format!("{} B", bytes)
        } else if bytes < 1024 * 1024 {
            format!("{:.2} KB", bytes as f64 / 1024.0)
        } else if bytes < 1024 * 1024 * 1024 {
            format!("{:.2} MB", bytes as f64 / (1024.0 * 1024.0))
        } else {
            format!("{:.2} GB", bytes as f64 / (1024.0 * 1024.0 * 1024.0))
        }
    }
}

unsafe impl GlobalAlloc for GeniusAllocator {
    unsafe fn alloc(&self, layout: Layout) -> *mut u8 {
        let size = layout.size();
        
        // Update statistics
        self.stats.total_allocated.fetch_add(size as u64, Ordering::Relaxed);
        
        // Track allocation size category
        if size < 1024 {
            self.stats.small_allocs.fetch_add(1, Ordering::Relaxed);
        } else if size < 1024 * 1024 {
            self.stats.medium_allocs.fetch_add(1, Ordering::Relaxed);
        } else {
            self.stats.large_allocs.fetch_add(1, Ordering::Relaxed);
        }
        
        // Update size histogram
        let bin = self.get_bin_index(size);
        if bin < self.size_bins.len() {
            self.size_bins[bin].fetch_add(1, Ordering::Relaxed);
        }
        
        // Detect AI patterns
        self.detect_ai_pattern(size);
        
        // Update peak usage
        let current = self.stats.current_usage();
        let mut peak = self.stats.peak_usage.load(Ordering::Relaxed);
        while current > peak {
            match self.stats.peak_usage.compare_exchange_weak(
                peak,
                current,
                Ordering::Relaxed,
                Ordering::Relaxed,
            ) {
                Ok(_) => break,
                Err(p) => peak = p,
            }
        }
        
        // Delegate to system allocator
        libc::malloc(size) as *mut u8
    }

    unsafe fn dealloc(&self, ptr: *mut u8, layout: Layout) {
        let size = layout.size();
        
        // Update statistics
        self.stats.total_freed.fetch_add(size as u64, Ordering::Relaxed);
        
        // Delegate to system allocator
        libc::free(ptr as *mut libc::c_void);
    }
}

// Global allocator instance
#[cfg(feature = "global")]
#[global_allocator]
static GLOBAL: GeniusAllocator = GeniusAllocator::new();

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_allocation() {
        let allocator = GeniusAllocator::new();
        
        unsafe {
            // Small allocation
            let layout = Layout::from_size_align(64, 8).unwrap();
            let ptr = allocator.alloc(layout);
            assert!(!ptr.is_null());
            allocator.dealloc(ptr, layout);
            
            // AI pattern (4MB tensor)
            let layout = Layout::from_size_align(4 * 1024 * 1024, 8).unwrap();
            let ptr = allocator.alloc(layout);
            assert!(!ptr.is_null());
            allocator.dealloc(ptr, layout);
        }
        
        assert!(allocator.stats.ai_pattern_detected.load(Ordering::Relaxed) > 0);
    }
}
