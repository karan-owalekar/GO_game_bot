# tournament.py
import subprocess
import time
import os
import sys
import random
from read import readInput, readOutput
from write import writeNextInput
import argparse
from host import GO

BOARD_SIZE = 5
PLAYER_DIR = 'players'
DEFAULT_PLAYER1 = 'alphabeta_player.py'
DEFAULT_PLAYER2 = 'my_player.py'

class TournamentSimulator:
    def __init__(self, player1, player2, rounds=20):
        self.player1 = player1
        self.player2 = player2
        self.rounds = rounds
        self.results = {
            'p1_as_black_wins': 0,
            'p1_as_black_losses': 0,
            'p1_as_black_ties': 0,
            'p1_as_white_wins': 0,
            'p1_as_white_losses': 0,
            'p1_as_white_ties': 0,
            'p2_as_black_wins': 0,
            'p2_as_black_losses': 0,
            'p2_as_black_ties': 0,
            'p2_as_white_wins': 0,
            'p2_as_white_losses': 0,
            'p2_as_white_ties': 0
        }
    
    def reset_game(self):
        self.board = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.previous_board = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.turn = 1  # 1 for Black, 2 for White
        self.pass_count = 0
    
    def write_input(self):
        writeNextInput(self.turn, self.previous_board, self.board)

    def run_player(self, player_file):
        try:
            subprocess.run(["python", os.path.join(PLAYER_DIR, player_file)], timeout=9)
        except subprocess.TimeoutExpired:
            print(f"Player {player_file} timed out!")
            return False
        return True

    def read_move(self):
        try:
            move_type, x, y = readOutput()
            return move_type, x, y
        except Exception as e:
            print(f"Error reading player output: {e}")
            return "PASS", -1, -1

    def apply_move(self, move_type, x, y):
        self.previous_board = [row[:] for row in self.board]
        if move_type == "MOVE":
            game = GO(BOARD_SIZE)
            game.set_board(self.turn, self.previous_board, self.board)
            if game.valid_place_check(x, y, self.turn):
                game.place_chess(x, y, self.turn)
                game.remove_died_pieces(3 - self.turn)
                self.board = [row[:] for row in game.board]
                self.pass_count = 0
                return True
            else:
                print(f"Invalid move by {self.current_player()} at {x},{y}")
                return False
        else:  # PASS
            self.pass_count += 1
            return True

    def next_turn(self):
        self.turn = 2 if self.turn == 1 else 1

    def current_player(self):
        return self.black_player if self.turn == 1 else self.white_player

    def check_game_end(self):
        # End if both passed
        if self.pass_count >= 2:
            return True
        
        # End if board is full
        if all(self.board[i][j] != 0 for i in range(BOARD_SIZE) for j in range(BOARD_SIZE)):
            return True
        
        # End if maximum moves reached (n*n*2 for a 5×5 board)
        move_count = sum(1 for i in range(BOARD_SIZE) for j in range(BOARD_SIZE) if self.board[i][j] != 0)
        if move_count >= BOARD_SIZE * BOARD_SIZE - 1:
            return True
        
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
            print(f"{self.current_player()} has no valid moves (forced pass)")
            self.next_turn()
            
        return False

    def declare_winner(self):
        black_score = sum(sum(1 for cell in row if cell == 1) for row in self.board)
        white_score = sum(sum(1 for cell in row if cell == 2) for row in self.board) + 2.5  # Komi rule
        
        if black_score > white_score:
            winner = "Black"
            # Update results based on who played black
            if self.black_player == self.player1:
                self.results['p1_as_black_wins'] += 1
                self.results['p2_as_white_losses'] += 1
            else:
                self.results['p2_as_black_wins'] += 1
                self.results['p1_as_white_losses'] += 1
        elif white_score > black_score:
            winner = "White"
            # Update results based on who played white
            if self.white_player == self.player1:
                self.results['p1_as_white_wins'] += 1
                self.results['p2_as_black_losses'] += 1
            else:
                self.results['p2_as_white_wins'] += 1
                self.results['p1_as_black_losses'] += 1
        else:
            winner = "Tie"
            # Update ties based on who played which color
            if self.black_player == self.player1:
                self.results['p1_as_black_ties'] += 1
                self.results['p2_as_white_ties'] += 1
            else:
                self.results['p2_as_black_ties'] += 1
                self.results['p1_as_white_ties'] += 1
        
        return winner, black_score, white_score

    def run_single_game(self, p1_is_black):
        self.reset_game()
        
        if p1_is_black:
            self.black_player = self.player1
            self.white_player = self.player2
        else:
            self.black_player = self.player2
            self.white_player = self.player1
        
        print(f"\nGame starting: {self.black_player} (Black) vs {self.white_player} (White)")
        
        while True:
            current_player = self.black_player if self.turn == 1 else self.white_player
            
            self.write_input()
            if not self.run_player(current_player):
                # Player timed out, other player wins
                print(f"{current_player} timed out! Game over.")
                if current_player == self.black_player:
                    if current_player == self.player1:
                        self.results['p1_as_black_losses'] += 1
                        self.results['p2_as_white_wins'] += 1
                    else:
                        self.results['p2_as_black_losses'] += 1
                        self.results['p1_as_white_wins'] += 1
                else:  # current_player is white
                    if current_player == self.player1:
                        self.results['p1_as_white_losses'] += 1
                        self.results['p2_as_black_wins'] += 1
                    else:
                        self.results['p2_as_white_losses'] += 1
                        self.results['p1_as_black_wins'] += 1
                break
            
            move_type, x, y = self.read_move()
            move_desc = f"{x},{y}" if move_type == "MOVE" else "PASS"
            print(f"{current_player} ({('Black' if self.turn == 1 else 'White')}): {move_desc}")
            
            if not self.apply_move(move_type, x, y):
                # Invalid move, player loses
                print(f"Invalid move by {current_player}! Game over.")
                if current_player == self.black_player:
                    if current_player == self.player1:
                        self.results['p1_as_black_losses'] += 1
                        self.results['p2_as_white_wins'] += 1
                    else:
                        self.results['p2_as_black_losses'] += 1
                        self.results['p1_as_white_wins'] += 1
                else:  # current_player is white
                    if current_player == self.player1:
                        self.results['p1_as_white_losses'] += 1
                        self.results['p2_as_black_wins'] += 1
                    else:
                        self.results['p2_as_white_losses'] += 1
                        self.results['p1_as_black_wins'] += 1
                break
            
            if self.check_game_end():
                winner, black_score, white_score = self.declare_winner()
                print(f"Game over! {winner} wins! Score - Black: {black_score} | White: {white_score:.1f}")
                break
            
            self.next_turn()
    
    def run_tournament(self):
        print(f"Starting tournament: {self.player1} vs {self.player2} ({self.rounds} rounds)")
        
        for i in range(self.rounds):
            p1_is_black = i % 2 == 0  # Alternate who starts as black
            print(f"\n--- Round {i+1}/{self.rounds} ---")
            self.run_single_game(p1_is_black)
        
        self.print_results()
    
    def print_results(self):
        p1_total_wins = self.results['p1_as_black_wins'] + self.results['p1_as_white_wins']
        p1_total_losses = self.results['p1_as_black_losses'] + self.results['p1_as_white_losses']
        p1_total_ties = self.results['p1_as_black_ties'] + self.results['p1_as_white_ties']
        
        p2_total_wins = self.results['p2_as_black_wins'] + self.results['p2_as_white_wins']
        p2_total_losses = self.results['p2_as_black_losses'] + self.results['p2_as_white_losses']
        p2_total_ties = self.results['p2_as_black_ties'] + self.results['p2_as_white_ties']
        
        print("\n" + "="*50)
        print(f"Tournament Results: {self.player1} vs {self.player2}")
        print("="*50)
        
        print(f"\n{self.player1} plays as Black | Win: {self.results['p1_as_black_wins']} | Lose: {self.results['p1_as_black_losses']} | Tie: {self.results['p1_as_black_ties']}")
        print(f"{self.player1} plays as White | Win: {self.results['p1_as_white_wins']} | Lose: {self.results['p1_as_white_losses']} | Tie: {self.results['p1_as_white_ties']}")
        
        print(f"\n{self.player2} plays as Black | Win: {self.results['p2_as_black_wins']} | Lose: {self.results['p2_as_black_losses']} | Tie: {self.results['p2_as_black_ties']}")
        print(f"{self.player2} plays as White | Win: {self.results['p2_as_white_wins']} | Lose: {self.results['p2_as_white_losses']} | Tie: {self.results['p2_as_white_ties']}")
        
        print("\nOverall:")
        print(f"{self.player1}: {p1_total_wins} wins, {p1_total_losses} losses, {p1_total_ties} ties")
        print(f"{self.player2}: {p2_total_wins} wins, {p2_total_losses} losses, {p2_total_ties} ties")
        
        if p1_total_wins > p2_total_wins:
            print(f"\nWinner: {self.player1} with a record of {p1_total_wins}-{p1_total_losses}-{p1_total_ties}")
            print(f"Win/Loss Ratio: {p1_total_wins/(p1_total_losses if p1_total_losses > 0 else 1):.2f}")
        elif p2_total_wins > p1_total_wins:
            print(f"\nWinner: {self.player2} with a record of {p2_total_wins}-{p2_total_losses}-{p2_total_ties}")
            print(f"Win/Loss Ratio: {p2_total_wins/(p2_total_losses if p2_total_losses > 0 else 1):.2f}")
        else:
            print("\nTournament ends in a tie!")


def list_players():
    players = [f for f in os.listdir(PLAYER_DIR) if f.endswith('.py')]
    return players

def main():
    parser = argparse.ArgumentParser(description='Run a tournament between two Go AI players')
    parser.add_argument('-p1', '--player1', help='First player filename (must be in players/ directory)')
    parser.add_argument('-p2', '--player2', help='Second player filename (must be in players/ directory)')
    parser.add_argument('-n', '--rounds', type=int, default=20, help='Number of rounds to play (default: 20)')
    args = parser.parse_args()
    
    players = list_players()
    
    if not players:
        print("Error: No player files found in 'players/' directory")
        sys.exit(1)
    
    # Use the default players if available and not specified otherwise
    player1 = args.player1
    player2 = args.player2
    
    # If player1 not specified, try to use DEFAULT_PLAYER1
    if not player1:
        if DEFAULT_PLAYER1 in players:
            player1 = DEFAULT_PLAYER1
        else:
            print(f"Default player '{DEFAULT_PLAYER1}' not found. You'll need to select a player.")
    
    # If player2 not specified, try to use DEFAULT_PLAYER2
    if not player2:
        if DEFAULT_PLAYER2 in players:
            player2 = DEFAULT_PLAYER2
        else:
            print(f"Default player '{DEFAULT_PLAYER2}' not found. You'll need to select a player.")
    
    # Validate the selected players
    if player1 and player1 not in players:
        print(f"Error: Player '{player1}' not found in 'players/' directory")
        player1 = None
    
    if player2 and player2 not in players:
        print(f"Error: Player '{player2}' not found in 'players/' directory")
        player2 = None
    
    # If players still not specified or invalid, ask for selection
    if not player1:
        print("Available players:")
        for i, player in enumerate(players):
            print(f"{i+1}. {player}")
        
        while True:
            try:
                choice = int(input(f"Select player 1 (1-{len(players)}): "))
                if 1 <= choice <= len(players):
                    player1 = players[choice-1]
                    break
            except ValueError:
                pass
            print("Invalid choice. Try again.")
    
    if not player2:
        print("Available players:")
        for i, player in enumerate(players):
            if player != player1:  # Don't show already selected player
                print(f"{i+1}. {player}")
        
        while True:
            try:
                choice = int(input(f"Select player 2 (1-{len(players)}): "))
                if 1 <= choice <= len(players) and players[choice-1] != player1:
                    player2 = players[choice-1]
                    break
            except ValueError:
                pass
            print("Invalid choice. Try again.")
    
    tournament = TournamentSimulator(player1, player2, args.rounds)
    tournament.run_tournament()

if __name__ == "__main__":
    main()