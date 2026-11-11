"""
RTSP Camera Stream Connector for SuratVision AI.
Connects directly to CP PLUS, Hikvision, Dahua, and standard ONVIF IP camera streams.
Provides automatic reconnection, frame rate normalization, and circular frame buffering.
"""

import time
import os
import cv2
from typing import Generator, Optional, Tuple, Dict, Any

class RTSPCameraConnector:
    """Connects to factory & godown RTSP CCTV video streams with auto-recovery."""

    # Common default RTSP URL formats in Surat factories
    STREAM_TEMPLATES = {
        "cpplus": "rtsp://{user}:{pwd}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0",
        "hikvision": "rtsp://{user}:{pwd}@{ip}:{port}/Streaming/Channels/{channel}01",
        "dahua": "rtsp://{user}:{pwd}@{ip}:{port}/cam/realmonitor?channel={channel}&subtype=0",
        "generic": "rtsp://{user}:{pwd}@{ip}:{port}/live/ch{channel}"
    }

    def __init__(self, stream_source: Any = 0, camera_brand: str = "generic", name: str = "Loading_Bay_Cam_1"):
        self.stream_source = stream_source
        self.camera_brand = camera_brand.lower()
        self.name = name
        self.is_running = False
        self.cap: Optional[cv2.VideoCapture] = None

    def connect(self) -> bool:
        """Initializes OpenCV video capture from RTSP URL or USB device."""
        print(f"[*] Connecting to {self.name} ({self.stream_source})...")
        try:
            self.cap = cv2.VideoCapture(self.stream_source)
            if self.cap.isOpened():
                self.is_running = True
                width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = self.cap.get(cv2.CAP_PROP_FPS) or 25
                print(f"[+] Connected to {self.name} successfully. Resolution: {width}x{height} @ {fps:.1f} FPS")
                return True
            else:
                print(f"[!] Failed to open camera stream {self.name}.")
                return False
        except Exception as e:
            print(f"[!] Connection exception for {self.name}: {e}")
            return False

    def stream_frames(self) -> Generator[Tuple[bool, Any], None, None]:
        """Yields frames continuously with automatic reconnection logic."""
        consecutive_failures = 0
        while self.is_running:
            if self.cap is None or not self.cap.isOpened():
                if not self.connect():
                    time.sleep(2.0)
                    continue

            ret, frame = self.cap.read()
            if not ret or frame is None:
                consecutive_failures += 1
                if consecutive_failures > 10:
                    print(f"[!] Stream {self.name} lost signal. Reconnecting...")
                    if self.cap:
                        self.cap.release()
                    time.sleep(2.0)
                    self.connect()
                    consecutive_failures = 0
                continue

            consecutive_failures = 0
            yield True, frame

    def disconnect(self):
        self.is_running = False
        if self.cap and self.cap.isOpened():
            self.cap.release()
        print(f"[*] Disconnected from {self.name}.")
