from __future__ import annotations
from random import choice, randint
from abc import ABC, abstractmethod
from render_strategies import RenderStrategy
from helper_functions import get_nieghbors, remove_out_of_bounds_neighbors


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


class RandomPrims(GenerationStrategy):
    def generate(
        self,
        size_x: int,
        size_y: int,
        live: bool = False,
        renderer: RenderStrategy | None = None,
    ) -> set[tuple[int, int]]:
        start_coord = (
            randint(0, size_x - 1),
            randint(0, size_y - 1),
        )  # Random start

        corridors = {start_coord}
        visited = {start_coord}
        walls = get_nieghbors(start_coord, 2, size_x=size_x, size_y=size_y)

        while walls:
            # Randomly take a wall and make it a corridor and remove it from walls
            next_cell = choice(list(walls))
            corridors.add(next_cell)
            walls.remove(next_cell)

            # Add unvisited nieghbors of that new corridor to the wall list
            nbrs = get_nieghbors(next_cell, 2, size_x=size_x, size_y=size_y)
            nbrs = nbrs.difference(visited)
            walls.update(nbrs)
            visited.update(nbrs)

            if live and renderer:
                print(
                    renderer.render(
                        size_x=size_x,
                        size_y=size_y,
                        corridors=corridors,
                        live=True,
                    )
                )
        return corridors
