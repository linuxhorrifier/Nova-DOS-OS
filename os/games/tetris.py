#!/usr/bin/env python3
import curses
import random
import time

W = 10
H = 20
TICK = 0.5

SHAPES = [
    # I
    [[(0,1),(0,0),(0,2),(0,3)], [( -1,2),(0,2),(1,2),(2,2)]],
    # O
    [[(0,0),(0,1),(1,0),(1,1)]],
    # T
    [[(0,1),(1,0),(1,1),(1,2)], [(0,1),(1,1),(1,2),(2,1)], [(1,0),(1,1),(1,2),(2,1)], [(0,1),(1,0),(1,1),(2,1)]],
    # L
    [[(0,2),(1,0),(1,1),(1,2)], [(0,1),(1,1),(2,1),(2,2)], [(1,0),(1,1),(1,2),(2,0)], [(0,0),(0,1),(1,1),(2,1)]],
    # J
    [[(0,0),(1,0),(1,1),(1,2)], [(0,1),(1,1),(2,1),(2,0)], [(1,0),(1,1),(1,2),(2,2)], [(0,2),(0,1),(1,1),(2,1)]],
    # S
    [[(0,1),(0,2),(1,0),(1,1)], [(0,1),(1,1),(1,2),(2,2)]],
    # Z
    [[(0,0),(0,1),(1,1),(1,2)], [(0,2),(1,2),(1,1),(2,1)]]
]

COLS = [1,2,3,4,5,6,7]

class Piece:
    def __init__(self, shape):
        self.shape = shape
        self.rot = 0
        self.blocks = shape[self.rot]
        self.y = 0
        self.x = W//2 - 2
        self.color = random.choice(COLS)
    def rotate(self):
        self.rot = (self.rot + 1) % len(self.shape)
        self.blocks = self.shape[self.rot]


def create_board():
    return [[0]*W for _ in range(H)]


def valid(board, piece, dy=0, dx=0):
    for by,bx in piece.blocks:
        y = piece.y + by + dy
        x = piece.x + bx + dx
        if x < 0 or x >= W or y >= H:
            return False
        if y >= 0 and board[y][x]:
            return False
    return True


def lock(board, piece):
    for by,bx in piece.blocks:
        y = piece.y + by
        x = piece.x + bx
        if 0 <= y < H and 0 <= x < W:
            board[y][x] = piece.color


def clear_lines(board):
    new = [row for row in board if any(v==0 for v in row)]
    cleared = H - len(new)
    for _ in range(cleared):
        new.insert(0,[0]*W)
    return new, cleared


def draw(win, board, piece, score, next_shape):
    win.clear()
    win.border()
    win.addstr(0,2,f" Score: {score} ")
    for y in range(H):
        for x in range(W):
            ch = ' ' if board[y][x]==0 else '#'
            if board[y][x]:
                win.addch(1+y,1+x,ch)
            else:
                win.addch(1+y,1+x,ch)
    # piece
    for by,bx in piece.blocks:
        y = piece.y + by
        x = piece.x + bx
        if y>=0:
            try:
                win.addch(1+y,1+x,'#')
            except curses.error:
                pass
    # next
    win.addstr(1, W+3, "Next:")
    for by,bx in next_shape[0]:
        win.addch(3+by, W+4+bx, '#')
    win.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.keypad(1)
    win = curses.newwin(H+2, W+2+8, 0, 0)
    win.keypad(1)
    board = create_board()
    piece = Piece(random.choice(SHAPES))
    next_piece_shape = random.choice(SHAPES)
    score = 0
    drop_timer = time.time()
    speed = TICK

    while True:
        ch = win.getch()
        if ch in (ord('q'), 27):
            break
        if ch == curses.KEY_LEFT and valid(board,piece,dx=-1):
            piece.x -=1
        if ch == curses.KEY_RIGHT and valid(board,piece,dx=1):
            piece.x +=1
        if ch == curses.KEY_DOWN and valid(board,piece,dy=1):
            piece.y +=1
            drop_timer = time.time()
        if ch == curses.KEY_UP:
            # rotate
            old_rot = piece.rot
            piece.rotate()
            if not valid(board,piece):
                piece.rot = old_rot
                piece.blocks = piece.shape[piece.rot]
        if time.time() - drop_timer > speed:
            if valid(board,piece,dy=1):
                piece.y +=1
            else:
                lock(board,piece)
                board, cleared = clear_lines(board)
                score += cleared * 100
                piece = Piece(next_piece_shape)
                next_piece_shape = random.choice(SHAPES)
                if not valid(board,piece):
                    win.addstr(H//2, 2, f" GAME OVER - Score: {score} (q to quit) ")
                    win.nodelay(0)
                    while True:
                        c = win.getch()
                        if c in (ord('q'), 27):
                            return
            drop_timer = time.time()
        draw(win, board, piece, score, next_piece_shape)
        time.sleep(0.02)

if __name__ == '__main__':
    curses.wrapper(main)
