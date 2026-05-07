from mlx import Mlx
from typing import Any, List, Tuple, Dict
from .maze import Maze
from .color import Color
from .maze_generator import MazeGenerator


class MazeWindow():
    """Class to contain the maze displaying window"""

    def __init__(self, config: Dict[str, Any]):
        self._m = Mlx()
        self._generator: MazeGenerator = MazeGenerator(**config)
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
        """Gives the maze area a background color (inside margins)"""

        if not color:
            color = self.bg_color
        for x in range(0, width * self.cell_size + self.wall_size - 1):
            for y in range(0, height * self.cell_size + self.wall_size - 1):
                self._m.mlx_pixel_put(
                    self._ptr, self._win, self.margin + x,
                    self.margin + y, color)

    def draw_maze_walls(
            self, width: int, height: int, row: List[List[int]]) -> None:
        """Draws the maze on the instance window"""

        for x in range(0, width):
            for y in range(0, height):
                self.draw_cell(
                    self.cell_size * x + self.margin,
                    self.cell_size * y + self.margin, row[y][x])

    def draw_single_block(self, coords: Tuple[int, int], color: int) -> None:
        """Paints a single block (space between walls)
        at the specified position, with the specified color"""

        for x in range(0, self.cell_size - self.wall_size - 1):
            for y in range(0, self.cell_size - self.wall_size - 1):
                self._m.mlx_pixel_put(
                    self._ptr, self._win,
                    x + (coords[0]) * self.cell_size + self.margin
                    + self.wall_size,
                    y + (coords[1]) * self.cell_size + self.margin
                    + self.wall_size,
                    color)

    def translate_path(self, coords: List[Tuple[int, int]]) -> None:
        """Receives a list of coordinates por the path and translates it into
        a string of directions (NESW)"""
        print(coords)

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

        print(path)
        return path

    def draw_path(self, start: Tuple[int, int], path: str, color: int) -> None:
        """Draws the path given as direction instructions (NESW)
        omitting the edges"""

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
        """Recieves a position to draw a cell and a hex value coding for
        open and closed walls"""

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
        """Prints the instructions for user interaction, distributing them
        accordingly to the maze/window size"""

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
        self.paint_bg(self.maze.width, self.maze.height, 0xCC000000)
        self.draw_instructions(self.maze.width, self.maze.height)

    def draw_maze(self) -> None:
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
        self._generator.generate()
        self.maze.rows = self._generator.maze
        self.maze.path = self.translate_path(self._generator.solution)
        self.draw_maze()

    def render(self) -> None:
        """Creates the window and sets user interactions"""

        # Setting user interaction:
        def mykey(keynum: int, stuff: Any) -> None:
            """Captures key release events"""

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
            """Captures ClientMessage events (WM_DELETE_WINDOW)"""
            self._m.mlx_destroy_window(self._ptr, self._win)
            self._m.mlx_release(self._ptr)

        # Creating window with maze size:
        self._win = self._m.mlx_new_window(
            self._ptr,
            self.cell_size * self.maze.width + 2 * self.margin + self.wall_size,
            self.cell_size * self.maze.height + 2 * self.margin + self.wall_size
            + 30,
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
        self._m.mlx_loop(self._ptr)
