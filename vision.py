import cv2
import mediapipe as mp
import math
import threading
from collections import deque


# ============================================================
# 1. 几何计算：计算三个关键点形成的夹角
# ============================================================

def calculate_angle(a, b, c):
    """
    计算 a-b-c 三个点形成的夹角
    返回角度，范围 0~180°
    """

    ba = [
        a.x - b.x,
        a.y - b.y,
        a.z - b.z
    ]

    bc = [
        c.x - b.x,
        c.y - b.y,
        c.z - b.z
    ]

    dot_product = sum(
        ba[i] * bc[i]
        for i in range(3)
    )

    magnitude_ba = math.sqrt(
        sum(x * x for x in ba)
    )

    magnitude_bc = math.sqrt(
        sum(x * x for x in bc)
    )

    if magnitude_ba == 0 or magnitude_bc == 0:
        return 0

    cosine = dot_product / (
        magnitude_ba * magnitude_bc
    )

    cosine = max(-1.0, min(1.0, cosine))

    angle = math.degrees(
        math.acos(cosine)
    )

    return angle


# ============================================================
# 2. 判断普通手指是否伸直
# ============================================================

def is_finger_open(landmarks, mcp, pip, dip):
    angle = calculate_angle(
        landmarks[mcp],
        landmarks[pip],
        landmarks[dip]
    )

    return angle > 160, angle


# ============================================================
# 3. 判断拇指是否伸直
# ============================================================

def is_thumb_open(landmarks):
    angle1 = calculate_angle(
        landmarks[1],
        landmarks[2],
        landmarks[3]
    )

    angle2 = calculate_angle(
        landmarks[2],
        landmarks[3],
        landmarks[4]
    )

    thumb_open = (
        angle1 > 150
        and
        angle2 > 150
    )

    return thumb_open, angle1, angle2


# ============================================================
# 4. RPS 手势分类
# ============================================================

def classify_rps(
    thumb_open,
    index_open,
    middle_open,
    ring_open,
    pinky_open
):
    """
    根据五根手指的开合状态判断：
    ROCK / PAPER / SCISSORS / UNKNOWN
    """

    # Rock：五指全部弯曲
    if not thumb_open and \
       not index_open and \
       not middle_open and \
       not ring_open and \
       not pinky_open:

        return "ROCK"

    # Paper：五指全部伸直
    if thumb_open and \
       index_open and \
       middle_open and \
       ring_open and \
       pinky_open:

        return "PAPER"

    # Scissors：食指和中指伸直，
    # 无名指和小拇指弯曲
    # 暂时忽略拇指
    if index_open and \
       middle_open and \
       not ring_open and \
       not pinky_open:

        return "SCISSORS"

    return "UNKNOWN"


# ============================================================
# 5. 15 帧稳定投票
# ============================================================

def get_stable_gesture(buffer):
    """
    根据最近 15 帧识别结果进行多数投票。

    某个手势至少出现 10 次，
    才认为识别结果稳定。
    """

    if len(buffer) < 15:
        return "WAITING"

    counts = {
        "ROCK": 0,
        "PAPER": 0,
        "SCISSORS": 0
    }

    for gesture in buffer:
        if gesture in counts:
            counts[gesture] += 1

    stable_gesture = max(
        counts,
        key=counts.get
    )

    if counts[stable_gesture] >= 10:
        return stable_gesture

    return "UNSTABLE"


# ============================================================
# 6. 创建摄像头 + MediaPipe
# ============================================================

class RPSVision:

    def __init__(self, camera_id=0):

        self.cap = cv2.VideoCapture(camera_id)

        if not self.cap.isOpened():
            raise RuntimeError("无法打开摄像头")

        self.mp_hands = mp.solutions.hands

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        self.mp_draw = mp.solutions.drawing_utils

        self.gesture_buffer = deque(maxlen=15)

        self.latest_frame = None
        self.latest_gesture = "UNKNOWN"
        self.latest_stable_gesture = "WAITING"

        self.running = False
        self.thread = None

    # ========================================================
    # 7. 获取一帧并进行 RPS 识别
    # ========================================================

    def read(self):

        return (
            self.latest_frame,
            self.latest_stable_gesture
    )


    def reset(self):
        """
        清空上一轮猜拳的手势历史。
        新一轮开始时调用。
        """
        self.gesture_buffer.clear()


    # ========================================================
    # 8. 关闭摄像头
    # ========================================================
    def close(self):

        self.cap.release()

        self.hands.close()

        cv2.destroyAllWindows()


    def _vision_loop(self):

        while self.running:

            # ====================================================
            # 1. 读取摄像头
            # ====================================================

            ret, frame = self.cap.read()

            if not ret:
                continue

            # ====================================================
            # 2. MediaPipe
            # ====================================================

            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            results = self.hands.process(rgb_frame)

            gesture = "UNKNOWN"

            # ====================================================
            # 3. 手部识别
            # ====================================================

            if results.multi_hand_landmarks:

                hand_landmarks = (
                    results.multi_hand_landmarks[0]
                )

                landmarks = hand_landmarks.landmark

                # ----------------------------
                # 拇指
                # ----------------------------

                thumb_open, thumb_angle1, thumb_angle2 = (
                    is_thumb_open(landmarks)
                )

                # ----------------------------
                # 四根普通手指
                # ----------------------------

                index_open, index_angle = is_finger_open(
                    landmarks, 5, 6, 7
                )

                middle_open, middle_angle = is_finger_open(
                    landmarks, 9, 10, 11
                )

                ring_open, ring_angle = is_finger_open(
                    landmarks, 13, 14, 15
                )

                pinky_open, pinky_angle = is_finger_open(
                    landmarks, 17, 18, 19
                )

                # ----------------------------
                # RPS 分类
                # ----------------------------

                gesture = classify_rps(
                    thumb_open,
                    index_open,
                    middle_open,
                    ring_open,
                    pinky_open
                )

                # ----------------------------
                # 绘制手部关键点
                # ----------------------------

                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )

                # ====================================================
                # 4. 生成5个手指状态文字
                # ====================================================

                text1 = (
                    f"Index: "
                    f"{'OPEN' if index_open else 'CLOSED'} "
                    f"{index_angle:.0f}°"
                )

                text2 = (
                    f"Middle: "
                    f"{'OPEN' if middle_open else 'CLOSED'} "
                    f"{middle_angle:.0f}°"
                )

                text3 = (
                    f"Ring: "
                    f"{'OPEN' if ring_open else 'CLOSED'} "
                    f"{ring_angle:.0f}°"
                )

                text4 = (
                    f"Pinky: "
                    f"{'OPEN' if pinky_open else 'CLOSED'} "
                    f"{pinky_angle:.0f}°"
                )

                text5 = (
                    f"Thumb: "
                    f"{'OPEN' if thumb_open else 'CLOSED'} "
                    f"{thumb_angle1:.0f}° / "
                    f"{thumb_angle2:.0f}°"
                )

                # ====================================================
                # 5. 显示5个手指状态
                # ====================================================

                cv2.putText(
                    frame,
                    text1,
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    text2,
                    (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    text3,
                    (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    text4,
                    (20, 130),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    text5,
                    (20, 160),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

            # ====================================================
            # 6. 15帧投票
            # ====================================================

            self.gesture_buffer.append(gesture)

            stable_gesture = get_stable_gesture(
                self.gesture_buffer
            )

            # ====================================================
            # 7. 显示当前手势
            # ====================================================

            cv2.putText(
                frame,
                f"Gesture: {gesture}",
                (20, 200),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            # ====================================================
            # 8. 显示稳定手势
            # ====================================================

            cv2.putText(
                frame,
                f"Stable: {stable_gesture}",
                (20, 235),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            # ====================================================
            # 9. 保存最新结果
            # ====================================================

            self.latest_frame = frame
            self.latest_gesture = gesture
            self.latest_stable_gesture = stable_gesture


    def start(self):

        self.running = True

        self.thread = threading.Thread(
            target=self._vision_loop,
            daemon=True
        )

        self.thread.start()

    def stop(self):

        self.running = False

        if self.thread is not None:
            self.thread.join(timeout=1)

        self.cap.release()
        self.hands.close()
        cv2.destroyAllWindows()