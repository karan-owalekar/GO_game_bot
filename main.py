# main.py
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import time
import os
import random
import shutil
from read import readInput, readOutput
from write import writeNextInput

BOARD_SIZE = 5
PLAYER_DIR = 'players'

class GoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Little-Go Game Visualizer")
        self.board = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.previous_board = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.turn = 1  # 1 for Black, 2 for White
        self.buttons = []
        self.game_log = []
        self.running = False
        self.manual_mode = False
        self.pass_count = 0
        self.create_widgets()

    def create_widgets(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        for i in range(BOARD_SIZE):
            row = []
            for j in range(BOARD_SIZE):
                btn = tk.Button(self.frame, text="", width=4, height=2,
                                command=lambda x=i, y=j: self.manual_move(x, y))
                btn.grid(row=i, column=j)
                row.append(btn)
            self.buttons.append(row)

        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=10)

        self.black_var = tk.StringVar()
        self.white_var = tk.StringVar()
        self.black_menu = ttk.Combobox(self.control_frame, textvariable=self.black_var, width=25)
        self.white_menu = ttk.Combobox(self.control_frame, textvariable=self.white_var, width=25)
        self.black_menu.grid(row=0, column=0, padx=5)
        self.white_menu.grid(row=0, column=1, padx=5)

        self.mode_var = tk.StringVar(value="bot")
        tk.Radiobutton(self.control_frame, text="Bot vs Bot", variable=self.mode_var, value="bot").grid(row=1, column=0)
        tk.Radiobutton(self.control_frame, text="Manual vs Bot", variable=self.mode_var, value="manual").grid(row=1, column=1)

        tk.Button(self.control_frame, text="Start Game", command=self.start_game).grid(row=2, column=0, pady=5)
        tk.Button(self.control_frame, text="Step", command=self.step_game).grid(row=2, column=1, pady=5)
        tk.Button(self.control_frame, text="Export Log", command=self.export_log).grid(row=3, column=0, columnspan=2, pady=5)

        self.update_dropdowns()

    def update_dropdowns(self):
        players = [f for f in os.listdir(PLAYER_DIR) if f.endswith('.py')]
        self.black_menu['values'] = players
        self.white_menu['values'] = players
        self.black_var.set(players[0] if players else '')
        self.white_var.set(players[1] if len(players) > 1 else players[0] if players else '')

    def update_board(self):
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                val = self.board[i][j]
                if val == 1:
                    self.buttons[i][j].config(text="X", bg="black", fg="white")
                elif val == 2:
                    self.buttons[i][j].config(text="O", bg="white", fg="black")
                else:
                    self.buttons[i][j].config(text="", bg="SystemButtonFace")

    def write_input(self):
        writeNextInput(self.turn, self.previous_board, self.board)

    def run_player(self, player_file):
        subprocess.run(["python", os.path.join(PLAYER_DIR, player_file)], timeout=9)

    def read_move(self):
        move_type, x, y = readOutput()
        return move_type, x, y

    def apply_move(self, move_type, x, y):
        from host import GO

        self.previous_board = [row[:] for row in self.board]
        if move_type == "MOVE":
            game = GO(BOARD_SIZE)
            game.set_board(self.turn, self.previous_board, self.board)
            if game.valid_place_check(x, y, self.turn):
                game.place_chess(x, y, self.turn)
                game.remove_died_pieces(3 - self.turn)
                self.board = [row[:] for row in game.board]
                self.pass_count = 0
                self.game_log.append(f"{self.get_player_name(self.turn)} played: {x},{y}")
            else:
                self.game_log.append(f"{self.get_player_name(self.turn)} attempted invalid move: {x},{y}")
                return
        else:
            self.pass_count += 1
            self.game_log.append(f"{self.get_player_name(self.turn)} passed")

    def next_turn(self):
        self.turn = 2 if self.turn == 1 else 1

    def check_game_end(self):
        from host import GO
        
        # End if both passed
        if self.pass_count >= 2:
            return self.declare_winner()
        
        # End if board is full
        if all(self.board[i][j] != 0 for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)):
            return self.declare_winner()
        
        # End if maximum moves reached (n*n-1 for a 5×5 board)
        move_count = sum(1 for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if self.board[i][j] != 0)
        if move_count >= BOARD_SIZE * BOARD_SIZE - 1:
            return self.declare_winner()
        
        # Check if current player has any valid moves
        game = GO(BOARD_SIZE)
        game.set_board(self.turn, self.previous_board, self.board)
        has_valid_moves = False
        
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if self.board[i][j] == 0 and game.valid_place_check(i, j, self.turn):
                    has_valid_moves = True
                    break
            if has_valid_moves:
                break
        
        # If current player has no valid moves, they must pass
        if not has_valid_moves and sum(1 for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if self.board[i][j] == 0) > 0:
            self.pass_count += 1
            self.game_log.append(f"{self.get_player_name(self.turn)} has no valid moves (forced pass)")
            self.next_turn()
            
        return False

    def declare_winner(self):
        black_score = sum(sum(1 for cell in row if cell == 1) for row in self.board)
        white_score = sum(sum(1 for cell in row if cell == 2) for row in self.board) + 2.5
        if black_score > white_score:
            winner = self.black_var.get()
        elif white_score > black_score:
            winner = self.white_var.get()
        else:
            winner = "Draw"
        self.running = False
        self.game_log.append(f"Game Over. Winner: {winner}")
        self.update_board()
        messagebox.showinfo("Game Over", f"Winner: {winner}\nBlack: {black_score} | White: {white_score:.1f}")
        return True

    def get_player_name(self, turn):
        return self.black_var.get() if turn == 1 else self.white_var.get()

    def step_game(self):
        if not self.running:
            return
        if self.manual_mode and self.turn == 1:
            return  # Wait for human move
        self.write_input()
        player_file = self.black_var.get() if self.turn == 1 else self.white_var.get()
        self.run_player(player_file)
        move_type, x, y = self.read_move()
        self.apply_move(move_type, x, y)
        self.update_board()
        if not self.check_game_end():
            self.next_turn()
            if not self.manual_mode:
                self.root.after(500, self.step_game)

    def manual_move(self, x, y):
        if not self.manual_mode or self.turn != 1:
            return
        if self.board[x][y] != 0:
            return
        self.previous_board = [row[:] for row in self.board]
        self.board[x][y] = 1
        self.pass_count = 0
        self.game_log.append(f"Manual player (Black) played: {x},{y}")
        self.update_board()
        self.turn = 2
        self.step_game()

    def start_game(self):
        self.board = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.previous_board = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.turn = 1
        self.game_log = []
        self.pass_count = 0
        self.running = True
        self.manual_mode = self.mode_var.get() == "manual"
        self.update_board()
        if not self.manual_mode:
            self.root.after(500, self.step_game)

    def export_log(self):
        with open("game_log.txt", "w") as f:
            for line in self.game_log:
                f.write(line + "\n")
        messagebox.showinfo("Exported", "Game log saved to game_log.txt")

if __name__ == "__main__":
    if not os.path.exists("players/random_player.py"):
        with open("players/random_player.py", "w") as f:
            f.write("""import sys\nimport os\nimport random\nsys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\nfrom read import readInput\nfrom write import writeOutput\n\npiece_type, prev, board = readInput(5)\navailable = [(i, j) for i in range(5) for j in range(5) if board[i][j] == 0]\nif available:\n    move = random.choice(available)\n    writeOutput(move)\nelse:\n    writeOutput(\"PASS\")\n""")
    root = tk.Tk()
    app = GoGUI(root)
    root.mainloop()