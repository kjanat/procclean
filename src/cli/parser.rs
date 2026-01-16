use clap::{Args, Parser, Subcommand};

#[derive(Parser, Debug)]
#[command(name = "procclean")]
#[command(version = "2.0.0")]
#[command(about = "A fast, interactive process cleaner", long_about = None)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Option<Commands>,
}

#[derive(Subcommand, Debug)]
pub enum Commands {
    /// List processes (default view)
    #[command(alias = "ls")]
    List(ListArgs),

    /// Show process groups
    #[command(alias = "g")]
    Groups(GroupsArgs),

    /// Kill one or more processes
    Kill(KillArgs),

    /// Show memory summary
    #[command(alias = "mem")]
    Memory(MemoryArgs),
}

#[derive(Args, Debug)]
pub struct ListArgs {
    /// Output format (table, json, csv, markdown)
    #[arg(short, long, default_value = "table")]
    pub format: String,

    /// Sort by field (memory, cpu, pid, name, cwd)
    #[arg(short, long, default_value = "memory")]
    pub sort: String,

    /// Sort in ascending order (default: descending for memory/cpu, ascending for name/cwd)
    #[arg(short, long)]
    pub ascending: bool,

    /// Filter preset (orphans, killable, high-memory, stale)
    #[arg(short = 'F', long)]
    pub filter: Option<String>,

    /// Show only orphan processes (shorthand for --filter=orphans)
    #[arg(short = 'o', long)]
    pub orphans: bool,

    /// Show only killable orphan processes (shorthand for --filter=killable)
    #[arg(short = 'k', long)]
    pub killable: bool,

    /// Show only high memory processes (shorthand for --filter=high-memory)
    #[arg(short = 'm', long)]
    pub high_memory: bool,

    /// High memory threshold in MB
    #[arg(long, default_value = "500.0")]
    pub high_memory_threshold: f64,

    /// Minimum memory in MB to display
    #[arg(long, default_value = "10.0")]
    pub min_memory: f64,

    /// Limit number of results
    #[arg(short = 'n', long)]
    pub limit: Option<usize>,

    /// Columns to display (comma-separated)
    #[arg(short = 'c', long)]
    pub columns: Option<String>,

    /// Filter by current working directory (optional path)
    #[arg(long)]
    pub cwd: Option<String>,
}

#[derive(Args, Debug)]
pub struct GroupsArgs {
    /// Output format (table, json)
    #[arg(short, long, default_value = "table")]
    pub format: String,

    /// Minimum memory in MB to display
    #[arg(long, default_value = "10.0")]
    pub min_memory: f64,
}

#[derive(Args, Debug)]
pub struct KillArgs {
    /// Process IDs to kill
    pub pids: Vec<u32>,

    /// Force kill (SIGKILL instead of SIGTERM)
    #[arg(short, long)]
    pub force: bool,

    /// Skip confirmation prompt
    #[arg(short = 'y', long)]
    pub yes: bool,

    /// Show only killable orphan processes (use with --cwd or alone)
    #[arg(short = 'k', long)]
    pub killable: bool,

    /// Show only orphan processes
    #[arg(short = 'o', long)]
    pub orphans: bool,

    /// Show only high memory processes
    #[arg(short = 'm', long)]
    pub high_memory: bool,

    /// Preview what would be killed without killing
    #[arg(long, alias = "dry-run", alias = "dry")]
    pub preview: bool,

    /// Filter by current working directory
    #[arg(long)]
    pub cwd: Option<String>,

    /// Filter preset (orphans, killable, high-memory, stale)
    #[arg(short = 'F', long)]
    pub filter: Option<String>,

    /// Minimum memory in MB
    #[arg(long, default_value = "10.0")]
    pub min_memory: f64,

    /// High memory threshold in MB
    #[arg(long, default_value = "500.0")]
    pub high_memory_threshold: f64,

    /// Output format for preview (table, json)
    #[arg(short = 'O', long, default_value = "table")]
    pub output: String,

    /// Sort by field (memory, cpu, pid, name, cwd)
    #[arg(short, long, default_value = "memory")]
    pub sort: String,

    /// Limit number of results
    #[arg(short = 'n', long)]
    pub limit: Option<usize>,

    /// Columns to display (comma-separated, for preview)
    #[arg(short = 'c', long)]
    pub columns: Option<String>,
}

#[derive(Args, Debug)]
pub struct MemoryArgs {
    /// Output format (table, json)
    #[arg(short, long, default_value = "table")]
    pub format: String,
}
