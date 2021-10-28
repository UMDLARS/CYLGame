import pytest

from CYLGame.Database import GameDB

from . import ex_db, temp_dir


def test_simple_create_game(temp_dir):
    db = GameDB(temp_dir)
    token = db.add_new_game()
    assert db.is_game_token(token)


def test_create_game_with_frames(temp_dir):
    db = GameDB(temp_dir)
    token = db.add_new_game(frames={"test": "test"})
    assert db.is_game_token(token)
    assert db.get_game_frames(token) == {"test": "test"}


def test_create_game_with_players(ex_db):
    db = ex_db  # type: GameDB
    token = db.add_new_game(player_tokens=db.__players)
    assert db.is_game_token(token)
    for player in db.__players:
        assert db.get_games_for_token(player) == [token]


def test_create_game_with_frames_and_players(ex_db):
    db = ex_db  # type: GameDB
    token = db.add_new_game(frames={"test": "test"}, player_tokens=db.__players)
    assert db.is_game_token(token)
    assert db.get_game_frames(token) == {"test": "test"}
    for player in db.__players:
        assert db.get_games_for_token(player) == [token]


def test_create_game_with_per_player_data(ex_db):
    db = ex_db  # type: GameDB
    per_player_data = {}
    for player in db.__players:
        per_player_data[player] = {"token": player}
    token = db.add_new_game(per_player_data=per_player_data)
    assert db.is_game_token(token)
    for player in db.__players:
        assert db.get_games_for_token(player) == [token]
        assert db.get_player_game_data(token, player) == {"token": player}
