import boto3
import time
import uuid
from botocore.exceptions import BotoCoreError, ClientError
import logging


class TranscriptionService:
    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        self.transcribe = boto3.client('transcribe', region_name=region)
        self.bucket_name = bucket_name

    def start_transcription_job(self, s3_uri: str, language_code: str = "en-US") -> str:
        job_name = f"transcription-{uuid.uuid4()}"
        try:
            self.transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={'MediaFileUri': s3_uri},
                MediaFormat='wav',
                LanguageCode=language_code,
                OutputBucketName=self.bucket_name,
                Settings={
                    'ShowSpeakerLabels': True,
                    'MaxSpeakerLabels': 2
                }
            )
            return job_name
        except (BotoCoreError, ClientError) as e:
            logging.error(f"Failed to start transcription job: {e}")
            raise

    def wait_for_transcription(self, job_name: str, timeout: int = 300) -> dict:
        start_time = time.time()
        while True:
            job = self.transcribe.get_transcription_job(TranscriptionJobName=job_name)
            status = job['TranscriptionJob']['TranscriptionJobStatus']

            if status in ['COMPLETED', 'FAILED']:
                return job

            if time.time() - start_time > timeout:
                raise TimeoutError("Transcription job timed out.")

            time.sleep(5)

    def get_transcript_url(self, job_response: dict) -> str:
        try:
            return job_response['TranscriptionJob']['Transcript']['TranscriptFileUri']
        except KeyError as e:
            logging.error(f"Transcript URL not found in job response: {e}")
            raise