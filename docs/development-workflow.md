# Development workflow

1. **Simulation:** explore the AmazingHand model and tune rock, paper, and scissors poses.
2. **Vision:** estimate hand landmarks, calculate finger angles, classify gestures, and reduce flicker with temporal voting.
3. **Camera-to-simulation:** test finger following and stable RPS poses with `simulation.py` before connecting the physical hand.
4. **Hardware integration:** use named poses with rustypot serial control, then add the game loop and expressive feedback.
5. **Iteration:** compare the camera view and robot response, adjust poses and thresholds, and record the demonstration.

## Validation sequence

```powershell
python -m pip check
python -m unittest discover -s tests -v
python scripts/vision_test.py --camera 0
python simulation.py --check-model
python simulation.py --mode fingers
python simulation.py --mode rps
# After configuring and calibrating the physical hand:
python test_real_hand.py
python main.py
```

The simulation uses the upstream AmazingHand model assets; setup is covered in the README. The four core physical-demo modules retain their original behavior. `simulation.py` provides a separate development entry point and never creates a servo controller.

The camera and simulation checks help test recognition and target mapping. Calibration and motion clearance must still be checked on the real hand. Upstream hardware designs, models, and libraries are credited in the README.
