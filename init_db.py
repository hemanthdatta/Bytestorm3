#!/usr/bin/env python
"""
Database initialization script for Azure SQL Database.
This script creates all database tables based on SQLAlchemy models.
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# Import the database configuration
from db_config import Base, engine

def init_db():
    """
    Initialize the database by creating all tables defined in models.
    """
    try:
        # Import all models to ensure they're registered with SQLAlchemy
        # Replace these imports with your actual model imports
        try:
            # Try to import models - adjust the import paths as needed for your project
            from src.models import User, Product, Category, Order, OrderItem
            logger.info("Models imported successfully")
        except ImportError as e:
            logger.warning(f"Could not import some models: {e}")
            logger.info("Will continue with available models")
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")
        return True
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting database initialization")
    success = init_db()
    
    if success:
        logger.info("Database initialization completed successfully")
        sys.exit(0)
    else:
        logger.error("Database initialization failed")
        sys.exit(1) 