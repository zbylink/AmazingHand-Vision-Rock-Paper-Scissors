# Development workflow and provenance

This repository packages the author's local RPS application separately from the
Pollen Robotics AmazingHand checkout. The workflow below describes the artifacts
that are actually available, rather than inventing a development timeline.

1. **Understand the upstream platform.** Use AmazingHand assembly, servo-ID, and
   calibration resources. The inspected parent checkout has base commit
   `3e8241074df3436a3044ced4881e3bb2133aa725`.
2. **Explore poses in simulation.** The retained `hand_control_mujoco.py` and the
   original parent directory's `rock_test.py`, `paper_test.py`, and
   `scissors_test.py` show the simulation stage. Only the adapter is included in
   this repository; upstream models and the parent experiments are not bundled.
3. **Build vision independently.** MediaPipe estimates landmarks; `vision.py`
   adds finger-angle rules, RPS classification, temporal voting, and overlays.
4. **Separate targets from transport.** `poses.py` holds named eight-servo target
   arrays; `hand_control.py` converts degrees to radians and sends serial writes.
5. **Integrate the physical interaction.** `main.py` coordinates random moves,
   recognition, outcome evaluation, and proud/shame/challenge feedback.
6. **Record the demonstration.** The supplied original video is retained byte for
   byte. Its six-round README excerpt is reproducible using the media script.
7. **Package for other developers.** Add a dependency snapshot, camera-only
   diagnostic, hardware-free logic checks, media provenance, limitations, and
   upstream credits. The original four application modules are preserved without
   behavioral edits in this publication.

## Validation ladder

Run each stage before proceeding to the next:

```powershell
python -m pip check
python -m unittest discover -s tests -v
python scripts/vision_test.py --camera 0
# These next commands enable torque and move the physical hand:
python test_real_hand.py
python main.py
```

The first two steps do not open a camera or servo connection. Camera and hardware
checks require the developer's equipment; they are not automated release checks.
Inspect and calibrate the hand before running the final two commands.

## What remains to validate

The existing environment imports successfully and passes `pip check`. Its
installed versions are recorded, but a fresh install on another machine has not
been verified. The historical video is demonstration evidence, not a timestamped
test log tying every installed package to the recording. No performance,
reliability, or recognition-accuracy benchmark is claimed.

## Attribution boundaries

The project-specific contribution is the RPS interaction pipeline and integration,
not the upstream hand design, MediaPipe model, or rustypot driver. The original
repository's MIT license is retained. Upstream-derived material remains subject
to the applicable upstream terms; `UPSTREAM-Apache-2.0.txt` preserves the license
text from the inspected AmazingHand parent checkout. See the README credits and
upstream repository for mechanical-design licensing and further notices.
