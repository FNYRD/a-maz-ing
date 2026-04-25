try:
    from typing import Tuple, List, Optional
except ImportError as e:
    print(f"An error happened importing the modules\n{e}")


class MazeTooSmallError(Exception):
    pass


    # No olvidar que debo verificar si es posible la creacion del laberinto o no
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
    
    def pattern(self) -> None:
        start_for: Tuple[int, int] = (((self.width // 2) - 1), (self.height // 2))
        start_to: Tuple[int, int] = (((self.width // 2) + 1), (self.height // 2))
        self.maze[start_for[1]][start_for[0]] = 42 # Borrar
        self.maze[start_to[1]][start_to[0]] = 42 # Borrar
        if self.width <= 5 >= self.height:
            raise MazeTooSmallError("Maze's size is too small "
                                    "for displaying the 42 pattern")
