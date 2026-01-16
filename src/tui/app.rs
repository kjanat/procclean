use crate::core::{
    filter_by_cwd, filter_killable, filter_orphans, get_memory_summary, get_process_list,
    kill_processes, sort_processes, MemorySummary, ProcessInfo,
};
use crate::formatters::clip;
use crate::tui::screens::ConfirmKillScreen;
use anyhow::Result;
use crossterm::{
    event::{self, Event, KeyCode, KeyEventKind},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::CrosstermBackend,
    layout::{Constraint, Direction, Layout, Rect},
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, Borders, Cell, Gauge, List, ListItem, ListState, Row, Table, TableState},
    Frame, Terminal,
};
use std::io;
use std::time::{Duration, Instant};

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum View {
    All,
    Orphans,
    Killable,
    HighMemory,
}

impl View {
    fn as_str(&self) -> &str {
        match self {
            View::All => "All Processes",
            View::Orphans => "Orphans",
            View::Killable => "Killable",
            View::HighMemory => "High Memory",
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SortKey {
    Memory,
    Cpu,
    Pid,
    Name,
    Cwd,
}

impl SortKey {
    fn as_str(&self) -> &str {
        match self {
            SortKey::Memory => "memory",
            SortKey::Cpu => "cpu",
            SortKey::Pid => "pid",
            SortKey::Name => "name",
            SortKey::Cwd => "cwd",
        }
    }
}

pub struct App {
    processes: Vec<ProcessInfo>,
    filtered_processes: Vec<ProcessInfo>,
    selected: Vec<usize>, // Indices of selected processes
    table_state: TableState,
    view: View,
    sort_key: SortKey,
    sort_reverse: bool,
    cwd_filter: Option<String>,
    memory_summary: MemorySummary,
    last_refresh: Instant,
    confirm_screen: Option<ConfirmKillScreen>,
    sidebar_state: ListState,
    should_quit: bool,
}

impl App {
    pub fn new() -> Result<Self> {
        let processes = get_process_list("memory", None, 10.0)?;
        let filtered_processes = processes.clone();
        let memory_summary = get_memory_summary();

        Ok(Self {
            processes,
            filtered_processes,
            selected: Vec::new(),
            table_state: TableState::default().with_selected(Some(0)),
            view: View::All,
            sort_key: SortKey::Memory,
            sort_reverse: true,
            cwd_filter: None,
            memory_summary,
            last_refresh: Instant::now(),
            confirm_screen: None,
            sidebar_state: ListState::default().with_selected(Some(0)),
            should_quit: false,
        })
    }

    pub fn run(&mut self) -> Result<()> {
        // Setup terminal
        enable_raw_mode()?;
        let mut stdout = io::stdout();
        execute!(stdout, EnterAlternateScreen)?;
        let backend = CrosstermBackend::new(stdout);
        let mut terminal = Terminal::new(backend)?;

        // Main loop
        loop {
            terminal.draw(|f| self.render(f))?;

            // Handle events with timeout for auto-refresh
            if event::poll(Duration::from_millis(100))? {
                if let Event::Key(key) = event::read()? {
                    if key.kind == KeyEventKind::Press {
                        self.handle_key(key.code)?;
                    }
                }
            }

            // Auto-refresh every 5 seconds
            if self.last_refresh.elapsed() > Duration::from_secs(5) {
                self.refresh()?;
            }

            if self.should_quit {
                break;
            }
        }

        // Restore terminal
        disable_raw_mode()?;
        execute!(terminal.backend_mut(), LeaveAlternateScreen)?;

        Ok(())
    }

    fn handle_key(&mut self, key: KeyCode) -> Result<()> {
        // Handle confirm screen if active
        if let Some(confirm_screen) = &mut self.confirm_screen {
            match key {
                KeyCode::Char('y') | KeyCode::Char('Y') => {
                    confirm_screen.select_yes();
                    self.do_kill()?;
                    self.confirm_screen = None;
                }
                KeyCode::Char('n') | KeyCode::Char('N') | KeyCode::Esc => {
                    self.confirm_screen = None;
                }
                KeyCode::Left | KeyCode::Right | KeyCode::Tab => {
                    confirm_screen.toggle_selection();
                }
                KeyCode::Enter => {
                    if confirm_screen.is_confirmed() {
                        self.do_kill()?;
                    }
                    self.confirm_screen = None;
                }
                _ => {}
            }
            return Ok(());
        }

        // Normal key handling
        match key {
            KeyCode::Char('q') => self.should_quit = true,
            KeyCode::Char('r') => self.refresh()?,
            KeyCode::Char('k') => self.show_kill_confirm(false),
            KeyCode::Char('K') => self.show_kill_confirm(true),
            KeyCode::Char('o') => self.set_view(View::Orphans)?,
            KeyCode::Char('O') => self.set_view(View::Killable)?,
            KeyCode::Char('a') => self.set_view(View::All)?,
            KeyCode::Char('m') => self.set_view(View::HighMemory)?,
            KeyCode::Char('w') => self.filter_by_current_cwd()?,
            KeyCode::Char('W') => self.clear_cwd_filter()?,
            KeyCode::Char(' ') => self.toggle_current_selection(),
            KeyCode::Char('s') => self.select_all(),
            KeyCode::Char('c') => self.clear_selection(),
            KeyCode::Char('1') => self.set_sort(SortKey::Memory)?,
            KeyCode::Char('2') => self.set_sort(SortKey::Cpu)?,
            KeyCode::Char('3') => self.set_sort(SortKey::Pid)?,
            KeyCode::Char('4') => self.set_sort(SortKey::Name)?,
            KeyCode::Char('5') => self.set_sort(SortKey::Cwd)?,
            KeyCode::Char('!') => self.toggle_sort_order()?,
            KeyCode::Up => self.previous_row(),
            KeyCode::Down => self.next_row(),
            KeyCode::PageUp => self.page_up(),
            KeyCode::PageDown => self.page_down(),
            KeyCode::Home => self.first_row(),
            KeyCode::End => self.last_row(),
            _ => {}
        }

        Ok(())
    }

    fn render(&mut self, frame: &mut Frame) {
        let chunks = Layout::default()
            .direction(Direction::Vertical)
            .constraints([
                Constraint::Length(3), // Header + memory bar
                Constraint::Min(10),   // Main content
                Constraint::Length(3), // Footer
            ])
            .split(frame.area());

        // Render header and memory bar
        self.render_header(frame, chunks[0]);

        // Main content area (sidebar + table)
        let main_chunks = Layout::default()
            .direction(Direction::Horizontal)
            .constraints([Constraint::Length(20), Constraint::Min(40)])
            .split(chunks[1]);

        self.render_sidebar(frame, main_chunks[0]);
        self.render_table(frame, main_chunks[1]);

        // Footer
        self.render_footer(frame, chunks[2]);

        // Confirm screen overlay
        if let Some(confirm_screen) = &self.confirm_screen {
            confirm_screen.render(frame, frame.area());
        }
    }

    fn render_header(&self, frame: &mut Frame, area: Rect) {
        let title = format!("procclean - {} processes", self.filtered_processes.len());

        let header_chunks = Layout::default()
            .direction(Direction::Vertical)
            .constraints([Constraint::Length(1), Constraint::Length(2)])
            .split(area);

        // Title
        let title_block = Block::default()
            .borders(Borders::BOTTOM)
            .title(title)
            .title_style(Style::default().add_modifier(Modifier::BOLD));
        frame.render_widget(title_block, header_chunks[0]);

        // Memory bar
        let mem_percent = self.memory_summary.percent;
        let mem_label = format!(
            "Memory: {:.1}/{:.1} GB ({:.0}%) | Swap: {:.1}/{:.1} GB",
            self.memory_summary.used_gb,
            self.memory_summary.total_gb,
            mem_percent,
            self.memory_summary.swap_used_gb,
            self.memory_summary.swap_total_gb,
        );

        let gauge = Gauge::default()
            .block(Block::default())
            .gauge_style(
                Style::default()
                    .fg(if mem_percent > 80.0 {
                        Color::Red
                    } else if mem_percent > 60.0 {
                        Color::Yellow
                    } else {
                        Color::Green
                    })
                    .bg(Color::Black),
            )
            .label(mem_label)
            .ratio(mem_percent / 100.0);

        frame.render_widget(gauge, header_chunks[1]);
    }

    fn render_sidebar(&mut self, frame: &mut Frame, area: Rect) {
        let views = vec![
            ("a", View::All),
            ("o", View::Orphans),
            ("O", View::Killable),
            ("m", View::HighMemory),
        ];

        let items: Vec<ListItem> = views
            .iter()
            .map(|(key, view)| {
                let style = if *view == self.view {
                    Style::default()
                        .fg(Color::Black)
                        .bg(Color::Cyan)
                        .add_modifier(Modifier::BOLD)
                } else {
                    Style::default()
                };

                let content = format!(" [{}] {}", key, view.as_str());
                ListItem::new(content).style(style)
            })
            .collect();

        let list = List::new(items).block(
            Block::default()
                .borders(Borders::ALL)
                .border_style(Style::default().fg(Color::Gray))
                .title("Views"),
        );

        frame.render_stateful_widget(list, area, &mut self.sidebar_state);
    }

    fn render_table(&mut self, frame: &mut Frame, area: Rect) {
        let header_cells = [
            "Sel", "PID", "Name", "RAM (MB)", "CPU%", "CWD", "PPID", "Parent", "Status",
        ]
        .iter()
        .map(|h| Cell::from(*h).style(Style::default().add_modifier(Modifier::BOLD)));
        let header = Row::new(header_cells).height(1).bottom_margin(0);

        let rows: Vec<Row> = self
            .filtered_processes
            .iter()
            .enumerate()
            .map(|(idx, proc)| {
                let sel_mark = if self.selected.contains(&idx) {
                    "[X]"
                } else {
                    "[ ]"
                };

                let cwd_display = clip(&proc.cwd, 35, crate::formatters::ClipSide::Left);

                let cells = vec![
                    Cell::from(sel_mark),
                    Cell::from(proc.pid.to_string()),
                    Cell::from(proc.name.clone()),
                    Cell::from(format!("{:.1}", proc.rss_mb)),
                    Cell::from(format!("{:.1}", proc.cpu_percent)),
                    Cell::from(cwd_display),
                    Cell::from(proc.ppid.to_string()),
                    Cell::from(proc.parent_name.clone()),
                    Cell::from(proc.display_status()),
                ];

                Row::new(cells).height(1)
            })
            .collect();

        let title = if let Some(cwd) = &self.cwd_filter {
            format!("Processes (CWD: {})", cwd)
        } else {
            "Processes".to_string()
        };

        let table = Table::new(
            rows,
            [
                Constraint::Length(5),
                Constraint::Length(8),
                Constraint::Length(20),
                Constraint::Length(10),
                Constraint::Length(8),
                Constraint::Length(35),
                Constraint::Length(8),
                Constraint::Length(15),
                Constraint::Min(20),
            ],
        )
        .header(header)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .border_style(Style::default().fg(Color::Gray))
                .title(title),
        )
        .row_highlight_style(
            Style::default()
                .bg(Color::DarkGray)
                .add_modifier(Modifier::BOLD),
        );

        frame.render_stateful_widget(table, area, &mut self.table_state);
    }

    fn render_footer(&self, frame: &mut Frame, area: Rect) {
        let selected_count = self.selected.len();
        let selected_memory: f64 = self
            .selected
            .iter()
            .filter_map(|&idx| self.filtered_processes.get(idx))
            .map(|p| p.rss_mb)
            .sum();

        let status_text = if selected_count > 0 {
            format!(
                "Selected: {} ({:.1} MB) | Sort: {} {}",
                selected_count,
                selected_memory,
                self.sort_key.as_str(),
                if self.sort_reverse { "↓" } else { "↑" }
            )
        } else {
            format!(
                "Sort: {} {}",
                self.sort_key.as_str(),
                if self.sort_reverse { "↓" } else { "↑" }
            )
        };

        let footer_text = vec![
            Line::from(vec![
                Span::styled(
                    " q:Quit r:Refresh k:Kill K:ForceKill space:Select s:SelectAll c:Clear w:FilterCWD W:ClearCWD ",
                    Style::default().fg(Color::Gray),
                ),
            ]),
            Line::from(vec![Span::styled(
                format!(" {} ", status_text),
                Style::default().fg(Color::Cyan),
            )]),
        ];

        let footer = ratatui::widgets::Paragraph::new(footer_text)
            .block(Block::default().borders(Borders::TOP));

        frame.render_widget(footer, area);
    }

    fn refresh(&mut self) -> Result<()> {
        let cursor_pos = self.table_state.selected();

        self.processes = get_process_list(self.sort_key.as_str(), None, 10.0)?;
        self.memory_summary = get_memory_summary();
        self.apply_filters()?;
        self.last_refresh = Instant::now();

        // Restore cursor position
        if let Some(pos) = cursor_pos {
            if pos < self.filtered_processes.len() {
                self.table_state.select(Some(pos));
            } else if !self.filtered_processes.is_empty() {
                self.table_state
                    .select(Some(self.filtered_processes.len() - 1));
            }
        }

        // Clear invalid selections
        self.selected
            .retain(|&idx| idx < self.filtered_processes.len());

        Ok(())
    }

    fn apply_filters(&mut self) -> Result<()> {
        self.filtered_processes = self.processes.clone();

        // Apply view filter
        match self.view {
            View::All => {}
            View::Orphans => {
                self.filtered_processes = filter_orphans(&self.filtered_processes);
            }
            View::Killable => {
                self.filtered_processes = filter_killable(&self.filtered_processes);
            }
            View::HighMemory => {
                self.filtered_processes =
                    crate::core::filter_high_memory(&self.filtered_processes, 500.0);
            }
        }

        // Apply CWD filter
        if let Some(cwd) = &self.cwd_filter {
            self.filtered_processes = filter_by_cwd(&self.filtered_processes, cwd);
        }

        // Sort
        sort_processes(
            &mut self.filtered_processes,
            self.sort_key.as_str(),
            self.sort_reverse,
        );

        Ok(())
    }

    fn set_view(&mut self, view: View) -> Result<()> {
        self.view = view;
        self.apply_filters()?;
        self.clear_selection();
        self.table_state.select(Some(0));
        Ok(())
    }

    fn set_sort(&mut self, key: SortKey) -> Result<()> {
        // If same key, toggle order
        if self.sort_key == key {
            self.sort_reverse = !self.sort_reverse;
        } else {
            self.sort_key = key;
            // Default reverse for memory/cpu/pid, ascending for name/cwd
            self.sort_reverse = matches!(key, SortKey::Memory | SortKey::Cpu | SortKey::Pid);
        }
        self.apply_filters()?;
        Ok(())
    }

    fn toggle_sort_order(&mut self) -> Result<()> {
        self.sort_reverse = !self.sort_reverse;
        self.apply_filters()?;
        Ok(())
    }

    fn filter_by_current_cwd(&mut self) -> Result<()> {
        if let Some(selected) = self.table_state.selected() {
            if let Some(proc) = self.filtered_processes.get(selected) {
                self.cwd_filter = Some(proc.cwd.clone());
                self.apply_filters()?;
                self.clear_selection();
                self.table_state.select(Some(0));
            }
        }
        Ok(())
    }

    fn clear_cwd_filter(&mut self) -> Result<()> {
        self.cwd_filter = None;
        self.apply_filters()?;
        self.clear_selection();
        self.table_state.select(Some(0));
        Ok(())
    }

    fn toggle_current_selection(&mut self) {
        if let Some(selected) = self.table_state.selected() {
            if let Some(pos) = self.selected.iter().position(|&x| x == selected) {
                self.selected.remove(pos);
            } else {
                self.selected.push(selected);
            }
        }
    }

    fn select_all(&mut self) {
        self.selected = (0..self.filtered_processes.len()).collect();
    }

    fn clear_selection(&mut self) {
        self.selected.clear();
    }

    fn show_kill_confirm(&mut self, force: bool) {
        let targets: Vec<ProcessInfo> = self
            .selected
            .iter()
            .filter_map(|&idx| self.filtered_processes.get(idx).cloned())
            .collect();

        if !targets.is_empty() {
            self.confirm_screen = Some(ConfirmKillScreen::new(targets, force));
        }
    }

    fn do_kill(&mut self) -> Result<()> {
        if let Some(confirm_screen) = &self.confirm_screen {
            let pids: Vec<u32> = confirm_screen.processes.iter().map(|p| p.pid).collect();
            let _ = kill_processes(&pids, confirm_screen.force);

            // Refresh after kill
            self.clear_selection();
            self.refresh()?;
        }
        Ok(())
    }

    fn next_row(&mut self) {
        if self.filtered_processes.is_empty() {
            return;
        }
        let i = match self.table_state.selected() {
            Some(i) => {
                if i >= self.filtered_processes.len() - 1 {
                    0
                } else {
                    i + 1
                }
            }
            None => 0,
        };
        self.table_state.select(Some(i));
    }

    fn previous_row(&mut self) {
        if self.filtered_processes.is_empty() {
            return;
        }
        let i = match self.table_state.selected() {
            Some(i) => {
                if i == 0 {
                    self.filtered_processes.len() - 1
                } else {
                    i - 1
                }
            }
            None => 0,
        };
        self.table_state.select(Some(i));
    }

    fn page_up(&mut self) {
        if self.filtered_processes.is_empty() {
            return;
        }
        let i = self.table_state.selected().unwrap_or(0);
        let new_i = i.saturating_sub(10);
        self.table_state.select(Some(new_i));
    }

    fn page_down(&mut self) {
        if self.filtered_processes.is_empty() {
            return;
        }
        let i = self.table_state.selected().unwrap_or(0);
        let new_i = (i + 10).min(self.filtered_processes.len() - 1);
        self.table_state.select(Some(new_i));
    }

    fn first_row(&mut self) {
        if !self.filtered_processes.is_empty() {
            self.table_state.select(Some(0));
        }
    }

    fn last_row(&mut self) {
        if !self.filtered_processes.is_empty() {
            self.table_state
                .select(Some(self.filtered_processes.len() - 1));
        }
    }
}
