# Hướng dẫn Setup Dự án

## Bước 1: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

## Bước 2: Cấu hình Firebase

### Tạo file .env
1. Sao chép file `env_example.txt` thành `.env`
2. Điền thông tin Firebase của bạn vào file `.env`:

```env
FIREBASE_API_KEY=your_api_key_here
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_DATABASE_URL=https://your_project-default-rtdb.region.firebasedatabase.app
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project.firebasestorage.app
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
FIREBASE_MEASUREMENT_ID=your_measurement_id
```

### Lấy thông tin Firebase
1. Truy cập [Firebase Console](https://console.firebase.google.com/)
2. Chọn dự án của bạn
3. Vào Project Settings (biểu tượng bánh răng)
4. Scroll xuống phần "Your apps" và chọn Web app
5. Sao chép thông tin cấu hình

## Bước 3: Cấu hình Firebase Database Rules

1. Vào Firebase Console > Realtime Database
2. Chọn tab "Rules"
3. Import file `firebase/FIREBASE_RULES_FINAL.json`

## Bước 4: Chạy game

```bash
python main.py
```

## Lưu ý bảo mật

- **KHÔNG** commit file `.env` lên Git
- **KHÔNG** chia sẻ thông tin Firebase với người khác
- File `.env` đã được thêm vào `.gitignore` để tự động ẩn

## Troubleshooting

### Lỗi "ModuleNotFoundError: No module named 'dotenv'"
```bash
pip install python-dotenv
```

### Lỗi Firebase connection
- Kiểm tra thông tin trong file `.env`
- Đảm bảo Firebase project đã được tạo và cấu hình đúng
- Kiểm tra Firebase Database Rules đã được import
