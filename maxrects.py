from dataclasses import dataclass, field
import typing

# from dataclasses import dataclass, field
from typing import List, Dict

from algorithm_types import BinHeuristicType
from items_type import Bin, Item
from packing_algorithm import PackingAlgorithm


class AvailableRect(
    typing.NamedTuple(
        "AvailableRect", [("x", int), ("y", int), ("width", int), ("height", int)]
    )
):
    x: int
    y: int
    width: int
    height: int

    @property
    def area(self) -> int:
        return self.width * self.height


class MaxRectsAlgorithm(PackingAlgorithm):
    height: int
    width: int
    items: List[Item] = field(default_factory=list)
    rotation: bool = False

    def __init__(self, rotation: bool, heuristic: BinHeuristicType):
        super().__init__(rotation, heuristic)
        self.free_area = self.area
        self.bin_rects: Dict[str, List[AvailableRect]] = {}
        # self.available_rects = [AvailableRect(0, 0, self.width, self.height)]

    @property
    def area(self) -> int:
        return self.width * self.height

    def initialize_bin(self, bin: Bin) -> None:
        """
        Initialize a bin with just one available rect.

        :param bin: The bin to be initialized.
        """
        self.bin_rects[bin.id] = [AvailableRect(0, 0, bin.width, bin.height)]

    def check_item_fit(
        self, item: Item, available_rect: AvailableRect
    ) -> tuple[bool, bool]:
        """
        Check if an item fits in the given rect, considering the possibility of rotation.

        :param item: The item to be checked.
        :return: A tuple where the first element is a boolean indicating if the item fits,
                 and the second element is a boolean indicating if rotation is necessary.
        """
        fits_without_rotation = (
            item.width <= available_rect.width and item.height <= available_rect.height
        )
        needs_rotation = (
            self.rotation
            and item.height <= available_rect.width
            and item.width <= available_rect.height
        )

        if fits_without_rotation:
            return True, False
        elif needs_rotation:
            return True, True
        else:
            return False, False

    def insert_item(self, item: Item, available_rect: AvailableRect) -> bool:
        """
        Insert an item into the rect.

        :param item: The item to be inserted.
        :return: Boolean indicating whether the item was successfully inserted.
        """
        fits, needs_rotation = self.check_item_fit(item, available_rect)
        if fits:
            if needs_rotation:
                item.rotate()
            item.x, item.y = available_rect.x, available_rect.y
            self.items.append(item)
            self.free_area -= item.area
            return True
        return False

    def _split_rect(self, rect: AvailableRect, item: Item) -> List[AvailableRect]:
        """
        Split a rect into two rects, one part horizontally and one part vertically.

        :param rect: The rect to be split.
        :param item: The item to be inserted.
        :return: A list of two rects.
        """
        rects = []
        if rect.width > item.width:
            rects.append(
                AvailableRect(
                    rect.x + item.width, rect.y, rect.width - item.width, item.height
                )
            )
        if rect.height > item.height:
            rects.append(
                AvailableRect(
                    rect.x, rect.y + item.height, rect.width, rect.height - item.height
                )
            )
        rect1 = AvailableRect(
            rect.x + item.width, rect.y, rect.width - item.width, item.height
        )

        return rects

    def _item_diagonal_points(self, item: Item) -> tuple:
        """
        Get bottom left and top right points of an item.

        :param item: The item to get points from.
        :return: A tuple of two points.
        """
        return (item.x, item.y, item.x + item.width, item.y + item.height)

    def _item_rect_overlap(self, item: Item, rect: AvailableRect) -> tuple:
        """
        Check if an item and a rect overlap and return the overlapping area - bottom left and top right points.

        :param item: The item to be checked.
        :param rect: The rect to be checked.
        :return: A tuple of two points indicating the overlapping area.
        """
        item_x1, item_y1, item_x2, item_y2 = self._item_diagonal_points(item)
        rect_x1, rect_y1, rect_x2, rect_y2 = (
            rect.x,
            rect.y,
            rect.x + rect.width,
            rect.y + rect.height,
        )

        if (
            item_x1 < rect_x2
            and item_x2 > rect_x1
            and item_y1 < rect_y2
            and item_y2 > rect_y1
        ):
            x1 = max(item_x1, rect_x1)
            y1 = max(item_y1, rect_y1)
            x2 = min(item_x2, rect_x2)
            y2 = min(item_y2, rect_y2)
            return x1, y1, x2, y2

        return None

    def _cut_out_overlapped_area(
        self, overlapped_area: tuple, rect: AvailableRect
    ) -> List[AvailableRect]:
        """
        Cut out the overlapping area of an item and a rect.
        New rects will be created and returned.

        :param item: The item to be cut out.
        :param rect: The rect from which to cut out.
        :return: A list of new rects.
        """
        rects = []
        x1, y1, x2, y2 = overlapped_area
        # left side
        if x1 > rect.x:
            rects.append(AvailableRect(rect.x, rect.y, x1 - rect.x, rect.height))
        # right side
        if x2 < rect.x + rect.width:
            rects.append(
                AvailableRect(x2, rect.y, rect.x + rect.width - x2, rect.height)
            )
        # bottom side
        if y1 > rect.y:
            rects.append(AvailableRect(rect.x, rect.y, rect.width, y1 - rect.y))
        # top side
        if y2 < rect.y + rect.height:
            rects.append(
                AvailableRect(rect.x, y2, rect.width, rect.y + rect.height - y2)
            )

        return rects

    def _doubled_rect(self, rect1: AvailableRect, rect2: AvailableRect) -> bool:
        """
        Check if rect1 is fully contained in rect2.

        :param rect1: The first rect.
        :param rect2: The second rect.
        :return: Boolean indicating whether rect1 is fully contained in rect2.
        """
        return (
            rect1.x >= rect2.x
            and rect1.y >= rect2.y
            and rect1.x + rect1.width <= rect2.x + rect2.width
            and rect1.y + rect1.height <= rect2.y + rect2.height
        )

    def _remove_doubled_rects(self) -> None:
        """
        Remove doubled rects from available rects.

        """
        doubled_rects = []
        for rect1 in self.available_rects:
            for rect2 in self.available_rects:
                if rect1 != rect2 and self._doubled_rect(rect1, rect2):
                    doubled_rects.append(rect1)
        self.available_rects = [
            rect for rect in self.available_rects if rect not in doubled_rects
        ]

    def _remove_overlaps(self, item: Item) -> None:
        """
        Remove rects that are overlapped by an item.

        :param item: The item to be checked.
        """
        new_rects = []
        for rect in self.available_rects:
            overlapped_area = self._item_rect_overlap(item, rect)
            if overlapped_area:
                new_rects.extend(self._cut_out_overlapped_area(overlapped_area, rect))
            else:
                new_rects.append(rect)
        self.available_rects = new_rects
        _remove_doubled_rects()


    def evaluate_rect(self, rect: AvailableRect, item: Item) -> float:
        """
        Evaluate and score a rect based on the given heuristic.

        :param rect: The rect to evaluate.
        :param item: The item to be placed.
        :return: A score indicating the rect's suitability.
        """
        fits, needs_rotation = self.check_item_fit(item, rect)
        if not fits:
            return 0

        if needs_rotation:
            item.rotate()

        epsilon = 1e-10
        area_occupied_ratio = ((rect.width - item.width) * (rect.height - item.height)) / (rect.area + epsilon)
        width_occupied_ratio = (rect.width - item.width) / (rect.width + epsilon)
        height_occupied_ratio = (rect.height - item.height) / (rect.height + epsilon)

        try:
            match self.heuristic:
                case BinHeuristicType.next_fit | BinHeuristicType.first_fit:
                    return 1
                case BinHeuristicType.best_area_fit:
                    # How much occupied area is after placing the item
                    return 1 - area_occupied_ratio
                case BinHeuristicType.worst_area_fit:
                    # How much free area is after placing the item
                    return area_occupied_ratio
                case BinHeuristicType.best_width_fit:
                    # How much occupied width is after placing the item
                    return 1 - width_occupied_ratio
                case BinHeuristicType.worst_width_fit:
                    # How much free width is after placing the item
                    return width_occupied_ratio
                case BinHeuristicType.best_height_fit:
                    # How much occupied height is after placing the item
                    return 1 - height_occupied_ratio
                case BinHeuristicType.worst_height_fit:
                    # How much free height is after placing the item
                    return height_occupied_ratio
                case _:
                    raise ValueError(f"Unknown heuristic: {self.heuristic}")

        finally:
            if needs_rotation:
                item.rotate() # Restore original dimensions


    def _find_best_rect(self, item: Item) -> AvailableRect | None:
        """
        Find the best rect for an item.

        :param item: The item to be placed in a rect.
        :return: The selected rect considered best for the item.
        """
        best_rect = None
        best_score = 0
        for rect in self.available_rects:
            score = self.evaluate_rect(rect, item)
            if score > best_score:
                best_score = score
                best_rect = rect
        return best_rect
        
    def pack_item(self, item: Item) -> bool:
        """
        Pack an item into a bin.

        :param item: The item to be packed.
        :return: Boolean indicating whether the item was successfully packed.
        """
        best_rect = self._find_best_rect(item)
        if best_rect:
            self.insert_item(item, best_rect)
            self.available_rects.extend(self._split_rect(best_rect, item))
            self.available_rects.remove(best_rect)
            self._remove_overlaps(item)
            return True
        return False

    def evaluate_bin(self, bin: Bin, item: Item) -> float:
        """
        Evaluate and score a bin based on the given heuristic.

        :param bin: The bin to evaluate.
        :param item: The item to be placed.
        :return: A score indicating the bin's suitability.
        """
        fits, needs_rotation = self.check_item_fit(item, bin)
        if not fits:
            return 0

        


    def find_best_bin(self, bins: List[Bin], item: Item) -> Bin:
        """
        Find the best bin for an item.

        :param bins: List of available bins.
        :param item: The item to be placed in a bin.
        :return: The selected bin considered best for the item.
        """
        best_bin = None
        best_score = 0
        for bin in bins:
            score = self.evaluate_bin(bin, item)
            if score > best_score:
                best_score = score
                best_bin = bin
        return best_bin