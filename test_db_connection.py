import traceback
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings

async def test_database_connection():
    try:
        # Print out connection details (be careful with sensitive info)
        print(f"Database URL: {settings.DATABASE_URL}")
        
        # Create async engine
        engine = create_async_engine(
            settings.DATABASE_URL, 
            echo=True  # This will log all SQL statements
        )
        
        # Create async session
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Try to perform a simple query
        async with async_session() as session:
            # Count articles to verify table access
            result = await session.execute(text("SELECT COUNT(*) FROM articles"))
            count = result.scalar()
            print(f"Number of articles: {count}")
            
    except Exception as e:
        print(f"Detailed error: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
    finally:
        await engine.dispose()
        
async def debug_database():
    async with engine.connect() as conn:
        # Check current settings
        results = await conn.execute(
            text("""
                SELECT 
                    current_database() as db,
                    current_schema() as schema,
                    current_user as user;
            """)
        )
        print(results.fetchone())
        
        # List all schemas
        schemas = await conn.execute(
            text("SELECT schema_name FROM information_schema.schemata")
        )
        print("Available schemas:", schemas.scalars().all())

# Run the async function
import asyncio
asyncio.run(test_database_connection())