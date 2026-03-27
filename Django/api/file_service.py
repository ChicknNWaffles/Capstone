"""
File Service for AWS S3 Operations
"""

import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import uuid
from datetime import datetime
import mimetypes
import logging

from . import s3_config

logger = logging.getLogger(__name__)


class S3FileService:
    
    def __init__(self):
        """Initialize S3 client with credentials"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=s3_config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=s3_config.AWS_SECRET_ACCESS_KEY,
            region_name=s3_config.AWS_S3_REGION_NAME,
            config=Config(signature_version=s3_config.AWS_S3_SIGNATURE_VERSION)
        )
        self.bucket_name = s3_config.AWS_STORAGE_BUCKET_NAME
    
    def _generate_file_key(self, project_id: int, filename: str) -> str:
        """Generate a unique S3 key (path) for the file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        safe_filename = filename.replace(' ', '_')
        return f"projects/{project_id}/{timestamp}_{unique_id}_{safe_filename}"
    
    def upload_file(self, file_obj, filename: str, project_id: int, user_id: int) -> dict:
        """Upload a file to S3 with encryption"""
        try:
            # Generate unique key for S3
            file_key = self._generate_file_key(project_id, filename)
            
            # Detect content type
            content_type, _ = mimetypes.guess_type(filename)
            content_type = content_type or 'application/octet-stream'
            
            # Get file size
            file_obj.seek(0, 2)  # Seek to end
            file_size = file_obj.tell()
            file_obj.seek(0)  # Reset to beginning
            
            # Upload with server-side encryption
            extra_args = {
                'ContentType': content_type,
                'ServerSideEncryption': 'AES256',  # Encryption at rest
                'Metadata': {
                    'uploaded-by': str(user_id),
                    'project-id': str(project_id),
                    'original-filename': filename
                }
            }
            
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                file_key,
                ExtraArgs=extra_args
            )
            
            logger.info(f"File uploaded successfully: {file_key}")
            
            return {
                'success': True,
                'file_key': file_key,
                'filename': filename,
                'size': file_size,
                'content_type': content_type,
                'upload_time': datetime.now().isoformat(),
                'project_id': project_id
            }
            
        except ClientError as e:
            logger.error(f"Error uploading file: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_download_url(self, file_key: str, expiry_seconds: int = None) -> dict:
        """Generate a pre-signed URL for secure file download"""
        try:
            expiry = expiry_seconds or s3_config.AWS_PRESIGNED_URL_EXPIRY
            
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expiry
            )
            
            return {
                'success': True,
                'download_url': url,
                'expires_in_seconds': expiry
            }
            
        except ClientError as e:
            logger.error(f"Error generating download URL: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_file(self, file_key: str) -> dict:
        """Delete a file from S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            
            logger.info(f"File deleted successfully: {file_key}")
            
            return {
                'success': True,
                'deleted_key': file_key
            }
            
        except ClientError as e:
            logger.error(f"Error deleting file: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_project_folder(self, project_id: int) -> dict:
        """Create an empty folder in S3 for a new project"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"projects/{project_id}/"
            )
            return {'success': True}
        except ClientError as e:
            logger.error(f"Error creating project folder: {e}")
            return {'success': False, 'error': str(e)}

    def create_branch_folder(self, project_id: int, branch_name: str) -> dict:
        """Create an empty folder in S3 for a branch: projects/{project_id}/{branch_name}/"""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"projects/{project_id}/{branch_name}/"
            )
            return {'success': True}
        except ClientError as e:
            logger.error(f"Error creating branch folder: {e}")
            return {'success': False, 'error': str(e)}

    def create_file(self, project_id: int, branch_name: str, filename: str, content: str = "") -> dict:
        """Create a file in S3 at projects/{project_id}/{branch_name}/{filename}"""
        try:
            key = f"projects/{project_id}/{branch_name}/{filename}"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content.encode("utf-8"),
                ContentType="text/plain",
                ServerSideEncryption="AES256",
            )
            logger.info(f"File created: {key}")
            return {"success": True, "file_key": key}
        except ClientError as e:
            logger.error(f"Error creating file: {e}")
            return {"success": False, "error": str(e)}

    def read_file(self, project_id: int, branch_name: str, filename: str) -> dict:
        """Read file content from S3 at projects/{project_id}/{branch_name}/{filename}"""
        try:
            key = f"projects/{project_id}/{branch_name}/{filename}"
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            content = response["Body"].read().decode("utf-8")
            return {"success": True, "content": content, "file_key": key}
        except ClientError as e:
            logger.error(f"Error reading file: {e}")
            return {"success": False, "error": str(e)}

    def delete_file_in_project(self, project_id: int, branch_name: str, filename: str) -> dict:
        """Delete a specific file from S3 at projects/{project_id}/{branch_name}/{filename}"""
        key = f"projects/{project_id}/{branch_name}/{filename}"
        return self.delete_file(key)

    def rename_file(self, project_id: int, branch_name: str, old_name: str, new_name: str) -> dict:
        """Rename a file in S3 by copying to new key then deleting old key"""
        try:
            old_key = f"projects/{project_id}/{branch_name}/{old_name}"
            new_key = f"projects/{project_id}/{branch_name}/{new_name}"
            self.s3_client.copy_object(
                Bucket=self.bucket_name,
                CopySource={"Bucket": self.bucket_name, "Key": old_key},
                Key=new_key,
                ServerSideEncryption="AES256",
            )
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=old_key)
            logger.info(f"File renamed: {old_key} -> {new_key}")
            return {"success": True, "old_key": old_key, "new_key": new_key}
        except ClientError as e:
            logger.error(f"Error renaming file: {e}")
            return {"success": False, "error": str(e)}

    def delete_project_folder(self, project_id: int) -> dict:
        """Delete all objects in a project's S3 folder"""
        try:
            prefix = f"projects/{project_id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            objects = [{'Key': obj['Key']} for obj in response.get('Contents', [])]
            if objects:
                self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': objects}
                )
            logger.info(f"Project folder deleted: {prefix}")
            return {'success': True}
        except ClientError as e:
            logger.error(f"Error deleting project folder: {e}")
            return {'success': False, 'error': str(e)}

    def list_files(self, project_id: int) -> dict:
        """List all files for a specific project"""
        try:
            prefix = f"projects/{project_id}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            for obj in response.get('Contents', []):
                # Get object metadata
                head = self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=obj['Key']
                )
                
                files.append({
                    'file_key': obj['Key'],
                    'filename': head.get('Metadata', {}).get('original-filename', obj['Key'].split('/')[-1]),
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'content_type': head.get('ContentType', 'unknown'),
                    'uploaded_by': head.get('Metadata', {}).get('uploaded-by')
                })
            
            return {
                'success': True,
                'project_id': project_id,
                'file_count': len(files),
                'files': files
            }
            
        except ClientError as e:
            logger.error(f"Error listing files: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_file_info(self, file_key: str) -> dict:
        """
        Get metadata for a specific file
        
        Args:
            file_key: S3 key of the file
            
        Returns:
            dict with file metadata
        """
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            
            return {
                'success': True,
                'file_key': file_key,
                'filename': response.get('Metadata', {}).get('original-filename', file_key.split('/')[-1]),
                'size': response['ContentLength'],
                'content_type': response.get('ContentType'),
                'last_modified': response['LastModified'].isoformat(),
                'encryption': response.get('ServerSideEncryption', 'None'),
                'metadata': response.get('Metadata', {})
            }
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return {
                    'success': False,
                    'error': 'File not found'
                }
            logger.error(f"Error getting file info: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Create a singleton instance for easy importing
file_service = S3FileService()