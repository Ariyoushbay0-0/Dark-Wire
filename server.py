import socket
import threading

import crypto



class Server:
    def __init__(self):
        self.crypto = crypto.Cripto()
        port = int(input("please enter port number (example: 9090): "))
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(("0.0.0.0", port))
        self.s.listen(1)
        
        print("standby for connect . . .")
        self.conn, self.addr = self.s.accept()
        self.keys = crypto.Cripto()
        print(f"connected: {self.addr}")
    def hanshake(self): 
        self.conn.send(self.keys.pub_ser)
        pub_B_ser = self.conn.recv(4096)

        self.keys.make_aes_key()
        encrypted_AES = self.keys.rsa_encrypt_msg(pub_B_ser, self.keys.aes_key + self.keys.aes_iv)
        self.conn.send(encrypted_AES)
