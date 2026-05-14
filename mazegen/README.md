# mazegen - 1.0.0

A Python maze generator module that creates mazes using **Depth-First Search (DFS)**
or **Wilson's algorithm**. Supports perfect mazes (single unique path) and imperfect
mazes (multiple paths / loops), optional seeding for reproducibility, and automatic
BFS-based solution finding.

---

## Installation

This module is distributed as a wheel package. Install it with:

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

> Requires Python ≥ 3.10

---

## Quick Start

```python
from mazegen.maze_generator import MazeGenerator

gen = MazeGenerator(
    width=15,
    height=15,
    entry=(0, 0),
    exit=(14, 14),
    perfect=True
)

gen.generate()
```

After calling `generate()`, the maze grid and solution are available as attributes (see below).

---

## Custom Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `width` | `int` | yes | Number of columns (2–50) |
| `height` | `int` | yes | Number of rows (2–50) |
| `entry` | `Tuple[int, int]` | yes | Entry cell coordinates `(x, y)` |
| `exit` | `Tuple[int, int]` | yes | Exit cell coordinates `(x, y)` |
| `perfect` | `bool` | yes | `True` = unique path; `False` = multiple paths |
| `seed` | `int` | no | Fixed seed for reproducible mazes |
| `alt_algorithm` | `bool` | no | `True` = Wilson's algorithm; `False` = DFS (default) |

```python
# Reproducible imperfect maze using Wilson's algorithm
gen = MazeGenerator(
    width=20,
    height=20,
    entry=(0, 0),
    exit=(19, 19),
    perfect=False,
    seed=42,
    alt_algorithm=True
)

gen.generate()
```

---

## Accessing the Generated Structure

After calling `generate()`, the maze is stored in `gen.maze` as a 2D list of integers.
Each cell is a hex value (`0x0`–`0xF`) where each bit encodes whether a wall is present:

| Bit | Hex mask | Wall |
|-----|----------|------|
| 0 | `0x1` | North |
| 1 | `0x2` | East |
| 2 | `0x4` | South |
| 3 | `0x8` | West |

A value of `0` means all walls are open; `0xF` means all walls are closed. 
The `0xF` value is reserved to create a `42` shape design in the center of the maze (if its size allows it). 
All the other cells have at least one open wall, in order to achieve full connectivity.  

```python
from typing import List

gen.generate()

# Access the full grid
grid: List[List[int]] = gen.maze

# Read a single cell at (x, y)
cell: int = gen.maze[y][x]

# Check which walls are open at (x, y)
north_open: bool = not (gen.maze[y][x] & 0x1)
east_open: bool  = not (gen.maze[y][x] & 0x2)
south_open: bool = not (gen.maze[y][x] & 0x4)
west_open: bool  = not (gen.maze[y][x] & 0x8)
```

---

## Accessing the Solution

After `generate()`, the solution is stored in `gen.solution` as an ordered list of
`(x, y)` coordinates from `entry` to `exit`, computed via BFS (shortest path).

```python
from typing import List, Tuple

gen.generate()

# Full solution path as coordinates
solution: List[Tuple[int, int]] = gen.solution

# First and last cell
start: Tuple[int, int] = solution[0]   # == entry
end: Tuple[int, int]   = solution[-1]  # == exit

# Print each step
x: int
y: int
for step in solution:
    x, y = step
    print(f"→ ({x}, {y})")
```
