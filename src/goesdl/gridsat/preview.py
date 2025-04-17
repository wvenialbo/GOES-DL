from typing import cast

from cartopy import crs as ccrs
from cartopy.crs import Globe, PlateCarree, Projection
from cartopy.feature import NaturalEarthFeature
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
from matplotlib import pyplot as plt
from matplotlib.collections import QuadMesh
from matplotlib.ticker import MultipleLocator
from netCDF4 import Dataset

from ..enhancement import EnhancementScale, cmap
from ..geodesy import RectangularRegion
from .netcdf_geodetic import GSLatLonGrid
from .netcdf_image import GSImage
from .netcdf_metadata import GSDatasetMetadata
from .netcdf_time import GSCoverageTime

# Create the Natural Earth projection (Platé-Carrée projection on WGS84 ellipsoid)


def read_gridsat_dataset(
    dataframe: Dataset, channel: str, region: RectangularRegion
) -> tuple[GSImage, GSCoverageTime, GSDatasetMetadata]:
    grid = GSLatLonGrid(dataframe, region)  # , corners=True

    data = GSImage(dataframe, channel, grid)

    coverage = GSCoverageTime(dataframe)

    metadata = GSDatasetMetadata(dataframe, channel)

    return data, coverage, metadata


class GSPlotParameter:

    title: str | tuple[str, str] = ""
    axis_label: tuple[str, str] = "", ""
    cbar_label: str = ""

    def __init__(
        self,
        title: str | tuple[str, str] = "",
        axis_label: tuple[str, str] = ("", ""),
        cbar_label: str = "",
    ) -> None:
        self.title = title
        self.axis_label = axis_label
        self.cbar_label = cbar_label


class GSPlot:

    # The figure dimensions (in inches)
    fig_size: tuple[float, float] = 4.0, 4.0

    # The figure resolution (in number of dots per inch)
    fig_dpi: int = 200

    # The image output resolution (in number of dots per inch)
    img_dpi: int = 200

    near_earth_scale: str = "10m"

    enhancement: EnhancementScale

    crs: Projection

    def __init__(self) -> None:
        self.enhancement = cmap["IRCOLOR"]

        # Create the target plot projection (same as above)

        target_globe = Globe(ellipse="WGS84")

        self.crs = PlateCarree(central_longitude=0.0, globe=target_globe)

    def plot(
        self,
        image: GSImage,
        param: GSPlotParameter,
        save_path: str = "",
        show: bool = True,
    ) -> None:
        # Create the figure and setup the axes
        fig = plt.figure("map", figsize=self.fig_size, dpi=self.fig_dpi)

        # Create the axes ith the required projection, i.e., `target_crs` (see definition above)
        ax = fig.add_axes((0.1, 0.16, 0.80, 0.75), projection=self.crs)

        self._add_grid(ax, image.region, param.axis_label)

        self._add_admin_info(ax)

        self._add_crosshair(ax)

        # Plot the data (in `gcrs`, see definition above) with a color map from the stock
        # shading;
        #   - center:  lon.shape == image.shape => "nearest" == "auto" == None | "gouraud"
        #   - corners: lon.shape != image.shape => "flat" == "auto" == None
        mesh = self._plot_data(ax, image)

        self._add_colorbar(mesh, fig, param.cbar_label)

        self._add_title(ax, param.title)

        # Save the media file (ensure the destination path does exist)
        if save_path:
            plt.savefig(save_path, dpi=self.img_dpi, bbox_inches="tight")

        # Show the plot
        if show:
            plt.show()
        else:
            plt.close()

    def save(
        self, save_path: str, image: GSImage, param: GSPlotParameter
    ) -> None:
        self.plot(image, param, save_path, False)

    def show(self, image: GSImage, param: GSPlotParameter) -> None:
        self.plot(image, param)

    def _add_admin_info(self, ax: plt.Axes) -> None:  # type: ignore
        # Create the Natural Earth projection (Platé-Carrée projection
        # on WGS84 ellipsoid)

        natearth_globe = ccrs.Globe(ellipse="WGS84")

        natearth_crs = ccrs.PlateCarree(
            central_longitude=0.0,
            globe=natearth_globe,
        )

        # Create political boundaries, in `natearth_crs` (see definition above)
        provinces = NaturalEarthFeature(
            category="cultural",
            name="admin_1_states_provinces",
            scale=self.near_earth_scale,
            facecolor="none",
            transform=natearth_crs,
        )

        countries = NaturalEarthFeature(
            category="cultural",
            name="admin_0_countries",
            scale=self.near_earth_scale,
            facecolor="none",
            transform=natearth_crs,
        )

        # Add political boundaries to the plot using our plot projection
        ax.add_feature(
            provinces, edgecolor="gray", linewidth=0.25, transform=self.crs
        )
        ax.add_feature(
            countries, edgecolor="black", linewidth=0.25, transform=self.crs
        )

    def _add_colorbar(
        self, mesh: QuadMesh, fig: plt.Figure, label: str  # type: ignore
    ) -> None:

        # Add the colorbar
        caxes = fig.add_axes([0.12, 0.05, 0.76, 0.02])
        cb = plt.colorbar(
            mesh,
            ticks=self.enhancement.cticks,
            orientation="horizontal",
            extend="both",
            cax=caxes,
        )

        # Create a minor tick locator for the colorbar
        minor_locator = MultipleLocator(5)

        # Set the colorbar tick characteristics
        cb.ax.xaxis.set_minor_locator(minor_locator)
        cb.ax.tick_params(
            labelsize=4,
            labelcolor="black",
            width=0.5,
            length=2.0,
            direction="out",
            pad=1.0,
        )
        cb.ax.tick_params(axis="both", which="minor", length=1.5, width=0.4)

        # Set the colorbar caption
        # f"{cmi_entity} {cmi_measure} [{cmi_units}]" -> TOA Brightness Temperature
        # cb_label = f"{image.metadata.long_name} @ {metadata.wavelength:.1f} μm [{image.metadata.units}]"
        cb.set_label(label=label, size=5.0, color="black", weight="normal")

        # Set the colorbar characteristics
        cb.outline.set_linewidth(0.4)  # type: ignore[operator]

    def _add_crosshair(self, ax: plt.Axes) -> None:  # type: ignore
        # Add a crosshair to the plot
        xlims = ax.get_xlim()
        ylims = ax.get_ylim()
        center_x = (xlims[1] + xlims[0]) / 2
        center_y = (ylims[1] + ylims[0]) / 2
        ax.axvline(x=center_x, color="red", linewidth=0.4)
        ax.axhline(y=center_y, color="red", linewidth=0.4)

    def _add_grid(
        self,
        ax: plt.Axes,  # type: ignore
        region: RectangularRegion,
        labels: tuple[str, str],
    ) -> None:

        # Set gridline ticks characteristics
        ax.tick_params(
            left=True,
            right=True,
            bottom=True,
            top=True,
            labelleft=True,
            labelright=False,
            labelbottom=True,
            labeltop=False,
            length=0.0,
            width=0.05,
            labelsize=4.5,
            labelcolor="black",
        )

        # Add gridlines, set the longitude and latitude grid major tick locations,
        # set gridline characteristics, and configure gridline labels
        ax.gridlines(
            xlocs=region.xticks,
            ylocs=region.yticks,
            linewidth=0.25,
            linestyle="--",
            color="red",
            alpha=0.6,
            draw_labels=False,
        )

        # Set X-axis label characteristics
        ax.set_xticks(region.xticks, crs=self.crs)
        ax.xaxis.set_major_formatter(
            LongitudeFormatter(dateline_direction_label=True)
        )
        ax.set_xlabel(
            labels[0],
            color="black",
            fontsize=6,
            labelpad=3.0,
        )

        # Set Y-axis label characteristics
        ax.set_yticks(region.yticks, crs=self.crs)
        ax.yaxis.set_major_formatter(LatitudeFormatter())
        ax.set_ylabel(
            labels[1],
            color="black",
            fontsize=6,
            labelpad=3.0,
        )

        # Set the map limits, in `target_crs` (see definition above)
        ax.set_extent(region.extent, crs=self.crs)

    def _add_title(
        self,
        ax: plt.Axes,  # type: ignore
        title: str | tuple[str, str],
    ) -> None:
        # Set the title
        if isinstance(title, str):
            plt.title(title)
            return

        ax.set_title(title[0], fontsize=6.5, loc="left")
        ax.set_title(title[1], fontsize=6.5, loc="right")

    def _plot_data(
        self,
        ax: plt.Axes,  # type: ignore
        data: GSImage,
    ) -> QuadMesh:
        # Plot the data (in `gcrs`, see definition above) with a color map from the stock
        # shading;
        #   - center:  lon.shape == image.shape => "nearest" == "auto" == None | "gouraud"
        #   - corners: lon.shape != image.shape => "flat" == "auto" == None

        mesh = ax.pcolormesh(
            data.grid.lon,
            data.grid.lat,
            data.image,
            shading="gouraud",  #
            cmap=self.enhancement.cmap,
            norm=self.enhancement.cnorm,
            transform=data.grid.crs,
        )

        return cast(QuadMesh, mesh)
