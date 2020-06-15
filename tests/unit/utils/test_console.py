import pytest

from qstrader.utils.console import GREEN, BLUE, CYAN, string_colour


@pytest.mark.parametrize(
    "text,colour,expected",
    [
        ('green colour', GREEN, "\x1b[1;32mgreen colour\x1b[0m"),
        ('blue colour', BLUE, "\x1b[1;34mblue colour\x1b[0m"),
        ('cyan colour', CYAN, "\x1b[1;36mcyan colour\x1b[0m"),
    ]
)
def test_string_colour(text, colour, expected):
    """
    Tests that the string colourisation for the terminal console
    produces the correct values.
    """
    assert string_colour(text, colour=colour) == expected
