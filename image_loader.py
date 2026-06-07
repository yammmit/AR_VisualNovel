import cv2
import os
import numpy as np
from PIL import Image, ImageSequence

class ImageLoader:
    @staticmethod
    def load_character_gifs():
        animations = {}
        states = ['normal', 'happy', 'mad'] 
        for state in states:
            filename = f"{state}.gif"
            frames = []
            if os.path.exists(filename):
                gif = Image.open(filename)
                # GIF의 모든 프레임을 추출하여 RGB로 변환
                for frame in ImageSequence.Iterator(gif):
                    frame = frame.convert("RGB")
                    raw_frame = np.array(frame)
                    # Pillow RGBA (R, G, B) -> OpenCV BGR (B, G, R)
                    bgr_frame = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2BGR)
                    
                    # ★ 컴퓨터비전 핵심: 흰색 배경(RGB 255,255,255)을 투명하게 만드는 로직 ★
                    
                    # 흰색 영역 탐지 (조명차가 있을 수 있으므로 Threshold 240~255 적용)
                    lower_white = np.array([240, 240, 240]) # BGR 순서
                    upper_white = np.array([255, 255, 255])
                    mask = cv2.inRange(bgr_frame, lower_white, upper_white)
                    
                    # 흰색 영역(Mask)은 투명도(Alpha)를 0으로, 나머지는 255로
                    # mask는 흰색이 255, 배경이 0이므로 반전시킴
                    alpha = cv2.bitwise_not(mask)
                    
                    # BGRA 프레임 조립 (원래 BGR + 새로 만든 Alpha)
                    b, g, r = cv2.split(bgr_frame)
                    processed_bgra_frame = cv2.merge([b, g, r, alpha])
                    
                    frames.append(processed_bgra_frame)
                animations[state] = frames
                print(f"{filename} ({len(frames)} 프레임, 자동 흰 배경 제거) 로드 완료!")
            else:
                print(f"{filename} 파일이 없습니다! 투명 GIF를 넣어주세요.")
                animations[state] = []
        return animations