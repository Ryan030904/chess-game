# Firebase Configuration cho Game Cờ Vua
import pyrebase
import os
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# Cấu hình Firebase từ biến môi trường
firebaseConfig = {
    "apiKey": os.getenv("FIREBASE_API_KEY", "AIzaSyDaLD3smPexm0fM366IgkIsiQIFumnR54E"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", "gamecovua-a75c9.firebaseapp.com"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL", "https://gamecovua-a75c9-default-rtdb.asia-southeast1.firebasedatabase.app"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID", "gamecovua-a75c9"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", "gamecovua-a75c9.firebasestorage.app"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", "186437598567"),
    "appId": os.getenv("FIREBASE_APP_ID", "1:186437598567:web:763e367e161339c43943c2"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID", "G-M7NPR9VYLJ")
}

# Khởi tạo Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

