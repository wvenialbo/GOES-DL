# GOES-CORE — GOES Satellite Dataset Access Core Functionality

*Since 1975, Geostationary Operational Environmental Satellites (GOES) have
provided continuous imagery and data on atmospheric conditions and solar
activity (space weather). They have even aided in the search and rescue of
people in distress. GOES data products have led to more accurate and timely
weather forecasts and a better understanding of long-term climate conditions.
The National Aeronautics and Space Administration (NASA) builds and launches
the GOES, and the National Oceanic and Atmospheric Administration (NOAA)
operates them &#91;[1](#hist)&#93;.*

**GOES-CORE** is an open-source Python package that provides the foundations
for streamlining the process of downloading and reading satellite dataset
imagery. This toolkit enables efficient dataset downloading from various
data sources and provides tools for extracting data segments directly from
NetCDF4 files produced by [GOES-R Series][0] satellites &#91;[2](#goesr)&#93;
and other similar datasets &#91;[3](#b1),[4](#ggc)&#93;.

## Key Features

- Seamless integration of different data sources into a unified download
  process.
- High-level API that abstracts away the complexity of data access from NOAA
  archives.

## Project Description

Core repository providing fundamental functionalities for meteorological and
climate dataset handling. This repository consolidates essential code to serve
as a foundation for environmental data processing ecosystems.

**Keywords:**
[goes](https://github.com/topics/goes),
[satellite](https://github.com/topics/satellite),
[satellite-dataset](https://github.com/topics/satellite-dataset),
[satellite-imagery](https://github.com/topics/satellite-imagery),
[satellite-imagery-analysis](https://github.com/topics/satellite-imagery-analysis),
[satellite-imagery-python](https://github.com/topics/satellite-imagery-python),
[satellite-data](https://github.com/topics/satellite-data),
[noaa](https://github.com/topics/noaa),
[noaa-satellite](https://github.com/topics/noaa-satellite),
[ncei](https://github.com/topics/ncei),
[unidata](https://github.com/topics/unidata),
[unidata-netcdf](https://github.com/topics/unidata-netcdf),
[netcdf](https://github.com/topics/netcdf),
[netcdf4](https://github.com/topics/netcdf4),
[aws](https://github.com/topics/aws),
[open-data](https://github.com/topics/open-data),
[open-source](https://github.com/topics/open-source),
[open-datasets](https://github.com/topics/open-datasets),
[python](https://github.com/topics/python),
[xarray](https://github.com/topics/xarray)

## Components

- **Ready-to-use classes**: Includes data source (`DatasourceAWS`,
  `DatasourceNCEI`, `DatasourceLocal`) and `Downloader` classes for direct use
  by end-users.
- **Developer API**: Defines the `Datasource` and `ProductLocator` abstract
  classes for data source handlers and product locators, establishing a clear
  API for developers creating meteorological and climate dataset downloaders.
- **Ecosystem Base**: Serves as a foundation for building and expanding tools
  within the meteorological and climate data ecosystem, promoting modularity
  and code reusability.

## Supported Data Sources

1. **NOAA’s AWS Cloud Archive**: A handler for NOAA’s ([National Oceanic and
   Atmospheric Administration][10]) Amazon Web Services Cloud Archive is
   provided.  *[GOES-R Series][0] (GOES-16 to GOES-18)* real-time data
   &#91;[2](#goesr)&#93; and *[GridSat-B1 Climate Data Record][42]* datasets
   &#91;[3](#b1)&#93; are accessible via the NOAA’s archive hosted on AWS.
2. **NOAA’s NCEI Archive**: A handler for NCEI’s ([National Centers for
   Environmental Information][11]) HTTP repository is provided. Several
   datasets, like *[GridSat-B1 Climate Data Record][42]* and
   *[GridSat-GOES/CONUS][43]* &#91;[4](#ggc)&#93; are available through NCEI
   Direct Download HTTP servers.

## Installation

To install **GOES-CORE**, use `pip`:

```bash
pip install goes-core
```

To update **GOES-CORE**, use:

```bash
pip install --upgrade goes-core
```

> **NOTE**: GOES-CORE is not a stand-alone package, but rather a foundation
> library intended to be used both by end-users directly (through a client
> application or library) and as a framework for developers building tools
> within meteorological and climate dataset ecosystems.

## Usage

See the [GOES-DL][25] satellite imagery data processing package and similar
projects for real world examples.

## Contributing

Contributions to **GOES-CORE** are welcome! If you would like to contribute,
for instance, adding a new data source handler:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Open a pull request with a description of your changes.

Please make sure to include tests for any new functionality.

## Requirements

- [Python 3.9+](https://www.python.org/) — Python Software Foundation
- [boto3](https://pypi.org/project/boto3): The AWS SDK for Python.
- [netCDF4](https://pypi.org/project/requests): Object-oriented interface to
  the netCDF library.
- [requests](https://pypi.org/project/requests): Python HTTP for Humans.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE)
file for details.

## Credits

When using **GOES-CORE** in any research, publication or website, please cite
this package as:

> Villamayor-Venialbo, W. (2025): *GOES-CORE: Python foundations for
> streamlining satellite dataset imagery access (Version 0.1-rc1)* [Software].
> GitHub. [git:wvenialbo/GOES-CORE][24], *[indicate access date]*.

## Contact and Support

For issues, questions, or requests, please feel free to open an issue on this
repository or contact the author, [wvenialbo at
gmail.com](mailto:wvenialbo@gmail.com).

---

## Similar Projects

- [Brian Blaylock's goes2go][22]: Download and process GOES-16 and GOES-17 data
  from NOAA's archive on AWS using Python.  ([readthedocs][31])
- [Joao Henry's GOES][23]: Python package to download and manipulate
  GOES-16/17/18 data.

<!-- markdownlint-capture -->
<!-- markdownlint-disable MD033 -->

## References

1. GOES History. *GOES-R Website*,
   [https://www.goes-r.gov/mission/history.html][1], retrieved on 2025.<a
   name="hist"></a>
2. GOES-R Series Data Products. *GOES-R Website*,
   [https://www.goes-r.gov/products/overview.html][2], retrieved on 2025.<a
   name="goesr"></a>
3. Geostationary IR Channel Brightness Temperature - GridSat B1. *NCEI’s
   Website*,
   [https://www.ncei.noaa.gov/products/gridded-geostationary-brightness-temperature][41],
   retrieved on 2025.<a name="b1"></a>
4. Gridded Satellite GOES/CONUS. *NCEI’s Website*,
   [https://www.ncei.noaa.gov/products/satellite/gridded-goes-conus][44],
   retrieved on 2025.<a name="ggc"></a>
5. NOAA Big Data Program, *NOAA Open Data Dissemination Program*,
   [https://github.com/NOAA-Big-Data-Program/bdp-data-docs][21], retrieved on
   2024.

<!-- markdownlint-restore -->

<!-- hidden-references: named links -->

[0]: https://www.goes-r.gov/
[1]: https://www.goes-r.gov/mission/history.html
[2]: https://www.goes-r.gov/products/overview.html
[10]: https://www.noaa.gov/
[11]: https://www.ncei.noaa.gov/
[21]: https://github.com/NOAA-Big-Data-Program/bdp-data-docs
[22]: https://github.com/blaylockbk/goes2go
[23]: https://github.com/joaohenry23/GOES
[24]: https://github.com/wvenialbo/GOES-CORE
[25]: https://github.com/wvenialbo/GOES-DL
[31]: https://goes2go.readthedocs.io/
[41]: https://www.ncei.noaa.gov/products/gridded-geostationary-brightness-temperature
[42]: https://www.ncei.noaa.gov/products/climate-data-records/geostationary-IR-channel-brightness-temperature
[43]: https://catalog.data.gov/dataset/gridded-satellite-goes-gridsat-goes-east-and-west-full-disk-and-conus-coverage-version-12
[44]: https://www.ncei.noaa.gov/products/satellite/gridded-goes-conus
