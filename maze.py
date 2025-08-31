from __future__ import annotations
from dataclasses import dataclass
from random import choice
from generation_strategies import GenerationStrategy, RandomDFS, RandomPrims
from render_strategies import RenderStrategy, ASCIIRender
from solver_strategies import (
    SolvingStrategy,
    DFSSolver,
    DFSRecursiveSolver,
    BFSSolver,
)


@dataclass
class Maze:
    size_x: int
    size_y: int
    gen_strat: GenerationStrategy
    solve_strat: SolvingStrategy
    rend_strat: RenderStrategy
    start_cell_buffer: int = 3
    end_cell_buffer: int = 3
    live: bool = False
    live_speed_delay: float = 0.0
    solution_path: set[tuple[int, int]] | None = None
    corridors: set[tuple[int, int]] | None = None

    def generate(self) -> None:
        self.corridors = self.gen_strat.generate(
            self.size_x,
            self.size_y,
            renderer=self.rend_strat,
            live=self.live,
            live_speed_delay=self.live_speed_delay,
        )

        # Assign random start/end points
        self.start = choice(list(self.corridors))
        self.end = choice(list(self.corridors))
        while self.start[0] > self.start_cell_buffer:
            self.start = choice(list(self.corridors))
        while self.end[0] < self.size_x - self.end_cell_buffer:
            self.end = choice(list(self.corridors))

    def solve(self) -> None:
        if self.corridors:
            self.solution_path = self.solve_strat.solve(
                size_x=self.size_x,
                size_y=self.size_y,
                corridors=self.corridors,
                start=self.start,
                end=self.end,
                live=self.live,
                live_speed_delay=self.live_speed_delay,
                renderer=self.rend_strat,
            )

    def render(self) -> str:
        """
        Renders the maze using the specified rendering strategy.

        Returns:
            str: The rendered maze as a string.
        """
        return self.rend_strat.render(
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


if __name__ == "__main__":
    new_maze = Maze(
        size_x=201,
        size_y=51,
        gen_strat=RandomDFS(),
        solve_strat=BFSSolver(),
        rend_strat=ASCIIRender(),
        live=False,
        live_speed_delay=0,
    )

    new_maze.generate()
    new_maze.hole_punch(500)
    new_maze.solve()
    bfs_solution = new_maze.render()

    new_maze.solve_strat = DFSSolver()
    new_maze.solve()
    dfs_solution = new_maze.render()

    print(bfs_solution)
    print(dfs_solution)
    print(bfs_solution == dfs_solution)
