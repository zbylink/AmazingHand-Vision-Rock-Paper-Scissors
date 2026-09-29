import time
import numpy as np

from rustypot import Scs0009PyController

from poses import POSES


class AmazingHand:


    def __init__(self):

        self.controller = Scs0009PyController(
            serial_port="COM9",
            baudrate=1000000,
            timeout=2,
        )

        # enable torque
        for i in range(1,9):
            self.controller.write_torque_enable(
                i,
                1
            )

        print("AmazingHand connected")


    def move(self, pose_name):

        if pose_name not in POSES:
            raise ValueError(
                f"Unknown pose {pose_name}"
            )


        deg = POSES[pose_name]

        print(
            "Moving:",
            pose_name
        )


        for i, angle in enumerate(deg):

            servo_id = i + 1

            # degree -> rad
            rad = np.deg2rad(angle)

            self.controller.write_goal_position(
                servo_id,
                rad
            )


            time.sleep(0.005)


    def smooth_move(self, start_pose, end_pose, duration=1.0, steps=50):

        start_deg = POSES[start_pose]
        end_deg = POSES[end_pose]


        print(
            f"Smooth move: {start_pose} -> {end_pose}"
        )


        for i in range(steps + 1):

            ratio = i / steps


            # 线性插值
            current_deg = (
                start_deg * (1-ratio)
                +
                end_deg * ratio
            )


            for j, angle in enumerate(current_deg):

                servo_id = j + 1

                self.controller.write_goal_position(
                    servo_id,
                    np.deg2rad(angle)
                )


            time.sleep(
                duration / steps
            )



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



    def shame(self):

        self.move("rock")
        time.sleep(0.3)

        self.smooth_move(
            "rock",
            "shame",
            duration=0.8
        )
            


    def challenge(self):

        for _ in range(2):

            self.move(
                "challenge_open"
            )

            time.sleep(0.3)

            self.move(
                "challenge_close"
            )

            time.sleep(0.2)



    def start(self):
        pass


    def stop(self):

        for i in range(1,9):

            self.controller.write_torque_enable(
                i,
                2
            )

        print(
            "AmazingHand stopped"
        )