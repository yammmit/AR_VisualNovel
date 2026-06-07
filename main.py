import cv2
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
    
    # ★ 애니메이션 락 변수 추가 ★
    anim_lock_frames = 0
    locked_state = "IDLE"
    locked_dialogue = "I'm Hatsune Miku. Please interact with me!"
    locked_color = COLOR_NORMAL

    print("🚀 AR_VisualNovel (Animation Lock System Ver.) 가동 완료!")

    while True:
        success, img = cap.read()
        if not success: break
        
        img = cv2.flip(img, 1)

        # 1. 손 추적기 실행
        raw_state, hand_center, img = interactor.analyze(img, model_center_x, model_center_y)

        # 2. 애니메이션 상태 관리 (Lock 시스템)
        if anim_lock_frames > 0:
            anim_lock_frames -= 1
            final_state = locked_state
            dialogue = locked_dialogue
            ui_color = locked_color
        else:
            # 락이 풀려있을 때만 새로운 상태 판정
            final_state = "IDLE"
            dialogue = "I'm Hatsune Miku. Please interact with me!"
            ui_color = COLOR_NORMAL

            if hand_center:
                cv2.circle(img, hand_center, 10, (255, 0, 0), cv2.FILLED)
                
                if raw_state == "PINCHING":
                    anim_lock_frames = 121  # mad.gif 프레임 수
                    locked_state = "PINCHING"
                    locked_dialogue = "Ouch! It hurts! Baka!"
                    locked_color = COLOR_MAD
                    affection = max(0.0, affection - 0.5)
                    final_state, dialogue, ui_color = locked_state, locked_dialogue, locked_color
                    
                elif raw_state == "PATTING":
                    anim_lock_frames = 43   # happy.gif 프레임 수
                    locked_state = "PATTING"
                    locked_dialogue = "Hehe... warm! I like it <3"
                    locked_color = COLOR_HAPPY
                    affection = min(MAX_AFFECTION, affection + 0.3)
                    final_state, dialogue, ui_color = locked_state, locked_dialogue, locked_color
                    
                elif raw_state == "TOUCHING":
                    final_state = "TOUCHING"
                    ui_color = COLOR_TOUCH
                    dialogue = "Yes? Do you need something?"
                    model_center_x = WIDTH // 2 + int((hand_center[0] - WIDTH/2) * 0.15)
            else:
                affection = max(0.0, affection - 0.05)
                model_center_x = int(model_center_x * 0.9 + (WIDTH // 2) * 0.1)

        # 3. 렌더링 및 UI 그리기
        display_img = renderer.render(img, final_state, model_center_x, HEIGHT // 2)
        ui.draw_status(display_img, final_state)
        ui.draw_gauge(display_img, affection, ui_color)
        ui.draw_dialogue(display_img, "Hatsune Miku", dialogue, ui_color)

        cv2.imshow("AR Visual Novel", display_img)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()