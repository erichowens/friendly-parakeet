#!/usr/bin/env python3
"""Generate parakeet icon for the menu bar app."""

from PIL import Image, ImageDraw, ImageFont
import os

def create_parakeet_icon():
    """Create a simple parakeet icon."""
    # Create images at different sizes
    sizes = [16, 32, 64, 128, 256, 512, 1024]

    for size in sizes:
        # Create a new image with transparent background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Calculate dimensions
        center_x = size // 2
        center_y = size // 2

        # Draw a simple parakeet silhouette
        # Body (oval)
        body_width = int(size * 0.5)
        body_height = int(size * 0.6)
        body_left = center_x - body_width // 2
        body_top = center_y - body_height // 2 + size // 10

        draw.ellipse([
            body_left, body_top,
            body_left + body_width, body_top + body_height
        ], fill=(76, 175, 80), outline=(56, 142, 60), width=max(1, size // 32))

        # Head (circle)
        head_size = int(size * 0.35)
        head_left = center_x - head_size // 2
        head_top = body_top - head_size // 3

        draw.ellipse([
            head_left, head_top,
            head_left + head_size, head_top + head_size
        ], fill=(102, 187, 106), outline=(76, 175, 80), width=max(1, size // 32))

        # Eye
        eye_size = max(2, size // 16)
        eye_x = center_x + size // 12
        eye_y = head_top + head_size // 3

        draw.ellipse([
            eye_x - eye_size // 2, eye_y - eye_size // 2,
            eye_x + eye_size // 2, eye_y + eye_size // 2
        ], fill=(33, 33, 33))

        # Beak (triangle)
        beak_size = size // 10
        beak_points = [
            (center_x + head_size // 2, eye_y),
            (center_x + head_size // 2 + beak_size, eye_y),
            (center_x + head_size // 2, eye_y + beak_size // 2)
        ]
        draw.polygon(beak_points, fill=(255, 193, 7))

        # Tail feathers
        tail_width = int(size * 0.3)
        tail_height = int(size * 0.25)
        tail_left = body_left - tail_width // 2
        tail_top = body_top + body_height - tail_height

        draw.ellipse([
            tail_left, tail_top,
            tail_left + tail_width, tail_top + tail_height
        ], fill=(56, 142, 60), outline=(46, 125, 50), width=max(1, size // 32))

        # Save individual size
        img.save(f'parakeet_icon_{size}x{size}.png')

    # Create the main PNG icon
    main_icon = Image.open('parakeet_icon_512x512.png')
    main_icon.save('parakeet_icon.png')

    print("✅ Generated parakeet icons at multiple resolutions")

    # Create .icns file for macOS (requires iconutil on Mac)
    try:
        # Create iconset directory
        os.makedirs('parakeet.iconset', exist_ok=True)

        # Copy files with correct names for iconset
        icon_mapping = {
            16: 'icon_16x16.png',
            32: 'icon_16x16@2x.png',
            32: 'icon_32x32.png',
            64: 'icon_32x32@2x.png',
            128: 'icon_128x128.png',
            256: 'icon_128x128@2x.png',
            256: 'icon_256x256.png',
            512: 'icon_256x256@2x.png',
            512: 'icon_512x512.png',
            1024: 'icon_512x512@2x.png'
        }

        for size, filename in icon_mapping.items():
            source = f'parakeet_icon_{size}x{size}.png'
            if os.path.exists(source):
                img = Image.open(source)
                img.save(f'parakeet.iconset/{filename}')

        # Convert to .icns using iconutil
        os.system('iconutil -c icns parakeet.iconset -o parakeet_icon.icns')

        # Clean up
        os.system('rm -rf parakeet.iconset')

        print("✅ Generated parakeet_icon.icns for macOS")

    except Exception as e:
        print(f"⚠️  Could not create .icns file (requires macOS with iconutil): {e}")

if __name__ == '__main__':
    create_parakeet_icon()