from mlx import Mlx
from typing import Any, List, Tuple
from .maze import Maze
import random
from enum import IntEnum


class Color(IntEnum):
    # Dark & Moody
    CHARCOAL = 0xFF1a1a1a
    DEEP_NAVY = 0xFF0a1428
    DARK_SLATE = 0xFF2c3e50

    # Rich Jewel Tones
    EMERALD = 0xFF27ae60
    SAPPHIRE = 0xFF2980b9
    AMETHYST = 0xFF8e44ad
    RUBY = 0xFFc0392b
    
    # Vibrant & Bold
    NEON_CYAN = 0xFF00d4ff
    NEON_MAGENTA = 0xFFff00ff
    NEON_LIME = 0xFF00ff41
    NEON_ORANGE = 0xFFff6600

    # Elegant Neutrals
    GRANITE = 0xFF555555
    GUNMETAL = 0xFF2f4f4f
    PEWTER = 0xFF708090

    # Atmospheric
    MIDNIGHT = 0xFF0f0f1e
    FOREST = 0xFF1b4332
    PLUM = 0xFF44355b
    TEAL = 0xFF0d5f5f

    # Basic
    RED = 0xFF0000FF
    GREEN = 0xFF00FF00
    BLUE = 0xFFFF0000
    BLACK = 0xFF000000

    def get_random_color():
        return random.choice(list(Color))


class MazeWindow():
    """Class to contain the maze displaying window"""

    def __init__(self):
        self._m = Mlx()
        self._ptr = self._m.mlx_init()
        self._win = None
        self.fg_color: int = 0xeeeeeeff
        self.bg_color: int = 0xff113355
        self.hl_color: int = 0xff00ffff
        self.margin: int = 10
        self.cell_size: int = 20
        self.wall_size: int = 4
        self.path_visible = True
    
    def paint_bg(self, width: int, height: int):
        """Gives the maze area a background color (inside margins)""" 

        for x in range(0, width * self.cell_size):
            for y in range(0, height * self.cell_size):
                self._m.mlx_pixel_put(
                    self._ptr, self._win, self.margin + x, self.margin + y, self.bg_color)

    def draw_maze(self, width: int, height: int, rows: List[str]) -> None:
        """Draws the maze on the instance window"""

        for x in range(0, width):
            for y in range(0, height):
                self.draw_cell(self.cell_size * x + self.margin,
                    self.cell_size * y + self.margin, rows[y][x])

    def draw_single_block(self, coords: Tuple[int, int], color: int):
        """Paints a single block (space between walls) at the specified position,
        with the specified color"""

        for x in range(0, self.cell_size - self.wall_size - 1):
            for y in range(0, self.cell_size - self.wall_size - 1):
                self._m.mlx_pixel_put(
                    self._ptr, self._win, 
                    x + (coords[0]) * self.cell_size + self.margin + self.wall_size,
                    y + (coords[1]) * self.cell_size + self.margin + self.wall_size,
                    color)

    def draw_path(self, start: Tuple[int, int], path: str, color: int) -> None:
        """Draws the path given as direction instructions (NESW) omitting the edges"""

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

    def draw_cell(self, x_offset: int, y_offset: int, value: str) -> None:
        """Recieves a position to draw a cell and a hex value coding for
        open and closed walls"""    

        code = int('0x' + value, 16)
        for x in range(0, self.cell_size + self.wall_size - 1):
            for y in range(0, self.cell_size + self.wall_size - 1):
                if y < self.wall_size and code & 0b0001:
                    self._m.mlx_pixel_put(
                        self._ptr, self._win, x + x_offset, y + y_offset, self.fg_color)
                elif x >= self.cell_size - 1 and code & 0b0010:
                    self._m.mlx_pixel_put(
                        self._ptr, self._win, x + x_offset, y + y_offset, self.fg_color)
                elif y >= self.cell_size - 1 and code & 0b0100:
                    self._m.mlx_pixel_put(
                        self._ptr, self._win, x + x_offset, y + y_offset, self.fg_color)
                elif x < self.wall_size and code & 0b1000:
                    self._m.mlx_pixel_put(
                        self._ptr, self._win, x + x_offset, y + y_offset, self.fg_color)
                elif value == "F":
                    self._m.mlx_pixel_put(
                            self._ptr, self._win, x + x_offset, y + y_offset, self.hl_color)
#                else:
#                    self._m.mlx_pixel_put(
#                            self._ptr, self._win, x + x_offset, y + y_offset, self.bg_color)
#                if x == 6 and y == 0:
#                    self._m.mlx_string_put(
#                            self._ptr, self._win, x + x_offset, y + y_offset,
#                            self.fg_color, value)

    def render(self, maze: Maze) -> None:
        """Receives the maze data and creates a window to draw it"""
       
        # Setting user interaction:
        def mykey(keynum: int, stuff: Any):
            """Captures key release events"""

            # 'q' to exit
            if keynum == 113:
                self._m.mlx_destroy_window(self._ptr, self._win)
                self._m.mlx_release(self._ptr)

            # 's' to show/hide solution path:
            if keynum == 115:
                if self.path_visible:
                    self.draw_path(maze.start, maze.path, self.bg_color)
                    self.path_visible = False
                else:
                    self.draw_path(maze.start, maze.path, 0xff888888)
                    self.path_visible = True

            # 'c' to change walls color:
            if keynum == 99:
                self.fg_color = Color.get_random_color()
                self.draw_maze(maze.width, maze.height, maze.rows)

        def close_window(stuff: Any):
            """Captures ClientMessage events (WM_DELETE_WINDOW)"""
            print(stuff)
            self._m.mlx_destroy_window(self._ptr, self._win)
            self._m.mlx_release(self._ptr)

        # Creating window with maze size:
        self._win = self._m.mlx_new_window(self._ptr,
                self.cell_size * maze.width + 2 * self.margin + self.wall_size,
                self.cell_size * maze.height + 2 * self.margin + self.wall_size,
                "A_Maze_Ing!")
        self._m.mlx_clear_window(self._ptr, self._win)
      
        # Draw the maze:
        self.paint_bg(maze.width, maze.height)
        self.draw_maze(maze.width, maze.height, maze.rows)

        # Draw start and exit:
        self.draw_single_block(maze.start, 0xff00ff00)
        self.draw_single_block(maze.exit, 0xffff0000)
        self.draw_path(maze.start, maze.path, 0xff888888)
        
        # Set hooks to capture events:
        self._m.mlx_hook(self._win, 33, 0, close_window, ["close window"])
        self._m.mlx_key_hook(self._win, mykey, ["key pressed"])
        self._m.mlx_loop(self._ptr)
