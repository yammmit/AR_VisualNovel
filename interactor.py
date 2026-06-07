import cv2
import mediapipe as mp
import math

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        # 최적화된 뼈대 추적 모델 로드
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

    def analyze(self, img, model_center_x, model_center_y):
        # OpenCV의 BGR을 MediaPipe용 RGB로 변환
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_img)

        state = "IDLE"
        hand_center = None

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # ★ 컴퓨터비전 시각화: 화면에 진짜 손 뼈대(Skeleton) 그리기 ★
                self.mp_draw.draw_landmarks(
                    img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0, 255, 255), thickness=2, circle_radius=4), # 관절(노란색)
                    self.mp_draw.DrawingSpec(color=(255, 0, 0), thickness=2) # 뼈대(파란색)
                )

                h, w, c = img.shape
                # 랜드마크 픽셀 좌표 변환
                thumb_tip = hand_landmarks.landmark[4]
                index_tip = hand_landmarks.landmark[8]
                middle_tip = hand_landmarks.landmark[12]

                thumb_pos = (int(thumb_tip.x * w), int(thumb_tip.y * h))
                index_pos = (int(index_tip.x * w), int(index_tip.y * h))
                middle_pos = (int(middle_tip.x * w), int(middle_tip.y * h))

                hand_center = index_pos # 포인터 기준점을 검지 끝으로 설정

                # 뼈대 좌표 간의 유클리드 거리 계산
                pinch_dist = math.hypot(thumb_pos[0] - index_pos[0], thumb_pos[1] - index_pos[1])
                open_dist = math.hypot(index_pos[0] - middle_pos[0], index_pos[1] - middle_pos[1])

                # 행동 판정 (State Machine)
                if pinch_dist < 40:
                    state = "PINCHING" # 엄지와 검지가 맞닿음 (꼬집기)
                elif open_dist > 40 and index_pos[1] < model_center_y - 60:
                    state = "PATTING" # 손가락을 펴고 머리 위쪽에 있음 (쓰다듬기)
                else:
                    state = "TOUCHING" # 그 외 평범한 접근 (말걸기)

        return state, hand_center, img