from __future__ import annotations
from dataclasses import dataclass
from random import choice
from strategies import (
    BFSSolver,
    GenerationStrategy,
    SolvingStrategy,
    RenderStrategy,
    RandomDFS,
    ASCIIRender,
)


@dataclass
class Maze:
    size_x: int
    size_y: int
    gen_strat: GenerationStrategy
    solve_strat: SolvingStrategy
    rend_strat: RenderStrategy

    def generate(self, live=False) -> None:
        self.corridors = self.gen_strat.generate(self.size_x, self.size_y)

        # Assign random start/end points
        self.start = choice(list(self.corridors))
        self.end = choice(list(self.corridors))
        while self.start[0] > 3:
            self.start = choice(list(self.corridors))
        while self.end[0] < self.size_x - 3:
            self.end = choice(list(self.corridors))

    def solve(self):
        self.solution_path = self.solve_strat.solve(
            corridors=self.corridors, start=self.start, end=self.end
        )

    def render(self, live=False) -> str:
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
        size_x=160,
        size_y=11,
        gen_strat=RandomDFS(),
        solve_strat=BFSSolver(),
        rend_strat=ASCIIRender(),
    )

    new_maze.generate()
    new_maze.solve()
    print(new_maze.render())
