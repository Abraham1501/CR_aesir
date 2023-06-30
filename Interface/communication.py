import socket
import logging
import asyncio
import time


class CommunicationPy():
    def __init__(self):
        self.SERVER = "169.254.129.130"
        self.PORT = 5556
        self.HEADER = 64
        self.FORMAT = 'utf-8'
        # Setup logger
        self.logger = logging.getLogger(__name__)


    def revc(self):
        try:
            while True:
                time.sleep(0.05)
                msg = self.client.recv(self.HEADER).decode(self.FORMAT).rstrip()
                self.client.send(b'D')
                if msg:
                    #msg_length = len(msg)
                    #msg = self.client.recv(msg_length).decode(self.FORMAT).rstrip()
                    #conec.send("Msg received".encode(self.FORMAT))
                    self.logger.info(msg)
                    self.logger.info(msg)
        except ConnectionResetError:
            self.logger.info("Disconnected")
            #self.client.close()
            raise ConnectionRefusedError

    def main(self):



        while True:
            try:
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.ADDR = (self.SERVER, self.PORT)
                self.client.connect(self.ADDR)
                self.logger.info(f'Connect {self.ADDR}')
                self.revc()
            except ConnectionRefusedError:
                self.logger.info("Not connected")
                time.sleep(3)
            except OSError:
                self.logger.info("OSError")
                time.sleep(3)