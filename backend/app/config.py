from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent

# Load .env file
env_path = PROJECT_ROOT / ".env"
print(f"Looking for .env at: {env_path}")
print(f".env exists: {env_path.exists()}")
load_dotenv(env_path)

# Debug: Print if credentials are loaded
print(f"AWS_ACCESS_KEY_ID loaded: {os.getenv('AWS_ACCESS_KEY_ID') is not None}")
print(f"AWS_SECRET_ACCESS_KEY loaded: {os.getenv('AWS_SECRET_ACCESS_KEY') is not None}")

DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "vehicle_master.db"
JSON_PATH = DATA_DIR / "vehicle_master.json"
UPLOAD_DIR = DATA_DIR / "uploads"

FRONTEND_DIR = PROJECT_ROOT / "frontend"

MODEL_VERSION = "v2.0"

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/jpg",
}

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024
MAX_IMAGE_DIMENSIONS = (1024, 1024)

# AWS Bedrock Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0")

print(f"Final AWS_ACCESS_KEY_ID: {AWS_ACCESS_KEY_ID[:10] if AWS_ACCESS_KEY_ID else 'None'}...")