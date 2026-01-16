use crate::core::models::ProcessInfo;
use crate::formatters::columns::ColumnSpec;
use anyhow::Result;
use comfy_table::{modifiers::UTF8_ROUND_CORNERS, presets::UTF8_FULL, Table};

/// Output format
#[derive(Debug, Clone, Copy)]
pub enum OutputFormat {
    Table,
    Json,
    Csv,
    Markdown,
}

impl OutputFormat {
    pub fn from_str(s: &str) -> Self {
        match s.to_lowercase().as_str() {
            "json" => Self::Json,
            "csv" => Self::Csv,
            "md" | "markdown" => Self::Markdown,
            _ => Self::Table,
        }
    }
}

/// Format processes as output
pub fn format_output(
    processes: &[ProcessInfo],
    format: OutputFormat,
    columns: &[&ColumnSpec],
) -> Result<String> {
    match format {
        OutputFormat::Table => Ok(format_table(processes, columns)),
        OutputFormat::Json => Ok(format_json(processes)?),
        OutputFormat::Csv => Ok(format_csv(processes, columns)),
        OutputFormat::Markdown => Ok(format_markdown(processes, columns)),
    }
}

/// Format as table
pub fn format_table(processes: &[ProcessInfo], columns: &[&ColumnSpec]) -> String {
    let mut table = Table::new();
    table
        .load_preset(UTF8_FULL)
        .apply_modifier(UTF8_ROUND_CORNERS);

    // Add header
    let headers: Vec<&str> = columns.iter().map(|c| c.header).collect();
    table.set_header(headers);

    // Add rows
    for proc in processes {
        let row: Vec<String> = columns.iter().map(|col| col.extract(proc)).collect();
        table.add_row(row);
    }

    table.to_string()
}

/// Format as JSON
pub fn format_json(processes: &[ProcessInfo]) -> Result<String> {
    let json = serde_json::to_string_pretty(processes)?;
    Ok(json)
}

/// Format as CSV
pub fn format_csv(processes: &[ProcessInfo], columns: &[&ColumnSpec]) -> String {
    let mut output = String::new();

    // Header
    let headers: Vec<&str> = columns.iter().map(|c| c.key).collect();
    output.push_str(&headers.join(","));
    output.push('\n');

    // Rows
    for proc in processes {
        let row: Vec<String> = columns
            .iter()
            .map(|col| {
                let val = col.extract(proc);
                // Escape CSV values
                if val.contains(',') || val.contains('"') || val.contains('\n') {
                    format!("\"{}\"", val.replace('"', "\"\""))
                } else {
                    val
                }
            })
            .collect();
        output.push_str(&row.join(","));
        output.push('\n');
    }

    output
}

/// Format as Markdown
pub fn format_markdown(processes: &[ProcessInfo], columns: &[&ColumnSpec]) -> String {
    let mut table = Table::new();
    table.load_preset(UTF8_FULL);

    // Add header
    let headers: Vec<&str> = columns.iter().map(|c| c.header).collect();
    table.set_header(headers);

    // Add rows
    for proc in processes {
        let row: Vec<String> = columns.iter().map(|col| col.extract(proc)).collect();
        table.add_row(row);
    }

    // Convert to markdown (using pipe format)
    let table_str = table.to_string();

    // Simple conversion to markdown table format
    let lines: Vec<&str> = table_str.lines().collect();
    if lines.is_empty() {
        return String::new();
    }

    let mut md = String::new();

    // Find header and separator
    for (i, line) in lines.iter().enumerate() {
        if i == 0 || i == lines.len() - 1 {
            // Skip border lines
            continue;
        }

        // Convert to markdown format
        let cleaned = line
            .trim_start_matches('│')
            .trim_end_matches('│')
            .replace('│', "|");
        md.push('|');
        md.push_str(&cleaned);
        md.push_str("|\n");

        // Add separator after header
        if i == 2 {
            let sep_count = columns.len();
            md.push('|');
            md.push_str(&vec!["---"; sep_count].join("|"));
            md.push_str("|\n");
        }
    }

    md
}
