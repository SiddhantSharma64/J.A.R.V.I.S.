import os
import sys
import json
import cv2

def AuthenticateFace():
    flag = 0
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    trainer_path = os.path.join('backend', 'auth', 'trainer', 'trainer.yml')
    if not os.path.exists(trainer_path):
        print("Trainer file not found. Bypassing authentication.")
        return 1  # Bypass if trainer file does not exist

    recognizer.read(trainer_path)
    
    cascadePath = os.path.join("backend", "auth", "haarcascade_frontalface_default.xml")
    faceCascade = cv2.CascadeClassifier(cascadePath)

    font = cv2.FONT_HERSHEY_SIMPLEX

    # Load dynamic names
    users_file = os.path.join("backend", "auth", "users.json")
    names = [""]
    if os.path.exists(users_file):
        try:
            with open(users_file, "r") as f:
                users = json.load(f)
                if users:
                    max_id = max([int(k) for k in users.keys()])
                    names = [""] * (max_id + 1)
                    for k, v in users.items():
                        names[int(k)] = v
        except Exception as e:
            print(f"Error loading users: {e}")
            names = ['', '', 'Ankit']
    else:
        names = ['', '', 'Ankit']

    if sys.platform == "win32":
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    else:
        cam = cv2.VideoCapture(0)

    if not cam.isOpened():
        print("Camera not found or not authorized. Bypassing authentication.")
        return 1

    cam.set(3, 640)  # set FrameWidth
    cam.set(4, 480)  # set FrameHeight

    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    import time
    start_time = time.time()
    # Reduced timeout to 8 seconds for a faster boot experience
    timeout = 8  

    while True:
        ret, img = cam.read()
        if not ret:
            print("Failed to read from camera. Bypassing authentication.")
            flag = 1
            break

        converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            converted_image,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH)),
        )

        for(x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

            id, accuracy = recognizer.predict(converted_image[y:y+h, x:x+w])

            # accuracy < 100 ==> "0" is a perfect match. Lower values = better accuracy.
            if accuracy < 100:
                if id < len(names):
                    user_name = names[id]
                else:
                    user_name = "unknown"
                accuracy_text = "  {0}%".format(round(100 - accuracy))
                
                # Only authenticate if accuracy is reasonably high (e.g. > 35%)
                if (100 - accuracy) > 35:
                    flag = 1
            else:
                user_name = "unknown"
                accuracy_text = "  {0}%".format(round(100 - accuracy))
                flag = 0

            cv2.putText(img, str(user_name), (x+5, y-5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(accuracy_text), (x+5, y+h-5), font, 1, (255, 255, 0), 1)

        cv2.imshow('camera', img)

        k = cv2.waitKey(10) & 0xff
        if k == 27:  # ESC to exit
            break
        if flag == 1:
            break
            
        # Timeout safety check
        if time.time() - start_time > timeout:
            print("Authentication timed out.")
            break

    cam.release()
    cv2.destroyAllWindows()
    return flag