from typing import Any, List, Tuple, Dict
from .maze import Maze
from .color import Color
from mazegen import MazeGenerator
import sys
try:
    from mlx import Mlx
except ImportError as e:
    print(e)
    print("Please install mlx graphic library")
    sys.exit(1)


class MazeWindow():
    """Class to contain the maze displaying window.

    This class is the core of the visual representation for maze.
    It istantiates the MazeGenerator, a Maze to contain its data
    and a minilibx window to visually represent them in an
    interactive way.
    """

    def __init__(self, config: Dict[str, Any]):
        """Initiate the maze window and its elements, maze and generator.

        config: dictionary with configuration parameter.
        """
        self._generator: MazeGenerator = MazeGenerator(**config)
        self._m = Mlx()
        self._ptr = self._m.mlx_init()
        self._win = None
        self.fg_color: int = 0xeeeeeeff
        self.bg_color: int = 0xff113355
        self.hl_color: int = 0xff00ffff
        self.margin: int = 10
        self.cell_size: int = 20
        if self.cell_size * config["width"] < 140:
            self.cell_size = 140 // config["width"]
        if (self.cell_size * config["height"] < 140
                and config["height"] < config["width"]):
            self.cell_size = 140 // config["height"]
        self.wall_size: int = 4
        self.path_visible = False
        self.menu_visible = False
        self.instructions: List[str] = [
            "(c) color", "(s) solution", "(f) pattern", "(g) regen", "(q) quit"
        ]
        self._generator.generate()
        self.maze: Maze = Maze(
            self._generator.maze,
            config["width"],
            config["height"],
            config["entry"],
            config["exit"],
            self.translate_path(self._generator.solution))

    def paint_bg(self, width: int, height: int,
                 color: int = 0) -> None:
        """Give the maze area a background color (inside margins).

        width: x dimension of the area to paint (in cells).
        height: y dimension of the area to paint (in cells).
        """
        if not color:
            color = self.bg_color
        for x in range(0, width * self.cell_size + self.wall_size - 1):
            for y in range(0, height * self.cell_size + self.wall_size - 1):
                self._m.mlx_pixel_put(
                    self._ptr, self._win, self.margin + x,
                    self.margin + y, color)

    def draw_maze_walls(
            self, width: int, height: int, rows: List[List[int]]) -> None:
        """Draw the maze on the instance window.

        width: number of cells in x.
        height: number of cells in y.
        rows: actual matrix containing maze data.
        """
        for x in range(0, width):
            for y in range(0, height):
                self.draw_cell(
                    self.cell_size * x + self.margin,
                    self.cell_size * y + self.margin, rows[y][x])

    def draw_single_block(self, coords: Tuple[int, int], color: int) -> None:
        """Paint a single block (space between walls) at coords.

        coords: x,y position.
        color: RGBA mlx specified color to paint the block.
        """
        for x in range(0, self.cell_size - self.wall_size - 1):
            for y in range(0, self.cell_size - self.wall_size - 1):
                self._m.mlx_pixel_put(
                    self._ptr, self._win,
                    x + (coords[0]) * self.cell_size + self.margin
                    + self.wall_size,
                    y + (coords[1]) * self.cell_size + self.margin
                    + self.wall_size,
                    color)

    def translate_path(self, coords: List[Tuple[int, int]]) -> str:
        """Translates path coordinates into a string of directions (NESW).

        coords: list of (x, y) coordinates for maze solution path.
        Return a sequence of cardinal directions (NESW) from entry to exit.
        """
        path: str = ""
        for i in range(0, len(coords) - 1):
            a: Tuple[int, int] = coords[i]
            b: Tuple[int, int] = coords[i + 1]
            if a[0] < b[0]:
                path += "E"
            elif a[0] > b[0]:
                path += "W"
            elif a[1] > b[1]:
                path += "N"
            elif a[1] < b[1]:
                path += "S"
        return path

    def draw_path(
            self, start: Tuple[int, int], path: str, color: int) -> None:
        """Draw the path given as cardinal instructions (NESW) omitting edges.

        path: the sequence of cardinal directions (NESW) from entry to exit.
        color: RGBA mlx valid color to paint the path.
        """
        x, y = start
        for step in path[:-1]:
            if step == "N":
                y -= 1
            elif step == "E":
                x += 1
            elif step == "S":
                y += 1
            elif step == "W":
                x -= 1
            self.draw_single_block((x, y), color)

    def draw_cell(self, x_offset: int, y_offset: int, code: int) -> None:
        """Draw the walls for a cell in the specified position.

        The hex value of the cell represents open (0) and closed (1) walls
        in binary coding, following a clockwise logic:
           Ex. 1010 means North and South closed, East and West open.

        x_offset: cell horizontal position.
        y_offset: cell vertical position.
        code: hex value (0-F) coding the walls.
        """

        for x in range(0, self.cell_size + self.wall_size - 1):
            for y in range(0, self.cell_size + self.wall_size - 1):
                if y < self.wall_size and code & 0b0001:
                    self._m.mlx_pixel_put(
                        self._ptr, self._win,
                        x + x_offset, y + y_offset, self.fg_color)
                elif x >= self.cell_size - 1 and code & 0b0010:
                    self._m.mlx_pixel_put(
                        self._ptr, self._win,
                        x + x_offset, y + y_offset, self.fg_color)
                elif y >= self.cell_size - 1 and code & 0b0100:
                    self._m.mlx_pixel_put(
                        self._ptr, self._win,
                        x + x_offset, y + y_offset, self.fg_color)
                elif x < self.wall_size and code & 0b1000:
                    self._m.mlx_pixel_put(
                        self._ptr, self._win,
                        x + x_offset, y + y_offset, self.fg_color)
                elif code == 0xF:
                    self._m.mlx_pixel_put(
                        self._ptr, self._win,
                        x + x_offset, y + y_offset, self.hl_color)

    def draw_instructions(self, width: int, height: int) -> None:
        """Print the instructions for user interaction.

        Check the best way to distribute instructions (bottom row / menu)
        accordingly to the maze/window size and print them.

        width: available space to write in x (in cells).
        height: maze height in cells (vertical offset for instructions).
        """
        if not self.menu_visible:
            # check if there is enough to show instructions in line:
            space = width * self.cell_size
            instructions = ((" | ").join(self.instructions))
            length = len(instructions) * 10 + 10

            if space >= length:
                self._m.mlx_string_put(
                    self._ptr, self._win,
                    self.margin + self.wall_size + (space - length) // 2,
                    height * self.cell_size + self.margin + self.wall_size + 9,
                    0xffcccccc, instructions)
            else:
                self._m.mlx_string_put(
                    self._ptr, self._win,
                    self.margin + self.wall_size,
                    height * self.cell_size + self.margin + self.wall_size + 9,
                    0xffcccccc, "(m) menu")
        else:
            self._m.mlx_string_put(
                self._ptr, self._win,
                self.margin + self.wall_size + 10,
                self.margin + self.wall_size + 10,
                0xffcccccc, "-- Menu --")
            for row, ins in enumerate(self.instructions):
                self._m.mlx_string_put(
                    self._ptr, self._win,
                    self.margin + self.wall_size + 10,
                    self.margin + self.wall_size + 20 * row + 30,
                    0xffcccccc, ins)

    def show_menu(self) -> None:
        """Paint a transparence layer on top of the maze for menu writting."""

        self.paint_bg(self.maze.width, self.maze.height, 0xCC000000)
        self.draw_instructions(self.maze.width, self.maze.height)

    def draw_maze(self) -> None:
        """Draw all maze elements in order."""

        # Draw the maze:
        self.paint_bg(self.maze.width, self.maze.height)
        self.draw_maze_walls(self.maze.width, self.maze.height, self.maze.rows)

        # Draw start and exit:
        self.draw_single_block(self.maze.start, 0xff00ff00)
        self.draw_single_block(self.maze.exit, 0xffff0000)

        # Draw solution path:
        if self.path_visible:
            self.draw_path(self.maze.start, self.maze.path, 0xff888888)

    def generate(self) -> None:
        """Call generator to create a new maze and show it."""

        self._generator.generate()
        self.maze.rows = self._generator.maze
        self.maze.path = self.translate_path(self._generator.solution)
        self.draw_maze()

    def render(self) -> None:
        """Create the window and set user interactions.

        Main method for the class, call mlx instance to create a window
        with the appropriate size to show the maze and sets the hooks
        to capture events allowing user interaction.
        """

        # Setting user interaction:
        def mykey(keynum: int, stuff: Any) -> None:
            """Capture key release events.

            keynum: code for the released key.
            stuff: not used (defined by mlx).
            """
            # 'q' to exit
            if keynum == 113:
                self._m.mlx_destroy_window(self._ptr, self._win)
                self._m.mlx_release(self._ptr)

            # 'Esc' to hide menu:
            if keynum in [65307, 115, 99, 102, 103]:
                if self.menu_visible:
                    self.menu_visible = False
                    self.draw_maze()

            # 'm' to show menu:
            if keynum == 109:
                if not self.menu_visible:
                    self.menu_visible = True
                    self.show_menu()

            # 's' to show/hide solution path:
            if keynum == 115:
                if self.path_visible:
                    self.draw_path(
                        self.maze.start, self.maze.path, self.bg_color)
                    self.path_visible = False
                else:
                    self.draw_path(
                        self.maze.start, self.maze.path, 0xff888888)
                    self.path_visible = True

            # 'c' to change walls color:
            if keynum == 99:
                self.fg_color = Color.get_random_color()
                self.draw_maze_walls(
                    self.maze.width, self.maze.height, self.maze.rows)

            # 'f' to change pattern color:
            if keynum == 102:
                self.hl_color = Color.get_random_color()
                self.draw_maze_walls(
                    self.maze.width, self.maze.height, self.maze.rows)

            # 'g' to regenerate:
            if keynum == 103:
                self.generate()

        def close_window(stuff: Any) -> None:
            """Respone for ClientMessage event (WM_DELETE_WINDOW)."""
            self._m.mlx_destroy_window(self._ptr, self._win)
            self._m.mlx_release(self._ptr)

        # Create window with maze size:
        self._win = self._m.mlx_new_window(
            self._ptr,
            self.cell_size * self.maze.width + 2 * self.margin
            + self.wall_size,
            self.cell_size * self.maze.height + 2 * self.margin
            + self.wall_size + 30,
            "A_Maze_Ing!")
        self._m.mlx_clear_window(self._ptr, self._win)

        # Draw the maze:
        self.paint_bg(self.maze.width, self.maze.height)
        self.draw_maze()

        # Write instructions for user interaction:
        self.draw_instructions(self.maze.width, self.maze.height)

        # Set hooks to capture events:
        self._m.mlx_hook(self._win, 33, 0, close_window, ["close window"])
        self._m.mlx_key_hook(self._win, mykey, ["key pressed"])

        # Rendering loop:
        self._m.mlx_loop(self._ptr)
