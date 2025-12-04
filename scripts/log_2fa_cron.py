import sys
import os
import datetime

# Add project root to path so we can import 'utils'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.totp_utils import generate_totp_code

DATA_PATH = "/data/seed.txt"

if __name__ == "__main__":
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r") as f:
                seed = f.read().strip()
            
            code = generate_totp_code(seed)
            
            # UTC Timestamp is required by the assignment
            now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{now} - 2FA Code: {code}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)