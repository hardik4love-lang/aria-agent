"""
Retention Scriptwriter Engine for ARIA.
Enforces the 3-Beat Hook Architecture and Dual-Column Audio-Visual Production Standards.
"""

from typing import List, Dict, Any, Optional
from aria.creator.models import ScriptBeat, ProductionScript, PackagingConcept


class RetentionScriptwriter:
    """Specialized engine for retention-engineered YouTube scripts."""

    def __init__(self, creator_wpm: int = 150):
        self.creator_wpm = creator_wpm

    def build_3_beat_hook(self, topic: str, premise: str, stakes: str) -> List[ScriptBeat]:
        """
        Builds the critical first 30-second hook using the 3-Beat Structure:
        Beat 1 (00:00 - 00:06): Immediate Visual & Conceptual Shock (Delivers on thumbnail).
        Beat 2 (00:06 - 00:16): Raising the Stakes / Why it matters now.
        Beat 3 (00:16 - 00:30): The Roadmap with Withheld Payoff.
        """
        beat1 = ScriptBeat(
            timecode_range="00:00 - 00:06",
            audio_narration=f"This {premise}. And right now, almost everyone is doing it completely backwards.",
            visual_cue="Tight macro cut on subject / high-contrast action. Red rim lighting. Instant movement, zero intro logo.",
            pacing_wpm=self.creator_wpm,
            retention_tactic="visual_shock"
        )
        beat2 = ScriptBeat(
            timecode_range="00:06 - 00:16",
            audio_narration=f"Because if you ignore this, {stakes}. But get this one mechanism right, and everything changes.",
            visual_cue="Fast dynamic punch-in zoom. Overlay proof screenshot or data point on upper third. SFX: sub-bass drop.",
            pacing_wpm=self.creator_wpm,
            retention_tactic="stakes_escalation"
        )
        beat3 = ScriptBeat(
            timecode_range="00:16 - 00:30",
            audio_narration=f"Over the next eight minutes, we are testing the three biggest myths about {topic}—including the final test, which completely broke our results.",
            visual_cue="Split-screen 3-part montage teasing the tests. Rapid kinetic text flashing 'TEST 1', 'TEST 2', 'THE PAYOFF'.",
            pacing_wpm=self.creator_wpm,
            retention_tactic="curiosity_gap"
        )
        return [beat1, beat2, beat3]

    def generate_dual_column_script(
        self,
        working_title: str,
        topic: str,
        premise: str,
        stakes: str,
        core_steps: List[Dict[str, str]],
        call_to_action_text: str,
        packaging: Optional[PackagingConcept] = None
    ) -> ProductionScript:
        """
        Generates a complete production script in dual-column AV format with telemetry.
        """
        hook_beats = self.build_3_beat_hook(topic, premise, stakes)

        # Hook words and duration
        hook_words = sum(len(b.audio_narration.split()) for b in hook_beats)
        hook_duration_sec = 30
        current_second = hook_duration_sec

        core_beats: List[ScriptBeat] = []
        for i, step in enumerate(core_steps, 1):
            narration = step.get("audio", f"Step {i} revolves around optimizing the core variable.")
            visual = step.get("visual", "B-roll demonstration with kinetic callouts.")
            tactic = step.get("tactic", "pattern_interrupt" if i % 2 == 0 else "curiosity_gap")

            # Dynamically size duration from word count based on creator WPM
            word_count = len(narration.split())
            duration_sec = max(3, int(round((word_count / self.creator_wpm) * 60)))
            end_second = current_second + duration_sec

            tc_start = f"{current_second // 60:02d}:{current_second % 60:02d}"
            tc_end = f"{end_second // 60:02d}:{end_second % 60:02d}"

            core_beats.append(ScriptBeat(
                timecode_range=f"{tc_start} - {tc_end}",
                audio_narration=narration,
                visual_cue=visual,
                pacing_wpm=self.creator_wpm,
                retention_tactic=tactic
            ))
            current_second = end_second

        # Call to Action Beat
        cta_words = len(call_to_action_text.split())
        cta_duration = max(4, int(round((cta_words / self.creator_wpm) * 60)))
        cta_start = f"{current_second // 60:02d}:{current_second % 60:02d}"
        cta_end = f"{(current_second + cta_duration) // 60:02d}:{(current_second + cta_duration) % 60:02d}"
        cta_beat = ScriptBeat(
            timecode_range=f"{cta_start} - {cta_end}",
            audio_narration=call_to_action_text,
            visual_cue="Host on A-camera. Clean lower-third with link and end-screen video card overlay.",
            pacing_wpm=self.creator_wpm,
            retention_tactic="payoff"
        )
        total_duration_sec = current_second + cta_duration

        all_beats = hook_beats + core_beats + [cta_beat]
        total_words = sum(len(b.audio_narration.split()) for b in all_beats)
        avg_wpm = (total_words / total_duration_sec) * 60 if total_duration_sec > 0 else self.creator_wpm
        visual_cut_freq = total_duration_sec / len(all_beats) if all_beats else 5.0

        # Compute Retention Health Score (0-100)
        wpm_score = 100 - min(40, abs(avg_wpm - 150) * 2)
        cut_score = 100 - min(40, abs(visual_cut_freq - 5.0) * 10)
        retention_score = round(max(50.0, (wpm_score * 0.5) + (cut_score * 0.5)), 1)

        return ProductionScript(
            working_title=working_title,
            target_duration_minutes=round(total_duration_sec / 60, 2),
            packaging_concept=packaging,
            hook_3_beat=hook_beats,
            core_narrative_blocks=core_beats,
            call_to_action=cta_beat,
            total_words=total_words,
            avg_pacing_wpm=round(avg_wpm, 1),
            visual_cut_frequency_sec=round(visual_cut_freq, 1),
            retention_health_score=retention_score
        )

    def format_markdown_av_table(self, script: ProductionScript) -> str:
        """
        Formats the script as a professional, production-grade 2-Column AV table.
        """
        lines = [
            f"# Production Script: {script.working_title}",
            f"**Target Duration:** {script.target_duration_minutes} min | **Total Words:** {script.total_words} | **Avg Pacing:** {script.avg_pacing_wpm} WPM | **Visual Cut Every:** {script.visual_cut_frequency_sec}s | **Retention Score:** {script.retention_health_score}/100",
            "",
            "| Timecode | Audio (Spoken Word & Sound Design) | Visual (Framing, B-Roll & On-Screen Graphics) | Tactic |",
            "| :--- | :--- | :--- | :--- |"
        ]

        all_beats = script.hook_3_beat + script.core_narrative_blocks + [script.call_to_action]
        for beat in all_beats:
            audio_clean = beat.audio_narration.replace("\n", " ").replace("|", "&#124;")
            visual_clean = beat.visual_cue.replace("\n", " ").replace("|", "&#124;")
            lines.append(f"| `{beat.timecode_range}` | {audio_clean} | {visual_clean} | `{beat.retention_tactic}` |")

        return "\n".join(lines)
