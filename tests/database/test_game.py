import pytest
from CYLGame.Database import GameDB


@pytest.fixture
def temp_dir():
    import tempfile
    import shutil
    dir_name = tempfile.mkdtemp()
    yield dir_name
    shutil.rmtree(dir_name)


@pytest.fixture
def ex_db(temp_dir):
    db = GameDB(temp_dir)
    stoken = db.add_new_school("Test")
    db.__players = []
    for _ in range(4):
        db.__players += [db.get_new_token(stoken)]
    return db


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
