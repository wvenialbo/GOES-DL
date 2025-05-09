from .utility import make_cmap, register_cmap, to_float

# Original float values taken from:
#   https://github.com/BIDS/colormap/blob/master/parula.py
#
# DISCLAIMER: We don't claim any rights to this file, but The Mathworks
# does. Consult them, or a lawyer, if you want to use it.
#
# NOTE: This is a copy of the old Parula colourmap from MATLAB R2016a.
# The new version can be found in the `parula` module.
#
# The Parula colourmap was introduced as the default colourmap in MATLAB
# R2014b. It replaced the previous default, "jet", and was designed to
# offer a more perceptually uniform and visually appealing colour scheme
# for data visualization. 
#
# Starting in R2017a, the colours in the parula colourmap are slightly
# different than in previous releases. The visual change is subtle;
# however, you might notice more colourful colours and smoother
# transitions between colours. Starting in R2019b, colourmaps have 256
# colours by default. In R2019a and previous releases, the default size
# is 64.
_parolinum_data: list[tuple[int, ...]] = [
    ( 53,  42, 135),
    ( 54,  48, 147),
    ( 54,  55, 160),
    ( 53,  61, 173),
    ( 50,  67, 186),
    ( 44,  74, 199),
    ( 32,  83, 212),
    ( 15,  92, 221),
    (  3,  99, 225),
    (  2, 104, 225),
    (  4, 109, 224),
    (  8, 113, 222),
    ( 13, 117, 220),
    ( 16, 121, 218),
    ( 18, 125, 216),
    ( 20, 129, 214),
    ( 20, 133, 212),
    ( 19, 137, 211),
    ( 16, 142, 210),
    ( 12, 147, 210),
    (  9, 152, 209),
    (  7, 156, 207),
    (  6, 160, 205),
    (  6, 164, 202),
    (  6, 167, 198),
    (  7, 169, 194),
    ( 10, 172, 190),
    ( 15, 174, 185),
    ( 21, 177, 180),
    ( 29, 179, 175),
    ( 37, 181, 169),
    ( 46, 183, 164),
    ( 56, 185, 158),
    ( 66, 187, 152),
    ( 77, 188, 146),
    ( 89, 189, 140),
    (101, 190, 134),
    (113, 191, 128),
    (124, 191, 123),
    (135, 191, 119),
    (146, 191, 115),
    (156, 191, 111),
    (165, 190, 107),
    (174, 190, 103),
    (183, 189, 100),
    (192, 188,  96),
    (200, 188,  93),
    (209, 187,  89),
    (217, 186,  86),
    (225, 185,  82),
    (233, 185,  78),
    (241, 185,  74),
    (248, 187,  68),
    (253, 190,  61),
    (255, 195,  55),
    (254, 200,  50),
    (252, 206,  46),
    (250, 211,  42),
    (247, 216,  38),
    (245, 222,  33),
    (245, 228,  29),
    (245, 235,  24),
    (246, 243,  19),
    (249, 251,  14),
]

_cm_name = "parolinum"
_cm_data = to_float(_parolinum_data)

parolinum = make_cmap(_cm_name, _cm_data, ncolors=256)

register_cmap(parolinum, name=_cm_name)
