# Enhancement regions
#     - 180K - 220K
#     - ...
#     - 205K - 220K
# default: 200K - 240K

st_step = 5
st_delta = -29
st_width = 40

st_range = list(range(180, 205 + st_step, st_step))

st_template = [
    (0.0, 255.0),
    (29.0, 226.0),
    (69.0, 186.0),
    (255.0, 0.0),
]

st_names = [f"K{keypoint}-{keypoint+st_width}" for keypoint in st_range]

st_default_i = 4

st_tables = [
    [(x0 + keypoint + st_delta, x1) for x0, x1 in st_template]
    for keypoint in st_range
]

st_stock = dict(zip(st_names, st_tables))

st_default = st_names[st_default_i]

st_extended = {
    "cira_ircimss2": [
        (159.0, 255.0),
        (240.0, 174.0),
        (327.0, 0.0),
    ],
    "smn_ircimss2": [
        (164.2, 255.0),
        (193.2, 226.0),
        (203.2, 216.0),
        (213.2, 206.0),
        (223.2, 194.0),
        (233.2, 182.0),
        (243.2, 170.0),
        (323.2, 0.0),
    ],
}

st_stock |= st_extended
