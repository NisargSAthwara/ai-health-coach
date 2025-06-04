# backend/data/init_db.py

import sys
import os

# Add the project root to sys.path to enable absolute imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from backend.data.db import engine
from models.db_models import Base

def init_tables():
    # print("Attempting to drop existing database tables...")
    # Base.metadata.drop_all(bind=engine)
    # print("Existing database tables dropped.")
    print("Attempting to create new database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables creation attempt complete.")

if __name__ == "__main__":
    init_tables()
