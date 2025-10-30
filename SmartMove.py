import random
import time

# Điểm cho từng quân cờ theo chuẩn quốc tế
pieceScore = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}

# Điểm thưởng vị trí cho từng quân (chuẩn quốc tế)
knightScores = [
    [-5, -4, -3, -3, -3, -3, -4, -5],
    [-4, -2,  0,  0,  0,  0, -2, -4],
    [-3,  0,  1,  1.5,1.5, 1,  0, -3],
    [-3,  0.5,1.5, 2, 2,1.5,0.5,-3],
    [-3,  0,  1.5, 2, 2,1.5, 0, -3],
    [-3,  0.5, 1,  1.5,1.5, 1,0.5,-3],
    [-4, -2,  0,  0.5,0.5, 0, -2, -4],
    [-5, -4, -3, -3, -3, -3, -4, -5]
]

bishopScores = [
    [-2, -1, -1, -1, -1, -1, -1, -2],
    [-1,  0,  0,  0,  0,  0,  0, -1],
    [-1,  0,  0.5, 1, 1,  0.5, 0, -1],
    [-1,  0.5, 0.5, 1, 1,  0.5,0.5,-1],
    [-1,  0,  1,  1,  1,  1,  0, -1],
    [-1,  1,  1,  1,  1,  1,  1, -1],
    [-1,  0.5, 0,  0,  0,  0, 0.5,-1],
    [-2, -1, -1, -1, -1, -1, -1, -2]
]

rookScores = [
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 0.5, 1, 1, 1, 1, 1, 1, 0.5],
    [-0.5, 0, 0, 0, 0, 0, 0,-0.5],
    [-0.5, 0, 0, 0, 0, 0, 0,-0.5],
    [-0.5, 0, 0, 0, 0, 0, 0,-0.5],
    [-0.5, 0, 0, 0, 0, 0, 0,-0.5],
    [-0.5, 0, 0, 0, 0, 0, 0,-0.5],
    [ 0,  0, 0, 0.5,0.5, 0, 0, 0]
]

queenScores = [
    [-2, -1, -1,-0.5,-0.5, -1, -1, -2],
    [-1,  0,  0,  0,  0,  0,  0, -1],
    [-1,  0,  0.5,0.5,0.5,0.5, 0, -1],
    [-0.5, 0, 0.5,0.5,0.5,0.5, 0,-0.5],
    [ 0,  0,  0.5,0.5,0.5,0.5, 0,-0.5],
    [-1,  0.5, 0.5,0.5,0.5,0.5, 0, -1],
    [-1,  0,  0.5, 0,  0,  0,  0, -1],
    [-2, -1, -1,-0.5,-0.5, -1, -1, -2]
]

pawnScores = [
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 5,  5,  5,  5,  5,  5,  5,  5],
    [ 1,  1,  2,  3,  3,  2,  1,  1],
    [0.5,0.5, 1, 2.5,2.5, 1, 0.5,0.5],
    [ 0,  0,  0,  2,  2,  0,  0,  0],
    [0.5,-0.5,-1, 0,  0, -1,-0.5,0.5],
    [0.5, 1,  1, -2, -2,  1,  1, 0.5],
    [ 0,  0,  0,  0,  0,  0,  0,  0]
]

piecePositionScores = {
    "N": knightScores,
    "B": bishopScores, 
    "R": rookScores,
    "Q": queenScores,
    "p": pawnScores
}

CHECKMATE = 1000
STALEMATE = 0

# =============== CÁC HÀM TIỆN ÍCH ===============

def findRandomMove(validMoves):
    """AI Rất Dễ: Chọn nước đi ngẫu nhiên"""
    return validMoves[random.randint(0, len(validMoves) - 1)]

def scoreBoard(gs):
    """Đánh giá điểm bàn cờ theo vật liệu và vị trí"""
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stalemate:
        return STALEMATE
    
    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                # Điểm vật liệu
                piecePositionScore = 0
                if square[1] != "K":
                    if square[1] in piecePositionScores:
                        if square[0] == 'w':
                            piecePositionScore = piecePositionScores[square[1]][row][col]
                        else:
                            piecePositionScore = piecePositionScores[square[1]][7-row][col]
                
                if square[0] == 'w':
                    score += pieceScore[square[1]] + piecePositionScore * 0.1
                elif square[0] == 'b':
                    score -= pieceScore[square[1]] + piecePositionScore * 0.1
    return score

# =============== AI RẤT DỄ (Random với heuristic cơ bản) ===============

def findVeryEasyMove(gs, validMoves):
    """
    AI Rất Dễ - Mức 1:
    - 90% nước đi ngẫu nhiên
    - 10% nước đi tốt (ăn quân địch)
    """
    if random.random() < 0.9:  # 90% random
        return findRandomMove(validMoves)
    
    # 10% chọn nước đi ăn quân địch
    captureMoves = [move for move in validMoves if move.pieceCaptured != '--']
    if captureMoves:
        return random.choice(captureMoves)
    
    return findRandomMove(validMoves)

# =============== AI DỄ (Random với heuristic tốt hơn) ===============

def findEasyMove(gs, validMoves):
    """
    AI Dễ - Mức 2:
    - 70% nước đi ngẫu nhiên
    - 30% nước đi tốt (ăn quân, tránh mất quân)
    """
    if random.random() < 0.7:  # 70% random
        return findRandomMove(validMoves)
    
    # 30% chọn nước đi có điểm cao
    random.shuffle(validMoves)
    bestMove = validMoves[0]
    maxScore = -CHECKMATE
    
    for move in validMoves:
        gs.makeMove(move, True)
        score = -scoreBoard(gs)
        gs.undoMove()
        
        if score > maxScore:
            maxScore = score
            bestMove = move
    
    return bestMove

# =============== AI TRUNG BÌNH (Minimax depth 2) ===============

def findMediumMove(gs, validMoves):
    """
    AI Trung Bình - Mức 3:
    - Sử dụng Minimax với Alpha-Beta pruning
    - Độ sâu: 2
    - Đánh giá vật liệu và vị trí cơ bản
    """
    return findBestMoveWithDepth(gs, validMoves, 2)

# =============== AI KHÓ (Minimax depth 3) ===============

def findHardMove(gs, validMoves):
    """
    AI Khó - Mức 4:
    - Sử dụng Minimax với Alpha-Beta pruning
    - Độ sâu: 3
    - Đánh giá vật liệu, vị trí, và chiến thuật
    """
    return findBestMoveWithDepth(gs, validMoves, 3)


# =============== HÀM MINIMAX VỚI ALPHA-BETA PRUNING ===============

def findBestMoveWithDepth(gs, validMoves, depth):
    """Tìm nước đi tốt nhất với độ sâu tùy chỉnh"""
    random.shuffle(validMoves)
    maxScore = -CHECKMATE
    bestMove = None
    
    for move in validMoves:
        tempGs = gs.clone()
        tempGs.makeMove(move, True)
        nextMoves = tempGs.getValidMoves()
        score = -negaMaxAlphaBeta(tempGs, nextMoves, depth - 1, -CHECKMATE, CHECKMATE, 
                                   1 if tempGs.whiteToMove else -1)
        if score > maxScore:
            maxScore = score
            bestMove = move
    
    return bestMove


def negaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    """Thuật toán NegaMax với Alpha-Beta Pruning"""
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move, True)
        nextMoves = gs.getValidMoves()
        score = -negaMaxAlphaBeta(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        maxScore = max(maxScore, score)
        alpha = max(alpha, score)
        gs.undoMove()
        
        if alpha >= beta:
            break
    
    return maxScore


# =============== HÀM TƯƠNG THÍCH CŨ ===============

def findBestMove(gs, validMoves):
    """Hàm cũ để tương thích - mặc định dùng AI Trung Bình"""
    return findMediumMove(gs, validMoves)

# =============== HÀM LẤY AI THEO MỨC ĐỘ ===============

def getAIMoveByLevel(gs, validMoves, level):
    """
    Lấy nước đi AI theo mức độ
    
    Args:
        gs: GameState
        validMoves: Danh sách nước đi hợp lệ
        level: 'very_easy', 'easy', 'medium', 'hard'
    
    Returns:
        Move: Nước đi được chọn
    """
    if level == 'very_easy':
        return findVeryEasyMove(gs, validMoves)
    elif level == 'easy':
        return findEasyMove(gs, validMoves)
    elif level == 'medium':
        return findMediumMove(gs, validMoves)
    elif level == 'hard':
        return findHardMove(gs, validMoves)
    else:
        # Mặc định là medium
        return findMediumMove(gs, validMoves)
