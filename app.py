#!/usr/bin/env python
"""
Frontend launcher for the Product Recommendation System.
"""
import os
import sys
import webbrowser
from threading import Timer

# Add the root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from src.frontend.app import app

if __name__ == "__main__":
    print("Starting Product Recommendation Frontend...")
    print("Dataset images will be loaded from:")
    print(f"  {os.path.join(project_root, 'datasets', 'amazon-2023-all(set)', 'images')}")
    print("\nOpening browser to http://localhost:3000")
    
    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=3000) 
