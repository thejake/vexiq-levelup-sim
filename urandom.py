"""Shim for MicroPython's `urandom`, which VEXcode-generated code imports.
Delegates to the standard library."""

from random import (choice, getrandbits, randint, random, randrange, seed,
                    uniform)

__all__ = ["choice", "getrandbits", "randint", "random", "randrange",
           "seed", "uniform"]
