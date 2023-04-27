#!/usr/bin/env python3
from multiprocessing import Pipe
from control_receiver import ControlReceiver
from sensor_stream import SensorStream
import evdev
import time
import signal
import sys
import os
import json
import serial
import serial.tools.list_ports
import logging
import time
import multiprocessing_logging
from plugin_system import PluginManager
from sensor_wrapper import SensorWrapper


ip = '169.254.129.130'
#ip = '192.168.0.28'
keyboard = '/dev/input/event0'

#pi_camera = VideoCamera(flip=False, vs=PiVideoStream().start())

#app = Flask(_name_)

class Manager:
    def __init__(self, logger, ser):
        # Set up the logger
        self.logger = logger
        self.logger.info("Starting main process...")
        
        # Setup the serial port
        self.ser = ser
        

    def terminate(self):
        # Terminate the two processes we spawn

        self.sensor_process.terminate()
        self.control_process.terminate()
        # We should already have joined the processes, but just in case, this ensures we actually terminate
        self.sensor_process.join()
        self.control_process.join()
    

    def sigint(self, signal, frame):
        self.logger.info("Received interrupt signal. Terminating...")
        # Make sure we terminate the child processes to prevent a zombie uprising
        self.terminate()
        # Also kill this process too
        sys.exit(0)

    def run(self):
        # Log process ID to file
        self.logger.debug(f"Process ID (PID): {os.getpid()}")
        # Create pipe. sensor_pipe receives, and control_pipe sends
        self.sensor_pipe, self.control_pipe = Pipe(duplex=False)
        # Create server and receiver processes
        self.sensor_process = SensorStream(1, self.sensor_pipe, self.ser, ip)
        self.control_process = ControlReceiver(2, self.control_pipe, self.ser, ip, keyboard)
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.sigint)
        
        # Start new processes
        self.control_process.start()
        self.sensor_process.start()
        
        # Join new processes to prevent early termination
        self.control_process.join()
        self.sensor_process.join()
        
        # Once both processes have ended, the manager can end too.
        self.logger.info("Exiting main process...")


if __name__ == '__main__':
    
    #threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False)).start()
    levels = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG
    }

    


    # Setup logger
    logging.basicConfig(level = logging.DEBUG, stream=sys.stdout, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    # Ensure multiprocessing compatibility
    multiprocessing_logging.install_mp_handler()
    # This ensures we know which script we are logging from
    logger = logging.getLogger(__name__)

    try:
        # Setup the serial port to the arduino so that it runs
        
        
        
        
        # Get the port list
        ports = list(serial.tools.list_ports.comports())
        
        arduino_port = None
        for port in ports:
            logger.info(port.description)
            ser = serial.Serial(port.device, 9600, timeout = 1)
            ser.flush()
            
            time.sleep(1)
            
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').rstrip()
                logger.info(data)
                if data == 'started':
                    arduino_port = port.device
                    break
                
            
        if arduino_port is not None:
            logger.info(f"Arduino conected at: {arduino_port}")
        else:
            logger.info("There was no arduino connected.")
            raise serial.serialutil.SerialException
        
        
        
    
    
        #devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

        #Filter everything that has the name "keyboard"
        #keyboard_devices = list(filter(lambda dev: 'eyboard' in dev.name.lower(), devices))

        #for device in keyboard_devices:
            # Get the first input event that has the name keyboard 
            # (they are listed backwards so the first one will prevail)

         #   logger.info(f"{device.name} at port {device.path}")
          #  keyboard = device.path
            
        #if keyboard is not None:
        #    logger.info(f"Keyboard is at {keyboard}")
        #else:
        #    logger.info("There was no keyboard")
        
        
        manager = Manager(logger, ser)
        
        # Main program loop
        manager.run()
        
    except serial.serialutil.SerialException:
        logger.error("Exiting the main program")
