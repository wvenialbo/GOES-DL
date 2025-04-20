# GOES-DL — Satellite Imagery Dataset Accessing Toolbox

[![AutoPEP](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-autopep.yml/badge.svg)](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-autopep.yml)
[![Bandit](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-bandit.yml/badge.svg)](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-bandit.yml)
[![Black](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-black.yml/badge.svg)](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-black.yml)
[![DocSig](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-docsig.yml/badge.svg)](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-docsig.yml)
[![Flake8](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-flake.yml/badge.svg)](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-flake.yml)
[![ISort](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-isort.yml/badge.svg)](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-isort.yml)
[![MyPy](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-mypy.yml/badge.svg)](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-mypy.yml)
[![PyCodeStyle](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-pycodestyle.yml/badge.svg)](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-pycodestyle.yml)
[![PyDocLint](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-pydoclint.yml/badge.svg)](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-pydoclint.yml)
[![PyDocStyle](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-pydocstyle.yml/badge.svg)](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-pydocstyle.yml)
[![PyFlakes](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-pyflakes.yml/badge.svg)](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-pyflakes.yml)
[![Pylint](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-pylint.yml/badge.svg)](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-pylint.yml)
[![Ruff](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-ruff.yml/badge.svg)](https://github.com/wvenialbo/GOES-DL/actions/workflows/python-ruff.yml)

*Since 1975, Geostationary Operational Environmental Satellites (GOES) have
provided continuous imagery and data on atmospheric conditions and solar
activity (space weather). They have even aided in search and rescue of people
in distress. GOES data products have led to more accurate and timely weather
forecasts and better understanding of long-term climate conditions. The
National Aeronautics and Space Administration (NASA) builds and launches the
GOES, and the National Oceanic and Atmospheric Administration (NOAA) operates
them &#91;[6](#hist)&#93;.*

**GOES-DL** is an open-source Python package that simplifies the process of
downloading satellite imagery datasets from various NOAA archives. This toolkit
supports second, third and fourth-generation GOES satellite data
&#91;[4](#goesi),[7](#goesr)&#93;, as well as the Gridded Satellite B1
(GridSat-B1) Climate Data Record &#91;[3](#gridb1)&#93;. GOES-DL provides an
easy-to-use interface to access data for scientific analysis, research, and
other applications.

> **Attention GOES-16 Data Users! (updated on 4/7/2025):**
>
> On April 7, 2025 at 15:10 UTC, the GOES-19 satellite was declared the
Operational GOES-East satellite. Shortly following the transition of GOES-19 to
GOES-East, all data distribution from GOES-16 will be turned off. GOES-16 will
commence drifting to the storage location at 104.7°W. All GOES-19 data are
available back to beta product declaration dates.

## Key Features

- **Real-time GOES 4th Generation Satellite Data (GOES Series R)**: Access
  real-time and archived data from NOAA's Amazon Web Services (AWS) cloud
  archive.

- **Gridded Satellite Data from GOES 2nd and 3rd Generation (GridSat-GOES)**:
  Download data from NOAA's National Centers for Environmental Information
  (NCEI) archive.

- **Gridded Satellite Data from ISCCP B1 (GridSat-B1)**: Fetch historical
  climate data from both NOAA's AWS archive and the NCEI archive.

- Seamless integration of different data sources into a unified download
  process, providing fundamental functionalities for meteorological satellite
  dataset handling.

- High-level API that abstracts away the complexity of data access from NOAA
  archives provides the foundations for streamlining the process of downloading
  satellite dataset imagery.

- Efficient extraction of data segments directly from NetCDF4 files streamlines
  the process of reading Level 2 GOES-R Series en GridSat satellite imagery.

## Supported Datasets

1. **GOES 2nd Generation (GOES-8 to GOES-12)**: Also known as the I to M
   Series, these datasets provide environmental monitoring and meteorological
   data for the Western Hemisphere &#91;[4](#goesi)&#93;.

2. **GOES 3rd Generation (GOES-13 to GOES-15)**: Also known as the N to P
   Series, these datasets provide environmental monitoring and meteorological
   data for the Western Hemisphere &#91;[4](#goesi)&#93;.

3. **GOES 4th Generation (GOES-16 to GOES-19)**: Also known as the R to U
   Series, these satellites offer advanced imagery and atmospheric measurements
   with better spatial, spectral, and temporal resolution &#91;[7](#goesr)&#93;.

4. **GridSat-B1 Climate Data Record (Version 2)**: Gridded satellite imagery
   for climate research, containing global infrared window, visible, and water
   vapor data over long time periods &#91;[3](#gridb1)&#93;.

Refer to [Gridded Satellite GOES (GridSat-GOES) East and West Full Disk and
CONUS Coverage, Version 1][52] and [NOAA Climate Data Record (CDR) of Gridded
Satellite Data from ISCCP B1 (GridSat-B1) Infrared Channel Brightness
Temperature, Version 2][53] for more information on the data format and details
of the content.

See [NOAA Geostationary Operational Environmental Satellites (GOES) 16, 17, 18
& 19][11] and [NOAA GOES on AWS (CICS)][12] for information on the GOES-R
Series data available from NOAA on AWS. You can find much more detailed
information about GOES-R Series data from NOAA's [Geostationary Operational
Environmental Satellites - R Series][0].

## Installation

To install **GOES-DL**, use `pip`:

```bash
pip install goes-dl
```

To update **GOES-DL**, use:

```bash
pip install --upgrade goes-dl
```

## Usage

Below are examples of how to use the GOES-DL package to download data from each
of the supported sources. You will find more examples in the
[examples](https://github.com/wvenialbo/GOES-DL/tree/main/examples) directory
of the repository. Some demonstrations are also available in Google Colab, see
below.

### 1. Download GOES 2nd and 3rd Generation Data (from NOAA's NCEI archive)

```python
# Import the locator and datasource according to your desired product
from goesdl.gridsat import GridSatProductLocatorGC
from goesdl.datasource import DatasourceNCEI
from goesdl.downloader import Downloader

# Initialize the product locator for GridSat-GOES (GOES-12, Full Disk)
locator = GridSatProductLocatorGC("F", "G12")

# GridSat-GOES data is available in HTTP from NCEI's archive
datasource = DatasourceNCEI(locator)

# Initialize the downloader with the locator and datasource
downloader = Downloader(
    datasource=datasource,
    locator=locator,
    repository="./my_data/gridsat-gc",
    date_format="%Y-%m-%dT%H:%M%z",  # use a custom short date format
)

# Download the dataset for a specific date
files1 = downloader.download_files(start="2012-08-23T00:00Z")

# ...or download the datasets within a given date range
files2 = downloader.download_files(
   start="2012-08-23T00:00-0004",
   end="2012-08-24T00:00-0004",
)

# `files1` and files2` are lists of strings with the path of the downloaded
# files relative to the base URL and local repository root directory.
```

### 2. Download GOES 4th Generation Data (from NOAA's AWS archive)

```python
# Import the locator and datasource according to your desired product
from goesdl.goesr import GOESProductLocatorABIPP
from goesdl.datasource import DatasourceAWS
from goesdl.downloader import Downloader

# Initialize the product locator for GOES-R Series (set your desired product)
locator = GOESProductLocatorABIPP("CMIP", "F", ["C02", "C08", "C13"], "G16")

# GOES-16 data is updated every 10 minutes. If you are downloading
# old data, you may leave the cache refresh rate as default (+inf).
datasource = DatasourceAWS(locator, cache=600)

# Initialize the downloader with the locator and datasource
downloader = Downloader(
    datasource=datasource,
    locator=locator,
    repository="./my_data/goes-r",
)

# Download the dataset for a specific date
files1 = downloader.download_files(start="2024-08-23T00:00:00Z")

# ...or get the list of datasets within a given date range
files2 = downloader.list_files(
   start="2024-08-23T00:00:00-0004",  # use the default date format
   end="2024-08-24T00:00:00-0004",
)

# ...custom filter the dataset list to download only the desired channels
file_list = [f for f in files2 if "C13" in f]

# ...and download the files in the filtered list
downloader.get_files(file_list)

# `files1` and files2` are lists of strings with the path of the downloaded
# files relative to the base URL and local repository root directory.
```

### 3. Download GridSat-B1 Data (from NOAA's AWS archive)

```python
# Import the locator and datasource according to your desired product
from goesdl.gridsat import GridSatProductLocatorB1
from goesdl.datasource import DatasourceAWS
from goesdl.downloader import Downloader

# Initialize the product locator for GridSat-B1
locator = GridSatProductLocatorB1()

# GridSat-B1 data is available in AWS from NOAA's archive
# Note: GridSat-B1 is lso available in HTTP from NCEI's
# archive, see next example
datasource = DatasourceAWS(locator)

# Initialize the downloader with the locator and datasource
downloader = Downloader(
    datasource=datasource,
    locator=locator,
    repository="./my_data/gridsat-b1",
    date_format="%Y-%m-%dT%H:%M%z",
)

# Download the dataset for a specific date
files1 = downloader.download_files(start="1984-08-23T00:00Z")

# ...or download the datasets within a given date range
files2 = downloader.download_files(
   start="1984-08-23T00:00-0004",
   end="1984-08-24T00:00-0004",
)

# `files1` and files2` are lists of strings with the path of the downloaded
# files relative to the base URL and local repository root directory.
```

### 4. Download GridSat-B1 Data (from NOAA's NCEI archive)

```python
# Import the locator and datasource according to your desired product
from goesdl.gridsat import GridSatProductLocatorB1
from goesdl.datasource import DatasourceNCEI
from goesdl.downloader import Downloader

# Initialize the product locator for GridSat-B1
locator = GridSatProductLocatorB1()

# GridSat-B1 data is available in HTTP from NCEI's archive
# Note: NCEI archive has the same folder structure as AWS, so, if you have
# downloaded data from AWS, you can use the same locator and change the
# datasource to HTTP. If a file is not found in the local repository, it
# will be downloaded from the remote datasource. In all previous examples,
# if a file was already downloaded, it will not be downloaded again.
datasource = DatasourceNCEI(locator)

# Initialize the downloader with the locator and datasource
downloader = Downloader(
    datasource=datasource,
    locator=locator,
    repository="./my_data/gridsat-b1",
    date_format="%Y-%m-%dT%H:%M%z",
)

# Download the dataset for a specific date
files1 = downloader.download_files(start="1984-08-23T00:00Z")

# ...or, alternatively, your can get the list of files within a date range
files2 = downloader.list_files(
   start="1984-08-23T00:00-0004",
   end="1984-08-24T00:00-0004",
)

# ...perform any processing you need to do with the list of files...
...

# ...and pass that resulting or filtered list to the `get_files` method
downloader.get_files(files2_filtered)

# `files1` and files2` are lists of strings with the path of the downloaded
# files relative to the base URL and local repository root directory.
```

## Demos: Colab Notebooks

1. [Hurricane Félix — Parallax effect](https://colab.research.google.com/drive/12aH5OIRPEcaWoL9e3atYDJekZPczVca9?usp=sharing)
2. [Storm-2012 — La tempestad en Roque Alonso](https://colab.research.google.com/drive/12aH5OIRPEcaWoL9e3atYDJekZPczVca9?usp=sharing)

## Pipeline and parameters

The general workflow for downloading data using **GOES-DL** is as follows:

1. **Initialize the locator**: Import the appropriate locator class for the
   desired product and satellite and initialize a locator object. The product
   locator provides the necessary information to find the data files in the
   dataset repository. This is the only step that is specific to the dataset
   being downloaded.
2. **Initialize the datasource**: Import the appropriate datasource class for
   the desired dataset and instantiate a datasource object. The datasource
   provides the necessary functionality to access the data files from the
   repository, it abstracts the complexity of accessing data from different
   sources. This step is common to all datasets. The datasource is Initialized
   with the locator object.
3. **Initialize the downloader**: Import the downloader class and initialize a
   downloader object. The downloader is the main interface for downloading data.
   It is initialized with the datasource and locator objects, as well as the
   date format to be used in the download process.

The `Downloader.download_files` and `Downloader.list_files` method accepts the
following parameters:

- **start_time**: A string specifying the starting date for the dataset to be
  downloaded.
- **end_time**: A string specifying the ending date for the dataset to be
  downloaded. If not provided, only the data for the start_time will be
  downloaded.

The default date format is the ISO 8601 format with timezone information
(`"%Y-%m-%dT%H:%M:%S%z"`). The date format can be changed by passing the desired
format to the downloader object during initialization.

The `Downloader.get_files` method accepts a list of strings with the paths of
the files to be downloaded. This method is useful when you want to download only
a subset of the files listed by the `Downloader.list_files` method.

## Data Sources

1. **NOAA NCEI Archive**: GridSat-B1 Climate Data Record and GOES-8 to GOES-15
   data is available through NOAA’s National Centers for Environmental
   Information.
2. **NOAA AWS Cloud Archive**: GOES-16 to GOES-19 data and GridSat-B1 Climate
   Data Record are accessible via the NOAA archive hosted on AWS.

## Project description

Tool package to download and read Geostationary Operational Environmental
Satellite 2nd, 3rd and 4th Generation (GOES-8 to GOES-19) and Gridded Satellite
(GridSat-B1 and GridSat-GOES) imagery datasets from NOAA's AWS and NCEI cloud
repositories using Python.

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
[downloader](https://github.com/topics/downloader),
[download](https://github.com/topics/download),
[xarray](https://github.com/topics/xarray)

## Contributing

Contributions to **GOES-DL** are welcome! If you'd like to contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Open a pull request with a description of your changes.

Please make sure to include tests for any new functionality.

## Requirements

- Python 3.10+
- [Boto3](https://pypi.org/project/boto3): AWS SDK for Python.
- [Cartopy](https://pypi.org/project/cartopy/): A Python library for
  cartographic visualizations with Matplotlib.
- [Matplotlib](https://pypi.org/project/matplotlib/): Python plotting package.
- [netCDF4](https://pypi.org/project/netCDF4/): Provides an object-oriented
  python interface to the netCDF version 4 library.
- [NumPy](https://pypi.org/project/numpy/): Fundamental package for array
  computing in Python.
- [Pillow (PIL)](https://pypi.org/project/pillow/): Python Imaging Library (Fork)
- [Pyproj](https://pypi.org/project/pyproj/): Python interface to PROJ
  (cartographic projections and coordinate transformations library).
- [Requests](https://pypi.org/project/requests): A simple, yet elegant, HTTP
  library for Python.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file
for details.

## Acknowledgments

This package relies on data provided by NOAA’s NCEI and NOAA’s archive on AWS.

## Credits

When using **GOES-DL** in any research, publication or website, please cite this
package as:

> Villamayor-Venialbo, W. (2025): *GOES-DL: A Python package for downloading
> GOES and GridSat-B1 satellite data (Version 0.2-rc6)* [Software]. GitHub.
> [git:wvenialbo/GOES-DL](https://github.com/wvenialbo/GOES-DL), *[indicate
> access date]*.

### Credits for GOES-R Series Data

**Dataset Citation:**

For Cloud and Moisture Imagery Products (CMIP), please cite the following:

> GOES-R Algorithm Working Group, and GOES-R Series Program (2017): NOAA GOES-R
> Series Advanced Baseline Imager (ABI) Level 2 Cloud and Moisture Imagery
> Products (CMIP). *[indicate subset used]*. *NOAA National Centers for
> Environmental Information*, [doi:10.7289/V5736P36][51], *[access date]*.

For other products, please, visit [NOAA National Centers for Environmental
Information][10].

### Credits for GridSat-GOES/CONUS

**Dataset Citation:**

> Knapp, K. R. (2017): Gridded Satellite GOES Coverage Data (GridSat-GOES),
> *[indicate subset used]*. *NOAA National Centers for Environmental
> Information*, [doi:10.7289/V5HM56GM][52], *[indicate access date]*.

Please cite the following article when using GridSat-GOES/CONUS data in any
publication:

> Knapp, K. R. and Wilkins, S. L.: Gridded Satellite (GridSat) GOES and CONUS
> data, *Earth System Science Data*, **10(3)**, 1417–1425,
> [doi:10.5194/essd-10-1417-2018](https://doi.org/10.5194/essd-10-1417-2018),
> 2018.

### Credits for GridSat-B1

**Dataset Citation:**

> Knapp, K. R.; NOAA CDR Program; (2014): NOAA Climate Data Record (CDR) of
> Gridded Satellite Data from ISCCP B1 (GridSat-B1) Infrared Channel Brightness
> Temperature, Version 2, *[indicate subset used]*. *NOAA National Centers for
> Environmental Information*, [doi:10.7289/V59P2ZKR][53], *[indicate access
> date]*.

Please cite the following article when using GridSat-B1 data in any publication:

> Knapp, K. R., Ansari S.; Bain, C. L.; Bourassa, M. A.; Dickinson, M. J.; Funk,
> C.; Helms, C. N.; Hennon, C. C.; Holmes, C. D.; Huffman, G. J.; Kossin, J. P.;
> Lee, H.-T.; Loew, A.; and Magnusdottir, G.: Globally gridded satellite
> (GridSat) observations for climate studies. *Bulletin of the American
> Meteorological Society*, **92(7)**, 893-907,
> [doi:10.1175/2011BAMS3039.1](https://doi.org/10.1175/2011BAMS3039.1), 2011.

When possible, please cite the following article when using the ISCCP-B1 data or
other ISCCP-B1 imagery or GIBBS imagery in a publication or website:

> Knapp, K. R.: Scientific data stewardship of International Satellite Cloud
> Climatology Project B1 global geostationary observations. *Journal of Applied
> Remote Sensing*, **2(1)**, 023548,
> [doi:10.1117/1.3043461](https://doi.org/10.1117/1.3043461), 2008.

## Contact and Support

For issues, questions, or requests, feel free to open an issue on this
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

1. Knapp, K. R. (2008): Scientific data stewardship of International Satellite
   Cloud Climatology Project B1 global geostationary observations. *Journal of
   Applied Remote Sensing*, **2(1)**, 023548,
   [doi:10.1117/1.3043461](https://doi.org/10.1117/1.3043461).
2. Knapp, K. R., Ansari S.; Bain, C. L.; Bourassa, M. A.; Dickinson, M. J.;
   Funk, C.; Helms, C. N.; Hennon, C. C.; Holmes, C. D.; Huffman, G. J.; Kossin,
   J. P.; Lee, H.-T.; Loew, A.; and Magnusdottir, G.; (2011): Globally gridded
   satellite (GridSat) observations for climate studies. *Bulletin of the
   American Meteorological Society*, **92(7)**, 893-907,
   [doi:10.1175/2011BAMS3039.1](https://doi.org/10.1175/2011BAMS3039.1).
3. Knapp, K. R; NOAA CDR Program; (2014): NOAA Climate Data Record (CDR) of
   Gridded Satellite Data from ISCCP B1 (GridSat-B1) Infrared Channel Brightness
   Temperature, Version 2. *NOAA National Centers for Environmental
   Information*, [doi:10.7289/V59P2ZKR][53].<a
   name="gridb1"></a>
4. Knapp, K. R; (2017): Gridded Satellite GOES Coverage Data (GridSat-GOES).
   *NOAA National Centers for Environmental Information*.
   [doi:10.7289/V5HM56GM][52].<a name="goesi"></a>
5. Knapp, K. R. and Wilkins, S. L.; (2018): Gridded Satellite (GridSat) GOES and
   CONUS data, *Earth System Science Data*, 10(3), 1417–1425,
   [doi:10.5194/essd-10-1417-2018](https://doi.org/10.5194/essd-10-1417-2018).
6. GOES History. *GOES-R Website*,
   [https://www.goes-r.gov/mission/history.html][1], retrieved on 2024.<a
   name="hist"></a>
7. GOES-R Series Data Products. *GOES-R Website*,
   [https://www.goes-r.gov/products/overview.html][2], retrieved on 2024.<a
   name="goesr"></a>
8. NOAA Big Data Program, *NOAA Open Data Dissemination Program*,
   [https://github.com/NOAA-Big-Data-Program/bdp-data-docs][21], retrieved on
   2024.
9. Beginner’s Guide to GOES-R Series Data: How to acquire, analyze, and
   visualize GOES-R Series data, *Resources compiled by GOES-R Product Readiness
   and Operations*, Satellite Products and Services Division, National Oceanic
   and Atmospheric Administration.  [PDF][42]. Last Updated on May 23, 2024,
   retrieved on 2024.
10. GOES-R Series Data Book, *GOES-R Series Program Office*, Goddard Space
    Flight Center, National Aeronautics and Space Administration. [PDF][41],
    retrieved on 2024.

<!-- markdownlint-restore -->

<!-- hidden-references: named links -->

[0]: https://www.goes-r.gov/
[1]: https://www.goes-r.gov/mission/history.html
[2]: https://www.goes-r.gov/products/overview.html
[10]: https://www.ncei.noaa.gov/
[11]: https://registry.opendata.aws/noaa-goes/
[12]: https://docs.opendata.aws/noaa-goes16/cics-readme.html
[21]: https://github.com/NOAA-Big-Data-Program/bdp-data-docs
[22]: https://github.com/blaylockbk/goes2go
[23]: https://github.com/joaohenry23/GOES
[31]: https://goes2go.readthedocs.io/
[41]: https://www.goes-r.gov/downloads/resources/documents/GOES-RSeriesDataBook.pdf
[42]: https://www.goes-r.gov/downloads/resources/documents/Beginners_Guide_to_GOES-R_Series_Data.pdf
[51]: https://doi.org/10.7289/V5736P36
[52]: https://doi.org/10.7289/V5HM56GM
[53]: https://doi.org/10.7289/V59P2ZKR
