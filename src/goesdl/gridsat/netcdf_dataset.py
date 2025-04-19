from ..netcdf import attribute
from .netcdf_platform import PlatformMetadata


class GSDatasetMetadata(PlatformMetadata):

    title: str = attribute()
    id: str = attribute()
    summary: str = attribute()
    conventions: str = attribute("Conventions")
    license: str = attribute()
    processing_level: str = attribute()
    product_version: str = attribute()
    project: str = attribute()
    institution: str = attribute()
    comment: str = attribute()
    instrument: str = attribute()
    keywords: str = attribute()
    platform_vocabulary: str = attribute()
    sensor_vocabulary: str = attribute()
    keywords_vocabulary: str = attribute()
    naming_authority: str = attribute()
    standard_name_vocabulary: str = attribute()
    metadata_link: str = attribute()
    ncei_template_version: str = attribute()
    date_created: str = attribute()
    date_modified: str = attribute()
    projection: str = attribute("Projection")
    time_coverage_start: str = attribute()
    time_coverage_end: str = attribute()
    history: str = attribute()
