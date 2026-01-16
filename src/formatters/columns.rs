use crate::core::models::ProcessInfo;

/// Side to clip when truncating text
#[derive(Debug, Clone, Copy)]
pub enum ClipSide {
    /// Keep the right portion (add "..." on left)
    Left,
    /// Keep the left portion (add "..." on right)
    Right,
}

/// Clip text to max length with ellipsis
pub fn clip(text: &str, max_len: usize, side: ClipSide) -> String {
    if text.len() <= max_len {
        return text.to_string();
    }

    match side {
        ClipSide::Left => {
            let keep = max_len.saturating_sub(3);
            format!("...{}", &text[text.len().saturating_sub(keep)..])
        }
        ClipSide::Right => {
            let keep = max_len.saturating_sub(3);
            format!("{}...", &text[..keep])
        }
    }
}

/// Column specification for formatting
pub struct ColumnSpec {
    pub key: &'static str,
    pub header: &'static str,
    pub max_width: Option<usize>,
    pub clip_side: ClipSide,
}

impl ColumnSpec {
    /// Extract and format the value for this column
    pub fn extract(&self, proc: &ProcessInfo) -> String {
        let value = match self.key {
            "pid" => proc.pid.to_string(),
            "name" => proc.name.clone(),
            "rss_mb" => format!("{:.1}", proc.rss_mb),
            "cpu_percent" => format!("{:.1}", proc.cpu_percent),
            "cwd" => proc.cwd.clone(),
            "ppid" => proc.ppid.to_string(),
            "parent_name" => proc.parent_name.clone(),
            "status" => proc.display_status(),
            "cmdline" => proc.cmdline.clone(),
            "username" => proc.username.clone(),
            _ => "?".to_string(),
        };

        if let Some(max_width) = self.max_width {
            clip(&value, max_width, self.clip_side)
        } else {
            value
        }
    }
}

/// Available columns
pub const COLUMNS: &[ColumnSpec] = &[
    ColumnSpec {
        key: "pid",
        header: "PID",
        max_width: None,
        clip_side: ClipSide::Right,
    },
    ColumnSpec {
        key: "name",
        header: "Name",
        max_width: Some(25),
        clip_side: ClipSide::Right,
    },
    ColumnSpec {
        key: "rss_mb",
        header: "RAM (MB)",
        max_width: None,
        clip_side: ClipSide::Right,
    },
    ColumnSpec {
        key: "cpu_percent",
        header: "CPU%",
        max_width: None,
        clip_side: ClipSide::Right,
    },
    ColumnSpec {
        key: "cwd",
        header: "CWD",
        max_width: Some(35),
        clip_side: ClipSide::Left,
    },
    ColumnSpec {
        key: "ppid",
        header: "PPID",
        max_width: None,
        clip_side: ClipSide::Right,
    },
    ColumnSpec {
        key: "parent_name",
        header: "Parent",
        max_width: Some(20),
        clip_side: ClipSide::Right,
    },
    ColumnSpec {
        key: "status",
        header: "Status",
        max_width: Some(40),
        clip_side: ClipSide::Right,
    },
    ColumnSpec {
        key: "cmdline",
        header: "Command",
        max_width: Some(60),
        clip_side: ClipSide::Right,
    },
    ColumnSpec {
        key: "username",
        header: "User",
        max_width: Some(15),
        clip_side: ClipSide::Right,
    },
];

/// Default columns to display
pub const DEFAULT_COLUMN_KEYS: &[&str] = &["pid", "name", "rss_mb", "cpu_percent", "cwd", "ppid", "status"];

/// Get column specs by keys
pub fn get_columns(keys: &[&str]) -> Vec<&'static ColumnSpec> {
    keys.iter()
        .filter_map(|key| COLUMNS.iter().find(|col| col.key == *key))
        .collect()
}

/// Get default columns
pub fn get_default_columns() -> Vec<&'static ColumnSpec> {
    get_columns(DEFAULT_COLUMN_KEYS)
}
