"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Check if initial state
    initial = True
    for row in board:
        if X in row or O in row:
            initial = False
            break
    if initial == True:
        return X
    
    # Check if board in terminal state - game over 
    elif terminal(board):
        return "G"

    # Assess all past moves to return next player
    else:
        X_count = 0
        O_count = 0
        for row in board:
            X_count += row.count(X)
            O_count += row.count(O)
        if X_count > O_count:
            return O
        elif X_count == O_count:
            return X



def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    if terminal(board):
        return "G"

    # If board is not terminal, possible actions are all empty cells
    empty_cells = set()

    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == EMPTY:
                empty_cells.add((i, j))
    
    return empty_cells


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Check if action is valid
    possible_actions = actions(board)

    if action in possible_actions:
        i, j = action
    else:
        raise Exception("Invalid Action")

    # Modify board with the valid action for given player
    move = player(board)
    new_board = copy.deepcopy(board)
    new_board[i][j] = move

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # Check for consecutive X or O horizontally
    for row in board:
        if O not in row and EMPTY not in row:
            return X
        if X not in row and EMPTY not in row:
            return O

    # Check for consecutive X's or O's vertically
    board_transpose = copy.deepcopy(board)
    board_transpose = list(map(list, zip(*board)))

    for row in board_transpose:
        if O not in row and EMPTY not in row:
            return X
        if X not in row and EMPTY not in row:
            return O

    # Check for consecutive X's or O's in both diagonals
    diagonal_elements = [[], []]
    
    for i in range(len(board)):
        diagonal_elements[0].append(board[i][i])
        diagonal_elements[1].append(board[i][2-i])
    
    for diagonal in diagonal_elements:
        if O not in diagonal and EMPTY not in diagonal:
            return X
        if X not in diagonal and EMPTY not in diagonal:
            return O


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Check if all cells have been exhausted
    exhausted = True
    for row in board:
        if EMPTY in row:
            exhausted = False
            break
    if exhausted:
        return True

    # If any player is a winner, board is at terminal state
    elif winner(board) is not None:
        return True

    return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if terminal(board):
        win = winner(board)

        if win == X:
            return 1
        if win == O:
            return -1
        else:
            return 0

def maximizer(board):

    if terminal(board):
        return utility(board)

    v = -float('inf')

    temp_board = copy.deepcopy(board)

    # Recursively find the maximum of minimized values
    for action in actions(board):
        v = max(v, minimizer(result(temp_board, action)))

    return v

def minimizer(board):
    if terminal(board):
        return utility(board)

    v = float('inf')

    temp_board = copy.deepcopy(board)

    # Recursively find the minimum of maximized values
    for action in actions(board):
        v = min(v, maximizer(result(temp_board, action)))

    return v

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    # Return "maximum" action from minimized actions
    if player(board)== X:
        maxima = -float("inf")
        for action in actions(board):
            v = minimizer(result(board, action)) 
            if v > maxima:
                maxima = v
                optimal = action
    
    # Return "minimum" action from maximized actions
    if player(board) == O:
        minima = float("inf")
        for action in actions(board):
            v = maximizer(result(board, action))
            if v < minima:
                minima = v
                optimal = action

    return optimal

    

    
    

    
