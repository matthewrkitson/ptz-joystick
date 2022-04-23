import inspect

def clamp(value, min_v, max_v):
    return max(min(value, max_v), min_v)

def assert_in_range(value, min_v, max_v):
    if not min_v <= value <= max_v:
        raise ValueError(f"Value must be between {min_v} and {max_v}, but was {value}")

def function():
    return inspect.stack()[1][3]
