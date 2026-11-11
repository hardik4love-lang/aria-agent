"""
Unit and Integration Tests for SuratVision AI CCTV Sentry Engine.
"""

import pytest
import numpy as np
from aria.surat_vision.safety_fire_detector import SafetyFireDetector
from aria.surat_vision.stock_movement_tracker import StockMovementTracker
from aria.surat_vision.rtsp_connector import RTSPCameraConnector

def test_rtsp_stream_templates():
    templates = RTSPCameraConnector.STREAM_TEMPLATES
    assert "cpplus" in templates
    assert "hikvision" in templates
    assert "dahua" in templates
    
    # Verify parameter formatting
    cpplus_url = templates["cpplus"].format(user="admin", pwd="pwd", ip="192.168.1.100", port=554, channel=1)
    assert "cam/realmonitor" in cpplus_url
    assert "192.168.1.100" in cpplus_url

def test_fire_detector_benign_frame():
    detector = SafetyFireDetector(sensitivity=0.8)
    # Neutral grey frame
    clean_frame = np.full((480, 640, 3), 128, dtype=np.uint8)
    result = detector.analyze_frame(clean_frame)
    assert result["fire_detected"] is False
    assert result["alert_level"] == "NORMAL"
    assert result["confidence"] == 0.0

def test_fire_detector_flame_detection():
    detector = SafetyFireDetector(sensitivity=0.8)
    # Synthetic fire frame: Bright saturated orange/yellow in BGR
    # BGR format: B=20, G=150, R=255 converts to high-saturation HSV in yellow/orange range
    fire_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Fill a 200x200 patch with intense fire-like color
    fire_frame[100:300, 200:400] = [20, 180, 255]

    # Process 3 consecutive frames to trigger the 3s temporal confirmation
    for _ in range(3):
        res = detector.analyze_frame(fire_frame)

    assert res["fire_detected"] is True
    assert res["alert_level"] == "CRITICAL"
    assert res["confidence"] > 0.50

def test_stock_movement_tracker_normal_dispatch():
    tracker = StockMovementTracker(direction_threshold_px=40)
    tracker.set_dispatch_target(expected_parcel_count=5)
    assert tracker.dispatch_challan_count == 5

    # Simulate 5 parcels moving across the threshold line
    for i in range(1, 6):
        # Frame 1: start at y=100
        tracker.process_detections([{"id": i, "label": "taka_roll", "bbox": [50, 100, 150, 200]}])
        # Frame 2: move to y=160 (delta = 60 > 40)
        res = tracker.process_detections([{"id": i, "label": "taka_roll", "bbox": [50, 160, 150, 260]}])

    assert res["total_loaded"] == 5
    assert res["discrepancy_detected"] is False
    assert res["discrepancy_delta"] == 0

def test_stock_movement_tracker_theft_discrepancy():
    tracker = StockMovementTracker(direction_threshold_px=40)
    tracker.set_dispatch_target(expected_parcel_count=2)

    # Load 3 parcels (1 extra beyond challan target)
    for i in range(1, 4):
        tracker.process_detections([{"id": i, "label": "parcel_box", "bbox": [10, 50, 80, 120]}])
        res = tracker.process_detections([{"id": i, "label": "parcel_box", "bbox": [10, 110, 80, 180]}])

    assert res["total_loaded"] == 3
    assert res["challan_target"] == 2
    assert res["discrepancy_detected"] is True
    assert res["discrepancy_delta"] == 1
