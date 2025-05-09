from .utility import make_cmap, register_cmap, to_float

# Original float values taken from:
#   https://github.com/rsnemmen/nmmn/blob/master/nmmn/plots.py
#
# DISCLAIMER: We don't claim any rights to this file, but Wolfram does.
# Consult them, or a lawyer, if you want to use it.
#
# NOTE: This is a reproduced approximation of that matches closely the
# one used by default in Wolfram Mathematica 11.
_wolfram_data: list[tuple[int, ...]] = [
    ( 51,  91, 150),
    (111, 116, 143),
    (167, 136, 110),
    (233, 167,  85),
    (251, 212, 141),
    (255, 247, 190),
]

_cm_name = "Wolfram"
_cm_data = to_float(_wolfram_data)

wolfram = make_cmap(_cm_name, _cm_data, ncolors=256)

register_cmap(wolfram, name=_cm_name)
