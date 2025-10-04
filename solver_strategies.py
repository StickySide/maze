from abc import ABC, abstractmethod
from collections import deque
from random import shuffle
from helper_functions import (
    get_neighbors,
    Coord,
    remove_out_of_bounds_neighbors,
)
from render_strategies import RenderStrategy


class SolvingStrategy(ABC):
    @abstractmethod
    def solve(
        self,
        size_x: int,
        size_y: int,
        corridors: set[Coord],
        start: Coord,
        end: Coord,
        live: bool = False,
        fps: float = 0.0,
        renderer: RenderStrategy | None = None,
    ) -> set[Coord] | None:
        pass


# == Concrete Classes ==
class DFSRecursiveSolver(SolvingStrategy):
    def solve(
        self,
        size_x: int,
        size_y: int,
        corridors: set[Coord],
        start: Coord,
        end: Coord,
        live: bool = False,
        fps: float = 0.0,
        renderer: RenderStrategy | None = None,
    ) -> set[Coord] | None:
        visited = {start}  # Track visited cells
        frontier_path = {start}  # Track the current path being explored

        def dfs(next_cell: Coord) -> set[Coord]:
            """Performs a depth-first search to find a path to the end cell.

            Arguments:
                next_cell -- The current cell being explored.

            Returns:
                A set of coordinates representing the path to the end cell, or an empty set if no path exists.
            """
            nbrs = get_neighbors(next_cell, 1)
            nbrs = remove_out_of_bounds_neighbors(nbrs, size_x, size_y)

            if live and renderer:
                renderer.render_to_screen(
                    size_x=size_x,
                    size_y=size_y,
                    start=start,
                    end=end,
                    corridors=corridors,
                    search_q={next_cell},
                    solution_path=frontier_path,
                    visited_cells=visited,
                    fps=fps,
                )

            if not nbrs:  # If there are no valid neighboring cells...
                return set()
            elif end in nbrs:  # We found the end!
                return {end}
            elif nbrs:  # If valid cells remain to be explored
                nbrs = list(nbrs)
                shuffle(nbrs)
                for nbr in nbrs:
                    if nbr not in visited and nbr in corridors:
                        visited.add(nbr)  # Mark valid neighbors visited
                        frontier_path.add(nbr)
                        if solution := dfs(nbr):
                            return solution.union({nbr})
            frontier_path.remove(next_cell)
            return set()  # If no solution is found in any neighbors

        path = dfs(start)

        if live and renderer:
            if live and renderer:
                renderer.render_to_screen(
                    size_x=size_x,
                    size_y=size_y,
                    start=start,
                    end=end,
                    corridors=corridors,
                    visited_cells=None,
                    solution_path=path,
                )

        return path


class DFSSolver(SolvingStrategy):
    def reconstruct(
        self,
        parents: dict[Coord, Coord],
        start_cell: Coord,
        end_cell: Coord,
    ) -> set[Coord]:
        path = [end_cell]
        while path[-1] != start_cell:
            path.append(parents[path[-1]])
        path.reverse()
        return set(path)

    def solve(
        self,
        size_x: int,
        size_y: int,
        corridors: set[Coord],
        start: Coord,
        end: Coord,
        live: bool = False,
        fps: float = 0.0,
        renderer: RenderStrategy | None = None,
    ) -> set[Coord] | None:
        search_q: list[Coord] = [start]
        visited: set[Coord] = {start}
        frontier_path: set[Coord] = {start}
        parents: dict[Coord, Coord] = {}

        while search_q:
            current_cell = search_q.pop()
            nbrs = get_neighbors(
                coord=current_cell,
                step=1,
                size_x=size_x,
                size_y=size_y,
                exclude=visited,
            )
            if not nbrs:
                continue
            elif end in nbrs:
                path = self.reconstruct(parents, start, current_cell)
                if live and renderer:
                    renderer.render_to_screen(
                        size_x=size_x,
                        size_y=size_y,
                        start=start,
                        end=end,
                        corridors=corridors,
                        solution_path=set(path),
                        fps=fps,
                    )

                return set(path)
            elif nbrs:
                nbrs = list(nbrs)
                shuffle(nbrs)
                for nbr in nbrs:
                    if nbr not in visited and nbr in corridors:
                        visited.add(nbr)
                        search_q.append(nbr)
                        frontier_path.add(nbr)
                        parents[nbr] = current_cell
                if live and renderer:  # Render solution if live
                    renderer.render_to_screen(
                        size_x=size_x,
                        size_y=size_y,
                        start=start,
                        end=end,
                        corridors=corridors,
                        search_q={current_cell},
                        solution_path=self.reconstruct(parents, start, current_cell),
                        visited_cells=visited,
                        fps=fps,
                    )

        else:
            return set()


class BFSSolver(SolvingStrategy):
    def solve(
        self,
        size_x: int,
        size_y: int,
        corridors: set[Coord],
        start: Coord,
        end: Coord,
        live: bool = False,
        fps: float = 0.0,
        renderer: RenderStrategy | None = None,
    ) -> set[Coord] | None:
        search_queue = deque([start])  # Search queue with start added
        searched = {start}  # Mark the start as searched
        parent: dict[Coord, Coord] = {}

        def _reconstruct_path() -> list[
            Coord
        ]:  # Helper function to reconstruct path if a solution is found
            path: list[Coord] = [cell]
            while path[-1] != start:
                path.append(parent[path[-1]])
            path.reverse()
            if live and renderer:  # Render solution if live
                renderer.render_to_screen(
                    size_x=size_x,
                    size_y=size_y,
                    corridors=corridors,
                    solution_path=set(path),
                    start=start,
                    end=end,
                    fps=fps,
                )
            return path

        # Main solving loop
        while search_queue:
            cell = search_queue.popleft()  # Pop the next coordinate
            if cell == end:  # End found!: reconstruct path
                return set(_reconstruct_path())

            elif cell in corridors:  # Found new empty hallway/start
                for nbr in get_neighbors(cell, step=1):
                    if (
                        nbr not in searched and nbr in corridors
                    ):  # If the cell isn't a wall or hasn't been visited...
                        search_queue.append(nbr)  # Explore further later...
                        searched.add(nbr)  # Mark visited
                        parent[nbr] = cell  # Record the neighbors parent

            adjusted_fps: float = fps * len(search_queue)

            if live and renderer:
                renderer.render_to_screen(
                    size_x=size_x,
                    size_y=size_y,
                    corridors=corridors,
                    search_q={cell},
                    solution_path=set(search_queue),
                    visited_cells=searched,
                    start=start,
                    end=end,
                    fps=adjusted_fps,
                )

        else:  # Queue exhausted: no path exists
            return None
