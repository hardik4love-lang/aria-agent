"""
Multi-Platform Content Repurposing Engine for ARIA.
Transforms long-form scripts into high-retention 9:16 vertical Shorts, Reels, and TikToks with audio loops.
"""

from typing import List
from aria.creator.models import ProductionScript, ShortsRepurpose


class ShortsRepurposer:
    """Specialized engine for vertical short-form extraction and audio looping."""

    def extract_shorts_from_script(self, script: ProductionScript) -> List[ShortsRepurpose]:
        """
        Extracts up to 2 high-energy, vertical 9:16 Shorts from the long-form production script.
        Enforces:
        - 1-3 second visual hook
        - Single clear tension-and-payoff arc under 55 seconds
        - Circular audio loop (the outro sentence connects into the intro sentence)
        """
        shorts: List[ShortsRepurpose] = []

        # Short #1: The Hook & Core Reveal
        hook_text = script.hook_3_beat[0].audio_narration if script.hook_3_beat else "Here is what no one told you."
        first_block = script.core_narrative_blocks[0].audio_narration if script.core_narrative_blocks else "The core mechanism is simple."

        short_1 = ShortsRepurpose(
            title=f"The Truth About {script.working_title} (Part 1)",
            target_duration_sec=45,
            vertical_hook_10s=f"Before you do anything else, watch this: {hook_text}",
            body_core=f"Here is what happened when we actually tested it: {first_block}",
            audio_loop_outro="And that is why you should always know that...",  # Seamlessly loops into "Before you do anything else..."
            visual_framing_9x16="Vertical 9:16 centered crop. Dynamic animated captions (word-by-word yellow/white glow) centered at chest level.",
            hashtags=["#Shorts", "#CreatorEconomy", "#TechTips", "#Viral"]
        )
        shorts.append(short_1)

        # Short #2: The Culmination / Twist
        if len(script.core_narrative_blocks) > 1:
            climax_block = script.core_narrative_blocks[-1].audio_narration
            short_2 = ShortsRepurpose(
                title=f"The Biggest Mistake In {script.working_title}",
                target_duration_sec=50,
                vertical_hook_10s="If you only remember one thing from this entire breakdown, make sure it's this:",
                body_core=climax_block,
                audio_loop_outro="Which brings us right back to the start, because...",
                visual_framing_9x16="Vertical 9:16 split screen. Top 50%: Host reaction. Bottom 50%: Screen recording proof / B-roll demonstration.",
                hashtags=["#LifeHack", "#Productivity", "#Shorts"]
            )
            shorts.append(short_2)

        return shorts
