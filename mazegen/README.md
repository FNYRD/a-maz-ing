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

---

## Verification

`gen.complying()` validates structural properties of the generated maze. It does not return a value — it prints three diagnostics to stdout.

```python
gen.generate()
gen.complying()
```

**Example output:**
```
Conexo = True
Perfect Argument = True
Perfect validator = True
Comply = True
```

### What it checks

The method runs a BFS from the entry cell and collects two counts:

| Symbol | Meaning |
|--------|---------|
| `v` | Number of reachable cells minus 1 (i.e. `visited − 1`) |
| `e` | Number of undirected edges between reachable cells (each wall opening counted once) |

Then it prints:

| Line | Expression | Meaning |
|------|-----------|---------|
| `Conexo` | `v == (width × height) − 16` | Every non-pattern cell is reachable from entry |
| `Perfect Argument` | value of `self.perfect` | The flag you passed at construction |
| `Perfect validator` | `e == v` | Whether the edge count satisfies the spanning-tree condition |
| `Comply` | `self.perfect == (e == v)` | Whether the maze behaves as declared |

The 16 subtracted from the total cell count corresponds to the cells occupied by the embedded `42` pattern, which are permanently walled off (`0xf`) and intentionally excluded from connectivity.

### Why `e == v` proves a perfect maze

A perfect maze is, graph-theoretically, a **spanning tree** of the grid: every cell is reachable and there are no loops. A tree on *N* nodes has exactly *N − 1* edges. Here `v = visited − 1`, so the condition `e == v` is equivalent to asserting *edges = nodes − 1* — the defining property of a tree.

If `e > v`, extra edges exist, meaning at least one loop is present → imperfect maze.  
If `e < v`, some cells are unreachable → disconnected maze (a generation bug).

`Comply = True` means the maze does what you asked: a perfect maze has no loops, an imperfect one has at least one.
