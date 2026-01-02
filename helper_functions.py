Coord = tuple[int, int]  # Coord: Type alias for a coordinate pair (x, y) in the maze.


def get_neighbors(
    coord: tuple[int, int],
    step: int,
    size_x: int | None = None,
    size_y: int | None = None,
    exclude: set[tuple[int, int]] | None = None,
) -> set[tuple[int, int]]:
    """Gets the 4 neighbors of a coordinate

    Arguments:
        coord -- Base coordinate
        step -- Distance from base coordinate to grab neighbors

    Returns:
        Set of neighbor coordinates
    """
    if exclude is None:
        exclude = set()
    if size_x and size_y:
        nbrs = [
            (coord[0], coord[1] - step),  # North
            (coord[0] + step, coord[1]),  # East
            (coord[0], coord[1] + step),  # South
            (coord[0] - step, coord[1]),  # West
        ]
        return {nbr for nbr in nbrs if 0 < nbr[0] < size_x - 1 and 0 < nbr[1] < size_y - 1 and nbr not in exclude}
    else:
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
    """Removes neighbors that fall outside the grid
    Arguments:
        neighbors -- Set of neighbor coordinates
        size_x -- Size of grid in x direction
        size_y -- Size of grid in y direction
    Returns:
        List of in-bounds neighbor coordinates
    """
    in_bounds_nbrs: list[Coord] = []
    for nbr in neighbors:
        if (size_x - 1) > nbr[0] > 0 and (size_y - 1) > nbr[1] > 0:
            in_bounds_nbrs.append(nbr)
    return in_bounds_nbrs
