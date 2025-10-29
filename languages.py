# Hệ thống đa ngôn ngữ cho game cờ vua
# Multilingual system for chess game

TRANSLATIONS = {
    'vi': {
        # Menu chính
        'start': 'Chơi với AI',
        'two_players': 'Hai người chơi',
        'statistics': 'Bảng điểm',
        'settings': 'Cài đặt',
        'exit': 'Thoát',
        
        # Menu độ khó AI
        'ai_difficulty_title': 'CHỌN ĐỘ KHÓ',
        'difficulty_easy': 'Dễ',
        'difficulty_medium': 'Trung bình',
        'difficulty_hard': 'Khó',
        
        # Settings
        'settings_title': 'CÀI ĐẶT',
        'sound': 'Âm thanh',
        'language': 'Ngôn ngữ',
        'on': 'Bật',
        'off': 'Tắt',
        'back': 'Quay lại',
        
        # Game
        'reset': 'Làm mới',
        'undo': 'Hoàn tác',
        'menu': 'Menu',
        'settings_btn': 'Cài đặt',
        
        # Game Modes
        'mode_easy': 'AI Dễ',
        'mode_medium': 'AI Trung bình', 
        'mode_hard': 'AI Khó',
        'mode_two_players': 'Hai người chơi',
        'current_mode': 'Chế độ:',
        
        # End game
        'checkmate_white': 'Trắng thắng bằng chiếu hết',
        'checkmate_black': 'Đen thắng bằng chiếu hết',
        'stalemate': 'Hòa cờ',
        
        # Pawn promotion
        'promotion_title': 'Chọn quân cờ phong cấp:',
        'queen': 'Hậu',
        'rook': 'Xe',
        'bishop': 'Tượng',
        'knight': 'Mã',
        
        # Statistics
        'stats_title': 'BẢNG ĐIỂM',
        'stats_total_games': 'Tổng số trận:',
        'stats_vs_ai': 'Đấu với AI:',
        'stats_easy': 'Dễ:',
        'stats_medium': 'TB:',
        'stats_hard': 'Khó:',
        'stats_two_players': 'Hai người:',
        'stats_wins': 'Thắng',
        'stats_losses': 'Thua',
        'stats_draws': 'Hòa',
        'stats_white_wins': 'Trắng thắng',
        'stats_black_wins': 'Đen thắng',
        'stats_win_rate': 'Tỉ lệ thắng:',
        'stats_reset': 'Xóa dữ liệu',
        'stats_no_games': 'Chưa có trận đấu nào!',
        
        # Authentication
        'login': 'Đăng nhập',
        'register': 'Đăng ký',
        'logout': 'Đăng xuất',
        'email': 'Email:',
        'password': 'Mật khẩu:',
        'username': 'Tên người chơi:',
        'login_title': 'ĐĂNG NHẬP',
        'register_title': 'ĐĂNG KÝ',
        'login_button': 'Đăng nhập',
        'register_button': 'Đăng ký',
        'go_to_register': 'Chưa có tài khoản? Đăng ký',
        'go_to_login': 'Đã có tài khoản? Đăng nhập',
        'guest_mode': 'Chơi không cần đăng nhập',
        
        # Auth Messages
        'register_success': 'Đăng ký thành công!',
        'login_success': 'Đăng nhập thành công!',
        'logout_success': 'Đăng xuất thành công!',
        'email_exists': 'Email đã được sử dụng!',
        'email_required': 'Vui lòng nhập Email!',
        'password_required': 'Vui lòng nhập Mật khẩu!',
        'username_required': 'Vui lòng nhập Tên người chơi!',
        'password_too_short': 'Mật khẩu phải ít nhất 6 ký tự!',
        'username_too_short': 'Tên phải ít nhất 3 ký tự!',
        'invalid_email': 'Email không hợp lệ!',
        'invalid_credentials': 'Email hoặc mật khẩu không đúng!',
        'register_failed': 'Đăng ký thất bại!',
        'login_failed': 'Đăng nhập thất bại!',
        'user_not_found': 'Không tìm thấy người dùng!',
        'welcome': 'Xin chào,',
    },
    'en': {
        # Main menu
        'start': 'Play vs AI',
        'two_players': 'Two Players',
        'statistics': 'Statistics',
        'settings': 'Settings',
        'exit': 'Exit',
        
        # AI Difficulty Menu
        'ai_difficulty_title': 'CHOOSE DIFFICULTY',
        'difficulty_easy': 'Easy',
        'difficulty_medium': 'Medium',
        'difficulty_hard': 'Hard',
        
        # Settings
        'settings_title': 'SETTINGS',
        'sound': 'Sound',
        'language': 'Language',
        'on': 'On',
        'off': 'Off',
        'back': 'Back',
        
        # Game
        'reset': 'Reset',
        'undo': 'Undo',
        'menu': 'Menu',
        'settings_btn': 'Settings',
        
        # Game Modes
        'mode_easy': 'AI Easy',
        'mode_medium': 'AI Medium',
        'mode_hard': 'AI Hard', 
        'mode_two_players': 'Two Players',
        'current_mode': 'Mode:',
        
        # End game
        'checkmate_white': 'White wins by checkmate',
        'checkmate_black': 'Black wins by checkmate',
        'stalemate': 'Stalemate',
        
        # Pawn promotion
        'promotion_title': 'Choose promotion piece:',
        'queen': 'Queen',
        'rook': 'Rook',
        'bishop': 'Bishop',
        'knight': 'Knight',
        
        # Statistics
        'stats_title': 'STATISTICS',
        'stats_total_games': 'Total Games:',
        'stats_vs_ai': 'VS AI:',
        'stats_easy': 'Easy:',
        'stats_medium': 'Med:',
        'stats_hard': 'Hard:',
        'stats_two_players': 'Two Players:',
        'stats_wins': 'Wins',
        'stats_losses': 'Losses',
        'stats_draws': 'Draws',
        'stats_white_wins': 'White Wins',
        'stats_black_wins': 'Black Wins',
        'stats_win_rate': 'Win Rate:',
        'stats_reset': 'Reset Data',
        'stats_no_games': 'No games played yet!',
        
        # Authentication
        'login': 'Login',
        'register': 'Register',
        'logout': 'Logout',
        'email': 'Email:',
        'password': 'Password:',
        'username': 'Username:',
        'login_title': 'LOGIN',
        'register_title': 'REGISTER',
        'login_button': 'Login',
        'register_button': 'Register',
        'go_to_register': "Don't have account? Register",
        'go_to_login': 'Have account? Login',
        'guest_mode': 'Play as Guest',
        
        # Auth Messages
        'register_success': 'Registration successful!',
        'login_success': 'Login successful!',
        'logout_success': 'Logout successful!',
        'email_exists': 'Email already used!',
        'email_required': 'Please enter Email!',
        'password_required': 'Please enter Password!',
        'username_required': 'Please enter Username!',
        'password_too_short': 'Password must be at least 6 characters!',
        'username_too_short': 'Username must be at least 3 characters!',
        'invalid_email': 'Invalid email!',
        'invalid_credentials': 'Email or password incorrect!',
        'register_failed': 'Registration failed!',
        'login_failed': 'Login failed!',
        'user_not_found': 'User not found!',
        'welcome': 'Welcome,',
    }
}

def get_text(key, language='vi'):
    """Lấy text theo ngôn ngữ hiện tại"""
    return TRANSLATIONS.get(language, TRANSLATIONS['vi']).get(key, key)

