use crate::core::{ProcessInfo, CONFIRM_PREVIEW_LIMIT};
use ratatui::{
    layout::{Constraint, Layout, Rect},
    style::{Color, Modifier, Style},
    text::{Line, Span},
    widgets::{Block, Borders, List, ListItem, Paragraph},
    Frame,
};

pub struct ConfirmKillScreen {
    pub processes: Vec<ProcessInfo>,
    pub force: bool,
    pub selected: bool, // true = Yes, false = No
}

impl ConfirmKillScreen {
    pub fn new(processes: Vec<ProcessInfo>, force: bool) -> Self {
        Self {
            processes,
            force,
            selected: false,
        }
    }

    pub fn toggle_selection(&mut self) {
        self.selected = !self.selected;
    }

    pub fn select_yes(&mut self) {
        self.selected = true;
    }

    pub fn select_no(&mut self) {
        self.selected = false;
    }

    pub fn is_confirmed(&self) -> bool {
        self.selected
    }

    pub fn render(&self, frame: &mut Frame, area: Rect) {
        // Calculate total memory
        let total_memory: f64 = self.processes.iter().map(|p| p.rss_mb).sum();

        // Title
        let title = if self.force {
            format!("Force Kill {} process(es)?", self.processes.len())
        } else {
            format!("Kill {} process(es)?", self.processes.len())
        };

        // Create a centered dialog
        let dialog_area = centered_rect(60, 20, area);

        // Clear background
        let block = Block::default()
            .borders(Borders::ALL)
            .border_style(Style::default().fg(Color::Yellow))
            .title(title)
            .title_style(Style::default().add_modifier(Modifier::BOLD));

        frame.render_widget(block, dialog_area);

        // Inner layout
        let inner = dialog_area.inner(ratatui::layout::Margin {
            horizontal: 2,
            vertical: 1,
        });

        let chunks = Layout::default()
            .direction(ratatui::layout::Direction::Vertical)
            .constraints([
                Constraint::Length(2),  // Subtitle
                Constraint::Min(5),     // Process list
                Constraint::Length(3),  // Buttons
            ])
            .split(inner);

        // Subtitle
        let subtitle = Paragraph::new(format!("Will free ~{:.1} MB", total_memory))
            .style(Style::default().fg(Color::Gray));
        frame.render_widget(subtitle, chunks[0]);

        // Process list (limited)
        let mut items: Vec<ListItem> = self
            .processes
            .iter()
            .take(CONFIRM_PREVIEW_LIMIT)
            .map(|p| {
                let line = format!("PID {} - {} ({:.1} MB)", p.pid, p.name, p.rss_mb);
                ListItem::new(line)
            })
            .collect();

        if self.processes.len() > CONFIRM_PREVIEW_LIMIT {
            items.push(ListItem::new(format!(
                "... and {} more",
                self.processes.len() - CONFIRM_PREVIEW_LIMIT
            )));
        }

        let list = List::new(items).block(Block::default().borders(Borders::NONE));
        frame.render_widget(list, chunks[1]);

        // Buttons
        let yes_style = if self.selected {
            Style::default()
                .bg(Color::Green)
                .fg(Color::Black)
                .add_modifier(Modifier::BOLD)
        } else {
            Style::default().fg(Color::Green)
        };

        let no_style = if !self.selected {
            Style::default()
                .bg(Color::Red)
                .fg(Color::Black)
                .add_modifier(Modifier::BOLD)
        } else {
            Style::default().fg(Color::Red)
        };

        let buttons = Line::from(vec![
            Span::raw("  "),
            Span::styled("[Y]es", yes_style),
            Span::raw("  "),
            Span::styled("[N]o", no_style),
        ]);

        let buttons_para = Paragraph::new(buttons);
        frame.render_widget(buttons_para, chunks[2]);
    }
}

/// Create a centered rectangle
fn centered_rect(percent_x: u16, percent_y: u16, area: Rect) -> Rect {
    let popup_layout = Layout::default()
        .direction(ratatui::layout::Direction::Vertical)
        .constraints([
            Constraint::Percentage((100 - percent_y) / 2),
            Constraint::Percentage(percent_y),
            Constraint::Percentage((100 - percent_y) / 2),
        ])
        .split(area);

    Layout::default()
        .direction(ratatui::layout::Direction::Horizontal)
        .constraints([
            Constraint::Percentage((100 - percent_x) / 2),
            Constraint::Percentage(percent_x),
            Constraint::Percentage((100 - percent_x) / 2),
        ])
        .split(popup_layout[1])[1]
}
