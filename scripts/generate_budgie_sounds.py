#!/usr/bin/env python3
"""
Generate professional budgie/parakeet sounds using AudioGen (AudioCraft).

This script generates pleasant, non-annoying budgie-themed UI sounds with
intelligent post-processing to ensure they're soft, modern, and suitable
for a productivity app.

Optionally uses CLAP semantic refinement to select the best variant from
multiple candidates (higher quality but slower).

Requirements (macOS):
  brew install ffmpeg
  pip install -r requirements-audio.txt

Usage:
  python3 scripts/generate_budgie_sounds.py
  python3 scripts/generate_budgie_sounds.py --use-clap --candidates 10  # CLAP refinement
  python3 scripts/generate_budgie_sounds.py --variants 3  # Simple variants
"""

import os
import io
import sys
import argparse
import tempfile
from dataclasses import dataclass
from typing import Optional, Tuple
import torch
from audiocraft.models import AudioGen
import soundfile as sf
import numpy as np
import librosa
from pydub import AudioSegment, effects


@dataclass
class SoundSpec:
    """Specification for a budgie sound"""
    name: str
    prompt: str
    target_description: str  # For CLAP refinement
    duration_ms: int


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate professional budgie sounds using AudioGen"
    )
    parser.add_argument(
        '--output',
        default="assets/sounds",
        help="Output directory (default: assets/sounds)"
    )
    parser.add_argument(
        '--variants',
        type=int,
        default=1,
        help="Number of simple variants to generate per sound (default: 1, ignored if --use-clap)"
    )
    parser.add_argument(
        '--use-clap',
        action='store_true',
        help="Use CLAP semantic refinement for higher quality (slower)"
    )
    parser.add_argument(
        '--candidates',
        type=int,
        default=10,
        help="Number of candidates for CLAP refinement (default: 10, only used with --use-clap)"
    )
    parser.add_argument(
        '--device',
        type=str,
        default=None,
        choices=['cpu', 'cuda', 'mps'],
        help="Device to run models on (default: auto-detect)"
    )
    return parser.parse_args()


# Sound definitions with carefully crafted prompts
# These prompts are designed to create pleasant, soft, budgie-like sounds
SOUND_SPECS = [
    SoundSpec(
        name="budgie_hello",
        prompt=(
            "soft friendly budgie chirp greeting, warm welcoming tone, gentle parakeet vocalization, "
            "melodic rising pitch, 250 ms, pleasant bird sound, no harsh transients, natural avian quality, "
            "cheerful but subtle, no distortion, no reverb, clean recording"
        ),
        target_description="friendly welcoming budgie greeting chirp, warm and gentle parakeet hello",
        duration_ms=250
    ),
    SoundSpec(
        name="budgie_alert",
        prompt=(
            "gentle budgie alert chirp, soft parakeet notification sound, melodic attention call, "
            "warm bird vocalization, 200 ms, pleasant and non-intrusive, natural avian tone, "
            "clear but gentle, no harsh sounds, no distortion, modern UI quality"
        ),
        target_description="gentle budgie notification sound, soft alert chirp, non-intrusive parakeet call",
        duration_ms=200
    ),
    SoundSpec(
        name="budgie_eureka",
        prompt=(
            "excited happy budgie discovery chirp, joyful parakeet trill, enthusiastic bird celebration, "
            "melodic ascending vocalization, 300 ms, warm and pleasant, natural avian excitement, "
            "delightful bird sound, no harsh transients, clean recording, uplifting tone"
        ),
        target_description="excited happy budgie discovery sound, joyful parakeet celebration, enthusiastic bird trill",
        duration_ms=300
    ),
    SoundSpec(
        name="budgie_chirp",
        prompt=(
            "soft budgie chirp, gentle parakeet vocalization, natural bird sound, warm friendly tone, "
            "150 ms, pleasant interaction sound, subtle avian quality, melodic and soft, "
            "no harsh edges, no distortion, clean modern recording"
        ),
        target_description="soft budgie chirp, gentle parakeet interaction sound",
        duration_ms=150
    ),
    SoundSpec(
        name="budgie_happy",
        prompt=(
            "cheerful budgie success chirp, happy parakeet vocalization, melodic celebration sound, "
            "warm bird trill, 220 ms, pleasant completion tone, natural avian quality, "
            "gentle and uplifting, no harsh transients, clean recording, joyful but subtle"
        ),
        target_description="cheerful budgie success sound, happy parakeet celebration chirp",
        duration_ms=220
    ),
]


def refine_with_clap(
    candidates: torch.Tensor,
    target_description: str,
    sample_rate: int
) -> Tuple[torch.Tensor, float]:
    """
    Use CLAP to select the best candidate from multiple generated sounds.

    Args:
        candidates: Tensor of shape (n_candidates, channels, samples)
        target_description: Text description for semantic matching
        sample_rate: Sample rate of the audio

    Returns:
        (best_audio, best_score)
    """
    try:
        from msclap import CLAP
    except ImportError:
        print("Warning: msclap not installed. Install with: pip install msclap")
        print("Falling back to random selection...")
        return candidates[0], 0.0

    print(f"  Computing CLAP embeddings for {len(candidates)} candidates...")

    # Load CLAP model
    clap = CLAP(version='2023', use_cuda=torch.cuda.is_available())

    # Convert to numpy for CLAP
    candidates_np = candidates.cpu().numpy()

    # Reshape to (n_candidates, samples) - CLAP expects mono
    if candidates_np.shape[1] == 1:
        candidates_np = candidates_np.squeeze(1)

    # CLAP API requires file paths, so save candidates as temp files
    temp_files = []
    try:
        for i, candidate in enumerate(candidates_np):
            # CLAP expects 48kHz
            candidate_resampled = librosa.resample(
                candidate,
                orig_sr=sample_rate,
                target_sr=48000
            )
            # Save to temp file
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_files.append(temp_file.name)
            temp_file.close()
            sf.write(temp_file.name, candidate_resampled, 48000)

        # Get audio embeddings from temp files
        audio_embeds = clap.get_audio_embeddings(temp_files, resample=False)

        # Get target text embedding
        target_embed = clap.get_text_embeddings([target_description])

        # Compute similarities
        similarities = clap.compute_similarity(audio_embeds, target_embed)
        scores = similarities[:, 0].detach().cpu().numpy()

        best_idx = scores.argmax()
        best_score = scores[best_idx]

        print(f"  CLAP Results: Best = #{best_idx} (score: {best_score:.3f})")
        print(f"  Score range: [{scores.min():.3f}, {scores.max():.3f}]")

        return candidates[best_idx], best_score

    finally:
        # Clean up temp files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass


def postprocess_budgie_sound(
    snd: AudioSegment,
    target_ms: int,
    fade_in_ms: int = 5,
    fade_out_ms: int = 40
) -> AudioSegment:
    """
    Post-process generated audio to create a soft, modern budgie sound.

    Steps:
    1. Convert to mono 48kHz for consistency
    2. Trim to target duration
    3. Soften high frequencies (budgie chirps can be sharp)
    4. Apply gentle fades
    5. Normalize and reduce volume for softness
    """
    # Convert to mono 48kHz
    s = snd.set_channels(1).set_frame_rate(48000)

    # Trim to reasonable maximum if too long
    if len(s) > 500:
        s = s[:500]

    # Trim to target duration
    s = s[:target_ms]

    # Soften high frequencies by blending with a low-passed version
    # This prevents harsh, sharp budgie sounds
    lowpassed = s.low_pass_filter(6000)  # Lower cutoff for softer bird sounds
    s = s.overlay(lowpassed - 3)

    # Apply fades (fade-out capped to clip length)
    fade_out_ms = min(fade_out_ms, max(15, int(len(s) * 0.4)))
    s = s.fade_in(fade_in_ms).fade_out(fade_out_ms)

    # Normalize to -1 dBFS peak, then reduce overall gain by 8 dB for softness
    # Budgie sounds need to be especially non-intrusive
    s = effects.normalize(s, headroom=1.0)
    s = s - 8

    return s


def generate_sounds_simple(output_dir: str, variants: int, device: Optional[str]):
    """Generate budgie sounds with simple AudioGen (no CLAP refinement)."""
    os.makedirs(output_dir, exist_ok=True)

    # Detect device
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

    print(f"Using device: {device}")
    print("Loading AudioGen model (this may take 30-60 seconds on first run)...")
    print("The model is ~1.5GB and will be cached for future use.")
    model = AudioGen.get_pretrained('facebook/audiogen-medium')

    # Configure generation parameters for high-quality, varied output
    model.set_generation_params(
        duration=0.8,  # Generate slightly longer, then trim
        top_k=250,     # Sampling diversity
        top_p=0.98,    # Nucleus sampling
    )
    print("Model loaded successfully!\n")

    # Generate each sound
    for spec in SOUND_SPECS:
        print(f"\nGenerating {spec.name}...")

        for variant_num in range(1, variants + 1):
            try:
                # Generate audio from prompt
                wav = model.generate([spec.prompt])[0].cpu()  # tensor [channels, samples]

                # Convert tensor to AudioSegment
                buf = io.BytesIO()
                sf.write(
                    buf,
                    wav.numpy().T,
                    model.sample_rate,
                    format='WAV',
                    subtype='FLOAT'
                )
                buf.seek(0)
                seg = AudioSegment.from_file(buf, format='wav')

                # Post-process for soft, pleasant sound
                seg = postprocess_budgie_sound(seg, spec.duration_ms)

                # Determine output filename
                if variants > 1:
                    out_filename = f"{spec.name}.v{variant_num}.mp3"
                else:
                    out_filename = f"{spec.name}.mp3"

                out_path = os.path.join(output_dir, out_filename)

                # Export as high-quality MP3
                seg.export(out_path, format="mp3", bitrate="192k")
                print(f"  ✓ Created: {out_filename}")

            except Exception as e:
                print(f"  ✗ Error generating {spec.name} variant {variant_num}: {e}")
                continue

    print(f"\n{'='*60}")
    print("Sound generation complete!")
    print(f"{'='*60}")
    print(f"Files saved to: {output_dir}")
    print(f"{'='*60}\n")


def generate_sounds_with_clap(output_dir: str, n_candidates: int, device: Optional[str]):
    """Generate budgie sounds using CLAP semantic refinement (highest quality)."""
    os.makedirs(output_dir, exist_ok=True)

    # Detect device
    if device is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'

    print(f"Using device: {device}")
    print("Loading AudioGen model (this may take 30-60 seconds on first run)...")
    print("The model is ~1.5GB and will be cached for future use.")
    model = AudioGen.get_pretrained('facebook/audiogen-medium')

    # Configure generation parameters
    model.set_generation_params(
        duration=0.8,
        top_k=250,
        top_p=0.98,
        use_sampling=True
    )
    print("Model loaded successfully!\n")
    print(f"Generating {n_candidates} candidates per sound for CLAP refinement...")
    print(f"This will take approximately {len(SOUND_SPECS) * 2} minutes.\n")

    # Generate each sound
    for i, spec in enumerate(SOUND_SPECS, 1):
        print(f"\n[{i}/{len(SOUND_SPECS)}] {'='*50}")
        print(f"Generating: {spec.name}")
        print(f"{'='*60}")

        try:
            # Stage 1: Generate multiple candidates
            prompts = [spec.prompt] * n_candidates
            print(f"  Generating {n_candidates} candidates...")
            with torch.no_grad():
                candidates = model.generate(prompts)
            print(f"  ✓ Generated {n_candidates} candidates")

            # Stage 2: CLAP refinement
            best_audio, clap_score = refine_with_clap(
                candidates,
                spec.target_description,
                model.sample_rate
            )

            # Stage 3: Post-process
            print(f"  Post-processing...")
            buf = io.BytesIO()
            sf.write(
                buf,
                best_audio.cpu().numpy().T,
                model.sample_rate,
                format='WAV',
                subtype='FLOAT'
            )
            buf.seek(0)
            seg = AudioSegment.from_file(buf, format='wav')
            seg = postprocess_budgie_sound(seg, spec.duration_ms)

            # Save
            out_path = os.path.join(output_dir, f"{spec.name}.mp3")
            seg.export(out_path, format="mp3", bitrate="192k")

            file_size = os.path.getsize(out_path) / 1024
            print(f"\n  ✓ SUCCESS: {spec.name}.mp3")
            print(f"    CLAP score: {clap_score:.3f}")
            print(f"    File size: {file_size:.1f} KB")

        except Exception as e:
            print(f"\n  ✗ ERROR: {spec.name}")
            print(f"    {e}")
            continue

    print(f"\n{'='*60}")
    print("GENERATION COMPLETE")
    print(f"{'='*60}")
    print(f"Files saved to: {output_dir}")
    print(f"{'='*60}\n")


def main():
    args = parse_args()

    print("\n" + "="*60)
    print("Friendly Parakeet Budgie Sound Generator")
    print("="*60 + "\n")

    if args.use_clap:
        print("Mode: CLAP Semantic Refinement (highest quality)")
        print(f"Candidates per sound: {args.candidates}")
        generate_sounds_with_clap(args.output, args.candidates, args.device)
    else:
        print("Mode: Simple AudioGen (faster)")
        print(f"Variants per sound: {args.variants}")
        generate_sounds_simple(args.output, args.variants, args.device)

    print("\nNext steps:")
    print("1. Listen to the generated sounds in assets/sounds/")
    print("2. Test them in your app")
    print("3. Adjust prompts in this script if needed")


if __name__ == "__main__":
    main()
