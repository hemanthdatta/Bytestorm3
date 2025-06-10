#!/bin/bash

echo "Starting startup script for Azure App Service..."

# Set Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)
echo "PYTHONPATH set to $PYTHONPATH"

# Activate Python environment if needed
if [ -d .venv ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Install requirements
echo "Installing requirements..."
pip install -r requirements-azure.txt

# Run migrations if needed (assuming Flask-Migrate is used)
# python -m flask db upgrade

# Start the application with Gunicorn
echo "Starting application with Gunicorn..."
gunicorn --bind=0.0.0.0:$PORT --timeout 600 application:app 