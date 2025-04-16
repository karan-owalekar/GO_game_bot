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
    
    # Find the move that maximizes captures in the next two moves
    best_move = find_aggressive_move(go, piece_type)
    
    # Write the output
    if best_move == "PASS":
        writeOutput("PASS")
    else:
        writeOutput(best_move)

def find_aggressive_move(go, piece_type):
    """
    Find the move that captures the maximum number of opponent stones
    looking ahead two moves
    
    :param go: GO game instance
    :param piece_type: 1('X') or 2('O')
    :return: (i, j) or "PASS" if no valid moves
    """
    valid_moves = []
    best_move = None
    max_capture = -1
    board_size = len(go.board)
    opponent = 3 - piece_type
    
    # Try each position on the board for our first move
    for i in range(board_size):
        for j in range(board_size):
            # Check if the move is valid
            if go.valid_place_check(i, j, piece_type, test_check=True):
                valid_moves.append((i, j))
                
                # Copy the GO instance to test this move
                test_go = go.copy_board()
                test_go.place_chess(i, j, piece_type)
                
                # Count immediate captures
                died_pieces = test_go.find_died_pieces(opponent)
                immediate_captures = len(died_pieces)
                test_go.remove_died_pieces(opponent)
                
                # Calculate potential captures after opponent's best response
                min_opponent_captures = float('inf')
                
                # Try each possible opponent response
                opponent_responses = []
                for x in range(board_size):
                    for y in range(board_size):
                        if test_go.valid_place_check(x, y, opponent, test_check=True):
                            opponent_responses.append((x, y))
                            
                            # If opponent has no possible response, great for us!
                            if not opponent_responses:
                                min_opponent_captures = 0
                            else:
                                # For each opponent response, see what our best follow-up is
                                for resp_x, resp_y in opponent_responses[:10]:  # Limit branching factor to 10
                                    resp_go = test_go.copy_board()
                                    resp_go.place_chess(resp_x, resp_y, opponent)
                                    resp_go.remove_died_pieces(piece_type)
                                    
                                    # Calculate our best second move after opponent's response
                                    max_second_captures = 0
                                    for second_x in range(board_size):
                                        for second_y in range(board_size):
                                            if resp_go.valid_place_check(second_x, second_y, piece_type, test_check=True):
                                                second_go = resp_go.copy_board()
                                                second_go.place_chess(second_x, second_y, piece_type)
                                                second_captures = len(second_go.find_died_pieces(opponent))
                                                max_second_captures = max(max_second_captures, second_captures)
                                    
                                    # We want to minimize opponent's best response
                                    min_opponent_captures = min(min_opponent_captures, max_second_captures)
                
                # Total score for this move is immediate captures plus future capture potential
                # If opponent has no moves, set min_opponent_captures to 0
                if min_opponent_captures == float('inf'):
                    min_opponent_captures = 0
                    
                total_capture_potential = immediate_captures + min_opponent_captures
                
                if total_capture_potential > max_capture:
                    max_capture = total_capture_potential
                    best_move = (i, j)
    
    if best_move:
        return best_move
    elif valid_moves:
        # If no good aggressive move found, choose a random valid move
        return random.choice(valid_moves)
    else:
        # No valid moves, pass
        return "PASS"

if __name__ == "__main__":
    main()
