from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# Database URL for PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://admin:password@database_m3:5432/auth"

# Create an engine instance
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

# Enable SQL logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)