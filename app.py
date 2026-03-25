from chalice import Chalice
from services import storage_service, transcription_service, comprehend_service
import base64
import json
import os

# Chalice app configuration
app = Chalice(app_name='VoiceNotesApp')
app.debug = True

# Environment configuration
BUCKET_NAME = "notesappcent.aws.ai"

# Service initialization
storage = storage_service.StorageService(BUCKET_NAME)
transcriber = transcription_service.TranscriptionService(BUCKET_NAME)
comprehender = comprehend_service.ComprehendService()


@app.route('/upload-audio', methods=['POST'], cors=True)
def upload_audio():
    """Handles base64 audio upload and begins transcription."""
    request_data = json.loads(app.current_request.raw_body)
    file_bytes = base64.b64decode(request_data['filebytes'])
    user_id = request_data.get('userId', 'anonymous')

    uploaded = storage.upload_audio_file(file_bytes, user_id)
    file_url = uploaded['fileUrl']

    job_name = transcriber.start_transcription_job(file_url)

    return {
        "message": "Audio uploaded and transcription started.",
        "fileId": uploaded['fileId'],
        "jobName": job_name
    }


@app.route('/transcription/{job_name}', methods=['GET'], cors=True)
def get_transcription(job_name):
    """Checks status of transcription job and returns transcript URL if ready."""
    job_response = transcriber.wait_for_transcription(job_name)
    status = job_response['TranscriptionJob']['TranscriptionJobStatus']

    if status == 'COMPLETED':
        transcript_url = transcriber.get_transcript_url(job_response)
        return {"status": status, "transcriptUrl": transcript_url}
    else:
        return {"status": status}


@app.route('/analyze-text', methods=['POST'], cors=True)
def analyze_text():
    """Analyzes text using AWS Comprehend for sentiment and key phrases only."""
    request_data = json.loads(app.current_request.raw_body)
    text = request_data['text']

    lang = comprehender.detect_dominant_language(text)
    key_phrases = comprehender.extract_key_phrases(text, lang)
    sentiment = comprehender.detect_sentiment(text, lang)

    return {
        "language": lang,
        "sentiment": sentiment,
        "keyPhrases": key_phrases
    }
