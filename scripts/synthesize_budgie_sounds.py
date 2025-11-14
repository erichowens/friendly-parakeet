#!/usr/bin/env python3
"""
Synthesize pleasant UI notification sounds for Friendly Parakeet.

Based on comprehensive research of professional UI sound design, these sounds use:
- Marimba/kalimba-inspired tones in the 600-1,800 Hz "sweet spot"
- Soft attacks (10ms) to avoid startle response
- Short durations (180-220ms) for non-intrusiveness
- "Parakeet-inspired" character through quick rhythms and upward pitch

Research shows actual budgie chirps (4,200-5,300 Hz) are in the "fire alarm"
range that causes annoyance. Professional apps use 700-2,000 Hz instead.

Requirements:
  pip install pydub numpy

Usage:
  python3 scripts/synthesize_budgie_sounds.py
"""

import os
import sys
import numpy as np
from pydub import AudioSegment, effects
from pydub.generators import Sine
from pathlib import Path


def create_marimba_tone(
    freq: float,
    duration_ms: int,
    attack_ms: int = 10,
    sample_rate: int = 48000
) -> AudioSegment:
    """
    Create a marimba-like tone with natural decay.

    Marimba characteristics:
    - Warm fundamental with controlled harmonics
    - Quick soft attack, exponential decay
    - Frequency range: 250-2,000 Hz (we use 600-1,800 Hz)
    """
    duration_s = duration_ms / 1000
    samples = int(sample_rate * duration_s)
    t = np.linspace(0, duration_s, samples)

    # Fundamental frequency
    fundamental = np.sin(2 * np.pi * freq * t)

    # Add harmonics (quieter than fundamental)
    harmonic_2 = np.sin(2 * np.pi * freq * 2 * t) * 0.3  # Octave
    harmonic_3 = np.sin(2 * np.pi * freq * 3 * t) * 0.15  # Fifth
    harmonic_5 = np.sin(2 * np.pi * freq * 5 * t) * 0.08  # Third

    # Mix harmonics
    waveform = fundamental + harmonic_2 + harmonic_3 + harmonic_5

    # Marimba envelope: soft attack, exponential decay
    attack_samples = int(sample_rate * attack_ms / 1000)
    attack_env = np.linspace(0, 1, attack_samples)

    decay_samples = samples - attack_samples
    # Exponential decay: -24dB in 150ms
    decay_rate = 8  # Controls how fast it decays
    decay_env = np.exp(-decay_rate * np.linspace(0, 1, decay_samples))

    envelope = np.concatenate([attack_env, decay_env])[:samples]
    waveform = waveform * envelope

    # Normalize and set comfortable level
    if np.abs(waveform).max() > 0:
        waveform = waveform / np.abs(waveform).max() * 0.4

    # Convert to 16-bit PCM
    waveform = np.int16(waveform * 32767)

    seg = AudioSegment(
        waveform.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )

    return seg


def create_kalimba_tone(
    freq: float,
    duration_ms: int,
    attack_ms: int = 8,
    sample_rate: int = 48000
) -> AudioSegment:
    """
    Create a kalimba-like tone (thumb piano).

    Kalimba characteristics:
    - Very pure fundamental with subtle harmonics
    - Gentle attack, sustained decay
    - Frequency range: 400-1,800 Hz
    - Known for "perfect frequency balance"
    """
    duration_s = duration_ms / 1000
    samples = int(sample_rate * duration_s)
    t = np.linspace(0, duration_s, samples)

    # Kalimba is purer than marimba - more fundamental, less harmonics
    fundamental = np.sin(2 * np.pi * freq * t)
    harmonic_2 = np.sin(2 * np.pi * freq * 2 * t) * 0.2
    harmonic_3 = np.sin(2 * np.pi * freq * 3 * t) * 0.1

    waveform = fundamental + harmonic_2 + harmonic_3

    # Kalimba envelope: very soft attack, gentle sustained decay
    attack_samples = int(sample_rate * attack_ms / 1000)
    attack_env = np.linspace(0, 1, attack_samples) ** 2  # Squared for softer curve

    decay_samples = samples - attack_samples
    # Gentler decay than marimba
    decay_rate = 5
    decay_env = np.exp(-decay_rate * np.linspace(0, 1, decay_samples))

    envelope = np.concatenate([attack_env, decay_env])[:samples]
    waveform = waveform * envelope

    # Normalize
    if np.abs(waveform).max() > 0:
        waveform = waveform / np.abs(waveform).max() * 0.35

    # Convert to 16-bit PCM
    waveform = np.int16(waveform * 32767)

    seg = AudioSegment(
        waveform.tobytes(),
        frame_rate=sample_rate,
        sample_width=2,
        channels=1
    )

    return seg


def create_triplet_melody(
    notes: list,
    note_duration_ms: int,
    instrument: str = "marimba",
    sample_rate: int = 48000
) -> AudioSegment:
    """
    Create a quick melody with multiple notes.

    This gives the "chirpy" parakeet-inspired character without
    using actual high-pitched bird frequencies.

    Args:
        notes: List of (frequency, duration_ms) tuples
        instrument: "marimba" or "kalimba"
    """
    result = AudioSegment.silent(duration=0)

    for freq, duration in notes:
        if instrument == "kalimba":
            note = create_kalimba_tone(freq, duration)
        else:
            note = create_marimba_tone(freq, duration)

        result = result + note

    return result


def soften_audio(seg: AudioSegment) -> AudioSegment:
    """Apply professional softening post-processing."""
    # Low-pass filter at 4000 Hz to remove harsh highs
    # (Research shows anything above 3000 Hz is in sensitive range)
    lowpassed = seg.low_pass_filter(4000)
    seg = seg.overlay(lowpassed - 2)

    # Very gentle fade out (already have soft attack from synthesis)
    fade_out_ms = min(30, max(10, int(len(seg) * 0.3)))
    seg = seg.fade_out(fade_out_ms)

    # Normalize and reduce volume for comfortable playback
    seg = effects.normalize(seg, headroom=1.0)
    seg = seg - 6  # Reduce by 6dB

    return seg


def generate_budgie_sounds():
    """Generate all parakeet-inspired notification sounds."""
    output_dir = Path("assets/sounds")
    output_dir.mkdir(exist_ok=True, parents=True)

    print("=" * 60)
    print("Synthesizing Parakeet-Inspired UI Sounds")
    print("=" * 60)
    print("\nBased on professional UI sound design research:")
    print("  • Frequency range: 600-1,800 Hz (marimba/kalimba)")
    print("  • Soft attacks: 8-10ms (non-jarring)")
    print("  • Short duration: 180-220ms (non-intrusive)")
    print("  • Warm, pleasant tones in human hearing sweet spot\n")

    # Note frequencies in Hz (using musical notes for reference)
    # C5 = 523, D5 = 587, E5 = 659, F5 = 698, G5 = 784, A5 = 880
    # C6 = 1047, D6 = 1175, E6 = 1319

    sounds = {
        "budgie_hello": {
            "generator": lambda: create_triplet_melody([
                (659, 60),   # E5 - Hello
                (784, 60),   # G5 - there
                (1047, 80),  # C6 - friend! (slightly longer, higher = cheerful)
            ], 60, "kalimba"),
            "description": "Friendly rising triplet (kalimba, E-G-C)"
        },

        "budgie_alert": {
            "generator": lambda: create_triplet_melody([
                (880, 70),   # A5 - Attention
                (1047, 70),  # C6 - please (gentle alert)
            ], 70, "marimba"),
            "description": "Gentle two-note alert (marimba, A-C)"
        },

        "budgie_eureka": {
            "generator": lambda: create_triplet_melody([
                (784, 50),   # G5 - I've
                (1047, 50),  # C6 - got
                (1319, 60),  # E6 - an
                (1047, 70),  # C6 - idea! (back down, resolved)
            ], 50, "kalimba"),
            "description": "Excited four-note celebration (kalimba, G-C-E-C)"
        },

        "budgie_chirp": {
            "generator": lambda: create_kalimba_tone(784, 150, attack_ms=8),
            "description": "Quick single note (kalimba, G5)"
        },

        "budgie_happy": {
            "generator": lambda: create_triplet_melody([
                (659, 55),   # E5 - Success
                (784, 55),   # G5 - achieved
                (659, 55),   # E5 - feeling
                (1047, 75),  # C6 - good! (resolved higher)
            ], 55, "marimba"),
            "description": "Bouncing happy melody (marimba, E-G-E-C)"
        }
    }

    for name, info in sounds.items():
        print(f"Creating {name}...")
        print(f"  {info['description']}")

        try:
            # Generate sound
            seg = info['generator']()

            # Apply post-processing
            seg = soften_audio(seg)

            # Export
            output_path = output_dir / f"{name}.mp3"
            seg.export(output_path, format="mp3", bitrate="192k")

            file_size = output_path.stat().st_size / 1024
            duration = len(seg)
            print(f"  ✓ Created: {output_path}")
            print(f"    Duration: {duration}ms, Size: {file_size:.1f} KB\n")

        except Exception as e:
            print(f"  ✗ Error: {e}\n")
            import traceback
            traceback.print_exc()
            continue

    print("=" * 60)
    print("Synthesis complete!")
    print("=" * 60)
    print(f"\nFiles saved to: {output_dir}")
    print("\nThese sounds are 'parakeet-INSPIRED' not actual parakeets:")
    print("  • Warm marimba/kalimba tones (600-1,800 Hz)")
    print("  • Quick melodic patterns for 'chirpy' character")
    print("  • Professional UI sound design standards")
    print("  • Pleasant, non-annoying for repeated use")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        generate_budgie_sounds()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
