use pyo3::prelude::*;
use crate::core::{
    get_memory_summary, get_process_list, kill_process as rust_kill_process,
    filter_orphans, filter_killable, MemorySummary, ProcessInfo,
};

/// Python-compatible ProcessInfo
#[pyclass(name = "ProcessInfo")]
#[derive(Clone)]
pub struct PyProcessInfo {
    #[pyo3(get)]
    pub pid: u32,
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub cmdline: String,
    #[pyo3(get)]
    pub cwd: String,
    #[pyo3(get)]
    pub ppid: u32,
    #[pyo3(get)]
    pub parent_name: String,
    #[pyo3(get)]
    pub rss_mb: f64,
    #[pyo3(get)]
    pub cpu_percent: f64,
    #[pyo3(get)]
    pub username: String,
    #[pyo3(get)]
    pub create_time: f64,
    #[pyo3(get)]
    pub is_orphan: bool,
    #[pyo3(get)]
    pub in_tmux: bool,
    #[pyo3(get)]
    pub status: String,
    #[pyo3(get)]
    pub exe_deleted: bool,
}

impl From<ProcessInfo> for PyProcessInfo {
    fn from(p: ProcessInfo) -> Self {
        Self {
            pid: p.pid,
            name: p.name,
            cmdline: p.cmdline,
            cwd: p.cwd,
            ppid: p.ppid,
            parent_name: p.parent_name,
            rss_mb: p.rss_mb,
            cpu_percent: p.cpu_percent,
            username: p.username,
            create_time: p.create_time,
            is_orphan: p.is_orphan,
            in_tmux: p.in_tmux,
            status: p.status,
            exe_deleted: p.exe_deleted,
        }
    }
}

impl From<PyProcessInfo> for ProcessInfo {
    fn from(p: PyProcessInfo) -> Self {
        Self {
            pid: p.pid,
            name: p.name,
            cmdline: p.cmdline,
            cwd: p.cwd,
            ppid: p.ppid,
            parent_name: p.parent_name,
            rss_mb: p.rss_mb,
            cpu_percent: p.cpu_percent,
            username: p.username,
            create_time: p.create_time,
            is_orphan: p.is_orphan,
            in_tmux: p.in_tmux,
            status: p.status,
            exe_deleted: p.exe_deleted,
        }
    }
}

#[pymethods]
impl PyProcessInfo {
    fn __repr__(&self) -> String {
        format!(
            "ProcessInfo(pid={}, name='{}', rss_mb={:.1})",
            self.pid, self.name, self.rss_mb
        )
    }

    fn is_orphan_candidate(&self) -> bool {
        self.is_orphan && !self.in_tmux
    }

    fn display_status(&self) -> String {
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

/// Python-compatible MemorySummary
#[pyclass(name = "MemorySummary")]
#[derive(Clone)]
pub struct PyMemorySummary {
    #[pyo3(get)]
    pub total_gb: f64,
    #[pyo3(get)]
    pub used_gb: f64,
    #[pyo3(get)]
    pub free_gb: f64,
    #[pyo3(get)]
    pub percent: f64,
    #[pyo3(get)]
    pub swap_total_gb: f64,
    #[pyo3(get)]
    pub swap_used_gb: f64,
}

impl From<MemorySummary> for PyMemorySummary {
    fn from(m: MemorySummary) -> Self {
        Self {
            total_gb: m.total_gb,
            used_gb: m.used_gb,
            free_gb: m.free_gb,
            percent: m.percent,
            swap_total_gb: m.swap_total_gb,
            swap_used_gb: m.swap_used_gb,
        }
    }
}

#[pymethods]
impl PyMemorySummary {
    fn __repr__(&self) -> String {
        format!(
            "MemorySummary(used={:.1}GB, total={:.1}GB, percent={:.1}%)",
            self.used_gb, self.total_gb, self.percent
        )
    }
}

/// Get list of processes
#[pyfunction]
#[pyo3(signature = (sort_by=None, min_memory_mb=None))]
pub fn get_processes(
    sort_by: Option<&str>,
    min_memory_mb: Option<f64>,
) -> PyResult<Vec<PyProcessInfo>> {
    let processes = get_process_list(
        sort_by.unwrap_or("memory"),
        None,
        min_memory_mb.unwrap_or(10.0),
    )
    .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

    Ok(processes.into_iter().map(PyProcessInfo::from).collect())
}

/// Get memory summary
#[pyfunction]
pub fn get_memory() -> PyMemorySummary {
    get_memory_summary().into()
}

/// Kill a process
#[pyfunction]
#[pyo3(signature = (pid, force=None))]
pub fn kill_process_py(pid: u32, force: Option<bool>) -> PyResult<(bool, String)> {
    let result = rust_kill_process(pid, force.unwrap_or(false));
    Ok((result.success, result.message))
}

/// Filter orphan processes
#[pyfunction]
pub fn filter_orphans_py(processes: Vec<PyProcessInfo>) -> Vec<PyProcessInfo> {
    let rust_procs: Vec<ProcessInfo> = processes.into_iter().map(ProcessInfo::from).collect();
    let filtered = filter_orphans(&rust_procs);
    filtered.into_iter().map(PyProcessInfo::from).collect()
}

/// Filter killable processes
#[pyfunction]
pub fn filter_killable_py(processes: Vec<PyProcessInfo>) -> Vec<PyProcessInfo> {
    let rust_procs: Vec<ProcessInfo> = processes.into_iter().map(ProcessInfo::from).collect();
    let filtered = filter_killable(&rust_procs);
    filtered.into_iter().map(PyProcessInfo::from).collect()
}
