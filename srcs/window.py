from typing import Any, List, Tuple, Dict
from .maze import Maze
from .color import Color
from mazegen import MazeGenerator
import sys
import time
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
        self.fg_color: int = Color.WALL
        self.bg_color: int = Color.BG
        self.hl_color: int = Color.HL
        self.margin: int = 10
        self.cell_size: int = 20
        if self.cell_size * config["width"] < 140:
            self.cell_size = 140 // config["width"]
        if (self.cell_size * config["height"] < 140
                and config["height"] < config["width"]):
            self.cell_size = 140 // config["height"]
        self.wall_size: int = 4
        self.path_visible: int = 0
        self.path_animated: bool = True
        self.menu_visible: bool = False
        self.win: bool = False
        self.win_time: float = 2.0
        self.playing: Tuple[int, int] | None = None
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

    def move_player(self, step: str) -> None:
        if not self.playing:
            return
        x, y = self.playing
        if step == "N" and not self.maze.rows[y][x] & 0b0001:
            y -= 1
        elif step == "E" and not self.maze.rows[y][x] & 0b0010:
            x += 1
        elif step == "S" and not self.maze.rows[y][x] & 0b0100:
            y += 1
        elif step == "W" and not self.maze.rows[y][x] & 0b1000:
            x -= 1
        self.playing = (x, y)
        if self.playing == self.maze.exit:
            self.draw_maze(self.maze)
            self.draw_single_block(self.maze.exit, Color.WHITE)
            self.win = True
            self.hl_color = Color.get_random_color()
            self.playing = None

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

    def draw_maze(self, maze: Maze) -> None:
        """Draw all maze elements in order.

        maze: class containing maze parameters
        """
        if self.menu_visible:
            return

        if self.hl_color != Color.HL:
            if self.hl_color != Color.BG:
                self.hl_color = Color.get_random_color()
            else:
                self.hl_color = Color.BG

        # Clear window:
        self._m.mlx_clear_window(self._ptr, self._win)

        # Draw the maze:
        self.paint_bg(maze.width, maze.height)
        self.draw_maze_walls(maze.width, maze.height, maze.rows)

        if self.win:
            time.sleep(self.win_time)
            self.win_time = 0.0
            self.bg_color = Color.BLACK
            self.fg_color = Color.BLACK
            return

        # Draw start and exit:
        self.draw_single_block(maze.start, Color.GREEN)
        self.draw_single_block(maze.exit, Color.RED)

        # Draw solution path:
        if self.path_visible > 0:
            if self.path_visible == len(maze.path):
                self.draw_path(
                    maze.start, maze.path[:self.path_visible], Color.GREEN)
                if self.path_animated:
                    self.hl_color = Color.get_random_color()
                    self.win = True
            else:
                self.draw_path(maze.start, maze.path[:self.path_visible],
                               Color.get_random_color())
                if self.path_visible < len(maze.path):
                    self.path_visible += 1

        # Player position:
        if self.playing:
            self.draw_single_block(
                    self.playing, Color.WHITE)

        # Write instructions for user interaction:
        self.draw_instructions(maze.width, maze.height)

    def generate(self) -> None:
        """Call generator to create a new maze."""

        self._generator.generate()
        self.maze.rows = self._generator.maze
        self.maze.path = self.translate_path(self._generator.solution)

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

            # 'Esc' to hide menu / skip path animation:
            if keynum in [65307, 115, 99, 102, 103, 112] and self.menu_visible:
                if self.menu_visible:
                    self.menu_visible = False

            elif keynum == 65307 or keynum == 103 and not self.menu_visible:
                if self.win:
                    self.win = False
                    self.win_time = 2.0
                    self.hl_color = Color.HL
                    self.fg_color = Color.WALL
                    self.bg_color = Color.BG
                    self.path_visible = 0
                    self.path_animated = False
                elif self.path_visible > 0:
                    self.path_visible = len(self.maze.path)
                elif self.playing:
                    self.playing = None

            # 'm' to show menu:
            if keynum == 109 and not self.win:
                if not self.menu_visible:
                    self.menu_visible = True
                    self.show_menu()

            # 's' to show/hide solution path:
            if keynum == 115 and not self.win:
                if self.path_visible > 0:
                    self.path_visible = 0
                else:
                    if self.path_animated:
                        self.path_visible = 2
                    else:
                        self.path_visible = len(self.maze.path)

            # 'c' to change walls color:
            if keynum == 99 and not self.win:
                self.fg_color = Color.get_random_color()

            # 'f' to change pattern color:
            if keynum == 102 and not self.win:
                if self.hl_color == Color.HL:
                    self.hl_color = Color.get_random_color()
                else:
                    self.hl_color = Color.HL

            # 'g' to regenerate:
            if keynum == 103:
                self.generate()
                self.playing = None
                self.path_animated = True
                self.hl_color = Color.HL

            # 'p' to play:
            if keynum == 112 and not self.win:
                self.playing = self.maze.start

            # move player:
            if self.playing and not self.menu_visible:
                if keynum == 65361:
                    self.move_player('W')
                if keynum == 65362:
                    self.move_player('N')
                if keynum == 65363:
                    self.move_player('E')
                if keynum == 65364:
                    self.move_player('S')

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

        # Set hooks to capture events:
        self._m.mlx_hook(self._win, 33, 0, close_window, ["close window"])
        self._m.mlx_key_hook(self._win, mykey, ["key pressed"])

        # Rendering loop:
        self._m.mlx_loop_hook(self._ptr, self.draw_maze, self.maze)
        self._m.mlx_loop(self._ptr)
