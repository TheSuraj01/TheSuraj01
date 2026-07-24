#!/usr/bin/env python3
"""
tools/render_graph.py

Reads `assets/contributions.json` and builds an animated SVG `graph.svg`.
- 52-week x 7-day contribution grid with rounded cells.
- Custom dark terminal color ramp.
- Animates grid columns in a left-to-right wave reveal effect.
- Displays top header and bottom stats summary & legend.
"""

import json
import os
from datetime import datetime

INPUT_PATH = "assets/contributions.json"
OUTPUT_PATH = "graph.svg"

# Slate / Cyan / Blue terminal palette
COLOR_RAMP = ["#1e293b", "#0f4c81", "#1d72b8", "#38bdf8", "#7dd3fc"]
BG_COLOR = "#0D1117"
BORDER_COLOR = "#30363D"
TEXT_COLOR = "#8B949E"
HIGHLIGHT_COLOR = "#C9D1D9"

def build_graph_svg(data, output_path):
    days = data.get("days", [])
    if not days:
        print("Error: No days found in contribution data.")
        return

    # A GitHub graph is usually 53 columns (weeks) by 7 rows (days)
    # Group days by week columns
    # Find the start offset based on the first day's weekday
    weeks = []
    current_week = []
    
    # Fill leading blank days if first day is not Sunday
    first_weekday = days[0].get("weekday", 0)
    # Python weekday is Mon=0, Sun=6. GitHub graph is Sun=0.
    # Let's align to GitHub's Sun=0 start.
    gh_first_weekday = (first_weekday + 1) % 7
    
    for _ in range(gh_first_weekday):
        current_week.append(None)
        
    for d in days:
        current_week.append(d)
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []
            
    if current_week:
        # pad remaining days to 7
        while len(current_week) < 7:
            current_week.append(None)
        weeks.append(current_week)

    # We want to display exactly 52 or 53 weeks.
    weeks = weeks[-53:]

    # SVG layout sizing
    cell_size = 12
    cell_gap = 4
    grid_height = 7 * (cell_size + cell_gap) - cell_gap
    grid_width = len(weeks) * (cell_size + cell_gap) - cell_gap
    
    padding_x = 24
    padding_y = 20
    header_height = 36
    stats_height = 40
    
    total_width = grid_width + (padding_x * 2) + 30 # extra padding for day labels
    total_height = header_height + padding_y + grid_height + stats_height + padding_y

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_width} {total_height}" width="{total_width}" height="{total_height}">',
        '  <defs>',
        '    <style>',
        '      @keyframes fadeInWave {',
        '        0% { opacity: 0; transform: translateY(4px); }',
        '        100% { opacity: 1; transform: translateY(0); }',
        '      }',
        '      .text-font { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 11px; fill: ' + TEXT_COLOR + '; }',
        '      .text-bold { font-weight: 600; fill: ' + HIGHLIGHT_COLOR + '; }',
        '      .header-title { font-size: 12px; font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace; font-weight: 500; fill: ' + TEXT_COLOR + '; }',
        '      .day-label { font-size: 9px; fill: ' + TEXT_COLOR + '; }',
        '      .month-label { font-size: 10px; fill: ' + TEXT_COLOR + '; }',
        '    </style>',
        '  </defs>',
        '',
        '  <!-- Terminal Frame -->',
        f'  <rect x="0" y="0" width="{total_width}" height="{total_height}" rx="10" ry="10" fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1.5" />',
        '',
        '  <!-- Window Control Buttons -->',
        f'  <circle cx="20" cy="18" r="5" fill="#FF5F56" />',
        f'  <circle cx="36" cy="18" r="5" fill="#FFBD2E" />',
        f'  <circle cx="52" cy="18" r="5" fill="#27C93F" />',
        f'  <text x="{total_width / 2}" y="22" text-anchor="middle" class="header-title">$ cat contributions.log</text>',
        f'  <line x1="0" y1="{header_height}" x2="{total_width}" y2="{header_height}" stroke="{BORDER_COLOR}" stroke-width="1" />',
        '',
        f'  <g transform="translate({padding_x}, {header_height + padding_y})">',
        '    <!-- Day Labels -->'
    ]

    # Add day labels (Mon, Wed, Fri)
    day_labels = [("", 0), ("Mon", 1), ("", 2), ("Wed", 3), ("", 4), ("Fri", 5), ("", 6)]
    for label, r in day_labels:
        if label:
            y_pos = r * (cell_size + cell_gap) + 10
            svg_lines.append(f'    <text x="0" y="{y_pos}" class="day-label">{label}</text>')
            
    svg_lines.append('    <g transform="translate(24, 0)">')
    
    # Add cells column by column for wave animation
    for col_idx, week in enumerate(weeks):
        # Staggered animation delay based on column
        delay = col_idx * 0.03
        x_pos = col_idx * (cell_size + cell_gap)
        
        # Add a group for the column with animation
        svg_lines.append(f'      <g opacity="0" style="animation: fadeInWave 0.4s ease-out {delay}s forwards;">')
        
        for row_idx, day in enumerate(week):
            y_pos = row_idx * (cell_size + cell_gap)
            if day is None:
                continue
                
            level = day.get("level", 0)
            color = COLOR_RAMP[level] if level < len(COLOR_RAMP) else COLOR_RAMP[-1]
            
            tooltip = f'{day.get("count", 0)} contributions on {day.get("date", "")}'
            svg_lines.append(
                f'        <rect x="{x_pos}" y="{y_pos}" width="{cell_size}" height="{cell_size}" rx="2" ry="2" fill="{color}">'
                f'<title>{tooltip}</title></rect>'
            )
            
        svg_lines.append('      </g>')
        
    svg_lines.append('    </g>')
    
    # Stats & Legend at bottom
    stats_y = grid_height + 25
    total = data.get("total_contributions", 0)
    streak = data.get("current_streak", 0)
    longest = data.get("longest_streak", 0)
    
    svg_lines.append(f'    <g transform="translate(24, {stats_y})">')
    svg_lines.append(f'      <text x="0" y="0" class="text-font">Total: <tspan class="text-bold">{total}</tspan></text>')
    svg_lines.append(f'      <text x="120" y="0" class="text-font">Streak: <tspan class="text-bold">{streak} days</tspan></text>')
    svg_lines.append(f'      <text x="260" y="0" class="text-font">Longest: <tspan class="text-bold">{longest} days</tspan></text>')
    
    # Legend
    legend_x = grid_width - 90
    svg_lines.append(f'      <g transform="translate({legend_x}, -10)">')
    svg_lines.append('        <text x="-35" y="10" class="day-label">Less</text>')
    for i, color in enumerate(COLOR_RAMP):
        svg_lines.append(f'        <rect x="{i * 14}" y="0" width="10" height="10" rx="2" ry="2" fill="{color}" />')
    svg_lines.append(f'        <text x="{len(COLOR_RAMP) * 14 + 4}" y="10" class="day-label">More</text>')
    svg_lines.append('      </g>')
    
    svg_lines.append('    </g>')
    
    svg_lines.append('  </g>')
    svg_lines.append('</svg>')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))
        
    print(f"Graph SVG rendered -> {output_path}")

def main():
    if not os.path.exists(INPUT_PATH):
        print(f"Warning: {INPUT_PATH} not found. Ensure pull_contributions.py runs first.")
        return
        
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    build_graph_svg(data, OUTPUT_PATH)

if __name__ == "__main__":
    main()
