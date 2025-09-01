from __future__ import annotations
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

from time import time


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
    fps: float = 0.0
    solution_path: set[tuple[int, int]] | None = None
    corridors: set[tuple[int, int]] | None = None
    title_text: bool = False

    def generate(self) -> None:
        self.corridors = self.gen_strat.generate(
            self.size_x,
            self.size_y,
            renderer=self.rend_strat,
            live=self.live,
            fps=self.fps,
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
                fps=self.fps,
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
            title_text=f"Generator: {self.gen_strat.__class__.__name__} | Solver: {self.solve_strat.__class__.__name__}"
            if self.title_text
            else None,
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
    maze = Maze(
        size_x=20,
        size_y=20,
        gen_strat=RandomPrims(),
        solve_strat=DFSSolver(),
        rend_strat=ASCIIRender(),
        live=True,
        fps=60,
        title_text=True,
    )

    maze.generate()
    # maze.hole_punch(200)
    maze.solve()

    # dfs_times = []
    # bfs_times = []
    # for i in range(100):
    #     start_time = time()
    #     maze.solve()
    #     end_time = time()
    #     dfs_solution = maze.render()
    #     total_time = end_time - start_time
    #     dfs_times.append(total_time)
    #     print(f"Iteration {i} time: {total_time}")

    # maze.solve_strat = BFSSolver()
    # for i in range(100):
    #     start_time = time()
    #     maze.solve()
    #     end_time = time()
    #     dfs_solution = maze.render()
    #     total_time = end_time - start_time
    #     bfs_times.append(total_time)
    #     print(f"Iteration {i} time: {total_time}")

    # print(
    #     f"DFS Solver -- Average time for 100 solutions: {sum(dfs_times) / len(dfs_times)}"
    # )
    # print(
    #     f"BFS Solver -- Average time for 100 solutions: {sum(bfs_times) / len(bfs_times)}"
    # )
