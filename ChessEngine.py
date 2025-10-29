import pygame as p

class GameState:
    def __init__(self):
        # Bàn cờ 8x8, "--" là ô trống
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.whiteToMove = True
        self.moveLog = []
        self.checkmate = False
        self.stalemate = False
        
        # Âm thanh
        try:
            self.move_sound = p.mixer.Sound("./assets/sounds/move.wav")
            self.capture_sound = p.mixer.Sound("./assets/sounds/capture.wav")
            self.click_sound = p.mixer.Sound("./assets/sounds/move.wav")  # Dùng âm di chuyển cho click
        except:
            self.move_sound = None
            self.capture_sound = None
            self.click_sound = None

    def makeMove(self, move, sound=True):
        """Thực hiện nước đi"""
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        
        # Phát âm thanh
        if sound and self.move_sound and self.capture_sound:
            if move.pieceCaptured != "--":
                self.capture_sound.play()
            else:
                self.move_sound.play()
    
    def playClickSound(self):
        """Phát âm thanh khi click button"""
        if self.click_sound:
            self.click_sound.play()

    def undoMove(self):
        """Hoàn tác nước đi cuối"""
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            # Nếu là nước đi phong cấp, đặt lại quân cờ gốc (tốt)
            if move.isPawnPromotion:
                self.board[move.startRow][move.startCol] = move.originalPiece
            else:
                self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # Reset trạng thái checkmate và stalemate
            self.checkmate = False
            self.stalemate = False
    
    def clone(self):
        """Tạo bản sao của game state"""
        import copy
        newGs = GameState()
        newGs.board = copy.deepcopy(self.board)
        newGs.whiteToMove = self.whiteToMove
        newGs.moveLog = copy.deepcopy(self.moveLog)
        newGs.checkmate = self.checkmate
        newGs.stalemate = self.stalemate
        return newGs

    def getValidMoves(self):
        """Lấy danh sách nước đi hợp lệ"""
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == 'p':
                        self.getPawnMoves(r, c, moves)
                    elif piece == 'R':
                        self.getRookMoves(r, c, moves)
                    elif piece == 'N':
                        self.getKnightMoves(r, c, moves)
                    elif piece == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif piece == 'Q':
                        self.getQueenMoves(r, c, moves)
                    elif piece == 'K':
                        self.getKingMoves(r, c, moves)
        
        # Lọc bỏ các nước đi đặt vua vào thế chiếu
        validMoves = []
        for move in moves:
            if not self.inCheck(move):
                validMoves.append(move)
        
        # Kiểm tra checkmate và stalemate
        if len(validMoves) == 0:
            if self.isUnderAttack():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        
        return validMoves

    def inCheck(self, move):
        """Kiểm tra xem nước đi có đặt vua vào thế chiếu hay không"""
        # Lưu trạng thái hiện tại
        tempBoard = [row[:] for row in self.board]
        tempWhiteToMove = self.whiteToMove
        
        # Thực hiện nước đi tạm thời
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        # KHÔNG thay đổi lượt chơi vì chúng ta đang kiểm tra vua của bên hiện tại
        
        # Kiểm tra xem vua có bị chiếu không
        inCheck = self.isUnderAttack()
        
        # Khôi phục trạng thái
        self.board = tempBoard
        self.whiteToMove = tempWhiteToMove
        
        return inCheck

    def isUnderAttack(self):
        """Kiểm tra xem vua hiện tại có bị tấn công hay không"""
        # Tìm vị trí vua
        kingRow, kingCol = self.findKing()
        if kingRow == -1:
            return False
        
        # Kiểm tra tất cả quân địch có thể tấn công vua không
        enemyColor = "b" if self.whiteToMove else "w"
        
        # Kiểm tra tốt
        if self.whiteToMove:
            # Vua trắng - kiểm tra tốt đen tấn công từ phía trên (row nhỏ hơn)
            # Tốt đen ở row nhỏ hơn có thể tấn công vua trắng
            if kingRow > 0:
                if kingCol > 0 and self.board[kingRow - 1][kingCol - 1] == "bp":
                    return True
                if kingCol < 7 and self.board[kingRow - 1][kingCol + 1] == "bp":
                    return True
        else:
            # Vua đen - kiểm tra tốt trắng tấn công từ phía dưới (row lớn hơn)
            # Tốt trắng ở row lớn hơn có thể tấn công vua đen
            if kingRow < 7:
                if kingCol > 0 and self.board[kingRow + 1][kingCol - 1] == "wp":
                    return True
                if kingCol < 7 and self.board[kingRow + 1][kingCol + 1] == "wp":
                    return True
        
        # Kiểm tra mã
        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for move in knightMoves:
            endRow = kingRow + move[0]
            endCol = kingCol + move[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                piece = self.board[endRow][endCol]
                if piece[0] == enemyColor and piece[1] == "N":
                    return True
        
        # Kiểm tra tượng và hậu (đường chéo)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for d in directions:
            for i in range(1, 8):
                endRow = kingRow + d[0] * i
                endCol = kingCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    piece = self.board[endRow][endCol]
                    if piece != "--":
                        if piece[0] == enemyColor and (piece[1] == "B" or piece[1] == "Q"):
                            return True
                        break
                else:
                    break
        
        # Kiểm tra xe và hậu (đường thẳng)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for d in directions:
            for i in range(1, 8):
                endRow = kingRow + d[0] * i
                endCol = kingCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    piece = self.board[endRow][endCol]
                    if piece != "--":
                        if piece[0] == enemyColor and (piece[1] == "R" or piece[1] == "Q"):
                            return True
                        break
                else:
                    break
        
        # Kiểm tra vua địch
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                endRow = kingRow + dr
                endCol = kingCol + dc
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    piece = self.board[endRow][endCol]
                    if piece[0] == enemyColor and piece[1] == "K":
                        return True
        
        return False

    def findKing(self):
        """Tìm vị trí vua hiện tại"""
        kingColor = "w" if self.whiteToMove else "b"
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == kingColor + "K":
                    return r, c
        return -1, -1

    def getPawnMoves(self, r, c, moves):
        """Lấy nước đi của tốt"""
        if self.whiteToMove:
            if self.board[r-1][c] == "--":
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
        else:
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))

    def getRookMoves(self, r, c, moves):
        """Lấy nước đi của xe"""
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        """Lấy nước đi của mã"""
        knightMoves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        """Lấy nước đi của tượng"""
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        """Lấy nước đi của hậu"""
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        """Lấy nước đi của vua"""
        kingMoves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


class Move:
    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = False
        self.promotionChoice = 'Q'
        self.originalPiece = self.pieceMoved  # Lưu quân cờ gốc trước khi phong cấp
        
        # Kiểm tra phong cấp tốt
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7):
            self.isPawnPromotion = True

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.startRow == other.startRow and self.startCol == other.startCol and \
                   self.endRow == other.endRow and self.endCol == other.endCol
        return False

    def getChessNotation(self):
        """Lấy ký hiệu cờ vua"""
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        """Chuyển đổi tọa độ thành ký hiệu cờ vua"""
        return self.colsToFiles[c] + self.rowsToRanks[r]

    colsToFiles = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
    rowsToRanks = {7: '1', 6: '2', 5: '3', 4: '4', 3: '5', 2: '6', 1: '7', 0: '8'}
