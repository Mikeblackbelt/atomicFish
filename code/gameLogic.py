import chess

def atomicCapture(board: chess.Board, move: chess.Move) -> chess.Board:
    """
    Explodes a capture move on the chess board according to atomic chess rules.
    Removes the captured piece and adjacent non-pawn, non-king pieces.
    """
    print([m.uci() for m in board.pseudo_legal_moves])
    if not any(m.uci() == move.uci() for m in board.pseudo_legal_moves):
        raise ValueError("Move is not pseudo-legal")

    if not board.is_capture(move):
        board.push(move)
        return board

    to_sq = move.to_square

    board.push(move)

    # Now remove adjacent pieces (explosion)
    for adj_sq in adjacent_squares(to_sq):
        piece = board.piece_at(adj_sq)
        if piece and piece.piece_type not in [chess.PAWN, chess.KING]:
            board.remove_piece_at(adj_sq)
        elif piece and piece.piece_type == chess.KING:
            board.empty()  
            return (board, not piece.color)
    
    board.remove_piece_at(to_sq)  # Remove the piece that was captured

    return board


def adjacent_squares(square):
    rank = chess.square_rank(square)
    file = chess.square_file(square)
    adj = []
    for dr in [-1, 0, 1]:
        for df in [-1, 0, 1]:
            if dr == 0 and df == 0:
                continue
            r = rank + dr
            f = file + df
            if 0 <= r <= 7 and 0 <= f <= 7:
                adj.append(chess.square(f, r))
    return adj

if __name__ == "__main__":
    fen = "rnbqkbnr/pppppppp/8/2rpp3/8/8/PPP1PPPP/RNBQKBNR w KQkq - 0 1"
    board = chess.Board(fen)
    print(board)

    while True:

        # Black plays pawn d5xc4 (capture)
       move = chess.Move.from_uci(input())
       #print("Is capture?", board.is_capture(move))  # True

       board = atomicCapture(board, move)
       print(board)
