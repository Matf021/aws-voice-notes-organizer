import boto3
from botocore.exceptions import BotoCoreError, ClientError
import logging
from typing import Dict, List


class ComprehendService:
    def __init__(self, region: str = "us-east-1"):
        self.comprehend = boto3.client("comprehend", region_name=region)

    def detect_dominant_language(self, text: str) -> str:
        try:
            response = self.comprehend.detect_dominant_language(Text=text)
            languages = response.get("Languages", [])
            if not languages:
                raise ValueError("No dominant language detected")
            return languages[0]["LanguageCode"]
        except (BotoCoreError, ClientError, ValueError) as e:
            logging.error(f"Language detection failed: {e}")
            raise

    def extract_key_phrases(self, text: str, language_code: str) -> List[str]:
        try:
            response = self.comprehend.detect_key_phrases(
                Text=text,
                LanguageCode=language_code
            )
            return [phrase["Text"] for phrase in response.get("KeyPhrases", [])]
        except (BotoCoreError, ClientError) as e:
            logging.error(f"Key phrase extraction failed: {e}")
            raise

    def detect_sentiment(self, text: str, language_code: str) -> str:
        try:
            response = self.comprehend.detect_sentiment(
                Text=text,
                LanguageCode=language_code
            )
            return response.get("Sentiment", "UNKNOWN")
        except (BotoCoreError, ClientError) as e:
            logging.error(f"Sentiment analysis failed: {e}")
            raise

    def classify_text(self, text: str, endpoint_arn: str) -> Dict[str, float]:
        """
        Classifies text using a custom classification endpoint.
        """
        try:
            response = self.comprehend.classify_document(
                Text=text,
                EndpointArn=endpoint_arn
            )
            return {
                label["Name"]: label["Score"]
                for label in response.get("Classes", [])
            }
        except (BotoCoreError, ClientError) as e:
            logging.error(f"Text classification failed: {e}")
            raise
