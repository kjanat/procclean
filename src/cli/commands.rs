use crate::cli::parser::{GroupsArgs, KillArgs, ListArgs, MemoryArgs};
use crate::core::{
    filter_by_cwd, filter_killable, filter_orphans, filter_stale, find_similar_processes,
    get_memory_summary, get_process_list, kill_processes, ProcessInfo, PREVIEW_LIMIT,
};
use crate::formatters::{format_output, get_columns, get_default_columns, OutputFormat};
use anyhow::Result;
use is_terminal::IsTerminal;
use std::io::{self, Write};

/// Run the list command
pub fn cmd_list(args: ListArgs) -> Result<()> {
    let mut processes = get_filtered_processes(
        args.cwd.as_deref(),
        args.filter.as_deref(),
        args.orphans,
        args.killable,
        args.high_memory,
        args.high_memory_threshold,
        args.min_memory,
        &args.sort,
    )?;

    // Apply limit
    if let Some(limit) = args.limit {
        processes.truncate(limit);
    }

    // Get columns
    let columns = if let Some(col_str) = &args.columns {
        let keys: Vec<&str> = col_str.split(',').collect();
        get_columns(&keys)
    } else {
        get_default_columns()
    };

    // Format output
    let format = OutputFormat::from_str(&args.format);
    let output = format_output(&processes, format, &columns)?;
    println!("{}", output);

    Ok(())
}

/// Run the groups command
pub fn cmd_groups(args: GroupsArgs) -> Result<()> {
    let processes = get_process_list("memory", None, args.min_memory)?;
    let groups = find_similar_processes(&processes);

    if args.format == "json" {
        let json = serde_json::to_string_pretty(&groups)?;
        println!("{}", json);
        return Ok(());
    }

    // Format as table
    println!("\n{} process groups found\n", groups.len());

    let mut sorted_groups: Vec<_> = groups.iter().collect();
    sorted_groups.sort_by(|a, b| {
        let a_mem: f64 = a.1.iter().map(|p| p.rss_mb).sum();
        let b_mem: f64 = b.1.iter().map(|p| p.rss_mb).sum();
        b_mem.partial_cmp(&a_mem).unwrap()
    });

    for (name, procs) in sorted_groups {
        let total_mem: f64 = procs.iter().map(|p| p.rss_mb).sum();
        println!("  {} ({} processes, {:.1} MB total)", name, procs.len(), total_mem);
        for proc in procs {
            println!("    PID {} - {:.1} MB", proc.pid, proc.rss_mb);
        }
        println!();
    }

    Ok(())
}

/// Run the kill command
pub fn cmd_kill(args: KillArgs) -> Result<()> {
    let targets = get_kill_targets(&args)?;

    if targets.is_empty() {
        println!("No processes to kill");
        return Ok(());
    }

    // Preview mode
    if args.preview {
        return do_preview(&args, &targets);
    }

    // Confirm
    if !args.yes && !confirm_kill(&args, &targets)? {
        println!("Cancelled");
        return Ok(());
    }

    // Kill processes
    let pids: Vec<u32> = targets.iter().map(|p| p.pid).collect();
    let results = kill_processes(&pids, args.force);

    // Report results
    let mut success_count = 0;
    for result in &results {
        if result.success {
            success_count += 1;
            println!("✓ {}", result);
        } else {
            eprintln!("✗ {}", result);
        }
    }

    println!(
        "\nKilled {} of {} processes",
        success_count,
        results.len()
    );

    Ok(())
}

/// Run the memory command
pub fn cmd_memory(args: MemoryArgs) -> Result<()> {
    let summary = get_memory_summary();

    if args.format == "json" {
        let json = serde_json::to_string_pretty(&summary)?;
        println!("{}", json);
        return Ok(());
    }

    // Format as table
    println!("\nMemory Summary:");
    println!("  Total:      {:.2} GB", summary.total_gb);
    println!("  Used:       {:.2} GB ({:.1}%)", summary.used_gb, summary.percent);
    println!("  Free:       {:.2} GB", summary.free_gb);
    println!("  Swap Total: {:.2} GB", summary.swap_total_gb);
    println!("  Swap Used:  {:.2} GB", summary.swap_used_gb);

    Ok(())
}

/// Get filtered processes based on arguments
fn get_filtered_processes(
    cwd: Option<&str>,
    filter: Option<&str>,
    orphans: bool,
    killable: bool,
    high_memory: bool,
    high_memory_threshold: f64,
    min_memory: f64,
    sort_by: &str,
) -> Result<Vec<ProcessInfo>> {
    let mut processes = get_process_list(sort_by, None, min_memory)?;

    // Apply CWD filter first
    if let Some(cwd_path) = cwd {
        processes = filter_by_cwd(&processes, cwd_path);
    }

    // Apply filter presets
    if killable || filter.as_deref() == Some("killable") {
        processes = filter_killable(&processes);
    } else if orphans || filter.as_deref() == Some("orphans") {
        processes = filter_orphans(&processes);
    } else if high_memory || filter.as_deref() == Some("high-memory") {
        processes = crate::core::filter_high_memory(&processes, high_memory_threshold);
    } else if filter.as_deref() == Some("stale") {
        processes = filter_stale(&processes);
    }

    Ok(processes)
}

/// Get target processes for killing
fn get_kill_targets(args: &KillArgs) -> Result<Vec<ProcessInfo>> {
    if !args.pids.is_empty() {
        // Kill specific PIDs - need to get process info for them
        let all_processes = get_process_list("pid", None, 0.0)?;
        Ok(all_processes
            .into_iter()
            .filter(|p| args.pids.contains(&p.pid))
            .collect())
    } else {
        // Kill based on filters
        get_filtered_processes(
            args.cwd.as_deref(),
            args.filter.as_deref(),
            args.orphans,
            args.killable,
            args.high_memory,
            args.high_memory_threshold,
            args.min_memory,
            &args.sort,
        )
    }
}

/// Show preview of what would be killed
fn do_preview(args: &KillArgs, targets: &[ProcessInfo]) -> Result<()> {
    println!("Would kill {} process(es):\n", targets.len());

    let columns = if let Some(col_str) = &args.columns {
        let keys: Vec<&str> = col_str.split(',').collect();
        get_columns(&keys)
    } else {
        get_default_columns()
    };

    let format = OutputFormat::from_str(&args.output);

    // Apply limit for preview
    let preview_targets: Vec<_> = targets.iter().take(PREVIEW_LIMIT).cloned().collect();
    let output = format_output(&preview_targets, format, &columns)?;
    println!("{}", output);

    if targets.len() > PREVIEW_LIMIT {
        println!("\n... and {} more", targets.len() - PREVIEW_LIMIT);
    }

    let total_memory: f64 = targets.iter().map(|p| p.rss_mb).sum();
    println!("\nWould free ~{:.1} MB", total_memory);

    Ok(())
}

/// Confirm kill operation
fn confirm_kill(args: &KillArgs, targets: &[ProcessInfo]) -> Result<bool> {
    // Skip if not a TTY
    if !io::stdin().is_terminal() {
        return Ok(true);
    }

    let total_memory: f64 = targets.iter().map(|p| p.rss_mb).sum();
    let action = if args.force { "Force kill" } else { "Kill" };

    println!(
        "{} {} process(es)? Will free ~{:.1} MB",
        action,
        targets.len(),
        total_memory
    );

    // Show preview
    let preview_count = PREVIEW_LIMIT.min(targets.len());
    for proc in targets.iter().take(preview_count) {
        println!("  PID {} - {} ({:.1} MB)", proc.pid, proc.name, proc.rss_mb);
    }
    if targets.len() > preview_count {
        println!("  ... and {} more", targets.len() - preview_count);
    }

    print!("\nContinue? [y/N] ");
    io::stdout().flush()?;

    let mut input = String::new();
    io::stdin().read_line(&mut input)?;

    Ok(input.trim().eq_ignore_ascii_case("y") || input.trim().eq_ignore_ascii_case("yes"))
}
