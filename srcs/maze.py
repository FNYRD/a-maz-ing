from typing import Tuple, List


class Maze():
    """Class to contain maze data"""
    def __init__(self, maze: str,
                 start_coord: Tuple[int, int],
                 exit_coord: Tuple[int, int], path: str
                 ) -> None:

        self.rows: List[str] = maze.strip("\n").split("\n")
        self.width: int = len(self.rows[0])
        self.height: int = len(self.rows)
        self.start: Tuple[int, int] = start_coord
        self.exit: Tuple[int, int] = exit_coord
        self.path: str = path
