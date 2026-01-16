pub mod cli;
pub mod core;
pub mod formatters;
pub mod tui;

// Re-export commonly used items
pub use core::{
    filter_by_cwd, filter_high_memory, filter_killable, filter_orphans, filter_stale,
    find_similar_processes, get_memory_summary, get_process_list, is_system_service,
    kill_process, kill_processes, sort_processes, KillResult, MemorySummary, ProcessInfo,
};

pub use formatters::{format_output, get_columns, get_default_columns, OutputFormat};

pub use cli::{cmd_groups, cmd_kill, cmd_list, cmd_memory, Cli, Commands};

pub use tui::App;

// Python bindings
#[cfg(feature = "python")]
pub mod python;

#[cfg(feature = "python")]
use pyo3::prelude::*;

/// Python module for procclean
#[cfg(feature = "python")]
#[pymodule]
fn _procclean(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<python::PyProcessInfo>()?;
    m.add_class::<python::PyMemorySummary>()?;
    m.add_function(wrap_pyfunction!(python::get_processes, m)?)?;
    m.add_function(wrap_pyfunction!(python::get_memory, m)?)?;
    m.add_function(wrap_pyfunction!(python::kill_process_py, m)?)?;
    m.add_function(wrap_pyfunction!(python::filter_orphans_py, m)?)?;
    m.add_function(wrap_pyfunction!(python::filter_killable_py, m)?)?;
    Ok(())
}
