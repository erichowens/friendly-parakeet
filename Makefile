# Friendly Parakeet Makefile
# Provides convenient commands for sound generation and other tasks

.PHONY: help sounds sounds-simple sounds-clap sounds-variants soften-sounds install-audio clean-sounds

help:
	@echo "Friendly Parakeet - Available Commands"
	@echo "======================================"
	@echo ""
	@echo "Sound Generation:"
	@echo "  make sounds         - Synthesize budgie sounds (recommended, works immediately)"
	@echo "  make sounds-synth   - Same as 'make sounds' (programmatic synthesis)"
	@echo "  make sounds-ai      - Generate with AudioGen AI (requires ML dependencies)"
	@echo "  make sounds-clap    - Generate with CLAP refinement (highest quality, requires ML)"
	@echo "  make sounds-variants - Generate 3 AI variants of each sound"
	@echo "  make soften-sounds  - Post-process existing sounds to make them softer"
	@echo ""
	@echo "Setup:"
	@echo "  make install-audio  - Install audio generation dependencies (for AI methods)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean-sounds   - Remove all generated sound files"
	@echo ""

# Install audio generation dependencies
install-audio:
	@echo "Installing audio generation dependencies..."
	@echo "Note: This requires ffmpeg to be installed via Homebrew"
	@echo "Run: brew install ffmpeg"
	@pip install -r requirements-audio.txt

# Generate budgie sounds (synthesis - recommended)
sounds: sounds-synth

sounds-synth:
	@echo "Synthesizing budgie sounds (programmatic approach)..."
	@python3 scripts/synthesize_budgie_sounds.py

# Generate budgie sounds with AI (requires heavy dependencies)
sounds-ai:
	@echo "Generating budgie sounds with AudioGen (AI approach)..."
	@echo "Note: Requires audiocraft, torch, and other ML dependencies"
	@python3 scripts/generate_budgie_sounds.py

# Generate budgie sounds with CLAP refinement (highest quality, most complex)
sounds-clap:
	@echo "Generating budgie sounds with CLAP refinement..."
	@echo "This will take 15-20 minutes but produces highest quality"
	@echo "Note: Requires audiocraft, msclap, torch, xformers, and other ML dependencies"
	@python3 scripts/generate_budgie_sounds.py --use-clap --candidates 10

# Generate multiple AI variants for comparison
sounds-variants:
	@echo "Generating 3 AI variants of each budgie sound..."
	@echo "Note: Requires audiocraft and other ML dependencies"
	@python3 scripts/generate_budgie_sounds.py --variants 3

# Post-process existing sounds to make them softer
soften-sounds:
	@echo "Softening sounds in assets/sounds/..."
	@python3 scripts/make_soft_budgie_sounds.py assets/sounds

# Clean all generated sounds
clean-sounds:
	@echo "Removing generated sound files..."
	@rm -f assets/sounds/*.mp3
	@echo "Sound files removed"
