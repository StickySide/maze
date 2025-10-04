from abc import ABC, abstractmethod
from time import sleep
from helper_functions import Coord


class RenderStrategy(ABC):
    @abstractmethod
    def _render(
        self,
        size_x: int,
        size_y: int,
        start: Coord | None = None,
        end: Coord | None = None,
        corridors: set[Coord] | None = None,
        solution_path: set[Coord] | None = None,
        search_q: set[Coord] | None = None,
        visited_cells: set[Coord] | None = None,
        live: bool = False,
        fps: int | None = None,
        title_text: str | None = None,
    ) -> str:
        pass

    def render_to_string(self, *args: object, **kwargs: object) -> str:
        return self._render(live=False, *args, **kwargs)  # type: ignore

    def render_to_screen(self, *args: object, **kwargs: object) -> None:
        print(self._render(live=True, *args, **kwargs))  # type: ignore


# == Concrete classes==
class ASCIIRender(RenderStrategy):
    def _render(
        self,
        size_x: int,
        size_y: int,
        start: Coord | None = None,
        end: Coord | None = None,
        corridors: set[Coord] | None = None,
        solution_path: set[Coord] | None = None,
        search_q: set[Coord] | None = None,
        visited_cells: set[Coord] | None = None,
        live: bool = False,
        fps: int | None = None,
        title_text: str | None = None,
    ) -> str:
        lines: list[str] = []
        if live:
            lines.append("\x1b[H")  # Cursor to upper left

        if title_text:
            lines.append(title_text)

        # FPS control
        if fps:
            sleep(1 / fps)

        for y in range(size_y):
            line: list[str] = []
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
        frame = "\n".join(lines)
        if live:
            print(frame)
        return frame
