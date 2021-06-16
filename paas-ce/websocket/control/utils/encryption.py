import hashlib
import random
from base64 import urlsafe_b64encode, urlsafe_b64decode
from Cryptodome.Cipher import AES

from django.conf import settings


class PasswordEncryption(object):
    def get_random_string(self, length=8):
        """
        生成长度为length 的随机字符串
        """
        aplhabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join(map(lambda _: random.choice(aplhabet), range(length)))

    def pad(self, text, blocksize=16):
        """
        PKCS#5 Padding
        """
        pad = blocksize - (len(text) % blocksize)
        return (text + pad * chr(pad)).encode('utf-8')

    def encrypt(self, plaintext, key='', base64=True):
        """
        AES Encrypt
        """
        if not key:
            key = settings.SECRET_KEY

        key = hashlib.md5(key.encode('utf-8')).digest()
        cipher = AES.new(key, AES.MODE_ECB)
        ciphertext = cipher.encrypt(self.pad(plaintext))
        # 将密文base64加密
        if base64:
            ciphertext = urlsafe_b64encode(ciphertext).decode().rstrip('=')

        return ciphertext

    def decrypt(self, ciphertext, key='', base64=True):
        """
        AES Decrypt
        """
        if not key:
            key = settings.SECRET_KEY

        if base64:
            ciphertext = urlsafe_b64decode(str(ciphertext + '=' * (4 - len(ciphertext) % 4)))

        data = ciphertext

        key = hashlib.md5(key.encode('utf-8')).digest()
        cipher = AES.new(key, AES.MODE_ECB)
        return self.unpad(cipher.decrypt(data).decode())

    def unpad(self, text):
        """
        PKCS#5 Padding
        """
        pad = ord(text[-1])
        return text[:-pad]
