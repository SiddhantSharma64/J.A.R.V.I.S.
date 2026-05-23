import os
import sys
import cv2

# Set up cross-platform camera capture
if sys.platform == "win32":
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
else:
    cam = cv2.VideoCapture(0)

cam.set(3, 640)  # set FrameWidth
cam.set(4, 480)  # set FrameHeight

cascade_path = os.path.join('backend', 'auth', 'haarcascade_frontalface_default.xml')
detector = cv2.CascadeClassifier(cascade_path)

face_id = input("Enter a Numeric user ID here (e.g. 1, 2, 3...): ")

print("Taking samples, look at camera...")
count = 0

samples_dir = os.path.join("backend", "auth", "samples")
os.makedirs(samples_dir, exist_ok=True)

while True:
    ret, img = cam.read()
    if not ret:
        break
    
    converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(converted_image, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        count += 1

        # Capture and save image
        sample_path = os.path.join(samples_dir, f"face.{face_id}.{count}.jpg")
        cv2.imwrite(sample_path, converted_image[y:y+h, x:x+w])

        cv2.imshow('image', img)

    k = cv2.waitKey(100) & 0xff
    if k == 27:  # Press 'ESC' to stop
        break
    elif count >= 100:  # Take 100 samples
        break

print("Samples taken, closing the program...")
cam.release()
cv2.destroyAllWindows()