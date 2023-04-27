import os
import logging
import time

class MotorHandler:

    def __init__(self, ser):
        
        self.logger = logging.getLogger(__name__)
        
        # setup the serial communication
        self.ser = ser
        
        # Setup the speeds
        self.speedR = 0
        self.speedL = 0
        
        self.keys = [False, False, False, False]
        
        self.speeds = [127, 115, 100]
        
        self.selected = 1
        
        self.maxSpeed = 127
        
        self.updateable = False
        
    
    def change_max_speed(self, speed):
        
        self.maxSpeed = speed
        
        self.update()
        
        
    def alternate_speed(self):
        
        self.maxSpeed = self.speeds[self.selected]
        
        self.selected += 1
        
        if self.selected == len(self.speeds):
            self.selected = 0
        
        self.update()
        
        
    def affect_max_speed(self, speed):
        
        if (self.maxSpeed == 127 and speed > 0) or (self.maxSpeed == 0 and speed < 0):
            return
        
        self.maxSpeed += speed
        
        if self.maxSpeed > 127:
            self.maxSpeed = 127
            
        if self.maxSpeed < 0:
            self.maxSpeed = 0
        
        self.update()
        
        
    def change_speed(self, left, right):
        
        self.speedR = self.maxSpeed * right
        
        self.speedL = self.maxSpeed * left
        
        self.update()
        
        
    def update(self):
        left = 0
        right = 0
        
        if self.keys[0]:
            left += 1
            right += 1
            
        if self.keys[1]:
            left += 1
            right -= 1
            
        if self.keys[2]:
            left -= 1
            right -= 1
            
        if self.keys[3]:
            left -= 1
            right += 1

        self.speedL = self.maxSpeed * left
        self.speedR = self.maxSpeed * right
        
        self.updateable = True
        
    
    def __str__(self):
        
        
        if(self.updateable):
            self.updateable = False
            
            leftN = False
            rightN = False
            
            sendR = self.speedR
            sendL = self.speedL
            
            # self.logger.info(self.speedR)
            # self.logger.info(self.speedL)
            
            if sendL < 0:
                leftN = True
                sendL *= -1
            
            if sendR < 0:
                rightN = True
                sendR *= -1
                
            if sendL > self.maxSpeed:
                sendL = self.maxSpeed
            
            if sendR > self.maxSpeed:
                sendR = self.maxSpeed
            
            if leftN:
                sendL += 128
            
            if rightN:
                sendR += 128
            
            hex1 = hex(sendL)[2:].zfill(2)
            hex2 = hex(sendR)[2:].zfill(2)
    
            send = (hex1 + hex2).upper()
            
            return f"M{send}"
        
        return ""
        #self.ser.write(send.encode() + b'\n')
        
        
            
        
            
        
        
    
        








