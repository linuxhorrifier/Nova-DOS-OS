#!/usr/bin/env python3
import curses
import random
import time

W = 40
H = 20

KEYS = {
    curses.KEY_UP: ( -1, 0),
    curses.KEY_DOWN: ( 1, 0),
    curses.KEY_LEFT: ( 0,-1),
    curses.KEY_RIGHT:( 0, 1),
    ord('w'):(-1,0), ord('s'):(1,0), ord('a'):(0,-1), ord('d'):(0,1)
}


def place_food(snake):
    while True:
        y = random.randint(1,H)
        x = random.randint(1,W)
        if (y,x) not in snake:
            return (y,x)


def draw(win, snake, food, score):
    win.clear()
    win.border()
    win.addstr(0,2,f" Score: {score} ")
    for i,(y,x) in enumerate(snake):
        ch = 'O' if i==0 else 'o'
        try:
            win.addch(y, x, ch)
        except curses.error:
            pass
    fy,fx = food
    win.addch(fy, fx, '*')
    win.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.keypad(1)
    win = curses.newwin(H+2, W+2, 0, 0)
    win.keypad(1)
    win.nodelay(1)

    mid = (H//2, W//2)
    snake = [mid, (mid[0], mid[1]-1), (mid[0], mid[1]-2)]
    direction = (0,1)
    food = place_food(snake)
    score = 0
    speed = 0.12
    paused = False

    draw(win, snake, food, score)
    while True:
        ch = win.getch()
        if ch != -1:
            if ch in (ord('q'), 27):
                break
            if ch in (ord('p'),):
                paused = not paused
            if ch in KEYS and not paused:
                nd = KEYS[ch]
                # prevent reverse
                if (nd[0] != -direction[0] or nd[1] != -direction[1]):
                    direction = nd
        if paused:
            time.sleep(0.05)
            continue
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        # collisions
        if head[0] <=0 or head[0] >= H+1 or head[1] <=0 or head[1] >= W+1 or head in snake:
            msg = f" GAME OVER - Score: {score} (press q) "
            win.addstr(H//2, max(2,(W//2)-len(msg)//2), msg)
            win.nodelay(0)
            while True:
                c = win.getch()
                if c in (ord('q'), 27):
                    return
            break
        snake.insert(0, head)
        if head == food:
            score += 1
            food = place_food(snake)
            speed = max(0.03, speed * 0.97)
        else:
            snake.pop()
        draw(win, snake, food, score)
        time.sleep(speed)


if __name__ == '__main__':
    curses.wrapper(main)
