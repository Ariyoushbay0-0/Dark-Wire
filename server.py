import os
import sys
import socket
import threading
import datetime

import crypto
from ui import UI


class Server:
    def __init__(self):
        self.crypto = crypto.Cripto()
        self.ui = UI()
        self.lock = threading.Lock()

        self.ui.banner()
        self.ui.section("HOST MODE")

        port = self.ui.ask("Port number", "9090")
        port = int(port)

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(("0.0.0.0", port))
        self.s.listen(1)

        # show local IP hint
        local_ip = self._get_local_ip()
        self.ui.info(f"Listening on  {local_ip}:{port}")
        self.ui.info("Waiting for peer to connect...")

        self.conn, self.addr = self.s.accept()
        self.ui.success(f"Peer connected from {self.addr[0]}:{self.addr[1]}")

    def _get_local_ip(self):
        try:
            tmp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            tmp.connect(("8.8.8.8", 80))
            ip = tmp.getsockname()[0]
            tmp.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def handshake(self):
        # key exchange
        self.conn.send(self.crypto.pub_ser)
        pub_B_ser = self.conn.recv(4096)
        self.pub_B_ser = pub_B_ser

        self.crypto.make_aes_key()
        encrypted_AES = self.crypto.rsa_encrypt_msg(
            pub_B_ser, self.crypto.aes_key + self.crypto.aes_iv
        )
        self.conn.send(encrypted_AES)
        self.conn.recv(4)  # ACK

        # name exchange
        self.my_name = self.ui.ask("Your name", "Host")
        encrypted_name = self.crypto.rsa_encrypt_msg(pub_B_ser, self.my_name)
        self.conn.send(encrypted_name)

        encrypted_other = self.conn.recv(4096)
        self.other_name = self.crypto.rsa_decrypt_msg(encrypted_other).decode()

        self.ui.success(f"Session established with  {self.other_name}")
        self.ui.divider()
        self.ui.hint("/file <path>  to send a file    |    Ctrl+C to quit")
        self.ui.divider()

    def send_msg(self, data):
        with self.lock:
            self.conn.send(b"MSG ")
            payload = data.encode("utf-8") if isinstance(data, str) else data
            if len(payload) <= 290:
                encrypted = self.crypto.rsa_encrypt_msg(self.pub_B_ser, payload)
            else:
                encrypted = self.crypto.aes_encrypt(payload)
            size = str(len(encrypted)).zfill(8).encode()
            self.conn.send(size)
            self.conn.send(encrypted)

    def recv_msg(self):
        while True:
            try:
                header = self.conn.recv(4)
                if not header:
                    self.ui.error("Connection closed by peer.")
                    os._exit(0)

                if header == b"MSG ":
                    size = int(self.conn.recv(8).decode())
                    data = self._recv_exact(size)
                    try:
                        msg = self.crypto.rsa_decrypt_msg(data).decode()
                    except Exception:
                        msg = self.crypto.aes_decrypt(data).decode()
                    ts = datetime.datetime.now().strftime("%H:%M")
                    self.ui.print_incoming(self.other_name, msg, ts)

                elif header == b"FILE":
                    name_size = int(self.conn.recv(8).decode())
                    file_name = self.conn.recv(name_size).decode()
                    file_size = int(self.conn.recv(16).decode())

                    data = self._recv_exact(file_size)
                    decrypted = self.crypto.aes_decrypt(data)

                    out_name = f"received_{file_name}"
                    with open(out_name, "wb") as f:
                        f.write(decrypted)

                    ts = datetime.datetime.now().strftime("%H:%M")
                    self.ui.print_file_recv(self.other_name, out_name, ts)

            except ConnectionResetError:
                self.ui.error("Peer disconnected.")
                os._exit(0)

    def _recv_exact(self, n):
        buf = b""
        while len(buf) < n:
            chunk = self.conn.recv(min(4096, n - len(buf)))
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
            self.conn.send(b"FILE")
            self.conn.send(str(len(file_name)).zfill(8).encode())
            self.conn.send(file_name.encode())
            self.conn.send(str(len(encrypted)).zfill(16).encode())
            self.conn.send(encrypted)

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
            self.conn.close()
            self.s.close()
