from __future__ import annotations
import argparse
from dataclasses import dataclass
from random import choice
from generation_strategies import (
    EmptyMaze,
    GenerationStrategy,
    RandomDFS,
    RandomPrims,
)
from render_strategies import RenderStrategy, ASCIIRender
from solver_strategies import (
    SolvingStrategy,
    DFSSolver,
    DFSRecursiveSolver,
    BFSSolver,
)
from helper_functions import Coord
# from time import time


@dataclass
class Maze:
    size_x: int
    size_y: int
    gen_strat: GenerationStrategy
    solve_strat: SolvingStrategy
    rend_strat: RenderStrategy
    start_cell_buffer: int = 3
    end_cell_buffer: int = 3
    solution_path: set[Coord] | None = None
    corridors: set[Coord] | None = None
    title_text: bool = False
    default_fps: int = 30

    def generate(
        self, live: bool = False, fps: int | None = None, holes: int = 0
    ) -> None:
        if fps is None:
            fps = self.default_fps

        self.corridors = self.gen_strat.generate(
            self.size_x,
            self.size_y,
            renderer=self.rend_strat,
            live=live,
            fps=fps,
        )

        if holes > 0:
            self.hole_punch(holes)

        # Assign random start/end points
        self.start = choice(list(self.corridors))
        self.end = choice(list(self.corridors))
        while self.start[0] > self.start_cell_buffer:
            self.start = choice(list(self.corridors))
        while self.end[0] < self.size_x - self.end_cell_buffer:
            self.end = choice(list(self.corridors))

    def solve(
        self,
        live: bool = False,
        fps: float | None = None,
    ) -> set[Coord] | None:
        if fps is None:
            fps = self.default_fps

        if self.corridors:
            self.solution_path = self.solve_strat.solve(
                size_x=self.size_x,
                size_y=self.size_y,
                corridors=self.corridors,
                start=self.start,
                end=self.end,
                live=live,
                fps=fps,
                renderer=self.rend_strat,
            )
            return self.solution_path

    def render(self) -> str:
        """
        Renders the maze using the specified rendering strategy.

        Returns:
            str: The rendered maze as a string.
        """
        return self.rend_strat.render_to_string(
            size_x=self.size_x,
            size_y=self.size_y,
            corridors=self.corridors,
            solution_path=self.solution_path,
            start=self.start,
            end=self.end,
            title_text=f"Generator: {self.gen_strat.__class__.__name__} | Solver: {self.solve_strat.__class__.__name__}"
            if self.title_text
            else None,
        )

    def render_to_screen(self) -> None:
        self.rend_strat.render_to_screen(
            size_x=self.size_x,
            size_y=self.size_y,
            corridors=self.corridors,
            solution_path=self.solution_path,
            start=self.start,
            end=self.end,
        )

    def hole_punch(self, holes: int = 5) -> None:
        """
        Randomly adds holes to the maze by converting wall cells into corridors.

        Args:
            holes (int): The number of holes to punch in the maze.
        """
        if self.corridors:
            walls = [
                (x, y)
                for x in range(1, self.size_x - 1)
                for y in range(1, self.size_y - 1)
                if (x, y) not in self.corridors
            ]
            for _ in range(holes):
                self.corridors.add(choice(walls))


def generate_and_display_maze(
    x: int | None = None,
    y: int | None = None,
    gen_strat: GenerationStrategy | None = None,
    solve_strat: SolvingStrategy | None = None,
    rend_strat: RenderStrategy | None = None,
    holes: int | None = None,
    live: bool = False,
    fps: int | None = None,
) -> None:
    if not x:
        x = 40
    if not y:
        y = 20
    if not gen_strat:
        gen_strat = RandomDFS()
    if not solve_strat:
        solve_strat = BFSSolver()
    if not rend_strat:
        rend_strat = ASCIIRender()
    if not holes:
        holes = 0

    """Quick function to generate and display a maze. Used with argparse

    Args:
        x (int, optional): _description_. Defaults to 40.
        y (int, optional): _description_. Defaults to 40.
        gen_strat (GenerationStrategy, optional): _description_. Defaults to RandomDFS().
        solve_strat (SolvingStrategy, optional): _description_. Defaults to DFSSolver().
        rend_strat (RenderStrategy, optional): _description_. Defaults to ASCIIRender().
        holes (int, optional): _description_. Defaults to 0.
        live (bool, optional): _description_. Defaults to False.
        fps (int, optional): _description_. Defaults to 30.
    """
    maze: Maze = Maze(
        size_x=x,
        size_y=y,
        gen_strat=gen_strat,
        solve_strat=solve_strat,
        rend_strat=rend_strat,
    )

    maze.generate(live=live, fps=fps)
    if live:
        maze.solve(live=live, fps=fps)
    else:
        maze.solve()
        maze.render_to_screen()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Maze generator",
        description="Generate mazes and solutions using various algorithms",
    )

    # TODO: Add arguments for renderer
    parser.add_argument("-x", type=int, help="Width of maze. Default: 40")
    parser.add_argument("-y", type=int, help="Height of maze. Default: 20")
    parser.add_argument(
        "-g",
        "--generator",
        type=str,
        help="Maze generation algorithm. dfs (default) = Random depth first search, prim = Random prims",
    )
    parser.add_argument(
        "-s",
        "--solver",
        type=str,
        help="Solution algorithm. dfs = Depth first search, bfs (default) = Breadth first search",
    )
    parser.add_argument(
        "-l",
        "--live",
        action="store_true",
        help="Display generation/solution animated live.",
    )
    parser.add_argument(
        "-o",
        "--holes",
        type=int,
        help="Number of walls to randomly delete in the maze. Default: 0",
    )
    parser.add_argument(
        "-f", "--fps", type=int, help="FPS to run the live render at. Default: 30"
    )

    # TODO: Finish assigning variables from args
    # ? Does this even need to be assigned? Just pass args directly to function? Maybe yes so the variables can be controlled...
    args = parser.parse_args()
    x: int | None = args.x if args.x else None
    y: int | None = args.y if args.y else None
    holes: int | None = args.holes
    live: bool = args.live
    gen_strat: GenerationStrategy | None = None
    solve_strat: SolvingStrategy | None = None

    if args.generator == "dfs":
        gen_strat = RandomDFS()
    elif args.generator == "prim":
        gen_strat = RandomPrims()
    elif args.generator == "empty":
        gen_strat = EmptyMaze()

    if args.solver == "dfs":
        solve_strat = DFSSolver()
    elif args.solver == "bfs":
        solve_strat = BFSSolver()

    # TODO: Create function that returns a maze
    # TODO: Call function with args to create a maze and run it
    generate_and_display_maze(
        x=x,
        y=y,
        gen_strat=gen_strat,
        solve_strat=solve_strat,
        holes=holes,
        live=live,
        fps=args.fps,
    )
