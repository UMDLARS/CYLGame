import pytest

from CYLGame.Database import GameDB


@pytest.fixture
def temp_dir():
    import shutil
    import tempfile

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
