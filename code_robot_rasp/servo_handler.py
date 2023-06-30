import os
import logging
import time

class ServoHandler:

    def __init__(self, ser):
        
        self.logger = logging.getLogger(__name__)
        
        # setup the serial communication
        self.ser = ser
        
        
        
        self.keys = [False, False, False, False, False, False, False, False, False, False]
        
        self.dirs = [0, 0, 0, 0, 0]
        
        self.speeds = [133, 67, 266]
        
        self.maxSpeed = 256
        
        self.selected = 0
        
        self.lastPos = ""

        self.sendDir = ""

        self.sendPos = ""
        
        self.speedChange = False
        self.rePos = False

        self.info = ""

        self.iselected = 0

        self.infos = [66, 69, 68, 63]
        
    
        
    def update(self):
        
        for i in range(0, len(self.dirs)):
            add = 0
            
            for j in range(1, 3):
                #self.logger.info(f"{i*2 + j -1} is {self.keys[i*2 + j -1]}, with {j}")
                if self.keys[i*2 + j - 1]:
                    add += j
            if self.dirs[i] != add:
                self.dirs[i] = add
                self.sendDir += " S" + hex(i + 4)[2:].zfill(2).upper() + f"{self.dirs[i]}"
            
            #self.logger.info(self.dirs[i])
             
        
        
    def alternate_speed(self):
        
        self.maxSpeed = self.speeds[self.selected]
        
        self.selected += 1
        
        if self.selected == len(self.speeds):
            self.selected = 0

    
    def alternate_info(self):
        
        self.iselected += 1
        
        if self.iselected == len(self.infos):
            self.iselected = 0

        
            
        self.info = "I" + str(self.infos[self.iselected])
        
    def preposition(self, num):
        self.rePos = True
        if(num == 0):
            # 7  (0-1023)/4
            # 6   (213-833)/4
            # 5  (817-197)/4

            self.lastPos += " SP060213 SP050817 SP040512"
            
        elif(num == 1):
            self.lastPos += " SP060523 SP050507"
            
        elif(num == 2):
            self.lastPos += " SP060679 SP050351"
            
        elif(num == 3):
            self.lastPos += " SP060299 SP050592 S040512"

        elif(num == 4):
            self.lastPos += " SP040512"

        elif(num == 5):
            self.lastPos += " SP080486 SP060833 SP050817 SP040512"
        
        elif(num == 6):
            self.lastPos += " SP080260"

        elif(num == 7):
            self.lastPos += " W01320103"
        
        elif(num == 8):
            self.lastPos += " SP080486"

        elif(num == 9):
            self.lastPos += " SP080760"
        
            
    
    def __str__(self):
        send = ''
        
        if(self.sendDir != ""):
            send += self.sendDir
            self.sendDir = ""
                
            #self.logger.info(f"Sending {send}")
            
        if(self.speedChange):
            self.speedChange = False
            send += " SS" + ("0" * (4 - (len(str(self.maxSpeed))))) + str(self.maxSpeed)
            
        if(self.lastPos != ""):
            send = f"{send} SP{self.lastPos}"
            self.lastPos = ""

        if(self.info != ""):
            send = f"{send} {self.info}"
            self.info = ""

        #self.logger.info(send)
        
        return send
        #self.ser.write(send.encode() + b'\n')
        
        
            
        
            
        
        
    
        








