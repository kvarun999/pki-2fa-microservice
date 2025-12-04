# authsvc/utils/crypto_helpers.py
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

PRIVATE_KEY_PATH = os.environ.get("STUDENT_PRIVATE_PEM", "../student_private.pem")

def load_private_key(path: str = PRIVATE_KEY_PATH):
    """
    Load PEM private key (no password).
    """
    with open(path, "rb") as f:
        data = f.read()
    private_key = serialization.load_pem_private_key(data, password=None, backend=default_backend())
    return private_key
