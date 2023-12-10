from random import seed

from algorithm_types import BinPackingAlgorithmType, BinHeuristicType, SortStrategy
from bins import BinManager
from item_generator import ItemGenerator

if __name__ == '__main__':
    run_all = True

    bin_width = 100
    bin_height = 100
    number_of_items = 42
    min_item_height = 5
    min_item_width = 5
    max_item_height = 45
    max_item_width = 45
    seed(1)  # Seed for reproducibility in random number generation

    generator = ItemGenerator(bin_width=bin_width, bin_height=bin_height, min_item_width=min_item_width,
                              min_item_height=min_item_height,
                              max_item_width=max_item_width, max_item_height=max_item_height)
    items = generator.generate_items(number_of_items)
    if run_all:

        for heuristic in BinHeuristicType:
            for sort in SortStrategy:
                for rotation in [True, False]:
                    binManager = BinManager(bin_width, bin_height, BinPackingAlgorithmType.shelf, heuristic, rotation,
                                            sort)
                    binManager.execute(items)
                    plot_title = f'Heuristic: {heuristic}, Rotation: {rotation}, Sort: {sort}'
                    binManager.visualize_bins(12, plot_title)
                    print(f'\t\t{plot_title}')
                    print(f'Number of bins: {len(binManager.bins)}')
                    print(f'Number of items: {len(binManager.items)}')
                    print(f'Number of items in bins: {sum(len(bin.items) for bin in binManager.bins)} \n\n')

    else:
        binManager = BinManager(bin_width, bin_height, BinPackingAlgorithmType.shelf, BinHeuristicType.best_height_fit,
                                True, SortStrategy.HEIGHT_DESC)
        binManager.execute(items)
        binManager.visualize_bins(12)
