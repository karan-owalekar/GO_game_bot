import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import time
import os
import random
import shutil
from PIL import Image, ImageTk
from read import readInput, readOutput
from write import writeNextInput

BOARD_SIZE = 5
PLAYER_DIR = 'players'

class GoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Little-Go Game Visualizer")
        self.root.configure(bg="#2c3e50")  # Dark blue background
        
        # Load piece images
        self.load_images()
        
        self.board = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.previous_board = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.turn = 1  # 1 for Black, 2 for White
        self.buttons = []
        self.game_log = []
        self.running = False
        self.manual_mode = False
        self.pass_count = 0
        
        self.create_widgets()
        
    def load_images(self):
        # Create assets directory if it doesn't exist
        if not os.path.exists("assets/images"):
            os.makedirs("assets/images", exist_ok=True)
            
        # Create default piece images if they don't exist
        black_path = "assets/images/black_stone.png"
        white_path = "assets/images/white_stone.png"
        bg_path = "assets/images/background.png"
        
        if not os.path.exists(black_path):
            img = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
            img_draw = ImageTk.Draw(img)
            img_draw.ellipse([2, 2, 38, 38], fill="black")
            img.save(black_path)
            
        if not os.path.exists(white_path):
            img = Image.new('RGBA', (40, 40), (0, 0, 0, 0))
            img_draw = ImageTk.Draw(img)
            img_draw.ellipse([2, 2, 38, 38], fill="white", outline="black", width=1)
            img.save(white_path)
            
        if not os.path.exists(bg_path):
            # Create a default background image with grid lines
            img = Image.new('RGB', (40, 40), "#d4b887")  # Wooden color
            img_draw = ImageTk.Draw(img)
            # Draw horizontal and vertical lines
            img_draw.line([(0, 20), (40, 20)], fill="#7f5733", width=1)
            img_draw.line([(20, 0), (20, 40)], fill="#7f5733", width=1)
            img.save(bg_path)
        
        # Load images
        self.black_img = ImageTk.PhotoImage(Image.open(black_path).resize((40, 40)))
        self.white_img = ImageTk.PhotoImage(Image.open(white_path).resize((40, 40)))
        self.bg_img = ImageTk.PhotoImage(Image.open(bg_path).resize((40, 40)))

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg="#2c3e50", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Turn indicator
        self.turn_frame = tk.Frame(main_frame, bg="#2c3e50")
        self.turn_frame.pack(pady=10)
        
        self.turn_label = tk.Label(self.turn_frame, text="Current Turn:", font=("Helvetica", 14), 
                                  bg="#2c3e50", fg="#ecf0f1")
        self.turn_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.turn_indicator = tk.Label(self.turn_frame, text="Black", font=("Helvetica", 14, "bold"), 
                                      bg="#2c3e50", fg="#ecf0f1")
        self.turn_indicator.pack(side=tk.LEFT)
        
        # Game board
        self.board_frame = tk.Frame(main_frame, bg="#34495e", padx=10, pady=10)  # Lighter blue for board frame
        self.board_frame.pack(pady=10)
        
        # Create grid of buttons
        for i in range(BOARD_SIZE):
            row = []
            for j in range(BOARD_SIZE):
                btn = tk.Button(self.board_frame, image=self.bg_img, width=40, height=40, bg="#d4b887",
                              relief=tk.FLAT, highlightthickness=1, highlightbackground="#7f5733",
                              command=lambda x=i, y=j: self.manual_move(x, y))
                btn.grid(row=i, column=j, padx=1, pady=1)
                row.append(btn)
            self.buttons.append(row)

        # Control panel
        self.control_frame = tk.Frame(main_frame, bg="#2c3e50", pady=10)
        self.control_frame.pack(fill=tk.X)
        
        # Player selection frame
        player_frame = tk.Frame(self.control_frame, bg="#2c3e50")
        player_frame.pack(pady=10)
        
        # Black player
        black_label = tk.Label(player_frame, text="Black:", font=("Helvetica", 12), 
                             bg="#2c3e50", fg="#ecf0f1")
        black_label.grid(row=0, column=0, padx=5, sticky=tk.W)
        
        self.black_var = tk.StringVar()
        self.black_menu = ttk.Combobox(player_frame, textvariable=self.black_var, width=25)
        self.black_menu.grid(row=0, column=1, padx=5)
        
        # White player
        white_label = tk.Label(player_frame, text="White:", font=("Helvetica", 12), 
                             bg="#2c3e50", fg="#ecf0f1")
        white_label.grid(row=1, column=0, padx=5, sticky=tk.W)
        
        self.white_var = tk.StringVar()
        self.white_menu = ttk.Combobox(player_frame, textvariable=self.white_var, width=25)
        self.white_menu.grid(row=1, column=1, padx=5)
        
        # Mode selection
        mode_frame = tk.Frame(self.control_frame, bg="#2c3e50")
        mode_frame.pack(pady=10)
        
        self.mode_var = tk.StringVar(value="bot")
        
        style = ttk.Style()
        style.configure("TRadiobutton", background="#2c3e50", foreground="#ecf0f1", font=("Helvetica", 12))
        
        ttk.Radiobutton(mode_frame, text="Bot vs Bot", variable=self.mode_var, 
                      value="bot", style="TRadiobutton").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Manual vs Bot", variable=self.mode_var, 
                      value="manual", style="TRadiobutton").pack(side=tk.LEFT, padx=10)
        
        # Action buttons
        button_frame = tk.Frame(self.control_frame, bg="#2c3e50")
        button_frame.pack(pady=10)

        # Modern, more subtle button styling
        button_style = {
            "font": ("Helvetica", 12),
            "fg": "#ecf0f1",       # Light text for all buttons
            "padx": 15,
            "pady": 8,
            "relief": tk.FLAT,
            "borderwidth": 0
        }

        # Start Game - subtle blue
        start_button = tk.Button(button_frame, text="Start Game", bg="#34495e", 
                                activebackground="#2c3e50", activeforeground="#3498db",
                                command=self.start_game, **button_style)
        start_button.pack(side=tk.LEFT, padx=8)

        # Step - subtle green
        step_button = tk.Button(button_frame, text="Step", bg="#34495e", 
                            activebackground="#2c3e50", activeforeground="#2ecc71",
                            command=self.step_game, **button_style)
        step_button.pack(side=tk.LEFT, padx=8)

        # Export - subtle red
        export_button = tk.Button(button_frame, text="Export Log", bg="#34495e", 
                                activebackground="#2c3e50", activeforeground="#e74c3c",
                                command=self.export_log, **button_style)
        export_button.pack(side=tk.LEFT, padx=8)
        
        # Status message
        self.status_var = tk.StringVar(value="Ready to play")
        self.status_label = tk.Label(main_frame, textvariable=self.status_var, font=("Helvetica", 12),
                                   bg="#2c3e50", fg="#ecf0f1")
        self.status_label.pack(pady=10)
        
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
                if val == 1:  # Black
                    self.buttons[i][j].config(image=self.black_img)
                elif val == 2:  # White
                    self.buttons[i][j].config(image=self.white_img)
                else:  # Empty - use background image
                    self.buttons[i][j].config(image=self.bg_img)
        
        # Update turn indicator
        if self.turn == 1:
            self.turn_indicator.config(text="Black", fg="#ecf0f1")
        else:
            self.turn_indicator.config(text="White", fg="#ecf0f1")
        
        self.root.update()

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
                self.status_var.set(f"{self.get_player_name(self.turn)} placed at {x},{y}")
            else:
                self.game_log.append(f"{self.get_player_name(self.turn)} attempted invalid move: {x},{y}")
                self.status_var.set(f"{self.get_player_name(self.turn)} attempted invalid move")
                return
        else:
            self.pass_count += 1
            self.game_log.append(f"{self.get_player_name(self.turn)} passed")
            self.status_var.set(f"{self.get_player_name(self.turn)} passed")

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
            self.status_var.set(f"{self.get_player_name(self.turn)} has no valid moves (forced pass)")
            self.next_turn()
            
        return False

    def declare_winner(self):
        black_score = sum(sum(1 for cell in row if cell == 1) for row in self.board)
        white_score = sum(sum(1 for cell in row if cell == 2) for row in self.board) + 2.5
        if black_score > white_score:
            winner = self.black_var.get()
            result_text = f"Black ({winner}) wins"
        elif white_score > black_score:
            winner = self.white_var.get()
            result_text = f"White ({winner}) wins"
        else:
            winner = "Draw"
            result_text = "Game ended in a draw"
        
        self.running = False
        self.game_log.append(f"Game Over. Winner: {winner}")
        self.status_var.set(f"Game Over. {result_text}")
        self.update_board()
        
        messagebox.showinfo("Game Over", 
                          f"{result_text}\nBlack: {black_score} | White: {white_score:.1f}")
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
        
        # Update status
        self.status_var.set(f"Waiting for {player_file} to move...")
        self.root.update()
        
        # Run the player
        self.run_player(player_file)
        move_type, x, y = self.read_move()
        self.apply_move(move_type, x, y)
        self.update_board()
        
        if not self.check_game_end():
            self.next_turn()
            if not self.manual_mode:
                self.root.after(500, self.step_game)

    def manual_move(self, x, y):
        if not self.running or not self.manual_mode or self.turn != 1:
            return
        if self.board[x][y] != 0:
            return
            
        from host import GO
        game = GO(BOARD_SIZE)
        game.set_board(self.turn, self.previous_board, self.board)
        
        if not game.valid_place_check(x, y, self.turn):
            self.status_var.set("Invalid move! Try again.")
            return
            
        self.previous_board = [row[:] for row in self.board]
        game.place_chess(x, y, self.turn)
        game.remove_died_pieces(3 - self.turn)
        self.board = [row[:] for row in game.board]
        
        self.pass_count = 0
        self.game_log.append(f"Manual player (Black) played: {x},{y}")
        self.status_var.set(f"You moved to {x},{y}")
        self.update_board()
        
        if not self.check_game_end():
            self.turn = 2
            self.root.after(500, self.step_game)

    def start_game(self):
        self.board = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.previous_board = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.turn = 1
        self.game_log = []
        self.pass_count = 0
        self.running = True
        self.manual_mode = self.mode_var.get() == "manual"
        
        # Reset UI - set all buttons to background image
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self.buttons[i][j].config(image=self.bg_img)
        
        self.status_var.set("Game started!")
        self.turn_indicator.config(text="Black")
        
        if not self.manual_mode:
            self.root.after(500, self.step_game)
        else:
            self.status_var.set("Your turn (Black)")

    def export_log(self):
        with open("game_log.txt", "w") as f:
            for line in self.game_log:
                f.write(line + "\n")
        self.status_var.set("Game log saved to game_log.txt")
        messagebox.showinfo("Exported", "Game log saved to game_log.txt")

if __name__ == "__main__":
    # Create players directory if it doesn't exist
    if not os.path.exists(PLAYER_DIR):
        os.makedirs(PLAYER_DIR)
        
    # Create random player if it doesn't exist
    if not os.path.exists("players/random_player.py"):
        with open("players/random_player.py", "w") as f:
            f.write("""import sys\nimport os\nimport random\nsys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\nfrom read import readInput\nfrom write import writeOutput\n\npiece_type, prev, board = readInput(5)\navailable = [(i, j) for i in range(5) for j in range(5) if board[i][j] == 0]\nif available:\n    move = random.choice(available)\n    writeOutput(move)\nelse:\n    writeOutput(\"PASS\")\n""")
    
    # Create assets directory if it doesn't exist 
    if not os.path.exists("assets/images"):
        os.makedirs("assets/images", exist_ok=True)
    
    root = tk.Tk()
    root.configure(bg="#2c3e50")
    app = GoGUI(root)
    root.mainloop()