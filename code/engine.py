import chess
import gameLogic
import random
import time

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3.5,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 10000
}

# Modes: 'play', 'evaluate', 'depth_test'
TEST_MODE = 'depth_test'

def evaluate_pos(board: chess.Board):
    score = 0
    score += (board.pawns & board.occupied_co[chess.WHITE]).bit_count() * 1 - (board.pawns & board.occupied_co[chess.BLACK]).bit_count() * 1
    score += (board.knights & board.occupied_co[chess.WHITE]).bit_count() * 3.5 - (board.knights & board.occupied_co[chess.BLACK]).bit_count() * 3.5
    score += (board.bishops & board.occupied_co[chess.WHITE]).bit_count() * 3 - (board.bishops & board.occupied_co[chess.BLACK]).bit_count() * 3
    score += (board.rooks & board.occupied_co[chess.WHITE]).bit_count() * 5 - (board.rooks & board.occupied_co[chess.BLACK]).bit_count() * 5
    score += (board.queens & board.occupied_co[chess.WHITE]).bit_count() * 9 - (board.queens & board.occupied_co[chess.BLACK]).bit_count() * 9
    score += (board.kings & board.occupied_co[chess.WHITE]).bit_count() * 10000 - (board.kings & board.occupied_co[chess.BLACK]).bit_count() * 10000
    return score
"""
def MVV_LVA(moves: list[chess.Move], board: chess.Board) -> float:
    sorted_moves = []
    for move in moves:
        if not board.is_capture(move):
            sorted_moves.append((move, 0))  
            
        to_sq = move.to_square
        captured_piece = board.piece_at(to_sq)
        if captured_piece is None:
            sorted_moves.append((move, 0))

        value = PIECE_VALUES[captured_piece.piece_type]
        if move.from_square == chess.E8 or move.from_square == chess.E1:  # King moves
             value += 10000
        sorted_moves.append((move, value))
"""

def minimax_iterative(board: chess.Board, depth: int, maximizing: bool) -> float: #removed recursion
    Node = lambda b, d, max_flag, alpha, beta: {
        'board': b,
        'depth': d,
        'max': max_flag,
        'alpha': alpha,
        'beta': beta,
        'children': iter(b.pseudo_legal_moves),
        'score': float('-inf') if max_flag else float('inf')
    }

    root = Node(board, depth, maximizing, float('-inf'), float('inf'))
    stack = [root]

    while stack:
        node = stack[-1]

        if node['depth'] == 0 or node['board'].is_game_over():
            if node['board'].is_game_over():
                result = node['board'].result()
                if result == '1-0':
                    node['score'] = 10000 + node['depth']
                elif result == '0-1':
                    node['score'] = -10000 - node['depth']
                else:
                    node['score'] = 0
            else:
                node['score'] = evaluate_pos(node['board'])
            stack.pop()
            if stack:
                parent = stack[-1]
                if node['score'] is not None:
                    if parent['max']:
                        parent['score'] = max(parent.get('score', float('-inf')), node['score'])
                        parent['alpha'] = max(parent['alpha'], node['score'])
                    else:
                        parent['score'] = min(parent.get('score', float('inf')), node['score'])
                        parent['beta'] = min(parent['beta'], node['score'])
                    if parent['beta'] <= parent['alpha']:
                        stack.pop()
            continue

        try:
            move = next(node['children'])
            temp_board = node['board'].copy()
            new_board, winner = gameLogic.atomicCapture(temp_board, move)

            if winner is not None:
                score = 10000 + node['depth'] if winner == chess.WHITE else -10000 - node['depth']
                if node['max']:
                    node['score'] = max(node.get('score', float('-inf')), score)
                    node['alpha'] = max(node['alpha'], score)
                else:
                    node['score'] = min(node.get('score', float('inf')), score)
                    node['beta'] = min(node['beta'], score)
                if node['beta'] <= node['alpha']:
                    stack.pop()
                continue

            child = Node(new_board, node['depth'] - 1, not node['max'], node['alpha'], node['beta'])
            stack.append(child)

        except StopIteration:
            stack.pop()
            if stack and node['score'] is not None:
                parent = stack[-1]
                if parent['max']:
                    parent['score'] = max(parent.get('score', float('-inf')), node['score'])
                    parent['alpha'] = max(parent['alpha'], node['score'])
                else:
                    parent['score'] = min(parent.get('score', float('inf')), node['score'])
                    parent['beta'] = min(parent['beta'], node['score'])
                if parent['beta'] <= parent['alpha']:
                    stack.pop()

    return root['score']


def find_best_move(board: chess.Board, depth: int) -> chess.Move | None:
    best_moves = []
    maximizing = board.turn
    best_score = float('-inf') if maximizing else float('inf')

    for move in board.pseudo_legal_moves:
        temp_board = board.copy()
        new_board, winner = gameLogic.atomicCapture(temp_board, move)

        if winner is not None:
            score = 10000 if winner == chess.WHITE else -10000
        else:
            score = minimax_iterative(new_board, depth - 1, not maximizing)

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
    match TEST_MODE:
        case 'evaluate':
            board = chess.Board()
            start_time = time.time()
            for _ in range(100_000):
                evaluate_pos(board)
            elapsed = time.time() - start_time
            print(f"Evaluation time per position: {elapsed / 100_000 * 1_000_000:.2f} μs "
                  f"(total {elapsed:.2f} seconds for 100k positions)")

        case 'play':
            board = chess.Board()
            while True:
                print(board)
                try:
                    player_move = chess.Move.from_uci(input("Your move: "))
                    board, winner = gameLogic.atomicCapture(board, player_move)
                except Exception:
                    print("Illegal move. Try again.")
                    continue

                if winner is not None:
                    print("Game over! Winner:", "White" if winner else "Black")
                    break
                if board.is_game_over():
                    print("Game over:", board.result())
                    break

                print("AI is thinking...")
                ai_move = find_best_move(board, depth=4)
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

        case 'depth_test':
            board = chess.Board()
            current_depth = 2
            times = []
            while True:
                start_time = time.time()
                find_best_move(board, current_depth)
                times.append(time.time() - start_time)
                branching_factor = times[-1] / times[-2] if len(times) > 1 else 1   
                print(f"Time taken for depth {current_depth}: {times[-1]:.3f}s (branching factor: {branching_factor})")
                current_depth += 2
