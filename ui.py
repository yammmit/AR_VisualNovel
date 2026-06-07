import cv2
from config import WIDTH, HEIGHT

class UIManager:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def draw_status(self, img, state_text):
        cv2.putText(img, "AR Visual Novel Engine v1.0", (10, 30), self.font, 0.6, (0, 255, 0), 2)
        cv2.putText(img, f"Action: {state_text}", (10, 60), self.font, 0.6, (255, 255, 255), 1)

    def draw_gauge(self, img, affection, color):
        cv2.putText(img, "Affection:", (WIDTH - 180, 30), self.font, 0.6, (0, 255, 255), 1)
        cv2.rectangle(img, (WIDTH - 110, 15), (WIDTH - 110 + int(affection), 35), color, cv2.FILLED)
        cv2.rectangle(img, (WIDTH - 110, 15), (WIDTH - 10, 35), (255, 255, 255), 1)

    def draw_dialogue(self, img, character_name, dialogue_text, color):
        # 반투명 대사창 배경
        overlay = img.copy()
        cv2.rectangle(overlay, (20, HEIGHT - 100), (WIDTH - 20, HEIGHT - 20), (0, 0, 0), cv2.FILLED)
        cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
        
        # 이름 및 대사 출력 (한글은 깨지므로 영어 권장)
        cv2.putText(img, character_name, (30, HEIGHT - 75), self.font, 0.6, color, 2)
        cv2.putText(img, dialogue_text, (30, HEIGHT - 40), self.font, 0.6, (255, 255, 255), 1)