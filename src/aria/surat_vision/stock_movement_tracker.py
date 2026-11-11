"""
Stock Movement & Parcel/Taka Counter for SuratVision AI.
Tracks parcel / bale / roll loading and unloading into tempos from factory loading bays.
Maintains continuous count and detects count discrepancies against dispatch challans.
"""

import time
import math
from typing import Dict, Any, List, Tuple

class StockMovementTracker:
    """Detects and counts parcels/bales moved across a virtual tripwire boundary."""

    def __init__(self, direction_threshold_px: int = 50):
        self.direction_threshold_px = direction_threshold_px
        self.total_loaded = 0
        self.total_unloaded = 0
        self.active_tracks = {}
        self.dispatch_challan_count = 0
        self.alert_discrepancy = False

    def set_dispatch_target(self, expected_parcel_count: int):
        """Sets the expected parcel count from the ERP / dispatch challan."""
        self.dispatch_challan_count = expected_parcel_count
        self.total_loaded = 0
        self.total_unloaded = 0
        self.alert_discrepancy = False
        print(f"[*] Dispatch challan target set: {expected_parcel_count} parcels.")

    def process_detections(self, detected_boxes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processes bounding boxes detected in the loading bay.
        Each box: {"id": int, "label": "parcel/taka_roll", "bbox": [x1, y1, x2, y2], "confidence": float}
        """
        current_time = time.time()
        for obj in detected_boxes:
            track_id = obj.get("id")
            bbox = obj.get("bbox", [0, 0, 0, 0])
            cy = (bbox[1] + bbox[3]) / 2 # vertical center

            if track_id not in self.active_tracks:
                self.active_tracks[track_id] = {"start_y": cy, "last_y": cy, "first_seen": current_time}
            else:
                self.active_tracks[track_id]["last_y"] = cy

                # Check if crossed crossing line (loading into tempo)
                delta_y = cy - self.active_tracks[track_id]["start_y"]
                if delta_y > self.direction_threshold_px and not self.active_tracks[track_id].get("counted"):
                    self.total_loaded += 1
                    self.active_tracks[track_id]["counted"] = True
                    print(f"[+] Parcel loaded. Total count: {self.total_loaded}")

        # Check for theft / discrepancy against challan
        if self.dispatch_challan_count > 0 and self.total_loaded > self.dispatch_challan_count:
            self.alert_discrepancy = True

        return {
            "total_loaded": self.total_loaded,
            "total_unloaded": self.total_unloaded,
            "challan_target": self.dispatch_challan_count,
            "discrepancy_detected": self.alert_discrepancy,
            "discrepancy_delta": self.total_loaded - self.dispatch_challan_count if self.alert_discrepancy else 0
        }
