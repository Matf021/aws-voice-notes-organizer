import boto3
from botocore.exceptions import BotoCoreError, ClientError
from typing import Dict
import uuid
import logging


class StorageService:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = boto3.client('s3')

    def upload_audio_file(self, file_bytes: bytes, user_id: str, extension: str = ".wav") -> Dict[str, str]:
        """
        Upload an audio file to the S3 bucket under a user-specific folder.
        Returns metadata including file ID and public URL.
        """
        file_id = f"{user_id}/{uuid.uuid4()}{extension}"

        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=file_id,
                Body=file_bytes,
                ContentType="audio/wav",
                ServerSideEncryption='AES256'
            )
            return {
                "fileId": file_id,
                "fileUrl": f"https://{self.bucket_name}.s3.amazonaws.com/{file_id}"
            }
        except (BotoCoreError, ClientError) as e:
            logging.error(f"Failed to upload file: {e}")
            raise

    def get_file_url(self, file_id: str) -> str:
        """
        Generate a pre-signed URL to access the file (optional, for private access).
        """
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_id},
                ExpiresIn=3600
            )
            return url
        except (BotoCoreError, ClientError) as e:
            logging.error(f"Failed to generate URL: {e}")
            raise

    def get_storage_location(self) -> str:
        return self.bucket_name
