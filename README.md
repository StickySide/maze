# Python Maze Generator & Solver

A powerful Python package for generating and solving mazes in the terminal with beautiful ASCII visualization and live animation support.

<!-- Insert demo GIF here showing the full generation and solving process -->
![Demo GIF Placeholder](./demos/full-demo.gif)

## Features

- **Multiple Generation Algorithms**: DFS, Prim's Algorithm, and Empty Maze
- **Multiple Solving Algorithms**: DFS (Iterative & Recursive), BFS
- **Live Animation**: Watch mazes being generated and solved in real-time
- **Customizable Visualization**: ASCII rendering with color-coded paths
- **Command-Line Interface**: Easy-to-use CLI with extensive options
- **Hole Punching**: Add random openings to make mazes more interesting
- **Flexible API**: Use as a library or standalone tool

## Quick Start

### Basic Command Line Usage
```bash
# Generate and solve a maze with default settings
python maze.py

# Generate a 50x30 maze using Prim's algorithm and solve with BFS
python maze.py -x 50 -y 30 --generator prim --solver bfs

# Watch live generation and solving with custom FPS
python maze.py --live --fps 15 --generator dfs --solver bfs
```

### Live Animation Example

![Depth first maze generation and solving](/demos/dfs-dfs.gif)

*Depth First Maze Generation and solving*

## Command Line Options

```
usage: Maze generator [-h] [-x WIDTH] [-y HEIGHT] [-g {dfs,prim}] [-s {dfs,bfs}] 
                      [-l] [-o HOLES] [-f FPS]

Generate mazes and solutions using various algorithms

options:
  -h, --help            show this help message and exit
  -x WIDTH, --width WIDTH
                        Width of maze (default: 40)
  -y HEIGHT, --height HEIGHT  
                        Height of maze (default: 20)
  -g {dfs,prim}, --generator {dfs,prim}
                        Generation algorithm (default: dfs)
  -s {dfs,bfs}, --solver {dfs,bfs}
                        Solving algorithm (default: bfs)
  -l, --live            Display generation/solution animated live
  -o HOLES, --holes HOLES
                        Number of walls to randomly delete (default: 0)
  -f FPS, --fps FPS     FPS for live animation (default: 30)
```

## Programming Interface

### Basic API Usage

```python
from maze import Maze
from generation_strategies import RandomPrims
from solver_strategies import BFSSolver
from render_strategies import ASCIIRender

# Create a maze
maze = Maze(
    size_x=50,
    size_y=30,
    gen_strat=RandomPrims(),
    solve_strat=BFSSolver(),
    rend_strat=ASCIIRender(),
)

# Generate and solve with live animation
maze.generate(live=True, fps=20)
solution = maze.solve(live=True, fps=10)

# ...or just print solution
print(solution)
```

### Custom Strategy Implementation

```python
from generation_strategies import GenerationStrategy
from helper_functions import Coord

class MyCustomGenerator(GenerationStrategy):
    def generate(self, size_x: int, size_y: int, **kwargs) -> set[Coord]:
        # Your custom generation logic here
        pass
```

## Requirements

- Python 3.9+
- No external dependencies (uses only standard library)

## Examples

### Large Maze with Holes
```bash
python maze.py -x 100 -y 40 --holes 50 --live --fps 30
```


## Contributing

Contributions are welcome! Some ideas for improvements:

- Additional generation algorithms (Wilson's, Eller's, etc.)
- New solving algorithms (A*, Dijkstra, etc.)
- Different rendering strategies (PNG export, web interface, etc.)
- Performance optimizations
- Unit tests

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

