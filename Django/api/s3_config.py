"""
AWS S3 Configuration for Capstone Project

This module handles S3 connection settings with encryption enabled.
- Server-side encryption (SSE-S3) is enabled on the bucket
- All transfers use HTTPS (encryption in transit)
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# AWS Credentials (loaded from environment variables for security)
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'capstone-cocoding-files')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')

# S3 Settings
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_FILE_OVERWRITE = False  # Don't overwrite files with same name
AWS_DEFAULT_ACL = None  # Use bucket default (private)
AWS_S3_VERIFY = True  # Verify SSL certificates

# Security: Encryption in transit (HTTPS)
AWS_S3_USE_SSL = True

# Security: Additional encryption settings
AWS_S3_OBJECT_PARAMETERS = {
    'ServerSideEncryption': 'AES256',  # Server-side encryption
}

# Optional: Custom domain if you set up CloudFront later
# AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

# URL expiration for pre-signed URLs (in seconds)
AWS_PRESIGNED_URL_EXPIRY = 3600  # 1 hour