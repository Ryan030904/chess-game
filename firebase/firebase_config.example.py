"""
Firebase configuration example (tracked).

Copy this file to `firebase/firebase_config.py` OR create a `.env` file with the variables from `env_example.txt`.
This example is safe to keep in the repo because it contains no real keys.
"""

import os
import pyrebase
from dotenv import load_dotenv

load_dotenv()

firebaseConfig = {
    "apiKey": os.getenv("FIREBASE_API_KEY", "your_api_key_here"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "your_project.firebaseapp.com"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL", "https://your_project-default-rtdb.region.firebasedatabase.app"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID", "your_project_id"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", "your_project.firebasestorage.app"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", "your_sender_id"),
    "appId": os.getenv("FIREBASE_APP_ID", "your_app_id"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID", "your_measurement_id"),
}

# Initialize Firebase (will fail if placeholders are not replaced or env not set)
try:
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()
    db = firebase.database()
except Exception:
    # If you keep placeholders, initialization will likely fail; that's expected for the example file.
    firebase = None
    auth = None
    db = None
