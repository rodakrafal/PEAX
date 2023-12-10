from dataclasses import dataclass, field
from typing import List, Dict

from algorithm_types import BinHeuristicType
from items_type import Bin, Item
from packing_algorithm import PackingAlgorithm


@dataclass
class Shelf:
    height: int
    width: int
    available_width: int
    vertical_offset: int = 0
    items: List[Item] = field(default_factory=list)
    rotation: bool = False

    @property
    def area(self) -> int:
        return self.available_width * self.height

    def check_item_fit(self, item: Item) -> tuple[bool, bool]:
        """
        Check if an item fits in the given shelf, considering the possibility of rotation.

        :param item: The item to be checked.
        :return: A tuple where the first element is a boolean indicating if the item fits,
                 and the second element is a boolean indicating if rotation is necessary.
        """
        fits_without_rotation = item.width <= self.available_width and item.height <= self.height
        needs_rotation = self.rotation and item.height <= self.available_width and item.width <= self.height

        if fits_without_rotation:
            return True, False
        elif needs_rotation:
            return True, True
        else:
            return False, False

    def insert_item(self, item: Item) -> bool:
        """
        Insert an item into the shelf.

        :param item: The item to be inserted.
        :return: Boolean indicating whether the item was successfully inserted.
        """
        fits, needs_rotation = self.check_item_fit(item)
        if fits:
            if needs_rotation:
                item.rotate()
            item.x, item.y = self.width - self.available_width, self.vertical_offset
            self.items.append(item)
            self.available_width -= item.width
            return True
        return False


class ShelfAlgorithm(PackingAlgorithm):
    def __init__(self, rotation: bool, heuristic: BinHeuristicType):
        super().__init__(rotation, heuristic)
        self.bin_shelves: Dict[str, Dict[str, list | int]] = {}

    def initialize_bin(self, bin: Bin) -> None:
        """
        Initialize a bin with an empty list of shelves and full available height.

        :param bin: Bin to be initialized.
        """
        self.bin_shelves[bin.id] = {'shelves': [], 'available_height': bin.height}

    def can_create_shelf(self, bin: Bin, item: Item) -> bool:
        """
        Check if a shelf can be created in a bin.

        :param bin: Bin to check.
        :param item: Item to be inserted into the shelf.
        :return: Boolean indicating whether a shelf can be created.
        """
        return item.height <= self.bin_shelves[bin.id]['available_height']

    def create_shelf(self, bin: Bin, item: Item) -> Shelf | None:
        """
        Create a shelf for a bin and insert an item into it.

        :param bin:  Bin to create shelf for.
        :param item: Item to be inserted into the shelf.
        :return: Created shelf if item fits, None otherwise.
        """
        if self.can_create_shelf(bin, item):
            vertical_offset = bin.height - self.bin_shelves[bin.id]['available_height']
            shelf = Shelf(width=bin.width, height=item.height, available_width=bin.width,
                          vertical_offset=vertical_offset, rotation=self.rotation)
            self.bin_shelves[bin.id]['shelves'].append(shelf)
            self.bin_shelves[bin.id]['available_height'] -= shelf.height

            return shelf
        else:
            return None

    def evaluate_shelf(self, shelf: Shelf, item: Item) -> float:
        """
        Evaluate and score a shelf based on the given heuristic.

        :param shelf: The shelf to evaluate.
        :param item: The item to be placed.
        :return: A score indicating the shelf's suitability.
        """
        fits, needs_rotation = shelf.check_item_fit(item)
        if not fits:
            return 0  # Item does not fit in this shelf

        if needs_rotation:
            item.rotate()  # Temporarily rotate the item for evaluation

        epsilon = 1e-10
        area_occupied_ratio = ((shelf.available_width - item.width) * shelf.height) / (shelf.area + epsilon)
        width_occupied_ratio = (shelf.available_width - item.width) / (shelf.width + epsilon)
        height_occupied_ratio = (shelf.height - item.height) / (shelf.height + epsilon)

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
                item.rotate()  # Restore original dimensions

    def find_best_shelf(self, bin: Bin, item: Item) -> Shelf | None:
        """
        Find the best shelf for an item in a bin.

        :param bin: The bin to find a shelf for.
        :param item: The item to be placed.
        :return: Union of the best shelf found and None in case no shelf was found.
        """
        best_shelf, best_score = None, 0
        for shelf in self.bin_shelves[bin.id]['shelves']:
            score = self.evaluate_shelf(shelf, item)
            if score > best_score:
                best_shelf, best_score = shelf, score
            if best_score == 1:
                return best_shelf  # Return immediately if perfect score is found

        return best_shelf or self.create_shelf(bin, item)

    def pack_item(self, bin: Bin, item: Item) -> bool:
        """
        Pack an item into a bin.

        :param bin: The bin to pack.
        :param item: The item to be packed.
        :return: Boolean indicating whether the item was successfully packed.
        """
        if bin.id not in self.bin_shelves:
            self.initialize_bin(bin)

        shelf = self.find_best_shelf(bin, item)
        if shelf is None:
            return False

        if not shelf.insert_item(item):
            return False

        bin.items.append(item)
        return True

    def evaluate_bin(self, bin: Bin, item: Item) -> float:
        """
        Evaluate and score a bin based on the given heuristic.

        :param bin: The bin to evaluate.
        :param item: The item to be placed.
        :return: A score indicating the bin's suitability.
        """
        fits, _ = self.check_item_fit(bin, item)
        best_score = 0
        if not fits:
            return best_score

        for shelf in self.bin_shelves[bin.id]['shelves']:
            score = self.evaluate_shelf(shelf, item)
            if score > best_score:
                best_score = score
            if best_score == 1:
                return best_score

        if best_score == 0:
            if self.can_create_shelf(bin, item):
                vertical_offset = bin.height - self.bin_shelves[bin.id]['available_height']
                shelf = Shelf(width=bin.width, height=item.height, available_width=bin.width,
                              vertical_offset=vertical_offset, rotation=self.rotation)
                best_score = self.evaluate_shelf(shelf, item)

        return best_score

    def find_best_bin(self, bins: List[Bin], item: Item) -> Bin:
        """
        Find the best bin for an item.

        :param bins: Bins to be searched.
        :param item: The item to be placed.
        :return: Best bin found.
        """
        best_bin, best_score = None, 0

        for bin in bins:
            score = self.evaluate_bin(bin, item)
            if score > best_score:
                best_bin, best_score = bin, score
            if best_score == 1:
                return best_bin

        return best_bin
