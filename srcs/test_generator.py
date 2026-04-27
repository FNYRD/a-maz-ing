#!/usr/bin/env python3
try:
    from maze_generator import MazeGenerator, MazeTooSmallError
    from typing import List
except ImportError as e:
    print(f"An error happened importing the modules\n{e}")

maze = MazeGenerator(10, 10, (0, 7), (6, 5), False)

try:
    maze.pattern()
    maze: List[List[int]] = maze.show()
    lines: int = len(maze)
    for i in range(lines):
        print(maze[i])
except MazeTooSmallError as e:
    print(f"Error {e}")









    # def pattern(self) -> None:
    #     """This function change the cell's value to 42 to print the 42 pattern"""
    #     if self.width <= 5 >= self.height:
            # raise MazeTooSmallError("Maze's size is too small "
            #                         "for displaying the 42 pattern")
    #     start_for: Tuple[int, int] = (((self.width // 2) - 1), (self.height // 2))
    #     start_to: Tuple[int, int] = (((self.width // 2) + 1), (self.height // 2))
    #     pattern: List[Tuple[int, int]] = []
    #     for i in range(3):
    #         self.maze[start_for[1] + i][start_for[0]] = 42
    #         self.maze[start_to[1] + i][start_to[0]] = 42
    #         self.maze[start_to[1] - i][start_to[0] + 1] = 42
    #         if i == 2:
    #             self.maze[start_to[1] + i][start_to[0] + 1] = 42
    #             self.maze[start_to[1] - i][start_to[0]] = 42
    #     for i in range(2):
    #         if i == 0:
    #             self.maze[start_for[1] - i - 1][start_for[0]] = 42
    #         self.maze[start_for[1] - i - 1][start_for[0] - 1] = 42