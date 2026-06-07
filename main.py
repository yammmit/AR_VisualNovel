import cv2
import math
from config import *
from image_loader import ImageLoader
from renderer import SpriteRenderer
from interactor import HandTracker 
from ui import UIManager

def main():
    animations = ImageLoader.load_character_gifs()
    if not any(animations.values()): return
    
    renderer = SpriteRenderer(animations)
    interactor = HandTracker() 
    ui = UIManager()
    
    cap = cv2.VideoCapture(0)
    cap.set(3, WIDTH)
    cap.set(4, HEIGHT)
    
    affection = 50.0
    model_center_x, model_center_y = WIDTH // 2, HEIGHT // 2

    print("🚀 AR_VisualNovel (GIF Animation & Computer Vision Hand Tracker Ver) 가동 완료!")

    while True:
        success, img = cap.read()
        if not success: break
        
        img = cv2.flip(img, 1)
        # 이번에는 CV 알고리즘 작동(윤곽선)을 잘 보여주기 위해 어둡게 처리하는 걸 뺐습니다.
        
        state_text, dialogue, ui_color = "IDLE", "I'm Hatsune Miku. Please interact with me!", COLOR_NORMAL

        # 손 추적기 실행 (이번엔 img 자체를 받아와서 윤곽선을 덧그립니다)
        state_text, hand_center, img = interactor.analyze(img, model_center_x, model_center_y)

        if hand_center:
            cv2.circle(img, hand_center, 10, (255, 0, 0), cv2.FILLED)
            
            if state_text == "PINCHING":
                ui_color = COLOR_MAD
                affection = max(0.0, affection - 0.5)
                dialogue = "Ouch! It hurts! Baka!"
            elif state_text == "PATTING":
                ui_color = COLOR_HAPPY
                affection = min(MAX_AFFECTION, affection + 0.3)
                dialogue = "Hehe... warm! I like it <3"
            elif state_text == "TOUCHING":
                ui_color = COLOR_TOUCH
                affection = min(MAX_AFFECTION, affection + 0.1)
                dialogue = "Yes? Do you need something?"
                model_center_x = WIDTH // 2 + int((hand_center[0] - WIDTH/2) * 0.15)
        else:
            affection = max(0.0, affection - 0.05)
            model_center_x = int(model_center_x * 0.9 + (WIDTH // 2) * 0.1)

        # GIF 애니메이션 렌더링
        display_img = renderer.render(img, state_text, model_center_x, HEIGHT // 2)
        
        ui.draw_status(display_img, state_text)
        ui.draw_gauge(display_img, affection, ui_color)
        ui.draw_dialogue(display_img, "Hatsune Miku", dialogue, ui_color)

        cv2.imshow("AR Visual Novel", display_img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()