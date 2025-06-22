"""
TOTP (Time-based One-Time Password) utilities for video editing workflows.

This module provides minimal, lean TOTP functionality for use with playwright
and YouTube video downloading where 2FA authentication may be required.
"""

import os
from typing import Optional

import pyotp


def generate_totp_code(secret: str) -> str:
    """
    Generate a TOTP code from a secret.
    
    Args:
        secret: Base32-encoded secret string
        
    Returns:
        6-digit TOTP code as string
        
    Raises:
        ValueError: If secret is invalid
    """
    try:
        totp = pyotp.TOTP(secret)
        return totp.now()
    except Exception as e:
        raise ValueError(f"Failed to generate TOTP code: {e}")


def verify_totp_code(secret: str, token: str, window: int = 1) -> bool:
    """
    Verify a TOTP code against a secret.
    
    Args:
        secret: Base32-encoded secret string
        token: 6-digit TOTP code to verify
        window: Time window for verification (default: 1)
        
    Returns:
        True if code is valid, False otherwise
    """
    try:
        totp = pyotp.TOTP(secret)
        return totp.verify(token, window=window)
    except Exception:
        return False


def get_totp_code_from_env(env_var: str = "TOTP_SECRET") -> Optional[str]:
    """
    Generate TOTP code from secret stored in environment variable.
    
    Args:
        env_var: Environment variable name containing the secret
        
    Returns:
        6-digit TOTP code as string, or None if env var not set
        
    Raises:
        ValueError: If secret is invalid
    """
    secret = os.getenv(env_var)
    if not secret:
        return None
    
    return generate_totp_code(secret)


def create_totp_provisioning_uri(
    secret: str, 
    name: str, 
    issuer: str = "AC Training Lab"
) -> str:
    """
    Create a provisioning URI for setting up TOTP in authenticator apps.
    
    Args:
        secret: Base32-encoded secret string
        name: Account name (e.g., email or username)
        issuer: Service name
        
    Returns:
        Provisioning URI string
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=name, issuer_name=issuer)