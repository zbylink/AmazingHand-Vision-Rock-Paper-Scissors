"""Hardware-free checks. Never import main or instantiate AmazingHand here."""
import unittest
from types import SimpleNamespace

import numpy as np

from poses import POSES
from vision import calculate_angle, classify_rps, get_stable_gesture


class RecognitionTests(unittest.TestCase):
    def test_right_straight_and_degenerate_angles(self):
        point = lambda x, y: SimpleNamespace(x=x, y=y, z=0)
        center = point(0, 0)
        self.assertAlmostEqual(calculate_angle(point(1, 0), center, point(0, 1)), 90)
        self.assertAlmostEqual(calculate_angle(point(1, 0), center, point(-1, 0)), 180)
        self.assertEqual(calculate_angle(center, center, point(1, 0)), 0)

    def test_labels_and_thumb_exception(self):
        self.assertEqual(classify_rps(False, False, False, False, False), "ROCK")
        self.assertEqual(classify_rps(True, True, True, True, True), "PAPER")
        for thumb in (False, True):
            self.assertEqual(classify_rps(thumb, True, True, False, False), "SCISSORS")
        self.assertEqual(classify_rps(True, False, False, False, False), "UNKNOWN")

    def test_vote_requires_full_window_and_ten_matches(self):
        self.assertEqual(get_stable_gesture(["ROCK"] * 14), "WAITING")
        self.assertEqual(get_stable_gesture(["ROCK"] * 9 + ["UNKNOWN"] * 6), "UNSTABLE")
        self.assertEqual(get_stable_gesture(["ROCK", "UNKNOWN", "ROCK"] * 5), "ROCK")
        self.assertEqual(get_stable_gesture(["UNKNOWN"] * 15), "UNSTABLE")

    def test_all_required_poses_have_eight_finite_targets(self):
        required = {"rock", "paper", "scissors", "middle", "proud_left", "proud_right",
                    "shame", "challenge_open", "challenge_close"}
        self.assertTrue(required.issubset(POSES))
        for name, pose in POSES.items():
            with self.subTest(pose=name):
                self.assertEqual(pose.shape, (8,))
                self.assertTrue(np.isfinite(pose).all())


if __name__ == "__main__":
    unittest.main()
