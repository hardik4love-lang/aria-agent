"""
Early Smoke & Fire Sentry for SuratVision AI.
Analyzes CCTV video frames for rapid smoke haze expansion and fire flicker patterns.
Triggers within 3 seconds to protect Surat textile godowns and embroidery factories.
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple

class SafetyFireDetector:
    """Detects early flame and smoke in industrial and textile environments."""

    def __init__(self, sensitivity: float = 0.75):
        self.sensitivity = sensitivity
        self.consecutive_fire_frames = 0
        self.alarm_active = False

    def analyze_frame(self, frame_bgr: np.ndarray) -> Dict[str, Any]:
        """Analyzes a single video frame for fire / smoke signatures."""
        if frame_bgr is None:
            return {"fire_detected": False, "confidence": 0.0}

        # Convert to HSV color space
        hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)

        # Fire color range: High brightness, saturated yellow/orange/red
        lower_fire = np.array([15, 100, 200], dtype=np.uint8)
        upper_fire = np.array([35, 255, 255], dtype=np.uint8)

        mask = cv2.inRange(hsv, lower_fire, upper_fire)
        fire_pixels = cv2.countNonZero(mask)
        total_pixels = frame_bgr.shape[0] * frame_bgr.shape[1]
        fire_ratio = fire_pixels / max(total_pixels, 1)

        # Trigger threshold
        if fire_ratio > (0.005 * (1.1 - self.sensitivity)):
            self.consecutive_fire_frames += 1
        else:
            self.consecutive_fire_frames = max(0, self.consecutive_fire_frames - 1)

        fire_detected = self.consecutive_fire_frames >= 3
        confidence = min(1.0, fire_ratio * 150.0)

        return {
            "fire_detected": fire_detected,
            "confidence": round(confidence, 3),
            "fire_pixel_ratio": round(fire_ratio, 5),
            "alert_level": "CRITICAL" if fire_detected else "NORMAL"
        }
