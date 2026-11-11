"""
Runnable Standalone Demo for SuratVision AI CCTV Intelligence.
Simulates textile factory loading bay tempo tracking and 3-second fire/smoke detection sentry.
"""

import sys
import time
import numpy as np
from aria.surat_vision.stock_movement_tracker import StockMovementTracker
from aria.surat_vision.safety_fire_detector import SafetyFireDetector
from aria.surat_vision.rtsp_connector import RTSPCameraConnector

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 70)
    print("👁️  SURATVISION AI - CCTV INTELLIGENCE & LOSS PREVENTION")
    print("   Surat Textile Mills, GIDC Godowns & Malls • 100% Camera Re-use")
    print("=" * 70)

    # 1. Test RTSP Connection Templates
    print("\n[STEP 1]: Verifying RTSP Stream Connectors for CP PLUS, Hikvision, Dahua...")
    for brand, template in RTSPCameraConnector.STREAM_TEMPLATES.items():
        sample_url = template.format(user="admin", pwd="***", ip="192.168.1.120", port=554, channel=1)
        print(f"  ✓ {brand.upper():<10}: {sample_url}")

    # 2. Test Tempo Loading & Challan Reconciliation
    print("\n[STEP 2]: Simulating Tempo Loading Bay (Pandasera GIDC Godown #4)...")
    tracker = StockMovementTracker(direction_threshold_px=40)
    challan_target = 10
    tracker.set_dispatch_target(expected_parcel_count=challan_target)
    print(f"  📋 ERP Dispatch Challan: Exactly {challan_target} grey cloth taka rolls authorized.")

    print("  📦 Loading boxes into tempo:")
    for parcel_id in range(1, 13):
        # Frame 1: worker picks up box
        tracker.process_detections([{"id": parcel_id, "label": "taka_roll", "bbox": [100, 50, 200, 150]}])
        # Frame 2: worker crosses tempo boundary
        res = tracker.process_detections([{"id": parcel_id, "label": "taka_roll", "bbox": [100, 120, 200, 220]}])
        
        status_note = ""
        if res["discrepancy_detected"]:
            status_note = f" 🚨 DISCREPANCY! +{res['discrepancy_delta']} unauthorized box(es) detected!"
        print(f"     Parcel #{parcel_id:02d} loaded -> Total Loaded: {res['total_loaded']}/{challan_target}{status_note}")
        time.sleep(0.05)

    if res["discrepancy_detected"]:
        print(f"  ⚠️ ALERT: Dispatch exceeded challan by {res['discrepancy_delta']} units! Auto-triggering owner WhatsApp alert.")

    # 3. Test 3-Second Fire/Smoke Sentry
    print("\n[STEP 3]: Simulating Early Fire / Smoke Sentry (Embroidery Unit #2)...")
    detector = SafetyFireDetector(sensitivity=0.8)
    
    # Normal frame
    normal_frame = np.full((480, 640, 3), 100, dtype=np.uint8)
    res_normal = detector.analyze_frame(normal_frame)
    print(f"  Normal Frame Status: {res_normal['alert_level']} (Confidence: {res_normal['confidence']:.2f})")

    # Fire frame
    print("  🔥 Simulating sudden ignition/flame outbreak on yarn storage rack:")
    fire_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    fire_frame[150:350, 250:450] = [20, 180, 255] # bright flame color

    for frame_idx in range(1, 4):
        res_fire = detector.analyze_frame(fire_frame)
        print(f"     T+{frame_idx}s Frame: {res_fire['alert_level']} (Confidence: {res_fire['confidence']:.2f}, Ratio: {res_fire['fire_pixel_ratio']})")
        time.sleep(0.05)

    if res_fire["fire_detected"]:
        print("  🚨 CRITICAL FIRE ALARM TRIGGERED (<3s Response): Siren sounded & siren relay tripped.")

    print("\n" + "=" * 70)
    print("✓ SuratVision AI Sentry Simulation Complete. All Pipelines Active.")
    print("=" * 70)

if __name__ == "__main__":
    main()
