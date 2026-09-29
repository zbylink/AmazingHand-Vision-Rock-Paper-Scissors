import time
import threading
import numpy as np

import mujoco
import mujoco.viewer

from poses import POSES



class AmazingHand:

    def __init__(self):

        XML_PATH = (
            "../AHSimulation/"
            "AHSimulation/"
            "AH_Left/mjcf/scene.xml"
        )

        self.model = mujoco.MjModel.from_xml_path(XML_PATH)
        self.data = mujoco.MjData(self.model)

        # start zero pose
        self.data.qpos[:] = self.model.key_qpos[0]

        mujoco.mj_forward(
            self.model,
            self.data
        )

        self.viewer = None
        self.running = False
        self.thread = None



    def move(self, pose_name):

        if pose_name not in POSES:
            raise ValueError(
                f"Unknown pose {pose_name}"
            )


        deg = POSES[pose_name]

        rad = np.deg2rad(deg)


        print(
            f"Moving to {pose_name}"
        )

        self.data.ctrl[:] = rad


    def middle(self):
        self.move("middle")


    def rock(self):
        self.move("rock")


    def paper(self):
        self.move("paper")


    def scissors(self):
        self.move("scissors")


    def proud(self):

        self.move("proud_left")
        time.sleep(0.2)

        self.move("proud_right")
        time.sleep(0.2)

        self.move("proud_left")
        time.sleep(0.2)

        self.move("proud_right")
        time.sleep(0.2)


    def shame(self):
        self.move("shame")


    def challenge(self):

        for _ in range(3):

            self.move("challenge_open")
            time.sleep(0.25)

            self.move("challenge_close")
            time.sleep(0.25)


    def _simulation_loop(self):

        with mujoco.viewer.launch_passive(
            self.model,
            self.data
        ) as viewer:

            self.viewer = viewer

            print(
                "MuJoCo viewer started"
            )


            while viewer.is_running() and self.running:

                mujoco.mj_step(
                    self.model,
                    self.data
                )

                viewer.sync()

                time.sleep(0.002)

        self.viewer = None
        

    def start(self):

        self.running = True

        self.thread = threading.Thread(
            target=self._simulation_loop,
            daemon=True
        )

        self.thread.start()


    def stop(self):

        self.running = False