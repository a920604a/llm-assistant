import os

from dotenv import load_dotenv

load_dotenv()


REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/2")
NOTE_API_URL = os.getenv("NOTE_API_URL", "http://noteserver:8000")
SPEECH_API_URL = os.getenv("SPEECH_API_URL", "http://imageserver:8000")
IMAGE_API_URL = os.getenv("IMAGE_API_URL", "http://speechserver:8000")
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://ollama:11434")


MODEL_NAME = "gpt-oss:20b"

FIRBASE_KEY_PATH = "/app"
