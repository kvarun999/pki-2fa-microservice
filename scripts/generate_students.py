from pathlib import Path
from typing import Tuple

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend


def generate_rsa_keypair(key_size: int = 4096) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
    
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend(),
    )
    public_key = private_key.public_key()
    return private_key, public_key


def save_keys_to_files():
    # Project root = parent of this file's directory
    project_root = Path(__file__).resolve().parent.parent

    private_key, public_key = generate_rsa_keypair()

    # Serialize private key to PEM (PKCS8, no encryption)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Serialize public key to PEM
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Required filenames (at repo root)
    private_path = project_root / "student_private.pem"
    public_path = project_root / "student_public.pem"

    # Write files
    private_path.write_bytes(private_pem)
    public_path.write_bytes(public_pem)

    # On Unix-like systems, lock down permissions for private key (600)
    try:
        private_path.chmod(0o600)
    except Exception:
        # On Windows this may fail; it's fine
        pass

    print(f"Generated private key: {private_path}")
    print(f"Generated public key:  {public_path}")


if __name__ == "__main__":
    save_keys_to_files()
