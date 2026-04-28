from mlx import Mlx
from typing import Any, List, Tuple, Dict
from .maze import Maze
from .color import Color
from .maze_generator import MazeGenerator

class MazeWindow():
    """Class to contain the maze displaying window"""

    def __init__(self, config: Dict[str, Any]):
        self._m = Mlx()
        self._generator: MazeGenrator = MazeGenerator(**config)
        self._ptr = self._m.mlx_init()
        self._win = None
        self.fg_color: int = 0xeeeeeeff
        self.bg_color: int = 0xff113355
        self.hl_color: int = 0xff00ffff
        self.margin: int = 10
        self.cell_size: int = 20
        self.wall_size: int = 4
        self.path_visible = True
        self.maze: Maze = Maze([[int('0x' + value, 16) for value in row] for row in
"""9515391539551795151151153
EBABAE812853C1412BA812812
96A8416A84545412AC4282C2A
C3A83816A9395384453A82D02
96842A852AC07AAD13A8283C2
C1296C43AAB83AA92AA8686BA
92E853968428444682AC12902
AC3814452FA83FFF82C52C42A
85684117AFC6857FAC1383D06
C53AD043AFFFAFFF856AA8143
91441294297FAFD501142C6BA
AA912AC3843FAFFF82856D52A
842A8692A92B8517C4451552A
816AC384468285293917A9542
C416928513C443A828456C3BA
91416AA92C393A82801553AAA
A81292AA814682C6A8693C6AA
A8442C6C2C1168552C16A9542
86956951692C1455416928552
C545545456C54555545444556""".strip("\n").split("\n")],
        config["width"],
        config["height"],
        config["entry"],
        config["exit"],
        "SWSESWSESWSSSEESEEENEESESEESSSEEESSSEEENNENEE")
    
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

    def draw_cell(self, x_offset: int, y_offset: int, code: int) -> None:
        """Recieves a position to draw a cell and a hex value coding for
        open and closed walls"""    

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
                elif code == 0xF:
                    self._m.mlx_pixel_put(
                            self._ptr, self._win, x + x_offset, y + y_offset, self.hl_color)

    def draw_instructions(self, width: int, height: int) -> None:
        """Prints the instructions for user interaction, distributing them
        accordingly to the maze/window size"""
        
        #print(width * self.cell_size)
        instructions: str = "(c) color | (s) solution | (f) pattern | (q) quit"
        space = width * self.cell_size
        length = len(instructions) * 10 + 10
        #print(space - length)
        
        # check if there is enough to show instructions in line:
        if space >=  length:
            self._m.mlx_string_put(
                    self._ptr, self._win,
                    self.margin + self.wall_size + (space - length) // 2,
                    height * self.cell_size + self.margin + self.wall_size + 10,
                    0xffcccccc, instructions)

    def render(self) -> None:
        """Creates the window and draws the maze on it"""
       
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

            # 'f' to change walls color:
            if keynum == 102:
                self.hl_color = Color.get_random_color()
                self.draw_maze(maze.width, maze.height, maze.rows)

            # 'g' to regenerate:
            if keynum == 103: #                             Connection w/ MazeGenerator!!!
                self.maze.rows = self._generator.show() #  <-----------------------
                self.draw_maze(self.maze.width, self.maze.height, self.maze.rows)

        def close_window(stuff: Any):
            """Captures ClientMessage events (WM_DELETE_WINDOW)"""
            print(stuff)
            self._m.mlx_destroy_window(self._ptr, self._win)
            self._m.mlx_release(self._ptr)

        maze = self.maze

        # Creating window with maze size:
        self._win = self._m.mlx_new_window(self._ptr,
                self.cell_size * maze.width + 2 * self.margin + self.wall_size,
                self.cell_size * maze.height + 2 * self.margin + self.wall_size + 30,
                "A_Maze_Ing!")
        self._m.mlx_clear_window(self._ptr, self._win)
      
        # Draw the maze:
        self.paint_bg(maze.width, maze.height)
        self.draw_maze(maze.width, maze.height, maze.rows)

        # Draw start and exit:
        self.draw_single_block(maze.start, 0xff00ff00)
        self.draw_single_block(maze.exit, 0xffff0000)
        self.draw_path(maze.start, maze.path, 0xff888888)

        # Write instructions for user interaction:
        self.draw_instructions(maze.width, maze.height)
        
        # Set hooks to capture events:
        self._m.mlx_hook(self._win, 33, 0, close_window, ["close window"])
        self._m.mlx_key_hook(self._win, mykey, ["key pressed"])
        self._m.mlx_loop(self._ptr)
