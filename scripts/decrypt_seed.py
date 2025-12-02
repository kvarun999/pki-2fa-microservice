import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

def decrypt_seed(encrypted_seed_b64, private_key):
    ciphertext = base64.b64decode(encrypted_seed_b64)

    try:
        decrypted = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception:
        raise ValueError("Decryption failed")

    hex_seed = decrypted.decode("utf-8").strip()

    if len(hex_seed) != 64 or not all(c in "0123456789abcdef" for c in hex_seed):
        raise ValueError("Invalid seed format")

    return hex_seed
