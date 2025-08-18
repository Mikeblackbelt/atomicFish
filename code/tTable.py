import chess
import pickle

class TTEntry:
    def __init__(self, depth, value, flag, best_move):
        self.depth = depth
        self.value = value
        self.flag = flag
        self.best_move = best_move

transposition_table = {}

def probe_tt(board_hash, depth, alpha, beta):
    entry = transposition_table.get(board_hash)
    if entry and entry.depth >= depth:
        if entry.flag == "EXACT":
            return entry
        elif entry.flag == "LOWERBOUND" and entry.value >= beta:
            return entry
        elif entry.flag == "UPPERBOUND" and entry.value <= alpha:
            return entry
    return None

def store_tt(board_hash, depth, value, flag, best_move):
    transposition_table[board_hash] = TTEntry(depth, value, flag, best_move)

def save_tt(filename="ttable.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(transposition_table, f)

def load_tt(filename="ttable.pkl"):
    global transposition_table
    try:
        with open(filename, "rb") as f:
            transposition_table = pickle.load(f)
    except FileNotFoundError:
        transposition_table = {}
