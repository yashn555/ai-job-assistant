import sys
import os

# Add root directory to python module search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app

# Vercel serverless entrypoint
handler = app
