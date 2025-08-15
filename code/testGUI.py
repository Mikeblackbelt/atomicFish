#thank you chatgpt i did not write this code

import tkinter as tk
from tkinter import messagebox
import chess
import engine  # your AI logic with find_BestMove
import gameLogic
import time

BOARD_SIZE = 480
SQUARE_SIZE = BOARD_SIZE // 8

# Colors
LIGHT_COLOR = "#F0D9B5"
DARK_COLOR = "#B58863"

# Simple piece symbols for display
PIECE_SYMBOLS = {
    "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
    "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚"
}

class AtomicChessGUI:
    def __init__(self, root):
        self.root = root
        self.board = chess.Board()
        self.selected_square = None

        self.canvas = tk.Canvas(root, width=BOARD_SIZE, height=BOARD_SIZE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.click_square)

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(8):
            for c in range(8):
                color = LIGHT_COLOR if (r + c) % 2 == 0 else DARK_COLOR
                x1, y1 = c * SQUARE_SIZE, r * SQUARE_SIZE
                x2, y2 = x1 + SQUARE_SIZE, y1 + SQUARE_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                square = chess.square(c, 7 - r)  # chess.SQUARES is 0-63, rank 7 at top
                piece = self.board.piece_at(square)
                if piece:
                    symbol = PIECE_SYMBOLS[piece.symbol()]
                    self.canvas.create_text(
                        x1 + SQUARE_SIZE/2, y1 + SQUARE_SIZE/2,
                        text=symbol, font=("Arial", 32)
                    )

    def click_square(self, event):
        col = event.x // SQUARE_SIZE
        row = 7 - (event.y // SQUARE_SIZE)
        square = chess.square(col, row)

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.board.pseudo_legal_moves:
                self.board, winner = gameLogic.atomicCapture(self.board, move)
                self.draw_board()
                self.selected_square = None

                if winner is not None:
                    messagebox.showinfo("Game Over", f"Winner: {'White' if winner else 'Black'}")
                    self.root.quit()
                    return
                self.canvas.update()
                time.sleep(1)
                # AI turn
                ai_move = engine.find_BestMove(4, self.board)
                if ai_move is None:
                    messagebox.showinfo("Game Over", "AI Resigns!" )
                    self.root.quit()
                    return
                self.board, winner = gameLogic.atomicCapture(self.board, ai_move)
                self.draw_board()
                if winner is not None:
                    messagebox.showinfo("Game Over", f"Winner: {'White' if winner else 'Black'}")
                    self.root.quit()
            else:
                # Invalid move, deselect
                self.selected_square = None

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Atomic Chess GUI")
    gui = AtomicChessGUI(root)
    root.mainloop()
