"""
Tests for TOTP utilities in video editing module.
"""

import os
import pytest
import pyotp

from ac_training_lab.video_editing.totp_utils import (
    generate_totp_code,
    verify_totp_code,
    get_totp_code_from_env,
    create_totp_provisioning_uri,
)


def test_generate_totp_code():
    """Test TOTP code generation with a known secret."""
    # Use a test secret
    secret = pyotp.random_base32()
    
    # Generate code
    code = generate_totp_code(secret)
    
    # Verify it's a 6-digit string
    assert len(code) == 6
    assert code.isdigit()


def test_generate_totp_code_invalid_secret():
    """Test TOTP code generation with invalid secret."""
    with pytest.raises(ValueError):
        generate_totp_code("invalid_secret")


def test_verify_totp_code():
    """Test TOTP code verification."""
    # Use a test secret
    secret = pyotp.random_base32()
    
    # Generate a code
    code = generate_totp_code(secret)
    
    # Verify the code
    assert verify_totp_code(secret, code) is True
    
    # Verify an invalid code
    assert verify_totp_code(secret, "000000") is False


def test_verify_totp_code_invalid_secret():
    """Test TOTP code verification with invalid secret."""
    result = verify_totp_code("invalid_secret", "123456")
    assert result is False


def test_get_totp_code_from_env():
    """Test getting TOTP code from environment variable."""
    test_secret = pyotp.random_base32()
    test_env_var = "TEST_TOTP_SECRET"
    
    # Test with no env var set
    result = get_totp_code_from_env(test_env_var)
    assert result is None
    
    # Test with env var set
    os.environ[test_env_var] = test_secret
    try:
        result = get_totp_code_from_env(test_env_var)
        assert result is not None
        assert len(result) == 6
        assert result.isdigit()
    finally:
        del os.environ[test_env_var]


def test_create_totp_provisioning_uri():
    """Test creating TOTP provisioning URI."""
    secret = pyotp.random_base32()
    name = "test@example.com"
    issuer = "Test Service"
    
    uri = create_totp_provisioning_uri(secret, name, issuer)
    
    # Check that URI contains expected components
    assert uri.startswith("otpauth://totp/")
    assert name in uri
    assert issuer in uri
    assert secret in uri


def test_totp_integration():
    """Test full TOTP workflow integration."""
    # Generate a random secret
    secret = pyotp.random_base32()
    
    # Generate a code
    code = generate_totp_code(secret)
    
    # Verify the code
    is_valid = verify_totp_code(secret, code)
    assert is_valid is True
    
    # Create provisioning URI
    uri = create_totp_provisioning_uri(secret, "test@example.com")
    assert "otpauth://totp/" in uri