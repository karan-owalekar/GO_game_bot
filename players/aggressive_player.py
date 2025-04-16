import sys
import os
import random
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from read import readInput
from write import writeOutput
from host import GO

TIME_LIMIT = 8.5  # Safely under 9s subprocess limit

def main():
    start_time = time.time()
    piece_type, previous_board, board = readInput(5)
    
    go = GO(5)
    go.set_board(piece_type, previous_board, board)
    
    move = find_aggressive_move(go, piece_type, start_time)
    
    writeOutput(move if move != "PASS" else "PASS")

def find_aggressive_move(go, piece_type, start_time):
    board_size = len(go.board)
    opponent = 3 - piece_type
    best_move = None
    max_total = -1
    valid_moves = []

    for i in range(board_size):
        for j in range(board_size):
            if not go.valid_place_check(i, j, piece_type, test_check=True):
                continue
            valid_moves.append((i, j))
            
            test_go = go.copy_board()
            test_go.place_chess(i, j, piece_type)
            immediate = len(test_go.find_died_pieces(opponent))
            test_go.remove_died_pieces(opponent)

            # Opponent's best counter-move
            min_our_second_gain = float('inf')
            opponent_counter_limit = 5  # pruning
            second_response_limit = 5

            counter_moves = [
                (x, y) for x in range(board_size) for y in range(board_size)
                if test_go.valid_place_check(x, y, opponent, test_check=True)
            ][:opponent_counter_limit]

            if not counter_moves:
                total = immediate
            else:
                for x2, y2 in counter_moves:
                    resp_go = test_go.copy_board()
                    resp_go.place_chess(x2, y2, opponent)
                    resp_go.remove_died_pieces(piece_type)

                    second_gain = 0
                    for sx in range(board_size):
                        for sy in range(board_size):
                            if resp_go.valid_place_check(sx, sy, piece_type, test_check=True):
                                sim = resp_go.copy_board()
                                sim.place_chess(sx, sy, piece_type)
                                captured = len(sim.find_died_pieces(opponent))
                                second_gain = max(second_gain, captured)
                                if second_gain > min_our_second_gain:
                                    break
                        if second_gain > min_our_second_gain:
                            break

                    min_our_second_gain = min(min_our_second_gain, second_gain)
                    if time.time() - start_time > TIME_LIMIT:
                        break

                total = immediate + min_our_second_gain

            if total > max_total:
                max_total = total
                best_move = (i, j)

            if time.time() - start_time > TIME_LIMIT:
                break

    return best_move if best_move else (random.choice(valid_moves) if valid_moves else "PASS")

if __name__ == "__main__":
    main()
