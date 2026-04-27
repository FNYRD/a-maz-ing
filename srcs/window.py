from mlx import Mlx
from typing import Any, List


class MazeWindow():
    """Class to contain the maze displaying window"""
    
    def __init__(self):
        self._m = Mlx()
        self._ptr = self._m.mlx_init()
        self._win = None
        self.fg_color: int = 0xeeeeeeff
        self.bg_color: int = 0x99ff55ff
        self.hl_color: int = 0xff00ffff
        self.margin: int = 10
        self.cell_size: int = 20
        self.wall_size: int = 4
    
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
                self.draw_cell(self.cell_size * x + self.margin - self.wall_size // 2,
                    self.cell_size * y + self.margin - self.wall_size // 2, rows[y][x])

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

    def render(self, maze: str) -> None:
        """Receives the maze data and creates a window to draw it"""
       
        # Setting user interaction:
        def mykey(keynum: int, stuff: Any):
            """Captures key release events"""
            # 'q' to exit
            if keynum == 113:
                self._m.mlx_destroy_window(self._ptr, self._win)
                self._m.mlx_release(self._ptr)

        def close_window(stuff: Any):
            """Captures ClientMessage events (WM_DELETE_WINDOW)"""
            print(stuff)
            self._m.mlx_destroy_window(self._ptr, self._win)
            self._m.mlx_release(self._ptr)

        # Defining maze dimentions:
        rows: List[str] = maze.strip("\n").split("\n")
        width = len(rows[0])
        height = len(rows)

        # Creating window with maze size:
        self._win = self._m.mlx_new_window(self._ptr,
                self.cell_size * width + 2 * self.margin,
                self.cell_size * height + 2 * self.margin, "A_Maze_Ing!")
        self._m.mlx_clear_window(self._ptr, self._win)
      
        # Draw the maze:
        self.paint_bg(width, height)
        self.draw_maze(width, height, rows)
        
        # Set hooks to capture events:
        self._m.mlx_hook(self._win, 33, 0, close_window, ["close window"])
        self._m.mlx_key_hook(self._win, mykey, [])
        self._m.mlx_loop(self._ptr)
