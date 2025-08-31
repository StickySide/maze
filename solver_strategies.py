from abc import ABC, abstractmethod
from collections import deque
from helper_functions import get_nieghbors, remove_out_of_bounds_neighbors
from render_strategies import RenderStrategy


class SolvingStrategy(ABC):
    @abstractmethod
    def solve(
        self,
        size_x: int,
        size_y: int,
        corridors: set[tuple[int, int]],
        start: tuple[int, int],
        end: tuple[int, int],
        live: bool = False,
        live_speed_delay: float = 0.0,
        renderer: RenderStrategy | None = None,
    ) -> set[tuple[int, int]] | None:
        pass


# == Concrete Classes ==
class DFSRecursiveSolver(SolvingStrategy):
    def solve(
        self,
        size_x: int,
        size_y: int,
        corridors: set[tuple[int, int]],
        start: tuple[int, int],
        end: tuple[int, int],
        live: bool = False,
        live_speed_delay: float = 0.0,
        renderer: RenderStrategy | None = None,
    ) -> set[tuple[int, int]] | None:
        visited = {start}  # Track visited cells
        frontier_path = {start}  # Track the current path being explored

        def dfs(next_cell: tuple[int, int]) -> set[tuple[int, int]]:
            """Performs a depth-first search to find a path to the end cell.

            Arguments:
                next_cell -- The current cell being explored.

            Returns:
                A set of coordinates representing the path to the end cell, or an empty set if no path exists.
            """
            nbrs = get_nieghbors(next_cell, 1)
            nbrs = remove_out_of_bounds_neighbors(nbrs, size_x, size_y)

            if live and renderer:
                print(
                    renderer.render(
                        size_x=size_x,
                        size_y=size_y,
                        start=start,
                        end=end,
                        corridors=corridors,
                        search_q={next_cell},
                        solution_path=frontier_path,
                        visited_cells=visited,
                        live=live,
                        live_speed_delay=live_speed_delay,
                    )
                )

            if not nbrs:  # If there are no valid neighboring cells...
                return set()
            elif end in nbrs:  # We found the end!
                return {end}
            elif nbrs:  # If valid cells remain to be explored
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
                print(
                    renderer.render(
                        size_x=size_x,
                        size_y=size_y,
                        start=start,
                        end=end,
                        corridors=corridors,
                        visited_cells=None,
                        solution_path=path,
                        live=live,
                    )
                )

        return path


class BFSSolver(SolvingStrategy):
    def solve(
        self,
        size_x: int,
        size_y: int,
        corridors: set[tuple[int, int]],
        start: tuple[int, int],
        end: tuple[int, int],
        live: bool = False,
        live_speed_delay: float = 0.0,
        renderer: RenderStrategy | None = None,
    ) -> set[tuple[int, int]] | None:
        search_queue = deque([start])  # Search queue with start added
        searched = {start}  # Mark the start as searched
        parent = {}

        while search_queue:
            cell = search_queue.popleft()  # Pop the next coordinate
            if cell == end:  # End found!: reconstruct path
                path = [cell]
                while path[-1] != start:
                    path.append(parent[path[-1]])
                path.reverse()
                if live and renderer:  # Render solution if live
                    print(
                        renderer.render(
                            size_x=size_x,
                            size_y=size_y,
                            corridors=corridors,
                            solution_path=set(path),
                            start=start,
                            end=end,
                            live_speed_delay=live_speed_delay,
                            live=live,
                        )
                    )
                return set(path)

            elif cell in corridors:  # Found new empty hallway/start
                for nbr in get_nieghbors(cell, step=1):
                    if (
                        nbr not in searched and nbr in corridors
                    ):  # If the cell isnt a wall or hasnt been visited...
                        search_queue.append(nbr)  # Explore further later...
                        searched.add(nbr)  # Mark visited
                        parent[nbr] = cell  # Record the neighbors parent

            if live and renderer:
                print(
                    renderer.render(
                        size_x=size_x,
                        size_y=size_y,
                        corridors=corridors,
                        search_q=set(search_queue),
                        visited_cells=searched,
                        start=start,
                        end=end,
                        live_speed_delay=live_speed_delay,
                        live=live,
                    )
                )

        else:  # Queue exhausted: no path exists
            return None
