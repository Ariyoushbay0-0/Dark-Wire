import os
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
    def hanshake(self): 
        self.conn.send(self.crypto.pub_ser)
        pub_B_ser = self.conn.recv(4096)
        self.pub_B_ser = pub_B_ser

        self.crypto.make_aes_key()
        encrypted_AES = self.crypto.rsa_encrypt_msg(pub_B_ser, self.crypto.aes_key + self.crypto.aes_iv)
        self.conn.send(encrypted_AES)

        self.conn.recv(4)

        self.my_name = input("please enter name : ")
        encrypted_name = self.crypto.rsa_encrypt_msg(pub_B_ser, self.my_name)
        self.conn.send(encrypted_name)


        encrypted_other = self.conn.recv(4096)
        self.other_name = self.crypto.rsa_decrypt_msg(encrypted_other).decode()
        print(f"chatting with: {self.other_name}")

    def send_msg(self, data):
        self.conn.send(b"MSG ")
        encrypted = self.crypto.rsa_encrypt_msg(self.pub_B_ser, data)
        self.conn.send(encrypted)

    def recv_msg(self):
        while True:
            header = self.conn.recv(4)

            if header == b"MSG ":
                data = self.conn.recv(4096)
                msg = self.crypto.rsa_decrypt_msg(data).decode()
                print(f"\n[{self.other_name}]: {msg}")

            elif header == b"FILE":
                name_size = int(self.conn.recv(8).decode())
                file_name = self.conn.recv(name_size).decode()

                file_size = int(self.conn.recv(16).decode())

                data = b""
                received = 0
                while received < file_size:
                    chunk = self.conn.recv(min(4096, file_size - received))
                    data += chunk                
                    received += len(chunk)

                decrypted = self.crypto.aes_decrypt(data)
                with open(f"received_{file_name}", "wb") as f:
                    f.write(decrypted)

                print(f"\n[{self.other_name}]: sent file → received_{file_name}")

    def send_file(self, file_path):
        self.conn.send(b"FILE")
    
        file_name = os.path.basename(file_path)
        self.conn.send(str(len(file_name)).zfill(8).encode())
        self.conn.send(file_name.encode())

        with open(file_path, "rb") as f:
            data = f.read()
        encrypted = self.crypto.aes_encrypt(data)
    
        self.conn.send(str(len(encrypted)).zfill(16).encode())
        self.conn.send(encrypted)
    
        print(f"\n[you]: sent file → {file_name}")

        while True:
            msg = input(f"[{self.my_name}]: ")
            if msg.startswith("/file "):
                path = msg[6:].strip()
                if not path:
                    print("usage: /file /path/to/file")
                    continue
                self.send_file(path)
            else:
                self.send_msg(msg)