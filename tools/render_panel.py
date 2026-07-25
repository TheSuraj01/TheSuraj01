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

    bg_color = "#050510"
    border_color = "#9d4edd"
    key_color = "#00f3ff"
    val_color = "#e2e8f0"
    accent_color = "#f000ff"
    prompt_color = "#00ff66"
    grid_color = "#1a103c"

    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {total_height}" width="{width}" height="{total_height}">')
    svg.append('  <defs>')
    svg.append('    <filter id="neonGlow" x="-20%" y="-20%" width="140%" height="140%">')
    svg.append('      <feGaussianBlur stdDeviation="2" result="blur" />')
    svg.append('      <feMerge>')
    svg.append('        <feMergeNode in="blur" />')
    svg.append('        <feMergeNode in="SourceGraphic" />')
    svg.append('      </feMerge>')
    svg.append('    </filter>')
    svg.append('    <pattern id="hexGrid" width="10" height="17.32" patternUnits="userSpaceOnUse" patternTransform="scale(0.5)">')
    svg.append(f'      <path d="M5 0 L10 2.88 L10 8.66 L5 11.54 L0 8.66 L0 2.88 Z" fill="none" stroke="{grid_color}" stroke-width="1"/>')
    svg.append('    </pattern>')
    svg.append('    <style>')
    svg.append('      @keyframes rowFadeIn {')
    svg.append('        0% { opacity: 0; transform: translateX(-6px); }')
    svg.append('        100% { opacity: 1; transform: translateX(0); }')
    svg.append('      }')
    svg.append('      @keyframes cursorBlink {')
    svg.append('        0%, 100% { opacity: 1; }')
    svg.append('        50% { opacity: 0; }')
    svg.append('      }')
    svg.append('      @keyframes glitch {')
    svg.append('        0% { transform: translate(0) }')
    svg.append('        20% { transform: translate(-2px, 1px) }')
    svg.append('        40% { transform: translate(-1px, -1px) }')
    svg.append('        60% { transform: translate(2px, 1px) }')
    svg.append('        80% { transform: translate(1px, -1px) }')
    svg.append('        100% { transform: translate(0) }')
    svg.append('      }')
    svg.append('      .term-header { font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 11px; font-weight: 700; fill: ' + accent_color + '; letter-spacing: 1px; }')
    svg.append('      .term-code { font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace; font-size: 12px; }')
    svg.append('      .key-text { fill: ' + key_color + '; font-weight: 600; filter: url(#neonGlow); }')
    svg.append('      .val-text { fill: ' + val_color + '; font-weight: 500; }')
    svg.append('      .accent-text { fill: ' + accent_color + '; font-weight: 600; filter: url(#neonGlow); }')
    svg.append('      .prompt-symbol { fill: ' + prompt_color + '; font-weight: 700; filter: url(#neonGlow); }')
    svg.append('    </style>')
    svg.append('  </defs>')
    svg.append('')
    svg.append('  <!-- Cyberpunk Frame -->')
    svg.append(f'  <rect x="0" y="0" width="{width}" height="{total_height}" rx="4" ry="4" fill="{bg_color}" stroke="{border_color}" stroke-width="2" filter="url(#neonGlow)" />')
    svg.append(f'  <rect x="0" y="0" width="{width}" height="{total_height}" rx="4" ry="4" fill="url(#hexGrid)" />')
    svg.append('')
    svg.append('  <!-- HUD Controls -->')
    svg.append(f'  <path d="M 15 12 L 25 12 L 30 18 L 40 18" stroke="{accent_color}" stroke-width="2" fill="none" filter="url(#neonGlow)" />')
    svg.append(f'  <path d="M {width - 40} 18 L {width - 30} 18 L {width - 25} 12 L {width - 15} 12" stroke="{key_color}" stroke-width="2" fill="none" filter="url(#neonGlow)" />')
    svg.append(f'  <text x="{width / 2}" y="22" text-anchor="middle" class="term-header" style="animation: glitch 4s infinite;">// SECURE_UPLINK : ESTABLISHED</text>')
    svg.append(f'  <line x1="0" y1="{header_height}" x2="{width}" y2="{header_height}" stroke="{border_color}" stroke-width="1" stroke-dasharray="4 2" />')
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
        svg.append(f'      <text x="0" y="0" class="term-code prompt-symbol">&gt;</text>')
        svg.append(f'      <text x="16" y="0" class="term-code key-text">{key_str}:</text>')
        svg.append(f'      <text x="96" y="0" class="term-code {val_class}">{val_str}</text>')
        svg.append(f'    </g>')

    # Terminal Prompt & Blinking Cursor Row at bottom
    cursor_y = start_y + (len(ROWS) * row_height)
    cursor_delay = 0.0 if is_preview else round(len(ROWS) * delay_step, 2)
    cursor_anim_attr = "" if is_preview else f'opacity="0" style="animation: rowFadeIn 0.35s ease-out {cursor_delay}s forwards;"'

    svg.append(f'    <g transform="translate(0, {cursor_y})" {cursor_anim_attr}>')
    svg.append(f'      <text x="0" y="0" class="term-code prompt-symbol">&gt;</text>')
    svg.append(f'      <text x="16" y="0" class="term-code val-text">status: active</text>')
    svg.append(f'      <rect x="116" y="-10" width="7" height="13" fill="{accent_color}" style="animation: cursorBlink 1s infinite;" filter="url(#neonGlow)" />')
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
