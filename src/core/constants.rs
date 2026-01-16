/// Preview limit for CLI confirmations
pub const PREVIEW_LIMIT: usize = 5;

/// Preview limit for TUI confirmation dialogs
pub const CONFIRM_PREVIEW_LIMIT: usize = 10;

/// Display width for CWD column
pub const CWD_MAX_WIDTH: usize = 35;

/// Keep this many chars when truncating CWD
pub const CWD_TRUNCATE_WIDTH: usize = 32;

/// High memory threshold in MB
pub const HIGH_MEMORY_THRESHOLD_MB: f64 = 500.0;

/// System executable paths that indicate system services
pub const SYSTEM_EXE_PATHS: &[&str] = &["/usr/lib", "/usr/libexec", "/lib"];

/// Critical services that should not be killed
pub const CRITICAL_SERVICES: &[&str] = &[
    // Display/session managers
    "gnome-shell",
    "kwin",
    "kwin_x11",
    "kwin_wayland",
    "plasmashell",
    "mutter",
    // Audio
    "pipewire",
    "pipewire-pulse",
    "wireplumber",
    "pulseaudio",
    // Remote sessions
    "tmux",
    "tmux: server",
    "mosh-server",
    // Shells
    "zsh",
    "-zsh",
    "bash",
    "-bash",
    "fish",
    "-fish",
    "ssh",
    "sshd",
    // System services
    "systemd",
    "init",
    "dbus-daemon",
    "dbus-broker",
    // Desktop services
    "ibus-daemon",
    "gjs",
    "gnome-keyring-daemon",
];
