# Enhancement regions
#     - 180K - 220K
#     - ...
#     - 205K - 220K
# default: 200K - 240K

st_step = 5
st_delta = -40
st_width = 40

st_range = range(180, 205 + st_step, st_step)

st_template = [
    (0.0, 0.0),
    (40.0, 40.0),
    (80.0, 80.0),
    (167.5, 255.0),
]

st_names = [f"K{keypoint}-{keypoint+st_width}" for keypoint in st_range]

st_default_i = 4

st_tables = [
    [(x0 + keypoint + st_delta, x1) for x0, x1 in st_template]
    for keypoint in st_range
]

st_stok = dict(zip(st_names, st_tables))

st_default = st_stok[st_names[st_default_i]]
