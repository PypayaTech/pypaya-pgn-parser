from io import StringIO
from pypaya_pgn_parser.pgn_parser import PGNParser


def process_pgn_file(file_path):
    # Initialize the parser
    parser = PGNParser()

    # Read the entire file into a StringIO object
    with open(file_path, 'r') as file:
        file_content = file.read()
    pgn_stringio = StringIO(file_content)

    game_count = 0

    while True:
        # Parse the next game
        result = parser.parse(pgn_stringio)

        # Check if we've reached the end of the file or encountered an error
        if result is None:
            print(f"Reached end of file or encountered an error after processing {game_count} games.")
            break

        game_info, game_moves = result

        # Process the game
        process_game(game_count, game_info, game_moves)
        game_count += 1

    print(f"Total games processed: {game_count}")


def process_game(game_number, game_info, game_moves):
    print(f"\nGame {game_number + 1} information:")
    for header, value in zip(["Event", "Site", "Date", "Round", "White", "Black", "Result"], game_info):
        print(f"{header}: {value}")

    print("\nMoves:")
    print(game_moves)

    # You can add more processing here, such as analyzing the moves,
    # storing the data, or any other operation you need to perform on each game


# Usage
file_path = "example.pgn"
process_pgn_file(file_path)
