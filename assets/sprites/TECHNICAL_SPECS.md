# Friendly Parakeet Mascot - Technical Specifications
## SNES-Style Pixel Art Sprite System

## Project Overview

**Goal**: Create a high-quality SNES-style parakeet mascot for the Friendly Parakeet app with:
- Three design options for selection
- Color palette swapping (inspired by Mortal Kombat)
- Smooth idle animations
- Integration with Flask dashboard
- User-customizable colors

## File Structure

```
friendly-parakeet/
├── assets/
│   └── sprites/
│       ├── generate_parakeet_sprites.py      # Sprite generator script
│       ├── ANIMATION_PLAN.md                 # Animation specifications
│       ├── COLOR_PALETTE_SWAPPING.md         # Palette swap implementation
│       ├── TECHNICAL_SPECS.md                # This file
│       │
│       ├── base/                             # Base sprites (not animated yet)
│       │   ├── parakeet_option1_classic_side_view.png
│       │   ├── parakeet_option2_cute_front_view.png
│       │   └── parakeet_option3_dynamic_action.png
│       │
│       ├── frames/                           # Animation frames (to be created)
│       │   ├── option1/
│       │   │   ├── idle_frame_01.png
│       │   │   ├── idle_frame_02.png
│       │   │   ├── idle_frame_03.png
│       │   │   └── idle_frame_04.png
│       │   ├── option2/
│       │   └── option3/
│       │
│       ├── palettes/                         # Color palette definitions
│       │   ├── palette_classic.json          # Green/Yellow (default)
│       │   ├── palette_blue.json             # Sky Blue/White
│       │   ├── palette_orange.json           # Sunset Orange/Yellow
│       │   ├── palette_purple.json           # Bonus: Purple
│       │   ├── palette_pink.json             # Bonus: Pink
│       │   └── palette_grayscale.json        # Bonus: Monochrome
│       │
│       ├── spritesheets/                     # Compiled sprite sheets
│       │   ├── option1_classic_idle.png      # All frames in one image
│       │   ├── option2_cute_idle.png
│       │   └── option3_dynamic_idle.png
│       │
│       └── animations/                       # Animation metadata
│           ├── idle_classic.json
│           ├── idle_cute.json
│           └── idle_dynamic.json
│
└── src/parakeet/
    ├── sprite_renderer.py                    # New module for rendering sprites
    ├── palette_manager.py                    # New module for palette management
    └── dashboard.py                          # Updated with mascot integration
```

## SNES Hardware Specifications

### Display Resolution
- **Native**: 256×224 pixels (NTSC) / 256×240 (PAL)
- **Modes**: Supports up to 512×448 with limitations
- **Aspect Ratio**: 8:7 pixel ratio (slightly wider than square)

### Sprite Specifications
- **Sprite Sizes**: 8×8, 16×16, 32×32, or 64×64 pixels
- **Max Sprites**: 128 total on-screen
- **Max per Scanline**: 32 sprites
- **Color Depth**: 4 bits per pixel (16 colors)
- **Palette Slots**: 8 independent 16-color palettes

### Color System
- **Color Space**: 15-bit RGB (5 bits per channel)
- **Total Colors**: 32,768 possible colors
- **On-screen**: Up to 256 colors simultaneously
- **Per Sprite**: 16 colors from one palette slot

### Memory
- **VRAM**: 64 KB total
- **Sprite Data**: 32 KB allocated for sprite graphics
- **Size per 32×32 sprite**: 2 KB (512 pixels × 4 bits)

## Our Sprite Specifications

### Base Sprite Design
- **Size**: 32×32 pixels (standard SNES sprite)
- **Colors**: 16 colors per sprite (SNES compliant)
- **Palette**: Indexed color mode for easy swapping
- **Transparency**: Color index 0 reserved
- **Style**: SNES-era pixel art aesthetic

### Three Design Options

#### Option 1: Classic Side-View
- **Pose**: Perched, facing right
- **Style**: Traditional SNES platformer sprite
- **Character**: Calm, approachable
- **Best For**: General-purpose mascot, status indicators
- **Animation**: Simple breathing with 4 frames

#### Option 2: Cute Front-Facing
- **Pose**: Looking at viewer (chibi style)
- **Style**: Big eyes, round proportions
- **Character**: Friendly, kawaii aesthetic
- **Best For**: App icon, welcome screens, mascot logo
- **Animation**: Bouncy idle with 6 frames

#### Option 3: Dynamic Action
- **Pose**: 3/4 view with extended wing
- **Style**: More angular, action-oriented
- **Character**: Energetic, active
- **Best For**: Loading states, active project indicators
- **Animation**: Wing flutter with 6 frames

### Color Palette Structure

Each palette uses 16 color slots:

```
Slot  | Name          | Usage                        | Bytes (RGB555)
------|---------------|------------------------------|---------------
0     | transparent   | Background (alpha = 0)       | 0x0000
1     | outline_dark  | Main outline, hard shadows   | 0x2108
2     | outline_light | Soft shadows, AA             | 0x4210
3-5   | body_*        | Primary body color (3 shades)| Varies
6-8   | chest_*       | Chest/belly color (3 shades) | Varies
9-10  | beak_*        | Beak color (2 shades)        | Varies
11-12 | eye_*         | Eye white + pupil            | Fixed
13-14 | feet_*        | Feet color (2 shades)        | Varies
15    | accent        | Wings/tail accent            | Varies
```

**Total Palette Size**: 16 colors × 2 bytes = 32 bytes per palette (tiny!)

## Animation Specifications

### Frame Rate
- **Game Logic**: 60 FPS (SNES standard)
- **Animation FPS**: 6-8 FPS (update every 8-10 frames)
- **Timing**: Frame durations defined per-frame

### Idle Animations

| Option  | Frames | Duration | Loop Type | Movement Type      |
|---------|--------|----------|-----------|-------------------|
| Option 1| 4      | 0.53s    | Circular  | Breathing bob     |
| Option 2| 6      | 0.80s    | Circular  | Happy bounce      |
| Option 3| 6      | 0.90s    | Circular  | Wing flutter      |

### Memory Requirements

```
Per Animation Set:
  Base sprite:        32×32×4 bits = 512 bytes
  × 6 frames:                       = 3 KB
  × 6 palettes:                     = 18 KB

Total per option:                   = ~18 KB
All three options:                  = ~54 KB
```

**Conclusion**: Extremely lightweight - can load all sprites and all palettes into memory.

## Implementation Phases

### Phase 1: Core Sprite System ✓ (Complete)
- [x] Research SNES specifications
- [x] Design three sprite options
- [x] Create sprite generator script
- [x] Generate base sprites (static, no animation)
- [x] Define color palette structure
- [x] Create palette JSON format
- [x] Document animation plan
- [x] Document palette swapping system

### Phase 2: Animation Creation (Next Steps)
- [ ] Choose preferred sprite option (or keep all three!)
- [ ] Create animation frames using pixel art tool (Aseprite/LibreSprite/Piskel)
- [ ] Export individual frames as PNG files
- [ ] Create sprite sheet compiler
- [ ] Generate sprite sheets for each option
- [ ] Create animation metadata JSON files
- [ ] Test animations in viewer

### Phase 3: Color Palette System
- [ ] Create palette JSON files for user's three parakeets
- [ ] Write palette swapper utility (`palette_manager.py`)
- [ ] Test palette swapping with all three base sprites
- [ ] Generate palette preview images
- [ ] Add bonus palettes (purple, pink, grayscale)
- [ ] Create palette selector UI component

### Phase 4: Dashboard Integration
- [ ] Create sprite renderer module (`sprite_renderer.py`)
- [ ] Add mascot to dashboard header
- [ ] Implement settings page for palette selection
- [ ] Add animation controls (play/pause)
- [ ] Hook mascot emotions to app state (idle/active/error)
- [ ] Add smooth transitions between states
- [ ] Performance testing and optimization

### Phase 5: Polish & Features
- [ ] Add blink animation overlay
- [ ] Create "look around" occasional animation
- [ ] Add hover interactions (wing lift, head tilt)
- [ ] Create click/activation animation
- [ ] Add loading state animation (continuous flutter)
- [ ] Custom palette editor UI
- [ ] Palette export/import functionality
- [ ] Share palettes with community

## Integration with Existing Code

### Config Schema Updates

Add to `src/parakeet/config.py`:

```python
DEFAULT_CONFIG = {
    # ... existing config ...
    'appearance': {
        'mascot_enabled': True,
        'mascot_sprite': 'option2',  # option1, option2, or option3
        'mascot_palette': 'classic',  # classic, blue, orange, etc.
        'mascot_animation': True,
        'mascot_position': 'header-right',  # header-right, header-left, floating
        'mascot_size': 'medium',  # small (32px), medium (64px), large (96px)
        'custom_palettes_dir': '~/.parakeet/palettes',
    }
}
```

### Dashboard Template Updates

Add to `templates/index.html`:

```html
<!-- Mascot Container -->
<div id="parakeet-mascot" class="mascot-container">
    <canvas id="mascot-canvas" width="64" height="64"></canvas>
</div>

<!-- Mascot Settings Modal -->
<div id="mascot-settings" class="modal">
    <h3>Customize Your Parakeet</h3>

    <label>Sprite Style:</label>
    <select id="sprite-select">
        <option value="option1">Classic Side-View</option>
        <option value="option2">Cute Front-Facing</option>
        <option value="option3">Dynamic Action</option>
    </select>

    <label>Color Palette:</label>
    <div class="palette-grid">
        <div class="palette-option" data-palette="classic">
            <img src="/static/sprites/preview_classic.png">
            <span>Green & Yellow</span>
        </div>
        <div class="palette-option" data-palette="blue">
            <img src="/static/sprites/preview_blue.png">
            <span>Sky Blue & White</span>
        </div>
        <div class="palette-option" data-palette="orange">
            <img src="/static/sprites/preview_orange.png">
            <span>Sunset Orange</span>
        </div>
    </div>
</div>
```

### New API Endpoints

Add to `src/parakeet/dashboard.py`:

```python
@app.route('/api/mascot/sprite/<sprite_name>/<palette_name>')
def get_mascot_sprite(sprite_name, palette_name):
    """Get sprite with specific palette applied"""
    renderer = get_sprite_renderer()
    sprite_data = renderer.get_sprite(sprite_name, palette_name)
    return send_file(sprite_data, mimetype='image/png')

@app.route('/api/mascot/animation/<sprite_name>')
def get_mascot_animation(sprite_name):
    """Get animation metadata for sprite"""
    with open(f'assets/sprites/animations/idle_{sprite_name}.json') as f:
        return jsonify(json.load(f))

@app.route('/api/mascot/palettes')
def list_palettes():
    """List all available color palettes"""
    manager = get_palette_manager()
    return jsonify(manager.list_palettes())

@app.route('/api/mascot/settings', methods=['POST'])
def update_mascot_settings():
    """Update mascot appearance settings"""
    settings = request.json
    config.set('appearance.mascot_sprite', settings['sprite'])
    config.set('appearance.mascot_palette', settings['palette'])
    return jsonify({'success': True})
```

## Performance Considerations

### Memory Usage
- **Cached sprites**: 54 KB (all variants)
- **Palette definitions**: <1 KB (all 6 palettes)
- **Animation metadata**: <2 KB
- **Total**: < 60 KB (negligible)

### CPU Usage
- **Animation updates**: Every 8-10 frames (6-8 FPS)
- **Palette swaps**: Cached (no runtime cost)
- **Rendering**: Canvas 2D (hardware accelerated)
- **Impact**: < 0.1% CPU on modern systems

### Optimization Strategies

1. **Pre-render All Variants**
   - Generate all sprite+palette combinations at app start
   - Cache in memory (60 KB total)
   - Instant switching with zero lag

2. **Lazy Load Animations**
   - Load base sprite immediately
   - Load animation frames on first view
   - Async loading doesn't block UI

3. **Sprite Sheet Batching**
   - Single texture load instead of multiple files
   - Reduce HTTP requests (web)
   - Reduce file I/O (desktop)

4. **Canvas Pooling**
   - Reuse canvas elements
   - Avoid creating/destroying objects
   - Reduce garbage collection

## Browser Compatibility

### CSS Requirements
```css
/* Pixel-perfect rendering */
image-rendering: pixelated;        /* Chrome, Edge */
image-rendering: -moz-crisp-edges; /* Firefox */
image-rendering: crisp-edges;      /* Safari */

/* Hardware acceleration */
transform: translateZ(0);
will-change: transform;
```

### Browser Support
- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- IE11: Partial (no `image-rendering: pixelated`)

## Testing Plan

### Visual Testing
- [ ] Sprites render correctly at 1×, 2×, 4×, 8× scale
- [ ] All 16 colors visible in each sprite
- [ ] Animations loop smoothly
- [ ] Palette swaps produce expected colors
- [ ] No pixel "bleeding" or anti-aliasing

### Functional Testing
- [ ] Palette changes persist after refresh
- [ ] Animation plays/pauses correctly
- [ ] Sprite selection updates correctly
- [ ] Custom palettes load properly
- [ ] Settings save to config.yaml

### Performance Testing
- [ ] Animation runs at consistent FPS
- [ ] No memory leaks during long sessions
- [ ] Palette swaps complete in < 16ms
- [ ] Dashboard loads in < 1 second with mascot

### Cross-Platform Testing
- [ ] Linux (primary platform)
- [ ] macOS
- [ ] Windows
- [ ] Web browsers (Chrome, Firefox, Safari)

## Tools and Dependencies

### Required Python Packages
```
Pillow >= 10.0.0     # Image manipulation
numpy >= 1.24.0      # Fast pixel operations (optional but recommended)
```

### Recommended Pixel Art Tools

#### Aseprite ($19.99 or compile free)
- **Pros**: Industry standard, excellent animation timeline, onion skinning
- **Cons**: Paid software
- **Link**: https://www.aseprite.org/

#### LibreSprite (Free)
- **Pros**: Free, open source, fork of old Aseprite
- **Cons**: Less features than modern Aseprite
- **Link**: https://libresprite.github.io/

#### Piskel (Free, Web-based)
- **Pros**: Free, runs in browser, beginner-friendly
- **Cons**: Limited features, requires internet
- **Link**: https://www.piskelapp.com/

#### GIMP (Free)
- **Pros**: Free, powerful, supports indexed color mode
- **Cons**: Not specialized for pixel art, steeper learning curve
- **Link**: https://www.gimp.org/

### Web Tools
- **Lospec Palette List**: Pre-made color palettes
- **Coolors**: Color palette generator
- **Pixel Art Scaler**: Test sprites at different sizes

## FAQ

### Q: Why 32×32 pixels?
A: Perfect balance of detail and SNES authenticity. 16×16 is too small for complex designs, 64×64 exceeds common SNES usage. 32×32 was standard for main characters (Mario, Mega Man X).

### Q: Can I use more than 16 colors?
A: Technically yes (modern systems have no limits), but staying within SNES constraints maintains the authentic retro aesthetic. If you need more colors, consider using multiple sprites layered together (body + accessories).

### Q: How do I create smooth animations?
A: Key principles:
1. Move pixels gradually (1-2 pixels per frame)
2. Use onion skinning to see previous frames
3. Test the loop (frame N should flow into frame 1)
4. Even spacing: if moving 6 pixels over 3 frames, move 2 per frame

### Q: Should I anti-alias my sprites?
A: NO! Anti-aliasing ruins pixel art. Every pixel should be a solid color from your palette. Use manual "AA" by adding intermediate colors to your palette if needed.

### Q: How many animation frames is optimal?
A: For idle animations: 4-6 frames is sweet spot. Fewer looks choppy, more is diminishing returns. Save complex animations (8+ frames) for special actions like "celebrating" or "error state".

### Q: Can I share my custom palettes?
A: Yes! Palettes are just JSON files. Export yours and share with the community. Consider creating a palette gallery in the app or on GitHub.

## Resources

### Documentation
- `ANIMATION_PLAN.md` - Complete animation guidelines and frame specifications
- `COLOR_PALETTE_SWAPPING.md` - Palette swap implementation and your three parakeet colors
- `TECHNICAL_SPECS.md` - This file (technical overview)

### Scripts
- `generate_parakeet_sprites.py` - Main sprite generator with three options
- `apply_palette_swap.py` - (To be created) Utility for batch palette swapping
- `create_spritesheet.py` - (To be created) Compile frames into sprite sheet

### Assets
- `base/` - Static base sprites (already generated!)
- `palettes/` - Color palette JSON files
- `frames/` - Individual animation frames (to be created)
- `spritesheets/` - Compiled texture atlases (to be created)

## Next Immediate Steps

1. **Review the three sprite options** (already generated!)
   - Option 1: Classic side-view
   - Option 2: Cute front-facing
   - Option 3: Dynamic action pose

2. **Choose your favorite** (or keep all three for variety!)

3. **Define your three parakeet color palettes**
   - Palette 1: Your first parakeet's colors
   - Palette 2: Your second parakeet's colors
   - Palette 3: Your third parakeet's colors

4. **Decide on animation approach**
   - Option A: Animate all three sprites
   - Option B: Pick one sprite, animate it fully
   - Option C: Start with static mascot, animate later

5. **Integration priority**
   - Dashboard header mascot (static first)
   - Add palette selector
   - Add animation later

## License and Credits

- Sprites created by: Claude Code (AI) + Your input
- Inspired by: SNES-era games (Super Mario World, Yoshi's Island, Mega Man X)
- Palette swap technique: Mortal Kombat series
- For: Friendly Parakeet project (https://github.com/erichowens/friendly-parakeet)

---

**Ready to bring your parakeet mascot to life!** 🦜✨
