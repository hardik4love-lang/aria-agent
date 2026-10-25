"""
Outlier Scout & Retention Analytics for ARIA.
Detects breakout viral topics and performs telemetry diagnostics on audience drop-offs.
"""

from typing import List, Dict, Any, Tuple
import re
from aria.creator.models import TrendOutlier, RetentionDiagnostic


class OutlierScout:
    """Specialized engine for market outlier detection and retention curve diagnostics."""

    OUTLIER_BREAKOUT_THRESHOLD = 2.5
    SHARP_DROP_THRESHOLD_PERCENT = 5.0

    def calculate_outlier_ratio(self, views_48h: int, channel_30d_median_views: int) -> float:
        """
        Calculates the Outlier Ratio = (Views in first 48h) / (Channel 30-day median views).
        If ratio >= 2.5x, the topic has exceptional organic viral pull independent of channel subscriber baseline.
        """
        if channel_30d_median_views <= 0:
            return 1.0
        return round(views_48h / channel_30d_median_views, 2)

    def evaluate_trend(
        self,
        topic: str,
        competitor_channel: str,
        views_48h: int,
        channel_median: int,
        key_angle: str
    ) -> TrendOutlier:
        """Evaluates a competitor upload and classifies whether it is a breakout topic."""
        ratio = self.calculate_outlier_ratio(views_48h, channel_median)
        is_breakout = ratio >= self.OUTLIER_BREAKOUT_THRESHOLD

        return TrendOutlier(
            topic=topic,
            competitor_channel=competitor_channel,
            views_48h=views_48h,
            channel_30d_median_views=channel_median,
            outlier_ratio=ratio,
            is_breakout=is_breakout,
            recommended_angle=key_angle
        )

    def extract_audience_demand_gaps(self, comments: List[str]) -> List[Dict[str, Any]]:
        """
        Parses audience comment corpus for unfulfilled demand questions:
        Detects 'why did', 'can you make a video on', 'how do you', 'what happens if'.
        """
        demand_patterns = [
            r"(?:can you|please|could you)\s+(?:make|do|cover)\s+(?:a video on|an episode about|something on)\s+([^?.!]+)",
            r"(?:why (?:hasn't|has no one|doesn't))\s+([^?.!]+)",
            r"(?:what happens (?:if|when))\s+([^?.!]+)",
            r"(?:how (?:do you|can we|does one))\s+([^?.!]+)"
        ]

        extracted_gaps: List[Dict[str, Any]] = []
        for comment in comments:
            for pat in demand_patterns:
                match = re.search(pat, comment, re.IGNORECASE)
                if match:
                    extracted_gaps.append({
                        "raw_comment": comment,
                        "identified_concept": match.group(1).strip()
                    })
                    break

        return extracted_gaps

    def diagnose_retention_curve(
        self,
        retention_datapoints: List[Tuple[int, float]]
    ) -> List[RetentionDiagnostic]:
        """
        Scans a sequence of (timestamp_seconds, retention_percentage) datapoints.
        Detects sudden drop-offs (>= 5.0% loss over <= 5 seconds) and flags them for editing intervention.
        """
        diagnostics: List[RetentionDiagnostic] = []
        sorted_points = sorted(retention_datapoints, key=lambda x: x[0])

        for i in range(len(sorted_points) - 1):
            t1, r1 = sorted_points[i]
            t2, r2 = sorted_points[i + 1]

            time_diff = t2 - t1
            drop = r1 - r2

            if time_diff <= 6 and drop >= self.SHARP_DROP_THRESHOLD_PERCENT:
                # Classify cause based on timestamp
                if t1 < 30:
                    cause = "Hook failed to deliver on thumbnail promise or had dead air / slow intro."
                    fix = "Eliminate opening throat-clearing; punch into core premise within 4 seconds."
                elif 60 <= t1 <= 180:
                    cause = "Expository slump: pacing dragged without pattern interrupts or visual changes."
                    fix = "Insert B-roll montage, sound effect beat, or split-screen demonstration."
                else:
                    cause = "Mid-video momentum collapse or prolonged sponsored segment without action."
                    fix = "Tighten narrative; keep sponsor integration under 45 seconds with continuous visual demo."

                diagnostics.append(RetentionDiagnostic(
                    timestamp_sec=t1,
                    drop_percentage=round(drop, 2),
                    suspected_cause=cause,
                    corrective_action=fix
                ))

        return diagnostics
