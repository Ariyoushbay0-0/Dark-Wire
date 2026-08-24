import os

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_public_key


class Cripto:
    def __init__(self):
        self.pri_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=3072
        )
        self.pub_key = self.pri_key.public_key()
        self.pri_ser = self.pri_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        self.pub_ser = self.pub_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def rsa_encrypt_msg(self, pub_B_ser, data) -> bytes:
        pub_b = load_pem_public_key(pub_B_ser)
        assert isinstance(pub_b, RSAPublicKey)

        if isinstance(data, str):
            data = data.encode("utf-8")
        if len(data) <= 290:
            return pub_b.encrypt(data, asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            ))
        else:
            raise ValueError("message too long for RSA")

    def rsa_decrypt_msg(self, data):
        return self.pri_key.decrypt(data, asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))

    def make_aes_key(self):
        self.aes_key = os.urandom(32)
        self.aes_iv = os.urandom(16)

    def aes_encrypt(self, data):
        if isinstance(data, str):
            data = data.encode("utf-8")

        padder = sym_padding.PKCS7(128).padder()
        padded = padder.update(data) + padder.finalize()

        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(self.aes_iv))
        encryptor = cipher.encryptor()
        return encryptor.update(padded) + encryptor.finalize()

    def aes_decrypt(self, data):
        cipher = Cipher(algorithms.AES(self.aes_key), modes.CBC(self.aes_iv))
        decryptor = cipher.decryptor()
        padded = decryptor.update(data) + decryptor.finalize()

        unpadder = sym_padding.PKCS7(128).unpadder()
        return unpadder.update(padded) + unpadder.finalize()