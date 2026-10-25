"""
ARIA 10/10 Viral Short Production Orchestrator.
Builds the market-grade vertical video for Konark Sun Temple:
- Broadcast Neural Audio (Edge-TTS en-IN-PrabhatNeural at +12% rate)
- Kinetic ASS Karaoke Subtitles (2-3 words per card, glowing Sun Gold highlight)
- 17 High-Cadence Rapid Cuts (~2.2s each)
- Alternating Real Video Timelapses and High-Res Historical Stills
- Synthesized Stereo Atmospheric Drone layered at -19 dB
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
    broll_dir = os.path.abspath("assets/broll/konark")
    output_dir = os.path.abspath("data/creator_output")
    os.makedirs(output_dir, exist_ok=True)

    final_output_mp4 = os.path.join(output_dir, "konark_10_out_of_10_short.mp4")

    # High-retention script: 80 words, 38s duration
    viral_script = (
        "This eight-hundred-year-old temple tells the exact time down to the second, with zero electricity. "
        "Carved in 1250 AD, Konarks twenty-four giant stone wheels are not just decorations. "
        "They are precision astronomical dials. "
        "Each spoke casts a shadow calculating exact minutes and solar alignments with jaw-dropping accuracy. "
        "Ancient legends say a massive magnetic stone once floated inside the sanctum, pulling iron ships off course in the ocean. "
        "How did ancient builders achieve this without computers? "
        "Drop your theory in the comments."
    )

    # Asset paths
    timelapse_1 = os.path.join(broll_dir, "konark_timelapse.webm")
    timelapse_sunset = os.path.join(broll_dir, "konark_sunset_timelapse.webm")
    wheel_img = os.path.join(broll_dir, "shot_1_konark_sun_temple_wheel.jpg")
    monolith_img = os.path.join(broll_dir, "shot_2_konark_sun_temple_13th_century.jpg")
    jagamohana_img = os.path.join(broll_dir, "shot_3_konark_sun_temple_jagamohana.jpg")
    horse_img = os.path.join(broll_dir, "shot_4_konark_sun_temple_horse_sculpture.jpg")
    carving_img = os.path.join(broll_dir, "shot_5_konark_sun_temple_stone_carving.jpg")

    # 17 Rapid Cuts (averaging 2.25s per cut for a 38.3s master video)
    asset_manifest = [
        # Hook: 0.0 - 6.3s (Cuts 1-3)
        {"media_path": wheel_img, "duration": 2.2, "motion": "zoom_in"},
        {"media_path": timelapse_1, "duration": 2.2, "start_time": 2.0},
        {"media_path": carving_img, "duration": 2.2, "motion": "pan_down"},

        # Mechanism: 6.3 - 13.1s (Cuts 4-7)
        {"media_path": wheel_img, "duration": 2.2, "motion": "zoom_out"},
        {"media_path": monolith_img, "duration": 2.2, "motion": "zoom_in"},
        {"media_path": timelapse_sunset, "duration": 2.3, "start_time": 1.0},
        {"media_path": wheel_img, "duration": 2.2, "motion": "pan_up"},

        # Astronomical precision: 13.1 - 23.3s (Cuts 8-11)
        {"media_path": jagamohana_img, "duration": 2.2, "motion": "zoom_in"},
        {"media_path": timelapse_1, "duration": 2.3, "start_time": 8.0},
        {"media_path": carving_img, "duration": 2.3, "motion": "zoom_in"},
        {"media_path": wheel_img, "duration": 2.4, "motion": "pan_up"},

        # Mystery / 52-ton magnet legend: 23.3 - 31.7s (Cuts 12-14)
        {"media_path": horse_img, "duration": 2.4, "motion": "zoom_in"},
        {"media_path": jagamohana_img, "duration": 2.4, "motion": "zoom_out"},
        {"media_path": timelapse_sunset, "duration": 2.4, "start_time": 11.0},

        # Climax question & CTA: 31.7 - 38.4s (Cuts 15-17)
        {"media_path": horse_img, "duration": 2.2, "motion": "pan_down"},
        {"media_path": monolith_img, "duration": 2.2, "motion": "zoom_out"},
        {"media_path": timelapse_sunset, "duration": 2.5, "start_time": 16.0},
    ]

    print("[*] Launching ARIA 10/10 Viral Video Engine...")
    result = ViralShortEngine.compile_viral_short(
        script=viral_script,
        asset_manifest=asset_manifest,
        output_final_path=final_output_mp4,
        voice="en-IN-PrabhatNeural",
        rate="+12%"
    )
    return result


if __name__ == "__main__":
    main()
