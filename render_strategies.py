from abc import ABC, abstractmethod
from time import sleep


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
