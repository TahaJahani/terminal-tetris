import os
import time
import random
from threading import Thread
import sys
import termios
import tty
import math

class Char:
    EMPTY = "⬜"
    FULL = "🟥🟨🟪🟩🟦🟫🟧"
    
    @staticmethod
    def is_full(char):
        return char in Char.FULL

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
    def __init__(self, shape, color):
        self.shape = shape
        self.width = len(shape[0])
        self.height = len(shape)
        self.x = 0
        self.y = 0
        self.color = color
        
    def get_coord_in_board(self, x, y):
        return self.x + x, self.y + y
    
    def is_board_coord_in_this_tile(self, x, y):
        min_x = self.x
        max_x = self.x + self.width
        min_y = self.y
        max_y = self.y + self.height
        return min_x <= x < max_x and min_y <= y < max_y
    
    def get_rotated_shape(self):
        new_width = self.get_rotated_width()
        new_height = self.get_rotated_height()
        new_shape = [[0] * new_width for _ in range(new_height)]

        for y in range(self.height):
            for x in range(self.width):
                new_shape[x][self.height - y - 1] = self.shape[y][x]
        return new_shape
    
    def get_rotated_width(self):
        return self.height
    
    def get_rotated_height(self):
        return self.width
    
    def get_rotated_x(self):
        delta_x = round((self.width - self.height) / 2)
        return self.x + delta_x
    
    def rotate(self):
        new_width = self.get_rotated_width()
        new_height = self.get_rotated_height()
        self.x = self.get_rotated_x()
        self.shape = self.get_rotated_shape()
        self.width = new_width
        self.height = new_height
    
    def move_down(self):
        self.y += 1
        
    def is_bottom_edge_cell(self, x, y):
        if self.shape[y][x] != 1:
            return False
        if y == self.height - 1:
            return True
        if self.shape[y+1][x] != 1:
            return True
        return False
    
    def is_left_edge_cell(self, x, y):
        if self.shape[y][x] != 1:
            return False
        if x == 0:
            return True
        if self.shape[y][x-1] != 1:
            return True
        return False
    
    def is_right_edge_cell(self, x, y):
        if self.shape[y][x] != 1:
            return False
        if x == self.width - 1:
            return True
        if self.shape[y][x+1] != 1:
            return True
        return False
    
    def move_left(self):
        self.x -= 1
    
    def move_right(self):
        self.x += 1
        
    @staticmethod
    def random():
        random_index = random.randint(0, len(Tile.__PREDEFINED_SHAPES) - 1)
        color = Char.FULL[random_index]
        shape = Tile.__PREDEFINED_SHAPES[random_index]
        return Tile(shape, color)
    

class Board:
    def __init__(self, height, width):
        self.board = [[Char.EMPTY for _ in range(width)] for _ in range(height)]
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
        K_UP  = b'\x1b[A'
        for key in self.read_keys():
            if key == K_LEFT:
                if self.can_falling_tile_move_left():
                    self.clear_falling_tile()
                    self.falling_tile.move_left()
                    self.show_falling_tile()
            elif key == K_RIGHT:
                if self.can_falling_tile_move_right():
                    self.clear_falling_tile()
                    self.falling_tile.move_right()
                    self.show_falling_tile()
            elif key == K_UP:
                if self.can_falling_tile_rotate():
                    self.clear_falling_tile()
                    self.falling_tile.rotate()
                    self.show_falling_tile()
        
        
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
        return self.board[y][x] == Char.EMPTY
    
    def is_cell_full(self, x, y):
        return not self.is_cell_empty(x, y)
            
    def clear_falling_tile(self):
        self.__fill_falling_tile_in_board(Char.EMPTY)
    
    def show_falling_tile(self):
        self.__fill_falling_tile_in_board(self.falling_tile.color)
            
    def __fill_falling_tile_in_board(self, char):
        for y in range(self.falling_tile.height):
            for x in range(self.falling_tile.width):
                board_x, board_y = self.falling_tile.get_coord_in_board(x, y)
                if self.falling_tile.shape[y][x] == 1:
                    self.board[board_y][board_x] = char
    
    def can_falling_tile_move_down(self):
        for y in range(self.falling_tile.height):
            for x in range(self.falling_tile.width):
                board_x, board_y = self.falling_tile.get_coord_in_board(x, y)
                if board_y == self.height - 1:
                    return False
                if self.falling_tile.is_bottom_edge_cell(x, y) and self.is_cell_full(board_x, board_y + 1):
                    return False
        return True
    
    def can_falling_tile_move_left(self):
        for y in range(self.falling_tile.height):
            for x in range(self.falling_tile.width):
                board_x, board_y = self.falling_tile.get_coord_in_board(x, y)
                if board_x == 0:
                    return False
                if self.falling_tile.is_left_edge_cell(x, y) and self.is_cell_full(board_x - 1, board_y):
                    return False
        return True
    
    def can_falling_tile_move_right(self):
        for y in range(self.falling_tile.height):
            for x in range(self.falling_tile.width):
                board_x, board_y = self.falling_tile.get_coord_in_board(x, y)
                if board_x == self.width - 1:
                    return False
                if self.falling_tile.is_right_edge_cell(x, y) and self.is_cell_full(board_x + 1, board_y):
                    return False
        return True
    
    def can_falling_tile_rotate(self):
        new_shape = self.falling_tile.get_rotated_shape()
        new_x = self.falling_tile.get_rotated_x()
        new_y = self.falling_tile.y
        new_width = self.falling_tile.get_rotated_width()
        new_height = self.falling_tile.get_rotated_height()
        if new_x < 0 or new_x + new_width > self.width or new_y + new_height > self.height:
            return False
        for y in range(new_height):
            for x in range(new_width):
                board_y = new_y + y
                board_x = new_x + x
                if new_shape[y][x] == 1 and self.is_cell_full(board_x, board_y) and not self.falling_tile.is_board_coord_in_this_tile(board_x, board_y):
                            return False
        return True
        
    
    def delete_row(self, row_index):
        for x in range(self.width):
            self.board[row_index][x] = Char.EMPTY
            
    def move_all_full_cells_down(self, row_index):
        for y in range(row_index, 0, -1):
            for x in range(self.width):
                if not self.falling_tile.is_board_coord_in_this_tile(x, y):
                    self.board[y-1][x] = self.board[y][x]
                    self.board[y][x] = Char.EMPTY
                    
    def get_full_rows(self):
        full_rows = []
        for y in range(self.height):
            is_full = True
            for x in range(self.width):
                is_full &= self.is_cell_full(x, y)
            if is_full:
                full_rows.append(y)
        return full_rows
        
    
    def add_new_falling_tile(self):
        random_tile = Tile.random()
        tile_x = self.width // 2  - random_tile.width // 2
        random_tile.x = tile_x
        self.falling_tile = random_tile
            
    
    def play_one_step(self):
        if self.can_falling_tile_move_down():
            self.clear_falling_tile()
            self.falling_tile.move_down()
        else:
            self.add_new_falling_tile()
        self.show_falling_tile()
        full_rows = self.get_full_rows()
        for row in full_rows:
            self.delete_row(row)
            self.move_all_full_cells_down(row)


board = Board(20, 10)
while True:
    board.play_one_step()
    board.print()
    time.sleep(0.5)

# tile = Tile([
#     [0,1,0],
#     [1,1,1]
# ], "")
# tile.rotate()
# for y in range(tile.height):
#     for x in range(tile.width):
#         print(tile.shape[y][x], end="")
#     print("")


# board = Board(20, 10)
# board.board[19][9] = Char.FULL[0]
# board.board[18][8] = Char.FULL[0]
# board.board[19][8] = Char.FULL[0]
# board.board[18][9] = Char.FULL[0]
# tile = Tile([
#     [1,1,1],
#     [0,1,0],
# ], Char.FULL[1])
# tile.x = 6
# tile.y = 17
# board.falling_tile = tile
# board.show_falling_tile()
# while True:
#     board.print()
#     time.sleep(0.5)