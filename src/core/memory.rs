use crate::core::models::MemorySummary;
use sysinfo::System;

/// Get system memory summary
pub fn get_memory_summary() -> MemorySummary {
    let mut sys = System::new_all();
    sys.refresh_memory();

    let total = sys.total_memory() as f64 / 1_073_741_824.0; // bytes to GB
    let used = sys.used_memory() as f64 / 1_073_741_824.0;
    let free = sys.available_memory() as f64 / 1_073_741_824.0;

    let swap_total = sys.total_swap() as f64 / 1_073_741_824.0;
    let swap_used = sys.used_swap() as f64 / 1_073_741_824.0;

    let percent = if total > 0.0 {
        (used / total) * 100.0
    } else {
        0.0
    };

    MemorySummary {
        total_gb: total,
        used_gb: used,
        free_gb: free,
        percent,
        swap_total_gb: swap_total,
        swap_used_gb: swap_used,
    }
}
