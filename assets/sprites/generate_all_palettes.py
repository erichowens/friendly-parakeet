#!/usr/bin/env python3
"""
Generate all sprite variations with all color palettes
This creates a comprehensive preview of all combinations
"""

import json
import os
from pathlib import Path
from PIL import Image
import numpy as np

# Import the sprite generation functions
import sys
sys.path.insert(0, str(Path(__file__).parent))
from generate_parakeet_sprites import (
    create_sprite_option_1_classic,
    create_sprite_option_2_cute,
    create_sprite_option_3_dynamic,
    render_sprite,
    C_TRANS
)


def load_palette(palette_file):
    """Load a palette JSON file"""
    with open(palette_file, 'r') as f:
        return json.load(f)


def apply_palette_swap(sprite_data, source_palette, target_palette):
    """
    Apply palette swap to sprite data

    Args:
        sprite_data: 2D array of color key strings
        source_palette: dict with 'colors' containing original colors
        target_palette: dict with 'colors' containing new colors

    Returns:
        Image with swapped palette
    """
    size = len(sprite_data)
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    pixels = img.load()

    # Use target palette colors
    target_colors = target_palette['colors']

    for y in range(size):
        for x in range(size):
            color_key = sprite_data[y][x]
            if color_key != C_TRANS and color_key in target_colors:
                color = target_colors[color_key]
                if len(color) == 3:
                    color = tuple(color) + (255,)
                else:
                    color = tuple(color)
                pixels[x, y] = color

    return img


def create_palette_preview_sheet(sprite_data, palettes, sprite_name, scale=4):
    """
    Create a preview sheet showing sprite with all palettes

    Args:
        sprite_data: The base sprite data
        palettes: List of (name, palette_dict) tuples
        sprite_name: Name for output file
        scale: Pixel scale factor
    """
    sprite_size = len(sprite_data) * scale
    padding = 10
    label_height = 20

    # Calculate sheet dimensions
    cols = 3
    rows = (len(palettes) + cols - 1) // cols

    sheet_width = cols * (sprite_size + padding) + padding
    sheet_height = rows * (sprite_size + label_height + padding) + padding

    # Create sheet
    sheet = Image.new('RGB', (sheet_width, sheet_height), (240, 240, 245))

    # Load source palette (classic)
    source_palette = palettes[0][1]  # Assume first is the source

    for idx, (palette_name, palette_dict) in enumerate(palettes):
        col = idx % cols
        row = idx // cols

        x = padding + col * (sprite_size + padding)
        y = padding + row * (sprite_size + label_height + padding) + label_height

        # Generate sprite with this palette
        sprite_img = apply_palette_swap(sprite_data, source_palette, palette_dict)
        sprite_img = sprite_img.resize((sprite_size, sprite_size), Image.NEAREST)

        # Paste onto sheet
        sheet.paste(sprite_img, (x, y), sprite_img)

    return sheet


def main():
    print("=" * 70)
    print("Generating All Palette Variations")
    print("=" * 70)

    # Load all palettes
    palettes_dir = Path(__file__).parent / 'palettes'
    palettes = []

    print("\nLoading palettes...")
    for palette_file in sorted(palettes_dir.glob('palette_*.json')):
        palette = load_palette(palette_file)
        palette_name = palette_file.stem.replace('palette_', '')
        palettes.append((palette_name, palette))
        print(f"  ✓ {palette['name']}")

    print(f"\nTotal palettes: {len(palettes)}")

    # Create sprite data
    sprites = {
        'option1_classic': create_sprite_option_1_classic(),
        'option2_cute': create_sprite_option_2_cute(),
        'option3_dynamic': create_sprite_option_3_dynamic(),
    }

    output_dir = Path(__file__).parent / 'palette_previews'
    output_dir.mkdir(exist_ok=True)

    print("\n" + "=" * 70)
    print("Generating individual sprite+palette combinations...")
    print("=" * 70)

    # Generate all combinations
    for sprite_name, sprite_data in sprites.items():
        print(f"\n{sprite_name}:")

        for palette_name, palette_dict in palettes:
            # Generate sprite with palette
            img = apply_palette_swap(sprite_data, palettes[0][1], palette_dict)
            img = img.resize((32 * 8, 32 * 8), Image.NEAREST)

            output_file = output_dir / f"{sprite_name}_{palette_name}.png"
            img.save(output_file)
            print(f"  ✓ {palette_name:15} → {output_file.name}")

    print("\n" + "=" * 70)
    print("Generating preview sheets...")
    print("=" * 70)

    # Generate preview sheets for each sprite
    for sprite_name, sprite_data in sprites.items():
        print(f"\nCreating preview sheet for {sprite_name}...")
        sheet = create_palette_preview_sheet(sprite_data, palettes, sprite_name, scale=6)

        output_file = output_dir / f"preview_sheet_{sprite_name}.png"
        sheet.save(output_file)
        print(f"  ✓ Saved: {output_file.name}")

    print("\n" + "=" * 70)
    print("✓ All variations generated successfully!")
    print("=" * 70)
    print(f"\nOutput location: {output_dir}")
    print(f"Total files: {len(list(output_dir.glob('*.png')))}")
    print("\nYou can now:")
    print("1. Review all palette variations in palette_previews/")
    print("2. Choose your favorite sprite option (1, 2, or 3)")
    print("3. Select your preferred color palettes")
    print("4. Customize the palette JSON files with your parakeets' exact colors")
    print("5. Start creating animation frames!")


if __name__ == '__main__':
    main()
