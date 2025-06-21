from dotenv import load_dotenv
import os
from pathlib import Path

env_path = Path(__file__).parent.absolute() / ".env"
print("Looking for .env at:", env_path)

print(".env exists:", env_path.exists())

load_dotenv(dotenv_path=env_path, override=True)

api_key = os.getenv("WEATHERSTACK_API_KEY")
print("Loaded WEATHERSTACK_API_KEY:", api_key)