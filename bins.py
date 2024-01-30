from typing import List

import matplotlib.pyplot as plt

from algorithm_types import BinHeuristicType, BinPackingAlgorithmType, SortStrategy
from items_type import Item, Bin
from packing_algorithm import PackingAlgorithm
from shelf import ShelfAlgorithm
from skyline import SkylineAlgorithm


class BinManager:
    def __init__(self, bin_width: int, bin_height: int, algorithm: BinPackingAlgorithmType,
                 heuristic: BinHeuristicType = BinHeuristicType.first_fit, rotation: bool = False,
                 sorting_strategy: SortStrategy = SortStrategy.NONE):
        self.bin_width = bin_width
        self.bin_height = bin_height
        self.heuristic = heuristic
        self.rotation = rotation
        self.algorithm = self.initialize_algorithm(algorithm)
        self.sorting_strategy = sorting_strategy
        self.bins: List[Bin] = []
        self.items: List[Item] = []

    def initialize_algorithm(self, algorithm: BinPackingAlgorithmType) -> PackingAlgorithm:
        match algorithm:
            case BinPackingAlgorithmType.shelf:
                return ShelfAlgorithm(self.rotation, self.heuristic)
            case BinPackingAlgorithmType.skyline:
                return SkylineAlgorithm(self.rotation, self.heuristic)
            case _:
                raise ValueError(f'Unknown algorithm: {self.algorithm}')

    def visualize_bins(self, number_of_bins: int = 1, title: str = 'Bins'):
        fig, axs = plt.subplots(1, min(len(self.bins), number_of_bins), figsize=(15, 8))
        if len(self.bins) == 1:  # If there's only one bin, axs is not a list but a single AxesSubplot object
            axs = [axs]
        for ax, bin in zip(axs, self.bins):
            bin.visualize(ax)
            ax.set_title(f'Bin with {len(bin.items)} items')

        plt.tight_layout(h_pad=2)
        plt.suptitle(title)
        plt.subplots_adjust(top=0.85)
        plt.show()

    def sort_items(self, items: List[Item]) -> List[Item]:
        if self.sorting_strategy is not SortStrategy.NONE:
            return sorted(items, key=self.sorting_strategy.value)
        else:
            return items

    def find_best_bin_for_item(self, item: Item, algorithm: PackingAlgorithm) -> Bin:
        return algorithm.find_best_bin(self.bins, item)

    def execute(self, items: List[Item]) -> List[Bin]:
        self.items = self.sort_items(items)
        for item in self.items:
            bin = self.find_best_bin_for_item(item, self.algorithm)
            if bin is None:
                bin = Bin(self.bin_width, self.bin_height)
                self.bins.append(bin)
            self.algorithm.pack_item(bin, item)
        return self.bins
