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
#keyboard = '/dev/input/event0'

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
        self.control_process = ControlReceiver(2, self.control_pipe, self.ser, ip)
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
        
        open_port = None
        for port in ports:
            
            if port.description == "ROBOTIS ComPort":
                open_port = port.device
                ser = serial.Serial(port.device, 9600, timeout = 1)
                ser.flush()
                break

        if open_port is not None:
            logger.info(f"OpenCM conected at: {open_port}")
        else:
            logger.info("OpenCM not connected.")
            raise serial.serialutil.SerialException
        
        manager = Manager(logger, ser)
        
        # Main program loop
        manager.run()
        
    except serial.serialutil.SerialException:
        logger.error("Exiting the main program")
