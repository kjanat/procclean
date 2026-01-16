use crate::core::models::ProcessInfo;
use anyhow::Result;
use std::collections::HashMap;
use std::fs;
use std::path::Path;
use sysinfo::{ProcessRefreshKind, ProcessesToUpdate, System};

/// Get list of all processes
pub fn get_process_list(
    sort_by: &str,
    filter_user: Option<&str>,
    min_memory_mb: f64,
) -> Result<Vec<ProcessInfo>> {
    let mut sys = System::new_all();
    sys.refresh_processes_specifics(
        ProcessesToUpdate::All,
        true,
        ProcessRefreshKind::everything(),
    );

    let _current_user = filter_user
        .map(String::from)
        .or_else(|| std::env::var("USER").ok())
        .unwrap_or_else(|| "unknown".to_string());

    let mut processes = Vec::new();

    for (pid, process) in sys.processes() {
        // Filter by user - disabled for now due to sysinfo API changes
        // TODO: Re-enable user filtering when we upgrade sysinfo

        let rss_mb = process.memory() as f64 / 1_048_576.0; // bytes to MB

        // Filter by minimum memory
        if rss_mb < min_memory_mb {
            continue;
        }

        let pid_num = pid.as_u32();
        let name = process.name().to_string_lossy().to_string();
        let cmdline = process
            .cmd()
            .iter()
            .map(|s| s.to_string_lossy().to_string())
            .collect::<Vec<_>>()
            .join(" ");

        let cwd = get_cwd(pid_num);
        let ppid = process.parent().map(|p| p.as_u32()).unwrap_or(0);
        let parent_name = process
            .parent()
            .and_then(|p| sys.process(p))
            .map(|p| p.name().to_string_lossy().to_string())
            .unwrap_or_else(|| "?".to_string());

        let cpu_percent = process.cpu_usage() as f64;
        let username = process
            .effective_user_id()
            .map(|s| s.to_string())
            .unwrap_or_else(|| "?".to_string());

        let create_time = process.start_time() as f64;
        let is_orphan = ppid == 1;
        let in_tmux = get_tmux_env(pid_num);
        let status = format!("{:?}", process.status()).to_lowercase();
        let exe_deleted = is_exe_deleted(pid_num);

        processes.push(ProcessInfo {
            pid: pid_num,
            name,
            cmdline,
            cwd,
            ppid,
            parent_name,
            rss_mb,
            cpu_percent,
            username,
            create_time,
            is_orphan,
            in_tmux,
            status,
            exe_deleted,
        });
    }

    // Sort processes
    sort_processes(&mut processes, sort_by, true);

    Ok(processes)
}

/// Sort processes by the specified field
pub fn sort_processes(processes: &mut [ProcessInfo], sort_by: &str, reverse: bool) {
    processes.sort_by(|a, b| {
        let cmp = match sort_by {
            "memory" | "mem" | "rss" => b.rss_mb.partial_cmp(&a.rss_mb).unwrap(),
            "cpu" => b.cpu_percent.partial_cmp(&a.cpu_percent).unwrap(),
            "pid" => a.pid.cmp(&b.pid),
            "name" => a.name.cmp(&b.name),
            "cwd" => a.cwd.cmp(&b.cwd),
            _ => a.pid.cmp(&b.pid),
        };

        if reverse && (sort_by == "name" || sort_by == "cwd") {
            cmp.reverse()
        } else if !reverse && (sort_by == "memory" || sort_by == "cpu" || sort_by == "pid") {
            cmp.reverse()
        } else {
            cmp
        }
    });
}

/// Get the current working directory of a process
fn get_cwd(pid: u32) -> String {
    let cwd_path = format!("/proc/{}/cwd", pid);
    fs::read_link(&cwd_path)
        .ok()
        .and_then(|p| p.to_str().map(String::from))
        .unwrap_or_else(|| "?".to_string())
}

/// Check if a process is running in tmux
fn get_tmux_env(pid: u32) -> bool {
    let environ_path = format!("/proc/{}/environ", pid);
    if let Ok(content) = fs::read(&environ_path) {
        // Environment variables are null-separated
        let env_str = String::from_utf8_lossy(&content);
        env_str.split('\0').any(|var| var.starts_with("TMUX="))
    } else {
        false
    }
}

/// Check if the executable has been deleted (stale process)
fn is_exe_deleted(pid: u32) -> bool {
    let exe_path = format!("/proc/{}/exe", pid);
    if let Ok(link) = fs::read_link(&exe_path) {
        link.to_string_lossy().contains("(deleted)")
    } else {
        false
    }
}

/// Find similar processes (grouped by name)
pub fn find_similar_processes(processes: &[ProcessInfo]) -> HashMap<String, Vec<ProcessInfo>> {
    let mut groups: HashMap<String, Vec<ProcessInfo>> = HashMap::new();

    for proc in processes {
        // Use the process name or the basename of the command
        let key = if proc.name.is_empty() {
            Path::new(&proc.cmdline)
                .file_name()
                .and_then(|s| s.to_str())
                .unwrap_or("unknown")
                .to_string()
        } else {
            proc.name.clone()
        };

        groups.entry(key).or_default().push(proc.clone());
    }

    // Only return groups with 2+ processes
    groups.retain(|_, procs| procs.len() >= 2);

    groups
}
