#!/usr/bin/env python
"""
Test script to verify connection to Azure SQL Database.
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

def test_connection():
    """
    Test connection to the configured database.
    """
    try:
        # Import the database configuration
        from db_config import engine
        
        # Test connection
        logger.info("Testing database connection...")
        connection = engine.connect()
        logger.info("Connection successful!")
        
        # Execute a simple query
        logger.info("Executing test query...")
        result = connection.execute("SELECT 1 AS test_result")
        row = result.fetchone()
        logger.info(f"Test query result: {row.test_result}")
        
        # Close connection
        connection.close()
        logger.info("Connection closed")
        
        return True
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting database connection test")
    success = test_connection()
    
    if success:
        logger.info("Database connection test completed successfully")
        sys.exit(0)
    else:
        logger.error("Database connection test failed")
        sys.exit(1) 