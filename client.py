import os
import sys
import socket
import threading
import datetime

import crypto
from ui import UI


class Client:
    def __init__(self):
        self.crypto = crypto.Cripto()
        self.ui = UI()
        self.lock = threading.Lock()

        self.ui.banner()
        self.ui.section("JOIN MODE")

        host = self.ui.ask("Host IP", "")
        port = int(self.ui.ask("Port number", "9090"))

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ui.info(f"Connecting to {host}:{port} ...")
        try:
            self.s.connect((host, port))
        except Exception as e:
            self.ui.error(f"Could not connect: {e}")
            sys.exit(1)

        self.ui.success(f"Connected to {host}:{port}")

    def handshake(self):
        # receive host public key, send ours
        pub_A_ser = self.s.recv(4096)
        self.pub_A_ser = pub_A_ser
        self.s.send(self.crypto.pub_ser)

        # receive encrypted AES key
        encrypted_AES = self.s.recv(4096)
        key_iv = self.crypto.rsa_decrypt_msg(encrypted_AES)
        self.crypto.load_aes_key(key_iv)

        # send ACK
        self.s.send(b"ACK!")

        # name exchange
        encrypted_other = self.s.recv(4096)
        self.other_name = self.crypto.rsa_decrypt_msg(encrypted_other).decode()

        self.my_name = self.ui.ask("Your name", "Client")
        encrypted_name = self.crypto.rsa_encrypt_msg(pub_A_ser, self.my_name)
        self.s.send(encrypted_name)

        self.ui.success(f"Session established with  {self.other_name}")
        self.ui.divider()
        self.ui.hint("/file <path>  to send a file    |    Ctrl+C to quit")
        self.ui.divider()

    def send_msg(self, data):
        with self.lock:
            self.s.send(b"MSG ")
            payload = data.encode("utf-8") if isinstance(data, str) else data
            if len(payload) <= 290:
                encrypted = self.crypto.rsa_encrypt_msg(self.pub_A_ser, payload)
            else:
                encrypted = self.crypto.aes_encrypt(payload)
            size = str(len(encrypted)).zfill(8).encode()
            self.s.send(size)
            self.s.send(encrypted)

    def recv_msg(self):
        while True:
            try:
                header = self.s.recv(4)
                if not header:
                    self.ui.error("Connection closed by host.")
                    os._exit(0)

                if header == b"MSG ":
                    size = int(self.s.recv(8).decode())
                    data = self._recv_exact(size)
                    try:
                        msg = self.crypto.rsa_decrypt_msg(data).decode()
                    except Exception:
                        msg = self.crypto.aes_decrypt(data).decode()
                    ts = datetime.datetime.now().strftime("%H:%M")
                    self.ui.print_incoming(self.other_name, msg, ts)

                elif header == b"FILE":
                    name_size = int(self.s.recv(8).decode())
                    file_name = self.s.recv(name_size).decode()
                    file_size = int(self.s.recv(16).decode())

                    data = self._recv_exact(file_size)
                    decrypted = self.crypto.aes_decrypt(data)

                    out_name = f"received_{file_name}"
                    with open(out_name, "wb") as f:
                        f.write(decrypted)

                    ts = datetime.datetime.now().strftime("%H:%M")
                    self.ui.print_file_recv(self.other_name, out_name, ts)

            except ConnectionResetError:
                self.ui.error("Host disconnected.")
                os._exit(0)

    def _recv_exact(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.s.recv(min(4096, n - len(buf)))
            if not chunk:
                raise ConnectionResetError
            buf += chunk
        return buf

    def send_file(self, file_path):
        if not os.path.isfile(file_path):
            self.ui.error(f"File not found: {file_path}")
            return

        file_name = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            data = f.read()
        encrypted = self.crypto.aes_encrypt(data)

        with self.lock:
            self.s.send(b"FILE")
            self.s.send(str(len(file_name)).zfill(8).encode())
            self.s.send(file_name.encode())
            self.s.send(str(len(encrypted)).zfill(16).encode())
            self.s.send(encrypted)

        ts = datetime.datetime.now().strftime("%H:%M")
        self.ui.print_file_sent(self.my_name, file_name, ts)

    def start(self):
        self.handshake()

        t = threading.Thread(target=self.recv_msg, daemon=True)
        t.start()

        try:
            while True:
                msg = self.ui.input_prompt(self.my_name)
                if not msg:
                    continue
                if msg.startswith("/file "):
                    path = msg[6:].strip()
                    if not path:
                        self.ui.hint("Usage: /file /path/to/file")
                    else:
                        self.send_file(path)
                else:
                    ts = datetime.datetime.now().strftime("%H:%M")
                    self.ui.print_outgoing(self.my_name, msg, ts)
                    self.send_msg(msg)
        except KeyboardInterrupt:
            self.ui.info("Session ended.")
            self.s.close()
