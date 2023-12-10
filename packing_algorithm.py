from abc import ABC, abstractmethod
from typing import List

from items_type import Bin, Item
from algorithm_types import BinHeuristicType

class PackingAlgorithm(ABC):
    def __init__(self, rotation: bool, heuristic: BinHeuristicType):
        """
        Initialize a packing algorithm.

        :param rotation: Boolean indicating whether rotation of items is allowed.
        :param heuristic: The heuristic type to be used for finding the best bin.
        """
        self.rotation = rotation
        self.heuristic = heuristic

    @abstractmethod
    def find_best_bin(self, bins: List[Bin], item: Item) -> Bin:
        """
        Abstract method to find the best bin for an item.
        Should be implemented by specific packing algorithm subclasses.

        :param bins: List of available bins.
        :param item: The item to be placed in a bin.
        :return: The selected bin considered best for the item.
        """
        pass

    @abstractmethod
    def pack_item(self, bin: Bin, item: Item) -> bool:
        """
        Abstract method to pack an item into a bin.
        Should be implemented by specific packing algorithm subclasses.

        :param bin: The bin in which to pack the item.
        :param item: The item to be packed.
        :return: Boolean indicating whether the item was successfully packed.
        """
        pass

    def check_item_fit(self, bin: Bin, item: Item) -> tuple[bool, bool]:
        """
        Check if an item fits in the given bin, considering the possibility of rotation.
        Returns a tuple (fits, needs_rotation) indicating whether the item fits and
        whether rotation is needed for a better fit.

        :param bin: The bin to check against the item.
        :param item: The item to be checked.
        :return: A tuple where the first element is a boolean indicating if the item fits,
                 and the second element is a boolean indicating if rotation is necessary.
        """
        fits_without_rotation = item.width <= bin.width and item.height <= bin.height
        needs_rotation = self.rotation and item.height <= bin.width and item.width <= bin.height

        if fits_without_rotation:
            return True, False
        elif needs_rotation:
            return True, True
        else:
            return False, False
