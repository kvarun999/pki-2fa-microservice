import base64
import binascii
import time
from datetime import datetime, timezone

import pyotp

# Constants required by assignment
TOTP_PERIOD = 30
TOTP_DIGITS = 6
TOTP_ALGORITHM = 'sha1'  # pyotp uses sha1 by default


def hex_to_base32(hex_seed: str) -> str:
    """
    Convert 64-char hex seed -> base32 string suitable for pyotp.
    Validates the hex string.
    Returns uppercase base32 string (with padding).
    """
    if not isinstance(hex_seed, str):
        raise ValueError("hex_seed must be a string")

    hex_seed = hex_seed.strip().lower()
    if len(hex_seed) != 64:
        raise ValueError("hex_seed must be exactly 64 hex characters")

    # validate characters
    try:
        seed_bytes = bytes.fromhex(hex_seed)
    except ValueError as e:
        raise ValueError("hex_seed contains non-hex characters") from e

    # base32 encode and return ASCII string (pyotp expects base32 string)
    base32_seed = base64.b32encode(seed_bytes).decode('ascii')  # returns uppercase with '=' padding
    return base32_seed


def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current 6-digit TOTP code from 64-char hex seed.
    Returns code as string zero-padded to 6 digits.
    """
    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=TOTP_DIGITS, interval=TOTP_PERIOD)
    code = totp.now()  # returns string like "123456"
    return code


def totp_seconds_remaining() -> int:
    """
    Return how many seconds left in the current TOTP period (0-30).
    """
    now = int(time.time())
    rem = TOTP_PERIOD - (now % TOTP_PERIOD)
    # If rem == TOTP_PERIOD it means the period just started; normalize to TOTP_PERIOD
    return rem


def generate_totp_payload(hex_seed: str) -> dict:
    """
    Convenience: returns { "code": "123456", "valid_for": seconds } for API response.
    """
    code = generate_totp_code(hex_seed)
    valid_for = totp_seconds_remaining()
    return {"code": code, "valid_for": valid_for}


def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify a provided 6-digit code against the seed with window tolerance.
    valid_window = 1 means accept codes at t-1, t, and t+1 windows (±30s).
    Returns True if valid, False otherwise.
    """
    if not code or not isinstance(code, str):
        raise ValueError("code must be a non-empty string")

    if len(code) != TOTP_DIGITS or not code.isdigit():
        # invalid format; caller should handle as 400 Bad Request
        return False

    base32_seed = hex_to_base32(hex_seed)
    totp = pyotp.TOTP(base32_seed, digits=TOTP_DIGITS, interval=TOTP_PERIOD)

    # pyotp's verify accepts valid_window (int)
    # Note: verify() returns True if code is valid within +/- valid_window.
    try:
        return totp.verify(code, valid_window=valid_window)
    except Exception:
        return False
