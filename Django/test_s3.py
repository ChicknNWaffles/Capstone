# Quick test to verify S3 connection
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Capstone.settings')

import django
django.setup()

# Now test S3
from api.file_service import file_service

print("Testing S3 connection...")
print(f"Bucket: {file_service.bucket_name}")

# Try to list files (even if empty, this tests the connection)
result = file_service.list_files(project_id=1)

if result['success']:
    print("✓ S3 connection successful!")
    print(f"  Files found: {result['file_count']}")
else:
    print("✗ S3 connection failed!")
    print(f"  Error: {result.get('error')}")