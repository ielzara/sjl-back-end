import anthropic
from app.core.config import settings
import os
from dotenv import load_dotenv

load_dotenv()

print("\nEnvironment Check:")
print(f"API Key length: {len(settings.ANTHROPIC_API_KEY)}")
print(f"API Key starts with: {os.getenv("ANTHROPIC_API_KEY")}...")

try:
    client = anthropic.Anthropic(
        # api_key=settings.ANTHROPIC_API_KEY,
        )
    
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Hello, world"}
        ]
    )
    print(message)
except Exception as e:
    print(f"\nError details:\n{str(e)}")