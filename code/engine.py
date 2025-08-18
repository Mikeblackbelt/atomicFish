import chess
import chess.polyglot
import gameLogic
import random
import tTable
import time

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3.5,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 10000
}

def evaluate_pos(board: chess.Board):
    score = 0
    score += (board.pawns & board.occupied_co[chess.WHITE]).bit_count() - (board.pawns & board.occupied_co[chess.BLACK]).bit_count()
    score += (board.knights & board.occupied_co[chess.WHITE]).bit_count() * 3.5 - (board.knights & board.occupied_co[chess.BLACK]).bit_count() * 3.5
    score += (board.bishops & board.occupied_co[chess.WHITE]).bit_count() * 3 - (board.bishops & board.occupied_co[chess.BLACK]).bit_count() * 3
    score += (board.rooks & board.occupied_co[chess.WHITE]).bit_count() * 5 - (board.rooks & board.occupied_co[chess.BLACK]).bit_count() * 5
    score += (board.queens & board.occupied_co[chess.WHITE]).bit_count() * 9 - (board.queens & board.occupied_co[chess.BLACK]).bit_count() * 9
    score += (board.kings & board.occupied_co[chess.WHITE]).bit_count() * 10000 - (board.kings & board.occupied_co[chess.BLACK]).bit_count() * 10000
    return score

def atomic_legal_moves(board: chess.Board):
    moves = []
    for move in board.pseudo_legal_moves:
        try:
            _, _ = gameLogic.atomicCapture(board.copy(), move)
            moves.append(move)
        except ValueError:
            continue
    return moves

def MVV_LVA(board: chess.Board):
    scored = []
    for move in atomic_legal_moves(board):
        score = 0
        if move.promotion:
            score += PIECE_VALUES[move.promotion] + 10
        if board.is_capture(move):
            attacker = board.piece_at(move.from_square)
            victim = board.piece_at(move.to_square)
            attacker_val = PIECE_VALUES[attacker.piece_type] if attacker else 0
            victim_val = PIECE_VALUES[victim.piece_type] if victim else 0
            score += victim_val - 0.1 * attacker_val
        scored.append((move, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return [m for m, _ in scored]

def minimax(board, depth, maximizing, alpha=float('-inf'), beta=float('inf')):
    # TT probe
    board_hash = chess.polyglot.zobrist_hash(board)
    entry = tTable.probe_tt(board_hash, depth, alpha, beta)
    if entry and entry.depth >= depth:
        if entry.flag == "EXACT":
            return entry.value
        elif entry.flag == "LOWERBOUND":
            alpha = max(alpha, entry.value)
        elif entry.flag == "UPPERBOUND":
            beta = min(beta, entry.value)
        if beta <= alpha:
            return entry.value

    if depth == 0 or board.is_game_over():
        if board.is_game_over():
            result = board.result()
            if result == '1-0':
                val = 10000 + depth
            elif result == '0-1':
                val = -10000 - depth
            else:
                val = 0
        else:
            val = evaluate_pos(board)
        tTable.store_tt(board_hash, depth, val, "EXACT", None)
        return val

    moves = MVV_LVA(board)
    best_val = float('-inf') if maximizing else float('inf')
    best_move = None

    for move in moves:
        try:
            new_board, winner = gameLogic.atomicCapture(board.copy(), move)
        except ValueError:
            continue

        if winner is not None:
            val = 10000 + depth if winner == chess.WHITE else -10000 - depth
        else:
            val = minimax(new_board, depth - 1, not maximizing, alpha, beta)

        if maximizing:
            if val > best_val:
                best_val = val
                best_move = move
            alpha = max(alpha, best_val)
        else:
            if val < best_val:
                best_val = val
                best_move = move
            beta = min(beta, best_val)

        if beta <= alpha:
            break

    # store in TT
    flag = "EXACT"
    if best_val <= alpha:
        flag = "UPPERBOUND"
    elif best_val >= beta:
        flag = "LOWERBOUND"

    tTable.store_tt(board_hash, depth, best_val, flag, best_move)
    return best_val

def find_best_move(board, depth):
    maximizing = board.turn
    moves = MVV_LVA(board)
    best_score = float('-inf') if maximizing else float('inf')
    best_moves = []

    for move in moves:
        try:
            new_board, winner = gameLogic.atomicCapture(board.copy(), move)
        except ValueError:
            continue

        if winner is not None:
            score = 10000 if winner == chess.WHITE else -10000
        else:
            score = minimax(new_board, depth - 1, not maximizing)

        if maximizing:
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        else:
            if score < best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

    return random.choice(best_moves) if best_moves else None

if __name__ == "__main__":
    tTable.load_tt("ttable.pkl")
    board = chess.Board()
    while not board.is_game_over():
        start_time = time.time()
        ai_move = find_best_move(board, 5)
        if ai_move is None:
            print(f"AI ({board.turn}) resigns or no legal moves.")
            break
        board, winner = gameLogic.atomicCapture(board, ai_move)
        print(f"AI plays: {ai_move.uci()} (Time: {time.time() - start_time:.2f}s)")
        time.sleep(1) #minmimum delay for better UX
        print(board)
        if winner is not None:
            print(f"Winner: {'White' if winner else 'Black'}")
            break
    tTable.save_tt("ttable.pkl")

