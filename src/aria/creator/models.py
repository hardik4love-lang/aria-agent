"""
Data models for ARIA's YouTube Influencer Production Engine.
Defines schemas for retention scripting, packaging matrix, trend outliers, and analytics telemetry.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ScriptBeat(BaseModel):
    """A discrete visual and narrative beat within an AV production script."""
    timecode_range: str = Field(description="Estimated timecode range, e.g. '00:00 - 00:06'")
    audio_narration: str = Field(description="Spoken text in creator voice, zero intro throat-clearing")
    visual_cue: str = Field(description="Exact camera framing, B-roll, on-screen text, or motion graphic cue")
    pacing_wpm: int = Field(default=150, description="Target speaking cadence in Words Per Minute (140-160 WPM ideal)")
    retention_tactic: str = Field(
        description="Applied retention device: 'visual_shock', 'stakes_escalation', 'curiosity_gap', 'pattern_interrupt', 'payoff'"
    )


class PackagingConcept(BaseModel):
    """A title and thumbnail packaging concept pair engineered for high CTR."""
    title: str = Field(description="High-CTR title variant (under 55 characters recommended)")
    thumbnail_concept: str = Field(description="Visual description of the primary visual element and expression")
    visual_focal_point: str = Field(description="Primary object or subject capturing the eye (Rule of Thirds)")
    on_screen_text: str = Field(default="", description="Max 2-3 high-impact words on thumbnail (optional)")
    psychological_lever: Literal["high_stakes_fomo", "extreme_novelty", "counter_intuitive_truth", "curiosity_loop"]
    curiosity_gap_score: float = Field(ge=0.0, le=10.0, description="Algorithmic score of narrative gap")
    image_generation_prompt: str = Field(description="Production-ready prompt for Midjourney / Flux / DALL-E")


class ProductionScript(BaseModel):
    """Full dual-column production script with embedded retention and pacing telemetry."""
    working_title: str
    target_duration_minutes: float
    packaging_concept: Optional[PackagingConcept] = None
    hook_3_beat: List[ScriptBeat]
    core_narrative_blocks: List[ScriptBeat]
    call_to_action: ScriptBeat
    total_words: int
    avg_pacing_wpm: float
    visual_cut_frequency_sec: float
    retention_health_score: float = Field(ge=0.0, le=100.0)


class ShortsRepurpose(BaseModel):
    """Vertical 9:16 micro-narrative extracted from a long-form production script."""
    title: str
    target_duration_sec: int = Field(default=55, le=60)
    vertical_hook_10s: str
    body_core: str
    audio_loop_outro: str
    visual_framing_9x16: str
    hashtags: List[str]


class TrendOutlier(BaseModel):
    """An outlier video topic validated across competitor channels."""
    topic: str
    competitor_channel: str
    views_48h: int
    channel_30d_median_views: int
    outlier_ratio: float
    is_breakout: bool
    recommended_angle: str


class RetentionDiagnostic(BaseModel):
    """Telemetry diagnostic evaluating audience drop-off points."""
    timestamp_sec: int
    drop_percentage: float
    suspected_cause: str
    corrective_action: str
