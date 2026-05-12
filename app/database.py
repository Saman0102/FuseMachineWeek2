import logging
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import settings
load_dotenv()

logger = logging.getLogger(__name__)

database_url = settings.get("DATABASE_URL") or os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL is not set in Dynaconf settings or environment")

engine = create_engine(database_url)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = session_local()
    try:
        db.connection()
        logger.info("Database connection established")
        yield db
    except SQLAlchemyError:
        logger.exception("Database connection failed")
        raise
    finally:
        db.close()
        logger.info("Database session closed")