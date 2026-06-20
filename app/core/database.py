from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = create_async_engine("postgresql+asyncpg://usuario:pass@localhost/db")
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db() -> AsyncSession:
    """
    Crea una sesión de base de datos por cada petición web
    y la cierra automáticamente cuando la petición termina.
    """
    async with AsyncSessionLocal() as session:
        yield session