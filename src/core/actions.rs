use nix::sys::signal::{self, Signal};
use nix::unistd::Pid;
use std::fmt;

/// Result of a kill operation
#[derive(Debug, Clone)]
pub struct KillResult {
    pub pid: u32,
    pub success: bool,
    pub message: String,
}

impl fmt::Display for KillResult {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        if self.success {
            write!(f, "Killed process {}: {}", self.pid, self.message)
        } else {
            write!(f, "Failed to kill process {}: {}", self.pid, self.message)
        }
    }
}

/// Kill a single process
pub fn kill_process(pid: u32, force: bool) -> KillResult {
    let signal = if force {
        Signal::SIGKILL
    } else {
        Signal::SIGTERM
    };

    let result = signal::kill(Pid::from_raw(pid as i32), signal);

    match result {
        Ok(_) => KillResult {
            pid,
            success: true,
            message: if force {
                "Force killed (SIGKILL)".to_string()
            } else {
                "Terminated (SIGTERM)".to_string()
            },
        },
        Err(nix::errno::Errno::ESRCH) => KillResult {
            pid,
            success: false,
            message: "Process not found".to_string(),
        },
        Err(nix::errno::Errno::EPERM) => KillResult {
            pid,
            success: false,
            message: "Permission denied".to_string(),
        },
        Err(e) => KillResult {
            pid,
            success: false,
            message: format!("Error: {}", e),
        },
    }
}

/// Kill multiple processes
pub fn kill_processes(pids: &[u32], force: bool) -> Vec<KillResult> {
    pids.iter().map(|&pid| kill_process(pid, force)).collect()
}
