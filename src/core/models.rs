use serde::{Deserialize, Serialize};

/// Information about a process
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProcessInfo {
    /// Process ID
    pub pid: u32,
    /// Process name
    pub name: String,
    /// Full command line
    pub cmdline: String,
    /// Current working directory
    pub cwd: String,
    /// Parent process ID
    pub ppid: u32,
    /// Parent process name
    pub parent_name: String,
    /// Resident set size in MB
    pub rss_mb: f64,
    /// CPU usage percentage
    pub cpu_percent: f64,
    /// Username of process owner
    pub username: String,
    /// Process creation time (Unix timestamp)
    pub create_time: f64,
    /// Whether this is an orphan process (ppid == 1)
    pub is_orphan: bool,
    /// Whether this process is running in tmux
    pub in_tmux: bool,
    /// Process status (running, sleeping, etc.)
    pub status: String,
    /// Whether the executable has been deleted (stale)
    pub exe_deleted: bool,
}

impl ProcessInfo {
    /// Returns true if this is an orphan process not in tmux
    /// These are candidates for cleanup
    pub fn is_orphan_candidate(&self) -> bool {
        self.is_orphan && !self.in_tmux
    }

    /// Get a short display status with flags
    pub fn display_status(&self) -> String {
        let mut parts = vec![self.status.clone()];

        if self.is_orphan {
            parts.push("[orphan]".to_string());
        }
        if self.in_tmux {
            parts.push("[tmux]".to_string());
        }
        if self.exe_deleted {
            parts.push("[stale]".to_string());
        }

        parts.join(" ")
    }
}

/// Memory summary information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemorySummary {
    /// Total memory in GB
    pub total_gb: f64,
    /// Used memory in GB
    pub used_gb: f64,
    /// Free memory in GB
    pub free_gb: f64,
    /// Memory usage percentage
    pub percent: f64,
    /// Total swap in GB
    pub swap_total_gb: f64,
    /// Used swap in GB
    pub swap_used_gb: f64,
}
