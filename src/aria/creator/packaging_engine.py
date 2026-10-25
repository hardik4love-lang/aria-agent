"""
Packaging Engine for ARIA.
Co-designs high-CTR Title & Thumbnail pairs across psychological levers with prompt generation.
"""

from typing import List, Dict, Any
import re
from aria.creator.models import PackagingConcept


class PackagingEngine:
    """Specialized engine for Title and Thumbnail co-design."""

    POWER_WORDS = {
        "illegal", "banned", "secret", "exposed", "stopped", "destroy",
        "ruined", "mistake", "warning", "never", "truth", "lies", "failed",
        "changed", "hacked", "surprising", "impossible", "fastest", "richest"
    }

    def score_curiosity_gap(self, title: str) -> float:
        """
        Scores title curiosity gap on a scale of 0.0 to 10.0 based on:
        - Brevity & punchiness (ideal: 35-50 characters)
        - Presence of psychological power words
        - Presence of open curiosity loops (why, how, what happens)
        - Absence of clickbait disappointment / generic clichés
        """
        score = 5.0
        char_len = len(title)

        # Length optimization: sweet spot is 30-55 chars (mobile readability without truncation)
        if 30 <= char_len <= 55:
            score += 2.0
        elif char_len > 70:
            score -= 1.5

        words = set(re.findall(r"\b[a-zA-Z]+\b", title.lower()))
        power_matches = words.intersection(self.POWER_WORDS)
        score += min(2.0, len(power_matches) * 1.0)

        # Question / Curiosity loop markers
        if any(marker in title.lower() for marker in ["why", "how", "what actually", "the truth about"]):
            score += 1.0

        # Numbers / specific quantities
        if re.search(r"\b\d+\b", title):
            score += 0.5

        return round(min(10.0, max(1.0, score)), 1)

    def generate_packaging_matrix(self, topic: str, key_insight: str) -> List[PackagingConcept]:
        """
        Generates 4 distinct, high-performing Title-Thumbnail pairs across core psychological levers.
        """
        concepts: List[PackagingConcept] = []

        # 1. High Stakes / FOMO
        title_1 = f"Stop Using {topic} Until You Watch This"
        concepts.append(PackagingConcept(
            title=title_1,
            thumbnail_concept="Host staring at camera with serious warning expression, holding up a red warning indicator next to the subject.",
            visual_focal_point="Host face on right third with intense eye contact; glowing red alert icon on left.",
            on_screen_text="STOP NOW",
            psychological_lever="high_stakes_fomo",
            curiosity_gap_score=self.score_curiosity_gap(title_1),
            image_generation_prompt=(
                f"Cinematic YouTube thumbnail, hyper-detailed photography, split lighting with red and deep blue rim light, "
                f"charismatic tech creator with an urgent serious expression holding up an item representing {topic}, "
                f"shallow depth of field, high contrast, clean minimalist background, 8k resolution, rule of thirds."
            )
        ))

        # 2. Extreme Novelty / "I Tested"
        title_2 = f"I Replaced Everything With {topic} For 30 Days"
        concepts.append(PackagingConcept(
            title=title_2,
            thumbnail_concept="Split before/after showing the chaotic previous setup vs the hyper-minimalist setup using the subject.",
            visual_focal_point="Extreme contrast between side A (red chaos) and side B (clean green success).",
            on_screen_text="30 DAYS LATER",
            psychological_lever="extreme_novelty",
            curiosity_gap_score=self.score_curiosity_gap(title_2),
            image_generation_prompt=(
                f"Ultra-high resolution YouTube thumbnail, side-by-side comparison aesthetic, left side cluttered and stressful with red tint, "
                f"right side pristine and futuristic showcasing {topic} with bright green clean lighting, vibrant color grading, high dynamic range."
            )
        ))

        # 3. Counter-Intuitive Truth / Myth Busting
        title_3 = f"The {topic} Lie Everyone Believes"
        concepts.append(PackagingConcept(
            title=title_3,
            thumbnail_concept="A giant red 'FALSE' stamp overlaid over the standard industry dogma, with host pointing directly at the flaw.",
            visual_focal_point="Bold red stamp over standard chart/subject, host looking intrigued.",
            on_screen_text="THE LIE",
            psychological_lever="counter_intuitive_truth",
            curiosity_gap_score=self.score_curiosity_gap(title_3),
            image_generation_prompt=(
                f"Modern studio YouTube thumbnail, creator looking skeptically at camera while pointing at a bold holographic graphic of {topic}, "
                f"dramatic studio lighting, cinematic rim light, crisp focus, clean negative space for YouTube title overlay, 8k octane render style."
            )
        ))

        # 4. Curiosity Loop / The Secret
        title_4 = f"How {topic} Actually Works Behind Closed Doors"
        concepts.append(PackagingConcept(
            title=title_4,
            thumbnail_concept="A partially opened vault or teardown showing internal components usually hidden from the public.",
            visual_focal_point="Cross-section internal reveal with warm internal glow.",
            on_screen_text="UNLOCKED",
            psychological_lever="curiosity_loop",
            curiosity_gap_score=self.score_curiosity_gap(title_4),
            image_generation_prompt=(
                f"Detailed documentary style YouTube thumbnail, dramatic moody studio lighting, macro cross-section teardown of {topic}, "
                f"intricate internal components glowing from within, dark atmospheric background, photorealistic, 8k."
            )
        ))

        return concepts
