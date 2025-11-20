# SNES Parakeet Sprite Animation Plan

## Overview
This document outlines the animation strategy for the Friendly Parakeet mascot sprites, following SNES hardware limitations and best practices for smooth, appealing character animation.

## Technical Specifications

### SNES Hardware Constraints
- **Sprite Size**: 32x32 pixels (base sprite)
- **Colors per Sprite**: 16 colors from a single palette slot
- **Frame Rate**: Target 6-8 FPS for idle animations (every 4-8 game frames at 60 FPS)
- **Memory**: Each 32x32 sprite = 2KB of VRAM

### Animation Timing
- **Idle Loop**: 4-6 frames, ~0.5-1 second total duration
- **Frame Hold**: 8-10 game frames per animation frame (smooth but not wasteful)
- **Loop Type**: Seamless ping-pong or circular loop

## Idle Animation Designs

### Option 1: Classic Side-View Idle Animation
**Style**: Gentle breathing with subtle bob
**Frames**: 4 frames
**Duration**: 32 frames at 60 FPS = 0.53 seconds per cycle

#### Frame Breakdown:
```
Frame 1 (Base): Neutral position, fully relaxed
Frame 2 (Inhale):
  - Body moves up 1 pixel
  - Chest expands slightly (1-2 pixels wider)
  - Tail feathers angle slightly down

Frame 3 (Peak):
  - Body at highest point (up 2 pixels from base)
  - Chest fully expanded
  - Wings very slightly lifted (1 pixel)

Frame 4 (Exhale):
  - Body moves down 1 pixel (1 pixel above base)
  - Chest returns to normal
  - Same as Frame 2 but in reverse

[Loop back to Frame 1]
```

**Pixel Changes per Frame**:
- Minimal: Only 20-30 pixels change per frame
- Focus: Body position (Y offset), chest width, subtle wing lift
- Tail: Slight angle change to enhance breathing illusion

#### Blink Animation (Optional Enhancement)
Can overlay on idle every 3-4 seconds:
- 2 frames: Eyes open → Eyes closed (3 pixels)
- Hold closed for 2 frames
- Open again

### Option 2: Cute Front-Facing Idle Animation
**Style**: Happy bounce with head tilt
**Frames**: 6 frames
**Duration**: 48 frames at 60 FPS = 0.8 seconds per cycle

#### Frame Breakdown:
```
Frame 1: Neutral, looking slightly left
Frame 2: Squash down 2 pixels (preparing to bounce)
Frame 3: Stretch up 3 pixels (bounce peak)
Frame 4: Neutral position, looking straight ahead
Frame 5: Squash down 2 pixels (preparing to bounce)
Frame 6: Stretch up 3 pixels (bounce peak), looking slightly right
[Loop back to Frame 1]
```

**Character**:
- Head tilts slightly left/right during bounces
- Wings do tiny flaps (2-3 pixel movement)
- Tail feathers fan slightly when at peak height
- Eyes: Add sparkle effect on frames 3 and 6 (1-2 pixels)

### Option 3: Dynamic Action Pose Idle
**Style**: Wing flutter and perch shift
**Frames**: 6 frames
**Duration**: 54 frames at 60 FPS = 0.9 seconds per cycle

#### Frame Breakdown:
```
Frame 1: Base pose, wing extended
Frame 2: Wing pulls in slightly (2 pixels)
Frame 3: Wing fully retracted position
Frame 4: Body shifts weight forward slightly
Frame 5: Wing begins to extend again
Frame 6: Wing at mid-extension
[Loop back to Frame 1]
```

**Movement Details**:
- Wing: Fluid feather movement (6-8 pixels of wing tip travel)
- Body: Slight weight shift (lean forward/back by 1-2 pixels)
- Tail: Compensates for weight shifts with small counter-movements

## Advanced Animation Concepts

### Idle Variations (For Polish)
Create 2-3 idle variants to prevent monotony:
1. **Standard Idle**: The main breathing loop
2. **Look Around**: Every 5-10 seconds, head turns to look left/right (2-3 frames)
3. **Stretch**: Rare (every 30 seconds), full body stretch animation (4-5 frames)

### Transition Animations
For responsive UI:
- **Hover Enter**: Quick wing lift (2 frames, 0.1s)
- **Click/Activate**: Full wing spread with bounce (4 frames, 0.2s)
- **Loading State**: Continuous wing flutter (loop 4 frames rapidly)

### Emotional States
Different idle speeds/styles for app states:
- **Active Project**: Standard idle (normal speed)
- **Idle/Waiting**: Slow idle (1.5x slower, more relaxed)
- **Error State**: Agitated idle (faster, jittery movements)
- **Success**: Excited bounce (faster, more energetic)

## Implementation Recommendations

### File Organization
```
sprites/
├── base/
│   ├── parakeet_option1_idle_frame01.png
│   ├── parakeet_option1_idle_frame02.png
│   ├── parakeet_option1_idle_frame03.png
│   └── parakeet_option1_idle_frame04.png
├── animations/
│   ├── idle_classic.json         # Animation metadata
│   ├── idle_cute.json
│   └── idle_dynamic.json
└── palettes/
    ├── palette_classic.json
    ├── palette_blue.json
    └── palette_yellow.json
```

### Animation Metadata Format (JSON)
```json
{
  "name": "idle_classic",
  "sprite_base": "parakeet_option1",
  "frames": [
    {
      "file": "idle_frame01.png",
      "duration": 8,
      "offset": {"x": 0, "y": 0}
    },
    {
      "file": "idle_frame02.png",
      "duration": 8,
      "offset": {"x": 0, "y": -1}
    }
  ],
  "loop": true,
  "fps": 60,
  "totalDuration": 32
}
```

### CSS Implementation (for Web Dashboard)
```css
.parakeet-mascot {
  width: 64px;
  height: 64px;
  image-rendering: pixelated;
  image-rendering: crisp-edges;
  animation: parakeet-idle 0.8s steps(4) infinite;
}

@keyframes parakeet-idle {
  0% { background-position: 0px 0px; }
  25% { background-position: -64px 0px; }
  50% { background-position: -128px 0px; }
  75% { background-position: -192px 0px; }
}
```

### Python Implementation
```python
class ParakeetSprite:
    def __init__(self, animation_file, palette_file):
        self.frames = load_animation(animation_file)
        self.palette = load_palette(palette_file)
        self.current_frame = 0
        self.frame_counter = 0

    def update(self):
        """Call every game tick (60 FPS)"""
        self.frame_counter += 1
        if self.frame_counter >= self.frames[self.current_frame].duration:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def render(self, surface, position):
        frame_img = self.frames[self.current_frame].image
        # Apply palette swap
        colored_frame = apply_palette(frame_img, self.palette)
        surface.blit(colored_frame, position)
```

## Frame-by-Frame Creation Guide

### Tools Recommended
- **Aseprite**: Professional pixel art tool with animation timeline ($19.99)
- **LibreSprite**: Free open-source fork of Aseprite
- **Piskel**: Free online pixel art editor
- **GIMP**: Free, use "indexed color mode" for palette work

### Workflow
1. **Create Frame 1**: Start with base sprite (already done!)
2. **Duplicate Layer**: Create Frame 2 by duplicating Frame 1
3. **Make Subtle Changes**: Move pixels for breathing/movement
4. **Onion Skinning**: View previous frame as ghost overlay to ensure smooth motion
5. **Test Loop**: Play back frames to verify smooth looping
6. **Export**: Save each frame as separate PNG (indexed color mode)

### Quality Checklist
- [ ] Movement feels natural (not robotic)
- [ ] Loop is seamless (Frame 4 transitions smoothly to Frame 1)
- [ ] No pixel "crawling" or jitter
- [ ] Silhouette remains recognizable in all frames
- [ ] Color count stays within 16 colors per frame
- [ ] Outline thickness consistent (1-2 pixels)

## Performance Optimization

### For Web Dashboard
- Use sprite sheets instead of individual files
- Preload all animation frames on app start
- Consider using CSS animations for simple loops
- Canvas rendering for complex effects (palette swaps)

### For Desktop/Python
- Cache palette-swapped versions
- Load sprites asynchronously
- Use hardware acceleration when available
- Consider using pygame.sprite.Group for efficient updates

## Next Steps

1. **Choose Preferred Sprite**: Select Option 1, 2, or 3 as base
2. **Create Animation Frames**: Use tool of choice to create 4-6 frames
3. **Test Animation**: Import into animation tool and verify smooth loop
4. **Create Sprite Sheet**: Combine frames into single texture atlas
5. **Implement in App**: Add to dashboard with palette swap system

## References

- SNES Sprite Limitations: See `TECHNICAL_SPECS.md`
- Color Palette System: See `COLOR_PALETTE_SWAPPING.md`
- Original sprite generator: `generate_parakeet_sprites.py`
