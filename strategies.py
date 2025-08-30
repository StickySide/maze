from __future__ import annotations
from random import choice, randint
from abc import ABC, abstractmethod
from collections import deque


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
    ) -> str:
        pass


# == Helper Functions ==
def get_neighbors(coord: tuple[int, int], step: int) -> set[tuple[int, int]]:
    """Gets the 4 nieghbors of a coordinate

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


# == Concrete classes==
class ASCIIRender(RenderStrategy):
    def move_cursor_to_upper_left(self):
        print("\x1b[H", end="")

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
    ) -> str:
        lines = ["\x1b[H"]  # Cursor to upper left
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
    def get_unvisited_nieghbors(
        self, neighbors: set[tuple[int, int]], visited: set
    ) -> set[tuple[int, int]] | None:
        return neighbors - visited

    # Remove neighbors that fall outside the grid
    def remove_out_of_bounds_nieghbors(
        self, nieghbors: set[tuple[int, int]], size_x: int, size_y: int
    ) -> list[tuple[int, int]] | None:
        in_bounds_nbrs = []
        for nbr in nieghbors:
            if (size_x - 1) > nbr[0] > 0 and (size_y - 1) > nbr[1] > 0:
                in_bounds_nbrs.append(nbr)
        return in_bounds_nbrs

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
            nbrs = get_neighbors(current_cell, 2)
            unvisited_nbrs = self.get_unvisited_nieghbors(nbrs, visited)

            if unvisited_nbrs:
                unvisited_nbrs = self.remove_out_of_bounds_nieghbors(
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
                    )
                )

        else:
            return corridors


class BFSSolver(SolvingStrategy):
    def solve(
        self,
        size_x: int,
        size_y: int,
        corridors: set[tuple[int, int]],
        start: tuple[int, int],
        end: tuple[int, int],
        live: bool = False,
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
                        )
                    )
                return set(path)

            elif cell in corridors:  # Found new empty hallway/start
                for nbr in get_neighbors(cell, step=1):
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
                    )
                )

        else:  # Queue exhausted: no path exists
            return None
