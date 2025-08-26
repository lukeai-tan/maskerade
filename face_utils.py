import cv2
import face_recognition

def blur_faces(img, blur_strength=(55, 55)):
    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_img)
    for top, right, bottom, left in face_locations:
        roi = img[top:bottom, left:right]
        img[top:bottom, left:right] = cv2.GaussianBlur(roi, blur_strength, 30)
    return img
