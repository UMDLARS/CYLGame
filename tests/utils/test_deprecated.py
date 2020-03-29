from unittest.mock import patch

from CYLGame.Utils import deprecated


@patch('CYLGame.Utils.warnings')
def test_decorator(warnings):
    @deprecated()
    def dep_func():
        pass
    dep_func()
    warnings.warn.assert_called()
