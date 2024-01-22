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

'''   
board = [[O, X, X],
         [EMPTY, X, O],
         [EMPTY, O, X]]

board = [[EMPTY, EMPTY, EMPTY],
         [EMPTY, EMPTY, EMPTY],
         [EMPTY, EMPTY, EMPTY]]

action = (1,2)
'''

def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # Count the number of empty space on the board
    count = board[0].count(None) + board[1].count(None) + board[2].count(None)
    
    # O's turn if count is even, X's turn if count is uneven
    if (count % 2) == 0:
        return "O"
    else:
        return "X"


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # Make a set and store every coordinate that has "None" as value
    actionlist = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == None:
                actionlist.add((i,j))
    
    # Return the set with all possible actions
    return actionlist

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Set i and j coordinate of the action
    i, j = action
    
    # Check if legal move; if board space is empty
    if board[i][j] != None:
        raise ValueError("Illegal Move")
    
    # Make a copy of the board and implement move
    boardcopy = copy.deepcopy(board)
    boardcopy[i][j] = player(board)
    
    # Return the new board state
    return boardcopy



def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Define all (8) possible win options and return winner 
    if board[0][0] == board [1][1] == board [2][2]:
        return board[0][0]
    elif board[0][2] == board [1][1] == board [2][0]:
        return board[0][2]
    elif board[0][0] == board [0][1] == board [0][2] != None:
        return board[0][0]
    elif board[1][0] == board [1][1] == board [1][2] != None:
        return board[1][0]
    elif board[2][0] == board [2][1] == board [2][2] != None:
        return board[2][0]
    elif board[0][0] == board [1][0] == board [2][0] != None:
        return board[0][0]
    elif board[0][1] == board [1][1] == board [2][1] != None:
        return board[0][1]
    elif board[0][2] == board [1][2] == board [2][2] != None:
        return board[0][2]    
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # Game is over when there is a winner, or when the board is full (aka no possible moves left)
    if winner(board) != None or len(actions(board)) == 0:
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # Use the winner function to determine winner
    if winner(board) == "X":
        return 1
    elif winner(board) == "O":
        return -1
    # If there is no winner, the game is tied
    else:
        return 0

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Don't return anything if game has ended
    if terminal(board):
        return None
    
    # Return action that maximizes utility for player X
    if player(board) == "X":
        return maxi(board)[1]
    # Return action that minimizes utility for player O
    else:
        return mini(board)[1]


def mini(board):
    """
    Returns the minimum utility score with associated action.
    """
    # If game has ended, return utility without action
    if terminal(board):
        return utility(board), None
    
    # Initial value for v
    v = 2
    
    # Loop over every action to find minimum utility
    for action in actions(board):
        v1, move1 = maxi(result(board, action))
        if v1 < v:
            v = v1
            move = action
            # If a winning action is found, directly return
            if v == -1:
                return v, move
    
    # Return minimum utility and action
    return v, move


def maxi(board):
    """
    Returns the maximum utility score with associated action.
    """
    # If game has ended, return utility without action
    if terminal(board):
        return utility(board), None
    
    # Initial value for v
    v = -2
    
    # Loop over every action to find maximum utility
    for action in actions(board):
        v1, move1 = mini(result(board, action))
        if v1 > v:
            v = v1
            move = action
            # If a winning action is found, directly return
            if v == 1:
                return v, move

    # Return maximum utility and action
    return v, move
    
