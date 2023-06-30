#Code that reads qr
import cv2
import numpy as np
import pyzbar.pyzbar
import webbrowser
from datetime import datetime

#path for save images (it has to be updated every time it gets on a new device)
images_path = r"C:\Users\odinh\OneDrive\Escritorio\Code_robot_client\images"

count = 0

def QR(image,font, cam):
    #Read QR
    decodeObjects = pyzbar.pyzbar.decode(image)

    for obj in decodeObjects:
        print("Data", obj.data)
        Data = str(obj.data)
        #if a link, open the link on the browser
        if Data[2] == "h":
            webbrowser.open(Data, 0, True)

        cv2.putText(image, str(obj.data), (50, 50), font, 2, (255, 0, 0), 3)
        #take image when read a QR
        take_picture(cam)
    return image

def take_picture(cam):
    ret, frame = cam.read()
    ret, jpeg = cv2.imencode(".jpg", frame)
    today_date = datetime.now().strftime("%m%d%Y-%H%M%S")
    cv2.imwrite(images_path + "/image" + str(count) + "_" + today_date + ".jpg", frame)
    print("Photo taken")