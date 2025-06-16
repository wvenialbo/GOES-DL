from typing import Any, Literal, cast

from cartopy import crs as ccrs
from cartopy.crs import Globe, PlateCarree, Projection
from cartopy.feature import NaturalEarthFeature
from cartopy.mpl.geoaxes import GeoAxes
from cartopy.mpl.gridliner import Gridliner
from cartopy.mpl.ticker import LatitudeFormatter, LongitudeFormatter
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.collections import QuadMesh
from matplotlib.figure import Figure
from matplotlib.spines import Spine
from matplotlib.ticker import MultipleLocator

from ..enhancement import EnhancementScale, get_scale
from ..protocols import GeodeticRegion, SatImageData
from .helpers import (
    BoxGeometry,
    GSPlotParameter,
    MarginGeometry,
    Size,
    SizeGeometry,
    set_outline,
)

ShaddingType = Literal["flat", "nearest", "gouraud", "auto"]
LocationType = Literal["left", "center", "right"]

default_plot_size = SizeGeometry(600, 600)
default_plot_margin = MarginGeometry(88, 150, 24, 50)
default_cbar_box = BoxGeometry(88, 64, 600, 16)


class AZPlot:

    # The figure/image resolution (in number of dots per inch)
    fig_dpi: int = 100

    # The figure dimensions (in inches)
    fig_size: tuple[float, float] = 2.0, 2.0

    axes_box: tuple[float, float, float, float] = 0.0, 0.0, 0.0, 0.0
    cbar_box: tuple[float, float, float, float] = 0.0, 0.0, 0.0, 0.0
    watermark_loc: tuple[float, float] = 0.0, 0.0

    enhancement: EnhancementScale

    crs: Projection

    scale: Size = Size(fig_dpi)

    def __init__(
        self,
        enhancement: EnhancementScale | None = None,
        crs: Projection | None = None,
    ) -> None:
        # Create a default colour-enhancement scale, if not provided
        if enhancement is None:
            enhancement = get_scale("IRCOLOR")

        self.enhancement = enhancement

        # Create a default plot target projection, if not provided
        if crs is None:
            target_globe = Globe(ellipse="WGS84")
            crs = PlateCarree(central_longitude=0.0, globe=target_globe)

        self.crs = crs

    def plot(
        self,
        image: SatImageData,
        param: GSPlotParameter,
        save_path: str = "",
        show: bool = True,
    ) -> None:
        # Setup the figure and axes boxes
        self._setup_boxes(param)

        # Create the figure and setup the axes
        fig = plt.figure(figsize=self.fig_size, dpi=self.fig_dpi)

        # Create the axes ith the required projection, i.e., `target_crs`
        ax = fig.add_subplot(1, 1, 1, projection=self.crs)
        ax.set_position(self.axes_box)

        self._add_grid_cent(fig, ax, image.region, param)

        self._add_map_features(ax, param)

        self._add_crosshair(ax)

        # Plot the data
        mesh = self._plot_data(ax, image, param)

        self._add_colorbar(mesh, fig, param)

        self._add_title(ax, param)

        # Add a watermark to the plot
        self._add_watermark(fig)

        # Save the media file
        if save_path:
            plt.savefig(save_path, dpi=self.fig_dpi, bbox_inches=None)

        # Show the plot
        if show:
            plt.show()
        else:
            plt.close()

    def save(
        self, save_path: str, image: SatImageData, param: GSPlotParameter
    ) -> None:
        self.plot(image, param, save_path, False)

    def show(self, image: SatImageData, param: GSPlotParameter) -> None:
        self.plot(image, param)

    def _add_map_features(self, ax: Axes, param: GSPlotParameter) -> None:
        if not param.nat_earth_features:
            return

        natearth_globe = ccrs.Globe(ellipse="WGS84")

        natearth_crs = ccrs.PlateCarree(
            central_longitude=0.0,
            globe=natearth_globe,
        )

        gax = cast(GeoAxes, ax)

        for feature_id, feature_style in zip(
            param.nat_earth_features, param.nat_earth_style
        ):
            category_name, feature_name = feature_id.split(":")

            linewidth, edgecolor, facecolor = feature_style

            # Create political boundaries, in `natearth_crs`
            feature = NaturalEarthFeature(
                category=category_name,
                name=feature_name,
                scale=param.nat_earth_scale,
                facecolor=facecolor,
                transform=natearth_crs,
            )

            # Add political boundaries to the plot using our plot projection
            gax.add_feature(
                feature,
                edgecolor=edgecolor,
                linewidth=linewidth,
                transform=self.crs,
            )

    def _add_colorbar(
        self, mesh: QuadMesh, fig: Figure, param: GSPlotParameter
    ) -> None:
        # Add a colourbar box
        caxes = fig.add_axes(self.cbar_box)

        # Set the colourbar tick geometry
        cb = plt.colorbar(
            mesh,
            ticks=self.enhancement.ticker.cticks,
            orientation=param.cbar_orientation,
            extend=param.cbar_extend,
            cax=caxes,
        )

        scale = self.scale

        # Set the colourbar characteristics
        cbar_outline: Spine = cb.ax.spines["outline"]
        set_outline(cbar_outline, scale.pt(param.cbar_linewidth))

        # Set the colourbar caption
        cb.set_label(
            label=param.cbar_label,
            size=scale.pt(param.cbar_labelsize),
            color=param.cbar_labelcolor,
            weight=param.cbar_labelweight,
        )

        # Set the colourbar tick characteristics
        cb.ax.tick_params(
            which="both",
            labelsize=scale.pt(param.cbar_tick_labelsize),
            labelcolor=param.cbar_tick_labelcolor,
            direction=param.cbar_tick_direction,
            pad=scale.pt(param.cbar_tick_pad),
        )

        # Set the colourbar major tick characteristics
        cb.ax.tick_params(
            which="major",
            length=scale.pt(param.cbar_tick_major_length),
            width=scale.pt(param.cbar_tick_major_width),
        )

        # Set the colourbar major tick characteristics
        cb.ax.tick_params(
            which="minor",
            length=scale.pt(param.cbar_tick_minor_length),
            width=scale.pt(param.cbar_tick_minor_width),
        )

        # Create a minor tick locator for the colourbar
        minor_locator = MultipleLocator(param.cbar_tick_minor_step)

        cb.ax.xaxis.set_minor_locator(minor_locator)

    def _add_crosshair(self, ax: Axes) -> None:
        # Add a crosshair to the plot
        xlims = ax.get_xlim()
        ylims = ax.get_ylim()
        center_x = (xlims[1] + xlims[0]) / 2
        center_y = (ylims[1] + ylims[0]) / 2
        ax.axvline(x=center_x, color="red", linewidth=0.4)
        ax.axhline(y=center_y, color="red", linewidth=0.4)

    def _add_grid_cent(
        self,
        fig: Figure,
        ax: Axes,
        region: GeodeticRegion,
        param: GSPlotParameter,
    ) -> None:
        gl = self._add_grid(ax, region, param, True)

        # Set X-axis label characteristics
        setattr(
            gl,
            "xlabel_style",
            {
                "color": "black",
                "fontsize": 5,
                "rotation": 0,
                # , 'labelpad': 3.0
            },
        )

        # Set X-axis label
        fig.text(
            0.5,
            0.106,
            param.axis_label[0],
            ha="center",
            va="center",
            fontsize=7,
            color="black",
        )

        # Set Y-axis label characteristics
        setattr(
            gl,
            "ylabel_style",
            {
                "color": "black",
                "fontsize": 5,
                # 'labelpad': 3.0
            },
        )

        # Set Y-axis label
        fig.text(
            0.041,
            0.55,
            param.axis_label[1],
            ha="center",
            va="center",
            rotation="vertical",
            fontsize=7,
            color="black",
        )

        # Set the map limits, in `target_crs`
        gax = cast(GeoAxes, ax)
        gax.set_extent(region.extent, crs=self.crs)

    def _add_grid_rect(
        self,
        ax: Axes,
        region: GeodeticRegion,
        param: GSPlotParameter,
    ) -> None:
        self._add_grid(ax, region, param, False)
        gax = cast(GeoAxes, ax)

        # Set X-axis label characteristics
        gax.set_xticks(region.xticks, crs=self.crs)
        gax.xaxis.set_major_formatter(
            LongitudeFormatter(dateline_direction_label=True)
        )

        # Set X-axis label
        ax.set_xlabel(
            param.axis_label[0],
            color="black",
            fontsize=6.0,
            labelpad=3.0,
        )

        # Set Y-axis label characteristics
        ax.set_yticks(region.yticks, crs=self.crs)
        ax.yaxis.set_major_formatter(LatitudeFormatter())

        # Set Y-axis label
        ax.set_ylabel(
            param.axis_label[1],
            color="black",
            fontsize=6.0,
            labelpad=3.0,
        )

        # Set the map limits, in `target_crs`
        gax.set_extent(region.extent, crs=self.crs)

    def _add_grid(
        self,
        ax: Axes,
        region: GeodeticRegion,
        param: GSPlotParameter,
        centered: bool,
    ) -> Gridliner:
        gax = cast(GeoAxes, ax)

        # Add gridlines
        gl = cast(
            Gridliner,
            gax.gridlines(
                xlocs=region.xticks,
                ylocs=region.yticks,
                linewidth=0.25,
                linestyle="--",
                color="red",
                alpha=0.6,
                draw_labels=centered,
            ),
        )

        # Set axis ticks characteristics
        left, right, bottom, top = param.axis_tick_draw
        labelleft, labelright, labelbottom, labeltop = param.axis_tick_label

        gax.tick_params(
            left=left,
            right=right,
            bottom=bottom,
            top=top,
            labelleft=labelleft,
            labelright=labelright,
            labelbottom=labelbottom,
            labeltop=labeltop,
            length=0.0,
            width=0.05,
            labelsize=4.5,
            labelcolor="black",
        )

        # Configure the gridline labels
        if centered:
            setattr(gl, "top_labels", labeltop)
            setattr(gl, "right_labels", labelright)
            setattr(gl, "bottom_labels", labelbottom)
            setattr(gl, "left_labels", labelleft)

        return gl

    def _add_title(
        self,
        ax: Axes,
        param: GSPlotParameter,
    ) -> None:
        if not param.title:
            return

        # Set the title
        title = param.title

        scale = self.scale

        if isinstance(title, str):
            plt.title(title, fontsize=scale.pt(param.title_size))
            return

        if len(title) < 2 or len(title) > 3:
            raise ValueError("Invalid title configuration")

        location: tuple[LocationType, ...] = (
            ("left", "right")
            if len(title) == 2
            else ("left", "center", "right")
        )

        for caption, loc in zip(title, location):
            if caption:
                ax.set_title(
                    caption, fontsize=scale.pt(param.title_size), loc=loc
                )

    def _add_watermark(self, fig: Figure) -> None:
        fig.text(
            self.watermark_loc[0],
            self.watermark_loc[1],
            "Generated by GOES-DL",
            horizontalalignment="right",
            verticalalignment="bottom",
            fontsize=4.0,
            color="gray",
            alpha=0.5,
            zorder=1000,
            transform=fig.transFigure,
        )

    def _plot_data(
        self,
        ax: Axes,
        data: SatImageData,
        param: GSPlotParameter,
    ) -> QuadMesh:
        mesh: Any = ax.pcolormesh(  # Any: avoid pylance/mypy conflict
            data.grid.lon,
            data.grid.lat,
            data.image,
            shading=cast(ShaddingType, param.shadding),
            cmap=self.enhancement.cmap,
            norm=self.enhancement.cnorm,
            transform=data.grid.crs,
        )

        return cast(QuadMesh, mesh)

    def _setup_boxes(self, param: GSPlotParameter) -> None:
        self.fig_dpi = param.fig_dpi
        self.scale = Size(self.fig_dpi)
        self.fig_size = (
            param.fig_width_px / self.fig_dpi,
            param.fig_height_px / self.fig_dpi,
        )
        self.axes_box = (
            param.left_margin_px / param.fig_width_px,
            param.bottom_margin_px / param.fig_height_px,
            (param.fig_width_px - param.left_margin_px - param.right_margin_px)
            / param.fig_width_px,
            (
                param.fig_height_px
                - param.top_margin_px
                - param.bottom_margin_px
            )
            / param.fig_height_px,
        )
        self.cbar_box = (
            param.left_margin_px / param.fig_width_px,
            param.cbar_bottom_px / param.fig_height_px,
            (param.fig_width_px - param.left_margin_px - param.right_margin_px)
            / param.fig_width_px,
            param.cbar_height_px / param.fig_height_px,
        )
        self.watermark_loc = (
            (param.fig_width_px - param.watermark_bottom_px)
            / param.fig_width_px,
            param.watermark_bottom_px / param.fig_height_px,
        )
