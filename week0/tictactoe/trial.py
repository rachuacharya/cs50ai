from tictactoe import *
import copy
X = "X"
O = "O"
EMPTY=None
board=[[EMPTY, O, X], [EMPTY,O, X], [EMPTY,EMPTY, EMPTY]]
board_1=[[O, O, X], [O, EMPTY, EMPTY], [X, EMPTY , X]]
board_x = [[O, O, O], [EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY , X]]


print(minimax(board))