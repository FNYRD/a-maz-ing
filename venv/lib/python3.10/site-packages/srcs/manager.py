from typing import Dict, Any, List, Tuple
from .window import MazeWindow


class MazeManager():
    """Class that show the maze window and save the maze on exit"""

    def __init__(self, config_data: Dict[str, Any]) -> None:
        """Initialize the manager.

        config_data: dictionary containing already validated maze parameters.
        """
        self._config_data: Dict[str, Any] = config_data
        self._output_file: str = self._config_data.pop("output_file")
        self._window = MazeWindow(self._config_data)

    def write_maze_file(self) -> None:
        """Save current maze to a text file"""

        maze: list[list[int]] = self._window.maze.rows
        path: str = self._window.maze.path
        m_entry: Tuple[int, int] = self._window.maze.start
        m_exit: Tuple[int, int] = self._window.maze.exit
        output: List[str] = [
            ''.join(f"{value:X}" for value in row) for row in maze]

        try:
            with open(self._output_file, "w") as of:
                for row in output:
                    of.write(row + '\n')
                of.write('\n')
                of.write(f"{m_entry[0]},{m_entry[1]}\n")
                of.write(f"{m_exit[0]},{m_exit[1]}\n")
                of.write(path + '\n')
        except Exception as e:
            print(f"Error: failed to write output file ({e})")

    def show_maze(self) -> None:
        """Method to initiate the visual representation of the maze"""

        self._window.render()
