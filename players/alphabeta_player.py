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
    
    # Find the best move using minimax with alpha-beta pruning
    best_move = find_minimax_move(go, piece_type)
    
    # Write the output
    if best_move == "PASS":
        writeOutput("PASS")
    else:
        writeOutput(best_move)

def evaluate(go, piece_type):
    """
    Evaluate the board state from piece_type's perspective
    
    :param go: GO game instance
    :param piece_type: 1('X') or 2('O')
    :return: score (higher is better for piece_type)
    """
    opponent = 3 - piece_type
    
    # Count pieces
    my_pieces = go.score(piece_type)
    opponent_pieces = go.score(opponent)
    
    # Count liberties
    my_liberties = 0
    opponent_liberties = 0
    board_size = len(go.board)
    
    for i in range(board_size):
        for j in range(board_size):
            if go.board[i][j] == piece_type:
                if go.find_liberty(i, j):
                    my_liberties += 1
            elif go.board[i][j] == opponent:
                if go.find_liberty(i, j):
                    opponent_liberties += 1
    
    # Territory control (empty spaces adjacent to my pieces)
    my_territory = 0
    opponent_territory = 0
    
    for i in range(board_size):
        for j in range(board_size):
            if go.board[i][j] == 0:  # Empty space
                my_adjacent = False
                opponent_adjacent = False
                
                neighbors = go.detect_neighbor(i, j)
                for ni, nj in neighbors:
                    if go.board[ni][nj] == piece_type:
                        my_adjacent = True
                    elif go.board[ni][nj] == opponent:
                        opponent_adjacent = True
                
                if my_adjacent and not opponent_adjacent:
                    my_territory += 1
                elif opponent_adjacent and not my_adjacent:
                    opponent_territory += 1
    
    # Combined score (weighting factors can be adjusted)
    score = (my_pieces - opponent_pieces) * 10 + \
            (my_liberties - opponent_liberties) * 2 + \
            (my_territory - opponent_territory) * 1
    
    return score

def get_valid_moves(go, piece_type, limit=10):
    """
    Get valid moves for the given piece type, limited by the branching factor
    
    :param go: GO game instance
    :param piece_type: 1('X') or 2('O')
    :param limit: maximum number of moves to return (branching factor)
    :return: list of (i, j) positions for valid moves
    """
    valid_moves = []
    board_size = len(go.board)
    
    # First check for capturing moves
    for i in range(board_size):
        for j in range(board_size):
            if go.valid_place_check(i, j, piece_type, test_check=True):
                test_go = go.copy_board()
                test_go.place_chess(i, j, piece_type)
                
                # Prioritize moves that capture opponent pieces
                died_pieces = test_go.find_died_pieces(3 - piece_type)
                if died_pieces:
                    valid_moves.append((i, j, len(died_pieces)))
    
    # Sort by number of captures (descending)
    capturing_moves = sorted(valid_moves, key=lambda x: x[2], reverse=True)
    result = [(move[0], move[1]) for move in capturing_moves]
    
    # If we need more moves to reach the limit, add other valid moves
    if len(result) < limit:
        for i in range(board_size):
            for j in range(board_size):
                if go.valid_place_check(i, j, piece_type, test_check=True) and (i, j) not in result:
                    result.append((i, j))
                    if len(result) >= limit:
                        break
            if len(result) >= limit:
                break
    
    return result[:limit]

def minimax(go, piece_type, depth, alpha, beta, maximizing):
    """
    Minimax algorithm with alpha-beta pruning
    
    :param go: GO game instance
    :param piece_type: 1('X') or 2('O')
    :param depth: current depth
    :param alpha: alpha value for pruning
    :param beta: beta value for pruning
    :param maximizing: whether this is a maximizing step
    :return: (score, move) tuple
    """
    opponent = 3 - piece_type
    
    # Terminal node or maximum depth reached
    if depth == 0:
        return evaluate(go, piece_type), None
    
    current_player = piece_type if maximizing else opponent
    valid_moves = get_valid_moves(go, current_player)
    
    # No valid moves, player must pass
    if not valid_moves:
        # Evaluate if we're at max depth or make recursive call
        if depth <= 1:
            return evaluate(go, piece_type), "PASS"
        new_go = go.copy_board()
        score, _ = minimax(new_go, piece_type, depth - 1, alpha, beta, not maximizing)
        return score, "PASS"
    
    best_move = None
    
    if maximizing:
        max_eval = float('-inf')
        for i, j in valid_moves:
            new_go = go.copy_board()
            if new_go.place_chess(i, j, current_player):
                new_go.remove_died_pieces(opponent)
                eval_score, _ = minimax(new_go, piece_type, depth - 1, alpha, beta, False)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = (i, j)
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
        
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for i, j in valid_moves:
            new_go = go.copy_board()
            if new_go.place_chess(i, j, current_player):
                new_go.remove_died_pieces(piece_type)
                eval_score, _ = minimax(new_go, piece_type, depth - 1, alpha, beta, True)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = (i, j)
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
        
        return min_eval, best_move

def find_minimax_move(go, piece_type):
    """
    Find the best move using minimax with alpha-beta pruning
    
    :param go: GO game instance
    :param piece_type: 1('X') or 2('O')
    :return: (i, j) or "PASS" if no valid moves
    """
    valid_moves = get_valid_moves(go, piece_type)
    
    if not valid_moves:
        return "PASS"
    
    # Use minimax with depth=2 (looking ahead 2 moves)
    _, best_move = minimax(go, piece_type, 2, float('-inf'), float('inf'), True)
    
    return best_move if best_move else random.choice(valid_moves)

if __name__ == "__main__":
    main()
