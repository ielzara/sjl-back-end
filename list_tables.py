import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings

async def list_tables():
    try:
        print(settings.DATABASE_URL)
        engine = create_async_engine(settings.DATABASE_URL)
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        
        async with async_session() as session:
            result = await session.execute(text("""
            SELECT current_database(), current_schema(), current_user;
        """))
            connection_info = result.first()
            print(f"Connected to database: {connection_info}")

            result = await session.execute(
                text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
            )
            
            tables = result.scalars().all()
            print("\nTables in database:")
            for table in tables:
                print(f"- {table}")
            
    except Exception as e:
        print(f"Detailed error: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(list_tables())