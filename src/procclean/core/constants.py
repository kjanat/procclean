"""Constants for process analysis."""

# Display constants
PREVIEW_LIMIT = 5  # Number of processes to show in previews
CONFIRM_PREVIEW_LIMIT = 10  # Number of processes to show in confirm dialogs
CWD_MAX_WIDTH = 35  # Max width for cwd column display
CWD_TRUNCATE_WIDTH = 32  # Width to keep when truncating cwd

# Memory thresholds
HIGH_MEMORY_THRESHOLD_MB = 500  # Default threshold for high memory filter

# System library paths - executables here are system services
SYSTEM_EXE_PATHS = ("/usr/lib", "/usr/libexec", "/lib")

# Critical services in /usr/bin that should never be killed
# (session managers, audio, shells, display, auth)
CRITICAL_SERVICES = {
    # Display/session
    "gnome-shell",
    "kwin",
    "plasmashell",
    "mutter",
    # Audio
    "pipewire",
    "pipewire-pulse",
    "wireplumber",
    "pulseaudio",
    # Remote sessions
    "tmux: server",
    "tmux",
    "mosh-server",
    # Shells
    "zsh",
    "-zsh",
    "bash",
    "-bash",
    "ssh",
    "sshd",
    # System
    "systemd",
    "init",
    "dbus-daemon",
    "dbus-broker",
    # Desktop services
    "ibus-daemon",
    "gjs",
    "gnome-keyring-daemon",
}
