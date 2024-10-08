from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.settings import config
from app.model import notification

engine = create_engine(config.dbconn, connect_args={}, echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def db_startup():
    notification.Base.metadata.create_all(engine)

async def db_shutdown():
    pass