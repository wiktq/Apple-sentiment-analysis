from pathlib import Path

# Directory configurations (optional, if you want to organize files)
ROOT_DIR = Path(__file__).parent
RAW_DIR = ROOT_DIR / "raw"
COOKIES_FILE = ROOT_DIR / "cookies.json"
RESUME_FILE = ROOT_DIR / "resume_state.json"

# Ensure directories exist
RAW_DIR.mkdir(exist_ok=True)

# Twitter credentials
TWITTER_USERNAME = "XXXX"
TWITTER_EMAIL = "XXXX"
TWITTER_PASSWORD = "XXXX"
