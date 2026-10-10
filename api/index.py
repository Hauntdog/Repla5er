import sys
import os

# Add the parent directory to sys.path so replacer can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from replacer import create_app

app = create_app()
