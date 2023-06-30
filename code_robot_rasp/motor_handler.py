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
        
        self.speeds = [1023, 512, 256]
        
        self.selected = 1
        
        self.maxSpeed = 1023
        
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
        
        if (self.maxSpeed == 1023 and speed > 0) or (self.maxSpeed == 0 and speed < 0):
            return
        
        self.maxSpeed += speed
        
        if self.maxSpeed > 1023:
            self.maxSpeed = 1023
            
        if self.maxSpeed < 0:
            self.maxSpeed = 0
        
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
                sendL += 1024
            
            if rightN:
                sendR += 1024
            
            hex1 = "0" * (4 - (len(str(sendR)))) + str(sendR)
            hex2 = "0" * (4 - (len(str(sendL)))) + str(sendL)
    
            send = (hex1 + hex2)
            
            return f"M{send}"
        
        return ""
        #self.ser.write(send.encode() + b'\n')
        
        
            
        
            
        
        
    
        








