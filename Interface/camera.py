#Code of camera
import cv2
from motion_detector import motion_detector
from QR import QR
import socket
import time
import logging
import asyncio
import threading
from datetime import datetime
import threading
import tkinter as tk
from PIL import Image
from PIL import ImageTk

class Camera(tk.Label):
    def __init__(self, master, posx, posy, vs):

        self.holder = Image.open("image/holder.jpeg")
        self.holder = self.holder.resize((posx, posy))
        self.holder = ImageTk.PhotoImage(self.holder)

        super().__init__(master=master, image=self.holder, borderwidth=0)
        self.image = self.holder

        self.resolutionX = posx
        self.resolutionY = posy

        self.logger = logging.getLogger(__name__)
        
        self.flipping = False
        self.cam = cv2.VideoCapture(vs)
        self.texts = ["", "Tracking", "Read QR", ""]
        self.text = self.texts[0]
        self.keys = ["'1'", "'2'", "'3'"]
        self.mode = "D"
        self.flip = False
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.count = 1
        # path for save images (it has to be updated every time it gets on a new device)
        self.images_path = r"C:\Users\odinh\OneDrive\Escritorio\Code_robot_client\images"

        self.Event = threading.Event()
        self.thread = threading.Thread(target=self.main_cam, args=())
        self.thread.start()

        

    def main_cam(self):
        
        ret, frame1 = self.cam.read()
        ret, frame2 = self.cam.read()

        while self.cam.isOpened():
            #asyncio.run(self.revc())
            # Check camera mode
            if self.mode == "Q":
                frame1 = QR(frame1, self.font, self.cam)
                #self.text = self.texts[2]
            elif self.mode == "M":
                frame1 = motion_detector(self.cam).frames(frame1, frame2)
                #self.text = self.texts[1]
            else:
                #self.text = self.texts[0]
                pass

            # Show image of camera
            
            #cv2.putText(frame1, self.text, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (200, 100, 100), 4)
            #cv2.putText(frame1, self.texts[3], (1200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (200, 100, 100), 4)
            #cv2.imshow("video", frame1)

            if not self.Event.is_set():
                try:
                    frame1 = cv2.resize(frame1, (self.resolutionX, self.resolutionY), interpolation=cv2.INTER_AREA)
                    frame1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
                    frame1 = Image.fromarray(frame1)
                    frame1 = ImageTk.PhotoImage(frame1)

                    self.configure(image=frame1)
                    self.image = frame1


                    frame1 = frame2
                except:
                    break

                ret, frame2 = self.cam.read()
            else:
                try:
                    self.config(image=self.holder)
                    self.image = self.holder
                    break
                except:
                    break

            # Check keys pressed
            
            if self.flipping:
            
                self.flipping = False
                if self.flip == True:
                    self.flip = False
                    time.sleep(1)
                else:
                    self.flip = True
                    time.sleep(1)
            if self.flip == True:
                frame2 = cv2.rotate(frame2, cv2.ROTATE_180)

            # Switch to close camera
            
        self.cam.release()

    def take_picture(self):
        ret, frame = self.cam.read()
        ret, jpeg = cv2.imencode(".jpg", frame)
        today_date = datetime.now().strftime("%m%d%Y-%H%M%S")
        cv2.imwrite(self.images_path + "/image" + str(self.count) + "_" + today_date + ".jpg", frame)
        self.logger.info("Photo taken")
        self.count += 1


    def stopCam(self):
        self.Event.set()

    def startNewCam(self, vs):
        self.stopCam()

        self.cam = cv2.VideoCapture(vs)

        self.thread = threading.Timer(1.0, target=self.main_cam, args=())

        self.thread.start()

        self.Event.clear()
    

        