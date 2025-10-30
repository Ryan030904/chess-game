import pygame as p
import SmartMove
import ChessEngine
import json
import os
from languages import get_text
from statistics import load_statistics, save_statistics, record_game_result, get_statistics_summary
from firebase.firebase_auth import register_user, login_user, logout_user, get_current_user, update_user_scores

# Khởi tạo Pygame
p.init()

# Các hằng số
DIMENTION = 8  # Kích thước bàn cờ (8x8)
BAR_HEIGHT = 50  # Chiều cao của thanh điều khiển
SQ_SIZE = 88  # Kích thước của mỗi ô vuông trên bàn cờ (88*8 = 704)
BOARD_SIZE = SQ_SIZE * DIMENTION  # Kích thước bàn cờ = 88 * 8 = 704
WIDTH = BOARD_SIZE  # Chiều rộng cửa sổ = chiều rộng bàn cờ = 704
HEIGHT = BOARD_SIZE + BAR_HEIGHT  # Chiều cao cửa sổ = bàn cờ + thanh điều khiển = 704 + 50 = 754
MAX_FPS = 15  # Tốc độ khung hình tối đa của trò chơi
IMAGES = {}  # Từ điển để lưu trữ hình ảnh các quân cờ

# Cài đặt game
SETTINGS_FILE = 'firebase/settings.json'
game_settings = {
    'sound_enabled': True,
    'language': 'vi',
    'ai_difficulty': 'medium'  # very_easy, easy, medium, hard
}

# Tải cài đặt từ file
def load_settings():
    global game_settings
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                game_settings = json.load(f)
    except:
        pass

# Lưu cài đặt vào file
def save_settings():
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(game_settings, f, indent=2)
    except:
        pass

# Cache cho font để tránh load lại
_font_cache = {}

# Hàm vẽ text với hiệu ứng glow bạch kim
def draw_glow_text(screen, text, font, x, y, color=p.Color('white'), glow_color=p.Color(200, 200, 255), glow_size=3):
    """Vẽ text với hiệu ứng glow bạch kim"""
    # Vẽ glow (nhiều lớp với độ mờ giảm dần)
    for i in range(glow_size, 0, -1):
        alpha = int(50 * (glow_size - i + 1) / glow_size)
        glow_surface = font.render(text, True, glow_color)
        glow_surface.set_alpha(alpha)
        
        # Vẽ glow ở 8 hướng
        for dx in [-i, 0, i]:
            for dy in [-i, 0, i]:
                if dx != 0 or dy != 0:
                    screen.blit(glow_surface, (x + dx, y + dy))
    
    # Vẽ text chính
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# Hàm lấy font hỗ trợ Unicode
def get_unicode_font(size, bold=True):
    """Tạo font hỗ trợ tiếng Việt với cache"""
    cache_key = f"{size}_{bold}"
    
    # Kiểm tra cache trước
    if cache_key in _font_cache:
        return _font_cache[cache_key]
    
    # Thử font tùy chỉnh trước
    custom_fonts = [
        "./assets/OpenSans_Condensed-MediumItalic.ttf",
        "./assets/OpenSans_Condensed-Medium.ttf",
        "./assets/OpenSans_Condensed-Regular.ttf"
    ]
    
    for font_path in custom_fonts:
        try:
            if os.path.exists(font_path):
                # Sử dụng đường dẫn tuyệt đối để tránh lỗi
                abs_path = os.path.abspath(font_path)
                font = p.font.Font(abs_path, size)
                # Test xem font có hỗ trợ tiếng Việt không
                test_render = font.render("ắ", True, (0, 0, 0))
                if test_render.get_width() > 0:  # Nếu render được
                    _font_cache[cache_key] = font
                    return font
        except Exception as e:
            continue
    
    # Nếu không tìm được font tùy chỉnh, thử font hệ thống
    font_names = [
        "Arial",
        "Segoe UI", 
        "Tahoma",
        "Verdana",
        "Calibri",
        "Times New Roman",
        "Microsoft Sans Serif"
    ]
    
    # Thử từng font cho đến khi tìm được
    for font_name in font_names:
        try:
            font = p.font.SysFont(font_name, size, bold, False)
            # Test xem font có hỗ trợ tiếng Việt không
            test_render = font.render("ắ", True, (0, 0, 0))
            if test_render.get_width() > 0:  # Nếu render được
                _font_cache[cache_key] = font
                return font
        except Exception as e:
            continue
    
    # Nếu không tìm được, dùng font mặc định
    default_font = p.font.Font(None, size)
    _font_cache[cache_key] = default_font
    return default_font

# Tải hình ảnh các quân cờ
def loadImage():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    # Tải hình ảnh cho từng quân cờ và chỉnh kích thước để phù hợp với ô vuông
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("./assets/imgs-80px/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

# Vẽ menu lên màn hình
def drawMenu(screen):
    background = p.image.load("./assets/backgrounds/back3.png")  # Tải ảnh nền
    background = p.transform.scale(background, (WIDTH, HEIGHT))  # Thay đổi kích thước ảnh nền
    screen.blit(background, (0, 0))  # Vẽ ảnh nền lên toàn màn hình

    lang = game_settings['language']
    
    # Vẽ profile box ở góc phải nếu đã đăng nhập
    current_user = get_current_user()
    logoutButtonRect = None
    
    if current_user:
        # Vẽ profile box ở góc phải màn hình
        profileBoxRect = p.Rect(WIDTH - 220, 20, 200, 120)
        
        # Vẽ shadow
        shadow_rect = p.Rect(profileBoxRect.x + 2, profileBoxRect.y + 2, profileBoxRect.width, profileBoxRect.height)
        p.draw.rect(screen, p.Color(0, 0, 0, 50), shadow_rect, border_radius=10)
        
        # Vẽ background chính
        p.draw.rect(screen, p.Color(255, 255, 255), profileBoxRect, border_radius=10)
        p.draw.rect(screen, p.Color(70, 130, 180), profileBoxRect, 2, border_radius=10)
        
        # Hiển thị "Xin chào,"
        nameFont = get_unicode_font(16, True)
        welcomeText = nameFont.render(get_text('welcome', lang), True, p.Color(70, 130, 180))
        screen.blit(welcomeText, (profileBoxRect.x + 10, profileBoxRect.y + 10))
        
        # Hiển thị username
        usernameFont = get_unicode_font(18, True)
        usernameText = usernameFont.render(current_user['username'], True, p.Color(0, 0, 0))
        screen.blit(usernameText, (profileBoxRect.x + 10, profileBoxRect.y + 30))
        
        # Nút đăng xuất
        logoutButtonRect = p.Rect(profileBoxRect.x + 30, profileBoxRect.y + 70, 140, 35)
        p.draw.rect(screen, p.Color(220, 53, 69), logoutButtonRect, border_radius=5)
        p.draw.rect(screen, p.Color(255, 69, 85), logoutButtonRect.inflate(-2, -2), border_radius=5)
        logoutFont = get_unicode_font(16, True)
        logoutText = logoutFont.render(get_text('logout', lang), True, p.Color('white'))
        logoutTextRect = logoutText.get_rect(center=logoutButtonRect.center)
        screen.blit(logoutText, logoutTextRect)
    
    startButtonRect = p.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 120, 200, 50)
    aiButtonRect = p.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50)
    statsButtonRect = p.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 50)
    settingsButtonRect = p.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50)
    exitButtonRect = p.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 120, 200, 50)

    drawButtonUnicode(screen, get_text('start', lang), startButtonRect)
    drawButtonUnicode(screen, get_text('two_players', lang), aiButtonRect)
    drawButtonUnicode(screen, get_text('statistics', lang), statsButtonRect)
    drawButtonUnicode(screen, get_text('settings', lang), settingsButtonRect)
    drawButtonUnicode(screen, get_text('exit', lang), exitButtonRect)

    p.display.flip()
    
    return startButtonRect, aiButtonRect, statsButtonRect, settingsButtonRect, exitButtonRect, logoutButtonRect

# Vẽ menu chọn độ khó AI
def drawAIDifficultyMenu(screen):
    background = p.image.load("./assets/backgrounds/back3.png")
    background = p.transform.scale(background, (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    
    lang = game_settings['language']
    
    # Tiêu đề với hiệu ứng glow
    titleFont = get_unicode_font(48, True)
    titleText = get_text('ai_difficulty_title', lang)
    titleX = WIDTH // 2 - titleFont.size(titleText)[0] // 2
    titleY = 80
    draw_glow_text(screen, titleText, titleFont, titleX, titleY, p.Color('black'), p.Color(200, 200, 255), 4)
    
    # 4 nút độ khó
    veryEasyButtonRect = p.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 90, 200, 45)
    easyButtonRect = p.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 30, 200, 45)
    mediumButtonRect = p.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 30, 200, 45)
    hardButtonRect = p.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 90, 200, 45)
    
    drawButtonUnicode(screen, get_text('difficulty_very_easy', lang), veryEasyButtonRect)
    drawButtonUnicode(screen, get_text('difficulty_easy', lang), easyButtonRect)
    drawButtonUnicode(screen, get_text('difficulty_medium', lang), mediumButtonRect)
    drawButtonUnicode(screen, get_text('difficulty_hard', lang), hardButtonRect)
    
    # Nút quay lại
    backButtonRect = p.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)
    drawButtonUnicode(screen, get_text('back', lang), backButtonRect)

    p.display.flip()
    
    return veryEasyButtonRect, easyButtonRect, mediumButtonRect, hardButtonRect, backButtonRect

# Vẽ màn hình Statistics (Bảng điểm)
def drawStatistics(screen):
    background = p.image.load("./assets/backgrounds/back3.png")
    background = p.transform.scale(background, (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    
    lang = game_settings['language']
    stats = get_statistics_summary()
    
    # Tiêu đề với hiệu ứng glow
    titleFont = get_unicode_font(48, True)
    titleText = get_text('stats_title', lang)
    titleX = WIDTH // 2 - titleFont.size(titleText)[0] // 2
    titleY = 60
    draw_glow_text(screen, titleText, titleFont, titleX, titleY, p.Color('black'), p.Color(200, 200, 255), 4)
    
    # Nếu chưa có trận nào
    if stats['total_games'] == 0:
        noGamesFont = get_unicode_font(32, True)
        noGamesText = noGamesFont.render(get_text('stats_no_games', lang), True, p.Color('yellow'))
        screen.blit(noGamesText, (WIDTH // 2 - noGamesText.get_width() // 2, HEIGHT // 2))
    else:
        # Tạo bảng thống kê chi tiết
        drawStatsTable(screen, stats, lang)
    
    # Nút Reset và Back
    resetStatsButtonRect = p.Rect(WIDTH // 2 - 220, HEIGHT - 120, 180, 50)
    backButtonRect = p.Rect(WIDTH // 2 + 40, HEIGHT - 120, 180, 50)
    
    # Nút Reset màu đỏ
    resetFont = get_unicode_font(22, True)
    p.draw.rect(screen, p.Color('darkred'), resetStatsButtonRect, border_radius=5)
    p.draw.rect(screen, p.Color('red'), resetStatsButtonRect.inflate(-4, -4), border_radius=5)
    resetText = resetFont.render(get_text('stats_reset', lang), True, p.Color('white'))
    resetTextRect = resetText.get_rect(center=resetStatsButtonRect.center)
    screen.blit(resetText, resetTextRect)
    
    # Nút Back
    drawButtonUnicode(screen, get_text('back', lang), backButtonRect)

    p.display.flip()
    
    return resetStatsButtonRect, backButtonRect

def drawStatsTable(screen, stats, lang):
    """Vẽ bảng thống kê chi tiết với khung đẹp"""
    # Fonts
    headerFont = get_unicode_font(18, True)
    dataFont = get_unicode_font(14, False)
    titleFont = get_unicode_font(22, True)
    modeFont = get_unicode_font(16, True)
    
    # Kích thước bảng
    tableX = 50
    tableY = 120
    tableWidth = WIDTH - 100
    tableHeight = 450
    
    # Vẽ khung bảng chính với shadow
    shadowRect = p.Rect(tableX + 3, tableY + 3, tableWidth, tableHeight)
    p.draw.rect(screen, p.Color(0, 0, 0, 100), shadowRect, border_radius=15)
    
    mainTableRect = p.Rect(tableX, tableY, tableWidth, tableHeight)
    p.draw.rect(screen, p.Color(25, 25, 35), mainTableRect, border_radius=15)
    p.draw.rect(screen, p.Color(70, 130, 180), mainTableRect, 3, border_radius=15)
    
    # Tiêu đề bảng
    tableTitle = titleFont.render("📊 BẢNG THỐNG KÊ CHI TIẾT", True, p.Color('white'))
    screen.blit(tableTitle, (tableX + 20, tableY + 20))
    
    # Tổng số trận
    totalText = headerFont.render(f"🎮 Tổng số trận: {stats['total_games']}", True, p.Color('cyan'))
    screen.blit(totalText, (tableX + 20, tableY + 50))
    
    # Header của bảng
    headerY = tableY + 90
    headerHeight = 40
    colWidth = (tableWidth - 40) // 7  # Thêm cột tỷ lệ thua và hòa
    
    # Vẽ header với gradient
    headers = ["Chế độ", "Tổng", "Thắng", "Thua", "Hòa", "Tỷ lệ thắng", "Tỷ lệ thua"]
    headerColors = [
        p.Color('white'), 
        p.Color(100, 200, 255), 
        p.Color(100, 255, 100), 
        p.Color(255, 100, 100), 
        p.Color(255, 255, 100), 
        p.Color(100, 255, 200),
        p.Color(255, 150, 100)
    ]
    
    for i, (header, color) in enumerate(zip(headers, headerColors)):
        headerRect = p.Rect(tableX + 20 + i * colWidth, headerY, colWidth - 5, headerHeight)
        p.draw.rect(screen, p.Color(40, 40, 50), headerRect, border_radius=8)
        p.draw.rect(screen, color, headerRect.inflate(-2, -2), border_radius=8)
        
        headerText = dataFont.render(header, True, p.Color('black'))
        headerTextRect = headerText.get_rect(center=headerRect.center)
        screen.blit(headerText, headerTextRect)
    
    # Dữ liệu các chế độ
    dataY = headerY + headerHeight + 15
    rowHeight = 35
    rowSpacing = 8
    
    # Màu sắc cho từng chế độ
    modeColors = {
        'very_easy': p.Color(100, 200, 100),
        'easy': p.Color(50, 150, 50),
        'medium': p.Color(200, 150, 50), 
        'hard': p.Color(200, 50, 50),
        'two_players': p.Color(100, 50, 150)
    }
    
    # Tên chế độ với icon
    modeNames = {
        'very_easy': '🟢 AI Rất Dễ',
        'easy': '🟢 AI Dễ',
        'medium': '🟠 AI Trung bình',
        'hard': '🔴 AI Khó',
        'two_players': '👥 Hai người'
    }
    
    currentY = dataY
    modes = ['very_easy', 'easy', 'medium', 'hard', 'two_players']
    
    for mode in modes:
        if mode in stats['modes'] and stats['modes'][mode]['total'] > 0:
            modeData = stats['modes'][mode]
            
            # Vẽ hàng dữ liệu với hiệu ứng
            rowRect = p.Rect(tableX + 20, currentY, tableWidth - 40, rowHeight)
            p.draw.rect(screen, p.Color(35, 35, 45), rowRect, border_radius=8)
            p.draw.rect(screen, modeColors[mode], rowRect.inflate(-2, -2), border_radius=8)
            
            # Tính tỷ lệ
            total = modeData['total']
            if mode == 'two_players':
                wins = modeData['white_wins']
                losses = modeData['black_wins']
                draws = modeData['draws']
                winRate = (wins / total * 100) if total > 0 else 0
                lossRate = (losses / total * 100) if total > 0 else 0
            else:
                wins = modeData['wins']
                losses = modeData['losses']
                draws = modeData['draws']
                winRate = modeData['win_rate']
                lossRate = (losses / total * 100) if total > 0 else 0
            
            # Dữ liệu từng cột
            data = [
                modeNames[mode],
                str(total),
                str(wins),
                str(losses),
                str(draws),
                f"{winRate:.1f}%",
                f"{lossRate:.1f}%"
            ]
            
            for i, (text, color) in enumerate(zip(data, headerColors)):
                colRect = p.Rect(tableX + 20 + i * colWidth, currentY, colWidth - 5, rowHeight)
                textSurface = dataFont.render(text, True, p.Color('white'))
                textRect = textSurface.get_rect(center=colRect.center)
                screen.blit(textSurface, textRect)
            
            currentY += rowHeight + rowSpacing
    
    # Tổng kết với khung đẹp
    if currentY < tableY + tableHeight - 80:
        summaryY = currentY + 20
        summaryRect = p.Rect(tableX + 20, summaryY, tableWidth - 40, 60)
        p.draw.rect(screen, p.Color(20, 20, 30), summaryRect, border_radius=10)
        p.draw.rect(screen, p.Color(100, 100, 150), summaryRect.inflate(-2, -2), border_radius=10)
        
        # Tính tổng kết
        totalWins = sum(mode['wins'] for mode in stats['modes'].values() if 'wins' in mode)
        totalLosses = sum(mode['losses'] for mode in stats['modes'].values() if 'losses' in mode)
        totalDraws = sum(mode['draws'] for mode in stats['modes'].values() if 'draws' in mode)
        overallWinRate = (totalWins / stats['total_games'] * 100) if stats['total_games'] > 0 else 0
        overallLossRate = (totalLosses / stats['total_games'] * 100) if stats['total_games'] > 0 else 0
        
        # Vẽ tổng kết với nhiều dòng
        summaryText1 = f"🏆 TỔNG KẾT: {stats['total_games']} trận đấu"
        summaryText2 = f"✅ Thắng: {totalWins} ({overallWinRate:.1f}%) | ❌ Thua: {totalLosses} ({overallLossRate:.1f}%) | 🤝 Hòa: {totalDraws}"
        
        summarySurface1 = headerFont.render(summaryText1, True, p.Color('white'))
        summarySurface2 = dataFont.render(summaryText2, True, p.Color('lightgray'))
        
        screen.blit(summarySurface1, (summaryRect.x + 15, summaryRect.y + 10))
        screen.blit(summarySurface2, (summaryRect.x + 15, summaryRect.y + 35))

# Vẽ màn hình Login
def drawLogin(screen, email_text="", password_text="", message="", message_color='red', active_input=None):
    # Màu nền trắng sáng
    screen.fill(p.Color(240, 240, 245))
    
    lang = game_settings['language']
    
    # Vẽ khung nền cho form
    formRect = p.Rect(WIDTH // 2 - 250, 100, 500, 550)
    p.draw.rect(screen, p.Color(255, 255, 255), formRect, border_radius=15)
    p.draw.rect(screen, p.Color(70, 130, 180), formRect, 3, border_radius=15)
    
    # Tiêu đề với hiệu ứng glow
    titleFont = get_unicode_font(56, True)
    titleText = get_text('login_title', lang)
    titleX = WIDTH // 2 - titleFont.size(titleText)[0] // 2
    titleY = 140
    draw_glow_text(screen, titleText, titleFont, titleX, titleY, p.Color('black'), p.Color(100, 150, 200), 3)
    
    # Input boxes
    labelFont = get_unicode_font(22, True)
    inputFont = get_unicode_font(20, False)
    
    y = 230
    spacing = 100
    
    # Email
    emailLabel = labelFont.render(get_text('email', lang), True, p.Color(50, 50, 50))
    screen.blit(emailLabel, (formRect.x + 40, y))
    emailBoxRect = p.Rect(formRect.x + 40, y + 35, formRect.width - 80, 45)
    
    # Highlight nếu đang active
    if active_input == 'email':
        p.draw.rect(screen, p.Color(220, 235, 255), emailBoxRect, border_radius=8)
        p.draw.rect(screen, p.Color(70, 130, 180), emailBoxRect, 3, border_radius=8)
    else:
        p.draw.rect(screen, p.Color(230, 230, 230), emailBoxRect, border_radius=8)
        p.draw.rect(screen, p.Color(100, 149, 237), emailBoxRect, 2, border_radius=8)
    
    if email_text:
        emailDisplay = inputFont.render(email_text, True, p.Color(0, 0, 0))
        screen.blit(emailDisplay, (emailBoxRect.x + 15, emailBoxRect.y + 10))
    
    # Vẽ con trỏ nháy nếu đang active
    if active_input == 'email':
        cursor_x = emailBoxRect.x + 15 + inputFont.size(email_text)[0]
        if int(p.time.get_ticks() / 500) % 2:  # Nháy mỗi 0.5s
            p.draw.line(screen, p.Color(0, 0, 0), 
                       (cursor_x, emailBoxRect.y + 10), 
                       (cursor_x, emailBoxRect.y + 35), 2)
    
    y += spacing
    
    # Password
    passwordLabel = labelFont.render(get_text('password', lang), True, p.Color(50, 50, 50))
    screen.blit(passwordLabel, (formRect.x + 40, y))
    passwordBoxRect = p.Rect(formRect.x + 40, y + 35, formRect.width - 80, 45)
    
    # Highlight nếu đang active
    if active_input == 'password':
        p.draw.rect(screen, p.Color(220, 235, 255), passwordBoxRect, border_radius=8)
        p.draw.rect(screen, p.Color(70, 130, 180), passwordBoxRect, 3, border_radius=8)
    else:
        p.draw.rect(screen, p.Color(230, 230, 230), passwordBoxRect, border_radius=8)
        p.draw.rect(screen, p.Color(100, 149, 237), passwordBoxRect, 2, border_radius=8)
    
    if password_text:
        # Hiển thị dấu * thay vì mật khẩu thật
        passwordDisplay = inputFont.render('*' * len(password_text), True, p.Color(0, 0, 0))
        screen.blit(passwordDisplay, (passwordBoxRect.x + 15, passwordBoxRect.y + 10))
    
    # Vẽ con trỏ nháy nếu đang active
    if active_input == 'password':
        cursor_x = passwordBoxRect.x + 15 + inputFont.size('*' * len(password_text))[0]
        if int(p.time.get_ticks() / 500) % 2:  # Nháy mỗi 0.5s
            p.draw.line(screen, p.Color(0, 0, 0), 
                       (cursor_x, passwordBoxRect.y + 10), 
                       (cursor_x, passwordBoxRect.y + 35), 2)
    
    y += spacing - 10
    
    # Message (nếu có)
    if message:
        messageFont = get_unicode_font(18, True)
        color = p.Color('green') if message_color == 'green' else p.Color('red')
        messageText = messageFont.render(get_text(message, lang), True, color)
        screen.blit(messageText, (WIDTH // 2 - messageText.get_width() // 2, y))
        y += 35
    
    # Buttons
    loginButtonRect = p.Rect(formRect.x + 100, y + 20, formRect.width - 200, 50)
    # Vẽ button đẹp hơn
    p.draw.rect(screen, p.Color(70, 130, 180), loginButtonRect, border_radius=10)
    p.draw.rect(screen, p.Color(100, 149, 237), loginButtonRect.inflate(-4, -4), border_radius=10)
    loginFont = get_unicode_font(24, True)
    loginText = loginFont.render(get_text('login_button', lang), True, p.Color('white'))
    loginTextRect = loginText.get_rect(center=loginButtonRect.center)
    screen.blit(loginText, loginTextRect)
    
    registerLinkRect = p.Rect(formRect.x + 50, y + 85, formRect.width - 100, 35)
    registerLinkFont = get_unicode_font(17, False)
    registerLinkText = registerLinkFont.render(get_text('go_to_register', lang), True, p.Color(0, 100, 200))
    registerLinkTextRect = registerLinkText.get_rect(center=registerLinkRect.center)
    screen.blit(registerLinkText, registerLinkTextRect)

    p.display.flip()
    
    return emailBoxRect, passwordBoxRect, loginButtonRect, registerLinkRect

# Vẽ màn hình Register
def drawRegister(screen, email_text="", username_text="", password_text="", message="", message_color='red', active_input=None):
    # Màu nền trắng sáng (đồng bộ với Login)
    screen.fill(p.Color(240, 240, 245))
    
    lang = game_settings['language']
    
    # Vẽ khung nền cho form (đồng bộ màu xanh dương với Login)
    formRect = p.Rect(WIDTH // 2 - 250, 80, 500, 600)
    p.draw.rect(screen, p.Color(255, 255, 255), formRect, border_radius=15)
    p.draw.rect(screen, p.Color(70, 130, 180), formRect, 3, border_radius=15)
    
    # Tiêu đề với hiệu ứng glow (màu xanh dương)
    titleFont = get_unicode_font(56, True)
    titleText = get_text('register_title', lang)
    titleX = WIDTH // 2 - titleFont.size(titleText)[0] // 2
    titleY = 120
    draw_glow_text(screen, titleText, titleFont, titleX, titleY, p.Color('black'), p.Color(100, 150, 200), 3)
    
    # Input boxes
    labelFont = get_unicode_font(22, True)
    inputFont = get_unicode_font(20, False)
    
    y = 210
    spacing = 95
    
    # Email
    emailLabel = labelFont.render(get_text('email', lang), True, p.Color(50, 50, 50))
    screen.blit(emailLabel, (formRect.x + 40, y))
    emailBoxRect = p.Rect(formRect.x + 40, y + 35, formRect.width - 80, 45)
    
    # Highlight nếu đang active
    if active_input == 'email':
        p.draw.rect(screen, p.Color(220, 235, 255), emailBoxRect, border_radius=8)
        p.draw.rect(screen, p.Color(70, 130, 180), emailBoxRect, 3, border_radius=8)
    else:
        p.draw.rect(screen, p.Color(230, 230, 230), emailBoxRect, border_radius=8)
        p.draw.rect(screen, p.Color(100, 149, 237), emailBoxRect, 2, border_radius=8)
    
    if email_text:
        emailDisplay = inputFont.render(email_text, True, p.Color(0, 0, 0))
        screen.blit(emailDisplay, (emailBoxRect.x + 15, emailBoxRect.y + 10))
    
    # Vẽ con trỏ nháy
    if active_input == 'email':
        cursor_x = emailBoxRect.x + 15 + inputFont.size(email_text)[0]
        if int(p.time.get_ticks() / 500) % 2:
            p.draw.line(screen, p.Color(0, 0, 0), 
                       (cursor_x, emailBoxRect.y + 10), 
                       (cursor_x, emailBoxRect.y + 35), 2)
    
    y += spacing
    
    # Password (Chuyển lên trước Username)
    passwordLabel = labelFont.render(get_text('password', lang), True, p.Color(50, 50, 50))
    screen.blit(passwordLabel, (formRect.x + 40, y))
    passwordBoxRect = p.Rect(formRect.x + 40, y + 35, formRect.width - 80, 45)
    
    # Highlight nếu đang active
    if active_input == 'password':
        p.draw.rect(screen, p.Color(220, 235, 255), passwordBoxRect, border_radius=8)
        p.draw.rect(screen, p.Color(70, 130, 180), passwordBoxRect, 3, border_radius=8)
    else:
        p.draw.rect(screen, p.Color(230, 230, 230), passwordBoxRect, border_radius=8)
        p.draw.rect(screen, p.Color(100, 149, 237), passwordBoxRect, 2, border_radius=8)
    
    if password_text:
        passwordDisplay = inputFont.render('*' * len(password_text), True, p.Color(0, 0, 0))
        screen.blit(passwordDisplay, (passwordBoxRect.x + 15, passwordBoxRect.y + 10))
    
    # Vẽ con trỏ nháy
    if active_input == 'password':
        cursor_x = passwordBoxRect.x + 15 + inputFont.size('*' * len(password_text))[0]
        if int(p.time.get_ticks() / 500) % 2:
            p.draw.line(screen, p.Color(0, 0, 0), 
                       (cursor_x, passwordBoxRect.y + 10), 
                       (cursor_x, passwordBoxRect.y + 35), 2)
    
    y += spacing
    
    # Username (Chuyển xuống sau Password)
    usernameLabel = labelFont.render(get_text('username', lang), True, p.Color(50, 50, 50))
    screen.blit(usernameLabel, (formRect.x + 40, y))
    usernameBoxRect = p.Rect(formRect.x + 40, y + 35, formRect.width - 80, 45)
    
    # Highlight nếu đang active
    if active_input == 'username':
        p.draw.rect(screen, p.Color(220, 235, 255), usernameBoxRect, border_radius=8)
        p.draw.rect(screen, p.Color(70, 130, 180), usernameBoxRect, 3, border_radius=8)
    else:
        p.draw.rect(screen, p.Color(230, 230, 230), usernameBoxRect, border_radius=8)
        p.draw.rect(screen, p.Color(100, 149, 237), usernameBoxRect, 2, border_radius=8)
    
    if username_text:
        usernameDisplay = inputFont.render(username_text, True, p.Color(0, 0, 0))
        screen.blit(usernameDisplay, (usernameBoxRect.x + 15, usernameBoxRect.y + 10))
    
    # Vẽ con trỏ nháy
    if active_input == 'username':
        cursor_x = usernameBoxRect.x + 15 + inputFont.size(username_text)[0]
        if int(p.time.get_ticks() / 500) % 2:
            p.draw.line(screen, p.Color(0, 0, 0), 
                       (cursor_x, usernameBoxRect.y + 10), 
                       (cursor_x, usernameBoxRect.y + 35), 2)
    
    y += spacing - 10
    
    # Message (nếu có)
    if message:
        messageFont = get_unicode_font(18, True)
        color = p.Color('green') if message_color == 'green' else p.Color('red')
        messageText = messageFont.render(get_text(message, lang), True, color)
        screen.blit(messageText, (WIDTH // 2 - messageText.get_width() // 2, y))
        y += 35
    
    # Buttons (đồng bộ màu xanh dương)
    registerButtonRect = p.Rect(formRect.x + 100, y + 20, formRect.width - 200, 50)
    p.draw.rect(screen, p.Color(70, 130, 180), registerButtonRect, border_radius=10)
    p.draw.rect(screen, p.Color(100, 149, 237), registerButtonRect.inflate(-4, -4), border_radius=10)
    registerFont = get_unicode_font(24, True)
    registerText = registerFont.render(get_text('register_button', lang), True, p.Color('white'))
    registerTextRect = registerText.get_rect(center=registerButtonRect.center)
    screen.blit(registerText, registerTextRect)
    
    loginLinkRect = p.Rect(formRect.x + 50, y + 85, formRect.width - 100, 35)
    loginLinkFont = get_unicode_font(17, False)
    loginLinkText = loginLinkFont.render(get_text('go_to_login', lang), True, p.Color(0, 100, 200))
    loginLinkTextRect = loginLinkText.get_rect(center=loginLinkRect.center)
    screen.blit(loginLinkText, loginLinkTextRect)

    p.display.flip()
    
    return emailBoxRect, passwordBoxRect, usernameBoxRect, registerButtonRect, loginLinkRect

# Vẽ màn hình Settings
def drawSettings(screen):
    background = p.image.load("./assets/backgrounds/back3.png")
    background = p.transform.scale(background, (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    
    lang = game_settings['language']
    
    # Tiêu đề với hiệu ứng glow
    titleFont = get_unicode_font(48, True)
    titleText = get_text('settings_title', lang)
    titleX = WIDTH // 2 - titleFont.size(titleText)[0] // 2
    titleY = 100
    draw_glow_text(screen, titleText, titleFont, titleX, titleY, p.Color('black'), p.Color(200, 200, 255), 4)
    
    # Âm thanh
    soundLabel = get_unicode_font(28, True)
    soundText = soundLabel.render(get_text('sound', lang) + ':', True, p.Color('white'))
    screen.blit(soundText, (WIDTH // 2 - 150, 250))
    
    soundOnRect = p.Rect(WIDTH // 2 + 20, 240, 80, 40)
    soundOffRect = p.Rect(WIDTH // 2 + 110, 240, 80, 40)
    
    if game_settings['sound_enabled']:
        drawButtonUnicode(screen, get_text('on', lang), soundOnRect)
        p.draw.rect(screen, p.Color('gray'), soundOffRect, border_radius=5)
        p.draw.rect(screen, p.Color('darkgray'), soundOffRect.inflate(-4, -4), border_radius=5)
        text_surf = get_unicode_font(24, True).render(get_text('off', lang), True, p.Color('gray'))
        text_rect = text_surf.get_rect(center=soundOffRect.center)
        screen.blit(text_surf, text_rect)
    else:
        p.draw.rect(screen, p.Color('gray'), soundOnRect, border_radius=5)
        p.draw.rect(screen, p.Color('darkgray'), soundOnRect.inflate(-4, -4), border_radius=5)
        text_surf = get_unicode_font(24, True).render(get_text('on', lang), True, p.Color('gray'))
        text_rect = text_surf.get_rect(center=soundOnRect.center)
        screen.blit(text_surf, text_rect)
        drawButtonUnicode(screen, get_text('off', lang), soundOffRect)
    
    # Ngôn ngữ
    langLabel = get_unicode_font(28, True)
    langText = langLabel.render(get_text('language', lang) + ':', True, p.Color('white'))
    screen.blit(langText, (WIDTH // 2 - 150, 340))
    
    viButtonRect = p.Rect(WIDTH // 2 + 20, 330, 80, 40)
    enButtonRect = p.Rect(WIDTH // 2 + 110, 330, 80, 40)
    
    if game_settings['language'] == 'vi':
        drawButtonUnicode(screen, 'VN', viButtonRect)
        p.draw.rect(screen, p.Color('gray'), enButtonRect, border_radius=5)
        p.draw.rect(screen, p.Color('darkgray'), enButtonRect.inflate(-4, -4), border_radius=5)
        text_surf = get_unicode_font(24, True).render('EN', True, p.Color('gray'))
        text_rect = text_surf.get_rect(center=enButtonRect.center)
        screen.blit(text_surf, text_rect)
    else:
        p.draw.rect(screen, p.Color('gray'), viButtonRect, border_radius=5)
        p.draw.rect(screen, p.Color('darkgray'), viButtonRect.inflate(-4, -4), border_radius=5)
        text_surf = get_unicode_font(24, True).render('VN', True, p.Color('gray'))
        text_rect = text_surf.get_rect(center=viButtonRect.center)
        screen.blit(text_surf, text_rect)
        drawButtonUnicode(screen, 'EN', enButtonRect)
    
    # Nút quay lại
    backButtonRect = p.Rect(WIDTH // 2 - 100, HEIGHT - 150, 200, 50)
    drawButtonUnicode(screen, get_text('back', lang), backButtonRect)

    p.display.flip()
    
    return soundOnRect, soundOffRect, viButtonRect, enButtonRect, backButtonRect

# Vẽ màn hình Settings trong game (với overlay)
def drawInGameSettings(screen, gs, validMoves, sqSelected):
    # Vẽ game state ở background
    drawGameState(screen, gs, validMoves, sqSelected)
    
    # Vẽ thanh điều khiển
    lang = game_settings['language']
    controlBar = p.Surface((WIDTH, BAR_HEIGHT))
    controlBar.fill(p.Color('gray'))
    screen.blit(controlBar, (0, 0))
    
    # Tạo overlay mờ
    overlay = p.Surface((WIDTH, HEIGHT - BAR_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(p.Color('black'))
    screen.blit(overlay, (0, BAR_HEIGHT))
    
    # Tạo hộp settings
    menuWidth = 450
    menuHeight = 420
    menuX = WIDTH // 2 - menuWidth // 2
    menuY = HEIGHT // 2 - menuHeight // 2 + BAR_HEIGHT // 2
    
    p.draw.rect(screen, p.Color('white'), p.Rect(menuX, menuY, menuWidth, menuHeight), border_radius=10)
    p.draw.rect(screen, p.Color('black'), p.Rect(menuX + 5, menuY + 5, menuWidth - 10, menuHeight - 10), border_radius=10)
    
    # Tiêu đề
    titleFont = get_unicode_font(40, True)
    title = titleFont.render(get_text('settings_title', lang), True, p.Color('white'))
    screen.blit(title, (menuX + menuWidth // 2 - title.get_width() // 2, menuY + 30))
    
    # Âm thanh
    soundLabel = get_unicode_font(26, True)
    soundText = soundLabel.render(get_text('sound', lang) + ':', True, p.Color('white'))
    screen.blit(soundText, (menuX + 60, menuY + 120))
    
    soundOnRect = p.Rect(menuX + menuWidth - 200, menuY + 110, 80, 40)
    soundOffRect = p.Rect(menuX + menuWidth - 110, menuY + 110, 80, 40)
    
    if game_settings['sound_enabled']:
        drawButtonUnicode(screen, get_text('on', lang), soundOnRect)
        p.draw.rect(screen, p.Color('gray'), soundOffRect, border_radius=5)
        p.draw.rect(screen, p.Color('darkgray'), soundOffRect.inflate(-4, -4), border_radius=5)
        text_surf = get_unicode_font(22, True).render(get_text('off', lang), True, p.Color('gray'))
        text_rect = text_surf.get_rect(center=soundOffRect.center)
        screen.blit(text_surf, text_rect)
    else:
        p.draw.rect(screen, p.Color('gray'), soundOnRect, border_radius=5)
        p.draw.rect(screen, p.Color('darkgray'), soundOnRect.inflate(-4, -4), border_radius=5)
        text_surf = get_unicode_font(22, True).render(get_text('on', lang), True, p.Color('gray'))
        text_rect = text_surf.get_rect(center=soundOnRect.center)
        screen.blit(text_surf, text_rect)
        drawButtonUnicode(screen, get_text('off', lang), soundOffRect)
    
    # Ngôn ngữ
    langLabel = get_unicode_font(26, True)
    langText = langLabel.render(get_text('language', lang) + ':', True, p.Color('white'))
    screen.blit(langText, (menuX + 60, menuY + 200))
    
    viButtonRect = p.Rect(menuX + menuWidth - 200, menuY + 190, 80, 40)
    enButtonRect = p.Rect(menuX + menuWidth - 110, menuY + 190, 80, 40)
    
    if game_settings['language'] == 'vi':
        drawButtonUnicode(screen, 'VN', viButtonRect)
        p.draw.rect(screen, p.Color('gray'), enButtonRect, border_radius=5)
        p.draw.rect(screen, p.Color('darkgray'), enButtonRect.inflate(-4, -4), border_radius=5)
        text_surf = get_unicode_font(22, True).render('EN', True, p.Color('gray'))
        text_rect = text_surf.get_rect(center=enButtonRect.center)
        screen.blit(text_surf, text_rect)
    else:
        p.draw.rect(screen, p.Color('gray'), viButtonRect, border_radius=5)
        p.draw.rect(screen, p.Color('darkgray'), viButtonRect.inflate(-4, -4), border_radius=5)
        text_surf = get_unicode_font(22, True).render('VN', True, p.Color('gray'))
        text_rect = text_surf.get_rect(center=viButtonRect.center)
        screen.blit(text_surf, text_rect)
        drawButtonUnicode(screen, 'EN', enButtonRect)
    
    # Nút Resume và Main Menu
    resumeButtonRect = p.Rect(menuX + 60, menuY + 310, 150, 50)
    mainMenuButtonRect = p.Rect(menuX + menuWidth - 210, menuY + 310, 150, 50)
    
    # Nút Resume
    drawButtonUnicode(screen, get_text('back', lang), resumeButtonRect)
    
    # Nút Main Menu (màu đỏ để cảnh báo)
    menuFont = get_unicode_font(22, True)
    p.draw.rect(screen, p.Color('darkred'), mainMenuButtonRect, border_radius=5)
    p.draw.rect(screen, p.Color('red'), mainMenuButtonRect.inflate(-4, -4), border_radius=5)
    menuText = menuFont.render(get_text('exit', lang), True, p.Color('white'))
    menuTextRect = menuText.get_rect(center=mainMenuButtonRect.center)
    screen.blit(menuText, menuTextRect)

    p.display.flip()
    
    return soundOnRect, soundOffRect, viButtonRect, enButtonRect, resumeButtonRect, mainMenuButtonRect

# Vẽ menu lên màn hình
# def drawMenu(screen):
#     background = p.image.load("./assets/backgrounds/back3.png")  # Tải ảnh nền
#     background = p.transform.scale(background, (WIDTH, HEIGHT))  # Thay đổi kích thước ảnh nền
#     screen.blit(background, (0, 0))  # Vẽ ảnh nền lên toàn màn hình
    
#     font = p.font.SysFont("Helvetica", 45, True, False)
#     text_start = font.render("Start", True, p.Color('White'))
#     text_ai = font.render("Two players", True, p.Color('White'))
#     text_exit = font.render("Exit", True, p.Color('White'))
    
#     screen.blit(text_start, (WIDTH // 2 - text_start.get_width() // 2, HEIGHT // 2 - 60))
#     screen.blit(text_ai, (WIDTH // 2 - text_ai.get_width() // 2, HEIGHT // 2))
#     screen.blit(text_exit, (WIDTH // 2 - text_exit.get_width() // 2, HEIGHT // 2 + 60))
#     p.display.flip()

# Vẽ nút trên màn hình
def drawButton(screen, text, rect):
    font = p.font.SysFont("Helvetica", 24, True, False)
    p.draw.rect(screen, p.Color('black'), rect, border_radius=5)
    p.draw.rect(screen, p.Color('white'), rect.inflate(-4, -4), border_radius=5)
    text_surf = font.render(text, True, p.Color('black'))
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

# Vẽ nút với font hỗ trợ Unicode (tiếng Việt)
def drawButtonUnicode(screen, text, rect):
    font = get_unicode_font(22, True)
    
    p.draw.rect(screen, p.Color('black'), rect, border_radius=5)
    p.draw.rect(screen, p.Color('white'), rect.inflate(-4, -4), border_radius=5)
    
    # Render với anti-aliasing để text rõ hơn
    text_surf = font.render(text, True, p.Color('black'))
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

# Lấy tên chế độ chơi theo ngôn ngữ
def get_game_mode_name(mode, language='vi'):
    """Lấy tên chế độ chơi theo ngôn ngữ"""
    if mode == 'very_easy':
        return get_text('mode_very_easy', language)
    elif mode == 'easy':
        return get_text('mode_easy', language)
    elif mode == 'medium':
        return get_text('mode_medium', language)
    elif mode == 'hard':
        return get_text('mode_hard', language)
    elif mode == 'two_players':
        return get_text('mode_two_players', language)
    else:
        return get_text('mode_medium', language)  # Mặc định

# Vẽ button chế độ chơi
def drawGameModeButton(screen, mode, rect):
    """Vẽ button hiển thị chế độ chơi hiện tại"""
    lang = game_settings['language']
    
    # Màu sắc khác nhau cho từng chế độ
    mode_colors = {
        'very_easy': p.Color(100, 200, 100),  # Xanh lá nhạt
        'easy': p.Color(50, 150, 50),         # Xanh lá
        'medium': p.Color(200, 150, 50),       # Cam
        'hard': p.Color(200, 50, 50),          # Đỏ
        'two_players': p.Color(100, 50, 150)   # Tím
    }
    
    color = mode_colors.get(mode, p.Color(100, 100, 100))
    
    # Vẽ background button
    p.draw.rect(screen, p.Color(30, 30, 30), rect, border_radius=8)
    p.draw.rect(screen, color, rect.inflate(-2, -2), border_radius=8)
    
    # Vẽ text
    mode_font = get_unicode_font(16, True)
    mode_text = get_game_mode_name(mode, lang)
    
    # Cắt text nếu quá dài
    if len(mode_text) > 12:
        mode_text = mode_text[:9] + "..."
    
    text_surf = mode_font.render(mode_text, True, p.Color('white'))
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

# Hàm chính để chạy trò chơi
def main():
    load_settings()  # Tải cài đặt
    
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))  # Thiết lập cửa sổ hiển thị
    clock = p.time.Clock()  # Thiết lập đồng hồ trò chơi
    screen.fill(p.Color("white"))  # Đổ màu trắng cho màn hình
    
    gs = ChessEngine.GameState()  # Khởi tạo trạng thái trò chơi
    validMoves = gs.getValidMoves()  # Lấy danh sách các nước đi hợp lệ
    moveMade = False  # Cờ kiểm tra nếu có nước đi được thực hiện
    animate = False  # Cờ kiểm tra nếu cần hiệu ứng
    loadImage()  # Tải hình ảnh của các quân cờ
    
    running = True  # Cờ vòng lặp chính
    sqSelected = ()  # Ô được chọn (ban đầu không có)
    playerClicks = []  # Danh sách lưu trữ các lần nhấp của người chơi
    gameOver = False  # Cờ kiểm tra nếu trò chơi kết thúc
    playerOne = True  # Cờ chỉ người chơi một là người chơi
    playerTwo = False  # Cờ chỉ người chơi hai là người chơi
    showLogin = True  # Cờ hiển thị đăng nhập
    showRegister = False  # Cờ hiển thị đăng ký
    showMenu = False  # Cờ hiển thị menu
    showSettings = False  # Cờ hiển thị settings
    showInGameSettings = False  # Cờ hiển thị settings trong game
    showAIDifficulty = False  # Cờ hiển thị menu chọn độ khó AI
    showStatistics = False  # Cờ hiển thị bảng điểm
    currentGameMode = None  # Chế độ game hiện tại: 'easy', 'medium', 'hard', 'two_players'
    
    # Biến cho input
    emailInput = ""
    passwordInput = ""
    usernameInput = ""
    activeInput = None  # 'email', 'password', 'username'
    authMessage = ""
    authMessageColor = 'red'
    messageTimer = 0  # Timer để tự động ẩn message
    
    # Biến để kiểm soát âm thanh AI
    aiThinkingStartTime = 0  # Thời gian bắt đầu AI suy nghĩ
    aiSoundThrottle = {
        'very_easy': 0,    # Không giới hạn
        'easy': 0,         # Không giới hạn  
        'medium': 100,     # 100ms giữa các âm thanh
        'hard': 200        # 200ms giữa các âm thanh
    }
    lastAISoundTime = 0  # Thời gian âm thanh AI cuối cùng

    resetButtonRect = p.Rect(10, 10, 100, 30)
    undoButtonRect = p.Rect(120, 10, 100, 30)
    menuButtonRect = p.Rect(230, 10, 100, 30)
    modeButtonRect = p.Rect(WIDTH - 150, 10, 140, 30)  # Button chế độ chơi

    while running:
        # Giảm timer cho message
        if messageTimer > 0:
            messageTimer -= 1
            if messageTimer == 0:
                authMessage = ""
        
        if showLogin:
            # Màn hình đăng nhập
            emailBoxRect, passwordBoxRect, loginButtonRect, registerLinkRect = drawLogin(
                screen, emailInput, passwordInput, authMessage, authMessageColor, activeInput
            )
            
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    
                    # Xác định input box nào được click
                    if emailBoxRect.collidepoint(location):
                        activeInput = 'email'
                    elif passwordBoxRect.collidepoint(location):
                        activeInput = 'password'
                    elif loginButtonRect.collidepoint(location):
                        # Xử lý đăng nhập
                        result = login_user(emailInput, passwordInput)
                        if result['success']:
                            authMessage = result['message']
                            authMessageColor = 'green'
                            messageTimer = 60  # Hiển thị 1 giây
                            p.time.wait(1000)  # Đợi 1 giây
                            showLogin = False
                            showMenu = True
                            emailInput = ""
                            passwordInput = ""
                        else:
                            authMessage = result['message']
                            authMessageColor = 'red'
                            messageTimer = 180  # Hiển thị 3 giây
                    elif registerLinkRect.collidepoint(location):
                        showLogin = False
                        showRegister = True
                        authMessage = ""
                        emailInput = ""
                        passwordInput = ""
                    else:
                        activeInput = None
                
                elif e.type == p.KEYDOWN:
                    if activeInput == 'email':
                        if e.key == p.K_BACKSPACE:
                            emailInput = emailInput[:-1]
                        elif e.key == p.K_TAB:
                            activeInput = 'password'
                        elif e.key == p.K_RETURN:
                            activeInput = 'password'
                        else:
                            emailInput += e.unicode
                    elif activeInput == 'password':
                        if e.key == p.K_BACKSPACE:
                            passwordInput = passwordInput[:-1]
                        elif e.key == p.K_TAB:
                            activeInput = 'email'
                        elif e.key == p.K_RETURN:
                            # Xử lý đăng nhập
                            result = login_user(emailInput, passwordInput)
                            if result['success']:
                                authMessage = result['message']
                                authMessageColor = 'green'
                                messageTimer = 60
                                p.time.wait(1000)
                                showLogin = False
                                showMenu = True
                                emailInput = ""
                                passwordInput = ""
                            else:
                                authMessage = result['message']
                                authMessageColor = 'red'
                                messageTimer = 180
                        else:
                            passwordInput += e.unicode
        
        elif showRegister:
            # Màn hình đăng ký (thứ tự: email, password, username)
            emailBoxRect, passwordBoxRect, usernameBoxRect, registerButtonRect, loginLinkRect = drawRegister(
                screen, emailInput, usernameInput, passwordInput, authMessage, authMessageColor, activeInput
            )
            
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    
                    if emailBoxRect.collidepoint(location):
                        activeInput = 'email'
                    elif passwordBoxRect.collidepoint(location):
                        activeInput = 'password'
                    elif usernameBoxRect.collidepoint(location):
                        activeInput = 'username'
                    elif registerButtonRect.collidepoint(location):
                        # Xử lý đăng ký
                        result = register_user(emailInput, passwordInput, usernameInput)
                        if result['success']:
                            authMessage = result['message']
                            authMessageColor = 'green'
                            messageTimer = 60
                            p.time.wait(1000)
                            showRegister = False
                            showMenu = True
                            emailInput = ""
                            passwordInput = ""
                            usernameInput = ""
                        else:
                            authMessage = result['message']
                            authMessageColor = 'red'
                            messageTimer = 180
                    elif loginLinkRect.collidepoint(location):
                        showRegister = False
                        showLogin = True
                        authMessage = ""
                        emailInput = ""
                        passwordInput = ""
                        usernameInput = ""
                    else:
                        activeInput = None
                
                elif e.type == p.KEYDOWN:
                    if activeInput == 'email':
                        if e.key == p.K_BACKSPACE:
                            emailInput = emailInput[:-1]
                        elif e.key == p.K_TAB:
                            activeInput = 'password'
                        elif e.key == p.K_RETURN:
                            activeInput = 'password'
                        else:
                            emailInput += e.unicode
                    elif activeInput == 'password':
                        if e.key == p.K_BACKSPACE:
                            passwordInput = passwordInput[:-1]
                        elif e.key == p.K_TAB:
                            activeInput = 'username'
                        elif e.key == p.K_RETURN:
                            activeInput = 'username'
                        else:
                            passwordInput += e.unicode
                    elif activeInput == 'username':
                        if e.key == p.K_BACKSPACE:
                            usernameInput = usernameInput[:-1]
                        elif e.key == p.K_TAB:
                            activeInput = 'email'
                        elif e.key == p.K_RETURN:
                            # Xử lý đăng ký
                            result = register_user(emailInput, passwordInput, usernameInput)
                            if result['success']:
                                authMessage = result['message']
                                authMessageColor = 'green'
                                messageTimer = 60
                                p.time.wait(1000)
                                showRegister = False
                                showMenu = True
                                emailInput = ""
                                passwordInput = ""
                                usernameInput = ""
                            else:
                                authMessage = result['message']
                                authMessageColor = 'red'
                                messageTimer = 180
                        elif e.unicode and e.unicode.isprintable():
                            # Cho phép nhập tất cả ký tự có thể in (bao gồm tiếng Việt)
                            usernameInput += e.unicode
        
        elif showMenu:
            startButtonRect, aiButtonRect, statsButtonRect, settingsButtonRect, exitButtonRect, logoutButtonRect = drawMenu(screen)
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if startButtonRect.collidepoint(location):
                        # Phát âm thanh
                        if game_settings['sound_enabled']:
                            gs.playClickSound()
                        showMenu = False  # Hiển thị menu chọn độ khó AI
                        showAIDifficulty = True
                    elif aiButtonRect.collidepoint(location):
                        # Phát âm thanh
                        if game_settings['sound_enabled']:
                            gs.playClickSound()
                        showMenu = False  # Chơi 2 người
                        playerTwo = True
                        currentGameMode = 'two_players'
                    elif statsButtonRect.collidepoint(location):
                        # Phát âm thanh
                        if game_settings['sound_enabled']:
                            gs.playClickSound()
                        showStatistics = True  # Mở Bảng điểm
                        showMenu = False
                    elif settingsButtonRect.collidepoint(location):
                        # Phát âm thanh
                        if game_settings['sound_enabled']:
                            gs.playClickSound()
                        showSettings = True  # Mở Settings
                        showMenu = False
                    elif exitButtonRect.collidepoint(location):
                        # Phát âm thanh
                        if game_settings['sound_enabled']:
                            gs.playClickSound()
                        running = False  # Thoát
                    elif logoutButtonRect and logoutButtonRect.collidepoint(location):
                        # Đăng xuất
                        logout_user()
                        showMenu = False
                        showLogin = True
                        authMessage = "logout_success"
                        authMessageColor = 'green'
                        messageTimer = 120
        
        elif showAIDifficulty:
            # Menu chọn độ khó AI
            veryEasyButtonRect, easyButtonRect, mediumButtonRect, hardButtonRect, backButtonRect = drawAIDifficultyMenu(screen)
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if veryEasyButtonRect.collidepoint(location):
                        # Phát âm thanh
                        if game_settings['sound_enabled']:
                            gs.playClickSound()
                        game_settings['ai_difficulty'] = 'very_easy'
                        save_settings()
                        showAIDifficulty = False
                        playerTwo = False  # Chơi với AI
                        currentGameMode = 'very_easy'
                    elif easyButtonRect.collidepoint(location):
                        # Phát âm thanh
                        if game_settings['sound_enabled']:
                            gs.playClickSound()
                        game_settings['ai_difficulty'] = 'easy'
                        save_settings()
                        showAIDifficulty = False
                        playerTwo = False  # Chơi với AI
                        currentGameMode = 'easy'
                    elif mediumButtonRect.collidepoint(location):
                        # Phát âm thanh
                        if game_settings['sound_enabled']:
                            gs.playClickSound()
                        game_settings['ai_difficulty'] = 'medium'
                        save_settings()
                        showAIDifficulty = False
                        playerTwo = False  # Chơi với AI
                        currentGameMode = 'medium'
                    elif hardButtonRect.collidepoint(location):
                        # Phát âm thanh
                        if game_settings['sound_enabled']:
                            gs.playClickSound()
                        game_settings['ai_difficulty'] = 'hard'
                        save_settings()
                        showAIDifficulty = False
                        playerTwo = False  # Chơi với AI
                        currentGameMode = 'hard'
                    elif backButtonRect.collidepoint(location):
                        # Phát âm thanh
                        if game_settings['sound_enabled']:
                            gs.playClickSound()
                        showAIDifficulty = False
                        showMenu = True
        
        elif showStatistics:
            # Menu bảng điểm
            resetStatsButtonRect, backButtonRect = drawStatistics(screen)
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if resetStatsButtonRect.collidepoint(location):
                        # Reset statistics
                        from statistics import reset_statistics
                        reset_statistics()
                    elif backButtonRect.collidepoint(location):
                        showStatistics = False
                        showMenu = True
        
        elif showSettings:
            soundOnRect, soundOffRect, viButtonRect, enButtonRect, backButtonRect = drawSettings(screen)
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if soundOnRect.collidepoint(location):
                        game_settings['sound_enabled'] = True
                        save_settings()
                    elif soundOffRect.collidepoint(location):
                        game_settings['sound_enabled'] = False
                        save_settings()
                    elif viButtonRect.collidepoint(location):
                        game_settings['language'] = 'vi'
                        save_settings()
                    elif enButtonRect.collidepoint(location):
                        game_settings['language'] = 'en'
                        save_settings()
                    elif backButtonRect.collidepoint(location):
                        showSettings = False
                        showMenu = True
        
        elif showInGameSettings:
            # Hiển thị Settings trong game
            soundOnRect, soundOffRect, viButtonRect, enButtonRect, resumeButtonRect, mainMenuButtonRect = drawInGameSettings(screen, gs, validMoves, sqSelected)
            for e in p.event.get():
                if e.type == p.QUIT:
                    running = False
                elif e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos()
                    if soundOnRect.collidepoint(location):
                        game_settings['sound_enabled'] = True
                        save_settings()
                    elif soundOffRect.collidepoint(location):
                        game_settings['sound_enabled'] = False
                        save_settings()
                    elif viButtonRect.collidepoint(location):
                        game_settings['language'] = 'vi'
                        save_settings()
                    elif enButtonRect.collidepoint(location):
                        game_settings['language'] = 'en'
                        save_settings()
                    elif resumeButtonRect.collidepoint(location):
                        showInGameSettings = False  # Quay lại game
                    elif mainMenuButtonRect.collidepoint(location):
                        # Quay về menu chính (reset game)
                        gs = ChessEngine.GameState()
                        validMoves = gs.getValidMoves()
                        sqSelected = ()
                        playerClicks = []
                        moveMade = False
                        animate = False
                        gameOver = False
                        showInGameSettings = False
                        showMenu = True
                        playerTwo = False
                        currentGameMode = None
        
        else:
            humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
            
            # Vòng lặp xử lý sự kiện
            for e in p.event.get():
                if e.type == p.QUIT:  # Nếu người dùng thoát trò chơi
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    showMenu = True
                    playerTwo = False
                    currentGameMode = None
                
                elif e.type == p.MOUSEBUTTONDOWN:  # Nếu nút chuột được nhấn
                    location = p.mouse.get_pos()

                    if resetButtonRect.collidepoint(location):
                        # Phát âm thanh
                        if game_settings['sound_enabled']:
                            gs.playClickSound()
                        gs = ChessEngine.GameState()
                        validMoves = gs.getValidMoves()
                        sqSelected = ()
                        playerClicks = []
                        moveMade = False
                        animate = False
                        gameOver = False

                    elif undoButtonRect.collidepoint(location):
                        # Phát âm âm thanh
                        if game_settings['sound_enabled']:
                            gs.playClickSound()
                        
                        # Logic hoàn tác nước kép trong chế độ AI
                        if not gameOver and currentGameMode in ['very_easy', 'easy', 'medium', 'hard']:
                            # Hoàn tác nước kép: cả AI và người chơi
                            moves_to_undo = 0
                            
                            # Đếm số nước đi cần hoàn tác
                            if len(gs.moveLog) > 0:
                                moves_to_undo = 1  # Ít nhất 1 nước
                                
                                # Nếu có 2 nước trở lên và đang là lượt người chơi, hoàn tác cả 2
                                if len(gs.moveLog) >= 2 and humanTurn:
                                    moves_to_undo = 2
                            
                            # Thực hiện hoàn tác
                            for _ in range(moves_to_undo):
                                if len(gs.moveLog) > 0:
                                    gs.undoMove()
                            
                            moveMade = True
                            animate = False
                        else:
                            # Chế độ hai người hoặc không có AI - hoàn tác bình thường
                            if len(gs.moveLog) > 0:
                                gs.undoMove()
                                moveMade = True
                                animate = False
                    
                    elif menuButtonRect.collidepoint(location):
                        # Phát âm thanh
                        if game_settings['sound_enabled']:
                            gs.playClickSound()
                        showInGameSettings = True  # Mở Settings trong game

                    elif not gameOver and humanTurn:
                        col = location[0] // SQ_SIZE  # Tính cột dựa trên vị trí chuột
                        row = (location[1] - BAR_HEIGHT) // SQ_SIZE  # Tính hàng dựa trên vị trí chuột
                        # Kiểm tra xem click có nằm trong bàn cờ không
                        if 0 <= row < DIMENTION and 0 <= col < DIMENTION:
                            if sqSelected == (row, col):  # Nếu cùng một ô được nhấp lại
                                sqSelected = ()  # Bỏ chọn ô
                                playerClicks = []  # Xóa các lần nhấp của người chơi
                            else:
                                sqSelected = (row, col)  # Chọn ô mới
                                playerClicks.append(sqSelected)  # Thêm ô được chọn vào danh sách nhấp
                            
                            if len(playerClicks) == 2:  # Nếu hai ô được chọn
                                move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)  # Tạo một nước đi
                                print(move.getChessNotation())  # In nước đi theo ký hiệu cờ vua
                                for i in range(len(validMoves)):
                                    if move == validMoves[i]:
                                        # Kiểm tra xem có phải là nước đi phong cấp tốt không
                                        if validMoves[i].isPawnPromotion:
                                            # Hiển thị menu chọn quân cờ
                                            drawGameState(screen, gs, validMoves, sqSelected)
                                            promotionRects, promotionPieces = drawPromotionMenu(screen, validMoves[i].pieceMoved[0])
                                            
                                            # Đợi người chơi chọn
                                            waitingForPromotion = True
                                            selectedPiece = 'Q'  # Mặc định là Hậu
                                            while waitingForPromotion:
                                                for event in p.event.get():
                                                    if event.type == p.QUIT:
                                                        waitingForPromotion = False
                                                        running = False
                                                    elif event.type == p.MOUSEBUTTONDOWN:
                                                        mousePos = p.mouse.get_pos()
                                                        for idx, rect in enumerate(promotionRects):
                                                            if rect.collidepoint(mousePos):
                                                                selectedPiece = promotionPieces[idx]
                                                                waitingForPromotion = False
                                                                break
                                            
                                            # Lưu lựa chọn vào move
                                            validMoves[i].promotionChoice = selectedPiece
                                        
                                        # Cập nhật pieceMoved để phản ánh quân cờ được phong cấp
                                        if validMoves[i].isPawnPromotion:
                                            # Lưu quân cờ gốc trước khi phong cấp
                                            validMoves[i].originalPiece = validMoves[i].pieceMoved
                                            # Tạo tên quân cờ mới dựa trên màu và lựa chọn
                                            color = validMoves[i].pieceMoved[0]  # 'w' hoặc 'b'
                                            validMoves[i].pieceMoved = color + selectedPiece
                                        
                                        gs.makeMove(validMoves[i], False)  # Thực hiện nước đi
                                        moveMade = True  # Đặt cờ moveMade thành True
                                        animate = True  # Đặt cờ animate thành True
                                        sqSelected = ()  # Bỏ chọn các ô
                                        playerClicks = []  # Xóa các lần nhấp của người chơi
                                if not moveMade:
                                    playerClicks = [sqSelected]  # Đặt lại danh sách nhấp của người chơi về lựa chọn hiện tại
                
                elif e.type == p.KEYDOWN:  # Nếu một phím được nhấn
                    if e.key == p.K_z:  # Nếu phím 'z' được nhấn, hoàn tác nước đi
                        gs.undoMove()
                        moveMade = True
                        animate = False
                    if e.key == p.K_r:  # Nếu phím 'r' được nhấn, thiết lập lại trò chơi
                        gs = ChessEngine.GameState()
                        validMoves = gs.getValidMoves()
                        sqSelected = ()
                        playerClicks = []
                        moveMade = False
                        animate = False

            # AI tìm nước đi theo độ khó đã chọn
            if not gameOver and not humanTurn:
                difficulty = game_settings.get('ai_difficulty', 'medium')
                
                # Ghi nhận thời gian bắt đầu AI suy nghĩ
                currentTime = p.time.get_ticks()
                if aiThinkingStartTime == 0:
                    aiThinkingStartTime = currentTime
                
                # Hiển thị indicator AI đang suy nghĩ cho mức độ khó
                if currentGameMode in ['hard']:
                    thinkingTime = currentTime - aiThinkingStartTime
                    if thinkingTime > 500:  # Sau 0.5 giây mới hiển thị
                        # Vẽ indicator AI đang suy nghĩ
                        indicatorRect = p.Rect(WIDTH - 200, HEIGHT - 50, 180, 30)
                        p.draw.rect(screen, p.Color(50, 50, 50, 150), indicatorRect, border_radius=5)
                        thinkingFont = get_unicode_font(16, True)
                        thinkingText = thinkingFont.render("AI đang suy nghĩ...", True, p.Color('white'))
                        screen.blit(thinkingText, (indicatorRect.x + 10, indicatorRect.y + 5))
                
                # Sử dụng hàm mới để lấy AI theo mức độ
                AIMove = SmartMove.getAIMoveByLevel(gs, validMoves, difficulty)
                
                # Fallback nếu không tìm được nước đi
                if AIMove == None:
                    AIMove = SmartMove.findRandomMove(validMoves)
                
                # Nếu AI phong cấp tốt, mặc định chọn Hậu
                if AIMove.isPawnPromotion:
                    AIMove.promotionChoice = 'Q'
                    # Lưu quân cờ gốc trước khi phong cấp
                    AIMove.originalPiece = AIMove.pieceMoved
                    # Cập nhật pieceMoved để phản ánh quân cờ được phong cấp
                    color = AIMove.pieceMoved[0]  # 'w' hoặc 'b'
                    AIMove.pieceMoved = color + 'Q'
                
                gs.makeMove(AIMove, False)
                moveMade = True
                animate = True
                
                # Reset thời gian AI suy nghĩ
                aiThinkingStartTime = 0

            if moveMade:
                if animate:
                    animaMove(gs.moveLog[-1], screen, gs.board, clock)  # Hiệu ứng nước đi
                
                # Phát âm thanh nếu được bật với throttling và âm lượng cho AI
                if game_settings['sound_enabled'] and len(gs.moveLog) > 0:
                    lastMove = gs.moveLog[-1]
                    currentTime = p.time.get_ticks()
                    
                    # Kiểm tra throttling cho AI
                    shouldPlaySound = True
                    if currentGameMode in ['medium', 'hard']:
                        throttleTime = aiSoundThrottle.get(currentGameMode, 0)
                        if currentTime - lastAISoundTime < throttleTime:
                            shouldPlaySound = False
                    
                    if shouldPlaySound:
                        # Điều chỉnh âm lượng theo mức độ AI
                        volume = 1.0
                        if currentGameMode == 'medium':
                            volume = 0.8
                        elif currentGameMode == 'hard':
                            volume = 0.6
                        
                        if lastMove.pieceCaptured != '--':
                            gs.playCaptureSoundWithVolume(volume)
                        else:
                            gs.playMoveSoundWithVolume(volume)
                        
                        # Cập nhật thời gian âm thanh cuối cùng
                        if currentGameMode in ['medium', 'hard']:
                            lastAISoundTime = currentTime
                
                validMoves = gs.getValidMoves()  # Lấy danh sách mới của các nước đi hợp lệ
                moveMade = False
                animate = False

            drawGameState(screen, gs, validMoves, sqSelected)  # Vẽ trạng thái trò chơi

            lang = game_settings['language']
            
            if gs.checkmate:  # Kiểm tra chiếu hết
                if not gameOver:  # Chỉ ghi kết quả lần đầu
                    gameOver = True
                    # Ghi kết quả vào thống kê
                    if currentGameMode in ['very_easy', 'easy', 'medium', 'hard']:
                        if gs.whiteToMove:  # Đen thắng (AI thắng)
                            record_game_result(currentGameMode, 'loss')
                            # Cập nhật Firebase nếu có user đăng nhập
                            if get_current_user():
                                update_user_scores(currentGameMode, 'loss')
                        else:  # Trắng thắng (Player thắng)
                            record_game_result(currentGameMode, 'win')
                            # Cập nhật Firebase nếu có user đăng nhập
                            if get_current_user():
                                update_user_scores(currentGameMode, 'win')
                    elif currentGameMode == 'two_players':
                        if gs.whiteToMove:
                            record_game_result('two_players', 'black_wins')
                        else:
                            record_game_result('two_players', 'white_wins')
                
                if gs.whiteToMove:
                    drawText(screen, get_text('checkmate_black', lang))  # Hiển thị thông báo nếu đen thắng
                else:
                    drawText(screen, get_text('checkmate_white', lang))  # Hiển thị thông báo nếu trắng thắng
            elif gs.stalemate:  # Kiểm tra hòa
                if not gameOver:  # Chỉ ghi kết quả lần đầu
                    gameOver = True
                    # Ghi kết quả hòa
                    if currentGameMode:
                        record_game_result(currentGameMode, 'draw')
                        # Cập nhật Firebase nếu có user đăng nhập và chế độ AI
                        if get_current_user() and currentGameMode in ['very_easy', 'easy', 'medium', 'hard']:
                            update_user_scores(currentGameMode, 'draw')
                
                drawText(screen, get_text('stalemate', lang))  # Hiển thị thông báo hòa

            # Tạo thanh điều khiển
            controlBar = p.Surface((WIDTH, BAR_HEIGHT))
            controlBar.fill(p.Color('gray'))
            drawButtonUnicode(controlBar, get_text('reset', lang), resetButtonRect)
            drawButtonUnicode(controlBar, get_text('undo', lang), undoButtonRect)
            drawButtonUnicode(controlBar, get_text('settings_btn', lang), menuButtonRect)

            # Vẽ các nút lên thanh điều khiển
            screen.blit(controlBar, (0, 0))
            
            # Vẽ button chế độ chơi ở góc phải (chỉ khi đang chơi)
            if currentGameMode:
                drawGameModeButton(screen, currentGameMode, modeButtonRect)

            clock.tick(MAX_FPS)  # Điều khiển tốc độ khung hình
            p.display.flip()  # Cập nhật màn hình

# Làm nổi bật ô được chọn và các nước đi có thể cho quân cờ được chọn
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):  # Kiểm tra nếu ô được chọn là quân cờ
            # Làm nổi bật ô được chọn
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  # Thiết lập độ trong suốt
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE + BAR_HEIGHT))
            # Làm nổi bật các nước đi từ ô được chọn
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE + BAR_HEIGHT))

# Vẽ trạng thái hiện tại của trò chơi
def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  # Vẽ bàn cờ
    highlightSquares(screen, gs, validMoves, sqSelected)  # Làm nổi bật các ô
    drawPieces(screen, gs.board)  # Vẽ các quân cờ trên bàn cờ

# Vẽ bàn cờ
def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]  # Định nghĩa màu của bàn cờ
    for r in range(DIMENTION):
        for c in range(DIMENTION):
            color = colors[(r + c) % 2]  # Thay đổi màu
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE + BAR_HEIGHT, SQ_SIZE, SQ_SIZE))  # Vẽ ô vuông

# Vẽ các quân cờ trên bàn cờ
def drawPieces(screen, board):
    for r in range(DIMENTION):
        for c in range(DIMENTION):
            piece = board[r][c]
            if piece != "--":  # Nếu có quân cờ trên ô
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE + BAR_HEIGHT, SQ_SIZE, SQ_SIZE))  # Vẽ quân cờ

# Hiệu ứng nước đi
def animaMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow  # Hàng đích
    dC = move.endCol - move.startCol  # Cột đích
    framesPerSquare = 10  # Số khung hình trên mỗi ô vuông
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare  # Tổng số khung hình
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount)
        drawBoard(screen)  # Vẽ bàn cờ
        drawPieces(screen, board)  # Vẽ các quân cờ
        # Xóa ô đích
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE + BAR_HEIGHT, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # Vẽ quân cờ bị ăn lên ô đích (nếu có)
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # Vẽ quân cờ đang di chuyển
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE + BAR_HEIGHT, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)  # Điều chỉnh tốc độ khung hình

# Vẽ văn bản lên màn hình (ví dụ: thông báo kết thúc trò chơi)
def drawText(screen, text):
    font = get_unicode_font(50, True)  # Định nghĩa phông chữ
    textObject = font.render(text, True, p.Color('White'))  # Tạo văn bản
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2, HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)  # Hiển thị văn bản lên màn hình
    textObject = font.render(text, True, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))  # Hiển thị văn bản với bóng đổ

# Hiển thị menu chọn quân cờ khi phong cấp tốt
def drawPromotionMenu(screen, color):
    # Tạo overlay mờ
    overlay = p.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(p.Color('black'))
    screen.blit(overlay, (0, 0))
    
    # Tạo hộp menu
    menuWidth = 400
    menuHeight = 220
    menuX = WIDTH // 2 - menuWidth // 2
    menuY = HEIGHT // 2 - menuHeight // 2
    
    p.draw.rect(screen, p.Color('white'), p.Rect(menuX, menuY, menuWidth, menuHeight), border_radius=10)
    p.draw.rect(screen, p.Color('black'), p.Rect(menuX + 5, menuY + 5, menuWidth - 10, menuHeight - 10), border_radius=10)
    
    # Tiêu đề
    lang = game_settings['language']
    font = get_unicode_font(24, True)
    title = font.render(get_text('promotion_title', lang), True, p.Color('white'))
    screen.blit(title, (menuX + menuWidth // 2 - title.get_width() // 2, menuY + 20))
    
    # Vẽ 4 quân cờ để chọn
    pieces = ['Q', 'R', 'B', 'N']  # Hậu, Xe, Tượng, Mã
    pieceNames = [get_text('queen', lang), get_text('rook', lang), get_text('bishop', lang), get_text('knight', lang)]
    pieceSize = 80
    spacing = (menuWidth - 4 * pieceSize) // 5
    
    rects = []
    labelFont = get_unicode_font(16, True)
    for i, piece in enumerate(pieces):
        x = menuX + spacing + i * (pieceSize + spacing)
        y = menuY + 80
        
        # Vẽ ô nền cho quân cờ
        rect = p.Rect(x, y, pieceSize, pieceSize)
        p.draw.rect(screen, p.Color('lightgray'), rect, border_radius=5)
        p.draw.rect(screen, p.Color('white'), rect.inflate(-4, -4), border_radius=5)
        
        # Vẽ quân cờ
        pieceKey = color + piece
        if pieceKey in IMAGES:
            pieceImg = p.transform.scale(IMAGES[pieceKey], (pieceSize - 10, pieceSize - 10))
            screen.blit(pieceImg, (x + 5, y + 5))
        
        # Vẽ tên quân cờ bên dưới
        label = labelFont.render(pieceNames[i], True, p.Color('white'))
        screen.blit(label, (x + pieceSize // 2 - label.get_width() // 2, y + pieceSize + 5))
        
        rects.append(rect)
    
    p.display.flip()
    return rects, pieces

# Chạy hàm main nếu đây là script được thực thi
if __name__ == "__main__":
    main()
