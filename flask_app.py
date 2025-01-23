from flask import Flask, render_template, Response
import cv2
from cvzone.HandTrackingModule import HandDetector
from cvzone.ClassificationModule import Classifier
import numpy as np
import math
import os
import signal
app = Flask(__name__)

# Initialize model and settings
detector = HandDetector(maxHands=1)
classifier = Classifier("Model/keras_model.h5", "Model/labels.txt")
offset = 20
imgSize = 300
labels = ["Hello", "I love you", "No", "Okay", "Please", "Thank you", "Yes"]

# Camera capture
camera = cv2.VideoCapture(0)

def generate_frames():
    while True:
        success, img = camera.read()
        if not success:
            break
        
        else:
            imgOutput = img.copy()
            hands, img = detector.findHands(img)
            if hands:
                hand = hands[0]
                x, y, w, h = hand['bbox']

                imgWhite = np.ones((imgSize, imgSize, 3), np.uint8) * 255

                imgCrop = img[y-offset:y + h + offset, x-offset:x + w + offset]
                try:
                    aspectRatio = h / w
                    if aspectRatio > 1:
                        k = imgSize / h
                        wCal = math.ceil(k * w)
                        imgResize = cv2.resize(imgCrop, (wCal, imgSize))
                        wGap = math.ceil((imgSize - wCal) / 2)
                        imgWhite[:, wGap: wCal + wGap] = imgResize
                        prediction, index = classifier.getPrediction(imgWhite, draw=False)
                    else:
                        k = imgSize / w
                        hCal = math.ceil(k * h)
                        imgResize = cv2.resize(imgCrop, (imgSize, hCal))
                        hGap = math.ceil((imgSize - hCal) / 2)
                        imgWhite[hGap: hCal + hGap, :] = imgResize
                        prediction, index = classifier.getPrediction(imgWhite, draw=False)

                    cv2.putText(imgOutput, labels[index], (x, y-30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.rectangle(imgOutput, (x-offset, y-offset), (x + w + offset, y + h + offset), (0, 255, 0), 2)

                except:
                    pass
            

            _, buffer = cv2.imencode('.jpg', imgOutput)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/stop', methods=['POST'])
# def stop():
#     global camera_running
#     camera_running = False  # Set the flag to stop the camera stream
#     camera.release()  # Release the camera
#     return "Camera Stopped", 200

# @app.route('/shutdown', methods=['POST'])
# def shutdown():
#     os.kill(os.getpid(), signal.SIGINT)  # Gracefully stop the Flask server
#     return "Shutting down...", 200

if __name__ == "__main__":
    app.run(debug=True)
