from unittest import case
import chess
import gameLogic
import random
import time 

piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3.5,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 10000
}

testMode = 'evaluate' # 'play' or 'evaluate'

def evaluatePos(board: chess.Board):
    score = 0
    score += board.pawns & board.occupied_co[chess.WHITE].bit_count() * piece_values[chess.PAWN] - board.pawns & board.occupied_co[chess.BLACK].bit_count() * piece_values[chess.PAWN]
    score += (board.knights & board.occupied_co[chess.WHITE]).bit_count() * piece_values[chess.KNIGHT] - (board.knights & board.occupied_co[chess.BLACK]).bit_count() * piece_values[chess.KNIGHT]
    score += (board.bishops & board.occupied_co[chess.WHITE]).bit_count() * piece_values[chess.BISHOP] - (board.bishops & board.occupied_co[chess.BLACK]).bit_count() * piece_values[chess.BISHOP]
    score += (board.rooks & board.occupied_co[chess.WHITE]).bit_count() * piece_values[chess.ROOK] - (board.rooks & board.occupied_co[chess.BLACK]).bit_count() * piece_values[chess.ROOK]
    score += (board.queens & board.occupied_co[chess.WHITE]).bit_count() * piece_values[chess.QUEEN] - (board.queens & board.occupied_co[chess.BLACK]).bit_count() * piece_values[chess.QUEEN]
    score += (board.kings & board.occupied_co[chess.WHITE]).bit_count() * piece_values[chess.KING] - (board.kings & board.occupied_co[chess.BLACK]).bit_count() * piece_values[chess.KING]

    return score

def minimax(board: chess.Board, depth: int, maximizing: bool, alpha=float('-inf'), beta=float('inf'), moveCounter=None):
    if moveCounter is None:
        moveCounter = [0]

    if board.is_game_over():
        if board.result() == '1-0':
            return 10000 + depth
        elif board.result() == '0-1':
            return -10000 - depth
        else:
            return 0

    if depth == 0:
        return evaluatePos(board)

    best_score = float('-inf') if maximizing else float('inf')

    for move in board.pseudo_legal_moves:
        moveCounter[0] += 1
        temp_board = board.copy()
        new_board, winner = gameLogic.atomicCapture(temp_board, move)

        if winner is not None:
            score = 10000 + depth if winner == chess.WHITE else -10000 - depth
        else:
            score = minimax(new_board, depth - 1, not maximizing, alpha, beta, moveCounter)

        if maximizing:
            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break  # prune
        else:
            best_score = min(best_score, score)
            beta = min(beta, best_score)
            if beta <= alpha:
                break  # prune

    return best_score

def find_BestMove(depth: int, board: chess.Board):
    moveCounter = [0]
    best_moves = []
    best_score = float('-inf') if board.turn else float('inf')

    for move in board.pseudo_legal_moves:
        temp_board = board.copy()
        new_board, winner = gameLogic.atomicCapture(temp_board, move)

        if winner is not None:
            score = 10000 if winner == chess.WHITE else -10000
        else:
            score = minimax(new_board, depth - 1, not board.turn, moveCounter=moveCounter)

        if board.turn and score > best_score:
            best_score = score
            best_moves = [move]
        elif board.turn and score == best_score:
            best_moves.append(move)
        elif not board.turn and score < best_score:
            best_score = score
            best_moves = [move]
        elif not board.turn and score == best_score:
            best_moves.append(move)

    print("Total positions evaluated:", moveCounter[0])
    return random.choice(best_moves) if best_moves else None

if __name__ == "__main__":
    match testMode:
        case 'evaluate':
             board = chess.Board()
             start_time = time.time()
             for i in range(10**5):    
                 evaluatePos(board)

             print(f"Evaluation time per position: {(time.time() - start_time)/10**5 * 10**6 } microseconds (total {time.time() - start_time} seconds for 100k positions)")

             """start_time = time.time()
             for i in range(10**5):
                 evaluatePos(board)
             print(f"Evaluation time per position: {(time.time() - start_time)/10**5 * 10**6 } microseconds (total {time.time() - start_time} seconds for 100k positions)")"""

        case 'play':    
                board = chess.Board()
                while True:
                    print(board)
                    try:
                        player_move = chess.Move.from_uci(input("Your move! "))
                        board, winner = gameLogic.atomicCapture(board, player_move)
                    except:
                        print("Illegal move. Try again.")
                        continue

                    print(board)
                    if winner is not None:
                        print("Game over! Winner:", "White" if winner else "Black")
                        break
                    if board.is_game_over():
                        print("Game over:", board.result())
                        break

                    print("AI is thinking...")
                    ai_move = find_BestMove(4, board)
                    if ai_move is None:
                        print("No valid AI move! Game over.")
                        break
                    board, winner = gameLogic.atomicCapture(board, ai_move)
                    print(f"AI plays: {ai_move.uci()}")
                    if winner is not None:
                        print("Game over! Winner:", "White" if winner else "Black")
                        break
                    if board.is_game_over():
                        print("Game over:", board.result())
                        break
