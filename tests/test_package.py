from kacoustics import KEYS


def test_key_set_is_26_letters_plus_space():
    assert len(KEYS) == 27 and KEYS[0] == "a" and KEYS[-2] == "z" and KEYS[-1] == "space"
