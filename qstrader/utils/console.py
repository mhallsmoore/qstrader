BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)


def string_colour(text, colour=WHITE):
    """
    Create string text in a particular colour to the terminal.
    """
    seq = "\x1b[1;%dm" % (30 + colour) + text + "\x1b[0m"
    return seq
