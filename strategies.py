from __future__ import annotations
from random import choice, randint
from abc import ABC, abstractmethod
from collections import deque
from time import sleep


# == Abstract Base Classes ==
class GenerationStrategy(ABC):
    @abstractmethod
    def generate(
        self,
        size_x: int,
        size_y: int,
        live: bool = False,
        renderer: RenderStrategy | None = None,
    ) -> set[tuple[int, int]]:
        pass


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


class RenderStrategy(ABC):
    @abstractmethod
    def render(
        self,
        size_x: int,
        size_y: int,
        start: tuple[int, int] | None = None,
        end: tuple[int, int] | None = None,
        corridors: set[tuple[int, int]] | None = None,
        solution_path: set[tuple[int, int]] | None = None,
        search_q: set[tuple[int, int]] | None = None,
        visited_cells: set[tuple[int, int]] | None = None,
        live: bool = False,
        live_speed_delay: float = 0.0,
    ) -> str:
        pass


# == Helper Functions ==
def get_nieghbors(coord: tuple[int, int], step: int) -> set[tuple[int, int]]:
    """Gets the 4 neighbors of a coordinate

    Arguments:
        coord -- Base coordinate
        step -- Distance from base coordinate to grab neighbors

    Returns:
        Set of neighbor coordinates
    """
    return {
        (coord[0], coord[1] - step),  # North
        (coord[0] + step, coord[1]),  # East
        (coord[0], coord[1] + step),  # South
        (coord[0] - step, coord[1]),  # West
    }

    # Remove neighbors that fall outside the grid


def remove_out_of_bounds_neighbors(
    neighbors: set[tuple[int, int]], size_x: int, size_y: int
) -> list[tuple[int, int]] | None:
    in_bounds_nbrs = []
    for nbr in neighbors:
        if (size_x - 1) > nbr[0] > 0 and (size_y - 1) > nbr[1] > 0:
            in_bounds_nbrs.append(nbr)
    return in_bounds_nbrs


# == Concrete classes==
class ASCIIRender(RenderStrategy):
    def render(
        self,
        size_x: int,
        size_y: int,
        start: tuple[int, int] | None = None,
        end: tuple[int, int] | None = None,
        corridors: set[tuple[int, int]] | None = None,
        solution_path: set[tuple[int, int]] | None = None,
        search_q: set[tuple[int, int]] | None = None,
        visited_cells: set[tuple[int, int]] | None = None,
        live: bool = False,
        live_speed_delay: float = 0.0,
    ) -> str:
        if live:
            lines = ["\x1b[H"]  # Cursor to upper left
        else:
            lines = []
        sleep(live_speed_delay)
        for y in range(size_y):
            line = []
            for x in range(size_x):
                if start and (x, y) == start:
                    line.append("\x1b[31mS\x1b[0m")
                elif end and (x, y) == end:
                    line.append("\x1b[34mE\x1b[0m")
                elif solution_path and (x, y) in solution_path:
                    line.append("\x1b[32m█\x1b[0m")
                elif search_q and (x, y) in search_q:
                    line.append("@")
                elif visited_cells and (x, y) in visited_cells:
                    line.append("\x1b[33m█\x1b[0m")
                elif corridors and (x, y) in corridors:
                    line.append(" ")  # Open corridor
                else:
                    line.append("█")  # solid wall
            lines.append("".join(line))
        return "\n".join(lines)


class RandomDFS(GenerationStrategy):
    # Filter out already visited neighbors
    def get_unvisited_neighbors(
        self, neighbors: set[tuple[int, int]], visited: set
    ) -> set[tuple[int, int]] | None:
        return neighbors - visited

    def generate(
        self,
        size_x: int,
        size_y: int,
        live: bool = False,
        renderer: RenderStrategy | None = None,
    ) -> set[tuple[int, int]]:
        """Main DFS maze generation algorithm/loop

        Returns:
            Set of coordinates representing the maze's corridors
        """
        corridors = set()  # Store carved corridor cells (including midpoints)
        visited = set()  # Track cells that have been visited by DFS
        search_q = []  # Stack (list used as LIFO) for DFS backtracking

        start_coord = (
            randint(0, size_x - 1),
            randint(0, size_y - 1),
        )  # Random start

        visited.add(start_coord)
        search_q.append(start_coord)

        while search_q:
            next_cell = None
            current_cell = search_q.pop()
            # Look two steps away (because midpoints represent walls)
            nbrs = get_nieghbors(current_cell, 2)
            unvisited_nbrs = self.get_unvisited_neighbors(nbrs, visited)

            if unvisited_nbrs:
                unvisited_nbrs = remove_out_of_bounds_neighbors(
                    unvisited_nbrs, size_x, size_y
                )

            if unvisited_nbrs:
                # Push current cell back (we'll return here if dead-end)
                search_q.append(current_cell)
                # Choose a random unvisited neighbor
                next_cell = choice(list(unvisited_nbrs))
                # Carve wall between current and next (the midpoint)
                mid = (
                    (current_cell[0] + next_cell[0]) // 2,
                    (current_cell[1] + next_cell[1]) // 2,
                )

                # Mark as visited and carve
                visited.add(next_cell)
                search_q.append(next_cell)
                corridors.add(mid)
                corridors.add(next_cell)

            if live and renderer:
                print(
                    renderer.render(
                        size_x=size_x,
                        size_y=size_y,
                        corridors=corridors,
                        solution_path=None,
                        start=None,
                        end=None,
                        live=live,
                    )
                )

        else:
            return corridors


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
