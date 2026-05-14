*This project has been created as part of the 42 curriculum by jericard, slenti.*

# A-Maze-Ing

## Description

A-Maze-Ing is a maze generator and interactive visualizer built in Python. The program
reads a configuration file to define the maze parameters, generates the maze
procedurally, and renders it in a graphical window where the user can interact with it
in real time.

Every generated maze contains a hidden **"42" pattern** embedded as part of its wall
structure — a tribute to the school.

The core generation logic is encapsulated in a standalone Python package (`mazegen`)
that can be installed and reused independently of the graphical application.

### Maze Generation

Two algorithms are available:

**Depth-First Search (DFS)** — the default. Starts from the entry cell and randomly
carves passages through unvisited neighbors, backtracking via a stack when it hits a
dead end. Fast, memory-efficient, and produces mazes with long winding corridors.

**Wilson's Algorithm** — an alternative selected via `ALT_ALGORITHM=True`. Uses
loop-erased random walks to produce a more uniform distribution of maze shapes, at the
cost of being slower on larger grids.

Both algorithms support two modes:
- **Perfect** (`PERFECT=True`): exactly one path between entry and exit cells.
- **Imperfect** (`PERFECT=False`): extra connections are added, creating loops and
  multiple paths between entry and exit cells.

After generation, a **BFS** pass finds the shortest path from entry to exit and stores
it as the maze solution attribute.

### Graphics

The graphical window is powered by **MinilibX**, a lightweight X11-based graphics
library developed at 42. It renders the maze pixel by pixel and captures keyboard
events for real-time interaction. For this reason, the project runs on **Linux only**.

---

## Instructions

> This project runs on **Linux only** due to its dependency on MinilibX, a graphical
> library that requires X11 — the display system used by most Linux distributions to
> render graphical windows.
> Running the project on other operating systems may be possible via Docker, but this
> is not covered by this project and is left to the user.

### Dependencies

- Python ≥ 3.10
- pip
- X11 (pre-installed on most Linux distributions)
- `mlx-2.2-py3-none-any.whl` — must be present at the root of the project

### Configuration file

Edit `config.txt` before running to customize the maze:

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `WIDTH` | int | yes | Number of columns (2–50) |
| `HEIGHT` | int | yes | Number of rows (2–50) |
| `ENTRY` | x,y | yes | Entry cell coordinates |
| `EXIT` | x,y | yes | Exit cell coordinates (≠ ENTRY) |
| `OUTPUT_FILE` | str | yes | Path to save the maze output file |
| `PERFECT` | TRUE/FALSE | yes | Perfect maze (unique path) or not |
| `SEED` | int | no | Fixed seed for reproducible results |
| `ALT_ALGORITHM` | TRUE/FALSE | no | Use Wilson's algorithm instead of DFS |

Example `config.txt`:
```
WIDTH=15
HEIGHT=15
ENTRY=0,0
EXIT=14,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=
ALT_ALGORITHM=False
```

### Using the mazegen module

The `mazegen` package can also be used independently in any Python project:

```python
from mazegen.maze_generator import MazeGenerator
from typing import List, Tuple, Optional

gen: MazeGenerator = MazeGenerator(
    width=15,
    height=15,
    entry=(0, 0),
    exit=(14, 14),
    perfect=True,
    seed=42,
    alt_algorithm=False
)

gen.generate()

# Access the maze grid
grid: List[List[int]] = gen.maze

# Each cell is a hex value where each bit represents a wall:
# bit 0 (0x1) → North | bit 1 (0x2) → East
# bit 2 (0x4) → South | bit 3 (0x8) → West
cell: int = gen.maze[y][x]
north_open: bool = not (gen.maze[y][x] & 0x1)
east_open: bool  = not (gen.maze[y][x] & 0x2)
south_open: bool = not (gen.maze[y][x] & 0x4)
west_open: bool  = not (gen.maze[y][x] & 0x8)

# Access the solution (BFS shortest path)
solution: List[Tuple[int, int]] = gen.solution  # ordered (x, y) coordinates
```

### Interactive controls

Once the window is open, the following keys are available:

| Key | Action |
|-----|--------|
| `s` | Show / hide solution path |
| `c` | Randomize wall color |
| `f` | "42 pattern" highlight color animation |
| `g` | Regenerate maze (new random maze, same config) |
| `a` | Switch algorithm and regenerate the maze
| `p` | Player mode (use arrow keys to explore the maze) |
| `m` | Show instructions menu |
| `Esc` | Exit the menu / Escape path animation / Exit win screen |
| `q` | Exit the program |

### Output file

After closing the window, the current maze is saved to the file defined in `OUTPUT_FILE`.
Format:

```
<hex row 1>
<hex row 2>
...
<entry_x>,<entry_y>
<exit_x>,<exit_y>
<NESW solution path>
```

Each row is a sequence of hex values (`0`–`F`), one per cell. The solution path is
encoded as a string of cardinal directions (`N`, `E`, `S`, `W`) from entry to exit.

### Installation

Clone the repository and run:

```bash
make build
```
To build `mazegen` package.  
  
Once it's created, run:

```bash
make install
```
This will:
1. Create a virtual environment and upgrade pip
2. Install Python dependencies from `requirements.txt`, including the MinilibX library
   from the local wheel file (`mlx-2.2-py3-none-any.whl`)
3. Install the `mazegen` package locally

### Running the program

```bash
make run
```

Or manually (by entering the virtual environment and running the main script directly):

```bash
source .venv/bin/activate
python3 a_maze_ing.py config.txt
```

Once done, exit the vitual environment with:

```bash
deactivate
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

---

## Team & Project Management

### Roles

| Member | Primary Responsibilities |
|--------|--------------------------|
| **jericard** | `mazegen` package — generation algorithms (DFS & Wilson's), BFS solver, the "42" pattern, `Makefile`, `pyproject.toml` |
| **slenti** | Input validation, config parser, graphical window, rendering, interactive controls, output file |

Both members collaborated throughout the entire project. Code reviews, debugging
sessions, and design decisions were shared — the roles above reflect primary ownership,
not exclusive work.

### Planning & Evolution

The project started with a study phase: we broke down the subject requirements, researched
maze generation algorithms, graph theory fundamentals, the mathematical properties of
perfect vs. imperfect mazes, and how MinilibX works. From there we moved into
development, building and testing incrementally — validation logic and other constraints
only became clear once we started coding, so solutions were designed as the project
evolved. The final phase was a joint testing round covering type checking (mypy),
linting (flake8), docstrings, type hints, and end-to-end simulation of the full workflow.

### What Worked & What Could Be Improved

**Worked well:** The incremental approach kept things moving without getting blocked.
Collaborating on debugging and sharing context early avoided large integration issues
at the end.

**Could be improved:** The narrow corridor constraint — the algorithms only carve
single-cell-wide passages, which is a side effect that was caught late in development.
It technically satisfies the subject's 3×3 corridor restriction, but a cleaner solution
would have been to handle this explicitly from the start rather than discovering it
mid-project.

### Tools

| Tool | Usage |
|------|-------|
| **Trello** | Task division and sprint tracking |
| **GitHub** | Version control — pull requests at the start of each feature, push to main only when complete |
| **Claude Code** | Quick information lookup and bug resolution during development |

---

## Resources

### Articles

- [Breadth-First Search (BFS): A Comprehensive Guide](https://medium.com/@tahsinsoyakk/breadth-first-search-bfs-a-comprehensive-guide-4672bbc5e48c) — BFS algorithm explained in depth
- [Depth-First Search: Fundamental Graph Algorithm](https://medium.com/data-science/deep-first-search-fundamental-graph-algorithm-d22991d5c144) — DFS concepts and implementation
- [The Ultimate Unbiased Maze Generation Technique](https://medium.com/@batu.senturk/the-ultimate-unbiased-maze-generation-technique-you-need-to-see-46123d5fec76) — Wilson's algorithm and unbiased maze generation

### Wikipedia

- [Maze Generation Algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm) — Overview of classic maze generation techniques
- [Maze Solving Algorithm](https://en.wikipedia.org/wiki/Maze-solving_algorithm) — Overview of maze solving approaches

### Videos

- [DFS in Python](https://www.youtube.com/watch?v=UAIDAxof3kA) — Practical DFS implementation walkthrough
- [BFS in Python](https://www.youtube.com/watch?v=gHHAZNuSTII) — Practical BFS implementation walkthrough
- [Graph Theory — Dot Dager](https://www.youtube.com/watch?v=lHJv5_1VL2o) — Graph theory fundamentals (Spanish)

### Graph Theory & Property Validation

- [Some Theorems on Trees — GeeksforGeeks](https://www.geeksforgeeks.org/dsa/some-theorems-on-trees/) — Tree theorems underlying the `complying()` validator: a connected graph with *N* nodes and *N − 1* edges is a tree, which is the formal basis for why `e == v` proves a perfect maze

### AI Usage

**Claude Code** was used during development for two specific purposes:
- Quick lookup of documentation and theoretical concepts
- Assisting in bug resolution during implementation

---

> **Note on additional required sections:** The additional content required by the
> subject (config file structure, algorithm choice and rationale, reusable code,
> team management) has been intentionally distributed across the relevant sections of
> this README rather than grouped into a separate section. This decision was made to
> keep the document practical and readable — each piece of information appears where
> it is most useful to the reader, not where it satisfies a checklist.
