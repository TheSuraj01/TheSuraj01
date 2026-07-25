#!/usr/bin/env python3
"""
tools/render_portrait.py

Converts `assets/photo-ready.png` into an animated SVG ASCII portrait (`portrait.svg`).
Row-by-row staggered SMIL animation draws the portrait in top-to-bottom.
"""

import os
import sys
from PIL import Image

GLYPHS = " '.,:;~+*xXO#"  # Left = light/empty, Right = dense/dark

def image_to_ascii(img_path, width=48, aspect_ratio_correction=0.55):
    """Reads image, downscales to target character width, and converts to 2D matrix of ASCII characters."""
    if not os.path.exists(img_path):
        # Trigger clean_photo script to generate photo-ready.png
        from clean_photo import clean_photo
        clean_photo("assets/photo.jpg", img_path)

    img = Image.open(img_path).convert("L")
    w_orig, h_orig = img.size
    
    height = int((h_orig / w_orig) * width * aspect_ratio_correction)
    img_resized = img.resize((width, height), Image.Resampling.LANCZOS)
    
    ascii_rows = []
    num_glyphs = len(GLYPHS)
    
    for y in range(height):
        row_chars = []
        for x in range(width):
            pixel_val = img_resized.getpixel((x, y))
            # Invert brightness: white background (255) -> lowest index 0 (' ')
            # Dark pixels (0) -> highest index ('#')
            inverted = 255 - pixel_val
            idx = int((inverted / 255.0) * (num_glyphs - 1))
            row_chars.append(GLYPHS[idx])
        ascii_rows.append("".join(row_chars))
        
    return ascii_rows

def escape_xml(text):
    """Escapes special XML characters in ASCII strings."""
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&apos;"))

def build_portrait_svg(ascii_rows, output_path="portrait.svg"):
    """Renders ASCII rows into an animated SVG file with terminal container frame."""
    num_rows = len(ascii_rows)
    num_cols = max(len(r) for r in ascii_rows) if ascii_rows else 50
    
    # Terminal Dimensions
    char_width = 7.2
    line_height = 13.5
    padding_x = 24
    padding_y = 20
    header_height = 36
    
    content_width = int(num_cols * char_width)
    content_height = int(num_rows * line_height)
    
    total_width = max(content_width + (padding_x * 2), 360)
    total_height = content_height + header_height + (padding_y * 2)

    # Accent colors
    bg_color = "#050510"
    border_color = "#9d4edd"
    text_color = "#00f3ff"  # Neon cyan
    header_text_color = "#f000ff"
    grid_color = "#1a103c"
    
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
        '    <pattern id="scanlines" width="4" height="4" patternUnits="userSpaceOnUse">',
        '      <rect width="4" height="2" fill="#000" fill-opacity="0.2" />',
        '    </pattern>',
        '    <style>',
        '      @keyframes fadeInRow {',
        '        0% { opacity: 0; transform: translateY(-3px) scale(0.98); }',
        '        100% { opacity: 1; transform: translateY(0) scale(1); }',
        '      }',
        '      @keyframes glitch {',
        '        0% { transform: translate(0) }',
        '        20% { transform: translate(-2px, 1px) }',
        '        40% { transform: translate(-1px, -1px) }',
        '        60% { transform: translate(2px, 1px) }',
        '        80% { transform: translate(1px, -1px) }',
        '        100% { transform: translate(0) }',
        '      }',
        '      .ascii-text { font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 11px; font-weight: 700; fill: ' + text_color + '; white-space: pre; filter: url(#neonGlow); }',
        '      .header-title { font-family: "JetBrains Mono", "Fira Code", monospace; font-size: 12px; font-weight: 700; fill: ' + header_text_color + '; letter-spacing: 1px; filter: url(#neonGlow); }',
        '    </style>',
        '  </defs>',
        '',
        '  <!-- Cyberpunk Window Frame -->',
        f'  <rect x="0" y="0" width="{total_width}" height="{total_height}" rx="4" ry="4" fill="{bg_color}" stroke="{border_color}" stroke-width="2" filter="url(#neonGlow)" />',
        f'  <rect x="0" y="0" width="{total_width}" height="{total_height}" rx="4" ry="4" fill="url(#scanlines)" />',
        '',
        '  <!-- HUD Controls -->',
        f'  <path d="M 15 12 L 25 12 L 30 18 L 40 18" stroke="{text_color}" stroke-width="2" fill="none" filter="url(#neonGlow)" />',
        f'  <path d="M {total_width - 40} 18 L {total_width - 30} 18 L {total_width - 25} 12 L {total_width - 15} 12" stroke="{header_text_color}" stroke-width="2" fill="none" filter="url(#neonGlow)" />',
        f'  <text x="{total_width / 2}" y="22" text-anchor="middle" class="header-title" style="animation: glitch 4s infinite;">TARGET_IDENT :: VERIFIED</text>',
        f'  <line x1="0" y1="{header_height}" x2="{total_width}" y2="{header_height}" stroke="{border_color}" stroke-width="1" stroke-dasharray="4 2" />',
        '',
        '  <!-- Animated ASCII Content -->',
        f'  <g transform="translate({padding_x}, {header_height + padding_y})">'
    ]

    # Staggered animation delay per row (40ms step)
    delay_step = 0.04
    
    for idx, row in enumerate(ascii_rows):
        y_pos = int(idx * line_height + 10)
        delay = round(idx * delay_step, 3)
        escaped_row = escape_xml(row)
        
        svg_lines.append(
            f'    <text x="0" y="{y_pos}" class="ascii-text" opacity="0" '
            f'style="animation: fadeInRow 0.3s ease-out {delay}s forwards;">{escaped_row}</text>'
        )

    svg_lines.append('  </g>')
    svg_lines.append('</svg>')
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_lines))
        
    print(f"ASCII portrait SVG rendered -> {output_path}")

def main():
    img_ready_path = "assets/photo-ready.png"
    output_svg_path = "portrait.svg"
    
    ascii_rows = image_to_ascii(img_ready_path, width=46)
    build_portrait_svg(ascii_rows, output_svg_path)

if __name__ == "__main__":
    main()
