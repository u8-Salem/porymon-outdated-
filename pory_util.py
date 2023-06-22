# utility functions lel

import os

def pjoin(path, *paths) -> str:
    return os.path.join(path, *paths)

# returns the count of lines in a string
def getStrLineCount(string) -> int:
    lines = string.splitlines()
    return len(lines)


