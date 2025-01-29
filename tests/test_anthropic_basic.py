import asyncio
import anthropic
from app.core.config import settings

async def test_basic_call():
    print("\nCreating Anthropic client...")
    client = anthropic.Anthropic(
        api_key=settings.ANTHROPIC_API_KEY,
    )
    
    print("API Key (first 10 chars):", settings.ANTHROPIC_API_KEY[:10] + "...")
    
    print("\nTesting basic API call...")
    try:
        response = await client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": "Hello, Claude"}
            ]
        )
        print("Response:", response.content)
    except Exception as e:
        print(f"\nError details:\n{str(e)}")
        print("\nAPI Request failed. This could mean:")
        print("1. The model name might not be correct")
        print("2. The API key might not be valid")
        print("3. The API key might not have access to this model")
        raise

if __name__ == "__main__":
    asyncio.run(test_basic_call())