# -*- coding: utf-8 -*-
"""
登录态加密方法.

使用AES算法，ECB模式
""" # noqa

try:
        from common.log import logger
except:
        pass


import hashlib
import random
from base64 import urlsafe_b64encode, urlsafe_b64decode
from Crypto.Util.Padding import pad, unpad

from Crypto.Cipher import AES
from django.conf import settings

def ensure_bytes(s):
    if isinstance(s, str):
        return s.encode('utf-8')
    return s

def decrypt(ciphertext, key='', base64=True):
    """
    AES Decrypt
    """
    # 直接返回 None，不进行后续操作
    if ciphertext == 'None' or ciphertext is None or not ciphertext:
        logger.info("Invalid ciphertext detected, returning None")
        return None
    if not key:
        key = settings.SECRET_KEY

    if base64:
        ciphertext = urlsafe_b64decode(str(ciphertext + '=' * (4 - len(ciphertext) % 4)))
    if not ciphertext or ciphertext == 'None' or ciphertext == '':
        return None

    key = ensure_bytes(key)
    key = hashlib.md5(key).digest()
    cipher = AES.new(key, AES.MODE_ECB)
    padded_plaintext = cipher.decrypt(ciphertext)
    plaintext = unpad(padded_plaintext, AES.block_size)
    return plaintext.decode('utf-8')

def encrypt(plaintext, key='', base64_type=True):
    """
    AES Encrypt
    """
    if not key:
        key = settings.SECRET_KEY
    if isinstance(plaintext, str):
        plaintext = plaintext.encode('utf-8')

    # 确保 key 是字节类型
    if isinstance(key, str):
        key = key.encode('utf-8')
    key = ensure_bytes(key)
    key = hashlib.md5(key).digest()
    cipher = AES.new(key, AES.MODE_ECB)
    padded_plaintext = pad(plaintext, AES.block_size)
    ciphertext = cipher.encrypt(padded_plaintext)
    encoded = urlsafe_b64encode(ciphertext).decode('utf-8').rstrip('=')
    return encoded


def salt(length=8):
    """
    生成长度为length 的随机字符串
    """
    aplhabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join([random.choice(aplhabet) for _ in range(length)])




if __name__ == '__main__':
        a = "m0qOJC3WuJrngjSXdEtjwBeLRVH_dKkQM0CBrAjIyAA"
        print("decrypt", decrypt(a, key="jO149njrTj4kEx6ZbUH8Zc53bfQJctINWaEzTWIsOoxSDNwK2I"))
