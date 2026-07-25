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

# Cyberpunk Neon palette
COLOR_RAMP = ["#0b0914", "#4a00e0", "#8e2de2", "#f000ff", "#00f3ff"]
BG_COLOR = "#050510"
BORDER_COLOR = "#9d4edd"
TEXT_COLOR = "#00f3ff"
HIGHLIGHT_COLOR = "#f000ff"

def build_graph_svg(data, output_path):
    days = data.get("days", [])
    if not days:
        print("Error: No days found in contribution data.")
        return

    weeks = []
    current_week = []
    
    first_weekday = days[0].get("weekday", 0)
    gh_first_weekday = (first_weekday + 1) % 7
    
    for _ in range(gh_first_weekday):
        current_week.append(None)
        
    for d in days:
        current_week.append(d)
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []
            
    if current_week:
        while len(current_week) < 7:
            current_week.append(None)
        weeks.append(current_week)

    weeks = weeks[-53:]

    cell_size = 12
    cell_gap = 4
    grid_height = 7 * (cell_size + cell_gap) - cell_gap
    grid_width = len(weeks) * (cell_size + cell_gap) - cell_gap
    
    padding_x = 24
    padding_y = 20
    header_height = 36
    stats_height = 40
    
    total_width = grid_width + (padding_x * 2) + 30
    total_height = header_height + padding_y + grid_height + stats_height + padding_y

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_width} {total_height}" width="{total_width}" height="{total_height}">',
        '  <defs>',
        '    <filter id="neonGlow" x="-20%" y="-20%" width="140%" height="140%">',
        '      <feGaussianBlur stdDeviation="2" result="blur" />',
        '      <feMerge>',
        '        <feMergeNode in="blur" />',
        '        <feMergeNode in="SourceGraphic" />',
        '      </feMerge>',
        '    </filter>',
        '    <style>',
        '      @keyframes fadeInWave {',
        '        0% { opacity: 0; transform: translateY(4px); }',
        '        100% { opacity: 1; transform: translateY(0); }',
        '      }',
        '      @keyframes glitch {',
        '        0% { transform: translate(0) }',
        '        20% { transform: translate(-2px, 1px) }',
        '        40% { transform: translate(-1px, -1px) }',
        '        60% { transform: translate(2px, 1px) }',
        '        80% { transform: translate(1px, -1px) }',
        '        100% { transform: translate(0) }',
        '      }',
        '      .text-font { font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 11px; fill: ' + TEXT_COLOR + '; }',
        '      .text-bold { font-weight: 700; fill: ' + HIGHLIGHT_COLOR + '; }',
        '      .header-title { font-size: 12px; font-family: "JetBrains Mono", "Fira Code", monospace; font-weight: 700; fill: ' + HIGHLIGHT_COLOR + '; letter-spacing: 1px; }',
        '      .day-label { font-size: 9px; fill: ' + TEXT_COLOR + '; font-family: monospace; }',
        '    </style>',
        '  </defs>',
        '',
        '  <!-- Cyberpunk Frame -->',
        f'  <rect x="0" y="0" width="{total_width}" height="{total_height}" rx="4" ry="4" fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="2" filter="url(#neonGlow)" />',
        '',
        '  <!-- HUD Controls -->',
        f'  <path d="M 15 12 L 25 12 L 30 18 L 40 18" stroke="{HIGHLIGHT_COLOR}" stroke-width="2" fill="none" filter="url(#neonGlow)" />',
        f'  <path d="M {total_width - 40} 18 L {total_width - 30} 18 L {total_width - 25} 12 L {total_width - 15} 12" stroke="{TEXT_COLOR}" stroke-width="2" fill="none" filter="url(#neonGlow)" />',
        f'  <text x="{total_width / 2}" y="22" text-anchor="middle" class="header-title" style="animation: glitch 3s infinite;">[ SYS :: UPLINK_DATA :: CONTRIBUTIONS ]</text>',
        f'  <line x1="0" y1="{header_height}" x2="{total_width}" y2="{header_height}" stroke="{BORDER_COLOR}" stroke-width="1" stroke-dasharray="4 2" />',
        '',
        f'  <g transform="translate({padding_x}, {header_height + padding_y})">',
        '    <!-- Day Labels -->'
    ]

    day_labels = [("", 0), ("MON", 1), ("", 2), ("WED", 3), ("", 4), ("FRI", 5), ("", 6)]
    for label, r in day_labels:
        if label:
            y_pos = r * (cell_size + cell_gap) + 10
            svg_lines.append(f'    <text x="0" y="{y_pos}" class="day-label">{label}</text>')
            
    svg_lines.append('    <g transform="translate(26, 0)">')
    
    for col_idx, week in enumerate(weeks):
        delay = col_idx * 0.03
        x_pos = col_idx * (cell_size + cell_gap)
        
        svg_lines.append(f'      <g opacity="0" style="animation: fadeInWave 0.4s ease-out {delay}s forwards;">')
        
        for row_idx, day in enumerate(week):
            y_pos = row_idx * (cell_size + cell_gap)
            if day is None:
                continue
                
            level = day.get("level", 0)
            color = COLOR_RAMP[level] if level < len(COLOR_RAMP) else COLOR_RAMP[-1]
            glow_attr = ' filter="url(#neonGlow)"' if level > 0 else ''
            
            tooltip = f'{day.get("count", 0)} contributions on {day.get("date", "")}'
            svg_lines.append(
                f'        <rect x="{x_pos}" y="{y_pos}" width="{cell_size}" height="{cell_size}" rx="1" ry="1" fill="{color}"{glow_attr}>'
                f'<title>{tooltip}</title></rect>'
            )
            
        svg_lines.append('      </g>')
        
    svg_lines.append('    </g>')
    
    stats_y = grid_height + 25
    total = data.get("total_contributions", 0)
    streak = data.get("current_streak", 0)
    longest = data.get("longest_streak", 0)
    
    svg_lines.append(f'    <g transform="translate(26, {stats_y})">')
    svg_lines.append(f'      <text x="0" y="0" class="text-font">TOTAL &gt; <tspan class="text-bold">{total}</tspan></text>')
    svg_lines.append(f'      <text x="120" y="0" class="text-font">STREAK &gt; <tspan class="text-bold">{streak} DAYS</tspan></text>')
    svg_lines.append(f'      <text x="260" y="0" class="text-font">PEAK &gt; <tspan class="text-bold">{longest} DAYS</tspan></text>')
    
    legend_x = grid_width - 90
    svg_lines.append(f'      <g transform="translate({legend_x}, -10)">')
    svg_lines.append('        <text x="-30" y="9" class="day-label">MIN</text>')
    for i, color in enumerate(COLOR_RAMP):
        glow_attr = ' filter="url(#neonGlow)"' if i > 0 else ''
        svg_lines.append(f'        <rect x="{i * 14}" y="0" width="10" height="10" rx="1" ry="1" fill="{color}"{glow_attr} />')
    svg_lines.append(f'        <text x="{len(COLOR_RAMP) * 14 + 4}" y="9" class="day-label">MAX</text>')
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
