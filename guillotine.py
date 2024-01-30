import typing
import ipdb
from dataclasses import dataclass, field
from typing import List, Dict

from algorithm_types import BinHeuristicType
from items_type import Bin, Item
from packing_algorithm import PackingAlgorithm

class FreeRectangle(typing.NamedTuple('FreeRectangle', [('width', int), ('height', int), ('x', int), ('y', int)])):
    __slots__ = ()
    @property
    def area(self):
        return self.width*self.height

@dataclass
class Guillotine:
    height: int
    width: int
    area: int
    free_area: int
    free_rects: List[FreeRectangle] = field(default_factory=list)
    items: List[Item] = field(default_factory=list)
    rotation: bool = False
    merge: bool = False


    def check_item_fit(self, item: Item) -> tuple[bool, bool]:
        """
        Check if an item fits given freerect and whether rotation is needed.

        :param item: The item to check.
        :return: A tuple (fits, needs_rotation) where fits is a boolean indicating 
                 whether the item fits in any free rectangle, and needs_rotation 
                 is a boolean indicating if rotation is necessary for the item to fit.
        """
        for rect in self.free_rects:
            # Check fit without rotation
            if item.width <= rect.width and item.height <= rect.height:
                return True, False

            # Check fit with rotation (if allowed)
            if self.rotation and item.height <= rect.width and item.width <= rect.height:
                return True, True

        return False, False

    def check_rect_fit(self, rect: FreeRectangle, item: Item) -> bool:
        fits_without_rotation = item.width <= rect.width and item.height <= rect.height
        needs_rotation = self.rotation and item.height <= rect.width and item.width <= rect.height

        if fits_without_rotation:
            return True, False
        elif needs_rotation:
            return True, True
        else:
            return False, False

    def insert_item(self, rect: FreeRectangle, item: Item) -> bool:
        fits, needs_rotation = self.check_rect_fit(rect, item)
        if fits:
            if needs_rotation:
                item.rotate()
            self.free_area -= item.area
            item.x, item.y = rect.x, rect.y
            self.items.append(item)

            #ipdb.set_trace()
            self.free_rects.remove(rect)
            splits = self.split_free_rect(item, rect)
            for rect in splits:
                self.free_rects.append(rect)
            return True
        return False


    def split_free_rect(self, item: Item, rect: FreeRectangle) -> List[FreeRectangle]:
        # Remaining lenghts
        w = rect.width - item.width
        h = rect.height - item.height

        # TODO: implement split heuristic
        return self.split_along_axis(rect, item, True)
    def split_along_axis(self, rect: FreeRectangle, item: Item, split: bool) -> List[FreeRectangle]:
        """
        Split a free rectangle into two smaller rectangles after placing an item in it
        """
        # Put item in bottom left corner, remaining lengths are:
        top_x = rect.x
        top_y = rect.y + item.height
        top_h = rect.height - item.height
        right_x = rect.x + item.width
        right_y = rect.y
        right_w = rect.width - item.width

        # horizontal
        if split:
            top_w = rect.width
            right_h = item.height
        # vertical
        else:
            top_w = item.width
            right_h = rect.height

        result = []
        if right_w > 0 and right_h > 0:
            right_rect = FreeRectangle(right_w, right_h, right_x, right_y)
            result.append(right_rect)
        if top_w > 0 and top_h > 0:
            top_rect = FreeRectangle(top_w, top_h, top_x, top_y)
            result.append(top_rect)
        return result

class GuillotineAlgorithm(PackingAlgorithm):
    def __init__(self, rotation: bool, heuristic: BinHeuristicType):
        super().__init__(rotation, heuristic)
        self.bin_guillotine: Dict[str, Guillotine] = {}

    def initialize_bin(self, bin: Bin) -> None:
        """
        Initialize a bin with an empty Guillotine instance.
        """
        self.bin_guillotine[bin.id] = Guillotine(
                height=bin.height,
                width=bin.width,
                area=bin.width * bin.height,
                free_area=bin.width * bin.height,
                rotation=self.rotation
                )
        # Add the initial free rectangle covering the whole bin area
        self.bin_guillotine[bin.id].free_rects.append(
                FreeRectangle(width=bin.width, height=bin.height, x=0, y=0)
                )

    def evaluate_free_rect(self, rect: FreeRectangle, item: Item) -> float:
        epsilon = 1e-10
        area_occupied_ratio = (item.area) / (rect.area + epsilon)
        width_occupied_ratio = (rect.width - item.width) / (rect.width + epsilon)
        height_occupied_ratio = (rect.height - item.height) / (rect.height + epsilon)

        try:
            match self.heuristic:
                case BinHeuristicType.next_fit | BinHeuristicType.first_fit:
                    return 1
                case BinHeuristicType.best_area_fit:
                    # How much occupied area is after placing the item
                    return area_occupied_ratio
                case BinHeuristicType.worst_area_fit:
                    # How much free area is after placing the item
                    return 1 - area_occupied_ratio
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
            pass

    def find_best_free_rect(self, bin: Bin, item: Item) -> FreeRectangle | None:
        best_rect, best_score = None, 0
        for rect in self.bin_guillotine[bin.id].free_rects:
            fits, needs_rotation = Guillotine.check_rect_fit(self, rect, item)
            if not fits:
                continue
            score = self.evaluate_free_rect(rect, item)
            if score > best_score:
                best_rect, best_score = rect, score
            if best_score == 1:
                return best_rect

        return best_rect

    def pack_item(self, bin: Bin, item: Item) -> bool:
        if bin.id not in self.bin_guillotine:
            self.initialize_bin(bin)

        rect = self.find_best_free_rect(bin, item)
        if rect is None:
            return False
        if not self.bin_guillotine[bin.id].insert_item(rect, item):
            return False
        bin.items.append(item)
        return True

    def evaluate_bin(self, bin: Bin, item: Item) -> float:
        fits, _ = self.check_item_fit(bin, item)
        best_score = 0
        if not fits:
            return best_score

        for rect in self.bin_guillotine[bin.id].free_rects:
            fits, _ = Guillotine.check_rect_fit(self, rect, item)
            if not fits:
                continue
            score = self.evaluate_free_rect(rect, item)
            if score > best_score:
                best_score = score
            if best_score == 1:
                return best_score

        return best_score

    def find_best_bin(self, bins: List[Bin], item: Item) -> Bin:
        best_bin, best_score = None, 0

        for bin in bins:
            score = self.evaluate_bin(bin, item)
            #ipdb.set_trace()
            if score > best_score:
                best_bin, best_score = bin, score
            if best_score == 1:
                return best_bin

        return best_bin
