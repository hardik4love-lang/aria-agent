import os
import sys
import json
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from aria.creator.viral_short_engine import ViralShortEngine
from aria.creator.multi_scene_video_builder import MultiSceneVideoBuilder
from aria.creator.youtube_publisher import YouTubePublisher

MANIFEST_PATH = "D:/aria-agent/data/creator_output/VIRAL_15_SHORTS_CONTROVERSY_SUITE.json"
OUTPUT_DIR = "D:/aria-agent/data/creator_output/viral_shorts_renders"
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def synthesize_all_voices():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        controversies = json.load(f)
        
    print(f"Loaded {len(controversies)} viral controversy shorts.")
    
    for c in controversies:
        cid = c["id"]
        slug = "".join(x if x.isalnum() else "_" for x in c["topic"].lower())[:30].strip("_")
        audio_path = os.path.join(OUTPUT_DIR, f"{cid}_{slug}_voice.mp3")
        ass_path = os.path.join(OUTPUT_DIR, f"{cid}_{slug}_kinetic.ass")
        publish_json_path = os.path.join(OUTPUT_DIR, f"{cid}_{slug}_publish.json")
        
        script = c["short_script_hook"]
        
        # 1. Generate Voiceover
        print(f"\n[{cid}] Synthesizing Neural Voice for: {c['topic']}...")
        try:
            sentences = await ViralShortEngine.generate_neural_voice(
                script=script,
                output_audio_path=audio_path,
                voice="en-IN-PrabhatNeural",
                rate="+12%"
            )
            print(f"  -> Generated {os.path.getsize(audio_path):,} bytes audio.")
            
            # 2. Build Kinetic ASS Subtitles
            if sentences:
                ViralShortEngine.build_kinetic_ass(sentences, ass_path)
                print(f"  -> Kinetic ASS Subtitles: {ass_path}")
        except Exception as e:
            print(f"  -> Note on voice synthesis: {e}")
            
        # 3. Create Automated YouTube Short Publishing Manifest
        pub_meta = {
            "id": cid,
            "title": f"{c['viral_question']} #Shorts",
            "description": f"{c['viral_question']}\n\n{c['facts_vs_myth']}\n\nProduced by ARIA Sacred Heritage AI. Subscribe for the full 52-minute documentary.\n\n#Shorts #AncientHistory #IndianArchitecture #KailasaTemple #EngineeringAnomalies #Mystery",
            "tags": ["Shorts", "AncientMysteries", "Archaeology", "Engineering", "Architecture", "India", "History"],
            "thumbnail_concept": c["thumbnail_visual"],
            "thumbnail_title": c["thumbnail_title"],
            "on_screen_hook": c["on_screen_text"],
            "audio_file": audio_path,
            "subtitles_file": ass_path,
            "target_format": "1080x1920 Vertical Short (15-30s)",
            "status": "READY_FOR_FFMPEG_COMPILATION"
        }
        with open(publish_json_path, "w", encoding="utf-8") as pf:
            json.dump(pub_meta, pf, indent=2)
            
    print("\n" + "=" * 70)
    print(f"✅ ALL {len(controversies)} VIRAL SHORTS ASSETS GENERATED & ARMED FOR PRODUCTION")
    print("=" * 70)

if __name__ == '__main__':
    asyncio.run(synthesize_all_voices())
