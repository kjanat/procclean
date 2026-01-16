use anyhow::Result;
use clap::Parser;
use procclean::{
    cli::{cmd_groups, cmd_kill, cmd_list, cmd_memory, Cli, Commands},
    tui::App,
};

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Some(Commands::List(args)) => cmd_list(args)?,
        Some(Commands::Groups(args)) => cmd_groups(args)?,
        Some(Commands::Kill(args)) => cmd_kill(args)?,
        Some(Commands::Memory(args)) => cmd_memory(args)?,
        None => {
            // No command specified, launch TUI
            let mut app = App::new()?;
            app.run()?;
        }
    }

    Ok(())
}
