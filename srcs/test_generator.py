#!/usr/bin/env python3
try:
    from maze_generator import MazeGenerator, MazeTooSmallError
    from typing import List
except ImportError as e:
    print(f"An error happened importing the modules\n{e}")

maze = MazeGenerator(6,6, (0, 1), (4, 2), False)

try:
    maze.pattern()
    maze: List[List[int]] = maze.show()
    lines: int = len(maze)
    for i in range(lines):
        print(maze[i])
except MazeTooSmallError as e:
    print(f"Error {e}")