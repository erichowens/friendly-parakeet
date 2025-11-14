# Friendly Parakeet Sound Files

Professional budgie/parakeet sounds for the Friendly Parakeet app.

## Sound Files (✓ Generated)

The following sound files exist in this directory:

- ✓ `budgie_hello.mp3` - Played when the app starts (250ms, friendly rising chirp)
- ✓ `budgie_alert.mp3` - Played for important notifications (200ms, gentle alert tone)
- ✓ `budgie_eureka.mp3` - Played when Brilliant Budgie has a new idea (300ms, excited trill)
- ✓ `budgie_chirp.mp3` - General chirp sound for interactions (150ms, quick chirp)
- ✓ `budgie_happy.mp3` - Success/completion sound (220ms, double chirp celebration)

## How Sounds Were Generated

### Current Method: Marimba/Kalimba Synthesis (Working!)

The sounds were created using **synthesize_budgie_sounds.py**, which generates pleasant "parakeet-INSPIRED" UI notification sounds using:
- Marimba and kalimba synthesis in the 600-1,800 Hz range
- Musical notes: E5 (659 Hz), G5 (784 Hz), A5 (880 Hz), C6 (1047 Hz), E6 (1319 Hz)
- Soft attacks (8-10ms) to avoid startle response
- Natural exponential decay envelopes
- Professional post-processing (4kHz low-pass filter, -6dB volume reduction)

**Why not actual budgie sounds?**
Research shows that natural budgie chirps peak at 4,200-5,300 Hz, which falls in the 3,000-8,000 Hz "fire alarm" range that causes human annoyance. Professional apps (Apple, Linear, Notion) use warm mid-range frequencies (700-2,000 Hz) instead.

**To regenerate:**
```bash
python3 scripts/synthesize_budgie_sounds.py
```

or

```bash
make sounds
```

**Advantages:**
- ✓ Works immediately, no complex dependencies
- ✓ Warm, pleasant tones in the human hearing "sweet spot"
- ✓ Research-based professional UI sound design
- ✓ Small file sizes (~4-7 KB each)
- ✓ "Parakeet-inspired" character through melody patterns, not harsh frequencies

### Alternative Method: AI Generation (Advanced)

For highest quality, you can use Meta's AudioGen with CLAP semantic refinement:

```bash
# Requires: brew install ffmpeg && pip install -r requirements-audio.txt
python3 scripts/generate_budgie_sounds.py --use-clap --candidates 10
```

**Note:** This requires heavy ML dependencies (torch, audiocraft, xformers) which can be difficult to install on some systems. The synthesis approach produces excellent results and is recommended for most users.

## Audio Specifications

All sounds meet these specs:

- **Format:** MP3
- **Bitrate:** 192 kbps
- **Sample Rate:** 48,000 Hz
- **Channels:** Mono
- **Duration:** 150-300ms depending on sound
- **Volume:** Normalized to -1dBFS peak, then reduced by 8dB
- **Processing:** Low-pass filtered at 6kHz, gentle fades (5ms in, 40ms out)

## Post-Processing Existing Sounds

If you have other sounds you want to make softer:

```bash
# Soften all sounds in assets/sounds/
python3 scripts/make_soft_budgie_sounds.py assets/sounds

# Adjust softness (higher = softer)
python3 scripts/make_soft_budgie_sounds.py assets/sounds --strength 10
```

## Why This Approach?

This is a **massive improvement** over random beeps and macOS `say` command:

1. **Professional Quality:** Carefully designed bird-like chirps
2. **Non-Intrusive:** Tuned to be pleasant, not annoying
3. **Consistent:** All sounds have matching characteristics
4. **Reliable:** Works on all systems without complex dependencies
5. **Customizable:** Easy to adjust frequencies and durations

## Technical Details

### Synthesis Pipeline

1. **Marimba Tone Generation**
   - Fundamental frequency + harmonics (2nd at 0.3, 3rd at 0.15, 5th at 0.08)
   - Soft attack envelope (10ms), exponential decay (decay_rate=8)
   - Frequency range: 600-1,800 Hz (professional UI sweet spot)
   - Normalized to 0.4 amplitude for comfortable listening

2. **Kalimba Tone Generation**
   - Purer tone than marimba - less harmonics (2nd at 0.2, 3rd at 0.1)
   - Very soft attack (8ms, squared curve), gentler decay (decay_rate=5)
   - Known for "perfect frequency balance"
   - Normalized to 0.35 amplitude

3. **Compound Melodies**
   - Multiple notes concatenated for "chirpy" parakeet-inspired character
   - Quick rhythmic patterns (50-80ms per note)
   - Rising sequences for friendly/excited tones
   - Different instruments for tonal variety

4. **Post-Processing**
   - Low-pass filter at 4kHz (removes sensitive high frequencies)
   - Gentle fade out (30ms)
   - Normalize to -1dBFS, reduce by 6dB
   - Export as 192kbps MP3

## Customization

Edit `scripts/synthesize_budgie_sounds.py` to adjust:

```python
# Marimba/kalimba frequencies and durations
"budgie_hello": create_triplet_melody([
    (659, 60),   # E5
    (784, 60),   # G5
    (1047, 80),  # C6
], 60, "kalimba")

# Adjust instrument characteristics
create_marimba_tone(freq=784, duration_ms=150, attack_ms=10)
create_kalimba_tone(freq=1047, duration_ms=200, attack_ms=8)

# Modify decay rates for different sustain characteristics
decay_rate = 8  # Higher = faster decay (marimba: 8, kalimba: 5)
```

## References

This implementation is based on comprehensive UI sound design research:
- **Research findings**: Natural budgie chirps (4,200-5,300 Hz) are in the "fire alarm" annoyance range
- **Professional standard**: Apps use 700-2,000 Hz (marimba/kalimba sounds)
- **Inspiration**: Apple notification sounds, Linear app, Notion
- **Technical reference**: `~/coding/audiogen-sfx-generator`, `~/coding/semantic_sounds`
- **Full research**: See `UI_NOTIFICATION_SOUND_RESEARCH.md` in project root
