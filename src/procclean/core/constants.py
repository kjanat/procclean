"""Constants for process analysis."""

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
