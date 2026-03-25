## AWS Voice Notes Organizer
A serverless application that processes voice notes by converting speech to text and extracting insights such as sentiment and key phrases using AWS services.

This project demonstrates an end-to-end audio processing pipeline, integrating cloud services with a backend API and a simple frontend interface.

# Features
- Upload audio files via web interface
- Automatic speech-to-text transcription using AWS Transcribe
- Natural language processing using AWS Comprehend:
  - Sentiment analysis
  - Key phrase extraction
- Dynamic note generation and display
- Serverless backend using AWS Chalice

# Tech Stack
- Python
- AWS Chalice
- AWS S3
- AWS Transcribe
- AWS Comprehend
- JavaScript (Frontend)
- HTML/CSS

# Architecture
1. User uploads an audio file from the frontend
2. Audio is converted to base64 and sent to the backend API
3. File is stored in AWS S3
4. AWS Transcribe processes the audio and generates a transcript
5. The transcript is analyzed using AWS Comprehend
6. Sentiment and key phrases are extracted
7. Results are displayed as structured notes in the UI
