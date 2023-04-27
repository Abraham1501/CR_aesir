#Main code to control the robot with keyboard of computer and camera
import threading
from keyboard_client import keyboard_c
from camera import Camera

#Initial variables
keys = keyboard_c()
cam = Camera()

def keyboard():
    keys.main()

def camera():
    cam.main()

if __name__ =="__main__":
    #start process thearding
    t1 = threading.Thread(target=keyboard)
    t2 = threading.Thread(target=camera)
    print("Starting...")
    t1.start()
    t2.start()
    t1.join()
    t2.join()