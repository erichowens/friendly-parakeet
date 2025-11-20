# Friendly Parakeet SNES-Style Mascot Sprites

## Overview

This directory contains a complete SNES-style pixel art mascot system for Friendly Parakeet, featuring three sprite designs with full color palette swapping support inspired by classic fighting games like Mortal Kombat.

## What You Have

### ✓ Three Sprite Options (32×32 pixels each)

1. **Option 1: Classic Side-View** - Traditional perched pose, facing right
2. **Option 2: Cute Front-Facing** - Chibi-style with big eyes, most mascot-friendly
3. **Option 3: Dynamic Action** - 3/4 view with extended wing, most energetic

### ✓ Six Color Palettes

1. **Classic Green & Yellow** - Traditional parakeet colors (default)
2. **Sky Blue & White** - Calm, serene blue parakeet
3. **Sunset Orange & Yellow** - Warm, energetic orange
4. **Royal Purple** - Mysterious rare variant
5. **Cherry Blossom Pink** - Gentle and friendly
6. **Monochrome Classic** - Retro Game Boy aesthetic

### ✓ Preview Images

All 18 combinations (3 sprites × 6 palettes) have been pre-generated in `palette_previews/`:
- Individual sprite+palette PNGs (256×256 pixels, 8× scale)
- Preview sheets showing all palettes for each sprite

## Quick Start

### View All Variations

```bash
cd assets/sprites/palette_previews
# Open preview_sheet_option1_classic.png to see all Option 1 palettes
# Open preview_sheet_option2_cute.png to see all Option 2 palettes
# Open preview_sheet_option3_dynamic.png to see all Option 3 palettes
```

### Generate Sprites with Different Palettes

```bash
cd assets/sprites
python generate_all_palettes.py
```

This regenerates all 18 sprite+palette combinations in the `palette_previews/` directory.

## Customizing Colors for Your Three Parakeets

To match your actual parakeets' colors:

1. **Edit the palette JSON files** in `palettes/`:
   - `palette_classic.json` - Your first parakeet
   - `palette_blue.json` - Your second parakeet
   - `palette_orange.json` - Your third parakeet

2. **Color structure** in each palette file:
   ```json
   {
     "name": "My Parakeet Name",
     "description": "Description of this color scheme",
     "colors": {
       "body_dark": [R, G, B],     // Dark body color (shadows)
       "body_main": [R, G, B],     // Main body color
       "body_light": [R, G, B],    // Body highlights
       "chest_dark": [R, G, B],    // Dark chest color
       "chest_main": [R, G, B],    // Main chest color
       "chest_light": [R, G, B],   // Chest highlights
       "accent": [R, G, B]         // Wing/tail accent
     }
   }
   ```

3. **RGB values**: 0-255 for each channel (Red, Green, Blue)

4. **Regenerate sprites** after editing:
   ```bash
   python generate_all_palettes.py
   ```

## Next Steps

### Phase 1: Choose Your Sprite (Recommended: Option 2)

Based on your goal of a "face of the app" mascot, **Option 2 (Cute Front-Facing)** is recommended because:
- Most mascot-friendly (faces the viewer)
- Big expressive eyes
- Perfect for app icons, headers, and branding
- Chibi proportions = maximum cute factor

### Phase 2: Create Animation Frames

See `ANIMATION_PLAN.md` for detailed animation specifications. For Option 2, you'll need:
- **6 frames** for the idle bounce animation
- **Frame duration**: 8 game frames each (~0.13s per frame)
- **Total loop time**: 0.8 seconds

**Recommended tools**:
- **Aseprite** ($19.99) - Professional, best animation timeline
- **LibreSprite** (Free) - Open source alternative
- **Piskel** (Free, web) - Beginner-friendly online editor

**Workflow**:
1. Open `parakeet_option2_cute_front_view.png` in your pixel art tool
2. Create 6 animation frames (see ANIMATION_PLAN.md for frame details)
3. Export each frame as separate PNG
4. Test the loop to ensure smooth animation

### Phase 3: Integrate into Dashboard

Once you have animated frames, integration involves:
1. Creating sprite renderer module (`src/parakeet/sprite_renderer.py`)
2. Adding mascot to dashboard template
3. Implementing palette selector in settings
4. Connecting mascot emotions to app state

See `TECHNICAL_SPECS.md` for complete integration plan.

## File Structure

```
sprites/
├── README.md                          # This file
├── ANIMATION_PLAN.md                  # Detailed animation specifications
├── COLOR_PALETTE_SWAPPING.md          # Complete palette swap guide
├── TECHNICAL_SPECS.md                 # Full technical documentation
│
├── generate_parakeet_sprites.py       # Main sprite generator
├── generate_all_palettes.py           # Palette variation generator
│
├── parakeet_option1_classic_side_view.png    # Base sprite 1
├── parakeet_option2_cute_front_view.png      # Base sprite 2 ⭐
├── parakeet_option3_dynamic_action.png       # Base sprite 3
│
├── palettes/                          # Color palette definitions
│   ├── palette_classic.json           # Green/Yellow (default)
│   ├── palette_blue.json              # Sky Blue/White
│   ├── palette_orange.json            # Sunset Orange
│   ├── palette_purple.json            # Royal Purple
│   ├── palette_pink.json              # Cherry Blossom
│   └── palette_grayscale.json         # Monochrome
│
└── palette_previews/                  # Pre-generated variations
    ├── preview_sheet_option1_classic.png    # All palettes for Option 1
    ├── preview_sheet_option2_cute.png       # All palettes for Option 2 ⭐
    ├── preview_sheet_option3_dynamic.png    # All palettes for Option 3
    └── [18 individual sprite+palette PNGs]
```

## Documentation

### Essential Reading

1. **README.md** (this file) - Quick start and overview
2. **ANIMATION_PLAN.md** - How to create animation frames (4-6 frames per sprite)
3. **COLOR_PALETTE_SWAPPING.md** - Complete guide to palette swapping system
4. **TECHNICAL_SPECS.md** - Full technical specifications and integration plan

### Key Features

- ✅ True SNES hardware constraints (32×32, 16 colors)
- ✅ Mortal Kombat-style palette swapping
- ✅ Three distinct sprite styles to choose from
- ✅ Six pre-configured color palettes
- ✅ Fully customizable colors via JSON
- ✅ Comprehensive documentation
- ✅ Animation specifications ready
- ✅ Dashboard integration plan complete

## Technical Details

### Sprite Specifications
- **Resolution**: 32×32 pixels (SNES standard)
- **Colors**: 16 colors per sprite (SNES compliant)
- **Palette Format**: 15-bit RGB (5 bits per channel)
- **File Format**: PNG with alpha transparency
- **Scale**: Base sprites at 256×256 (8× upscale for visibility)

### Palette Swapping System
- **Method**: Color index remapping (MK technique)
- **Performance**: Pre-cache all variants (<60KB total memory)
- **Customization**: User-editable JSON palette files
- **Variants**: Unlimited - create as many palettes as you want!

### Animation System
- **Frame Rate**: 6-8 FPS (SNES-accurate timing)
- **Idle Animations**: 4-6 frames per sprite
- **Loop Type**: Seamless circular loops
- **File Size**: ~3KB per animation frame, ~18KB per full animation

## Recommendations

### For Mascot/Branding
**Use Option 2 (Cute Front-Facing)** with your favorite palette:
- Best for app icon
- Perfect for dashboard header
- Most recognizable and friendly
- Easiest to brand

### For Color Palettes
Match your three actual parakeets by editing:
1. `palette_classic.json` → Your first parakeet's colors
2. `palette_blue.json` → Your second parakeet's colors
3. `palette_orange.json` → Your third parakeet's colors

Keep the other palettes (purple, pink, grayscale) as bonus options for users!

### Animation Priority
1. **Start with static mascot** - Add sprites to dashboard without animation first
2. **Add idle animation** - Create 4-6 frame breathing/bounce animation
3. **Add interactivity** - Hover effects, click responses
4. **Add emotional states** - Different animations for active/idle/error states

## Examples of Use

### As App Icon
Use Option 2 (cute front-facing) at 512×512 resolution with your favorite palette.

### In Dashboard Header
Animated idle loop, changes color based on user's palette setting.

### Project Status Indicator
- **Green palette**: Active projects (work happening)
- **Blue palette**: Stable projects (no recent changes)
- **Orange palette**: Projects needing attention
- **Grayscale**: Archived projects

### Loading States
Continuous wing flutter animation (fast loop).

### Celebration
Bounce animation when commits succeed or milestones reached.

## Credits

- **Design**: Claude Code (AI) with SNES pixel art research
- **Inspiration**: SNES-era games (Super Mario World, Yoshi's Island)
- **Palette Technique**: Mortal Kombat color swap system
- **Project**: Friendly Parakeet by @erichowens

## Support

For questions or custom palette help:
1. See documentation in this directory
2. Check CLAUDE.md for project context
3. Open issue on GitHub

---

**Have fun customizing your parakeet mascot!** 🦜✨

Choose your favorite sprite, tweak the colors to match your real parakeets, and bring your mascot to life with animation!
