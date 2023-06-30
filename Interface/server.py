import logging
import tkinter
import socket
import time
import threading


class Server():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.SERVER = '169.254.129.130'
        self.conection = threading.Event()
        self.threadSen = threading.Thread(target=self.senServer, args=())
        self.threadKey = threading.Thread(target=self.keyserver, args=())

        #Decoration

        

    
    def start(self):
        self.threadSen.start()
        self.threadKey.start()


    def changeSer(self, ip):
        self.SERVER = ip
        self.start()


    def keyserver(self):
        #Keyboard connect
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ADDR = (self.SERVER, 5555)
            self.client.connect(self.ADDR)
            
            self.logger.info(f'Connect {self.ADDR}')
            while not self.conection.is_set():
                pass
        except ConnectionRefusedError:
            self.logger.info(f'Refused')
        except ConnectionAbortedError:
            self.logger.info(f'Aborted')
        except OSError:
            self.logger.info(f'OSError')

        self.client.close()

    
    def press_k(self, k):
        k = str(k)
        self.logger.info(k)
        for key in self.keys:
            if k == key:
                if self.keystatus[self.keys.index(key)] == False:
                    self.logger.info(k)
                    self.keystatus[self.keys.index(key)] = True
                    msg = 'D_' + str(self.keysend[self.keys.index(key)])
                    self.logger.info(msg)
                    self.send(msg)

    # detect keys release
    def release_k(self,k):
        k = str(k)
        self.logger.info(k)
        for key in self.keys:
            if k == key:
                if self.keystatus[self.keys.index(key)] == True:
                    
                    self.keystatus[self.keys.index(key)] = False
                    msg = 'U_' + str(self.keysend[self.keys.index(key)])
                    self.logger.info(msg)
                    self.send(msg)

    
    def senServer(self):

        #Message receiver connect
        try:
            self.clientk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.ADDR = (self.SERVER, 5556)
            self.clientk.connect(self.ADDR)
            
            self.logger.info(f'Connect {self.ADDR}')
            while not self.conection.is_set():
                time.sleep(0.05)
                msg = self.clientk.recv(64).decode('utf-8').rstrip()
                self.clientk.send(b'D')
                if msg:
                    #msg_length = len(msg)
                    #msg = self.client.recv(msg_length).decode(self.FORMAT).rstrip()
                    #conec.send("Msg received".encode(self.FORMAT))
                    self.logger.info(msg)
        except ConnectionRefusedError:
            self.logger.info("Not connected")
            time.sleep(3)
        except OSError:
            self.logger.info("OSError")
            time.sleep(3)

        self.clientk.close()