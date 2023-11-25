from dataclasses import dataclass
from random import randint, seed
from typing import List

from bins import Item


@dataclass
class ItemGenerator:
    bin_width: int
    bin_height: int
    max_item_width: int
    max_item_height: int
    min_item_width: int
    min_item_height: int
    def generate_items(self, count: int) -> List[Item]:
        items = []

        for i in range(count):
            width = randint(self.min_item_width, min(self.max_item_width, self.bin_width))
            height = randint(self.min_item_height, min(self.max_item_height, self.bin_height))
            items.append(Item(width, height, ''))

        return items
