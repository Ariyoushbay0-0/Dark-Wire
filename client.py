import os
import socket
import threading

import crypto


class Client:
    def __init__(self):
        self.crypto = crypto.Cripto()
        ip = input("please enter server IP: ")
        port = int(input("please enter port number: "))
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.connect((ip, port))
        print("connected!")

    def handshake(self):
        pub_B_ser = self.s.recv(4096)
        self.pub_B_ser = pub_B_ser
        self.s.send(self.crypto.pub_ser)

        encrypted_AES = self.s.recv(4096)
        aes_data = self.crypto.rsa_decrypt_msg(encrypted_AES)
        self.crypto.aes_key = aes_data[:32]
        self.crypto.aes_iv = aes_data[32:]
        self.s.send(b"OK  ")

        encrypted_other = self.s.recv(4096)
        self.other_name = self.crypto.rsa_decrypt_msg(encrypted_other).decode()
        print(f"chatting with: {self.other_name}")

        self.my_name = input("please enter name: ")
        encrypted_name = self.crypto.rsa_encrypt_msg(pub_B_ser, self.my_name)
        self.s.send(encrypted_name)

    def send_msg(self, data):
        self.s.send(b"MSG ")
        encrypted = self.crypto.rsa_encrypt_msg(self.pub_B_ser, data)
        self.s.send(encrypted)

    def recv_msg(self):
        while True:
            header = self.s.recv(4)

            if header == b"MSG ":
                data = self.s.recv(4096)
                msg = self.crypto.rsa_decrypt_msg(data).decode()
                print(f"\n[{self.other_name}]: {msg}")

            elif header == b"FILE":
                name_size = int(self.s.recv(8).decode())
                file_name = self.s.recv(name_size).decode()

                file_size = int(self.s.recv(16).decode())

                data = b""
                received = 0
                while received < file_size:
                    chunk = self.s.recv(min(4096, file_size - received))
                    data += chunk
                    received += len(chunk)

                decrypted = self.crypto.aes_decrypt(data)
                with open(f"received_{file_name}", "wb") as f:
                    f.write(decrypted)

                print(f"\n[{self.other_name}]: sent file → received_{file_name}")

    def send_file(self, file_path):
        self.s.send(b"FILE")

        file_name = os.path.basename(file_path)
        self.s.send(str(len(file_name)).zfill(8).encode())
        self.s.send(file_name.encode())

        with open(file_path, "rb") as f:
            data = f.read()
        encrypted = self.crypto.aes_encrypt(data)

        self.s.send(str(len(encrypted)).zfill(16).encode())
        self.s.send(encrypted)

        print(f"\n[you]: sent file → {file_name}")

    def start(self):
        self.handshake()

        t_recv = threading.Thread(target=self.recv_msg)
        t_recv.daemon = True
        t_recv.start()

        while True:
            msg = input(f"[{self.my_name}]: ")
            if msg.startswith("/file "):
                self.send_file(msg[6:])
            else:
                self.send_msg(msg)