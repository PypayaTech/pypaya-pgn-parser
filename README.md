# pypaya-pgn-parser

A lightweight Python package that provides efficient parsing capabilities for Portable Game Notation (PGN) chess files.

## Features

- Fast and memory-efficient PGN parsing
- Robust handling of various PGN formats and edge cases
- Easy-to-use API for integrating into your chess applications
- No external dependencies for core functionality

## Installation

You can install pypaya-pgn-parser using pip:

```bash
pip install pypaya-pgn-parser
```

## Usage

Here's a quick example of how to use pypaya-pgn-parser:

```python
from io import StringIO
from pypaya_pgn_parser.pgn_parser import PGNParser

# Example PGN string
pgn_string = '''[Event "Example Game"]
[Site "Chess.com"]
[Date "2023.09.15"]
[Round "1"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Nb8 10. d4 Nbd7 1-0

[Event "Example Game"]
[Site "Chess.com"]
[Date "2023.09.15"]
'''

# Create a StringIO object from the PGN string
pgn_stringio = StringIO(pgn_string)

# Initialize the parser
parser = PGNParser()

# Parse the PGN
first_game_info, first_game_moves = parser.parse(pgn_stringio)

# Print the results for first game
print("First game information:")
for header, value in zip(["Event", "Site", "Date", "Round", "White", "Black", "Result"], first_game_info):
    print(f"{header}: {value}")

print("\nFirst game moves:")
print(first_game_moves)

# Parse the PGN
second_game_info, second_game_moves = parser.parse(pgn_stringio)

# Print the results for second game
print("Second game information:")
for header, value in zip(["Event", "Site", "Date", "Round", "White", "Black", "Result"], second_game_info):
    print(f"{header}: {value}")

print("\nSecond game moves:")
print(second_game_moves)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
