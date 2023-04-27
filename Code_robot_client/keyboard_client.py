#Conect the keyboard with Raspberry
import socket
from pynput import keyboard

#This file the antivirus as malwere, you have to give him permission
class keyboard_c():
    def __init__(self):
        #server variales and send messages
        self.PORT = 5555
        self.SERVER = "169.254.129.130"
        self.FORMAT = 'utf-8'
        self.HEADER = 64
        #keys list
        self.keysend = ["W","S","A","D","Q","E","G","H","J", "p","SPACE", "KP1", "KP2", "KP4", "KP6", "KP7", "KP8", "KP9"]
        self.keys = ["'w'", "'s'", "'a'", "'d'", "'q'", "'e'", "'g'","'h'","'j'", "'p'", "Key.space", "Key.end", "key.down"
            ,"key.left", "key.right", "key.home", "key.up", "key.page_up"]
        self.keystatus = [False, False, False, False, False, False, False, False, False, False, False, False, False, False,False, False, False]

    #send the keys pressed
    def send(self, msg):
        message = msg.encode(self.FORMAT)
        msg_length = len(message)
        send_length = str(msg_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length))
        self.client.send(send_length)
        self.client.send(message)
        print(self.client.recv(2048).decode(self.FORMAT))

    # detect keys pressed
    def press_k(self, k):
        k = str(k)
        print(k)
        for key in self.keys:
            if k == key:
                if self.keystatus[self.keys.index(key)] == False:
                    self.keystatus[self.keys.index(key)] = True
                    msg = 'D_' + str(self.keysend[self.keys.index(key)])
                    print(msg)
                    self.send(msg)

    # detect keys release
    def release_k(self,k):
        k = str(k)
        print(k)
        for key in self.keys:
            if k == key:
                if self.keystatus[self.keys.index(key)] == True:
                    self.keystatus[self.keys.index(key)] = False
                    msg = 'U_' + str(self.keysend[self.keys.index(key)])
                    print(msg)
                    self.send(msg)
    def main(self):
        #Star conection with server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ADDR = (self.SERVER, self.PORT)
        self.client.connect(ADDR)
        print("Connect...")
        #funtion detect keyboard
        with keyboard.Listener(on_press=self.press_k, on_release=self.release_k) as listener: listener.join()