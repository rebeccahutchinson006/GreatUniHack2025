"""
Audio playback module for playing generated TTS audio.
"""
import os
import platform
import subprocess
from typing import Optional
from pathlib import Path
from .exceptions import TranslationError


class AudioPlaybackError(TranslationError):
    """Base exception for audio playback errors"""
    pass


class AudioPlayer:
    """
    Cross-platform audio player for TTS-generated audio files.
    Supports MP3 playback on Windows, macOS, and Linux.
    """
    
    def __init__(self):
        """Initialize the audio player with platform detection."""
        self.system = platform.system()
        self._check_dependencies()
    
    def _check_dependencies(self):
        """
        Check if required audio playback tools are available.
        """
        if self.system == "Linux":
            # Check for common Linux audio players
            players = ['mpg123', 'ffplay', 'mpv', 'vlc']
            self.player = None
            for player in players:
                if self._command_exists(player):
                    self.player = player
                    break
            if not self.player:
                raise AudioPlaybackError(
                    "No audio player found. Please install one of: mpg123, ffplay, mpv, or vlc"
                )
        elif self.system == "Darwin":  # macOS
            self.player = "afplay"
        elif self.system == "Windows":
            self.player = "powershell"
        else:
            raise AudioPlaybackError(f"Unsupported operating system: {self.system}")
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH."""
        try:
            subprocess.run(
                ['which', command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def play(self, audio_path: str, blocking: bool = True) -> Optional[subprocess.Popen]:
        """
        Play an audio file.
        
        Args:
            audio_path: Path to the audio file to play.
            blocking: If True, wait for playback to complete. If False, return
                     immediately and allow playback in background.
        
        Returns:
            If blocking=False, returns the subprocess.Popen object for the player.
            If blocking=True, returns None after playback completes.
        
        Raises:
            AudioPlaybackError: If the audio file doesn't exist or playback fails.
        """
        if not os.path.exists(audio_path):
            raise AudioPlaybackError(f"Audio file not found: {audio_path}")
        
        try:
            if self.system == "Linux":
                cmd = self._get_linux_command(audio_path)
            elif self.system == "Darwin":  # macOS
                cmd = ["afplay", audio_path]
            elif self.system == "Windows":
                cmd = [
                    "powershell",
                    "-c",
                    f"(New-Object Media.SoundPlayer '{audio_path}').PlaySync()"
                ]
            else:
                raise AudioPlaybackError(f"Unsupported OS: {self.system}")
            
            if blocking:
                subprocess.run(cmd, check=True)
                return None
            else:
                return subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
        except subprocess.CalledProcessError as e:
            raise AudioPlaybackError(f"Failed to play audio: {str(e)}")
        except Exception as e:
            raise AudioPlaybackError(f"Unexpected error during playback: {str(e)}")
    
    def _get_linux_command(self, audio_path: str) -> list:
        """Get the appropriate command for Linux audio playback."""
        if self.player == "mpg123":
            return ["mpg123", "-q", audio_path]
        elif self.player == "ffplay":
            return ["ffplay", "-nodisp", "-autoexit", audio_path]
        elif self.player == "mpv":
            return ["mpv", "--no-video", audio_path]
        elif self.player == "vlc":
            return ["vlc", "--intf", "dummy", "--play-and-exit", audio_path]
        else:
            raise AudioPlaybackError(f"Unknown player: {self.player}")
    
    def stop(self, process: Optional[subprocess.Popen]):
        """
        Stop background playback.
        
        Args:
            process: The subprocess.Popen object returned from play(blocking=False).
        """
        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()


class StreamingAudioPlayer:
    """
    Player for streaming audio data directly without saving to file first.
    Useful for real-time playback of TTS-generated audio.
    """
    
    def __init__(self):
        """Initialize the streaming audio player."""
        self.system = platform.system()
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if required tools for streaming are available."""
        if self.system == "Linux":
            if not self._command_exists('ffplay'):
                raise AudioPlaybackError(
                    "ffplay is required for streaming playback. "
                    "Install with: sudo apt-get install ffmpeg"
                )
            self.player = "ffplay"
        elif self.system == "Darwin":  # macOS
            if not self._command_exists('ffplay'):
                raise AudioPlaybackError(
                    "ffplay is required for streaming playback. "
                    "Install with: brew install ffmpeg"
                )
            self.player = "ffplay"
        elif self.system == "Windows":
            self.player = "ffplay"  # Assume available
        else:
            raise AudioPlaybackError(f"Unsupported OS: {self.system}")
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH."""
        try:
            subprocess.run(
                ['which', command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def play_bytes(self, audio_data: bytes, blocking: bool = True) -> Optional[subprocess.Popen]:
        """
        Play audio data directly from bytes without saving to file.
        
        Args:
            audio_data: Audio data as bytes (MP3 format).
            blocking: If True, wait for playback to complete.
        
        Returns:
            If blocking=False, returns the subprocess.Popen object.
            If blocking=True, returns None after playback.
        
        Raises:
            AudioPlaybackError: If playback fails.
        """
        try:
            cmd = ["ffplay", "-nodisp", "-autoexit", "-i", "pipe:0"]
            
            if blocking:
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                process.communicate(input=audio_data)
                return None
            else:
                process = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                process.stdin.write(audio_data)
                process.stdin.close()
                return process
                
        except Exception as e:
            raise AudioPlaybackError(f"Failed to play audio stream: {str(e)}")