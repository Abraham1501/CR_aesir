#Code of camera
import cv2
from motion_detector import motion_detector
from QR import QR
import keyboard as kb
import time
from datetime import datetime

class Camera():
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        self.texts = ["", "Tracking", "Read QR"]
        self.text = self.texts[0]
        self.keys = ["'1'", "'2'", "'3'"]
        self.mode = "D"
        self.flip = False
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.count = 1
        # path for save images (it has to be updated every time it gets on a new device)
        self.images_path = r"C:\Users\odinh\OneDrive\Escritorio\Code_robot_client\images"

    def main(self):
        ret, frame1 = self.cam.read()
        ret, frame2 = self.cam.read()

        while self.cam.isOpened():
            # Check camera mode
            if self.mode == "Q":
                frame1 = QR(frame1, self.font, self.cam)
                self.text = self.texts[2]
            elif self.mode == "M":
                frame1 = motion_detector(self.cam).frames(frame1, frame2)
                self.text = self.texts[1]
            else:
                self.text = self.texts[0]

            # Show image of camera
            frame1 = cv2.resize(frame1, (1440, 810), interpolation=cv2.INTER_AREA)
            cv2.putText(frame1, self.text, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (200, 100, 100), 4)
            cv2.imshow("video", frame1)
            frame1 = frame2
            ret, frame2 = self.cam.read()

            # Check keys pressed
            if kb.is_pressed("shift+1"):
                self.mode = "D"
            elif kb.is_pressed("shift+2"):
                self.mode = "M"
            elif kb.is_pressed("shift+3"):
                self.mode = "Q"
            elif kb.is_pressed("t"):
                self.take_picture()
            elif kb.is_pressed("shift+5"):
                if self.flip == True:
                    self.flip = False
                    time.sleep(1)
                else:
                    self.flip = True
                    time.sleep(1)
            if self.flip == True:
                frame1 = cv2.rotate(frame1, cv2.ROTATE_180)

            # Switch to close camera
            if cv2.waitKey(40) == 27:
                break

        cv2.destroyAllWindows()
        self.cam.release()

    def take_picture(self):
        ret, frame = self.cam.read()
        ret, jpeg = cv2.imencode(".jpg", frame)
        today_date = datetime.now().strftime("%m%d%Y-%H%M%S")
        cv2.imwrite(self.images_path + "/image" + str(self.count) + "_" + today_date + ".jpg", frame)
        print("Photo taken")
        self.count += 1