#!/usr/bin/env python3
import sys
import curses
import subprocess

GAMES = [('Snake','snake.py'), ('Tetris','tetris.py')]

MENU = "Choose a game:\n\n"
for i,(n,f) in enumerate(GAMES,1):
    MENU += f"{i}. {n}\n"
MENU += "\nq. Quit\n"


def main():
    print(MENU)
    choice = input('Enter choice: ').strip()
    if choice.lower()=='q':
        sys.exit(0)
    try:
        i = int(choice)-1
        if 0 <= i < len(GAMES):
            script = GAMES[i][1]
            subprocess.run(['python3', script])
    except Exception as e:
        print('Invalid choice')

if __name__=='__main__':
    main()
