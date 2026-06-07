import cv2
import numpy as np

class SpriteRenderer:
    def __init__(self, animations):
        self.animations = animations
        # 각 상태별 현재 재생 중인 프레임 번호 저장
        self.frame_indices = {'normal': 0, 'happy': 0, 'mad': 0}

    def overlay_transparent(self, bg_img, img_to_overlay_t, x, y, overlay_size=None):
        try:
            bg_img_copy = bg_img.copy()
            if overlay_size is not None:
                img_to_overlay_t = cv2.resize(img_to_overlay_t, overlay_size)

            b, g, r, a = cv2.split(img_to_overlay_t)
            overlay_color = cv2.merge((b, g, r))
            mask = cv2.medianBlur(a, 5)

            h, w, _ = overlay_color.shape
            
            # 화면 밖으로 나가도 에러 안 나게 방어하는 알고리즘
            if y < 0:
                img_to_overlay_t, mask, overlay_color = img_to_overlay_t[-y:], mask[-y:], overlay_color[-y:]
                h += y; y = 0
            if x < 0:
                img_to_overlay_t, mask, overlay_color = img_to_overlay_t[:, -x:], mask[:, -x:], overlay_color[:, -x:]
                w += x; x = 0
            if y + h > bg_img_copy.shape[0]:
                h = bg_img_copy.shape[0] - y
                mask, overlay_color = mask[:h], overlay_color[:h]
            if x + w > bg_img_copy.shape[1]:
                w = bg_img_copy.shape[1] - x
                mask, overlay_color = mask[:, :w], overlay_color[:, :w]

            roi = bg_img_copy[y:y+h, x:x+w]
            img1_bg = cv2.bitwise_and(roi, roi, mask=cv2.bitwise_not(mask))
            img2_fg = cv2.bitwise_and(overlay_color, overlay_color, mask=mask)
            bg_img_copy[y:y+h, x:x+w] = cv2.add(img1_bg, img2_fg)
            return bg_img_copy
        except:
            return bg_img

    def render(self, img, state, center_x, center_y):
        img_key = 'normal'
        if state == 'PATTING': img_key = 'happy'
        elif state == 'PINCHING': img_key = 'mad'

        frames = self.animations.get(img_key)
        if not frames: frames = self.animations.get('normal')
        if not frames: return img

        # GIF 프레임 1칸 전진 (무한 루프 재생)
        self.frame_indices[img_key] = (self.frame_indices[img_key] + 1) % len(frames)
        current_frame = frames[self.frame_indices[img_key]]

        target_w, target_h = 450, 550
        draw_x = center_x - (target_w // 2)
        draw_y = img.shape[0] - target_h + 50 

        return self.overlay_transparent(img, current_frame, draw_x, draw_y, (target_w, target_h))