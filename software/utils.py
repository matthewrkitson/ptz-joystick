import inspect
import logging

def clamp(value, min_v, max_v, log=False):
    if log:
        if value < min_v or value > max_v:
            logging.debug(f"{function()}: Value out of range; clamping {value} between {min_v} and {max_v}")

    return max(min(value, max_v), min_v)

def assert_in_range(value, min_v, max_v):
    if not min_v <= value <= max_v:
        raise ValueError(f"Value must be between {min_v} and {max_v}, but was {value}")

def interpolate(in_min, value_in, in_max, out_min, out_max):
    in_range = in_max - in_min
    out_range = out_max - out_min
    range_fraction = (value_in - in_min) / in_range
    out = out_min + (range_fraction * out_range)
    return int(out)

def function():
    return inspect.stack()[1][3]
