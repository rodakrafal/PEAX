from random import seed
from typing import List

from bins import Item, Bin
import matplotlib.pyplot as plt

from item_generator import ItemGenerator


def visualize_bins(bin_list: List[Bin]):
    # Create a figure with subplots - one subplot per bin
    fig, axs = plt.subplots(1, len(bin_list), figsize=(15, 5))
    if len(bin_list) == 1:  # If there's only one bin, axs is not a list but a single AxesSubplot object
        axs = [axs]
    for ax, bin in zip(axs, bin_list):
        bin.visualize(ax)
    plt.tight_layout()
    plt.show()


def best_fit_algorithm(item_list: List[Item], bin_width: int, bin_height: int) -> List[Bin]:
    bin_list: List[Bin] = []
    for item in sorted(item_list, key=lambda i: (i.height * i.width), reverse=True):  # Sort items by area, descending
        placed = False
        for bin in bin_list:
            if bin.place_item(item):
                placed = True
                break
        if not placed:
            new_bin = Bin(bin_width, bin_height)
            new_bin.place_item(item)
            bin_list.append(new_bin)
    return bin_list


# Example usage: Generate items for a bin of size 10x5
bin_width = 100
bin_height = 100
seed(1)  # Seed for reproducibility in random number generation
generator = ItemGenerator(bin_width=bin_width, bin_height=bin_height, max_item_width=45, max_item_height=45,
                          min_item_width=5, min_item_height=5)
items = generator.generate_items(43)
print(items)  # Print generated items

# Example usage
bins = best_fit_algorithm(items, bin_width, bin_height)
visualize_bins(bins)