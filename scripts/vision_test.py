"""Preview the current threaded vision API without opening a servo connection."""
import argparse
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import cv2
from vision import RPSVision


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0)
    args = parser.parse_args()
    vision = RPSVision(camera_id=args.camera)
    try:
        vision.start()
        deadline = time.monotonic() + 10
        while True:
            frame, _ = vision.read()
            if frame is None:
                if time.monotonic() > deadline:
                    raise RuntimeError("No initial frame within 10 seconds")
                time.sleep(0.01)
                continue
            cv2.imshow("Vision-only RPS", frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
                break
    finally:
        vision.stop()


if __name__ == "__main__":
    main()
