from typing import Tuple, List


class Maze():
    """Class to contain maze data"""
    def __init__(self, maze: List[List[int]],
                 width: int,
                 height: int,
                 start_coord: Tuple[int, int],
                 exit_coord: Tuple[int, int], path: str
                 ) -> None:

        self.rows: List[List[int]] = maze
        self.width: int = width
        self.height: int = height
        self.start: Tuple[int, int] = start_coord
        self.exit: Tuple[int, int] = exit_coord
        self.path: str = path
