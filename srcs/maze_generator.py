try:
    from typing import Tuple, List, Optional
    import random
except ImportError as e:
    print(f"An error happened importing the modules\n{e}")


class MazeTooSmallError(Exception):
    pass


class MazeNotExistsError(Exception):
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

    def __isvalid(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        x, y = position
        options: List[Tuple[int, int]] = []
        if 0 < y - 1 and 0 < x <= self.width - 2 and self.maze[y - 1][x] == 0xf:
            options.append((x, y - 1))
        if self.height - 1 > y + 1 and 0 < x <= self.width - 2 and self.maze[y + 1][x] == 0xf:
            options.append((x, y + 1))
        if 0 < x - 1 and 0 < y <= self.height - 2 and self.maze[y][x - 1] == 0xf:
            options.append((x - 1, y))
        if self.width - 1 > x + 1 and 0 < y <= self.height - 2 and self.maze[y][x + 1] == 0xf:
            options.append((x + 1, y))
        return options

    def __opening_walls(self, current: Tuple[int, int],
                        next: Tuple[int, int]) -> None:
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
        while True:
            options = self.__isvalid(current)
            if len(options) > 0:
                next = random.choice(options)
                self.__opening_walls(current, next)
                stack.append(current)
                current = next
                if next == self.exit:
                    # BORRAR, ES SOLO PARA VER SI LLEGA A LA SALIDA
                    self.maze[self.exit[1]][self.exit[0]] = 100
                    break
            else:
                if len(stack) == 0:
                    break
                current = stack.pop()

# FALTA:
# SEED, PERFECT Y EL ANCHO DE LOS PASILLOS
