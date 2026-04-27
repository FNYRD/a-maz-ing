from typing import Tuple


class Maze():
	"""Class to contain maze data"""
	def __init__(self, maze: str, start_coord: Tuple[int, int],
            exit_coord: Tuple[int, int], path: str) -> None:
		self.maze = maze
		self.start = start_coord
		self.exit = exit_coord
		self.path = path
