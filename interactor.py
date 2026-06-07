import cv2
import numpy as np

class HandTracker:
    def __init__(self):
        self.prev_y = 0

    def analyze(self, img, model_center_x, model_center_y):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # 살색 범위 (조명에 따라 좁게 설정)
        mask = cv2.inRange(hsv, np.array([0, 20, 70]), np.array([20, 255, 255]))
        mask = cv2.erode(mask, np.ones((5,5), np.uint8), iterations=2)
        mask = cv2.dilate(mask, np.ones((5,5), np.uint8), iterations=2)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        state = "TOUCHING"
        hand_center = None
        
        if contours:
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > 5000:
                M = cv2.moments(largest)
                cx, cy = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
                hand_center = (cx, cy)
                
                # 움직임 감지 알고리즘 (위/아래 방향으로 판정)
                if cy < model_center_y - 50: state = "PATTING"    # 위로 올리면 쓰다듬기
                elif cy > model_center_y + 50: state = "PINCHING" # 아래로 내리면 때리기
                self.prev_y = cy
                
        return state, hand_center, img