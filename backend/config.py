import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
if not ANTHROPIC_API_KEY:
    raise RuntimeError("ANTHROPIC_API_KEY is not set in .env")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

FAST_MODEL = "claude-haiku-4-5-20251001"
REASONING_MODEL = "claude-sonnet-5"

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_data")
SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), "sample_data")
