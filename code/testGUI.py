import tkinter as tk
from tkinter import messagebox
import chess
import gameLogic
import engine  # your engine.py module

BOARD_SIZE = 8
SQUARE_SIZE = 60

# Unicode symbols for chess pieces
UNICODE_PIECES = {
    chess.PAWN:   {'w': '♙', 'b': '♟'},
    chess.KNIGHT: {'w': '♘', 'b': '♞'},
    chess.BISHOP: {'w': '♗', 'b': '♝'},
    chess.ROOK:   {'w': '♖', 'b': '♜'},
    chess.QUEEN:  {'w': '♕', 'b': '♛'},
    chess.KING:   {'w': '♔', 'b': '♚'},
}

class AtomicChessGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Atomic Chess GUI")
        self.board = chess.Board()
        self.selected_square = None

        self.canvas = tk.Canvas(self.root, width=BOARD_SIZE*SQUARE_SIZE, height=BOARD_SIZE*SQUARE_SIZE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.draw_board()
        self.root.mainloop()

    def draw_board(self):
        self.canvas.delete("all")
        colors = ["#f0d9b5", "#b58863"]
        for rank in range(BOARD_SIZE):
            for file in range(BOARD_SIZE):
                x1 = file * SQUARE_SIZE
                y1 = rank * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE
                color = colors[(rank + file) % 2]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                piece = self.board.piece_at(chess.square(file, 7 - rank))
                if piece:
                    symbol = UNICODE_PIECES[piece.piece_type]['w' if piece.color else 'b']
                    self.canvas.create_text(
                        x1 + SQUARE_SIZE/2, y1 + SQUARE_SIZE/2,
                        text=symbol, font=("Arial", 32)
                    )

    def on_click(self, event):
        file = event.x // SQUARE_SIZE
        rank = 7 - (event.y // SQUARE_SIZE)
        square = chess.square(file, rank)

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.board.pseudo_legal_moves:
                try:
                    self.board, winner = gameLogic.atomicCapture(self.board.copy(), move)
                except ValueError:
                    messagebox.showerror("Invalid Move", "Move invalid after atomic explosion!")
                    self.selected_square = None
                    return

                self.selected_square = None
                self.draw_board()

                if winner is not None:
                    messagebox.showinfo("Game Over", f"Winner: {'White' if winner else 'Black'}")
                    return
                if self.board.is_game_over():
                    messagebox.showinfo("Game Over", f"Result: {self.board.result()}")
                    return

                self.root.update()
                self.root.after(100, self.ai_move)
            else:
                self.selected_square = None

    def ai_move(self):
        move = engine.find_best_move(self.board, depth=4)
        if move is None:
            messagebox.showinfo("Game Over", "No valid AI move!")
            return
        try:
            self.board, winner = gameLogic.atomicCapture(self.board.copy(), move)
        except ValueError:
            messagebox.showerror("Invalid AI Move", "AI tried illegal move!")
            return

        self.draw_board()
        if winner is not None:
            messagebox.showinfo("Game Over", f"Winner: {'White' if winner else 'Black'}")
            return
        if self.board.is_game_over():
            messagebox.showinfo("Game Over", f"Result: {self.board.result()}")
            return

AtomicChessGUI()
