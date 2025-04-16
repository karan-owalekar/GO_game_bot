import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from read import readInput
from write import writeOutput

piece_type, prev, board = readInput(5)
available = [(i, j) for i in range(5) for j in range(5) if board[i][j] == 0]

if available:
    move = random.choice(available)
    writeOutput(move)
else:
    writeOutput("PASS")
