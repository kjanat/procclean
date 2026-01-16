"""
Main entry point for procclean CLI
"""

import os
import subprocess
import sys
from pathlib import Path


def find_binary() -> Path | None:
    """Find the procclean binary (Rust executable)"""
    # Check if running from development
    dev_binary = Path(__file__).parent.parent.parent / "target" / "release" / "procclean"
    if dev_binary.exists():
        return dev_binary

    # Check in PATH
    try:
        result = subprocess.run(
            ["which", "procclean"],
            capture_output=True,
            text=True,
            check=True,
        )
        binary_path = Path(result.stdout.strip())
        if binary_path.exists():
            return binary_path
    except subprocess.CalledProcessError:
        pass

    # Check in package directory (for installed wheels)
    package_dir = Path(__file__).parent
    possible_locations = [
        package_dir / "bin" / "procclean",
        package_dir / "procclean",
    ]

    for location in possible_locations:
        if location.exists() and location.is_file():
            return location

    return None


def main():
    """Main entry point - delegates to Rust binary"""
    binary = find_binary()

    if binary is None:
        print("Error: procclean binary not found.", file=sys.stderr)
        print("", file=sys.stderr)
        print("The Rust binary is required for procclean to run.", file=sys.stderr)
        print("Please ensure procclean is properly installed:", file=sys.stderr)
        print("  pip install procclean", file=sys.stderr)
        print("", file=sys.stderr)
        print("Or build from source:", file=sys.stderr)
        print("  cargo build --release", file=sys.stderr)
        sys.exit(1)

    # Execute the Rust binary with all arguments
    try:
        result = subprocess.run(
            [str(binary)] + sys.argv[1:],
            check=False,
        )
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"Error running procclean: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
