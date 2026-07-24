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
    bg_color = "#0D1117"
    border_color = "#30363D"
    text_color = "#38BDF8"  # Vibrant cyan accent
    header_text_color = "#8B949E"
    
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_width} {total_height}" width="{total_width}" height="{total_height}">',
        '  <defs>',
        '    <style>',
        '      @keyframes fadeInRow {',
        '        0% { opacity: 0; transform: translateY(-3px); }',
        '        100% { opacity: 1; transform: translateY(0); }',
        '      }',
        '      .ascii-text { font-family: "JetBrains Mono", "Fira Code", "Courier New", monospace; font-size: 11px; font-weight: 600; fill: ' + text_color + '; white-space: pre; }',
        '      .header-title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 12px; font-weight: 500; fill: ' + header_text_color + '; }',
        '    </style>',
        '  </defs>',
        '',
        '  <!-- Outer Terminal Window Frame -->',
        f'  <rect x="0" y="0" width="{total_width}" height="{total_height}" rx="10" ry="10" fill="{bg_color}" stroke="{border_color}" stroke-width="1.5" />',
        '',
        '  <!-- Window Controls -->',
        f'  <circle cx="20" cy="18" r="5" fill="#FF5F56" />',
        f'  <circle cx="36" cy="18" r="5" fill="#FFBD2E" />',
        f'  <circle cx="52" cy="18" r="5" fill="#27C93F" />',
        f'  <text x="{total_width / 2}" y="22" text-anchor="middle" class="header-title">portrait.ascii</text>',
        f'  <line x1="0" y1="{header_height}" x2="{total_width}" y2="{header_height}" stroke="{border_color}" stroke-width="1" />',
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
