"""
Database configuration module for ByteMart application.
Supports both SQLite for development and Azure SQL Database for production.
"""
import os
import urllib.parse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv('azure-env')

# Get the database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Determine which database to use
if DATABASE_URL and DATABASE_URL.startswith("mssql"):
    # Using Azure SQL Database
    connection_string = DATABASE_URL
    
    # Fix connection string format if necessary for pyodbc
    if "pyodbc" in connection_string and "driver=" in connection_string.lower():
        params = urllib.parse.parse_qs(urllib.parse.urlparse(connection_string).query)
        if "driver" in params:
            driver = params["driver"][0].replace("+", " ")
            connection_string = connection_string.replace(urllib.parse.quote_plus(params["driver"][0]), urllib.parse.quote_plus(driver))
    
    # Create engine with appropriate connection pooling settings for Azure
    engine = create_engine(
        connection_string,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800  # Recycle connections every 30 minutes
    )
    print("Using Azure SQL Database connection")
else:
    # Fallback to SQLite for development
    sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "appain.db")
    engine = create_engine(f"sqlite:///{sqlite_path}", connect_args={"check_same_thread": False})
    print(f"Using SQLite database at {sqlite_path}")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get DB session
def get_db():
    """
    Get a database session.
    Usage:
        db = next(get_db())
        try:
            # use db
        finally:
            db.close()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 