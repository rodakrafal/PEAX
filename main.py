import os
from random import seed

from algorithm_types import BinPackingAlgorithmType, BinHeuristicType, SortStrategy
from bins import BinManager
from item_generator import ItemGenerator

if __name__ == '__main__':
    run_all = True
    heuristic_all = False
    sort_all = False

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
    while True:
        print("2D Bin Packing Solver")
        print("1. Generate Items")
        print("2. Load Items from CSV")
        print("0. Exit")
        user_choice = input("Enter your choice (0-2): ")
        if user_choice == '1':
            items = generator.generate_items(number_of_items)
            print("Do you want to save generated files in CSV?")
            print("> yes")
            print("> no")
            user_choice = input("Enter your choice: ")
            if user_choice.lower() == 'yes':
                file_path = input("Enter the path to the CSV file: ")
                generator.save_items(file_path, items)
        elif user_choice == '2':
            file_path = input("Enter the path to the CSV file: ")
            if os.path.exists(file_path):
                items = generator.load_items(file_path)
                if not items:
                    print("Error: No valid items found in the file.")
                    exit()
                else:
                    print("Items loaded successfully.")
            else:
                print(f"Error: File not found at {file_path}")
                continue
        elif user_choice == '0':
            exit()
        else:
            print("Invalid choice. Please enter correct number")
            continue
        
        print("\nBin Heuristic:")
        for i, heuristic in enumerate(BinHeuristicType, start=1):
            print(f"{i}. {heuristic.value}")
        print("0. ALL")
        user_choice = input("Select Bin Heuristic (1-10): ")
        try:
            user_choice = int(user_choice)
            if 1 <= user_choice <= len(BinHeuristicType):
                bin_heuristic_type = list(BinHeuristicType)[user_choice - 1]
            elif user_choice == '0':
                heuristic_all = True;
            else:
                print("Invalid choice. Please enter correct number")
                continue
        except ValueError:
            print("Invali choice. Please enter a number")

        print("\nSort Strategy:")
        for i, sort_strategy in enumerate(SortStrategy, start=1):
            print(f"{i}. {sort_strategy.name}")
        print("0. ALL")
        user_choice = input("Select Sort Strategy (1-15): ")
        try:
            user_choice = int(user_choice)
            if 1 <= user_choice <= len(SortStrategy):
                bin_sort_strategy = list(SortStrategy)[user_choice - 1]
            elif user_choice == '0':
                sort_all = True
            else:
                print("Invalid choice. Please enter correct number")
                continue
        except ValueError:
            print("Invali choice. Please enter a number")

        if run_all:

            for heuristic in BinHeuristicType if heuristic_all else [bin_heuristic_type]:
                for sort in SortStrategy if sort_all else [bin_sort_strategy]:
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
