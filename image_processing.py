import cv2
import os

def blur_bbox(img, bbox, blur_strength=(25, 25)):
    tl, tr, br, bl = bbox
    x_coords = [tl[0], tr[0], br[0], bl[0]]
    y_coords = [tl[1], tr[1], br[1], bl[1]]
    x_min, x_max = int(min(x_coords)), int(max(x_coords))
    y_min, y_max = int(min(y_coords)), int(max(y_coords))
    roi = img[y_min:y_max, x_min:x_max]
    img[y_min:y_max, x_min:x_max] = cv2.GaussianBlur(roi, blur_strength)
    return img

def save_image(img, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, img)
