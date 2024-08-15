
def contains_any(string: str, substrings: list):
    return any(substring in string for substring in substrings)