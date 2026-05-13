from typing import Tuple, List


class Maze():
    """Class to contain maze data"""

    def __init__(self,
                 maze: List[List[int]],
                 width: int,
                 height: int,
                 start_coord: Tuple[int, int],
                 exit_coord: Tuple[int, int],
                 path: str
                 ) -> None:
        """Initialize the maze with the requiered parameters

        maze: a matrix of int values representing the walls per cell.
        width: number of cells in x.
        height: number of cells in y.
        start_coord: x,y coordinates of maze's entrance.
        exit_coord: x,y coordinates of maze's exit.
        path: sequence of cardinal directions (NESW) to follow from entrance
        to exit to find the maze's shortest (or unique) solution.
        """
        self.rows: List[List[int]] = maze
        self.width: int = width
        self.height: int = height
        self.start: Tuple[int, int] = start_coord
        self.exit: Tuple[int, int] = exit_coord
        self.path: str = path
