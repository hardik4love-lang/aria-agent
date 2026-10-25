"""
ARIA Zero-Cost Neural & Local Voiceover Synthesizer.
Dual-layer synthesis engine:
1. Primary: Edge-TTS Neural Voice (High-Fidelity broadcast audio)
2. Resilient Fallback: Native SAPI / OS Speech Synthesizer (100% offline, zero-network dependency)
100% $0.00 perpetual TCO.
"""

import os
import sys
import asyncio
import subprocess
from typing import Optional


class AudioSynthesizer:
    """Synthesizes high-fidelity voiceover narration for video deliverables."""

    VOICE_INDIAN_FEMALE = "en-IN-NeerjaNeural"
    VOICE_BRITISH_FEMALE = "en-GB-SoniaNeural"
    VOICE_AMERICAN_FEMALE = "en-US-JennyNeural"

    @classmethod
    def _synthesize_local_sapi(cls, text: str, output_wav_path: str) -> str:
        """Generates voiceover using native Windows SAPI speech engine."""
        try:
            import win32com.client
            os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            stream.Open(output_wav_path, 3)  # 3 = SSFMCreateForWrite
            speaker.AudioOutputStream = stream
            speaker.Speak(text)
            stream.Close()
            return output_wav_path
        except Exception as e:
            raise RuntimeError(f"Local SAPI speech synthesis failed: {e}")

    @classmethod
    def _convert_wav_to_mp3(cls, wav_path: str, mp3_path: str) -> str:
        """Converts intermediate WAV to clean MP3 via FFmpeg."""
        cmd = ["ffmpeg", "-y", "-i", wav_path, "-codec:a", "libmp3lame", "-qscale:a", "2", mp3_path]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if os.path.exists(wav_path):
            try:
                os.remove(wav_path)
            except Exception:
                pass
        return mp3_path

    @classmethod
    async def _async_edge_tts(
        cls,
        text: str,
        output_path: str,
        voice: str = VOICE_INDIAN_FEMALE,
        rate: str = "-2%",
        pitch: str = "+1Hz"
    ) -> str:
        import edge_tts
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
        await communicate.save(output_path)
        return output_path

    @classmethod
    def synthesize_text(
        cls,
        text: str,
        output_mp3_path: str,
        voice: str = VOICE_INDIAN_FEMALE
    ) -> str:
        """Synthesizes speech to MP3 with automatic graceful fallback."""
        os.makedirs(os.path.dirname(os.path.abspath(output_mp3_path)), exist_ok=True)

        # 1. Try Edge-TTS Neural Voice
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if not loop.is_running():
                loop.run_until_complete(cls._async_edge_tts(text, output_mp3_path, voice=voice))
                if os.path.exists(output_mp3_path) and os.path.getsize(output_mp3_path) > 1000:
                    return output_mp3_path
        except Exception as e:
            print(f"[*] Note: Edge-TTS network handshake bypassed ({e}). Mobilizing resilient offline voice engine...")

        # 2. Resilient Offline Fallback: SAPI -> FFmpeg MP3
        temp_wav = output_mp3_path.replace(".mp3", "_temp.wav")
        cls._synthesize_local_sapi(text, temp_wav)
        cls._convert_wav_to_mp3(temp_wav, output_mp3_path)
        return output_mp3_path

    @classmethod
    def synthesize_file(
        cls,
        text_file_path: str,
        output_mp3_path: str,
        voice: str = VOICE_INDIAN_FEMALE
    ) -> str:
        """Synthesizes voiceover from a text file path."""
        with open(text_file_path, "r", encoding="utf-8") as f:
            raw_text = f.read().strip()
        return cls.synthesize_text(raw_text, output_mp3_path, voice=voice)
