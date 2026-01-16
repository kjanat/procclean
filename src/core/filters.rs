use crate::core::constants::{CRITICAL_SERVICES, HIGH_MEMORY_THRESHOLD_MB, SYSTEM_EXE_PATHS};
use crate::core::models::ProcessInfo;
use glob::Pattern;
use std::path::Path;

/// Filter processes to only orphans (ppid == 1)
pub fn filter_orphans(processes: &[ProcessInfo]) -> Vec<ProcessInfo> {
    processes
        .iter()
        .filter(|p| p.is_orphan)
        .cloned()
        .collect()
}

/// Filter processes to killable orphans (orphans not in tmux and not system services)
pub fn filter_killable(processes: &[ProcessInfo]) -> Vec<ProcessInfo> {
    processes
        .iter()
        .filter(|p| p.is_orphan_candidate() && !is_system_service(p))
        .cloned()
        .collect()
}

/// Filter processes with high memory usage
pub fn filter_high_memory(processes: &[ProcessInfo], threshold_mb: f64) -> Vec<ProcessInfo> {
    processes
        .iter()
        .filter(|p| p.rss_mb > threshold_mb)
        .cloned()
        .collect()
}

/// Filter processes with deleted executables (stale)
pub fn filter_stale(processes: &[ProcessInfo]) -> Vec<ProcessInfo> {
    processes
        .iter()
        .filter(|p| p.exe_deleted)
        .cloned()
        .collect()
}

/// Filter processes by current working directory
pub fn filter_by_cwd(processes: &[ProcessInfo], cwd_path: &str) -> Vec<ProcessInfo> {
    let cwd_path = cwd_path.trim();

    // Try as a glob pattern first
    if cwd_path.contains('*') || cwd_path.contains('?') {
        if let Ok(pattern) = Pattern::new(cwd_path) {
            return processes
                .iter()
                .filter(|p| pattern.matches(&p.cwd))
                .cloned()
                .collect();
        }
    }

    // Otherwise, try as a prefix match with normalized paths
    let normalized_cwd = normalize_path(cwd_path);
    processes
        .iter()
        .filter(|p| {
            let normalized_proc_cwd = normalize_path(&p.cwd);
            normalized_proc_cwd.starts_with(&normalized_cwd)
        })
        .cloned()
        .collect()
}

/// Check if a process is a system service
pub fn is_system_service(proc: &ProcessInfo) -> bool {
    // Check if executable is in system paths
    for system_path in SYSTEM_EXE_PATHS {
        if proc.cmdline.starts_with(system_path) {
            return true;
        }
    }

    // Check if name is a critical service (case-insensitive)
    let name_lower = proc.name.to_lowercase();
    for critical in CRITICAL_SERVICES {
        if name_lower == critical.to_lowercase() {
            return true;
        }
    }

    false
}

/// Normalize a path by resolving it and converting to string
fn normalize_path(path: &str) -> String {
    // Simple normalization: remove trailing slashes and resolve relative paths
    let path = path.trim_end_matches('/');

    // Try to canonicalize, but fall back to original if it fails
    Path::new(path)
        .canonicalize()
        .ok()
        .and_then(|p| p.to_str().map(String::from))
        .unwrap_or_else(|| path.to_string())
}

/// Apply high memory threshold filter
pub fn apply_high_memory_filter(processes: Vec<ProcessInfo>) -> Vec<ProcessInfo> {
    filter_high_memory(&processes, HIGH_MEMORY_THRESHOLD_MB)
}
