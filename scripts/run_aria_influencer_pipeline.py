import os
import sys
import json
import asyncio
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from aria.creator.retention_scriptwriter import RetentionScriptwriter
from aria.creator.packaging_engine import PackagingEngine
from aria.creator.viral_short_engine import ViralShortEngine
from aria.creator.youtube_publisher import YouTubePublisher

async def main():
    print("=" * 70)
    print("ARIA AUTONOMOUS YOUTUBE & SACRED HERITAGE INFLUENCER ENGINE")
    print("=" * 70)
    
    topic = "Brihadisvara Granite Superstructure"
    premise = "80-ton single-block granite Kumbam capstone resting 66 meters high without mortar"
    stakes = "the nearest granite quarry was 60 kilometers away across river deltas"
    
    output_dir = "D:/aria-agent/data/creator_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Co-Design Viral Packaging Matrix
    print(f"\n[1/4] Co-Designing Viral Packaging Matrix for: {topic}...")
    packager = PackagingEngine()
    matrix = packager.generate_packaging_matrix(topic, "How 1,000-year-old interlocking granite survived 6 major earthquakes")
    best_packaging = matrix[0]
    print(f"  -> Title: {best_packaging.title}")
    print(f"  -> Curiosity Gap: {best_packaging.curiosity_gap_score}/10")
    print(f"  -> Thumbnail Concept: {best_packaging.thumbnail_concept}")
    
    # 2. Synthesize High-Retention Viral Script Beats
    print(f"\n[2/4] Synthesizing High-Retention 3-Beat Hook Script...")
    scriptwriter = RetentionScriptwriter()
    hook_beats = scriptwriter.build_3_beat_hook(topic=topic, premise=premise, stakes=stakes)
    narration_text = " ".join([b.audio_narration for b in hook_beats])
    print(f"  -> Script Word Count: {len(narration_text.split())} words")
    print(f"  -> Hook Line: \"{hook_beats[0].audio_narration}\"")
    
    script_file = os.path.join(output_dir, "brihadisvara_influencer_script.txt")
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(narration_text)
    
    # 3. Generate Neural Voiceover (Edge-TTS)
    print(f"\n[3/4] Synthesizing Neural Voiceover (Edge-TTS)...")
    audio_file = os.path.join(output_dir, "brihadisvara_neural_voice.mp3")
    try:
        sentences = await ViralShortEngine.generate_neural_voice(
            script=narration_text,
            output_audio_path=audio_file,
            voice="en-IN-PrabhatNeural",
            rate="+10%"
        )
        print(f"  -> Neural Voiceover generated: {audio_file} ({os.path.getsize(audio_file):,} bytes)")
    except Exception as e:
        print(f"  -> Edge-TTS note: {e}")
    
    # 4. Packaging Influencer Videos with YouTube Publish Manifests
    print(f"\n[4/4] Generating Ready-to-Publish Influencer Video Manifests...")
    existing_videos = [
        ("D:/aria-agent/data/creator_output/kailasa_10_out_of_10_short.mp4", "The Impossible Ancient Machine: Kailasa Temple Secrets", "D:/aria-agent/data/creator_output/kailasa_preview_1.jpg"),
        ("D:/aria-agent/data/creator_output/konark_10_out_of_10_short.mp4", "The Sundial That Decodes The Cosmos: Konark Sun Temple", "D:/aria-agent/data/creator_output/preview_1.jpg"),
        ("D:/aria-agent/data/creator_output/konark_REAL_multiscene_video.mp4", "Ancient Astronomical Clock Hidden in Granite: Konark 4K", "D:/aria-agent/data/creator_output/preview_2.jpg")
    ]
    
    for vpath, vtitle, vthumb in existing_videos:
        if os.path.exists(vpath):
            thumb_path = vthumb if os.path.exists(vthumb) else None
            pub_res = YouTubePublisher.upload_short(
                video_path=vpath,
                title=vtitle,
                description=f"{vtitle}. Produced autonomously by ARIA Sacred Heritage AI. 100% CC0 / CC-BY Public Archives. #Shorts #Architecture #IndianHeritage #Engineering",
                tags=["Shorts", "AncientTemples", "Archaeology", "Engineering", "SacredHeritage"],
                thumbnail_path=thumb_path
            )
            print(f"  [READY FOR PUBLISHING] {os.path.basename(vpath)} -> Status: {pub_res.get('status')}")
    
    print("\n" + "=" * 70)
    print("ARIA INFLUENCER & VIDEO PRODUCTION SUITE IS FULLY ARMED")
    print("=" * 70)

if __name__ == '__main__':
    asyncio.run(main())
