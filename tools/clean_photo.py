#!/usr/bin/env python3
"""
tools/clean_photo.py

Cleans a source portrait photo for ASCII conversion:
1. Cuts background out using `rembg` (or fallback).
2. Evens out lighting using OpenCV CLAHE (Adaptive Histogram Equalization).
3. Composites subject onto a pure white canvas so background stays light in ASCII ramp.
"""

import sys
import os
import argparse
import numpy as np

def generate_fallback_portrait(output_path):
    """Generates a high-contrast procedural developer portrait silhouette when no photo is provided."""
    from PIL import Image, ImageDraw, ImageFilter

    width, height = 400, 400
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    # Dark silhouette of head and shoulders (developer posture)
    # Head
    draw.ellipse([150, 80, 250, 190], fill=(20, 20, 20))
    # Neck
    draw.rectangle([185, 175, 215, 215], fill=(25, 25, 25))
    # Shoulders / Body
    draw.ellipse([80, 200, 320, 420], fill=(15, 15, 15))
    # Headphones / Glasses outline accents
    draw.arc([140, 95, 260, 185], start=200, end=340, fill=(200, 200, 200), width=6)
    draw.rectangle([138, 125, 155, 160], fill=(180, 180, 180))
    draw.rectangle([245, 125, 262, 160], fill=(180, 180, 180))
    # Glasses
    draw.rectangle([170, 125, 198, 142], outline=(220, 220, 220), width=3)
    draw.rectangle([202, 125, 230, 142], outline=(220, 220, 220), width=3)
    draw.line([198, 133, 202, 133], fill=(220, 220, 220), width=2)
    # Laptop screen glow angle
    draw.polygon([(100, 400), (300, 400), (280, 310), (120, 310)], fill=(240, 240, 245))
    draw.polygon([(110, 395), (290, 395), (275, 320), (125, 320)], fill=(30, 40, 50))

    img.save(output_path, "PNG")
    print(f"Generated default procedural portrait -> {output_path}")

def clean_photo(input_path, output_path):
    from PIL import Image

    if not os.path.exists(input_path):
        print(f"Source file '{input_path}' not found. Generating default developer portrait...")
        generate_fallback_portrait(output_path)
        return

    try:
        import cv2
        # Try using rembg
        try:
            from rembg import remove
            with open(input_path, "rb") as f:
                input_bytes = f.read()
            output_bytes = remove(input_bytes)
            from io import BytesIO
            img_rgba = Image.open(BytesIO(output_bytes)).convert("RGBA")
        except Exception as e:
            print(f"Note: rembg background removal skipped/fallback ({e}). Loading image directly.")
            img_rgba = Image.open(input_path).convert("RGBA")

        # Convert to numpy array for OpenCV CLAHE processing
        img_np = np.array(img_rgba)
        
        # Extract RGB and Alpha channels
        if img_np.shape[2] == 4:
            rgb = img_np[:, :, :3]
            alpha = img_np[:, :, 3]
        else:
            rgb = img_np
            alpha = np.ones((rgb.shape[0], rgb.shape[1]), dtype=np.uint8) * 255

        # Convert RGB to LAB color space and apply CLAHE to L channel
        lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl_l = clahe.apply(l_channel)

        merged_lab = cv2.merge((cl_l, a_channel, b_channel))
        enhanced_rgb = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2RGB)

        # Composite onto a clean white background
        height, width, _ = enhanced_rgb.shape
        white_bg = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        alpha_factor = (alpha / 255.0)[:, :, np.newaxis]
        final_img_np = (enhanced_rgb * alpha_factor + white_bg * (1.0 - alpha_factor)).astype(np.uint8)

        final_img = Image.fromarray(final_img_np)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        final_img.save(output_path, "PNG")
        print(f"Cleaned photo successfully saved -> {output_path}")

    except Exception as err:
        print(f"Error during photo cleanup ({err}). Generating fallback portrait...")
        generate_fallback_portrait(output_path)

def main():
    parser = argparse.ArgumentParser(description="Clean photo for ASCII conversion.")
    parser.add_argument("input", nargs="?", default="assets/photo.jpg", help="Path to input photo")
    parser.add_argument("--output", default="assets/photo-ready.png", help="Path to output PNG")
    args = parser.parse_args()

    clean_photo(args.input, args.output)

if __name__ == "__main__":
    main()
