#!/usr/bin/env python3
"""
tools/render_panel.py

Renders a terminal "system info" style panel SVG (`sysinfo.svg`).
Supports `PREVIEW=1` environment variable for rendering a static preview frame.
"""

import os
import sys

ROWS = [
    ("user", "thesuraj01 (Suraj Kumar Yadav)"),
    ("role", "Software Engineer @ Spotline, Inc."),
    ("focus", "AI & ML · Systems Architecture"),
    ("stack", "Python · TypeScript · React · Next.js · Go · Rust"),
    ("now", "Building Agentic-RAG & Multi-Agent Systems"),
    ("location", "India"),
    ("links", "surajkumaryadavin.vercel.app · github.com/thesuraj01")
]

def escape_xml(text):
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

def render_panel(output_path="sysinfo.svg", is_preview=False):
    width = 460
    header_height = 36
    padding_x = 20
    padding_y = 20
    row_height = 28
    
    total_height = header_height + (padding_y * 2) + (len(ROWS) * row_height) + 20

    bg_color = "#0D1117"
    border_color = "#30363D"
    key_color = "#8B949E"
    val_color = "#C9D1D9"
    accent_color = "#38BDF8"
    prompt_color = "#27C93F"

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {total_height}" width="{width}" height="{total_height}">')
    svg.append('  <defs>')
    svg.append('    <style>')
    svg.append('      @keyframes rowFadeIn {')
    svg.append('        0% { opacity: 0; transform: translateX(-6px); }')
    svg.append('        100% { opacity: 1; transform: translateX(0); }')
    svg.append('      }')
    svg.append('      @keyframes cursorBlink {')
    svg.append('        0%, 100% { opacity: 1; }')
    svg.append('        50% { opacity: 0; }')
    svg.append('      }')
    svg.append('      .term-header { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: 500; fill: #8B949E; }')
    svg.append('      .term-code { font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace; font-size: 12px; }')
    svg.append('      .key-text { fill: ' + key_color + '; font-weight: 500; }')
    svg.append('      .val-text { fill: ' + val_color + '; font-weight: 600; }')
    svg.append('      .accent-text { fill: ' + accent_color + '; font-weight: 600; }')
    svg.append('      .prompt-symbol { fill: ' + prompt_color + '; font-weight: 700; }')
    svg.append('    </style>')
    svg.append('  </defs>')
    svg.append('')
    svg.append('  <!-- Terminal Frame -->')
    svg.append(f'  <rect x="0" y="0" width="{width}" height="{total_height}" rx="10" ry="10" fill="{bg_color}" stroke="{border_color}" stroke-width="1.5" />')
    svg.append('')
    svg.append('  <!-- Window Control Buttons -->')
    svg.append('  <circle cx="20" cy="18" r="5" fill="#FF5F56" />')
    svg.append('  <circle cx="36" cy="18" r="5" fill="#FFBD2E" />')
    svg.append('  <circle cx="52" cy="18" r="5" fill="#27C93F" />')
    svg.append(f'  <text x="{width / 2}" y="22" text-anchor="middle" class="term-header">sysinfo --verbose</text>')
    svg.append(f'  <line x1="0" y1="{header_height}" x2="{width}" y2="{header_height}" stroke="{border_color}" stroke-width="1" />')
    svg.append('')
    svg.append(f'  <g transform="translate({padding_x}, {header_height + padding_y})">')

    delay_step = 0.15
    start_y = 12

    for idx, (key, val) in enumerate(ROWS):
        y_pos = start_y + (idx * row_height)
        delay = 0.0 if is_preview else round(idx * delay_step, 2)
        
        anim_attr = "" if is_preview else f'opacity="0" style="animation: rowFadeIn 0.35s ease-out {delay}s forwards;"'
        
        key_str = escape_xml(key)
        val_str = escape_xml(val)
        
        # Color highlight for key role/stack values
        val_class = "accent-text" if key in ("role", "now") else "val-text"

        svg.append(f'    <g transform="translate(0, {y_pos})" {anim_attr}>')
        svg.append(f'      <text x="0" y="0" class="term-code prompt-symbol">&#x276F;</text>')
        svg.append(f'      <text x="16" y="0" class="term-code key-text">{key_str}:</text>')
        svg.append(f'      <text x="96" y="0" class="term-code {val_class}">{val_str}</text>')
        svg.append(f'    </g>')

    # Terminal Prompt & Blinking Cursor Row at bottom
    cursor_y = start_y + (len(ROWS) * row_height)
    cursor_delay = 0.0 if is_preview else round(len(ROWS) * delay_step, 2)
    cursor_anim_attr = "" if is_preview else f'opacity="0" style="animation: rowFadeIn 0.35s ease-out {cursor_delay}s forwards;"'

    svg.append(f'    <g transform="translate(0, {cursor_y})" {cursor_anim_attr}>')
    svg.append(f'      <text x="0" y="0" class="term-code prompt-symbol">&#x276F;</text>')
    svg.append(f'      <text x="16" y="0" class="term-code val-text">status: active</text>')
    svg.append(f'      <rect x="116" y="-10" width="7" height="13" fill="{accent_color}" style="animation: cursorBlink 1s infinite;" />')
    svg.append(f'    </g>')

    svg.append('  </g>')
    svg.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg))

    print(f"System info panel SVG rendered ({'preview mode' if is_preview else 'animated mode'}) -> {output_path}")

def main():
    is_preview = os.environ.get("PREVIEW", "0") in ("1", "true", "TRUE")
    render_panel("sysinfo.svg", is_preview=is_preview)

if __name__ == "__main__":
    main()
