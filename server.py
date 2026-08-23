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
        print(f"connected: {self.addr}")