from __future__ import annotations
from dataclasses import dataclass
from random import choice
from generation_strategies import GenerationStrategy, RandomDFS, RandomPrims
from render_strategies import RenderStrategy, ASCIIRender
from solver_strategies import SolvingStrategy, DFSRecursiveSolver, BFSSolver


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

    def generate(self, live=None) -> None:
        if not live:
            live = self.live

        self.corridors = self.gen_strat.generate(
            self.size_x, self.size_y, renderer=self.rend_strat, live=live
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
        return self.rend_strat.render(
            size_x=self.size_x,
            size_y=self.size_y,
            corridors=self.corridors,
            solution_path=self.solution_path,
            start=self.start,
            end=self.end,
        )


if __name__ == "__main__":
    new_maze = Maze(
        size_x=100,
        size_y=30,
        gen_strat=RandomPrims(),
        solve_strat=DFSRecursiveSolver(),
        rend_strat=ASCIIRender(),
        live=True,
        live_speed_delay=1,
    )

    new_maze.generate()
