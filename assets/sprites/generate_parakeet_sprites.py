#!/usr/bin/env python3
"""
SNES-Style Parakeet Sprite Generator
Creates pixel art parakeet mascot sprites with color palette swapping support
"""

from PIL import Image, ImageDraw
import json

# SNES Color Palette System
# Using indexed colors that can be easily swapped
# Colors are defined as (R, G, B) tuples

# Base Palette - Classic Green/Yellow Parakeet
PALETTE_CLASSIC = {
    'transparent': (0, 0, 0, 0),           # 0 - Transparent
    'outline_dark': (33, 33, 33),          # 1 - Black outline
    'outline_light': (66, 66, 66),         # 2 - Dark gray (soft shadows)
    'body_dark': (102, 176, 50),           # 3 - Dark green
    'body_main': (153, 217, 70),           # 4 - Main green body
    'body_light': (198, 239, 130),         # 5 - Light green highlight
    'chest_dark': (230, 190, 50),          # 6 - Dark yellow
    'chest_main': (255, 230, 100),         # 7 - Main yellow chest
    'chest_light': (255, 250, 180),        # 8 - Light yellow highlight
    'beak_dark': (200, 120, 40),           # 9 - Dark orange beak
    'beak_main': (255, 160, 70),           # 10 - Main orange beak
    'eye_white': (255, 255, 255),          # 11 - Eye white
    'eye_pupil': (50, 50, 80),             # 12 - Eye pupil (dark blue)
    'feet_dark': (180, 100, 60),           # 13 - Dark feet
    'feet_main': (220, 140, 90),           # 14 - Main feet color
    'accent': (100, 180, 220),             # 15 - Wing/tail accent (light blue)
}

# Color indices for easy palette swapping
C_TRANS = 'transparent'
C_OUT_D = 'outline_dark'
C_OUT_L = 'outline_light'
C_BODY_D = 'body_dark'
C_BODY_M = 'body_main'
C_BODY_L = 'body_light'
C_CHEST_D = 'chest_dark'
C_CHEST_M = 'chest_main'
C_CHEST_L = 'chest_light'
C_BEAK_D = 'beak_dark'
C_BEAK_M = 'beak_main'
C_EYE_W = 'eye_white'
C_EYE_P = 'eye_pupil'
C_FEET_D = 'feet_dark'
C_FEET_M = 'feet_main'
C_ACCENT = 'accent'


def create_sprite_option_1_classic():
    """
    Option 1: Classic Side-View Parakeet
    32x32 pixels, facing right, perched pose
    Perfect for SNES-style sprites with clean outlines
    """
    size = 32
    sprite_data = [
        [C_TRANS] * size for _ in range(size)
    ]

    # Define the sprite pixel by pixel (y, x, color)
    # Head (rows 6-14, centered around x=16-22)
    pixels = [
        # Head outline and structure
        (7, 18, C_OUT_D), (7, 19, C_OUT_D), (7, 20, C_OUT_D), (7, 21, C_OUT_D),
        (8, 17, C_OUT_D), (8, 18, C_BODY_D), (8, 19, C_BODY_M), (8, 20, C_BODY_M), (8, 21, C_BODY_D), (8, 22, C_OUT_D),
        (9, 16, C_OUT_D), (9, 17, C_BODY_D), (9, 18, C_BODY_M), (9, 19, C_BODY_L), (9, 20, C_BODY_M), (9, 21, C_BODY_D), (9, 22, C_OUT_D),
        (10, 16, C_OUT_D), (10, 17, C_BODY_M), (10, 18, C_BODY_L), (10, 19, C_BODY_L), (10, 20, C_BODY_M), (10, 21, C_OUT_D),

        # Eye
        (9, 20, C_EYE_W), (9, 21, C_OUT_D),
        (10, 20, C_EYE_P), (10, 21, C_OUT_D),

        # Beak
        (10, 22, C_OUT_D), (10, 23, C_BEAK_M), (10, 24, C_OUT_D),
        (11, 21, C_OUT_D), (11, 22, C_BEAK_D), (11, 23, C_BEAK_M), (11, 24, C_OUT_D),
        (12, 21, C_OUT_D), (12, 22, C_OUT_D), (12, 23, C_OUT_D),

        # Neck to body transition
        (11, 16, C_OUT_D), (11, 17, C_BODY_M), (11, 18, C_BODY_L), (11, 19, C_BODY_M), (11, 20, C_BODY_D),
        (12, 15, C_OUT_D), (12, 16, C_BODY_D), (12, 17, C_BODY_M), (12, 18, C_BODY_M), (12, 19, C_BODY_D), (12, 20, C_OUT_D),

        # Upper body/chest
        (13, 14, C_OUT_D), (13, 15, C_BODY_D), (13, 16, C_CHEST_D), (13, 17, C_CHEST_M), (13, 18, C_CHEST_L), (13, 19, C_CHEST_M), (13, 20, C_OUT_D),
        (14, 13, C_OUT_D), (14, 14, C_BODY_D), (14, 15, C_CHEST_D), (14, 16, C_CHEST_M), (14, 17, C_CHEST_L), (14, 18, C_CHEST_M), (14, 19, C_CHEST_D), (14, 20, C_OUT_D),
        (15, 12, C_OUT_D), (15, 13, C_BODY_D), (15, 14, C_CHEST_D), (15, 15, C_CHEST_M), (15, 16, C_CHEST_L), (15, 17, C_CHEST_M), (15, 18, C_CHEST_D), (15, 19, C_BODY_D), (15, 20, C_OUT_D),
        (16, 12, C_OUT_D), (16, 13, C_BODY_D), (16, 14, C_CHEST_D), (16, 15, C_CHEST_M), (16, 16, C_CHEST_M), (16, 17, C_CHEST_D), (16, 18, C_BODY_D), (16, 19, C_BODY_D), (16, 20, C_OUT_D),

        # Mid body
        (17, 12, C_OUT_D), (17, 13, C_BODY_D), (17, 14, C_BODY_M), (17, 15, C_BODY_M), (17, 16, C_BODY_M), (17, 17, C_BODY_D), (17, 18, C_BODY_D), (17, 19, C_OUT_D),
        (18, 13, C_OUT_D), (18, 14, C_BODY_D), (18, 15, C_BODY_M), (18, 16, C_BODY_M), (18, 17, C_BODY_D), (18, 18, C_OUT_D),

        # Wing detail
        (14, 11, C_OUT_D), (14, 12, C_ACCENT), (14, 13, C_OUT_D),
        (15, 10, C_OUT_D), (15, 11, C_ACCENT), (15, 12, C_OUT_D),
        (16, 9, C_OUT_D), (16, 10, C_ACCENT), (16, 11, C_ACCENT), (16, 12, C_OUT_D),
        (17, 9, C_OUT_D), (17, 10, C_ACCENT), (17, 11, C_ACCENT), (17, 12, C_OUT_D),
        (18, 10, C_OUT_D), (18, 11, C_ACCENT), (18, 12, C_ACCENT), (18, 13, C_OUT_D),
        (19, 11, C_OUT_D), (19, 12, C_ACCENT), (19, 13, C_OUT_D),

        # Tail feathers (long, pointing down-right)
        (19, 14, C_OUT_D), (19, 15, C_BODY_D), (19, 16, C_OUT_D),
        (20, 14, C_OUT_D), (20, 15, C_BODY_M), (20, 16, C_ACCENT), (20, 17, C_OUT_D),
        (21, 15, C_OUT_D), (21, 16, C_BODY_M), (21, 17, C_ACCENT), (21, 18, C_OUT_D),
        (22, 16, C_OUT_D), (22, 17, C_ACCENT), (22, 18, C_ACCENT), (22, 19, C_OUT_D),
        (23, 17, C_OUT_D), (23, 18, C_ACCENT), (23, 19, C_OUT_D),
        (24, 18, C_OUT_D), (24, 19, C_OUT_D),

        # Legs and feet
        (19, 17, C_OUT_D), (19, 18, C_FEET_D),
        (20, 18, C_OUT_D), (20, 19, C_FEET_M), (20, 20, C_OUT_D),
        (21, 19, C_OUT_D), (21, 20, C_FEET_M), (21, 21, C_OUT_D),
        (22, 20, C_OUT_D), (22, 21, C_FEET_M), (22, 22, C_OUT_D),
        # Toes spreading out
        (23, 20, C_OUT_D), (23, 21, C_OUT_D), (23, 22, C_OUT_D), (23, 23, C_OUT_D),
        (23, 19, C_OUT_D), (23, 24, C_OUT_D),
    ]

    # Apply pixels to sprite data
    for y, x, color in pixels:
        if 0 <= y < size and 0 <= x < size:
            sprite_data[y][x] = color

    return sprite_data


def create_sprite_option_2_cute():
    """
    Option 2: Rounder/Cuter Front-Facing Parakeet
    32x32 pixels, chibi-style with big head and eyes
    """
    size = 32
    sprite_data = [
        [C_TRANS] * size for _ in range(size)
    ]

    pixels = [
        # Head (bigger, rounder)
        (6, 14, C_OUT_D), (6, 15, C_OUT_D), (6, 16, C_OUT_D), (6, 17, C_OUT_D),
        (7, 13, C_OUT_D), (7, 14, C_BODY_D), (7, 15, C_BODY_M), (7, 16, C_BODY_M), (7, 17, C_BODY_D), (7, 18, C_OUT_D),
        (8, 12, C_OUT_D), (8, 13, C_BODY_D), (8, 14, C_BODY_M), (8, 15, C_BODY_L), (8, 16, C_BODY_L), (8, 17, C_BODY_M), (8, 18, C_BODY_D), (8, 19, C_OUT_D),
        (9, 11, C_OUT_D), (9, 12, C_BODY_D), (9, 13, C_BODY_M), (9, 14, C_BODY_L), (9, 15, C_BODY_L), (9, 16, C_BODY_L), (9, 17, C_BODY_L), (9, 18, C_BODY_M), (9, 19, C_BODY_D), (9, 20, C_OUT_D),

        # Big cute eyes
        (10, 11, C_OUT_D), (10, 12, C_BODY_M), (10, 13, C_OUT_D), (10, 14, C_EYE_W), (10, 15, C_EYE_W), (10, 16, C_EYE_W), (10, 17, C_EYE_W), (10, 18, C_OUT_D), (10, 19, C_BODY_M), (10, 20, C_OUT_D),
        (11, 11, C_OUT_D), (11, 12, C_BODY_M), (11, 13, C_EYE_W), (11, 14, C_EYE_W), (11, 15, C_EYE_P), (11, 16, C_EYE_P), (11, 17, C_EYE_W), (11, 18, C_EYE_W), (11, 19, C_BODY_M), (11, 20, C_OUT_D),
        (12, 11, C_OUT_D), (12, 12, C_BODY_M), (12, 13, C_OUT_D), (12, 14, C_EYE_W), (12, 15, C_EYE_P), (12, 16, C_EYE_P), (12, 17, C_EYE_W), (12, 18, C_OUT_D), (12, 19, C_BODY_M), (12, 20, C_OUT_D),

        # Small beak (centered, cute)
        (13, 12, C_OUT_D), (13, 13, C_BODY_M), (13, 14, C_BODY_M), (13, 15, C_OUT_D), (13, 16, C_OUT_D), (13, 17, C_BODY_M), (13, 18, C_BODY_M), (13, 19, C_OUT_D),
        (14, 13, C_OUT_D), (14, 14, C_OUT_D), (14, 15, C_BEAK_M), (14, 16, C_BEAK_M), (14, 17, C_OUT_D), (14, 18, C_OUT_D),
        (15, 14, C_OUT_D), (15, 15, C_BEAK_D), (15, 16, C_BEAK_D), (15, 17, C_OUT_D),
        (16, 15, C_OUT_D), (16, 16, C_OUT_D),

        # Body (small, round, chibi proportions)
        (17, 12, C_OUT_D), (17, 13, C_BODY_D), (17, 14, C_CHEST_D), (17, 15, C_CHEST_M), (17, 16, C_CHEST_M), (17, 17, C_CHEST_D), (17, 18, C_BODY_D), (17, 19, C_OUT_D),
        (18, 11, C_OUT_D), (18, 12, C_BODY_D), (18, 13, C_CHEST_D), (18, 14, C_CHEST_M), (18, 15, C_CHEST_L), (18, 16, C_CHEST_L), (18, 17, C_CHEST_M), (18, 18, C_CHEST_D), (18, 19, C_BODY_D), (18, 20, C_OUT_D),
        (19, 11, C_OUT_D), (19, 12, C_BODY_D), (19, 13, C_CHEST_D), (19, 14, C_CHEST_M), (19, 15, C_CHEST_L), (19, 16, C_CHEST_L), (19, 17, C_CHEST_M), (19, 18, C_CHEST_D), (19, 19, C_BODY_D), (19, 20, C_OUT_D),
        (20, 12, C_OUT_D), (20, 13, C_BODY_D), (20, 14, C_CHEST_D), (20, 15, C_CHEST_M), (20, 16, C_CHEST_M), (20, 17, C_CHEST_D), (20, 18, C_BODY_D), (20, 19, C_OUT_D),
        (21, 13, C_OUT_D), (21, 14, C_BODY_D), (21, 15, C_BODY_M), (21, 16, C_BODY_M), (21, 17, C_BODY_D), (21, 18, C_OUT_D),

        # Wings (small, stubby, cute)
        (18, 10, C_OUT_D), (18, 11, C_ACCENT), (19, 9, C_OUT_D), (19, 10, C_ACCENT), (19, 11, C_OUT_D),
        (20, 10, C_OUT_D), (20, 11, C_ACCENT), (20, 12, C_OUT_D),
        (18, 20, C_ACCENT), (18, 21, C_OUT_D), (19, 20, C_OUT_D), (19, 21, C_ACCENT), (19, 22, C_OUT_D),
        (20, 20, C_OUT_D), (20, 21, C_ACCENT), (20, 22, C_OUT_D),

        # Tail (short, fan-shaped)
        (22, 14, C_OUT_D), (22, 15, C_ACCENT), (22, 16, C_ACCENT), (22, 17, C_OUT_D),
        (23, 13, C_OUT_D), (23, 14, C_ACCENT), (23, 15, C_BODY_M), (23, 16, C_BODY_M), (23, 17, C_ACCENT), (23, 18, C_OUT_D),
        (24, 14, C_OUT_D), (24, 15, C_ACCENT), (24, 16, C_ACCENT), (24, 17, C_OUT_D),

        # Feet (tiny, cute)
        (22, 14, C_OUT_D), (22, 15, C_FEET_D), (22, 17, C_FEET_D), (22, 18, C_OUT_D),
        (23, 14, C_FEET_M), (23, 15, C_OUT_D), (23, 17, C_OUT_D), (23, 18, C_FEET_M),
        (24, 13, C_OUT_D), (24, 14, C_OUT_D), (24, 18, C_OUT_D), (24, 19, C_OUT_D),
    ]

    for y, x, color in pixels:
        if 0 <= y < size and 0 <= x < size:
            sprite_data[y][x] = color

    return sprite_data


def create_sprite_option_3_dynamic():
    """
    Option 3: Dynamic 3/4 View - Action Pose
    32x32 pixels, more dynamic angle, wing partially spread
    """
    size = 32
    sprite_data = [
        [C_TRANS] * size for _ in range(size)
    ]

    pixels = [
        # Head (3/4 view angle)
        (7, 16, C_OUT_D), (7, 17, C_OUT_D), (7, 18, C_OUT_D), (7, 19, C_OUT_D),
        (8, 15, C_OUT_D), (8, 16, C_BODY_D), (8, 17, C_BODY_M), (8, 18, C_BODY_M), (8, 19, C_BODY_L), (8, 20, C_OUT_D),
        (9, 15, C_OUT_D), (9, 16, C_BODY_M), (9, 17, C_BODY_L), (9, 18, C_BODY_L), (9, 19, C_BODY_M), (9, 20, C_BODY_D), (9, 21, C_OUT_D),
        (10, 14, C_OUT_D), (10, 15, C_BODY_M), (10, 16, C_BODY_L), (10, 17, C_BODY_L), (10, 18, C_BODY_M), (10, 19, C_BODY_D), (10, 20, C_OUT_D),

        # Eye (visible from 3/4 angle)
        (9, 19, C_OUT_D), (9, 20, C_EYE_W),
        (10, 19, C_OUT_D), (10, 20, C_EYE_P),

        # Beak (angled)
        (10, 21, C_OUT_D), (10, 22, C_BEAK_M), (10, 23, C_OUT_D),
        (11, 20, C_OUT_D), (11, 21, C_BEAK_D), (11, 22, C_BEAK_M), (11, 23, C_OUT_D),
        (12, 20, C_OUT_D), (12, 21, C_OUT_D), (12, 22, C_OUT_D),

        # Neck and upper body
        (11, 15, C_OUT_D), (11, 16, C_BODY_M), (11, 17, C_BODY_L), (11, 18, C_BODY_M), (11, 19, C_BODY_D),
        (12, 14, C_OUT_D), (12, 15, C_BODY_D), (12, 16, C_CHEST_D), (12, 17, C_CHEST_M), (12, 18, C_CHEST_M), (12, 19, C_OUT_D),
        (13, 13, C_OUT_D), (13, 14, C_BODY_D), (13, 15, C_CHEST_D), (13, 16, C_CHEST_M), (13, 17, C_CHEST_L), (13, 18, C_CHEST_M), (13, 19, C_OUT_D),

        # Body with wing extended
        (14, 12, C_OUT_D), (14, 13, C_BODY_D), (14, 14, C_CHEST_D), (14, 15, C_CHEST_M), (14, 16, C_CHEST_L), (14, 17, C_CHEST_M), (14, 18, C_BODY_D), (14, 19, C_OUT_D),
        (15, 12, C_OUT_D), (15, 13, C_BODY_D), (15, 14, C_CHEST_M), (15, 15, C_CHEST_M), (15, 16, C_CHEST_D), (15, 17, C_BODY_D), (15, 18, C_OUT_D),
        (16, 12, C_OUT_D), (16, 13, C_BODY_D), (16, 14, C_BODY_M), (16, 15, C_BODY_M), (16, 16, C_BODY_D), (16, 17, C_OUT_D),
        (17, 13, C_OUT_D), (17, 14, C_BODY_D), (17, 15, C_BODY_M), (17, 16, C_OUT_D),

        # Extended wing (dynamic!)
        (13, 8, C_OUT_D), (13, 9, C_ACCENT), (13, 10, C_OUT_D),
        (14, 7, C_OUT_D), (14, 8, C_ACCENT), (14, 9, C_ACCENT), (14, 10, C_ACCENT), (14, 11, C_OUT_D),
        (15, 6, C_OUT_D), (15, 7, C_ACCENT), (15, 8, C_BODY_M), (15, 9, C_ACCENT), (15, 10, C_ACCENT), (15, 11, C_ACCENT), (15, 12, C_OUT_D),
        (16, 6, C_OUT_D), (16, 7, C_ACCENT), (16, 8, C_ACCENT), (16, 9, C_BODY_M), (16, 10, C_ACCENT), (16, 11, C_ACCENT), (16, 12, C_OUT_D),
        (17, 7, C_OUT_D), (17, 8, C_ACCENT), (17, 9, C_ACCENT), (17, 10, C_BODY_D), (17, 11, C_ACCENT), (17, 12, C_ACCENT), (17, 13, C_OUT_D),
        (18, 8, C_OUT_D), (18, 9, C_ACCENT), (18, 10, C_ACCENT), (18, 11, C_ACCENT), (18, 12, C_OUT_D),
        (19, 9, C_OUT_D), (19, 10, C_ACCENT), (19, 11, C_OUT_D),

        # Tail feathers (flowing)
        (18, 13, C_OUT_D), (18, 14, C_BODY_D), (18, 15, C_BODY_M), (18, 16, C_OUT_D),
        (19, 13, C_OUT_D), (19, 14, C_BODY_M), (19, 15, C_ACCENT), (19, 16, C_ACCENT), (19, 17, C_OUT_D),
        (20, 14, C_OUT_D), (20, 15, C_ACCENT), (20, 16, C_ACCENT), (20, 17, C_ACCENT), (20, 18, C_OUT_D),
        (21, 15, C_OUT_D), (21, 16, C_ACCENT), (21, 17, C_ACCENT), (21, 18, C_OUT_D),
        (22, 16, C_OUT_D), (22, 17, C_ACCENT), (22, 18, C_OUT_D),
        (23, 17, C_OUT_D), (23, 18, C_OUT_D),

        # Legs
        (18, 15, C_OUT_D), (18, 16, C_FEET_D),
        (19, 16, C_OUT_D), (19, 17, C_FEET_M),
        (20, 17, C_OUT_D), (20, 18, C_FEET_M), (20, 19, C_OUT_D),
        (21, 18, C_OUT_D), (21, 19, C_FEET_M), (21, 20, C_OUT_D),
        (22, 19, C_OUT_D), (22, 20, C_OUT_D), (22, 21, C_OUT_D),
    ]

    for y, x, color in pixels:
        if 0 <= y < size and 0 <= x < size:
            sprite_data[y][x] = color

    return sprite_data


def render_sprite(sprite_data, palette, scale=4):
    """
    Render sprite data to PIL Image using the specified palette
    """
    size = len(sprite_data)
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    pixels = img.load()

    for y in range(size):
        for x in range(size):
            color_key = sprite_data[y][x]
            if color_key != C_TRANS:
                color = palette[color_key]
                if len(color) == 3:
                    color = color + (255,)  # Add alpha
                pixels[x, y] = color

    # Scale up for better visibility
    if scale > 1:
        img = img.resize((size * scale, size * scale), Image.NEAREST)

    return img


def save_sprite_with_palette(sprite_data, palette, filename, scale=4):
    """Save sprite as PNG with specified palette"""
    img = render_sprite(sprite_data, palette, scale)
    img.save(filename)
    print(f"Saved: {filename}")


def save_palette_definition(palette, filename):
    """Save palette as JSON for easy swapping"""
    # Convert tuples to lists for JSON
    palette_json = {k: list(v) for k, v in palette.items()}
    with open(filename, 'w') as f:
        json.dump(palette_json, f, indent=2)
    print(f"Saved palette: {filename}")


if __name__ == '__main__':
    print("Generating SNES-Style Parakeet Sprites...")
    print("=" * 60)

    # Create all three sprite options
    sprite1 = create_sprite_option_1_classic()
    sprite2 = create_sprite_option_2_cute()
    sprite3 = create_sprite_option_3_dynamic()

    # Save with classic palette
    save_sprite_with_palette(sprite1, PALETTE_CLASSIC,
                            'parakeet_option1_classic_side_view.png', scale=8)
    save_sprite_with_palette(sprite2, PALETTE_CLASSIC,
                            'parakeet_option2_cute_front_view.png', scale=8)
    save_sprite_with_palette(sprite3, PALETTE_CLASSIC,
                            'parakeet_option3_dynamic_action.png', scale=8)

    # Save base palette
    save_palette_definition(PALETTE_CLASSIC, 'palette_classic.json')

    print("=" * 60)
    print("✓ All sprite options generated successfully!")
    print("\nNext steps:")
    print("1. Review the three sprite options")
    print("2. Choose your favorite for animation development")
    print("3. Define additional color palettes for your three parakeets")
