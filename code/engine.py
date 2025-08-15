import chess
import gameLogic
import random

def getMoveResult(board: chess.Board, move: chess.Move):
    newboard = board.copy()
    newboard, winner = gameLogic.atomicCapture(newboard, move)
    return newboard, winner

def evaluatePos(board: chess.Board):
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 10**10
    }
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values[piece.piece_type]
            score += value if piece.color == chess.WHITE else -value
    return score

def minimax(board: chess.Board, depth: int, maximizing: bool):
    if board.is_game_over():
        return float('inf') if maximizing else float('-inf')
    best_score = float('-inf') if maximizing else float('inf')
    for move in board.pseudo_legal_moves:
        temp_board = board.copy()
        new_board, winner = gameLogic.atomicCapture(temp_board, move)
        if winner is not None:
            score = float('inf') if winner == chess.WHITE else float('-inf')
        elif depth > 1:
            score = minimax(new_board, depth - 1, not maximizing)
        else:
            score = evaluatePos(new_board)
        if maximizing:
            best_score = max(best_score, score)
        else:
            best_score = min(best_score, score)
    return best_score

def find_BestMove(depth: int, board: chess.Board):
    moves_scores = []
    for move in board.pseudo_legal_moves:
        temp_board = board.copy()
        new_board, winner = gameLogic.atomicCapture(temp_board, move)
        if winner is not None:
            score = float('inf') if winner == chess.WHITE else float('-inf')
        else:
            score = minimax(new_board, depth - 1, not board.turn)
        moves_scores.append((move, score))
    best_score = max(moves_scores, key=lambda x: x[1])[1] if board.turn else min(moves_scores, key=lambda x: x[1])[1]
    best_moves = [move for move, score in moves_scores if score == best_score]
    if abs(best_score) > 1000:
        return None
    return random.choice(best_moves)

if __name__ == "__main__":
    board = chess.Board()
    while True:
        print(board)
        player_move = chess.Move.from_uci(input("Your move! "))
        board, winner = gameLogic.atomicCapture(board, player_move)
        print(board)
        if winner is not None:
            print("Game over! Winner:", "White" if winner else "Black")
            break
        if board.is_game_over():
            print("Game over:", board.result())
            break
        print("AI is thinking...")
        ai_move = find_BestMove(4, board)
        board, winner = gameLogic.atomicCapture(board, ai_move)
        print(f"AI plays: {ai_move.uci()}")
        if winner is not None:
            print("Game over! Winner:", "White" if winner else "Black")
            break
        if board.is_game_over():
            print("Game over:", board.result())
            break
