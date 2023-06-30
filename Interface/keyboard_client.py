#Conect the keyboard with Raspberry
import socket
import time
from pynput import keyboard
import logging

#This file the antivirus as malwere, you have to give him permission
class keyboard_c():
    def __init__(self):
        #server variales and send messwwwswwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwages
        self.PORT = 5555
        self.SERVER = "169.254.129.130"
        self.FORMAT = 'utf-8'
        self.HEADER = 64
        #keys listww
        self.keysend = ["W","S","A","D","Q","E","G","H","J", "P", "K", "R", "L", "I", "M", "T", "TAB","SPACE", "KP0","KP1", "KP2", "KP4", "KP6", "KP7", "KP8", "KP9"]
        self.keys = ["'w'", "'s'", "'a'", "'d'", "'q'", "'e'", "'g'","'h'","'j'", "'p'", "'k'", "'r'", "'l'", "'i'", "'m'", "'t'", "Key.tab", "Key.space", "Key.insert","Key.end", "Key.down"
            ,"Key.left", "Key.right", "Key.home", "Key.up", "Key.page_up"]
        self.keystatus = [False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False]
        # Setup logger
        self.logger = logging.getLogger(__name__)

    #send the keys pressed
    def send(self, msg):

        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)
        msg = self.client.recv(2048).decode(self.FORMAT)
        self.logger.info(msg)

    # detct keys pressed
    def press_k(self, k):
        k = str(k)
        self.logger.info(k)
        for key in self.keys:
            if k == key:
                if self.keystatus[self.keys.index(key)] == False:
                    self.keystatus[self.keys.index(key)] = True
                    msg = 'D_' + str(self.keysend[self.keys.index(key)])
                    self.logger.info(msg)
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
                    self.logger.info(msg)
                    self.send(msg)
    def main(self):
        #Star conection with server

        while True:
            try:
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.ADDR = (self.SERVER, self.PORT)
                self.client.connect(self.ADDR)
                self.logger.info(f'Connect {self.ADDR}')
                self.logger.info(f'Connect {self.ADDR} - keyboard')
                #funtion detect keyboard
                with keyboard.Listener(on_press=self.press_k, on_release=self.release_k) as listener: listener.join()
            except ConnectionRefusedError:
                self.logger.info(f'Refused')
                time.sleep(3)
            except ConnectionAbortedError:
                self.logger.info(f'Aborted')
                time.sleep(3)
            except OSError:
                self.logger.info(f'OSError')
                time.sleep(3)