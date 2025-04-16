import sys
import os
import random
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from read import readInput
from write import writeOutput
from host import GO

def main():
    # Read the input
    piece_type, previous_board, board = readInput(5)
    
    # Initialize a GO game instance with the current state
    go = GO(5)
    go.set_board(piece_type, previous_board, board)
    
    # Find the move that captures the maximum number of opponent stones
    best_move = find_greedy_move(go, piece_type)
    
    # Write the output
    if best_move == "PASS":
        writeOutput("PASS")
    else:
        writeOutput(best_move)

def find_greedy_move(go, piece_type):
    """
    Find the move that captures the maximum number of opponent stones
    
    :param go: GO game instance
    :param piece_type: 1('X') or 2('O')
    :return: (i, j) or "PASS" if no valid moves
    """
    valid_moves = []
    best_move = None
    max_capture = -1
    board_size = len(go.board)
    
    # Try each position on the board
    for i in range(board_size):
        for j in range(board_size):
            # Check if the move is valid
            if go.valid_place_check(i, j, piece_type, test_check=True):
                # Copy the GO instance to test this move
                test_go = go.copy_board()
                test_go.place_chess(i, j, piece_type)
                
                # Count how many opponent pieces would be captured
                died_pieces = test_go.find_died_pieces(3 - piece_type)
                captures = len(died_pieces)
                
                valid_moves.append((i, j))
                if captures > max_capture:
                    max_capture = captures
                    best_move = (i, j)
    
    if best_move and max_capture > 0:
        return best_move
    elif valid_moves:
        # If no captures are possible, choose a random valid move
        return random.choice(valid_moves)
    else:
        # No valid moves, pass
        return "PASS"

if __name__ == "__main__":
    main()