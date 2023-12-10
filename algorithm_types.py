from enum import Enum, unique
from functools import partial

@unique
class BinPackingAlgorithmType(Enum):
    """
    Enum for packing algorithms.
    """
    shelf = "Shelf"
    skyline = "Skyline"
    maxrects = "MaximalRectangle"
    guillotine =  "Guillotine"


@unique
class BinHeuristicType(Enum):
    """
    Enum for packing heuristic both for the bin and item placement.
    """
    next_fit = "NextFit"
    first_fit = "FirstFit"
    best_area_fit = "BestAreaFit"
    worst_area_fit = "WorstAreaFit"
    best_width_fit = "BestWidthFit"
    worst_width_fit = "WorstWidthFit"
    best_height_fit = "BestHeightFit"
    worst_height_fit = "WorstHeightFit"


@unique
class SortStrategy(Enum):
    """
    Enum for sorting strategies.
    """
    # No sorting
    NONE: None = None
    # Sort by area, descending
    AREA_DESC = partial(lambda item: -item.area)
    # Sort by area, ascending
    AREA_ASC = partial(lambda item: item.area)
    # Sort by width, descending
    WIDTH_DESC = partial(lambda item: -item.width)
    # Sort by width, ascending
    WIDTH_ASC = partial(lambda item: item.width)
    # Sort by height, descending
    HEIGHT_DESC = partial(lambda item: -item.height)
    # Sort by height, ascending
    HEIGHT_ASC = partial(lambda item: item.height)
    # Sort by perimeter, descending
    PERIMETER_DESC = partial(lambda item: -2 * (item.width + item.height))
    # Sort by perimeter, ascending
    PERIMETER_ASC = partial(lambda item: 2 * (item.width + item.height))
    # Sort by shorter site, descending
    SHORTER_SIDE_DESC = partial(lambda item: -min(item.width, item.height))
    # Sort by shorter site, ascending
    SHORTER_SIDE_ASC = partial(lambda item: min(item.width, item.height))
    # Sort by longer site, descending
    LONGER_SIDE_DESC = partial(lambda item: -max(item.width, item.height))
    # Sort by longer site, ascending
    LONGER_SIDE_ASC = partial(lambda item: max(item.width, item.height))
    # Sort by side difference, descending
    SIDE_DIFF_DESC = partial(lambda item: -abs(item.width - item.height))
    # Sort by side difference, ascending
    SIDE_DIFF_ASC = partial(lambda item: abs(item.width - item.height))
