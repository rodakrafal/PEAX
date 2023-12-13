import csv
from dataclasses import dataclass
from random import randint
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
            items.append(Item(width, height, id=str(i)))

        return items
    def load_items(self, file_path: str) -> List[Item]:
        items = []

        with open(file_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for i, row in enumerate(csv_reader):
                width, height = map(int, row)
                if 0 < width <= self.bin_width and 0 < height <= self.bin_height:
                    items.append(Item(width, height, id=str(i)))
        return items
    def save_items(self, file_path: str, items: List[Item]) -> None:
        with open(file_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for item in items:
                if 0 < item.width <= self.bin_width and 0 < item.height <= self.bin_height:
                    csv_writer.writerow([item.width, item.height])
