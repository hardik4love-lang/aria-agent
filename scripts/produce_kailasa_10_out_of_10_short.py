"""
ARIA 10/10 Viral Short Production: Kailasa Temple (Cave 16, Ellora).
Full Commercial Market Standard:
- Broadcast Neural Audio (Edge-TTS en-IN-PrabhatNeural at +14% rate)
- Kinetic ASS Karaoke Subtitles (2-3 words per card, glowing Sun Gold highlight)
- 21 High-Cadence Rapid Cuts (~2.3s each)
- Alternating Real Video Timelapses and High-Res 12MB+ Historical Stills
- Atmospheric Synthesized Stereo Ambient Drone layered at -18.4 dB
- Cinematic Golden Hour Color Grade + Vignette
"""

import os
import sys

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add src to path
sys.path.insert(0, os.path.abspath("src"))

from aria.creator.viral_short_engine import ViralShortEngine


def main():
    kailasa_broll = os.path.abspath("assets/broll/kailasa")
    common_broll = os.path.abspath("assets/broll/konark")
    output_dir = os.path.abspath("data/creator_output")
    os.makedirs(output_dir, exist_ok=True)

    final_output_mp4 = os.path.join(output_dir, "kailasa_10_out_of_10_short.mp4")

    # High-retention script: 96 words, ~49s duration
    kailasa_script = (
        "This twelve-hundred-year-old temple was not built from the ground up. "
        "It was carved out of a single solid mountain from the top down. "
        "Ancient artisans chiseled over two hundred thousand tons of basalt with zero room for error. "
        "One single broken pillar would ruin the entire monument forever. "
        "With zero scaffolding, sculptors carved roofs, giant pillars, and life-sized stone elephants as they descended into the rock. "
        "In 1682, Emperor Aurangzeb sent three thousand men to demolish it completely. "
        "After three continuous years of relentless hammering, the mountain defeated them. The monolithic structure barely had a scratch. "
        "How did eighth-century engineers achieve this without modern machines? "
        "Drop your theory in the comments."
    )

    # Assets
    timelapse_sky = os.path.join(common_broll, "konark_timelapse.webm")
    timelapse_sunset = os.path.join(common_broll, "konark_sunset_timelapse.webm")

    img_overview = os.path.join(kailasa_broll, "shot_1_kailasa_overview.jpg")
    img_elephants = os.path.join(kailasa_broll, "shot_2_kailasa_elephants.jpg")
    img_courtyard = os.path.join(kailasa_broll, "shot_3_kailasa_courtyard.jpg")
    img_pillars = os.path.join(kailasa_broll, "shot_4_kailasa_pillars.jpg")
    img_majestic = os.path.join(kailasa_broll, "shot_5_kailasa_majestic.jpg")
    img_gajalakshmi = os.path.join(kailasa_broll, "shot_6_kailasa_gajalakshmi.jpg")
    img_temple_angle = os.path.join(kailasa_broll, "shot_7_kailasa_temple_angle.jpg")
    img_ravana = os.path.join(kailasa_broll, "shot_8_kailasa_ravana.jpg")

    # 21 High-Cadence Rapid Cuts (~2.34s each for 49.2s runtime)
    asset_manifest = [
        # Hook: 0.0 - 6.8s (Cuts 1-3)
        {"media_path": img_overview, "duration": 2.3, "motion": "zoom_in"},
        {"media_path": timelapse_sky, "duration": 2.3, "start_time": 1.0},
        {"media_path": img_overview, "duration": 2.3, "motion": "pan_down"},

        # Scale & zero-margin error: 6.8 - 16.0s (Cuts 4-8)
        {"media_path": img_majestic, "duration": 2.3, "motion": "zoom_in"},
        {"media_path": img_courtyard, "duration": 2.3, "motion": "zoom_in"},
        {"media_path": timelapse_sunset, "duration": 2.3, "start_time": 2.0},
        {"media_path": img_pillars, "duration": 2.4, "motion": "pan_up"},
        {"media_path": img_temple_angle, "duration": 2.4, "motion": "zoom_out"},

        # No scaffolding & top-down descent: 16.0 - 27.8s (Cuts 9-13)
        {"media_path": img_overview, "duration": 2.3, "motion": "zoom_out"},
        {"media_path": img_majestic, "duration": 2.4, "motion": "pan_down"},
        {"media_path": img_pillars, "duration": 2.4, "motion": "zoom_in"},
        {"media_path": img_elephants, "duration": 2.4, "motion": "pan_down"},
        {"media_path": img_ravana, "duration": 2.4, "motion": "zoom_in"},

        # Aurangzeb 3-year siege: 27.8 - 39.8s (Cuts 14-18)
        {"media_path": img_gajalakshmi, "duration": 2.4, "motion": "zoom_in"},
        {"media_path": img_courtyard, "duration": 2.4, "motion": "pan_up"},
        {"media_path": timelapse_sunset, "duration": 2.3, "start_time": 8.0},
        {"media_path": img_ravana, "duration": 2.4, "motion": "zoom_out"},
        {"media_path": img_overview, "duration": 2.4, "motion": "zoom_in"},

        # The mystery question & CTA: 39.8 - 49.3s (Cuts 19-21)
        {"media_path": img_temple_angle, "duration": 2.4, "motion": "zoom_in"},
        {"media_path": img_majestic, "duration": 2.3, "motion": "zoom_out"},
        {"media_path": timelapse_sunset, "duration": 2.5, "start_time": 15.0},
    ]

    print("[*] Launching ARIA 10/10 Production for Kailasa Temple...")
    result = ViralShortEngine.compile_viral_short(
        script=kailasa_script,
        asset_manifest=asset_manifest,
        output_final_path=final_output_mp4,
        voice="en-IN-PrabhatNeural",
        rate="+14%",
        temp_dir="D:/aria-agent/data/creator_output/temp_kailasa_engine"
    )
    return result


if __name__ == "__main__":
    main()
