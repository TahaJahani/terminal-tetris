import os
import time

class Tile:
    def __init__(self, shape):
        self.shape = shape
        self.width = len(shape[0])
        self.height = len(shape)
        self.x = 0
        self.y = 0
    

class Board:
    def __init__(self, height, width):
        self.board = [[Board.EMPTY for _ in range(width)] for _ in range(height)]
        self.falling_tile: Tile = None
    
    def print(self):
        os.system("clear")
        for row in self.board:
            for cell in row:
                print(cell, end="")
            print("")
    
    

    


board = Board(20, 10)
board.print()
    