#!/usr/bin/env python3
try:
    from typing import Tuple, List, Optional, Dict
    from collections.abc import Callable
    from collections import deque
    import random
except ImportError as e:
    print(f"An error happened importing the modules\n{e}")


class MazeTooSmallError(Exception):
    """Exception raised when the maze is too small for the 42 pattern, or when
    entry/exit positions leave no valid placement for it.

    Attributes
    ----------
    msg : str
        Default error message describing the size constraint.
    """

    msg: str = ("Maze's size is too small "
                "for displaying the 42 "
                "pattern")


class MazeNotExistsError(Exception):
    """Exception raised when a maze operation is
    attempted before the maze is generated.

    Attributes
    ----------
    msg : str
        Default error message indicating the maze does not exist yet.
    """

    msg: str = ("You're trying to excute functions "
                "realted to a non-existent Maze")


class MazeGenerator:
    """Generate mazes using DFS or Wilson's algorithm.

    Supports perfect and imperfect mazes, optional seeding for reproducibility,
    and embeds a hidden '42' pattern in the maze grid.

    Attributes
    ----------
    width : int
        Number of columns in the maze.
    height : int
        Number of rows in the maze.
    entry : Tuple[int, int]
        (x, y) coordinates of the maze entry point.
    exit : Tuple[int, int]
        (x, y) coordinates of the maze exit point.
    perfect : bool
        Whether the maze is perfect (no loops, single solution).
    seed : int, optional
        Seed for the random number generator.
    maze : List[List[int]]
        2D grid representing the maze state.
    pattern : List[Tuple[int, int]]
        Coordinates of the 42 pattern cells.
    solution : List[Tuple[int, int]]
        Shortest path from entry to exit, computed by the BFS algorithm.
    alt_algorithm : bool, optional
        If True, uses Wilson's algorithm instead of DFS.
    """

    def __init__(self, width: int, height: int, entry: Tuple[int, int],
                 exit: Tuple[int, int], perfect: bool,
                 seed: Optional[int] = None,
                 alt_algorithm: Optional[bool] = False) -> None:
        """Initialize maze dimensions, entry/exit points,
        and generation options."""
        self.width: int = width
        self.height: int = height
        self.entry: Tuple[int, int] = entry
        self.exit: Tuple[int, int] = exit
        self.perfect: bool = perfect
        self.seed: Optional[int] = seed
        self.maze: List[List[int]] = []
        self.pattern: List[Tuple[int, int]] = []
        self.solution: List[Tuple[int, int]] = []
        self.alt_algorithm: Optional[bool] = alt_algorithm

    def _pattern(self, offseth: int = 0, offsetw: int = 0,
                 direction: int = 0) -> None:
        """Embed the '42' pattern into the maze grid.

        Computes the pattern cell coordinates centered in the maze and adjusts
        placement if any cell overlaps with the entry or exit. Raises
        MazeTooSmallError if no valid position can be found.

        Parameters
        ----------
        offseth : int, optional
            Vertical offset applied to
            the pattern center, by default 0.
        offsetw : int, optional
            Horizontal offset applied to
            the pattern center, by default 0.
        direction : int, optional
            Tracks the last shift direction to
            avoid infinite recursion, by default 0.

        Raises
        ------
        MazeTooSmallError
            If the maze is too small or no valid pattern placement exists.
        """
        if self.width <= 10 >= self.height:
            raise MazeTooSmallError("Maze's size is too small "
                                    "for displaying the 42 "
                                    "pattern")
        start_for: Tuple[int, int] = (((self.width // 2) - 1) + offsetw,
                                      (self.height // 2) + offseth)
        start_to: Tuple[int, int] = (((self.width // 2) + 1) + offsetw,
                                     (self.height // 2) + offseth)

        to_holes: List[Tuple[int, int]] = [((self.height // 2) + 1 + offseth,
                                            ((self.width // 2) + 2) + offsetw),
                                           (((self.height // 2) - 1) + offseth,
                                            ((self.width // 2) + 1) + offsetw)]

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
        if ((entry_test in pattern_xy)
            or (exit_test in pattern_xy)
            or (entry_test in to_holes)
                or (exit_test in to_holes)):
            if start_for[1] - 2 > 1 and direction != 2:
                self._pattern(offseth - 1, offsetw, 1)
            elif start_for[1] + 2 < self.height - 2 and direction != 1:
                self._pattern(offseth + 1, offsetw, 2)
            elif start_for[0] - 2 > 1 and direction != 4:
                self._pattern(offseth, offsetw - 1, 3)
            elif start_for[0] + 2 < self.width - 2 and direction != 3:
                self._pattern(offseth, offsetw + 1, 4)
            else:
                raise MazeTooSmallError()
            return
        for coordinate in pattern_xy:
            self.maze[coordinate[0]][coordinate[1]] = 42
        self.pattern = pattern_xy

    def _narrow_corridor(self, position: Tuple[int, int],
                         options:
                         List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """Filter out neighbors that would produce
        corridors wider than one cell.

        Checks whether the current cell is
        already partof a horizontal or vertical
        corridor and removes candidates with
        the same orientation, preventing two
        parallel open passages from being merged
        into a wide corridor.

        Parameters
        ----------
        position : Tuple[int, int]
            (x, y) coordinates of the current cell.
        options : List[Tuple[int, int]]
            Candidate neighbor cells to move to.

        Returns
        -------
        List[Tuple[int, int]]
            Filtered list of neighbors that do not produce wide corridors.
        """
        try:
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
        except IndexError as e:
            print(f"Probably the options list is empty. Error: {e}")
            return to_return

    def _isvalid(self, position: Tuple[int, int],
                 flag: int = 0) -> List[Tuple[int, int]]:
        """Return the valid neighbors of a cell
        based on the current generation phase.

        When flag is 0, returns only unvisited
        neighbors (value 0xf). When flag
        is non-zero, returns neighbors that are
        not part of the 42 pattern. Results
        are passed through _narrow_corridor to
        avoid wide corridors.

        Parameters
        ----------
        position : Tuple[int, int]
            (x, y) coordinates of the current cell.
        flag : int, optional
            Controls the neighbor filter: 0 for unvisited cells only,
            non-zero to exclude pattern cells, by default 0.

        Returns
        -------
        List[Tuple[int, int]]
            List of valid neighbor coordinates.
        """
        x, y = position
        options: List[Tuple[int, int]] = []
        condition: Callable[[int], bool] = (lambda cell:
                                            cell != 42 if flag
                                            else cell == 0xf)
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
        """Open the shared wall between two adjacent cells.

        Clears the appropriate wall bits in both cells depending on their
        relative positions (horizontal or vertical neighbors).

        Parameters
        ----------
        current : Tuple[int, int]
            (x, y) coordinates of the current cell.
        next : Tuple[int, int]
            (x, y) coordinates of the neighboring cell.

        Raises
        ------
        ValueError
            If either current or next is an empty tuple.
        """
        if len(current) == 0 or len(next) == 0:
            raise ValueError(
                "You're passing empty arfuments to _opening_walls function")
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
        """Carve passages through the maze
        using a depth-first search algorithm.

        Performs one or two passes depending on whether the maze is perfect or
        imperfect. In the first pass, walls are opened along the DFS path. In
        the second pass (imperfect only), additional connections are made at
        a reduced frequency to introduce loops. After generation,
        any remaining fully-walled cells are forcibly opened, and the 42
        pattern cells are restored.

        Raises
        ------
        MazeNotExistsError
            If the maze grid has not been
            initialized before calling this method.
        """
        if len(self.maze) == 0:
            raise MazeNotExistsError(
                "You cannot creat a maze with dimensions 0x0")
        fifteen: List[Tuple[int, int]] = []
        stack: List[Tuple[int, int]] = []
        next: Tuple[int, int] = (0, 0)
        current: Tuple[int, int] = self.entry
        options: List[Tuple[int, int]]
        spins: Callable[[bool], int] = lambda perfect: 1 if perfect else 2
        visited: set[Tuple[int, int]] = set()
        second_door: int = 0
        if self.seed is not None:
            random.seed(self.seed)
        for spin in range(spins(self.perfect)):
            if spin == 1:
                current = self.entry
                stack = []
                if self.seed is not None:
                    random.seed(self.seed + 5)
            limit: int = int((self.width * self.height) * 0.10)
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
                        limit = int((self.width * self.height) * 0.30)
                    if spin == 0:
                        self._opening_walls(current, next)
                    stack.append(current)
                    current = next
                else:
                    if len(stack) == 0:
                        break
                    current = stack.pop()
                limit -= 1

        if not self.perfect:
            condicion: (Callable[[int],
                        Tuple[int, int]]) = (lambda i: self.entry
                                             if i == 0 else self.exit)
            location: Tuple[int, int]
            for i in range(2):
                location = condicion(i)
                options = self._isvalid(location, 1)
                for cell in options:
                    second_door = self.maze[location[1]][location[0]]
                    self._opening_walls(location, cell)
                    if ((location == self.exit) and
                            (second_door !=
                             self.maze[location[1]][location[0]])):
                        break
        fifteen = [(x, y) for y, fila in enumerate(self.maze)
                   for x, cell in enumerate(fila) if cell == 15]
        if len(fifteen) > 0:
            for cell in fifteen:
                self._opening_walls(
                    cell, random.choice(self._isvalid(cell, 1)))
        for coordinate in self.pattern:
            self.maze[coordinate[0]][coordinate[1]] = 0xf

    def _bfs(self) -> List[Tuple[int, int]]:
        """Find the shortest path from
        entry to exit using breadth-first search.

        Traverses the maze respecting wall bits to determine which neighbors
        are reachable, then reconstructs the path by backtracking through
        a parent map.

        Returns
        -------
        List[Tuple[int, int]]
            Ordered list of (x, y) coordinates from entry to exit.
        """
        try:
            fifo: deque[Tuple[int, int]] = deque()
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
        except Exception as e:
            print(f"Something went wrong during the BFS Algorithm: {e}")
            return path

    def _wilson(self) -> None:
        """Carve passages through the maze using Wilson's algorithm.

        Performs a loop-erased random
        walk from unvisited cells until all cells
        are connected. For imperfect mazes, a second
        path is started from the entry to introduce an
        additional route. After generation, the 42 pattern
        cells are restored.
        """
        if self.seed:
            random.seed(self.seed)
        fifteen: List[Tuple[int, int]] = []
        fifteen = [(x, y) for y, fila in enumerate(self.maze)
                   for x, cell in enumerate(fila) if cell == 15]
        # we don't want another path starting from exit in a perfect maze:
        if self.perfect:
            fifteen.remove(self.exit)

        current: Tuple[int, int] = self.entry
        next: Tuple[int, int]
        path: List[Tuple[int, int]] = [self.entry]
        index: int = 0
        extra_path: int = 0 if self.perfect else 1
        first_path: List[Tuple[int, int]] = []

        while True:
            options = self._isvalid(current, 1)
            # we only want to reach exit in the first pass if perfect
            if (self.exit in options and path[0] != self.entry
                    and self.perfect and len(options) > 1):
                options.remove(self.exit)
            if not self.perfect:
                self._narrow_corridor(current, options)

            next = random.choice(options)
            if next not in path:
                path.append(next)

                if (((self.maze[next[1]][next[0]] != 15)
                        and path[0] != self.entry) or (next == self.exit)):
                    for i in range(len(path) - 1):
                        self._opening_walls(path[i], path[i + 1])
                        if path[i] in fifteen:
                            fifteen.remove(path[i])
                    if len(fifteen) == 0:
                        break

                    current = random.choice(fifteen)
                    if path == first_path:
                        extra_path = 1
                    # if imperfect, let's create a second path from entry:
                    if extra_path:
                        first_path = path.copy()
                        extra_path = 0
                        current = self.entry
                    path = []
                    path.append(current)
                else:
                    current = next
            else:
                index = path.index(next)
                path = path[0:index + 1]
                current = path[-1]

        for coordinate in self.pattern:
            self.maze[coordinate[0]][coordinate[1]] = 0xf

    def complying(self) -> None:
        """Validate maze connectivity and
        whether it satisfies the perfect condition.

        Performs a BFS from the entry to count visited cells and edges, then
        prints whether the maze is fully connected and whether the edge count
        matches the expected value for a perfect maze.
        """
        fifo: deque[Tuple[int, int]] = deque()
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
        """Initialize the maze grid and run the full generation pipeline.

        Fills the grid with fully-walled cells, places the 42 pattern, runs
        either DFS or Wilson's algorithm to carve passages, and computes the
        solution path via BFS.
        """
        self.maze = [[0xf for _ in range(self.width)]
                     for _ in range(self.height)]
        try:
            self._pattern()
        except MazeTooSmallError as e:
            print(e)
        except RecursionError:
            print(MazeTooSmallError.msg)
        if self.alt_algorithm:
            self._wilson()
        else:
            self._dfs()
        self.solution = self._bfs()
