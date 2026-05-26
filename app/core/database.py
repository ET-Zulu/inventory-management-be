
from fastapi.params import Depends
from sqlmodel import create_engine , Session, SQLModel , text
from typing import Annotated, Optional


from app.core.config import settings

print("DATABASE URL:", settings.postgres_url)
engine = create_engine(settings.postgres_url, pool_size=20,max_overflow= 30 , pool_pre_ping=True)


def get_session() -> Session: # type: ignore
    """Get a new database session."""
    with Session(engine) as session:
        yield session


SessionType = Annotated[Session, Depends(get_session)]



