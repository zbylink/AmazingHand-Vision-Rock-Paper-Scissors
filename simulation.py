"""Camera-driven AmazingHand simulation. No serial connection is opened."""
import argparse
from collections import deque
from pathlib import Path
import time

import cv2
import mediapipe as mp
import numpy as np

from poses import POSES
from vision import is_finger_open, is_thumb_open, classify_rps, get_stable_gesture


DEFAULT_MODEL = (Path(__file__).resolve().parent / "external/AmazingHand/Demo/"
                 "AHSimulation/AHSimulation/AH_Left/mjcf/scene.xml")
ACTUATORS = [f"finger{finger}_motor{motor}" for finger in range(1, 5)
             for motor in (1, 2)]


def analyze_landmarks(landmarks):
    """Use the same angles and RPS rules as the physical demo."""
    thumb, a1, a2 = is_thumb_open(landmarks)
    fingers = [is_finger_open(landmarks, *triplet) for triplet in
               ((5, 6, 7), (9, 10, 11), (13, 14, 15), (17, 18, 19))]
    gesture = classify_rps(thumb, *(state for state, _ in fingers))
    # AmazingHand has index, middle, ring and thumb; no independent pinky.
    angles = np.array([fingers[0][1], fingers[1][1], fingers[2][1], min(a1, a2)])
    return angles, gesture


def finger_targets(angles):
    """Interpolate each finger pair between stored closed and open poses."""
    angles = np.asarray(angles, dtype=float)
    if angles.shape != (4,) or not np.isfinite(angles).all():
        raise ValueError("Expected four finite angles: index, middle, ring, thumb")
    closed = np.array([80.0, 80.0, 80.0, 70.0])
    opened = np.array([160.0, 160.0, 160.0, 150.0])
    amount = np.repeat(np.clip((angles - closed) / (opened - closed), 0, 1), 2)
    return POSES["rock"] * (1 - amount) + POSES["paper"] * amount


def load_model(path):
    import mujoco

    path = Path(path).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Scene not found: {path}. See README simulation setup or use --model.")
    model = mujoco.MjModel.from_xml_path(str(path))
    ids = np.array([mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, name)
                    for name in ACTUATORS])
    if model.nu != 8 or (ids < 0).any():
        raise ValueError("Expected eight named AmazingHand finger actuators")
    data = mujoco.MjData(model)
    zero = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_KEY, "zero")
    if zero >= 0:
        mujoco.mj_resetDataKeyframe(model, data, zero)
    write_targets(model, data, ids, POSES["middle"])
    mujoco.mj_forward(model, data)
    return model, data, ids


def write_targets(model, data, ids, degrees):
    targets = np.deg2rad(degrees)
    limited = model.actuator_ctrllimited[ids].astype(bool)
    ranges = model.actuator_ctrlrange[ids]
    targets = np.where(limited, np.clip(targets, ranges[:, 0], ranges[:, 1]), targets)
    data.ctrl[ids] = targets


def run(args):
    import mujoco
    import mujoco.viewer

    model, data, ids = load_model(args.model)
    if args.check_model:
        for name in ("middle", "rock", "paper", "scissors"):
            write_targets(model, data, ids, POSES[name])
            for _ in range(100):
                mujoco.mj_step(model, data)
            if not np.isfinite(data.qpos).all():
                raise RuntimeError(f"Non-finite simulation state at {name}")
        print("Model check passed: eight actuators; four poses; 400 physics steps.")
        return

    cap = cv2.VideoCapture(args.camera)
    hands = None
    try:
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open camera {args.camera}")
        hands = mp.solutions.hands.Hands(
            max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
        history = deque(maxlen=15)
        target = POSES["middle"].copy()
        current = target.copy()
        previous = time.monotonic()
        last_hand = previous
        window = "AmazingHand - camera to simulation"
        with mujoco.viewer.launch_passive(model, data) as viewer:
            with viewer.lock():
                viewer.cam.lookat[:] = [0, 0, 0.10]
                viewer.cam.distance = 0.55
                viewer.cam.azimuth = 150
                viewer.cam.elevation = -20
            print(f"Mode: {args.mode}. Press Q in the camera window or close either window to exit.")
            while viewer.is_running():
                ok, frame = cap.read()
                if not ok:
                    raise RuntimeError("Camera stopped delivering frames")
                result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                now = time.monotonic()
                dt = min(now - previous, 0.1)
                previous = now
                gesture = "UNKNOWN"
                angles = None
                if result.multi_hand_landmarks:
                    hand = result.multi_hand_landmarks[0]
                    angles, gesture = analyze_landmarks(hand.landmark)
                    last_hand = now
                    mp.solutions.drawing_utils.draw_landmarks(
                        frame, hand, mp.solutions.hands.HAND_CONNECTIONS)
                else:
                    history.clear()
                history.append(gesture)
                stable = get_stable_gesture(history)
                if args.mode == "fingers" and angles is not None:
                    target = finger_targets(angles)
                elif args.mode == "rps" and stable in ("ROCK", "PAPER", "SCISSORS"):
                    target = POSES[stable.lower()].copy()
                if now - last_hand > 0.5:
                    target = POSES["middle"].copy()
                current += (1 - np.exp(-dt / 0.12)) * (target - current)
                with viewer.lock():
                    write_targets(model, data, ids, current)
                    for _ in range(max(1, round(dt / model.opt.timestep))):
                        mujoco.mj_step(model, data)
                viewer.sync()
                cv2.putText(frame, f"{args.mode} | Gesture: {gesture} | Stable: {stable}",
                            (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                if angles is not None:
                    for row, (name, angle) in enumerate(zip(("Index", "Middle", "Ring", "Thumb"), angles)):
                        cv2.putText(frame, f"{name}: {angle:.0f} deg", (12, 55 + row * 24),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1)
                cv2.imshow(window, frame)
                if cv2.waitKey(1) & 0xFF in (ord("q"), ord("Q")):
                    break
                if cv2.getWindowProperty(window, cv2.WND_PROP_VISIBLE) < 1:
                    break
    finally:
        cap.release()
        if hands is not None:
            hands.close()
        cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--mode", choices=("fingers", "rps"), default="fingers")
    parser.add_argument("--check-model", action="store_true", help="Check physics without camera or GUI")
    args = parser.parse_args()
    try:
        run(args)
    except KeyboardInterrupt:
        pass
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
