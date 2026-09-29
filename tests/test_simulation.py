import unittest
from types import SimpleNamespace

import numpy as np

from poses import POSES
from simulation import finger_targets, analyze_landmarks
from vision import calculate_angle


class SimulationTests(unittest.TestCase):
    def test_open_closed_and_clipped_targets(self):
        np.testing.assert_allclose(finger_targets([180] * 4), POSES["paper"])
        np.testing.assert_allclose(finger_targets([0] * 4), POSES["rock"])
        np.testing.assert_allclose(finger_targets([120, 120, 120, 110]),
                                   (POSES["paper"] + POSES["rock"]) / 2)

    def test_thumb_moves_independently(self):
        targets = finger_targets([80, 80, 80, 150])
        np.testing.assert_allclose(targets[:6], POSES["rock"][:6])
        np.testing.assert_allclose(targets[6:], POSES["paper"][6:])

    def test_invalid_targets(self):
        for value in ([90] * 3, [90, 90, 90, float("nan")]):
            with self.assertRaises(ValueError):
                finger_targets(value)

    def test_angles_under_3d_rotations_translation_and_scale(self):
        points = np.array([[1.0, 0.2, 0.3], [0.1, 0.1, 0], [-0.3, 0.8, 0.2]])
        def angle(xyz):
            return calculate_angle(*(SimpleNamespace(x=x, y=y, z=z) for x, y, z in xyz))
        expected = angle(points)
        rng = np.random.default_rng(42)
        for _ in range(100):
            rotation, _ = np.linalg.qr(rng.normal(size=(3, 3)))
            if np.linalg.det(rotation) < 0:
                rotation[:, 0] *= -1
            transformed = 2.3 * points @ rotation.T + [3, -5, 8]
            self.assertAlmostEqual(angle(transformed), expected, places=9)

    def test_scissors_label_survives_landmark_rotation(self):
        points = np.zeros((21, 3))
        # Straight index/middle, bent ring/pinky; scissors ignores thumb.
        for start, opened in ((5, True), (9, True), (13, False), (17, False)):
            points[start] = [0, 0, 0]
            points[start + 1] = [1, 0, 0]
            points[start + 2] = [2, 0, 0] if opened else [1, 1, 0]
        for theta in np.linspace(0, 2 * np.pi, 25):
            c, s = np.cos(theta), np.sin(theta)
            rotation = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
            landmarks = [SimpleNamespace(x=x, y=y, z=z) for x, y, z in points @ rotation.T]
            _, label = analyze_landmarks(landmarks)
            self.assertEqual(label, "SCISSORS")


if __name__ == "__main__":
    unittest.main()
