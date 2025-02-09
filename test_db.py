import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings

async def test_connection():
    try:
        # Create async engine
        engine = create_async_engine(settings.DATABASE_URL)
        
        # Create async session
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Try to connect
        async with async_session() as session:
            # Execute a simple query
            result = await session.execute(text("SELECT 1"))
            print("Database connection successful!")
            print(f"Query result: {result.scalar()}")
            
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_connection())