"""Sound playback utilities for Friendly Parakeet."""

import subprocess
import platform
from pathlib import Path
from typing import Optional


class SoundPlayer:
    """Plays pleasant budgie-inspired notification sounds."""

    def __init__(self, enabled: bool = True):
        """Initialize the sound player.

        Args:
            enabled: Whether sound playback is enabled
        """
        self.enabled = enabled
        self.sounds_dir = self._find_sounds_directory()

    def _find_sounds_directory(self) -> Path:
        """Find the assets/sounds directory.

        Returns:
            Path to sounds directory
        """
        # Try relative to this file (development)
        sounds_dir = Path(__file__).parent.parent.parent / "assets" / "sounds"
        if sounds_dir.exists():
            return sounds_dir

        # Try relative to package installation
        import pkg_resources
        try:
            sounds_dir = Path(pkg_resources.resource_filename('parakeet', 'assets/sounds'))
            if sounds_dir.exists():
                return sounds_dir
        except Exception:
            pass

        # Fallback to home directory
        sounds_dir = Path.home() / ".parakeet" / "sounds"
        if sounds_dir.exists():
            return sounds_dir

        # Return development path as fallback
        return Path(__file__).parent.parent.parent / "assets" / "sounds"

    def play(self, sound_type: str) -> bool:
        """Play a notification sound.

        Args:
            sound_type: Type of sound to play. One of:
                - "hello": Friendly greeting (E-G-C rising triplet)
                - "alert": Gentle attention getter (A-C two-note)
                - "eureka": Excited discovery (G-C-E-C celebration)
                - "chirp": Quick interaction sound (single G5 note)
                - "happy": Success/completion (E-G-E-C bouncing melody)

        Returns:
            True if sound was played, False otherwise
        """
        if not self.enabled:
            return False

        sound_files = {
            "hello": "budgie_hello.mp3",
            "alert": "budgie_alert.mp3",
            "eureka": "budgie_eureka.mp3",
            "chirp": "budgie_chirp.mp3",
            "happy": "budgie_happy.mp3"
        }

        sound_file = sound_files.get(sound_type)
        if not sound_file:
            return False

        sound_path = self.sounds_dir / sound_file

        if not sound_path.exists():
            return False

        try:
            system = platform.system()

            if system == "Darwin":  # macOS
                # Use afplay (supports MP3)
                subprocess.Popen(
                    ["afplay", str(sound_path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                return True

            elif system == "Linux":
                # Try multiple Linux audio players
                players = ["paplay", "aplay", "mpg123", "ffplay"]
                for player in players:
                    try:
                        subprocess.Popen(
                            [player, str(sound_path)],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                        return True
                    except FileNotFoundError:
                        continue

            elif system == "Windows":
                # Windows Media Player
                import winsound
                winsound.PlaySound(str(sound_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
                return True

        except Exception:
            # Silently fail if sound can't be played
            pass

        return False

    def enable(self):
        """Enable sound playback."""
        self.enabled = True

    def disable(self):
        """Disable sound playback."""
        self.enabled = False

    def toggle(self) -> bool:
        """Toggle sound playback on/off.

        Returns:
            New enabled state
        """
        self.enabled = not self.enabled
        return self.enabled


# Global sound player instance
_sound_player: Optional[SoundPlayer] = None


def get_sound_player() -> SoundPlayer:
    """Get the global sound player instance.

    Returns:
        Global SoundPlayer instance
    """
    global _sound_player
    if _sound_player is None:
        _sound_player = SoundPlayer()
    return _sound_player


def play_sound(sound_type: str) -> bool:
    """Play a notification sound (convenience function).

    Args:
        sound_type: Type of sound to play

    Returns:
        True if sound was played, False otherwise
    """
    return get_sound_player().play(sound_type)
