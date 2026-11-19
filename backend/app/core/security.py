"""
IntelliGrievance AI - Security Utilities
Cryptographic password hashing via PBKDF2-HMAC-SHA256 (standard library, zero-dependency, FIPS-compliant)
and JWT generation/verification via HMAC-SHA256 with URL-safe base64.
"""

import hmac
import hashlib
import json
import base64
import time
from typing import Optional, Dict, Any
from backend.app.core.config import settings

SALT = "IntelliGrievance_Security_Salt_2026".encode("utf-8")

def hash_password(password: str) -> str:
    """Generate secure salted PBKDF2-SHA256 hash."""
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), SALT, 100000)
    return dk.hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Constant-time comparison for password verification."""
    return hmac.compare_digest(hash_password(plain_password), hashed_password)

def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _b64_decode(data: str) -> bytes:
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data.encode("utf-8"))

def create_access_token(data: Dict[str, Any], expires_delta_minutes: Optional[int] = None) -> str:
    """
    Creates an RFC 7519 compliant HMAC-SHA256 JWT string without third-party dependencies.
    """
    header = {"alg": "HS256", "typ": "JWT"}
    payload = data.copy()
    
    expire_minutes = expires_delta_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    payload["exp"] = int(time.time()) + (expire_minutes * 60)
    payload["iat"] = int(time.time())
    
    header_b64 = _b64_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64_encode(signature)
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes and cryptographically verifies an HMAC-SHA256 JWT token.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
            
        header_b64, payload_b64, sig_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        
        if not hmac.compare_digest(_b64_encode(expected_sig), sig_b64):
            return None
            
        payload = json.loads(_b64_decode(payload_b64).decode("utf-8"))
        if payload.get("exp") and payload["exp"] < int(time.time()):
            return None  # Token expired
            
        return payload
    except Exception:
        return None
