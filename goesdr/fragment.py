from .datarecord import DataRecord


def netcdf_fragment(recordclass: type) -> type:
    origin_bases = recordclass.__bases__
    if DataRecord not in origin_bases:
        new_bases = (DataRecord,) + origin_bases
        recordclass.__bases__ = new_bases
    return recordclass
