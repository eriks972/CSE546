import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import json

from collections import defaultdict

# global counter (client-side)
keyword_counters = defaultdict(int)


def prf_forward_private(key, word):
    """
    Generate forward-private trapdoor
    """
    keyword_counters[word] += 1

    counter = keyword_counters[word]

    return prf(key, f"{word}_{counter}")

def generate_key():
    """
    Generate a secret key for PRF
    """
    return os.urandom(32)


def prf(key, word):
    """
    Pseudorandom Function using HMAC-SHA256
    """
    return hmac.new(key, word.encode(), hashlib.sha256).hexdigest()

def encrypt_posting_list(key, posting_list):
    """
    Encrypt posting list using AES-GCM
    """

    aes = AESGCM(key[:32])  # AES-256 key

    nonce = os.urandom(12)

    data = json.dumps(posting_list).encode()

    ciphertext = aes.encrypt(nonce, data, None)

    return nonce + ciphertext


def decrypt_posting_list(key, blob):
    """
    Decrypt posting list
    """

    aes = AESGCM(key)

    nonce = blob[:12]
    ciphertext = blob[12:]

    plaintext = aes.decrypt(nonce, ciphertext, None)

    return json.loads(plaintext.decode())