try:
    from typing import Tuple, List, Optional
    from collections.abc import Callable
    import random
    from exceptions import MazeNotExistsError, MazeTooSmallError
except ImportError as e:
    print(f"An error happened importing the modules\n{e}")


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
        self.maze: List[List[int]] = []

    def __pattern(self, offseth: int = 0, offsetw: int = 0,
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
            if start_for[1] - 2 > 1 and direction != 2:
                self.__pattern(offseth - 1, offsetw, 1)
            elif start_for[1] + 2 < self.height and direction != 1:
                self.__pattern(offseth + 1, offsetw, 2)
            elif start_for[0] - 2 > 1 and direction != 4:
                self.__pattern(offseth, offsetw - 1, 3)
            elif start_for[0] + 2 < self.width and direction != 3:
                self.__pattern(offseth, offsetw + 1, 4)
            else:
                raise MazeTooSmallError("Maze's size is too small "
                                        "for displaying the 42 "
                                        "pattern")
            return
        for coordinate in pattern_xy:
            self.maze[coordinate[0]][coordinate[1]] = 42

    def generate(self) -> None:
        self.maze = [[0xf for _ in range(self.width)]
                     for _ in range(self.height)]
        self.__pattern()

    def __isvalid(self, position: Tuple[int, int],
                  flag: int = 0) -> List[Tuple[int, int]]:
        """This function will populate the options list with all
        the valid cells to access, adapted to each case."""
        x, y = position
        options: List[Tuple[int, int]] = []
        condition: Callable = lambda cell: cell != 42 if flag else cell == 0xf
        if position == (0, 0):
            options.append((1, 1))
        if position == (self.width - 1, self.height - 1):
            options.append((self.width - 2, self.height - 2))
        if position == (self.width - 1, 0):
            options.append((self.width - 2, 1))
        if position == (0, self.height - 1):
            options.append((1, self.height - 2))
        if ((0 < y - 1) and (0 < x <= self.width - 2)
                and (condition(self.maze[y - 1][x]))):
            options.append((x, y - 1))
        if ((self.height - 1 > y + 1) and (0 < x <= self.width - 2)
                and (condition(self.maze[y + 1][x]))):
            options.append((x, y + 1))
        if ((0 < x - 1) and (0 < y <= self.height - 2)
                and (condition(self.maze[y][x - 1]))):
            options.append((x - 1, y))
        if ((self.width - 1 > x + 1) and (0 < y <= self.height - 2)
                and (condition(self.maze[y][x + 1]))):
            options.append((x + 1, y))
        return options

    def __opening_walls(self, current: Tuple[int, int],
                        next: Tuple[int, int]) -> None:
        """This function will calculate which wall must be open depending
        on the move between the cells."""
        cx, cy = current
        nx, ny = next
        if cy != ny:
            if cy < ny:
                self.maze[cy][cx] &= ~0x4
                self.maze[ny][nx] &= ~0x1
            elif cy > ny:
                self.maze[ny][nx] &= ~0x4
                self.maze[cy][cx] &= ~0x1
            return
        if cx < nx:
            self.maze[cy][cx] &= ~0x2
            self.maze[ny][nx] &= ~0x8
        elif cx > nx:
            self.maze[ny][nx] &= ~0x2
            self.maze[cy][cx] &= ~0x8

    def dfs(self) -> None:
        """This algorithm will open radomly the walls till
        find a path from entry to exit"""
        if len(self.maze) == 0:
            raise MazeNotExistsError(
                "You cannot creat a maze with dimensions 0x0")
        stack: List[Tuple[int, int]] = []
        next: Tuple[int, int] = (0, 0)
        current: Tuple[int, int] = self.entry
        options: List[Tuple[int, int]]
        exit_cell: Tuple[int, int] = (0, 0)
        spins: Callable = lambda: 1 if self.perfect else 2
        if self.exit in {(0, 0), (self.width - 1, self.height - 1),
                         (self.width - 1, 0), (0, self.height - 1)}:
            exit_cell = self.__isvalid(self.exit)[0]
        else:
            exit_cell = self.exit
        if self.seed is not None:
            random.seed(self.seed)
        for spin in range(spins()):
            if spin == 1 and self.seed:
                random.seed(self.seed + 5)
                current = self.entry
            while True:
                options = self.__isvalid(current, spin)
                if len(options) > 0:
                    next = random.choice(options)
                    self.__opening_walls(current, next)
                    stack.append(current)
                    current = next
                    if next == exit_cell:
                        # BORRAR, ES SOLO PARA VER SI LLEGA A LA SALIDA
                        self.maze[exit_cell[1]][exit_cell[0]] = 100
                        break
                else:
                    if len(stack) == 0:
                        break
                    current = stack.pop()

# FALTA:
# EL ANCHO DE LOS PASILLOS
