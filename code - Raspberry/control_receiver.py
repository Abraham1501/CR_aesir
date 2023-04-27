#!/usr/bin/env python3
from motor_handler import MotorHandler
from servo_handler import ServoHandler
from websocket_process import WebSocketProcess
#from keyboard import server_keyboard
from evdev import InputDevice, categorize, ecodes
import threading
import keyboard
import websockets
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
    def __init__(self, mpid, pipe, ser, ip, keyboard):
        WebSocketProcess.__init__(self, mpid, pipe, ip, 5555)
        
        self.ser = ser
        
        if keyboard is not None:
            self.dev = InputDevice(keyboard)
        
        self.speedR = 0 
        self.speedL = 0
        self.maxSpeed = 127
        
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
        self.state = {
            "LEFT_STICK_X": 0.0,
            "LEFT_STICK_Y": 0.0,
            "RIGHT_STICK_X": 0.0,
            "RIGHT_STICK_Y": 0.0,
            "LEFT_BOTTOM_SHOULDER": 0.0,
            "RIGHT_BOTTOM_SHOULDER": 0.0,
            "LEFT_TOP_SHOULDER": False,
            "RIGHT_TOP_SHOULDER": False,
            "ARM_MODE": ARM_MODES.SHOULDER,
            "ARM_MODE_FLAG": False,
            "GRIPPER": False,
        }
        
        self.logger.info("Starting controller branch")
        
        #self.func = self.awaiting()
        #asyncio.run(self.func)
        
        

    def set_arm_mode(self, mode):
        self.state[FLAG_ARM] |= self.state[ARM] != mode
        self.state[ARM] = mode


    def gamepad_movement_handler(self, type="TRIGGER"):
        if type == "TRIGGER":
            # Set speed range to be from 0 to `speed`
              #left = self.state["LEFT_BOTTOM_SHOULDER"] * self.motors.speed
              #right = self.state["RIGHT_BOTTOM_SHOULDER"] * self.motors.speed

            # If modifier pressed, then invert value
            left *= (-1) ** self.state["LEFT_TOP_SHOULDER"]
            right *= (-1) ** self.state["RIGHT_TOP_SHOULDER"]

            # Send command to servo handler, independent flag allows the two sides to operate independently
              #self.motors.move(left, right, independent=True)
        else:
            x = self.state["LEFT_STICK_X"] * -1
            y = self.state["LEFT_STICK_Y"] * -1
            # Convert to polar
            r = math.hypot(y, x)
            t = math.atan2(x, y)
            # Rotate by 45 degrees
            t += math.pi / 4
            # Back to cartesian
            left = r * math.cos(t)
            right = r * math.sin(t)
            # Rescale the new coords
            left *= math.sqrt(2)
            right *= math.sqrt(2)
            # Clamp to -1/+1
            left = max(-1, min(left, 1))
            right = max(-1, min(right, 1))
            # Multiply by speed to get our final speed to be sent to the servos
              #left *= self.motors.speed
              #right *= self.motors.speed
            # Send command to servos
              #self.motors.move(left, right)

    def arm_movement_handler(self):
        vel = 0
        if abs(self.state["RIGHT_STICK_Y"]) > 0.5:
            vel = math.copysign(1, self.state["RIGHT_STICK_Y"])
        if self.state[ARM] == ARM_MODES.SHOULDER:
        #    self.servos.move(int(self.config["arm"]["shoulder"]), vel)
            pass
        elif self.state[ARM] == ARM_MODES.ELBOW:
        #    self.servos.move(int(self.config["arm"]["elbow"]), vel)
            pass
        elif self.state[ARM] == ARM_MODES.WRIST:
        #    self.servos.move(int(self.config["arm"]["wrist"]), vel)
            pass


    def keyboard_handler(self, control, value):
        #speed = self.motors.speed
        if control == "FORWARD":
        #    self.motors.move(speed, speed)
            pass
        elif control == "BACKWARDS":
        #    self.motors.move(-speed, -speed)
            pass
        elif control == "LEFT":
        #    self.motors.move(-speed, speed)
            pass
        elif control == "RIGHT":
        #    self.motors.move(speed, -speed)
            pass
        elif control == "STOP":
        #    self.motors.move(0, 0)
            pass
        elif control == "SPEED_UP":
            if value == "DOWN":
        #        self.motors.speed = min(1023, speed + 128)
                # Send a message to SensorStream to update the interface with the current speed
        #        self.pipe.send(["SYNC_SPEED", self.motors.speed])
                pass
        elif control == "SPEED_DOWN":
            if value == "DOWN":
        #        self.motors.speed = max(127, speed - 128)
                # Send a message to SensorStream to update the interface with the current speed
        #        self.pipe.send(["SYNC_SPEED", self.motors.speed])
                pass
        elif control == "PADDLE_FORWARD":
            if value == "DOWN":
        #        self.motors.move_paddle(speed)
                pass
            else:
        #        self.motors.stop_paddle()
                pass
        elif control == "PADDLE_REVERSE":
            if value == "DOWN":
        #        self.motors.move_paddle(-speed)
                pass
            else:
        #        self.motors.stop_paddle()
                pass
        elif control == "ENTER":
            if value == "DOWN":
                self.state["ARM"] = not self.state["ARM"]
        elif control == "HOME":
            if value == "DOWN":
                self.logger.info("GOING HOME")
            #    self.servos.go_to_pos(int(self.config["arm"]["elbow"]), 4800)
                self.logger.info("GOING HOME: 1")
            #    self.servos.go_to_pos(int(self.config["arm"]["shoulder"]), 3712)
                self.logger.info("GOING HOME: 2")
            #    self.servos.go_to_pos(int(self.config["arm"]["wrist"]), 3456)
                self.logger.info("GOING HOME: 3")
            #    self.servos.go_to_pos(int(self.config["arm"]["elbow"]), 3776)
                self.logger.info("GOING HOME: 4")
            #    self.servos.go_to_pos(int(self.config["arm"]["gripper"]), 4112)
                self.logger.info("GOING HOME: 5")
        elif control == "MAPPING":
            if value == "DOWN":
                self.logger.info("GOING MAPPING")
            #    self.servos.go_to_pos(int(self.config["arm"]["elbow"]), 4800)
                self.logger.info("GOING MAPPING: 1")
            #    self.servos.go_to_pos(int(self.config["arm"]["wrist"]), 3724)
                self.logger.info("GOING MAPPING: 2")
            #    self.servos.go_to_pos(int(self.config["arm"]["shoulder"]), 5960)
                self.logger.info("GOING MAPPING: 3")
            #    self.servos.go_to_pos(int(self.config["arm"]["elbow"]), 3820)
                self.logger.info("GOING MAPPING: 4")
            #    self.servos.go_to_pos(int(self.config["arm"]["gripper"]), 4112)
                self.logger.info("GOING MAPPING: 5")
        elif control == "RUNNING":
            if value == "DOWN":
                self.logger.info("GOING EXPLORING")
            #    self.servos.go_to_pos(int(self.config["arm"]["elbow"]), 4800)
                self.logger.info("GOING EXPLORING (but with the camera and without mapping): 1")
            #    self.servos.go_to_pos(int(self.config["arm"]["wrist"]), 5600)
                self.logger.info("GOING EXPLORING (but with the camera and without mapping): 2")
            #    self.servos.go_to_pos(int(self.config["arm"]["shoulder"]), 3712)
                self.logger.info("GOING EXPLORING (but with the camera and without mapping): 3")
            #    self.servos.go_to_pos(int(self.config["arm"]["elbow"]), 3776)
                self.logger.info("GOING EXPLORING (but with the camera and without mapping): 4")
            #    self.servos.go_to_pos(int(self.config["arm"]["gripper"]), 4112)
                self.logger.info("GOING EXPLORING (but with the camera and without mapping): 5")

    def message_handler(self, buf):
        # Load object from JSON
        msg = json.loads(buf)

        typ = msg["type"]  # axis, button, or keyboard
        control = msg["control"]  # FACE_0, LEFT_STICK_Y, SPEED_UP etc.

        if typ == "KEYBOARD":
            value = msg["value"] if "value" in msg else False  # UP, DOWN
            # Handle directional movement etc
            self.keyboard_handler(control, value)
        elif typ == "BUTTON":
            value = msg["value"]  # UP, DOWN
            # Store in state, because it might be useful (e.g. for modifiers)
            self.state[control] = True if value == "DOWN" else False
            # 
            if control == "LEFT_TOP_SHOULDER" or control == "RIGHT_TOP_SHOULDER":
                self.gamepad_movement_handler(type="TRIGGER")
            # Then handle any button events
            if control == "DPAD_LEFT":
                if value == "DOWN":
            #        self.motors.speed = min(1023, self.motors.speed + 128)
            #        self.pipe.send(["SYNC_SPEED", self.motors.speed])
                    pass
            elif control == "DPAD_RIGHT":
                if value == "DOWN":
            #        self.motors.speed = max(127, self.motors.speed - 128)
            #        self.pipe.send(["SYNC_SPEED", self.motors.speed])
                    pass
            elif control == "DPAD_UP":
                if value == "DOWN":
            #        self.keyboard_handler("PADDLE_FORWARD", self.motors.speed)
                    pass
                elif value == "UP":
            #        self.motors.stop_paddle()
                    pass
            elif control == "DPAD_DOWN":
                if value == "DOWN":
            #        self.keyboard_handler("PADDLE_REVERSE", self.motors.speed)
                    pass
                elif value == "UP":
            #        self.motors.stop_paddle()
                    pass
            # TOGGLE GRIPPER
            elif control == "FACE_3":
                if value == "DOWN":
                    self.state["GRIPPER"] = not self.state["GRIPPER"]
            #ARM MODES
            elif control == "FACE_3":
                if value == "DOWN":
                    self.set_arm_mode(ARM_MODES.SHOULDER)
            elif control == "FACE_1":
                if value == "DOWN":
                    self.set_arm_mode(ARM_MODES.ELBOW)
            elif control == "FACE_3":
                if value == "DOWN":
                    self.set_arm_mode(ARM_MODES.WRIST)
        elif typ == "AXIS":
            # If axis, store as float
            value = float(msg["value"])
            # Update state with new value of axis
            self.state[control] = value
            # Handle trigger and stick controls
            if control == "LEFT_STICK_X" or control == "LEFT_STICK_Y":
                self.gamepad_movement_handler(type="STICK")
            elif control == "RIGHT_STICK_X":
                if self.state["GRIPPER"] and abs(self.state["RIGHT_STICK_X"]) > 0.5:
            #        self.servos.move(int(self.config["arm"]["gripper"]), math.copysign(1, self.state["RIGHT_STICK_X"]))
                    pass
            elif control == "RIGHT_STICK_Y":
                self.arm_movement_handler()
            else:
                self.gamepad_movement_handler(type="TRIGGER")

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
            
        elif key == 'KP0':
            self.servos.keys[4] = press
            self.servos.update()
            
        elif key == 'KP1':
            self.servos.keys[5] = press
            self.servos.update()
            
        elif key == 'KP6':
            self.servos.keys[6] = press
            self.servos.update()
            
        elif key == 'KP4':
            self.servos.keys[7] = press   
            self.servos.update()
            
        elif key == 'KP9':
            self.servos.keys[8] = press
            self.servos.update()
            
        elif key == 'KP7':
            self.servos.keys[9] = press 
            self.servos.update()
            
        elif key == 'TAB':
            if press:
                self.servos.alternate_speed()\
            
        elif key == 'SPACE':
            if press:
                self.motors.alternate_speed()
        
        elif key == 'P':
            if press:
                self.ser.write(b'ping\n')
        
        elif key == 'G':
            if press:
                self.servos.preposition(0)
                
        elif key == 'H':
            if press:
                self.servos.preposition(0)
                
        elif key == 'J':
            if press:
                self.servos.preposition(0)
                
        
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
                print(f"[NEW CONECTION] {addr} conneted.")
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
                                self.ser.write(send.encode() + b'\n')
                                send = ""
                        except (SerialException):
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
        
