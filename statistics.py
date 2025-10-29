# Hệ thống thống kê trận đấu
import json
import os

STATS_FILE = 'firebase/statistics.json'

DEFAULT_STATS = {
    'vs_ai_easy': {
        'total': 0,
        'wins': 0,
        'losses': 0,
        'draws': 0
    },
    'vs_ai_medium': {
        'total': 0,
        'wins': 0,
        'losses': 0,
        'draws': 0
    },
    'vs_ai_hard': {
        'total': 0,
        'wins': 0,
        'losses': 0,
        'draws': 0
    },
    'two_players': {
        'total': 0,
        'white_wins': 0,
        'black_wins': 0,
        'draws': 0
    }
}

def load_statistics():
    """Tải thống kê từ file"""
    try:
        if os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return DEFAULT_STATS.copy()
    except:
        return DEFAULT_STATS.copy()

def save_statistics(stats):
    """Lưu thống kê vào file"""
    try:
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
    except:
        pass

def record_game_result(mode, result, player_color='white'):
    """
    Ghi lại kết quả trận đấu
    
    Args:
        mode: 'easy', 'medium', 'hard', 'two_players'
        result: 'win', 'loss', 'draw'
        player_color: 'white' hoặc 'black' (chỉ dùng cho two_players)
    """
    stats = load_statistics()
    
    if mode in ['easy', 'medium', 'hard']:
        key = f'vs_ai_{mode}'
        if key in stats:
            stats[key]['total'] += 1
            if result == 'win':
                stats[key]['wins'] += 1
            elif result == 'loss':
                stats[key]['losses'] += 1
            elif result == 'draw':
                stats[key]['draws'] += 1
    
    elif mode == 'two_players':
        if 'two_players' in stats:
            stats['two_players']['total'] += 1
            if result == 'white_wins':
                stats['two_players']['white_wins'] += 1
            elif result == 'black_wins':
                stats['two_players']['black_wins'] += 1
            elif result == 'draw':
                stats['two_players']['draws'] += 1
    
    save_statistics(stats)

def get_win_rate(wins, total):
    """Tính tỉ lệ thắng"""
    if total == 0:
        return 0.0
    return (wins / total) * 100

def get_statistics_summary():
    """Lấy tóm tắt thống kê"""
    stats = load_statistics()
    
    summary = {
        'total_games': 0,
        'total_wins': 0,
        'total_losses': 0,
        'total_draws': 0,
        'modes': {}
    }
    
    # Thống kê vs AI
    for difficulty in ['easy', 'medium', 'hard']:
        key = f'vs_ai_{difficulty}'
        if key in stats:
            mode_stats = stats[key]
            summary['total_games'] += mode_stats['total']
            summary['total_wins'] += mode_stats['wins']
            summary['total_losses'] += mode_stats['losses']
            summary['total_draws'] += mode_stats['draws']
            
            summary['modes'][difficulty] = {
                'total': mode_stats['total'],
                'wins': mode_stats['wins'],
                'losses': mode_stats['losses'],
                'draws': mode_stats['draws'],
                'win_rate': get_win_rate(mode_stats['wins'], mode_stats['total'])
            }
    
    # Thống kê 2 người chơi
    if 'two_players' in stats:
        tp = stats['two_players']
        summary['total_games'] += tp['total']
        summary['modes']['two_players'] = {
            'total': tp['total'],
            'white_wins': tp['white_wins'],
            'black_wins': tp['black_wins'],
            'draws': tp['draws']
        }
    
    return summary

def reset_statistics():
    """Reset tất cả thống kê"""
    save_statistics(DEFAULT_STATS.copy())


