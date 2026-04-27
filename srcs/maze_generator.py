try:
    from typing import Tuple, List, Optional
except ImportError as e:
    print(f"An error happened importing the modules\n{e}")


class MazeTooSmallError(Exception):
    pass


class MazeGenerator:
    """This constructor sets the arguments for the maze creation"""
    def __init__(self, width: int, height: int, entry: Tuple[int, int],
                 exit: Tuple[int, int], perfect: bool,
                 seed: Optional[int] = None) -> None:
        self.width: int = width
        self.height: int = height
        self.entry: Tuple[int, int] = entry
        self.exit: Tuple[int, int] = exit
        self.perfect: bool = perfect
        self.seed: Optional[int] = seed
        self.maze = [[0xf for _ in range(self.width)]
                     for _ in range(self.height)]

    def show(self) -> List[List[int]]:
        """This function shows the maze after setting
         the entry and exit position"""
        self.maze[self.entry[1]][self.entry[0]] = 5
        self.maze[self.exit[1]][self.exit[0]] = 9
        return self.maze

    def pattern(self, offseth: int = 0, offsetw: int = 0,
                direction: int = 0) -> None:
        """This function change the cell's value to 42 to
        print the 42 pattern"""
        if self.width <= 10 >= self.height:
            raise MazeTooSmallError("Maze's size is too small "
                                    "for displaying the 42 "
                                    "pattern")
        start_for: Tuple[int, int] = (((self.width // 2) - 1) + offsetw,
                                      (self.height // 2) + offseth)
        start_to: Tuple[int, int] = (((self.width // 2) + 1) + offsetw,
                                     (self.height // 2) + offseth)
        entry_test: Tuple[int, int] = (self.entry[1], self.entry[0])
        exit_test: Tuple[int, int] = (self.exit[1], self.exit[0])
        pattern_xy: List[Tuple[int, int]] = []
        for i in range(3):
            pattern_xy.append((start_for[1] + i, start_for[0]))
            pattern_xy.append((start_to[1] + i, start_to[0]))
            pattern_xy.append((start_to[1] - i, start_to[0] + 1))
            pattern_xy.append((start_for[1] - i, start_for[0] - 1))
            if i == 2:
                pattern_xy.append((start_to[1] + i, start_to[0] + 1))
                pattern_xy.append((start_to[1] - i, start_to[0]))
        if entry_test in pattern_xy or exit_test in pattern_xy:
            if start_for[1] - 2 >= 0 and direction != 2:
                self.pattern(offseth - 1, 0, 1)
            elif start_for[1] + 2 <= self.height and direction != 1:
                self.pattern(offseth + 1, 0, 2)
            elif start_for[0] - 2 >= 0 and direction != 4:
                self.pattern(0, offsetw - 1, 3)
            elif start_for[0] + 2 <= self.width and direction != 3:
                self.pattern(0, offsetw + 1, 4)
            else:
                raise MazeTooSmallError("Maze's size is too small "
                                        "for displaying the 42 "
                                        "pattern")
            return
        for coordinate in pattern_xy:
            self.maze[coordinate[0]][coordinate[1]] = 42
        print(pattern_xy)
