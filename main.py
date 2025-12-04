import os
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from utils.crypto_helpers import load_private_key
from utils.decrypt_seed import decrypt_seed
from utils.totp_utils import generate_totp_payload, verify_totp_code

app = FastAPI()

# Configuration
DATA_PATH = os.environ.get("SEED_DATA_PATH", "/data/seed.txt")

# Pydantic models for request validation
class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

def write_seed_file(hex_seed: str):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        f.write(hex_seed.strip())
    # Try to set secure permissions
    try:
        os.chmod(DATA_PATH, 0o600)
    except Exception:
        pass

def read_seed_file():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError("Seed file missing")
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return f.read().strip()

@app.post("/decrypt-seed")
async def decrypt_seed_endpoint(request: DecryptRequest):
    try:
        # Load key and decrypt
        private_key = load_private_key("/app/student_private.pem")
        hex_seed = decrypt_seed(request.encrypted_seed, private_key)
        
        # Save to persistent volume
        write_seed_file(hex_seed)
        return {"status": "ok"}
    except Exception:
        return Response(content='{"error": "Decryption failed"}', status_code=500, media_type="application/json")

@app.get("/generate-2fa")
async def generate_2fa_endpoint():
    try:
        hex_seed = read_seed_file()
        payload = generate_totp_payload(hex_seed)
        return payload
    except FileNotFoundError:
        return Response(content='{"error": "Seed not decrypted yet"}', status_code=500, media_type="application/json")
    except Exception:
        return Response(content='{"error": "Internal error"}', status_code=500, media_type="application/json")

@app.post("/verify-2fa")
async def verify_2fa_endpoint(request: VerifyRequest):
    if not request.code:
        return Response(content='{"error": "Missing code"}', status_code=400, media_type="application/json")
    
    try:
        hex_seed = read_seed_file()
        is_valid = verify_totp_code(hex_seed, request.code, valid_window=1)
        return {"valid": is_valid}
    except Exception:
        # If seed is missing or other error, return valid: false or 500 depending on spec.
        # The prompt asks for handling missing seed with 500
        if not os.path.exists(DATA_PATH):
             return Response(content='{"error": "Seed not decrypted yet"}', status_code=500, media_type="application/json")
        return {"valid": False}