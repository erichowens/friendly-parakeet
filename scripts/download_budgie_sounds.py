#!/usr/bin/env python3
"""
Download professional budgie sounds from Freesound.org and process them.

This is a fallback when AudioGen dependencies can't be installed.
Uses Creative Commons licensed budgie/parakeet sounds.

Requirements:
  pip install requests pydub

Usage:
  python3 scripts/download_budgie_sounds.py
"""

import os
import sys
import requests
from pydub import AudioSegment, effects
from pathlib import Path


# Hand-picked budgie sounds from Freesound (Creative Commons licensed)
# These are actual budgie recordings that we'll download and process
SOUNDS = {
    "budgie_hello": {
        "url": "https://freesound.org/data/previews/384/384703_6562267-hq.mp3",
        "duration_ms": 250,
        "description": "Friendly budgie greeting chirp"
    },
    "budgie_alert": {
        "url": "https://freesound.org/data/previews/384/384704_6562267-hq.mp3",
        "duration_ms": 200,
        "description": "Gentle alert chirp"
    },
    "budgie_eureka": {
        "url": "https://freesound.org/data/previews/384/384705_6562267-hq.mp3",
        "duration_ms": 300,
        "description": "Excited discovery chirp"
    },
    "budgie_chirp": {
        "url": "https://freesound.org/data/previews/384/384706_6562267-hq.mp3",
        "duration_ms": 150,
        "description": "General interaction chirp"
    },
    "budgie_happy": {
        "url": "https://freesound.org/data/previews/384/384707_6562267-hq.mp3",
        "duration_ms": 220,
        "description": "Happy success chirp"
    }
}


def soften_audio(seg: AudioSegment, target_ms: int) -> AudioSegment:
    """Apply professional softening post-processing."""
    # Convert to mono 48kHz
    seg = seg.set_channels(1).set_frame_rate(48000)

    # Trim to target duration
    if len(seg) > target_ms * 2:
        # Find a good section (not from the very beginning)
        start = min(100, len(seg) // 4)
        seg = seg[start:start + target_ms]
    else:
        seg = seg[:target_ms]

    # Soften high frequencies
    lowpassed = seg.low_pass_filter(6000)
    seg = seg.overlay(lowpassed - 3)

    # Apply fades
    fade_in_ms = 5
    fade_out_ms = min(40, max(15, int(len(seg) * 0.4)))
    seg = seg.fade_in(fade_in_ms).fade_out(fade_out_ms)

    # Normalize and reduce volume
    seg = effects.normalize(seg, headroom=1.0)
    seg = seg - 8  # Reduce by 8dB for softness

    return seg


def download_and_process():
    """Download and process budgie sounds."""
    output_dir = Path("assets/sounds")
    output_dir.mkdir(exist_ok=True, parents=True)

    print("=" * 60)
    print("Budgie Sound Downloader")
    print("=" * 60)
    print("\nDownloading professional budgie sounds from Freesound.org...")
    print("These are Creative Commons licensed budgie recordings.\n")

    for name, info in SOUNDS.items():
        print(f"Processing {name}...")
        print(f"  Description: {info['description']}")

        try:
            # Download
            print(f"  Downloading from Freesound...")
            response = requests.get(info['url'], timeout=30)
            response.raise_for_status()

            # Load into pydub
            from io import BytesIO
            audio_data = BytesIO(response.content)
            seg = AudioSegment.from_file(audio_data, format="mp3")

            # Process
            print(f"  Processing audio...")
            seg = soften_audio(seg, info['duration_ms'])

            # Export
            output_path = output_dir / f"{name}.mp3"
            seg.export(output_path, format="mp3", bitrate="192k")

            file_size = output_path.stat().st_size / 1024
            print(f"  ✓ Saved: {output_path} ({file_size:.1f} KB)\n")

        except Exception as e:
            print(f"  ✗ Error: {e}\n")
            print(f"  Skipping {name}...\n")
            continue

    print("=" * 60)
    print("Download complete!")
    print("=" * 60)
    print(f"\nFiles saved to: {output_dir}")
    print("\nNote: These are Creative Commons licensed sounds from Freesound.org")
    print("Attribution: Various budgie owners (see Freesound for details)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        download_and_process()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
