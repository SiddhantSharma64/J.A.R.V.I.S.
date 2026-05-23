import os
from dotenv import load_dotenv

# Load environment variables from the root .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "jarvis")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
ENABLE_FACE_AUTH = os.getenv("ENABLE_FACE_AUTH", "True").lower() == "true"
PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY", "")
TTS_VOICE = os.getenv("TTS_VOICE", "Evan")
TTS_RATE = int(os.getenv("TTS_RATE", "190"))
COUNTRY_CODE = os.getenv("COUNTRY_CODE", "+91")