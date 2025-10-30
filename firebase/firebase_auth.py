# Module xử lý Authentication với Firebase
from .firebase_config import auth, db
import json
import bcrypt

# Biến lưu trạng thái user hiện tại
current_user = None
current_user_token = None

def hash_password(password):
    """
    Mã hóa mật khẩu bằng bcrypt
    
    Args:
        password (str): Mật khẩu gốc
    
    Returns:
        str: Mật khẩu đã hash
    """
    salt = bcrypt.gensalt(rounds=10)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """
    Kiểm tra mật khẩu với mật khẩu hash
    
    Args:
        password (str): Mật khẩu gốc
        hashed_password (str): Mật khẩu đã hash
    
    Returns:
        bool: True nếu khớp, False nếu không
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(email, password, username):
    """
    Đăng ký tài khoản mới
    
    Returns:
        dict: {'success': bool, 'message': str, 'user': dict/None}
    """
    try:
        # Kiểm tra input rỗng
        if not email or not email.strip():
            return {
                'success': False,
                'message': 'email_required',
                'user': None
            }
        
        if not password or not password.strip():
            return {
                'success': False,
                'message': 'password_required',
                'user': None
            }
        
        if not username or not username.strip():
            return {
                'success': False,
                'message': 'username_required',
                'user': None
            }
        
        # Kiểm tra độ dài mật khẩu
        if len(password) < 6:
            return {
                'success': False,
                'message': 'password_too_short',
                'user': None
            }
        
        # Kiểm tra độ dài username
        if len(username) < 3:
            return {
                'success': False,
                'message': 'username_too_short',
                'user': None
            }
        
        # Tạo tài khoản với Firebase Auth TRƯỚC
        user = auth.create_user_with_email_and_password(email, password)
        
        # Lấy token để authenticate khi ghi database
        user_token = user['idToken']
        
        # Lưu thông tin user vào Realtime Database với token
        user_data = {
            'email': email,
            'username': username,
            'password_hash': hash_password(password),  # Lưu mật khẩu hash
            'created_at': str(__import__('datetime').datetime.now()),
            'scores': {
                'very_easy': {
                    'wins': 0,
                    'losses': 0,
                    'draws': 0,
                    'total': 0,
                    'winRate': 0.0,
                    'score': 0
                },
                'easy': {
                    'wins': 0,
                    'losses': 0,
                    'draws': 0,
                    'total': 0,
                    'winRate': 0.0,
                    'score': 0
                },
                'medium': {
                    'wins': 0,
                    'losses': 0,
                    'draws': 0,
                    'total': 0,
                    'winRate': 0.0,
                    'score': 0
                },
                'hard': {
                    'wins': 0,
                    'losses': 0,
                    'draws': 0,
                    'total': 0,
                    'winRate': 0.0,
                    'score': 0
                }
            }
        }
        
        # Ghi vào database với authentication token
        db.child("users").child(user['localId']).set(user_data, user_token)
        
        # Tự động đăng nhập user sau khi đăng ký thành công
        global current_user, current_user_token
        current_user = {
            'uid': user['localId'],
            'email': email,
            'username': username,
            'scores': user_data['scores']
        }
        current_user_token = user['idToken']
        
        
        return {
            'success': True,
            'message': 'register_success',
            'user': current_user
        }
        
    except Exception as e:
        error_message = str(e)
        print(f"Error in register_user: {error_message}")  # Debug
        
        # Xử lý các lỗi Firebase
        if 'EMAIL_EXISTS' in error_message:
            return {
                'success': False,
                'message': 'email_exists',
                'user': None
            }
        elif 'WEAK_PASSWORD' in error_message:
            return {
                'success': False,
                'message': 'password_too_short',
                'user': None
            }
        elif 'INVALID_EMAIL' in error_message:
            return {
                'success': False,
                'message': 'invalid_email',
                'user': None
            }
        else:
            return {
                'success': False,
                'message': 'register_failed',
                'user': None
            }

def login_user(email, password):
    """
    Đăng nhập tài khoản
    
    Returns:
        dict: {'success': bool, 'message': str, 'user': dict/None}
    """
    global current_user, current_user_token
    
    # Kiểm tra input rỗng
    if not email or not email.strip():
        return {
            'success': False,
            'message': 'email_required',
            'user': None
        }
    
    if not password or not password.strip():
        return {
            'success': False,
            'message': 'password_required',
            'user': None
        }
    
    try:
        # Đăng nhập với Firebase Auth
        user = auth.sign_in_with_email_and_password(email, password)
        user_token = user['idToken']
        
        # Lấy thông tin user từ Database với token
        user_data = db.child("users").child(user['localId']).get(user_token).val()
        
        if user_data:
            # Kiểm tra mật khẩu hash (nếu có)
            if 'password_hash' in user_data:
                if not verify_password(password, user_data['password_hash']):
                    return {
                        'success': False,
                        'message': 'invalid_credentials',
                        'user': None
                    }
            
            current_user = {
                'uid': user['localId'],
                'email': user_data['email'],
                'username': user_data['username'],
                'scores': user_data.get('scores', {})
            }
            current_user_token = user['idToken']
            
            return {
                'success': True,
                'message': 'login_success',
                'user': current_user
            }
        else:
            return {
                'success': False,
                'message': 'user_not_found',
                'user': None
            }
            
    except Exception as e:
        error_message = str(e)
        print(f"Error in login_user: {error_message}")  # Debug
        
        # Xử lý các lỗi Firebase
        if 'INVALID_EMAIL' in error_message:
            return {
                'success': False,
                'message': 'invalid_email',
                'user': None
            }
        elif 'EMAIL_NOT_FOUND' in error_message or 'INVALID_PASSWORD' in error_message or 'INVALID_LOGIN_CREDENTIALS' in error_message:
            return {
                'success': False,
                'message': 'invalid_credentials',
                'user': None
            }
        else:
            return {
                'success': False,
                'message': 'login_failed',
                'user': None
            }

def logout_user():
    """Đăng xuất user hiện tại"""
    global current_user, current_user_token
    current_user = None
    current_user_token = None

def get_current_user():
    """Lấy thông tin user hiện tại"""
    return current_user

def update_user_scores(mode, result):
    """
    Cập nhật điểm số của user
    
    Args:
        mode: 'very_easy', 'easy', 'medium', 'hard'
        result: 'win', 'loss', 'draw'
    """
    global current_user, current_user_token
    
    if not current_user or not current_user_token:
        return False
    
    try:
        uid = current_user['uid']
        
        # Lấy scores hiện tại với token
        scores = db.child("users").child(uid).child("scores").child(mode).get(current_user_token).val()
        
        if not scores:
            scores = {
                'wins': 0,
                'losses': 0,
                'draws': 0,
                'total': 0,
                'winRate': 0.0,
                'score': 0
            }
        
        # Cập nhật scores
        scores['total'] += 1
        
        if result == 'win':
            scores['wins'] += 1
            scores['score'] += 10  # +10 điểm cho thắng
        elif result == 'loss':
            scores['losses'] += 1
            scores['score'] = max(0, scores['score'] - 5)  # -5 điểm cho thua (min 0)
        elif result == 'draw':
            scores['draws'] += 1
            scores['score'] += 3  # +3 điểm cho hòa
        
        # Tính win rate
        if scores['total'] > 0:
            scores['winRate'] = (scores['wins'] / scores['total']) * 100
        
        # Cập nhật vào Firebase với token
        db.child("users").child(uid).child("scores").child(mode).update(scores, current_user_token)
        
        # Cập nhật current_user
        current_user['scores'][mode] = scores
        
        return True
        
    except Exception as e:
        print(f"Error updating scores: {e}")
        return False

def get_user_scores():
    """Lấy điểm số của user hiện tại"""
    if current_user and 'scores' in current_user:
        return current_user['scores']
    return None

def migrate_add_password_hash(email, password):
    """
    Hàm di chuyển dữ liệu: Thêm password_hash cho user cũ
    Sử dụng khi user đã tồn tại nhưng chưa có password_hash
    
    Args:
        email (str): Email của user
        password (str): Mật khẩu gốc của user
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        # Đăng nhập với Firebase Auth để lấy uid
        user = auth.sign_in_with_email_and_password(email, password)
        user_token = user['idToken']
        uid = user['localId']
        
        # Lấy dữ liệu user hiện tại
        user_data = db.child("users").child(uid).get(user_token).val()
        
        if user_data and 'password_hash' not in user_data:
            # Thêm password hash
            user_data['password_hash'] = hash_password(password)
            if 'created_at' not in user_data:
                user_data['created_at'] = str(__import__('datetime').datetime.now())
            
            # Cập nhật lên database
            db.child("users").child(uid).set(user_data, user_token)
            
            return {
                'success': True,
                'message': 'migration_success'
            }
        elif user_data and 'password_hash' in user_data:
            return {
                'success': True,
                'message': 'already_has_password_hash'
            }
        else:
            return {
                'success': False,
                'message': 'user_not_found'
            }
            
    except Exception as e:
        error_message = str(e)
        print(f"Error in migrate_add_password_hash: {error_message}")
        return {
            'success': False,
            'message': str(e)
        }

