# Test uploading a file to S3
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Capstone.settings')

import django
django.setup()

from api.file_service import file_service
from io import BytesIO

# Create a simple test file in memory
test_content = b"# This is a test python file."
test_file = BytesIO(test_content)

print("Uploading test file...")
result = file_service.upload_file(
    file_obj=test_file,
    filename="test_file.py",
    project_id=2,
    user_id=1
)

if result['success']:
    print("✓ Upload successful!")
    print(f"  File key: {result['file_key']}")
    print(f"  Size: {result['size']} bytes")
    
    # Now get a download URL
    print("\nGenerating download URL...")
    url_result = file_service.get_download_url(result['file_key'])
    if url_result['success']:
        print("✓ Download URL generated!")
        print(f"  URL: {url_result['download_url'][:80]}...")
else:
    print("✗ Upload failed!")
    print(f"  Error: {result.get('error')}")