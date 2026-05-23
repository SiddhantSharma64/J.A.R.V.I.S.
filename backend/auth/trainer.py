import os
import cv2
import numpy as np
from PIL import Image

path = os.path.join('backend', 'auth', 'samples')
os.makedirs(path, exist_ok=True)

recognizer = cv2.face.LBPHFaceRecognizer_create()

cascade_path = os.path.join("backend", "auth", "haarcascade_frontalface_default.xml")
detector = cv2.CascadeClassifier(cascade_path)

def Images_And_Labels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".jpg")]     
    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        try:
            gray_img = Image.open(imagePath).convert('L')  # convert to grayscale
            img_arr = np.array(gray_img, 'uint8')
            
            # Extract user ID from filename: face.ID.count.jpg
            parts = os.path.split(imagePath)[-1].split(".")
            if len(parts) >= 3:
                id_val = int(parts[1])
                faces = detector.detectMultiScale(img_arr)

                for (x, y, w, h) in faces:
                    faceSamples.append(img_arr[y:y+h, x:x+w])
                    ids.append(id_val)
        except Exception as e:
            print(f"Error reading sample {imagePath}: {e}")

    return faceSamples, ids

print("Training faces. It will take a few seconds. Wait...")

faces, ids = Images_And_Labels(path)
if len(faces) > 0:
    recognizer.train(faces, np.array(ids))
    
    trainer_dir = os.path.join('backend', 'auth', 'trainer')
    os.makedirs(trainer_dir, exist_ok=True)
    
    recognizer.write(os.path.join(trainer_dir, 'trainer.yml'))
    print("Model trained, Now we can recognize your face.")
else:
    print("No faces found to train.")