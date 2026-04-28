from typing import Dict, Any
from .window import MazeWindow
from .maze import Maze


class MazeManager():
    """Main class to run all the circus"""

    def __init__(self, config_data: Dict[str, Any]) -> None:
        self._config_data: Dict[str, Any] = config_data
        self._output_file: str = self._config_data.pop("output_file")
        self._window = MazeWindow(self._config_data)

    def write_maze_file(self) -> None:
        """Saves the current maze to a file"""
        #open(self._output_file, w) ....
        pass

    def show_maze(self) -> None:
        """Shows the maze"""
        self._window.render()
