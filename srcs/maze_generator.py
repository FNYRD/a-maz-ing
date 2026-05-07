#!/usr/bin/env python3
try:
    from typing import Tuple, List, Optional, Dict
    from collections.abc import Callable
    from collections import deque
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
        self.pattern: List[Tuple[int, int]] = []
        self.solution: List[Tuple[int, int]] = []

    def _pattern(self, offseth: int = 0, offsetw: int = 0,
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
            pattern_xy.append((start_for[1] - i, start_for[0] - 2))
            if i == 2:
                pattern_xy.append((start_to[1] + i, start_to[0] + 1))
                pattern_xy.append((start_to[1] - i, start_to[0]))
        pattern_xy.append((start_for[1], start_for[0] - 1))
        if entry_test in pattern_xy or exit_test in pattern_xy:
            if start_for[1] - 2 > 1 and direction != 2:
                self._pattern(offseth - 1, offsetw, 1)
            elif start_for[1] + 2 < self.height and direction != 1:
                self._pattern(offseth + 1, offsetw, 2)
            elif start_for[0] - 2 > 1 and direction != 4:
                self._pattern(offseth, offsetw - 1, 3)
            elif start_for[0] + 2 < self.width and direction != 3:
                self._pattern(offseth, offsetw + 1, 4)
            else:
                raise MazeTooSmallError("Maze's size is too small "
                                        "for displaying the 42 "
                                        "pattern")
            return
        for coordinate in pattern_xy:
            self.maze[coordinate[0]][coordinate[1]] = 42
        self.pattern = pattern_xy

    def _narrow_corridor(self, position: Tuple[int, int],
                         options:
                         List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        xp, yp = position
        lateral: bool = ((self.maze[yp][xp] & 0x2 == 0)
                         and (self.maze[yp][xp] & 0x8 == 0))
        vertical: bool = ((self.maze[yp][xp] & 0x1 == 0)
                          and (self.maze[yp][xp] & 0x4 == 0))
        to_return: List[Tuple[int, int]] = []
        for option in options:
            xo, yo = option
            if yp != yo:
                if (((self.maze[yo][xo] & 0x2 == 0)
                     and (self.maze[yo][xo] & 0x8 == 0))
                        and lateral):
                    pass
                else:
                    to_return.append(option)
            elif xp != xo:
                if (((self.maze[yo][xo] & 0x1 == 0)
                     and (self.maze[yo][xo] & 0x4 == 0))
                        and vertical):
                    pass
                else:
                    to_return.append(option)
        return to_return

    def _isvalid(self, position: Tuple[int, int],
                 flag: int = 0) -> List[Tuple[int, int]]:
        """This function will populate the options list with all
        the valid cells to access, adapted to each case."""
        x, y = position
        options: List[Tuple[int, int]] = []
        condition: Callable = lambda cell: cell != 42 if flag else cell == 0xf
        if ((0 <= y - 1) and (0 <= x <= self.width - 1)
                and (condition(self.maze[y - 1][x]))):
            options.append((x, y - 1))
        if ((self.height - 1 >= y + 1) and (0 <= x <= self.width - 1)
                and (condition(self.maze[y + 1][x]))):
            options.append((x, y + 1))
        if ((0 <= x - 1) and (0 <= y <= self.height - 1)
                and (condition(self.maze[y][x - 1]))):
            options.append((x - 1, y))
        if ((self.width - 1 >= x + 1) and (0 <= y <= self.height - 1)
                and (condition(self.maze[y][x + 1]))):
            options.append((x + 1, y))
        return self._narrow_corridor(position, options)

    def _opening_walls(self, current: Tuple[int, int],
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

    def _dfs(self) -> None:
        """This algorithm will open radomly the walls till
        find a path from entry to exit"""
        if len(self.maze) == 0:
            raise MazeNotExistsError(
                "You cannot creat a maze with dimensions 0x0")
        stack: List[Tuple[int, int]] = []
        next: Tuple[int, int] = (0, 0)
        current: Tuple[int, int] = self.entry
        options: List[Tuple[int, int]]
        spins: Callable = lambda: 1 if self.perfect else 2
        visited: set[Tuple[int, int]] = set()
        second_door: int = 0
        if self.seed is not None:
            random.seed(self.seed)
        for spin in range(spins()):
            if spin == 1:
                current = self.entry
                stack = []
                if self.seed is not None:
                    random.seed(self.seed + 5)
            limit: int = int((self.width * self.height) * 0.30)
            while True:
                options = self._isvalid(current, spin)
                if spin == 1:
                    visited.add(current)
                    options = [o for o in options if o not in visited]
                if current == self.exit:
                    options = []
                if len(options) > 0:
                    next = random.choice(options)
                    if spin == 1 and limit < 1:
                        self._opening_walls(current, next)
                        limit = int((self.width * self.height) * 0.50)
                    if spin == 0:
                        self._opening_walls(current, next)
                    stack.append(current)
                    current = next
                else:
                    if len(stack) == 0:
                        break
                    current = stack.pop()
                limit -= 1
        options = self._isvalid(self.exit, 1)
        if not self.perfect:
            for cell in options:
                second_door = self.maze[self.exit[1]][self.exit[0]]
                self._opening_walls(self.exit, cell)
                if second_door != self.maze[self.exit[1]][self.exit[0]]:
                    break
        for coordinate in self.pattern:
            self.maze[coordinate[0]][coordinate[1]] = 0xf

    def _bfs(self) -> List[Tuple[int, int]]:
        fifo: deque = deque()
        visited: set[Tuple[int, int]] = set()
        parents: Dict[Tuple[int, int], Tuple[int, int]] = {}
        fifo.append(self.entry)
        visited.add(self.entry)
        path: List[Tuple[int, int]] = []
        last: Tuple[int, int] = self.exit
        while True:
            x, y = fifo.popleft()
            if (x, y) == self.exit:
                path.append(self.exit)
                break

            if self.maze[y][x] & 0x2 == 0:
                if (x + 1, y) not in visited:
                    visited.add((x + 1, y))
                    fifo.append((x + 1, y))
                    parents[(x + 1, y)] = (x, y)

            if self.maze[y][x] & 0x8 == 0:
                if (x - 1, y) not in visited:
                    visited.add((x - 1, y))
                    fifo.append((x - 1, y))
                    parents[(x - 1, y)] = (x, y)

            if self.maze[y][x] & 0x1 == 0:
                if ((x, y - 1)) not in visited:
                    visited.add((x, y - 1))
                    fifo.append((x, y - 1))
                    parents[(x, y - 1)] = (x, y)

            if self.maze[y][x] & 0x4 == 0:
                if ((x, y + 1)) not in visited:
                    visited.add((x, y + 1))
                    fifo.append((x, y + 1))
                    parents[(x, y + 1)] = (x, y)

        while True:
            last = parents[last]
            path.append(last)
            if last == self.entry:
                break
        path.reverse()
        return path
    
    def _wilson(self) -> None:
        self._opening_walls(self.entry, random.choice(self._isvalid(self.entry)))
        current: Tuple[int, int] = self.entry
        next: Tuple[int, int]
        path: List[Tuple[int, int]] = [self.entry]
        index: int = 0
        fifteen: List[Tuple[int, int]] = [(0, 0)]
        while len(fifteen) > 0:
            fifteen = [(x, y) for y, fila in enumerate(self.maze)
                    for x, cell in enumerate(fila) if cell == 15]
            if len(fifteen) == 0:
                break
            options = self._isvalid(current, 1)
            if len(options) == 0:
                break
            next = random.choice(options)
            if next not in path:
                path.append(next)

                if ((self.maze[next[1]][next[0]] != 15) or
                    (next == self.exit)):
                    for i in range(len(path) - 1):
                        self._opening_walls(path[i],path[i + 1])
                    path = []
                    if len(fifteen) == 0:
                        break
                    current = random.choice(fifteen)
                    path.append(current)
                else:
                    current = next
                    
            else:
                index = path.index(next)
                path = path[0:index + 1]
                current = path[len(path) - 1]


    def complying(self) -> None:
        fifo: deque = deque()
        visited: set[Tuple[int, int]] = set()
        fifo.append(self.entry)
        visited.add(self.entry)
        e: int = 0
        v: int = 0
        while len(fifo) > 0:
            x, y = fifo.popleft()

            if self.maze[y][x] & 0x2 == 0:
                if (x + 1, y) not in visited:
                    visited.add((x + 1, y))
                    fifo.append((x + 1, y))
                e += 1

            if self.maze[y][x] & 0x8 == 0:
                if (x - 1, y) not in visited:
                    visited.add((x - 1, y))
                    fifo.append((x - 1, y))
                e += 1

            if self.maze[y][x] & 0x1 == 0:
                if ((x, y - 1)) not in visited:
                    visited.add((x, y - 1))
                    fifo.append((x, y - 1))
                e += 1

            if self.maze[y][x] & 0x4 == 0:
                if ((x, y + 1)) not in visited:
                    visited.add((x, y + 1))
                    fifo.append((x, y + 1))
                e += 1
        e = e // 2
        v = len(visited) - 1
        print(f"Conexo = {v == ((self.height * self.width) - 16)}")
        print(
            f"Perfect Argument = {self.perfect}\nPerfect validator = {e == v}")
        print(f"Comply = {self.perfect == (e == v)}")

    def generate(self) -> None:
        self.maze = [[0xf for _ in range(self.width)]
                     for _ in range(self.height)]
        try:
            self._pattern()
        except MazeTooSmallError as e:
            print(e)
        # self._dfs()
        self._wilson()
        # self.solution = self._bfs()
        # self.complying()


def main() -> None:
    maze = MazeGenerator(11, 11, (0, 0), (9, 9), True)
    try:
        maze.generate()
    except MazeTooSmallError as e:
        print(f"Error {e}")


if __name__ == "__main__":
    main()


# POR HACER:

# Hacer que el imperfecto no quede tan agujereado DONE

# verificar y demostrar que el laberinto es perfecto o imperfecto

# Verificar que sea conexo Creando un BFS que verifique el acceso a todas
# las celdas
# Que sea E = V - 1
# E = Verificar todos los bits de una celda y lo que no este en cero se suma
# V = width * height - 1

# Crear el algoritmo Wilson
