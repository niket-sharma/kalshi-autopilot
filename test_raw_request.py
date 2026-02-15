"""Test raw Kalshi API request with detailed logging."""
import time
import base64
from pathlib import Path
import requests
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

# Load config
API_KEY = "ed627e5b-18bf-4192-bfe8-f22dd6e5f069"
BASE_URL = "https://api.elections.kalshi.com"
KEY_PATH = Path("kalshi_private_key.pem")

print("=" * 60)
print("Raw Kalshi API Request Test")
print("=" * 60)

# Load private key
print(f"\n1. Loading private key from {KEY_PATH}...")
try:
    with open(KEY_PATH, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )
    print("   ✅ Private key loaded")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

# Create signature
path = "/trade-api/v2/portfolio/balance"
method = "GET"
full_url = f"{BASE_URL}{path}"
timestamp = str(int(time.time() * 1000))
message = f"{timestamp}{method}{path}"

print(f"\n2. Creating signature...")
print(f"   Timestamp: {timestamp}")
print(f"   Method: {method}")
print(f"   Path: {path}")
print(f"   Message to sign: {message}")

try:
    signature = private_key.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    signature_b64 = base64.b64encode(signature).decode()
    print(f"   ✅ Signature created (length: {len(signature_b64)})")
    print(f"   First 50 chars: {signature_b64[:50]}...")
except Exception as e:
    print(f"   ❌ Failed: {e}")
    exit(1)

# Create headers
headers = {
    "KALSHI-ACCESS-KEY": API_KEY,
    "KALSHI-ACCESS-TIMESTAMP": timestamp,
    "KALSHI-ACCESS-SIGNATURE": signature_b64,
    "Content-Type": "application/json"
}

print(f"\n3. Request headers:")
for key, value in headers.items():
    if key == "KALSHI-ACCESS-SIGNATURE":
        print(f"   {key}: {value[:50]}...")
    else:
        print(f"   {key}: {value}")

# Make request
print(f"\n4. Making request to {full_url}...")
try:
    response = requests.get(full_url, headers=headers)
    print(f"   Status code: {response.status_code}")
    print(f"   Response headers: {dict(response.headers)}")
    print(f"   Response body: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ SUCCESS! Authentication working!")
        data = response.json()
        balance = data.get('balance', 0) / 100.0
        print(f"   Balance: ${balance:.2f}")
    else:
        print(f"\n❌ FAILED! Status {response.status_code}")
        print(f"   This might mean:")
        print(f"   - Wrong API key")
        print(f"   - Wrong private key")
        print(f"   - Signature format issue")
        
except Exception as e:
    print(f"   ❌ Request failed: {e}")

print("\n" + "=" * 60)
