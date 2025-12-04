import os
import base64
import subprocess
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

def get_latest_commit_hash() -> str:
    """Get the latest git commit hash."""
    return subprocess.check_output(['git', 'log', '-1', '--format=%H']).decode('ascii').strip()

def load_private_key(path: str) -> rsa.RSAPrivateKey:
    """Load a private key from a PEM file."""
    with open(path, "rb") as key_file:
        return serialization.load_pem_private_key(key_file.read(), password=None)

def load_public_key(path: str) -> rsa.RSAPublicKey:
    """Load a public key from a PEM file."""
    with open(path, "rb") as key_file:
        return serialization.load_pem_public_key(key_file.read())

def sign_message(message: str, private_key: rsa.RSAPrivateKey) -> bytes:
    """Sign a message using RSA-PSS."""
    return private_key.sign(
        message.encode('utf-8'),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

def encrypt_with_public_key(data: bytes, public_key: rsa.RSAPublicKey) -> bytes:
    """Encrypt data with a public key using RSA-OAEP."""
    return public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def main():
    """Generate the commit proof."""
    # Get the latest commit hash
    commit_hash = get_latest_commit_hash()
    print(f"Commit Hash: {commit_hash}")

    # Load student private key
    student_private_key = load_private_key("student_private.pem")

    # Sign the commit hash
    signature = sign_message(commit_hash, student_private_key)

    # Load instructor public key
    instructor_public_key = load_public_key("instructor_public.pem")

    # Encrypt the signature
    encrypted_signature = encrypt_with_public_key(signature, instructor_public_key)

    # Base64 encode the encrypted signature
    encoded_encrypted_signature = base64.b64encode(encrypted_signature).decode('utf-8')
    print(f"Encrypted Signature: {encoded_encrypted_signature}")

if __name__ == "__main__":
    main()