import pytest
from CYLGame.Database import GameDB
from . import temp_dir, ex_db


def test_simple_str(ex_db: GameDB):
    tok = ex_db.__players[0]
    ex_db.save_value(tok, "test_key", "test_value")
    assert ex_db.get_value(tok, "test_key") == "test_value"


def test_simple_2(ex_db: GameDB):
    tok = ex_db.__players[0]
    ex_db.save_value(tok, "test_key", "test_value")
    assert ex_db.get_value(tok, "test_key", "default_value") == "test_value"


def test_overwrite(ex_db: GameDB):
    tok = ex_db.__players[0]
    ex_db.save_value(tok, "test_key", "str")
    assert ex_db.get_value(tok, "test_key") == "str"
    ex_db.save_value(tok, "test_key", 12)
    assert ex_db.get_value(tok, "test_key") == 12
    ex_db.save_value(tok, "test_key", 3.14)
    assert ex_db.get_value(tok, "test_key") == 3.14


def test_simple_int(ex_db: GameDB):
    tok = ex_db.__players[0]
    ex_db.save_value(tok, "test_key", 12)
    assert ex_db.get_value(tok, "test_key") == 12


def test_simple_float(ex_db: GameDB):
    tok = ex_db.__players[0]
    ex_db.save_value(tok, "test_key", 3.14)
    assert ex_db.get_value(tok, "test_key") == 3.14


def test_default_value(ex_db: GameDB):
    tok = ex_db.__players[0]
    # ex_db.save_value(tok, "test_key", "test_value")
    assert ex_db.get_value(tok, "test_key", "default_value") == "default_value"
