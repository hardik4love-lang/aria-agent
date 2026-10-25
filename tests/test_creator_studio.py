"""
Unit tests for ARIA's Creator Studio (YouTube Influencer Production Engine).
Verifies models, scriptwriter, packaging matrix, outlier scout, and repurposing.
"""

import pytest
from aria.creator import (
    RetentionScriptwriter,
    PackagingEngine,
    OutlierScout,
    ShortsRepurposer,
    ScriptBeat,
    PackagingConcept,
    ProductionScript,
)


def test_3_beat_hook_generation():
    writer = RetentionScriptwriter(creator_wpm=150)
    hook = writer.build_3_beat_hook(
        topic="AI Micro-SaaS",
        premise="single line of code generated $12,000 in passive revenue",
        stakes="you waste months building apps nobody ever pays for"
    )

    assert len(hook) == 3
    assert hook[0].retention_tactic == "visual_shock"
    assert hook[1].retention_tactic == "stakes_escalation"
    assert hook[2].retention_tactic == "curiosity_gap"
    assert "00:00" in hook[0].timecode_range
    assert "00:30" in hook[2].timecode_range


def test_dual_column_script_generation_and_markdown():
    writer = RetentionScriptwriter(creator_wpm=150)
    core_steps = [
        {
            "audio": "First, we initialize the sovereign backend without any paid third-party dependencies.",
            "visual": "A-roll talking head pushes in. Code terminal displays 0 dependencies.",
            "tactic": "pattern_interrupt"
        },
        {
            "audio": "Next, the automated webhook verifies incoming events under 20 milliseconds.",
            "visual": "Split screen terminal benchmark hitting sub-20ms latency counter.",
            "tactic": "curiosity_gap"
        }
    ]

    script = writer.generate_dual_column_script(
        working_title="I Built a $10,000 Micro-SaaS in 24 Hours",
        topic="Sovereign AI Micro-SaaS",
        premise="simple webhook handles 10,000 paid transactions",
        stakes="you lose 40% of potential buyers to slow checkouts",
        core_steps=core_steps,
        call_to_action_text="If you want the production template, the link is right below this video."
    )

    assert isinstance(script, ProductionScript)
    assert script.working_title == "I Built a $10,000 Micro-SaaS in 24 Hours"
    assert script.total_words > 0
    assert 130 <= script.avg_pacing_wpm <= 170
    assert 0.0 <= script.retention_health_score <= 100.0

    # Test Markdown formatting
    md = writer.format_markdown_av_table(script)
    assert "| Timecode | Audio (Spoken Word & Sound Design) | Visual" in md
    assert "00:00 - 00:06" in md
    assert "visual_shock" in md


def test_packaging_engine_scoring_and_matrix():
    packager = PackagingEngine()

    # Test curiosity gap scoring
    score_high = packager.score_curiosity_gap("The Secret Reason Why 99% Of YouTubers Fail")
    score_low = packager.score_curiosity_gap("A Very Long And Completely Boring Informative Video Tutorial About Modern Python Web Programming")
    assert score_high > score_low
    assert 1.0 <= score_high <= 10.0

    # Test packaging matrix generation
    matrix = packager.generate_packaging_matrix(
        topic="Next.js 15",
        key_insight="new caching model breaks existing deployments"
    )
    assert len(matrix) == 4
    levers = {c.psychological_lever for c in matrix}
    assert "high_stakes_fomo" in levers
    assert "extreme_novelty" in levers
    assert "counter_intuitive_truth" in levers
    assert "curiosity_loop" in levers

    # Verify Midjourney / DALL-E prompt presence
    for concept in matrix:
        assert len(concept.image_generation_prompt) > 50
        assert "thumbnail" in concept.image_generation_prompt.lower()


def test_outlier_scout_calculation():
    scout = OutlierScout()

    # Normal video (not breakout)
    ratio_normal = scout.calculate_outlier_ratio(views_48h=10000, channel_30d_median_views=8000)
    assert ratio_normal == 1.25

    # Breakout video (> 2.5x)
    trend = scout.evaluate_trend(
        topic="Local LLM Workstations",
        competitor_channel="HardwareUnboxed",
        views_48h=120000,
        channel_median=35000,
        key_angle="Budget $500 rig outperforms M3 Max"
    )
    assert trend.outlier_ratio == 3.43
    assert trend.is_breakout is True


def test_outlier_scout_audience_gaps():
    scout = OutlierScout()
    comments = [
        "Great video, but can you please make a video on setting up local DeepSeek R1 on Windows?",
        "Loved the audio quality!",
        "Why hasn't anyone covered the real power consumption of these cards?",
        "First!"
    ]

    gaps = scout.extract_audience_demand_gaps(comments)
    assert len(gaps) == 2
    concepts = [g["identified_concept"].lower() for g in gaps]
    assert any("deepseek" in c for c in concepts)
    assert any("power consumption" in c for c in concepts)


def test_retention_curve_diagnostics():
    scout = OutlierScout()
    # Simulating a video with a severe drop between second 15 and 20
    datapoints = [
        (0, 100.0),
        (5, 96.0),
        (10, 92.0),
        (15, 90.0),
        (20, 83.0),  # Drop of 7% in 5 seconds!
        (30, 80.0),
        (60, 78.0),
        (65, 71.0),  # Drop of 7% in 5 seconds!
        (90, 68.0)
    ]

    diags = scout.diagnose_retention_curve(datapoints)
    assert len(diags) == 2
    assert diags[0].timestamp_sec == 15
    assert diags[0].drop_percentage == 7.0
    assert "Hook" in diags[0].suspected_cause or "pacing" in diags[0].suspected_cause.lower()


def test_shorts_repurposing():
    writer = RetentionScriptwriter()
    script = writer.generate_dual_column_script(
        working_title="The Ultimate Micro-SaaS Blueprint",
        topic="Micro-SaaS",
        premise="automated backend runs for $0/month",
        stakes="you burn all your runway on unused AWS instances",
        core_steps=[
            {"audio": "Step one is replacing cloud databases with local SQLite replication.", "visual": "Architecture diagram."},
            {"audio": "Step two is setting up GitHub Actions daemon to process transactions.", "visual": "Workflow runner log."}
        ],
        call_to_action_text="Subscribe for more engineering breakdowns."
    )

    repurposer = ShortsRepurposer()
    shorts = repurposer.extract_shorts_from_script(script)

    assert len(shorts) == 2
    assert shorts[0].target_duration_sec <= 60
    assert "Vertical 9:16" in shorts[0].visual_framing_9x16
    assert len(shorts[0].hashtags) >= 2
    assert shorts[0].audio_loop_outro.endswith("...")
