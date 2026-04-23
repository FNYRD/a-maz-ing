from typing import Dict, Any


class MazeManager():
    """Main class to run all the circus"""

    def __init__(self, config_data: Dict[str, Any]) -> None:
        self._config_data: Dict[str, Any] = config_data
        #self._maze: Maze = None

    def gen_maze(self):
        #self._maze = Maze(self.config_data)
        pass
