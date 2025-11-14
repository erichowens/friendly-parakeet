#!/usr/bin/env python3
"""
Post-process existing audio files to make them softer and more pleasant.

This script applies the same post-processing as generate_budgie_sounds.py
but to existing audio files. Useful for:
- Softening third-party sounds you've downloaded
- Re-processing sounds with different settings
- Batch processing a directory of sounds

Requirements:
  brew install ffmpeg
  pip install pydub ffmpeg-python

Usage:
  python3 scripts/make_soft_budgie_sounds.py assets/sounds
  python3 scripts/make_soft_budgie_sounds.py path/to/sounds --strength 6
"""

import os
import sys
import argparse
from glob import glob
from pydub import AudioSegment, effects


def parse_args():
    parser = argparse.ArgumentParser(
        description="Post-process audio files to make them soft and pleasant"
    )
    parser.add_argument(
        'input_dir',
        help="Directory containing audio files to process"
    )
    parser.add_argument(
        '--strength',
        type=int,
        default=8,
        help="Softness reduction in dB (default: 8, higher = softer)"
    )
    parser.add_argument(
        '--lowpass-freq',
        type=int,
        default=6000,
        help="Low-pass filter frequency in Hz (default: 6000)"
    )
    return parser.parse_args()


def soften_audio(
    seg: AudioSegment,
    reduction_db: int = 8,
    lowpass_freq: int = 6000
) -> AudioSegment:
    """
    Apply softening post-processing to make audio pleasant and non-intrusive.

    Steps:
    1. Convert to mono 48kHz
    2. Soften high frequencies
    3. Apply gentle fades
    4. Normalize and reduce volume
    """
    # Convert to mono 48kHz
    seg = seg.set_channels(1).set_frame_rate(48000)

    # Soften high frequencies by blending with a low-passed version
    lowpassed = seg.low_pass_filter(lowpass_freq)
    seg = seg.overlay(lowpassed - 3)

    # Apply fades: quick in, short out
    fade_in_ms = 3
    fade_out_ms = min(40, max(10, int(len(seg) * 0.4)))
    seg = seg.fade_in(fade_in_ms).fade_out(fade_out_ms)

    # Normalize then lower by specified dB for softness
    seg = effects.normalize(seg, headroom=1.0)
    seg = seg - reduction_db

    return seg


def main():
    args = parse_args()

    SFX_DIR = os.path.abspath(args.input_dir)
    EXTS = (".mp3", ".wav", ".ogg", ".flac", ".m4a")

    if not os.path.isdir(SFX_DIR):
        print(f"Error: Directory not found: {SFX_DIR}")
        sys.exit(1)

    files = [
        p for p in glob(os.path.join(SFX_DIR, "*"))
        if os.path.splitext(p)[1].lower() in EXTS
    ]

    if not files:
        print(f"No audio files found in {SFX_DIR}")
        print(f"Supported formats: {', '.join(EXTS)}")
        sys.exit(0)

    print(f"\n{'='*60}")
    print("Budgie Sound Softener")
    print(f"{'='*60}")
    print(f"Processing {len(files)} files in {SFX_DIR}")
    print(f"Softness reduction: {args.strength} dB")
    print(f"Low-pass filter: {args.lowpass_freq} Hz")
    print(f"{'='*60}\n")

    success_count = 0
    for path in files:
        filename = os.path.basename(path)
        try:
            # Load audio
            seg = AudioSegment.from_file(path)

            # Apply softening
            seg = soften_audio(
                seg,
                reduction_db=args.strength,
                lowpass_freq=args.lowpass_freq
            )

            # Export in-place using original format
            ext = os.path.splitext(path)[1].lower()
            fmt = {
                ".mp3": "mp3",
                ".wav": "wav",
                ".ogg": "ogg",
                ".flac": "flac",
                ".m4a": "mp4"
            }.get(ext, "mp3")

            export_kwargs = {"format": fmt}
            if fmt == "mp3":
                export_kwargs["bitrate"] = "192k"

            seg.export(path, **export_kwargs)
            print(f"  ✓ Softened: {filename}")
            success_count += 1

        except Exception as e:
            print(f"  ✗ Error processing {filename}: {e}")

    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"Successfully processed {success_count}/{len(files)} files")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
