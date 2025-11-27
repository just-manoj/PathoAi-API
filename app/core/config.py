import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get settings from environment variables
MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise Exception("MONGODB_URI environment variable is missing!")
MONGODB_DB = os.getenv("MONGODB_DB", "pathoai")
APP_NAME = os.getenv("APP_NAME", "PathoAi API")
DEBUG = os.getenv("DEBUG", "False") == "True"
OPENAI_TOKEN = os.getenv("OPENAI_TOKEN", "")
GEMINI_TOKEN = os.getenv("GEMINI_TOKEN", "")


