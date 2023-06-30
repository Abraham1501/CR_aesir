#!/usr/bin/env python3
#from smbus2 import SMBus
from websocket_process import WebSocketProcess
from sensor_wrapper import SensorWrapper
import importlib
import websockets
import socket
import asyncio
import multiprocessing
#import psutil
import json
import logging
import os
import subprocess
import re
import sys
import inspect
import time
from plugin_system import PluginManager


class SensorStream(WebSocketProcess):
    def __init__(self, mpid, pipe, ser, ip):
        WebSocketProcess.__init__(self, mpid, pipe, ip, 5556)
        # Setup logger
        self.logger = logging.getLogger(__name__)

        # Plan b for when there is no connection
        self.planB = True

        # Create new plugin manager looking for subclasses of SensorWrapper in "src/sensors/"
        self.pm = PluginManager(SensorWrapper, os.getcwd() + "/sensors")
 
        # Create dict to store the number of each type of sensor
        self.sensor_count = {}

        # Create list of sensors
        self.sensors = []
        
        # Serial port
        self.ser = ser
        
        # funny hardcode instead of using a config file which i could have done perfectly
        self.list = [('cpu_temp', True, 1), ('co2', True, 1)]
        # self.list = []
        
        for sensor_config in self.list:
            #if sensor_config.get('enabled', False):
                # Find the appropriate wrapper class and create the sensor object
                type_ = sensor_config[0]
                sensor = self.pm.wrappers[type_](sensor_config[1], sensor_config[2], sensor_config[0])
                # Count the number of times we create a sensor of this type, to assign a unique id
                if type_ not in self.sensor_count:
                    self.sensor_count[type_] = 1
                else:
                    self.sensor_count[type_] += 1
                # Assign index
                sensor.index = self.sensor_count[type_]
                # Add to list of sensors
                self.sensors.append(sensor)
                self.logger.info(f"Created sensor of type '{type_}' (#{sensor.index})")
        self.logger.info(f"Loaded {len(self.sensors)} sensors")


        #asyncio.run(self.func)

    def get_data(self):
        # Create empty message
        msg = {}

        # Ensure that the time is the same across sensors
        now = time.time()

        
        
        # Get data from each Sensor
        for sensor in self.sensors:
            # Ensure time elapsed is greater than period
            if sensor.is_ready(now):
                data = sensor.get_data()
                # Make sure we actually got data from the sensor
                if data is not None:
                    # Generate UID for sensor
                    uid = f"{sensor.type_}_{sensor.index}"
                            
                    # Any sensor data handled automatically (anything in this for loop) goes in the "sensor_data" dict
                    if "sensor_data" not in msg:
                        msg["sensor_data"] = {}
                    # Create message
                    if uid is not None:
                        msg["sensor_data"][uid] = data
        try:
            while self.ser.in_waiting > 0:
                data = self.ser.readline().decode('utf-8').rstrip()
                uid = None
                try:
                    # Takes the message until the : if there is one
                    
                    ind = data[:data.index(':')]
                    
                    # The index of the string that contains ':'
                    source = data.index(':') + 1
                    
                    # If the message starts with C:
                    if ind == 'l':
                        if len(data) > source:
                            data = data[source:]
                            uid = 'load'
                    if ind == 'p':
                        if len(data) > source:
                            data = data[source:]
                            uid = 'pos'
                    if ind == 'v':
                        if len(data) > source:
                            data = data[source:]
                            uid = 'volt'
                    if ind == 't':
                        if len(data) > source:
                            data = data[source:]
                            uid = 'temp'
                    if ind == 'e':
                        if len(data) > source:
                            data = data[source:]
                            uid = 'err'
                    
                    
                except ValueError:
                    # If it does not have a ':'
                    self.logger.info(data)
                
                if uid is not None:  
                    if "sensor_data" not in msg:
                        msg["sensor_data"] = {}
                        # Create message
                    
                    msg["sensor_data"][uid] = data
        except(OSError):
            self.logger.info({"OpenCM disconnected"})
            pass
        # Print out each message if print_messages is enabled
        # Return message to be sent to control panel
        return json.dumps(msg)

    def send(self, msg):
        try:
            message = msg.encode(self.FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(self.FORMAT)
            send_length += b' ' * (self.HEADER - len(send_length))
            self.client.send(send_length)
            self.client.send(message)
            # self.logger.info(self.client.recv(2048).decode(self.FORMAT))
            # print(self.client.recv(2048).decode(self.FORMAT))
        except:
            self.logger.info("error send")
            try:
                self.client.connect(self.ADDR)
                self.logger.info(f'Connect {self.ADDR}')
            except:
                self.logger.info(f'error connection - sensor stream')
                time.sleep(1)

    async def main(self, server):
        try:
            HEADER = 64
            FORMAT = 'utf-8'
            server.listen()
            while True:
                try:
                    conec, addr = server.accept()
                    self.logger.info(f"[NEW CONECTION] {addr} conneted.")


                    while True:
                        
                        data = self.get_data()
                        if (data != '{}'):
                            self.logger.info(f"{data}")
                            conec.send(data.encode())
                            confirm = conec.recv(64).decode('utf-8')
                            if not confirm:
                                pass
                            
                        await asyncio.sleep(0.05)

                except BrokenPipeError:
                    self.logger.info("Disconnected")
                    conec.close()
                
                except ConnectionRefusedError:
                    self.logger.info("Disconnected")
                    conec.close()
                
                except ConnectionResetError:
                    self.logger.info("Disconnected")
                    conec.close()
                    

                #except KeyboardInterrupt:
                    #self.logger.info(Going out of awaiting")
                    #break
        except KeyboardInterrupt:
            self.logger.info("Disconect")
            multiprocessing.current_process().terminate()

    
        """
        self.planB = False
        self.logger.info(f"New client connected ({websocket.remote_address[0]})")
        # Store websocket
        self.websocket = websocket
        # Send the initial info to notify interface that the service is ready.
        await self.send_init_info()
        # Enter runtime loop
        while True:
            try:
                # Check if there are messages ready to be received
                if self.pipe.poll():
                    # Handle message (received from control_receiver.py)
                    await self.pipe_message_handler(self.pipe.recv())
                # Send sensor data etc
                data = self.get_data()
                # Make sure data is not empty
                if data != "{}":
                    await websocket.send(data)
                # Short sleep to prevent issues
                await asyncio.sleep(0.05)
            except websockets.exceptions.ConnectionClosed:
                self.logger.info(f"Client disconnected ({websocket.remote_address[0]})")
                self.planB = True
                break
        # Close each sensor
        for sensor in self.sensors:
            sensor.close()
        """

    def server(self):
        self.logger.info(self.ip)
        self.logger.info(self.port)
        ADDR = (self.ip, self.port)
        self.logger.info('passed')
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.logger.info('entered')
        server.bind(ADDR)
        
        asyncio.get_event_loop().run_until_complete(self.main(server))
        asyncio.get_event_loop().run_forever()

    async def awaiting(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ADDR = (self.SERVER, self.PORT)
        while True:
            try:
                self.client.connect(self.ADDR)
                self.logger.info(f'Connect {self.ADDR}')
                while True:
                    try:
                        if self.planB:
                            data = self.get_data()
                        if (data != '{}'):
                            self.logger.info(f"{data}")
                            self.send(data)
                        await asyncio.sleep(0.05)
                    except KeyboardInterrupt:
                        self.logger.info("Disconect")
                        break

                await asyncio.sleep(0.05)    
            except KeyboardInterrupt:
                self.logger.info("Going out of awaiting")
                break
        
                



    
