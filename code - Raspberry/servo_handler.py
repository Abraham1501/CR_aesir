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
        
        self.speeds = [15, 10, 5, 20]
        
        self.maxSpeed = 15
        
        self.selected = 0
        
        self.lastPos = ''
        
        self.updateable = False
        self.speedChange = False
        self.rePos = False
        
    
        
    def update(self):
        
        for i in range(0, len(self.dirs)):
            add = 0
            
            for j in range(1, 3):
                #self.logger.info(f"{i*2 + j -1} is {self.keys[i*2 + j -1]}, with {j}")
                if self.keys[i*2 + j - 1]:
                    add += j
            
            self.dirs[i] = add
            
            #self.logger.info(self.dirs[i])
            
        
        self.updateable = True
        
    def alternate_speed(self):
        
        self.maxSpeed = self.speeds[self.selected]
        
        self.selected += 1
        
        if self.selected == len(self.speeds):
            self.selected = 0
            
        self.speedChange = True
        
    def preposition(self, num):
        self.rePos = True
        self.lastPos = ''
        if(num == 0):
            self.lastPos = f"{self.lastPos}{hex(90)[2:].zfill(2).upper()}" # 3
            self.lastPos = f"{self.lastPos}{hex(0)[2:].zfill(2).upper()}" # 2
            self.lastPos = f"{self.lastPos}{hex(20)[2:].zfill(2).upper()}" # 1
            self.lastPos = f"{self.lastPos}{hex(90)[2:].zfill(2).upper()}" # 0
            
        elif(num == 1):
            self.lastPos = f"{self.lastPos}{hex(90)[2:].zfill(2).upper()}" # 3
            self.lastPos = f"{self.lastPos}{hex(90)[2:].zfill(2).upper()}" # 2
            self.lastPos = f"{self.lastPos}{hex(90)[2:].zfill(2).upper()}" # 1
            self.lastPos = f"{self.lastPos}{hex(90)[2:].zfill(2).upper()}" # 0
            
        elif(num == 3):
            self.lastPos = f"{self.lastPos}{hex(90)[2:].zfill(2).upper()}" # 3
            self.lastPos = f"{self.lastPos}{hex(0)[2:].zfill(2).upper()}" # 2
            self.lastPos = f"{self.lastPos}{hex(45)[2:].zfill(2).upper()}" # 1
            self.lastPos = f"{self.lastPos}{hex(90)[2:].zfill(2).upper()}" # 0
    
    def __str__(self):
        send = ''
        
        if(self.updateable):
            self.updateable = False
            
            send = 'S'
            
            for n in self.dirs:
                send = f"{send}{n}"
                
            #self.logger.info(f"Sending {send}")
            
        if(self.speedChange):
            self.speedChange = False
            send = f"{send} SS{hex(self.maxSpeed)[2:].zfill(2).upper()}"
            
        if(self.rePos):
            self.rePos = False
            send = f"{send} SP{self.lastPos}"
            
        
        return send
        #self.ser.write(send.encode() + b'\n')
        
        
            
        
            
        
        
    
        








