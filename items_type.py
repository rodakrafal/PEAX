import uuid
from dataclasses import dataclass, field
from typing import List

from matplotlib.patches import Rectangle


@dataclass
class Item:
    """
    Represents an item to be packed into a bin.

    :param width: The width of the item.
    :param height: The height of the item.
    :param rotated: Boolean indicating whether the item is rotated.
    :param x: The x-coordinate of the item's bottom-left corner.
    :param y: The y-coordinate of the item's bottom-left corner.
    :param id: A unique identifier for the item.
    """
    width: int
    height: int
    rotated: bool = False
    x: int = -1
    y: int = -1
    id: str = -1

    @property
    def area(self) -> int:
        """
        Calculate the area of the item.

        :return: Calculated area.
        """
        return self.width * self.height

    def rotate(self) -> None:
        """
        Rotate the item by swapping its width and height.
        """
        self.width, self.height = self.height, self.width
        self.rotated = not self.rotated


@dataclass
class Bin:
    """
    Represents a bin into which items can be packed.

    :param width: The width of the bin.
    :param height: The height of the bin.
    :param items: List of items already packed into the bin.
    :param _id: A unique identifier for the bin.
    """
    width: int
    height: int
    items: List[Item] = field(default_factory=list)
    _id: str = field(init=False, default_factory=lambda: str(uuid.uuid4()))

    @property
    def id(self) -> str:
        """
        Get the unique identifier of the bin.

        :return: The unique identifier for the bin.
        """
        return self._id
    @property
    def area(self) -> int:
        """
        Calculate the area of the bin.

        :return: Calculated area.
        """
        return self.width * self.height

    @property
    def remaining_area(self) -> int:
        """
        Calculate the remaining area of the bin.

        :return:
        """
        return self.area - sum(item.area for item in self.items)

    def visualize(self, ax) -> None:
        """
        Visualizes the bin and its contents as a 2D diagram using Matplotlib.
        
        :param ax: The Matplotlib Axes object on which to draw.
        """
        for item in self.items:
            color = 'red' if item.rotated else 'blue'
            rect = Rectangle((item.x, item.y), item.width, item.height, linewidth=1, edgecolor='black', facecolor=color)
            ax.add_patch(rect)
            ax.set_xlim(0, self.width)
            ax.set_ylim(0, self.height)
            ax.text(item.x + item.width / 2, item.y + item.height / 2, item.id, ha='center', va='center')
