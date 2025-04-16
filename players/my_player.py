#import host
import numpy as np
import time

#Input
with open('input.txt') as f:
    lines = f.readlines()

# Parse player number 
playerNumber = int(lines[0])

# Use numpy to convert to array directly 
previous_board = np.array([list(line.rstrip()) for line in lines[1:6]], dtype=int)
current_board = np.array([list(line.rstrip()) for line in lines[6:11]], dtype=int)

# Convert to list of lists if needed
previousBoard = previous_board.tolist() 
currentBoard = current_board.tolist()

_komi = 2.5 #Seting komi for white player
_yourPlayer = playerNumber
_maxDepth = 5 #Seting max depth for Min-Max algorithm

def countOccurrences(matrix, target):
    matrix_array = np.array(matrix)
    return np.sum(matrix_array == target)

def getAllAvailableMoves(board):
    open = np.where(np.array(board) == 0)
    return list(zip(open[0], open[1]))

def removeLongJumpMoves(availableMoves, currentBoard, playerNumber):
    deltas = ([0, 1], [1, 0], [0, -1], [-1, 0],  
              [1, 1], [-1, -1], [1, -1], [-1, 1])
              
    for move in availableMoves[:]:
        x, y = move
        
        validSurround = set()
        for dx, dy in deltas:
            if 0 <= x+dx < len(currentBoard) and 0 <= y+dy < len(currentBoard[0]):
                validSurround.add((x+dx, y+dy))
                
        if not any(currentBoard[s[0]][s[1]] == playerNumber for s in validSurround):
            availableMoves.remove(move)
            
    return availableMoves

def removeCapturedPieces(board, opponentNumber):
    new_board = [row[:] for row in board]
    to_check = set()
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == opponentNumber:
                deltas = ([0, 1], [1, 0], [0, -1], [-1, 0])
                # check if any of the surrounding cells is 0
                for dx, dy in deltas:
                    if 0 <= i+dx < len(board) and 0 <= j+dy < len(board[0]) and board[i+dx][j+dy] == 0:
                        new_board[i][j] = "r"
                        to_check.add((i, j))
                        break
                else:
                    new_board[i][j] = "g"
                    to_check.add((i, j))

    while to_check:
        tempBoard = [row[:] for row in new_board]
        to_check_next = set()
        for i, j in to_check:
            if new_board[i][j] == "g":
                deltas = ([0, 1], [1, 0], [0, -1], [-1, 0])
                # check if any of the surrounding cells is "r"
                for dx, dy in deltas:
                    if 0 <= i+dx < len(board) and 0 <= j+dy < len(board[0]) and new_board[i+dx][j+dy] == "r":
                        new_board[i][j] = "r"
                        to_check_next.add((i, j))
                        break
                else:
                    to_check_next.add((i, j))
        if tempBoard == new_board:
            break
        to_check = to_check_next

    for i in range(len(board)):
        for j in range(len(board[0])):
            if new_board[i][j] == "g":
                new_board[i][j] = 0
            elif new_board[i][j] == "r":
                new_board[i][j] = opponentNumber

    return new_board

def getLibertyMoves(currentBoard, availableMoves, playerNumber):
    libertyMoves = []
    for move in availableMoves:
        tempBoard = [row[:] for row in currentBoard]
        tempBoard[move[0]][move[1]] = playerNumber

        if tempBoard != removeCapturedPieces(tempBoard, (playerNumber%2)+1):
            libertyMoves.append(move)
    
    return libertyMoves

def removeKOMoves(libertyMoves, previousBoard, availableMoves, playerNumber):
    for move in libertyMoves:
        if previousBoard[move[0]][move[1]] == playerNumber:
            availableMoves.remove(move)
            libertyMoves.remove(move)
    return availableMoves

def removeSuicideMoves(currentBoard, availableMoves, libertyMoves, playerNumber):
    newMovesAfterSuicide = []
    for move in availableMoves:
        if move not in libertyMoves:
            #check if this move kills our player
            tempBoard = [row[:] for row in currentBoard]
            tempBoard[move[0]][move[1]] = playerNumber
            if tempBoard == removeCapturedPieces(tempBoard, playerNumber):
                newMovesAfterSuicide.append(move)
        else:
            newMovesAfterSuicide.append(move)
    return newMovesAfterSuicide     

def getAvailableMoves(currentBoard, previousBoard, playerNumber, count):
    #Getting all available moves
    availableMoves = getAllAvailableMoves(currentBoard)
    # print("[INFO] Available moves: ")
    # print(availableMoves, end="\n\n")

    libertyMoves = getLibertyMoves(currentBoard, availableMoves, playerNumber)
    # print("[INFO] Liberty moves: ")
    # print(libertyMoves, end="\n\n")

    if count < 13:
        availableMoves = removeLongJumpMoves(availableMoves, currentBoard, playerNumber)
    # print("[INFO] Available moves after removing long jumps: ")
    # print(availableMoves, end="\n\n")

    #remove KO moves
    availableMoves = removeKOMoves(libertyMoves, previousBoard, availableMoves, playerNumber)
    # print("[INFO] Available moves after removing KO moves: ")
    # print(availableMoves, end="\n\n")
    # print(libertyMoves)

    #remove suicude moves
    availableMoves = removeSuicideMoves(currentBoard, availableMoves, libertyMoves, playerNumber)
    # print("[INFO] Available moves after removing suicide moves: ")
    # print(availableMoves, end="\n\n")
    return availableMoves

def evaluateBoard(whitePoints, blackPoints, numAvailableMoves):
    # print("White Score", whitePoints)
    # print("Black Score", blackPoints)
    # print()
    if _yourPlayer == 1:
        return ((whitePoints+_komi)-blackPoints)*0.8 + numAvailableMoves*0.2
    else:
        return (blackPoints-(whitePoints+_komi))*0.8 + numAvailableMoves*0.2

def getMaxMove(currentBoard, previousBoard, playerNumber, depth, alpha, beta):
    whitePoints = countOccurrences(currentBoard, 1)
    blackPoints = countOccurrences(currentBoard, 2)
    availableMoves = getAvailableMoves(currentBoard.copy(), previousBoard.copy(), playerNumber, whitePoints+blackPoints)
    if len(availableMoves) == 0 or depth == _maxDepth:
        return evaluateBoard(whitePoints, blackPoints, len(availableMoves)), None  # Return the best score and no move initially

    best_score = float('-inf')
    best_move = None

    for move in availableMoves:
        nextBoard = [row[:] for row in currentBoard]
        nextBoard[move[0]][move[1]] = playerNumber
        nextBoard = removeCapturedPieces(nextBoard.copy(), playerNumber % 2 + 1)

        current_score, _ = getMinMove(nextBoard.copy(), currentBoard.copy(), playerNumber % 2 + 1, depth + 1, alpha, beta)

        if current_score > best_score:
            best_score = current_score
            best_move = move

        alpha = max(alpha, best_score)

        if beta <= alpha:
            break  # Prune the rest of the branches

    return best_score, best_move

def getMinMove(currentBoard, previousBoard, playerNumber, depth, alpha, beta):
    whitePoints = countOccurrences(currentBoard, 1)
    blackPoints = countOccurrences(currentBoard, 2)
    availableMoves = getAvailableMoves(currentBoard.copy(), previousBoard.copy(), playerNumber, whitePoints+blackPoints)
    if len(availableMoves) == 0 or depth == _maxDepth:
        return evaluateBoard(whitePoints, blackPoints, len(availableMoves)), None  # Return the best score and no move initially

    best_score = float('inf')
    best_move = None

    for move in availableMoves:
        nextBoard = [row[:] for row in currentBoard]
        nextBoard[move[0]][move[1]] = playerNumber
        nextBoard = removeCapturedPieces(nextBoard.copy(), playerNumber % 2 + 1)

        current_score, _ = getMaxMove(nextBoard.copy(), currentBoard.copy(), playerNumber % 2 + 1, depth + 1, alpha, beta)

        if current_score < best_score:
            best_score = current_score
            best_move = move

        beta = min(beta, best_score)

        if beta <= alpha:
            break  # Prune the rest of the branches

    return best_score, best_move


###############################################################################################################

# print(playerNumber)
# print(previousBoard)
# print("[INFO] Current board: ")
# for row in currentBoard:
#     print(row)
# print()

#Play best first move
if all(all(x==0 for x in y) for y in currentBoard):
    with open("output.txt", "w") as f:
        f.write("2,2")
    #print("[OUTPUT] 2,2")
    exit()
elif (countOccurrences(currentBoard, (playerNumber%2 + 1)) == 1) and (countOccurrences(currentBoard, playerNumber) == 0):
    if currentBoard[2][2] == (playerNumber%2 + 1):
        with open("output.txt", "w") as f:
            f.write("1,2")
        #print("[OUTPUT] 1,2")
        exit()
    else:
        with open("output.txt", "w") as f:
            f.write("2,2")
        #print("[OUTPUT] 2,2")
        exit()
else:
    pass

#Using Min-Max algorithm to find best move
start = time.time()
best_score, best_move = getMaxMove(currentBoard.copy(), previousBoard.copy(), playerNumber, 1, float('-inf'), float('inf'))
# print("Time taken:", time.time()-start)
whitePoints = countOccurrences(currentBoard, 1)
blackPoints = countOccurrences(currentBoard, 2)
possibleMoves = getAvailableMoves(currentBoard.copy(), previousBoard.copy(), playerNumber, whitePoints+blackPoints)
# print("Available moves: ", possibleMoves)

if len(possibleMoves)>0:
    # print("Best move: ", best_move)
    # print("Best score: ", best_score)
    with open("output.txt", "w") as f:
        f.write(str(best_move[0])+","+str(best_move[1]))
else:
    # print("BEST MOVE: PASS")
    with open("output.txt", "w") as f:
        f.write("PASS")