from mlx import Mlx
from typing import Any, List


class Window():
    """Testing class for graphical library"""
    def __init__(self):
        self._m = Mlx()
        self._ptr = self._m.mlx_init()
        self._win = None
        self.fg_color: int = 0xeeeeeeff
        self.bg_color: int = 0x222200ff
        self.hl_color: int = 0x0000ffff
        self.margin = 10

    def draw_cell(self, x_offset: int, y_offset: int, value: str) -> None:
        for x in range(0, 22):
            for y in range(0, 22):
                if x < 3  or x >= 19 or y < 3 or y >= 19:
                    self._m.mlx_pixel_put(
                            self._ptr, self._win, x + x_offset, y + y_offset, self.fg_color)
                else:
                    self._m.mlx_pixel_put(
                            self._ptr, self._win, x + x_offset, y + y_offset, self.bg_color)
                if x == 6 and y == 0:
                    self._m.mlx_string_put(
                            self._ptr, self._win, x + x_offset, y + y_offset,
                            self.fg_color, value)



    def render(self, maze: str) -> None:
        
        def mykey(keynum: int, stuff: Any):
            # 'q' to exit
            if keynum == 113:
                self._m.mlx_destroy_window(self._ptr, self._win)
                self._m.mlx_release(self._ptr)

        rows: List[str] = maze.strip("\n").split("\n")
        width = len(rows[0])
        height = len(rows)

        # Create window with maze size:
        self._win = self._m.mlx_new_window(self._ptr, 20 * width + 2 * self.margin,
                20 * height + 2 * self.margin, "A_Maze_ing!")
        self._m.mlx_clear_window(self._ptr, self._win)
        
        for x in range(0, width):
            for y in range(0, height):
                self.draw_cell(20 * x + self.margin - 1, 20 * y + self.margin -1, rows[y][x])

        self._m.mlx_key_hook(self._win, mykey, [])
        self._m.mlx_loop(self._ptr)

