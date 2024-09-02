import io
from typing import List, Tuple
import pytest
from pypaya_pgn_parser.pgn_parser import PGNParser
from pypaya_pgn_parser.headers import HEADERS, DEFAULT_VALUES


def assert_game_info(game_info: List[str], expected_info: List[str]):
    assert len(game_info) == len(HEADERS) - 1, f"Expected {len(HEADERS) - 1} headers, got {len(game_info)}"
    for i, (actual, expected) in enumerate(zip(game_info, expected_info)):
        if expected == "DEFAULT":
            assert actual == DEFAULT_VALUES[i], f"Mismatch in game_info[{i}]. Expected default value, Got: {actual}"
        elif expected == "RESULT":
            assert actual in ["1-0", "0-1", "1/2-1/2", "*"], f"Invalid result in game_info[{i}]. Got: {actual}"
        elif expected != "?":
            assert actual == expected, f"Mismatch in game_info[{i}]. Expected: {expected}, Got: {actual}"


def assert_moves(moves: str, expected_moves: str):
    assert moves.split() == expected_moves.split(), f"Mismatch in moves. Expected: {expected_moves}, Got: {moves}"


def parse_pgn(parser, pgn_str: str) -> Tuple[List[str], str]:
    pgn = io.StringIO(pgn_str)
    result = parser.parse(pgn)
    assert result is not None, "Parser returned None instead of a tuple"
    return result


def assert_all_headers_unknown(game_info: List[str]):
    assert game_info == DEFAULT_VALUES, f"Expected all default values in game_info, got {game_info}"


@pytest.fixture
def parser():
    return PGNParser()


def test_parse_complete_game(parser):
    pgn_str = '''[Event "Test Event"]
[Site "Test Site"]
[Date "2023.01.01"]
[Round "1"]
[White "Player 1"]
[Black "Player 2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 1-0
'''
    game_info, moves = parse_pgn(parser, pgn_str)
    expected_info = ["Test Event", "Test Site", "2023.01.01", "1", "Player 1", "Player 2", "1-0"] + ["DEFAULT"] * 10
    assert_game_info(game_info, expected_info)
    assert_moves(moves, "e4 e5 Nf3 Nc6 Bb5 a6")


def test_parse_headers(parser):
    pgn_str = '''[Event "Test Event"]
[Site "Test Site"]
[Date "2023.07.21"]
[Round "1"]
[White "Player 1"]
[Black "Player 2"]
[Result "1-0"]
[WhiteElo "2000"]
[BlackElo "1900"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 1-0'''

    game_info, moves = parse_pgn(parser, pgn_str)

    expected_info = ["Test Event", "Test Site", "2023.07.21", "1", "Player 1", "Player 2", "1-0",
                     "DEFAULT", "DEFAULT", "2000", "1900"] + ["DEFAULT"] * 6
    assert_game_info(game_info, expected_info)

    assert_moves(moves, "e4 e5 Nf3 Nc6 Bb5")


def test_parse_incomplete_game(parser):
    pgn_str = '''[Event "Incomplete Game"]
[White "Player 1"]
[Black "Player 2"]

1. e4 e5 2. Nf3
'''
    game_info, moves = parse_pgn(parser, pgn_str)

    expected_info = ["Incomplete Game", "DEFAULT", "DEFAULT", "DEFAULT", "Player 1", "Player 2", "DEFAULT"] + [
        "DEFAULT"] * 10
    assert_game_info(game_info, expected_info)

    assert_moves(moves, "e4 e5 Nf3")


def test_parse_missing_headers(parser):
    pgn_str = '''[Event "Missing Headers"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 1-0
'''
    game_info, moves = parse_pgn(parser, pgn_str)

    expected_info = ["Missing Headers"] + ["DEFAULT"] * 5 + ["RESULT"] + ["DEFAULT"] * 10
    assert_game_info(game_info, expected_info)
    assert_moves(moves, "e4 e5 Nf3 Nc6 Bb5 a6")


def test_parse_empty_game(parser):
    pgn_str = '''[Event "Test Event"]
[Result "*"]

*'''
    game_info, moves = parse_pgn(parser, pgn_str)

    expected_info = ["Test Event", "DEFAULT", "DEFAULT", "DEFAULT", "DEFAULT", "DEFAULT", "*"] + ["DEFAULT"] * 10
    assert_game_info(game_info, expected_info)
    assert moves == "", f"Expected empty string for moves, got {moves}"


def test_parse_multiple_games(parser):
    pgn_str = '''[Event "Game 1"]
[White "Player 1"]
[Black "Player 2"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 1-0

[Event "Game 2"]
[White "Player 3"]
[Black "Player 4"]

1. d4 d5 2. c4 e6 3. Nc3 Nf6 0-1
'''
    parser = PGNParser()
    stream = io.StringIO(pgn_str)

    # Parse first game
    game1_info, game1_moves = parser.parse(stream)

    # Parse second game
    game2_info, game2_moves = parser.parse(stream)

    # Check that there are no more games
    result = parser.parse(stream)
    assert result is None, "Expected no more games"

    # Assertions
    assert game1_info[0] == "Game 1", f"Expected 'Game 1', got {game1_info[0]}"
    assert game2_info[0] == "Game 2", f"Expected 'Game 2', got {game2_info[0]}"
    assert "e4" in game1_moves, f"Expected 'e4' in moves, got {game1_moves}"
    assert "d4" in game2_moves, f"Expected 'd4' in moves, got {game2_moves}"


def test_parse_end_of_stream(parser):
    pgn = io.StringIO('')
    assert parser.parse(pgn) is None


def test_parse_invalid_pgn(parser):
    pgn_str = '''
Invalid PGN content
'''
    game_info, moves = parse_pgn(parser, pgn_str)

    assert_all_headers_unknown(game_info)

    assert moves == ""


def test_parse_with_comments_and_variations(parser):
    pgn_str = '''[Event "Test Event"]

1. e4 e5 2. Nf3 {A common move} Nc6 (2... d6 3. d4 {The Philidor Defense}) 3. Bb5 1-0'''

    game_info, moves = parse_pgn(parser, pgn_str)

    expected_info = ["Test Event"] + ["DEFAULT"] * 5 + ["RESULT"] + ["DEFAULT"] * 10
    assert_game_info(game_info, expected_info)
    assert_moves(moves, "e4 e5 Nf3 Nc6 Bb5")


def test_parse_with_special_moves(parser):
    pgn_str = '''[Event "Test Event"]
    
1. e4 e5 2. d4 exd4 3. Nf3 Bc5 4. Be2 Ne7 5. O-O 1-0'''

    game_info, moves = parse_pgn(parser, pgn_str)

    expected_info = ["Test Event"] + ["DEFAULT"] * 5 + ["RESULT"] + ["DEFAULT"] * 10
    assert_game_info(game_info, expected_info)

    expected_moves = "e4 e5 d4 exd4 Nf3 Bc5 Be2 Ne7 O-O"
    assert_moves(moves, expected_moves)


def test_parse_game_with_promotions(parser):
    pgn_str = '''[Event "Test Event"]
    
1. g4 f5 2. g5 f4 3. g6 f3 4. gxh7 fxe2 5. hxg8=N exf1=Q+'''

    game_info, moves = parse_pgn(parser, pgn_str)

    expected_info = ["Test Event"] + ["DEFAULT"] * 16
    assert_game_info(game_info, expected_info)

    expected_moves = "g4 f5 g5 f4 g6 f3 gxh7 fxe2 hxg8=N exf1=Q+"
    assert_moves(moves, expected_moves)


def test_parse_game_with_annotations(parser):
    pgn_str = '''[Event "Test Event"]

1. e4! e5 2. Nf3 Nc6 3. Bb5 a6?! 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O 9. h3 Na5 10. Bc2 c5 11. d4 Qc7 12. Nbd2 cxd4 13. cxd4 Nc6 14. Nb3 a5 15. Be3 a4 16. Nbd2 Bd7?? 17. Rc1 Rfc8 18. Bb1! 1-0'''

    game_info, moves = parse_pgn(parser, pgn_str)

    expected_info = ["Test Event"] + ["DEFAULT"] * 5 + ["RESULT"] + ["DEFAULT"] * 10
    assert_game_info(game_info, expected_info)

    expected_moves = "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7 Re1 b5 Bb3 d6 c3 O-O h3 Na5 Bc2 c5 d4 Qc7 Nbd2 cxd4 cxd4 Nc6 Nb3 a5 Be3 a4 Nbd2 Bd7 Rc1 Rfc8 Bb1"
    assert_moves(moves, expected_moves)


def test_parse_game_no_headers(parser):
    pgn_str = '''1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 1-0'''

    game_info, moves = parse_pgn(parser, pgn_str)

    expected_info = ["DEFAULT"] * 6 + ["RESULT"] + ["DEFAULT"] * 10
    assert_game_info(game_info, expected_info)
    assert_moves(moves, "e4 e5 Nf3 Nc6 Bb5 a6 Ba4 Nf6 O-O Be7")


if __name__ == "__main__":
    pytest.main()
