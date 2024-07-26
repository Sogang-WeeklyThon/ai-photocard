import os
import uvicorn
import json
import cv2
import numpy as np
from fastapi import FastAPI

app = FastAPI()

def crop(image):
    alpha_channel = image[:, :, 3]

    # 알파 채널을 바이너리 이미지로 변환
    _, binary_mask = cv2.threshold(alpha_channel, 1, 255, cv2.THRESH_BINARY)

    kernel = np.ones((5, 5), np.uint8)
    dilated_mask = cv2.dilate(binary_mask, kernel, iterations=1)

    # 확장된 마스크의 컨투어 찾기
    contours, _ = cv2.findContours(dilated_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 컨투어가 여러 개일 수 있으므로 가장 큰 컨투어를 선택
    largest_contour = max(contours, key=cv2.contourArea)

    # 물체의 경계 상자 찾기
    x, y, w, h = cv2.boundingRect(largest_contour)

    # 원본 이미지에서 물체 부분을 네모로 crop
    cropped_image = image[y:y+h, x:x+w]
    return cropped_image

def check_garo_jail_gingeo(img_list):
    garo_gilees = [img.shape[1] for img in img_list]
    max_ = max(garo_gilees)
    return garo_gilees.index(max_)

@app.get("/healthy_check")
async def health():
    return "healthy!"

@app.post("/pb_integration")
async def pb_integration(request: dict):
    person_path = request["person"]
    background_path = request["background"]
    background = cv2.imread(background_path,cv2.IMREAD_UNCHANGED)
    overlay = cv2.imread(person_path, cv2.IMREAD_UNCHANGED)

    # 오버레이 이미지를 배경 이미지 위에 놓을 위치를 지정합니다.
    x_offset = background.shape[1] // 2
    y_offset = background.shape[0] // 7 * 6
    print(overlay.shape)
    print(background.shape)
    # 오버레이 이미지의 크기를 배경 이미지에 맞추거나 적절히 조정합니다.
    new_width = int(background.shape[1] * 0.8)
    new_height = int(background.shape[0] * 0.8)

    overlay_resized = cv2.resize(overlay, (new_width, new_height))

    # Create a mask with a gradient
    gradient_strength = 0.3  # Increase gradient strength for less transparency
    gradient = np.linspace(1 - gradient_strength, 1, new_height // 2)
    alpha_gradient = np.concatenate((gradient, gradient[::-1], np.ones(new_height % 2)), axis=0)
    alpha_gradient = np.tile(alpha_gradient[:, None], (1, new_width))

    # Apply the gradient to the alpha channel
    if overlay_resized.shape[2] == 4:
        alpha_channel = overlay_resized[:, :, 3].astype(float) / 255.0
        alpha_channel *= alpha_gradient
        overlay_resized[:, :, 3] = (alpha_channel * 255).astype(overlay_resized.dtype)
    else:
        alpha_channel = (255 * alpha_gradient).astype(overlay_resized.dtype)
        overlay_resized = np.dstack((overlay_resized, alpha_channel))

    # Apply Gaussian blur to the alpha channel for smoother transition
    alpha_channel_blurred = cv2.GaussianBlur(overlay_resized[:, :, 3], (51, 51), 0)
    overlay_resized[:, :, 3] = alpha_channel_blurred

    # Determine the region to overlay
    y1, y2 = y_offset - overlay_resized.shape[0], y_offset
    x1, x2 = x_offset - overlay_resized.shape[1] // 2, x_offset + overlay_resized.shape[1] // 2

    # Extract the alpha channel
    alpha_s = overlay_resized[:, :, 3] / 255.0
    alpha_l = 1.0 - alpha_s

    # Blend the overlay with the background
    for c in range(0, 3):
        background[y1:y2, x1:x2, c] = (alpha_s * overlay_resized[:, :, c] +
                                    alpha_l * background[y1:y2, x1:x2, c])

    # Save or display the result
    save_path = f"./integrated_images/{len(os.listdir('./integrated_images'))}.jpg"
    cv2.imwrite(save_path, background)
    return save_path

@app.post("/pbs_integration")    
async def pbs_integration(request:dict):
    print("get post")
    pb_path = request["pb_path"]
    sticker_paths = request["sticker_path"]
    
    if isinstance(sticker_paths, str):
        sticker_paths = [sticker_paths]
    
    sticker_paths = sticker_paths[:min(len(sticker_paths), 5)]
    attach_order = ["upper_left","upper_right","under_center","under_left","under_right"]
    stickers = [cv2.imread(sticker_path, cv2.IMREAD_UNCHANGED) for sticker_path in sticker_paths]
    cropped_stickers = [crop(img) for img in stickers]
    
    if len(cropped_stickers) >= 3:
        idx_ = check_garo_jail_gingeo(cropped_stickers)
        cropped_stickers[2], cropped_stickers[idx_] = cropped_stickers[idx_], cropped_stickers[2]
    
    person_background = cv2.imread(pb_path, cv2.IMREAD_UNCHANGED)
    bg_height, bg_width = person_background.shape[:2]
    
    sticker_positions = {
        "upper_left": (int(bg_width * 0.2), int(bg_height * 0.1)),
        "upper_right": (int(bg_width * 0.8), int(bg_height * 0.1)),
        "under_center": (int(bg_width * 0.5), int(bg_height * 0.95)),
        "under_left": (int(bg_width * 0.2), int(bg_height * 0.9)),
        "under_right": (int(bg_width * 0.8), int(bg_height * 0.9))
    }

    resized_stickers = []
    for idx, sticker in enumerate(cropped_stickers):
        resize_factor = 0.2
        if idx == 2:
            resize_factor = 0.3
        sticker_height, sticker_width = sticker.shape[:2]
        scale_factor = min(bg_width / sticker_width, bg_height / sticker_height) * resize_factor
        new_size = (int(sticker_width * scale_factor), int(sticker_height * scale_factor))
        resized_sticker = cv2.resize(sticker, new_size, interpolation=cv2.INTER_AREA)
        resized_stickers.append(resized_sticker)
    
    for sticker, position in zip(resized_stickers, attach_order):
        x, y = sticker_positions[position]
        x -= sticker.shape[1] // 2
        y -= sticker.shape[0] // 2
        y = max(0, min(y, bg_height - sticker.shape[0]))
        x = max(0, min(x, bg_width - sticker.shape[1]))
        
        alpha_s = sticker[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s
        
        for c in range(0, 3):
            person_background[y:y+sticker.shape[0], x:x+sticker.shape[1], c] = (alpha_s * sticker[:, :, c] +
                                                                               alpha_l * person_background[y:y+sticker.shape[0], x:x+sticker.shape[1], c])
    
    # Save or return the final image
    save_path = f"./final_images/{len(os.listdir('./final_images'))}.jpeg"
    cv2.imwrite(save_path, person_background)
    return save_path
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8123)