import cv2
import numpy as np

# 두 이미지 파일을 읽어들입니다.
background = cv2.imread('/home/mjk0307/otaku/otaku/midjourney_api/output/A blue frame adorned with delicate, whimsi/bottom_right.jpg',cv2.IMREAD_UNCHANGED)
overlay = cv2.imread('/home/mjk0307/otaku/otaku/background_removed/1.png', cv2.IMREAD_UNCHANGED)

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
# background = cv2.resize(background, (int(background.shape[1]//(2**0.9)), int(background.shape[0]//(2**0.9))))
cv2.imwrite('result5.jpeg', background)
cv2.imshow('result', background)
cv2.waitKey(0)
cv2.destroyAllWindows()

# # 오버레이할 부분을 배경 이미지에서 잘라냅니다.
# y1, y2 = y_offset - overlay_resized.shape[0], y_offset
# x1, x2 = x_offset - overlay_resized.shape[1]//2, x_offset + overlay_resized.shape[1] // 2

# # 알파 채널이 없는 경우 투명도 설정
# if overlay_resized.shape[2] == 3:
#     alpha_s = np.ones((new_height, new_width))
# else:
#     alpha_s = overlay_resized[:, :, 3] / 255.0  # 알파 채널이 있는 경우 (png 파일)
    
# alpha_l = 1.0 - alpha_s


# for c in range(0, 3):
#     background[y1:y2, x1:x2, c] = (alpha_s * overlay_resized[:, :, c] + alpha_l * background[y1:y2, x1:x2, c])

# # 결과 이미지를 저장하거나 표시합니다.
# cv2.imwrite('result.png', background)
# cv2.imshow('result', background)
# cv2.waitKey(0)
# cv2.destroyAllWindows()