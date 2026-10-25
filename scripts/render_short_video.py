#!/usr/bin/env python3
"""
ARIA Automated End-to-End Short-Form Video Production Pipeline.
Bridges the gap between research/scriptwriting and finished broadcast MP4 deliverables:
1. Synthesizes zero-cost neural voiceover via Edge-TTS
2. Pairs voiceover with Aria's photorealistic portrait & temple visual assets
3. Renders 1080x1920 vertical video with burnt-in subtitle timings via FFmpeg
"""

import os
import sys
import argparse

# Ensure utf-8 encoding on Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add src to pythonpath
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from aria.creator.audio_synthesizer import AudioSynthesizer
from aria.creator.video_renderer import VideoRenderer


def render_temple_short(temple_slug: str = "kailasa", voice: str = "en-IN-NeerjaNeural") -> dict:
    creator_dir = os.path.join(BASE_DIR, "data", "creator_output")
    assets_dir = os.path.join(BASE_DIR, "assets")

    narration_file = os.path.join(creator_dir, f"{temple_slug}_viral_30s_narration.txt")
    srt_file = os.path.join(creator_dir, f"{temple_slug}_viral_30s.srt")
    image_file = os.path.join(assets_dir, "aria_sacred_heritage_portrait.jpg")

    audio_output = os.path.join(creator_dir, f"{temple_slug}_viral_30s_audio.mp3")
    video_output = os.path.join(creator_dir, f"{temple_slug}_viral_30s.mp4")

    if not os.path.exists(narration_file):
        raise FileNotFoundError(f"Narration file not found: {narration_file}")
    if not os.path.exists(image_file):
        raise FileNotFoundError(f"Visual asset not found: {image_file}")

    print("==================================================================")
    print(f"  ARIA AUTOMATED VIDEO PRODUCTION PIPELINE")
    print(f"  Temple: {temple_slug.upper()} | Voice: {voice}")
    print(f"  Visual Asset: {os.path.basename(image_file)}")
    print("==================================================================")

    # 1. Synthesize neural audio
    print(f"\n[1/2] Synthesizing broadcast-grade neural voiceover...")
    AudioSynthesizer.synthesize_file(narration_file, audio_output, voice=voice)
    audio_size = os.path.getsize(audio_output)
    print(f"  [+] Audio synthesized: {audio_output} ({audio_size:,} bytes)")

    # 2. Render vertical video
    print(f"\n[2/2] Compositing 1080x1920 vertical video with FFmpeg...")
    res = VideoRenderer.render_vertical_short(
        image_path=image_file,
        audio_path=audio_output,
        output_mp4_path=video_output,
        srt_path=srt_file if os.path.exists(srt_file) else None
    )

    print(f"\n[+] VIDEO PRODUCTION COMPLETE!")
    print(f"  • Deliverable: {video_output}")
    print(f"  • File Size: {res['file_size_bytes']:,} bytes")
    print(f"  • Resolution: {res['resolution']}")
    print("==================================================================\n")

    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render ARIA Short-Form Video Deliverable")
    parser.add_argument("--temple", default="kailasa", help="Temple slug (default: kailasa)")
    parser.add_argument("--voice", default="en-IN-NeerjaNeural", help="Neural voice identifier")
    args = parser.parse_args()

    render_temple_short(args.temple, voice=args.voice)
