import os
import time

class Tile:
    def __init__(self, shape):
        self.shape = shape
        self.width = len(shape[0])
        self.height = len(shape)
        self.x = 0
        self.y = 0
        
    def get_coord_in_board(self, x, y):
        return self.x + x, self.y + y
    
    def move_down(self):
        self.y += 1
    

class Board:
    EMPTY = "⬜"
    FULL = "⬛"
    def __init__(self, height, width):
        self.board = [[Board.EMPTY for _ in range(width)] for _ in range(height)]
        self.falling_tile: Tile = None
    
    def print(self):
        os.system("clear")
        for row in self.board:
            for cell in row:
                print(cell, end="")
            print("")
            
    def clear_falling_tile(self):
        self.__fill_falling_tile_in_board(Board.EMPTY)
    
    def show_falling_tile(self):
        self.__fill_falling_tile_in_board(Board.FULL)
            
    def __fill_falling_tile_in_board(self, char):
        for y in range(self.falling_tile.height):
            for x in range(self.falling_tile.width):
                board_x, board_y = self.falling_tile.get_coord_in_board(x, y)
                if self.falling_tile.shape[y][x] == 1:
                    self.board[board_y][board_x] = char
    
    def play_one_step(self):
        board.clear_falling_tile()
        board.falling_tile.move_down()
        board.show_falling_tile()
    
    

    


board = Board(20, 10)
tile = Tile([
    [0,1,0],
    [1,1,1]
])
tile.x = 2
tile.y = 1
board.falling_tile = tile

while True:
    board.play_one_step()
    board.print()
    time.sleep(0.5)
    