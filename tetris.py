import os
import time
import random
from threading import Thread
import sys
import termios
import tty

class Tile:
    __PREDEFINED_SHAPES = [
        [
            [1,1],
            [1,1]
        ],
        [
            [1],
            [1],
            [1],
            [1],
        ],
        [
            [0,1,1],
            [1,1,0]
        ],
        [
            [1,1,0],
            [0,1,1]
        ],
        [
            [1,0],
            [1,0],
            [1,1],
        ],
        [
            [0,1],
            [0,1],
            [1,1]
        ],
        [
            [1,1,1],
            [0,1,0]
        ]
        
    ]
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
        
    def is_edge_cell(self, x, y):
        if self.shape[y][x] != 1:
            return False
        if y == self.height - 1:
            return True
        if self.shape[y+1][x] != 1:
            return True
        return False
    
    def move_left(self):
        self.x -= 1
    
    def move_right(self):
        self.x += 1
        
    @staticmethod
    def random():
        random_shape = random.choice(Tile.__PREDEFINED_SHAPES)
        return Tile(random_shape)
    

class Board:
    EMPTY = "⬜"
    FULL = "⬛"
    def __init__(self, height, width):
        self.board = [[Board.EMPTY for _ in range(width)] for _ in range(height)]
        self.width = width
        self.height = height
        self.add_new_falling_tile()
        self.start_input_thread()
        self.end_game = False
        
    def start_input_thread(self):
        input_thread = Thread(target=self.read_input)
        input_thread.start()
        
    def read_input(self):
        K_RIGHT = b'\x1b[C'
        K_LEFT  = b'\x1b[D'
        for key in self.read_keys():
            if key == K_LEFT:
                self.clear_falling_tile()
                self.falling_tile.move_left()
            elif key == K_RIGHT:
                self.clear_falling_tile()
                self.falling_tile.move_right()
        
        
    def read_keys(self):
        stdin = sys.stdin.fileno()
        tattr = termios.tcgetattr(stdin)
        try:
            tty.setcbreak(stdin, termios.TCSANOW)
            while True:
                yield sys.stdin.buffer.read1()
        except KeyboardInterrupt:
            yield None
        finally:
            termios.tcsetattr(stdin, termios.TCSANOW, tattr)
        
    
    def print(self):
        os.system("clear")
        for row in self.board:
            for cell in row:
                print(cell, end="")
            print("")
            
    def is_cell_empty(self, x, y):
        return self.board[y][x] == Board.EMPTY
    
    def is_cell_full(self, x, y):
        return not self.is_cell_empty(x, y)
            
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
    
    def can_falling_tile_move(self):
        for y in range(self.falling_tile.height):
            for x in range(self.falling_tile.width):
                board_x, board_y = self.falling_tile.get_coord_in_board(x, y)
                if board_y == self.height - 1:
                    return False
                if self.falling_tile.is_edge_cell(x, y) and self.is_cell_full(board_x, board_y + 1):
                    return False
        return True
    
    def add_new_falling_tile(self):
        random_tile = Tile.random()
        tile_x = self.width // 2  - random_tile.width // 2
        random_tile.x = tile_x
        self.falling_tile = random_tile
            
    
    def play_one_step(self):
        if self.can_falling_tile_move():
            self.clear_falling_tile()
            self.falling_tile.move_down()
        else:
            self.add_new_falling_tile()
        self.show_falling_tile()
    
    

    


board = Board(20, 10)
while True:
    board.play_one_step()
    board.print()
    time.sleep(0.5)