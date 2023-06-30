#!/usr/bin/env python3
from motor_handler import MotorHandler
from servo_handler import ServoHandler
from websocket_process import WebSocketProcess
#from keyboard import server_keyboard
from evdev import InputDevice, categorize, ecodes
import threading
import keyboard
import websockets
import serial
import socket
import multiprocessing
import asyncio
import os
import json
import math
import atexit
import logging

class ARM_MODES:
    SHOULDER = 1
    ELBOW = 2
    WRIST = 3

ARM = "ARM_MODE"
FLAG_ARM = "ARM_MODE_FLAG"


class ControlReceiver(WebSocketProcess):
    def __init__(self, mpid, pipe, ser, ip):
        WebSocketProcess.__init__(self, mpid, pipe, ip, 5555)
        
        self.ser = ser

        #if keyboard is not None:
        #    self.dev = InputDevice(keyboard)
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        # Create MotorHandler object to handle motors
        self.motors: MotorHandler = MotorHandler(self.ser)
        self.servos: ServoHandler = ServoHandler(self.ser)
          # self.servos: ServoHandler = ServoHandler(self.config)
        # When script exits or is interrupted stop all servos
          #atexit.register(self.motors.close)
          #atexit.register(self.motors.close_paddle)
        # Default controller state object
        
        self.logger.info("Starting controller branch")
        
        #self.func = self.awaiting()
        #asyncio.run(self.func)

    def key_handler(self, press, key):
        # self.logger.info('Key pressed')
        
        try:
                # Takes the message until the : if there is one
                key = key[key.index('_') + 1:]
                # The index of the string that contains ':'
        except ValueError:
            pass
        
        if (press):
            self.logger.info(f"{key}")
        
        if key == 'W':
            self.motors.keys[0] = press
            self.motors.update()
            
        elif key == 'A':
            self.motors.keys[1] = press
            self.motors.update()
            
        elif key == 'S':
            self.motors.keys[2] = press
            self.motors.update()
            
        elif key == 'D':
            self.motors.keys[3] = press
            self.motors.update()
            
        elif key == 'E':
            self.servos.keys[0] = press
            self.servos.update()
            
        elif key == 'Q':
            self.servos.keys[1] = press
            self.servos.update()
            
        elif key == 'KP2':
            self.servos.keys[2] = press
            self.servos.update()
            
        elif key == 'KP8':
            self.servos.keys[3] = press
            self.servos.update()
            
        elif key == 'KP1':
            self.servos.keys[4] = press
            self.servos.update()
            
        elif key == 'KP0':
            self.servos.keys[5] = press
            self.servos.update()
            
        elif key == 'KP6':
            self.servos.keys[6] = press
            self.servos.update()
            
        elif key == 'KP4':
            self.servos.keys[7] = press   
            self.servos.update()
            
        elif key == 'KP9':
            if press:
                self.servos.preposition(6)
            
        elif key == 'KP7':
            if press:
                self.servos.preposition(9)
            
        elif key == 'TAB':
            if press:
                self.servos.alternate_speed()
            
        elif key == 'SPACE':
            if press:
                self.motors.alternate_speed()
        
        elif key == 'P':
            if press:
                self.ser.write(b'P')
        
        elif key == 'G':
            if press:
                self.servos.preposition(0)
                
        elif key == 'H':
            if press:
                self.servos.preposition(1)
                
        elif key == 'J':
            if press:
                self.servos.preposition(2)
        
        elif key == 'K':
            if press:
                self.servos.preposition(3)

        elif key == 'R':
            if press:
                self.servos.preposition(4)
        
        elif key == 'L':
            if press:
                self.servos.preposition(5)

        elif key == 'T':
            if press:
                self.servos.preposition(8)

        elif key == 'M':
            if press:
                self.servos.preposition(7)

        elif key == 'I':
            if press:
                self.servos.alternate_info()
        
                
        
        #self.logger.info(key)
    
    async def main(self, server):
        HEADER = 64
        FORMAT = 'utf-8'
        server.listen()
        try:
            while True:
                await asyncio.sleep(0.05)
                self.logger.info('awaiting')
                conec, addr = server.accept()
                self.logger.info(f"[NEW CONECTION] {addr} conneted.")
                send = ""
                try:
                    while True:
                        await asyncio.sleep(0.005)
                        
                        append = str(self.motors)
                        
                        if append != "":
                            send = f"{send} {append}"
                                    
                        append = str(self.servos)
                                
                        if append != "":
                            send = f"{send} {append}"
                                    
                        try:
                            if send != "":
                                #self.logger.info(send)
                                
                                send = f"{send}"

                                self.ser.write(send.encode())

                                send = ""
                        except (serial.serialutil.SerialException):
                            pass

                        msg_length = conec.recv(HEADER).decode(FORMAT)
                        if msg_length:
                            msg_length = int(msg_length)
                            msg = conec.recv(msg_length).decode(FORMAT)
                            
                            conec.send("Msg received".encode(FORMAT))
                            msg = str(msg)
                            if msg[0] == "U":
                                self.key_handler(False, msg)
                            else:
                                self.key_handler(True, msg)
                except ConnectionResetError:
                    self.logger.info("Disconnected")
                    conec.close()
        except KeyboardInterrupt: 
            self.running = False
            multiprocessing.current_process().terminate()
    
    def server(self):
        
        ADDR =(self.ip, self.port)
        self.logger.info('passed')
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.logger.info('entered')
        server.bind(ADDR)
        
        asyncio.get_event_loop().run_until_complete(self.main(server))
        asyncio.get_event_loop().run_forever()
            
    """     
    async def awaiting(self):
        
        send = ""
        self.logger.info('key')
        while True:
            
            async for event in self.dev.async_read_loop():
                
                await asyncio.sleep(0.005)
                
                append = str(self.motors)
                
                if append != "":
                    send = f"{send} {append}"
                            
                append = str(self.servos)
                        
                if append != "":
                    send = f"{send} {append}"
                            
                try:
                    if send != "":
                        #self.logger.info(send)
                        self.ser.write(send.encode() + b'\n')
                        send = ""
                except (SerialException):
                    pass
                
                if event.type == ecodes.EV_KEY:
                    
                    key_event = categorize(event)
                    
                    if key_event.keystate == key_event.key_down:
                        self.key_handler(True, str(key_event.keycode))
                        self.logger.info(f"Key pressed:  {str(key_event.keycode)}")
                        
                    elif key_event.keystate == key_event.key_up:
                        self.key_handler(False, str(key_event.keycode))
                        #self.logger.info(f"Key released:  {str(key_event.keycode)}")
        """
