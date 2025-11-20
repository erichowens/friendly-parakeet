# Color Palette Swapping System
## Mortal Kombat-Style Palette Swaps for Friendly Parakeet

## Overview

This document explains how to implement a flexible color palette swapping system inspired by classic fighting games like Mortal Kombat, where characters like Sub-Zero, Scorpion, and Reptile share the same sprite data but use different color palettes.

**Key Concept**: One base sprite design + multiple color palettes = Multiple character variants with zero additional sprite work.

## The Mortal Kombat Technique

### How It Works

1. **Indexed Color System**: Sprites use color indices (0-15) rather than RGB values
2. **Palette Definition**: Each color index maps to a specific RGB value
3. **Runtime Swapping**: Change the palette lookup table without touching sprite pixel data
4. **Memory Efficiency**: Store one sprite, many palettes (tiny JSON files)

### Example:
```
Pixel value at (10, 15) = Color Index 4 (body_main)

Palette "Classic":     Index 4 = RGB(153, 217, 70)  [Green]
Palette "Blue":        Index 4 = RGB(70, 150, 217)  [Blue]
Palette "Yellow":      Index 4 = RGB(217, 195, 70)  [Yellow]
```

## Color Slot Definitions

### The 16-Color SNES Palette Structure

Our parakeet sprites use 16 color slots with specific roles:

| Index | Slot Name      | Purpose                          | Swap Priority |
|-------|----------------|----------------------------------|---------------|
| 0     | transparent    | Transparent pixels               | Never swap    |
| 1     | outline_dark   | Main outline/shadows             | Rarely swap   |
| 2     | outline_light  | Soft shadows/anti-aliasing       | Rarely swap   |
| 3     | body_dark      | Dark body color (shadows)        | **PRIMARY**   |
| 4     | body_main      | Main body color                  | **PRIMARY**   |
| 5     | body_light     | Body highlights                  | **PRIMARY**   |
| 6     | chest_dark     | Dark chest/belly color (shadows) | **PRIMARY**   |
| 7     | chest_main     | Main chest/belly color           | **PRIMARY**   |
| 8     | chest_light    | Chest highlights                 | **PRIMARY**   |
| 9     | beak_dark      | Beak shadows                     | Secondary     |
| 10    | beak_main      | Beak main color                  | Secondary     |
| 11    | eye_white      | Eye whites                       | Rarely swap   |
| 12    | eye_pupil      | Eye pupil                        | Rarely swap   |
| 13    | feet_dark      | Feet shadows                     | Secondary     |
| 14    | feet_main      | Feet main color                  | Secondary     |
| 15    | accent         | Wing/tail accent color           | **PRIMARY**   |

**Swap Priority Legend:**
- **PRIMARY**: These colors define the character's color scheme (body, chest, accent)
- **Secondary**: Can be changed for variety (beak, feet)
- **Rarely swap**: Usually keep consistent across all palettes (outlines, eyes)

## User's Three Parakeet Palettes

Based on your three parakeets, here are suggested color schemes:

### Palette 1: Classic Green/Yellow Parakeet (Default)
```json
{
  "name": "Classic Green & Yellow",
  "description": "Traditional parakeet colors - vibrant green with yellow chest",
  "colors": {
    "transparent": [0, 0, 0, 0],
    "outline_dark": [33, 33, 33],
    "outline_light": [66, 66, 66],
    "body_dark": [102, 176, 50],
    "body_main": [153, 217, 70],
    "body_light": [198, 239, 130],
    "chest_dark": [230, 190, 50],
    "chest_main": [255, 230, 100],
    "chest_light": [255, 250, 180],
    "beak_dark": [200, 120, 40],
    "beak_main": [255, 160, 70],
    "eye_white": [255, 255, 255],
    "eye_pupil": [50, 50, 80],
    "feet_dark": [180, 100, 60],
    "feet_main": [220, 140, 90],
    "accent": [100, 180, 220]
  }
}
```

### Palette 2: Sky Blue/White Parakeet
```json
{
  "name": "Sky Blue & White",
  "description": "Serene blue parakeet with white chest - calm and peaceful",
  "colors": {
    "transparent": [0, 0, 0, 0],
    "outline_dark": [33, 33, 33],
    "outline_light": [66, 66, 66],
    "body_dark": [65, 135, 195],
    "body_main": [100, 180, 240],
    "body_light": [160, 210, 250],
    "chest_dark": [220, 225, 230],
    "chest_main": [245, 250, 255],
    "chest_light": [255, 255, 255],
    "beak_dark": [180, 140, 120],
    "beak_main": [220, 190, 170],
    "eye_white": [255, 255, 255],
    "eye_pupil": [50, 50, 80],
    "feet_dark": [160, 130, 110],
    "feet_main": [200, 170, 150],
    "accent": [80, 120, 200]
  }
}
```

### Palette 3: Sunset Orange/Yellow Parakeet
```json
{
  "name": "Sunset Orange & Yellow",
  "description": "Warm sunset colors - energetic orange with golden accents",
  "colors": {
    "transparent": [0, 0, 0, 0],
    "outline_dark": [33, 33, 33],
    "outline_light": [66, 66, 66],
    "body_dark": [200, 110, 40],
    "body_main": [255, 145, 60],
    "body_light": [255, 185, 120],
    "chest_dark": [235, 175, 50],
    "chest_main": [255, 210, 80],
    "chest_light": [255, 240, 150],
    "beak_dark": [160, 80, 50],
    "beak_main": [210, 120, 80],
    "eye_white": [255, 255, 255],
    "eye_pupil": [50, 50, 80],
    "feet_dark": [140, 90, 60],
    "feet_main": [180, 120, 90],
    "accent": [220, 150, 80]
  }
}
```

## Additional Bonus Palettes

### Palette 4: Purple/Violet Parakeet (Like MK's Reptile)
```json
{
  "name": "Royal Purple",
  "description": "Mysterious purple variant - rare and special",
  "colors": {
    "body_dark": [110, 70, 155],
    "body_main": [160, 110, 215],
    "body_light": [200, 160, 240],
    "chest_dark": [190, 160, 200],
    "chest_main": [230, 210, 240],
    "chest_light": [250, 240, 255],
    "accent": [140, 90, 200]
  }
}
```

### Palette 5: Pink/Rose Parakeet
```json
{
  "name": "Cherry Blossom Pink",
  "description": "Soft pink palette - gentle and friendly",
  "colors": {
    "body_dark": [200, 100, 140],
    "body_main": [255, 150, 190],
    "body_light": [255, 200, 225],
    "chest_dark": [240, 200, 210],
    "chest_main": [255, 230, 240],
    "chest_light": [255, 245, 250],
    "accent": [255, 120, 180]
  }
}
```

### Palette 6: Monochrome/Grayscale
```json
{
  "name": "Monochrome Classic",
  "description": "Retro Game Boy aesthetic - nostalgic grayscale",
  "colors": {
    "body_dark": [80, 85, 90],
    "body_main": [130, 140, 145],
    "body_light": [190, 200, 205],
    "chest_dark": [160, 165, 170],
    "chest_main": [210, 215, 220],
    "chest_light": [245, 245, 250],
    "accent": [100, 110, 120]
  }
}
```

## Implementation Guide

### Python Implementation

#### 1. Palette Loader
```python
import json
from PIL import Image
import numpy as np

class PaletteManager:
    def __init__(self, palettes_dir='./palettes'):
        self.palettes_dir = palettes_dir
        self.palettes = {}
        self.load_all_palettes()

    def load_palette(self, palette_file):
        """Load a single palette JSON file"""
        with open(f"{self.palettes_dir}/{palette_file}") as f:
            return json.load(f)

    def load_all_palettes(self):
        """Load all available palettes"""
        import os
        for file in os.listdir(self.palettes_dir):
            if file.endswith('.json'):
                name = file.replace('.json', '')
                self.palettes[name] = self.load_palette(file)

    def get_palette(self, name):
        """Get palette by name"""
        return self.palettes.get(name, self.palettes['classic'])
```

#### 2. Sprite Palette Swapper
```python
def apply_palette_swap(sprite_image, old_palette, new_palette):
    """
    Apply palette swap to sprite image

    Args:
        sprite_image: PIL Image in RGBA mode
        old_palette: dict mapping color names to RGB values
        new_palette: dict mapping color names to RGB values

    Returns:
        New PIL Image with swapped palette
    """
    # Convert image to numpy array for fast pixel manipulation
    img_array = np.array(sprite_image)
    result = img_array.copy()

    # Build color mapping
    for color_name in old_palette['colors'].keys():
        if color_name == 'transparent':
            continue

        old_color = tuple(old_palette['colors'][color_name][:3])
        new_color = tuple(new_palette['colors'][color_name][:3])

        # Find all pixels with old color and replace with new color
        mask = np.all(img_array[:, :, :3] == old_color, axis=2)
        result[mask, :3] = new_color

    return Image.fromarray(result)


def quick_palette_swap(sprite_image, palette_json):
    """
    Faster version using pre-generated lookup table
    """
    # Create color lookup table (LUT)
    lut = create_palette_lut(palette_json)

    img_array = np.array(sprite_image)
    result = img_array.copy()

    # Apply LUT in single operation (vectorized)
    for old_rgb, new_rgb in lut.items():
        mask = np.all(img_array[:, :, :3] == old_rgb, axis=2)
        if mask.any():
            result[mask, :3] = new_rgb

    return Image.fromarray(result)
```

#### 3. Cached Palette System (Performance Optimization)
```python
class CachedSpriteRenderer:
    """
    Cache pre-rendered sprites with different palettes
    Only regenerate when palette changes
    """
    def __init__(self, base_sprite):
        self.base_sprite = base_sprite
        self.cache = {}

    def get_sprite(self, palette_name):
        if palette_name not in self.cache:
            palette = palette_manager.get_palette(palette_name)
            self.cache[palette_name] = apply_palette_swap(
                self.base_sprite,
                palette_manager.get_palette('classic'),
                palette
            )
        return self.cache[palette_name]

    def clear_cache(self):
        self.cache = {}
```

### JavaScript/Web Implementation

#### 1. Canvas-Based Palette Swapping
```javascript
class ParakeetSpriteRenderer {
    constructor(spriteImage, basePalette) {
        this.spriteImage = spriteImage;
        this.basePalette = basePalette;
        this.canvas = document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.paletteCache = new Map();
    }

    swapPalette(newPalette) {
        // Check cache first
        const cacheKey = newPalette.name;
        if (this.paletteCache.has(cacheKey)) {
            return this.paletteCache.get(cacheKey);
        }

        // Setup canvas
        this.canvas.width = this.spriteImage.width;
        this.canvas.height = this.spriteImage.height;

        // Draw original sprite
        this.ctx.drawImage(this.spriteImage, 0, 0);

        // Get image data
        const imageData = this.ctx.getImageData(
            0, 0, this.canvas.width, this.canvas.height
        );
        const data = imageData.data;

        // Build color mapping
        const colorMap = this.buildColorMap(this.basePalette, newPalette);

        // Swap colors pixel by pixel
        for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i + 1];
            const b = data[i + 2];
            const a = data[i + 3];

            // Skip transparent pixels
            if (a === 0) continue;

            const colorKey = `${r},${g},${b}`;
            const newColor = colorMap.get(colorKey);

            if (newColor) {
                data[i] = newColor.r;
                data[i + 1] = newColor.g;
                data[i + 2] = newColor.b;
            }
        }

        // Put modified data back
        this.ctx.putImageData(imageData, 0, 0);

        // Cache result
        const result = this.canvas.toDataURL();
        this.paletteCache.set(cacheKey, result);

        return result;
    }

    buildColorMap(oldPalette, newPalette) {
        const map = new Map();

        for (const [colorName, oldRGB] of Object.entries(oldPalette.colors)) {
            if (colorName === 'transparent') continue;

            const newRGB = newPalette.colors[colorName];
            const key = `${oldRGB[0]},${oldRGB[1]},${oldRGB[2]}`;
            map.set(key, {
                r: newRGB[0],
                g: newRGB[1],
                b: newRGB[2]
            });
        }

        return map;
    }
}
```

#### 2. CSS Filter Approach (Approximate, Fast)
```css
/* Approximate palette swaps using CSS filters */
.parakeet-blue {
    filter: hue-rotate(180deg) saturate(1.2);
}

.parakeet-orange {
    filter: hue-rotate(30deg) saturate(1.4) brightness(1.1);
}

.parakeet-purple {
    filter: hue-rotate(270deg) saturate(1.3);
}
```

**Note**: CSS filters are fast but approximate. For pixel-perfect palette swaps, use Canvas approach.

### React Component Example
```jsx
import React, { useState, useEffect } from 'react';

const ParakeetMascot = ({ palettePreset = 'classic' }) => {
    const [currentSprite, setCurrentSprite] = useState(null);
    const [currentFrame, setCurrentFrame] = useState(0);

    useEffect(() => {
        // Load sprite with selected palette
        const renderer = new ParakeetSpriteRenderer(
            baseSpriteImage,
            palettes.classic
        );
        const swappedSprite = renderer.swapPalette(palettes[palettePreset]);
        setCurrentSprite(swappedSprite);
    }, [palettePreset]);

    useEffect(() => {
        // Animate frames
        const interval = setInterval(() => {
            setCurrentFrame(frame => (frame + 1) % 4);
        }, 150); // ~6 FPS

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="parakeet-mascot">
            <img
                src={currentSprite}
                alt="Friendly Parakeet"
                style={{
                    imageRendering: 'pixelated',
                    transform: `translateY(${currentFrame % 2 ? '2px' : '0px'})`
                }}
            />
        </div>
    );
};
```

## User Settings Integration

### Config File Structure
```yaml
# ~/.parakeet/config.yaml
appearance:
  mascot_palette: "classic"  # classic, blue, orange, purple, pink, grayscale
  allow_custom_palettes: true
  palette_directory: "~/.parakeet/palettes"

# User can add custom palettes here
custom_palettes:
  - name: "My Custom Parakeet"
    file: "custom_green_red.json"
```

### Dashboard Settings UI
```python
# In dashboard.py
@app.route('/api/settings/palette', methods=['POST'])
def set_palette():
    """API endpoint to change mascot palette"""
    palette_name = request.json.get('palette')
    config.set('appearance.mascot_palette', palette_name)
    return jsonify({'success': True, 'palette': palette_name})

@app.route('/api/palettes/available')
def get_available_palettes():
    """List all available palettes"""
    return jsonify({
        'palettes': palette_manager.list_palettes(),
        'current': config.get('appearance.mascot_palette')
    })
```

## Performance Considerations

### Optimization Strategies

1. **Pre-cache on Load**
   - Generate all palette variants when app starts
   - Store in memory (small file size)
   - Instant switching with no lag

2. **Lazy Loading**
   - Only generate palettes when requested
   - Good for apps with many palettes
   - Trade-off: slight delay on first switch

3. **Sprite Sheet Multiplication**
   - Pre-render all animation frames × all palettes
   - Store as sprite sheets
   - Zero runtime overhead (but larger file size)

4. **Indexed Color Mode**
   - Store sprites in 8-bit indexed PNG
   - Swap palette at image decode time
   - Most memory efficient (but requires custom decoder)

### Recommended Approach for Friendly Parakeet

**For Dashboard**: Pre-cache 3-6 most common palettes on startup
- Typical memory: 6 palettes × 6 frames × 32×32 pixels × 4 bytes = ~150KB
- Instant palette switching
- Minimal memory footprint

## Testing Your Palettes

### Visual Checklist
- [ ] All body colors clearly visible
- [ ] Good contrast between body and chest
- [ ] Outline remains visible against body colors
- [ ] Eyes readable (white stays white, pupil stays dark)
- [ ] Beak is distinguishable from body
- [ ] Palette feels cohesive (colors harmonize)

### Accessibility
- [ ] Sufficient contrast ratio (WCAG AA: 4.5:1 minimum)
- [ ] Colorblind-friendly (test with colorblind simulators)
- [ ] Works on both light and dark backgrounds

### Color Harmony
- [ ] Use complementary or analogous colors
- [ ] Consistent saturation levels across palette
- [ ] Highlight colors are noticeably lighter
- [ ] Shadow colors are noticeably darker

## Next Steps

1. **Save Your Palette Files**
   - Create JSON files for your three parakeets
   - Test them with the sprite generator

2. **Integrate into App**
   - Add palette setting to config.yaml
   - Update dashboard to show palette selector
   - Load user's preferred palette on startup

3. **Create UI for Palette Customization**
   - Color picker for each slot
   - Live preview
   - Save custom palettes
   - Share palettes with others (export/import)

## Example: Complete Workflow

```bash
# 1. Generate base sprites (already done!)
python generate_parakeet_sprites.py

# 2. Create your three palette files
cp palette_classic.json palette_blue.json
# Edit palette_blue.json with your blue parakeet colors

# 3. Generate sprites with new palettes
python apply_palette_swap.py --sprite option1 --palette blue

# 4. Test in dashboard
parakeet dashboard --palette blue

# 5. Switch palettes in real-time
# Use dashboard settings UI or:
parakeet config-set appearance.mascot_palette blue
```

---

**Remember**: The beauty of palette swapping is that you only need to create the animation frames ONCE. All palette variants share the same pixel art, just with different colors. This is how MK created multiple ninjas with minimal effort!
