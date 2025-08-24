# TOTP (Two-Factor Authentication) Support

This module provides TOTP (Time-based One-Time Password) functionality for use with video editing workflows, particularly for YouTube authentication when using playwright automation.

## Usage

### Basic TOTP Operations

```python
from ac_training_lab.video_editing import (
    generate_totp_code,
    verify_totp_code,
    create_totp_provisioning_uri
)

# Generate a TOTP code from a secret
secret = "JBSWY3DPEHPK3PXP"  # Base32-encoded secret
code = generate_totp_code(secret)
print(f"Current TOTP code: {code}")

# Verify a TOTP code
is_valid = verify_totp_code(secret, code)
print(f"Code is valid: {is_valid}")

# Create a provisioning URI for authenticator apps
uri = create_totp_provisioning_uri(secret, "user@example.com", "AC Training Lab")
print(f"Provisioning URI: {uri}")
```

### YouTube Integration with TOTP

```python
from ac_training_lab.video_editing import (
    get_current_totp_for_youtube,
    download_youtube_with_totp
)

# Set environment variable with your YouTube TOTP secret
# export YOUTUBE_TOTP_SECRET="your_base32_secret_here"

# Get current TOTP code for YouTube
totp_code = get_current_totp_for_youtube()
if totp_code:
    print(f"YouTube TOTP code: {totp_code}")

# Download video with TOTP support
video_id = "your_video_id"
download_youtube_with_totp(video_id)  # Uses TOTP from environment
# or
download_youtube_with_totp(video_id, totp_code="123456")  # Explicit TOTP code
```

### Environment Variables

- `YOUTUBE_TOTP_SECRET`: Base32-encoded secret for YouTube 2FA
- `TOTP_SECRET`: Default environment variable for TOTP secret

### Installation

Install with video editing support:

```bash
pip install ac-training-lab[video-editing]
```

Or install pyotp directly:

```bash
pip install pyotp
```

## Use Cases

This functionality is designed for:

1. **Playwright Automation**: When automating YouTube interactions that require 2FA
2. **Scheduled Downloads**: Automated video downloads with 2FA authentication
3. **CI/CD Pipelines**: Automated workflows that need TOTP authentication

## Security Notes

- Store TOTP secrets securely as environment variables
- Never commit TOTP secrets to version control
- Use separate secrets for different services
- Consider using secret management services for production deployments