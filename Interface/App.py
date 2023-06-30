import tkinter as tk
import logging
import multiprocessing_logging
import threading
import sys
import time
import socket
from camera import Camera
from PIL import Image
from PIL import ImageTk
 

class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.wm_title("Aesir interface")
        self.wm_protocol("WM_DELETE_WINDOW", self.onClose)
        self.geometry("1920x1080")
        self.attributes('-fullscreen', True)
        
        self.logger = logging.getLogger(__name__)
        self.mainFrame = tk.Frame(self, background="gray")
        self.mainFrame.pack(fill="both", expand=True)

        #self.mainFrame.bind("<key>", self.keyhand)

        self.SERVER = "169.254.129.130"


        self.thread = None
        self.Event = None
        self.visual = None

        self.create_widgets()

    def create_widgets(self):

        #Background thing

        self.bg = Image.open("image/background.jpeg")
        self.bg = self.bg.resize((1536, 864))
        self.bg = ImageTk.PhotoImage(self.bg)

        self.background = tk.Label(self.mainFrame, image=self.bg, borderwidth=0)

        self.background.place(x=0, y=0)


        #Camera image
        self.feed = Camera(self.mainFrame, 768, 432, 0)
        self.feed.pack(pady=30, side="top")

        #Server connection
    

    def onClose(self):
        self.feed.stopCam()

        self.quit()

        




logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

# Ensure multiprocessing compatibility
multiprocessing_logging.install_mp_handler()
logger = logging.getLogger(__name__)

app = Application()

app.mainloop()


# root.after(time, function) calls a function after some time