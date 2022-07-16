from checkpointing.hash.specific import is_installed


def test_is_installed_positive():
    assert is_installed("dill")

def test_is_installed_negative():
    assert not is_installed("ModuleThatDoesntExist")