from dataclasses import dataclass, field
from enum import Enum, unique
from typing import List

@unique
class PackingAlgorithm(Enum):
    shelf: "Shelf"
    skyline: "Skyline"

@dataclass
class Item:
    width: int
    height: int
    id: str
    x: int
    y: int
    rotated: bool

    def rotate(self) -> None:
        self.width, self.height = self.height, self.width
        self.rotated = not self.rotated

@dataclass
class Bin:
    width: int
    height: int
    id: str
    algorithm: PackingAlgorithm
    items: List[Item] = field(default_factory=list)


    def insert_item(self, item: Item) -> bool:
        pass

    def visualize(self, ax):
        pass