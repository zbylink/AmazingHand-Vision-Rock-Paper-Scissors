import time
import random
import cv2

from hand_control import AmazingHand
from vision import RPSVision


hand = AmazingHand()
vision = RPSVision()


def update_camera_window(duration):

    start = time.time()

    while time.time() - start < duration:

        frame, _ = vision.read()

        if frame is not None:
            cv2.imshow(
                "RPS Vision",
                frame
            )

        cv2.waitKey(1)

update_camera_window(1)

hand.start()
vision.start()
update_camera_window(1)

moves = ["rock", "paper", "scissors"]

try:

    for round_num in range(20):

        print(f"\n===== Round {round_num + 1} =====")

        # ==========================================
        # 1. 回到中间位置
        # ==========================================

        hand.middle()
        update_camera_window(0.5)

        # ==========================================
        # 2. 机器人随机出拳
        # ==========================================

        t1 = time.time()

        robot_move = random.choice(moves)

        print(
            f"Robot chose: {robot_move}, "
            f"time={time.time()-t1:.3f}s"
        )

        hand.move(robot_move)
        update_camera_window(1)

        # ==========================================
        # 3. 初始化，并等待人类出拳
        # ==========================================
        
        human_move = None

        print("Please show your hand...")

        while True:

            frame, stable_gesture = vision.read()

            if frame is None:
                print("无法读取摄像头")
                break

            cv2.imshow(
                "RPS Vision",
                frame
            )

            if stable_gesture in [
                "ROCK",
                "PAPER",
                "SCISSORS"
            ]:
                human_move = stable_gesture.lower()

                print(
                    "Human detected:",
                    human_move,
                    "delay:",
                    time.time()-t1,
                    "s"
                )

                # 本轮识别结束，立即清空历史
                vision.reset()

                break

            key = cv2.waitKey(1)

            if key == ord("q") or key == ord("Q"):
                raise KeyboardInterrupt

        if human_move is None:
            print("没有成功识别人类手势")
            continue

        print("Human chose:", human_move)

        # ==========================================
        # 4. 判断胜负
        # ==========================================

        if robot_move == human_move:

            print("Draw!")

            hand.middle()
            update_camera_window(0.5)

            # 平局：
            # 不执行 Challenge
            # 直接进入下一轮

        elif (
            (robot_move == "rock" and human_move == "scissors")
            or
            (robot_move == "paper" and human_move == "rock")
            or
            (robot_move == "scissors" and human_move == "paper")
        ):

            print("Robot wins!")

            # 得意
            hand.proud()
            update_camera_window(0.5)

            # 回中
            hand.middle()
            update_camera_window(0.5)

            # 挑战
            hand.challenge()
            update_camera_window(0.5)

        else:

            print("Robot loses!")

            # 自愧不如
            hand.shame()
            update_camera_window(1)

            # 回中
            hand.middle()
            update_camera_window(0.5)

            # 挑战
            hand.challenge()
            update_camera_window(0.5)

finally:

    # ==========================================
    # 5. 程序结束，释放资源
    # ==========================================

    vision.stop()

    hand.middle()
    update_camera_window(1)

    hand.stop()