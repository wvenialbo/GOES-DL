from collections.abc import Sequence
from pathlib import Path
from typing import cast

from matplotlib import pyplot as plt
from matplotlib.colors import Colormap, Normalize
from numpy import ndarray
from numpy.typing import ArrayLike

from ..utils.array import ArrayFloat64


class PlottingParameters:

    @staticmethod
    def _validate_dpi(value: int) -> None:
        """
        Validate a DPI value.

        Parameters
        ----------
        value : int
            Integer representing the DPI.
        """
        if value <= 0:
            raise ValueError("`dpi` must be greater than 0")
        if value > 1000:
            raise ValueError("`dpi` must be less than or equal to 1000")

    @staticmethod
    def _validate_margin(value: int, which: str) -> None:
        """
        Validate a margin value.

        Parameters
        ----------
        value : int
            Integer representing the margin in pixels.
        which : str
            String representing the margin type.
        """
        if value < 0:
            raise ValueError(f"`{which}` must be greater than or equal to 0")

    @classmethod
    def _validate_margins(
        cls, left: int, bottom: int, right: int, top: int
    ) -> None:
        cls._validate_margin(left, "left")
        cls._validate_margin(bottom, "bottom")
        cls._validate_margin(right, "right")
        cls._validate_margin(top, "top")

    @staticmethod
    def _validate_size(value: int, which: str) -> None:
        """
        Validate a size value.

        Parameters
        ----------
        value : int
            Integer representing the size in pixels.
        which : str
            String representing the size type.
        """
        if value <= 0:
            raise ValueError(f"`{which}` must be greater than 0")

    @classmethod
    def _validate_sizes(cls, width: int, height: int) -> None:
        cls._validate_size(width, "width")
        cls._validate_size(height, "height")


class PlotParameters(PlottingParameters):

    padding: tuple[int, int, int, int] = (0, 0, 0, 0)
    shape: tuple[int, int] = (0, 0)

    title: str = ""
    xlabel: str = ""
    ylabel: str = ""

    def __init__(self, title: str = "") -> None:
        self.padding = (0, 0, 0, 0)
        self.shape = (0, 0)

        self.title = title
        self.xlabel = ""
        self.ylabel = ""

    def set_paddings(self, paddings: tuple[int, int, int, int]) -> None:
        """
        Set the paddings of the plot.

        Parameters
        ----------
        paddings : tuple[int, int, int, int]
            Tuple of integers:
                - the first element is the left margin
                - the second element is the bottom margin
                - the third element is the right margin
                - the fourth element is the top margin
        """
        self.set_padding(*paddings)

    def set_padding(
        self,
        left: int,
        bottom: int | None = None,
        right: int | None = None,
        top: int | None = None,
    ) -> None:
        """
        Set the margins of the plot.

        Parameters
        ----------
        left : int
            Integer representing the left margin in pixels.
        bottom : int
            Integer representing the bottom margin in pixels.
        right : int
            Integer representing the right margin in pixels.
        top : int
            Integer representing the top margin in pixels.
        """
        if bottom is None:
            bottom = left
        if right is None:
            right = left
        if top is None:
            top = bottom

        self._validate_margins(left, bottom, right, top)

        self.padding = left, bottom, right, top

    def set_shape(self, shape: tuple[int, int]) -> None:
        """
        Set the shape of the plot.

        Parameters
        ----------
        shape : tuple[int, int]
            Tuple of integers:
                - the first element is the number of rows
                - the second element is the number of columns
        """
        self.set_size(shape[1], shape[0])

    def set_sizes(self, sizes: tuple[int, int]) -> None:
        """
        Set the sizes of the plot.

        Parameters
        ----------
        sizes : tuple[int, int]
            Tuple of integers:
                - the first element is the width
                - the second element is the height
        """
        self.set_size(*sizes)

    def set_size(self, width: int, height: int | None = None) -> None:
        """
        Set the size of the plot in pixels.

        Parameters
        ----------
        width : int
            Integer representing the width of the plot in pixels.
        height : int, optional
            Integer representing the height of the plot in pixels. If
            None, height is set to width.
        """
        height = width if height is None else height

        self._validate_sizes(width, height)

        self.shape = height, width

    def set_title(self, title: str) -> None:
        """
        Set the title of the plot.

        Parameters
        ----------
        title : str
            Title of the figure.
        """
        self.title = title

    @property
    def extent(self) -> tuple[int, int]:
        """
        Get the extent of the plot.

        Returns
        -------
        tuple[int, int]
            Tuple of integers:
                - the first element is the width
                - the second element is the height
        """
        width = self.size[0] + self.padding[0] + self.padding[2]
        height = self.size[1] + self.padding[1] + self.padding[3]
        return width, height

    @property
    def rectangle(self) -> tuple[int, int, int, int]:
        """
        Get the rectangle of the plot.

        Returns
        -------
        tuple[int, int, int, int]
            Tuple of ints:
                - the first element is the left margin
                - the second element is the bottom margin
                - the third element is the width
                - the fourth element is the height
        """
        left = self.padding[0]
        bottom = self.padding[1]
        width = self.size[0]
        height = self.size[1]
        return left, bottom, width, height

    @property
    def size(self) -> tuple[int, int]:
        """
        Get the size of the plot.

        Returns
        -------
        tuple[int, int]
            Tuple of integers:
                - the first element is the width
                - the second element is the height
        """
        return self.shape[1], self.shape[0]


class FigureParameters(PlottingParameters):
    """
    Class to handle figure parameters for plotting.
    """

    dpi: int = 100
    shape: tuple[int, int] = (0, 0)
    margins: tuple[int, int, int, int] = (0, 0, 0, 0)

    plots: list[PlotParameters] = []

    title: str = ""

    _update: bool = False

    def __init__(
        self,
        title: str = "",
        dpi: int = 100,
    ) -> None:
        self._validate_dpi(dpi)

        self.dpi = dpi
        self.shape = (0, 0)
        self.margins = (0, 0, 0, 0)

        self.plots = []

        self.title = title

        self._update = False

    def add_plot(self, title: str = "") -> PlotParameters:
        """
        Add a plot to the figure.

        Parameters
        ----------
        title : str
            Title of the plot.

        Returns
        -------
        PlotParameters
            Instance of PlotParameters.
        """
        plot = PlotParameters(title)
        self.append_plot(plot)
        return self.plots[-1]

    def append_plot(self, plot: PlotParameters) -> None:
        """
        Add a plot to the figure.

        Parameters
        ----------
        plot : PlotParameters
            Instance of PlotParameters.
        """
        self.plots.append(plot)
        self._update = True

    def set_margins(self, margins: tuple[int, int, int, int]) -> None:
        """
        Set the margins of the figure.

        Parameters
        ----------
        margins : tuple[int, int, int, int]
            Tuple of integers:
                - the first element is the left margin
                - the second element is the bottom margin
                - the third element is the right margin
                - the fourth element is the top margin
        """
        self.set_margin(*margins)

    def set_margin(
        self,
        left: int,
        bottom: int | None = None,
        right: int | None = None,
        top: int | None = None,
    ) -> None:
        """
        Set the margins of the figure.

        Parameters
        ----------
        left : int
            Integer representing the left margin in pixels.
        bottom : int
            Integer representing the bottom margin in pixels.
        right : int
            Integer representing the right margin in pixels.
        top : int
            Integer representing the top margin in pixels.
        """
        if bottom is None:
            bottom = left
        if right is None:
            right = left
        if top is None:
            top = bottom

        self._validate_margins(left, bottom, right, top)

        self.padding = left, bottom, right, top

    def set_title(self, title: str) -> None:
        """
        Set the title of the figure.

        Parameters
        ----------
        title : str
            Title of the figure.
        """
        self.title = title

    def _update_shape(self) -> None:
        """
        Update the shape of the figure based on the plots.
        """
        if not self._update:
            return

        self._update = False

        for plot in self.plots:
            extent = plot.extent

            width = extent[0] + self.margins[0] + self.margins[2]
            height = extent[1] + self.margins[1] + self.margins[3]

            self.shape = (
                max(self.size[0], width),
                max(self.size[1], height),
            )

    @property
    def figsize(self) -> tuple[float, float]:
        """
        Get the figure size in inches.

        Returns
        -------
        tuple[float, float]
            Tuple of floats:
                - the first element is the width in inches
                - the second element is the height in inches
        """
        self._update_shape()
        return self.shape[1] / self.dpi, self.shape[0] / self.dpi

    @property
    def size(self) -> tuple[int, int]:
        """
        Get the size of the plot.

        Returns
        -------
        tuple[int, int]
            Tuple of integers:
                - the first element is the width
                - the second element is the height
        """
        self._update_shape()
        return self.shape[1], self.shape[0]


class Image:

    parameters: FigureParameters

    def __init__(self, parameters: FigureParameters) -> None:
        self.parameters = parameters

    def draw(
        self,
        array: ArrayLike | Sequence[ArrayLike],
        cmap: Colormap | None = None,
        norm: Normalize | None = None,
    ) -> None:
        """
        Draw the images.

        Parameters
        ----------
        array : ArrayLike | Sequence[ArrayLike]
            Array or sequence of arrays representing images.
        """
        if not isinstance(array, Sequence):
            array = [array]

        if not array:
            raise ValueError("`array` must not be empty")

        if len(array) != len(self.parameters.plots):
            raise ValueError(
                f"Number of plots ({len(self.parameters.plots)}) "
                f"must match number of arrays ({len(array)})"
            )

        plt.figure(figsize=self.parameters.figsize, dpi=self.parameters.dpi)

        for plot, matrix in zip(self.parameters.plots, array):
            if not isinstance(matrix, ndarray):
                raise ValueError(
                    f"Array {matrix} must be an instance of ArrayLike"
                )

            matrix = cast(ArrayFloat64, matrix)

            if len(matrix.shape) != 2:
                raise ValueError(
                    f"Array {matrix} must be a 2D array, but got "
                    f"{len(matrix.shape)}D"
                )

            self._draw_image(plot, matrix, cmap, norm)

    def finalize(self, show: bool = False) -> None:
        if show:
            plt.show()
        else:
            plt.close()

    def save(self, path: str | Path, overwrite: bool = False) -> None:
        """
        Save the figure to a file.

        Parameters
        ----------
        path : str | Path
            Path to save the figure.
        overwrite : bool
            If True, overwrite the file if it exists.
        """
        path = self._validate_output_path(path)

        if path.exists() and not overwrite:
            raise ValueError(
                f"File '{path}' already exists, "
                "use `overwrite=True` to overwrite"
            )

        figure = plt.gcf()

        figure.savefig(
            path,
            dpi=self.parameters.dpi,
            bbox_inches=None,
            pad_inches=0,
            facecolor="none",
            transparent=True,
        )

    def _draw_image(
        self,
        plot: PlotParameters,
        matrix: ArrayLike,
        cmap: Colormap | None,
        norm: Normalize | None,
    ) -> None:
        """
        Draw the image.

        Parameters
        ----------
        figure : Figure
            Instance of Figure.
        plot : PlotParameters
            Instance of PlotParameters.
        matrix : ArrayLike
            Array representing the image.
        """
        fig_width, fig_height = self.parameters.size
        plot_left, plot_bottom, plot_width, plot_height = plot.rectangle
        left = plot_left / fig_width
        bottom = plot_bottom / fig_height
        width = plot_width / fig_width
        height = plot_height / fig_height

        figure = plt.gcf()

        axis = figure.add_axes((left, bottom, width, height), frame_on=False)

        axis.set_axis_off()

        axis.imshow(
            matrix,
            cmap=cmap,
            norm=norm,
            aspect="auto",
            origin="upper",
            interpolation="nearest",
        )

    @staticmethod
    def _validate_output_path(path: str | Path) -> Path:
        if not path:
            raise ValueError("`path` is empty")
        path = Path(path)
        if path == Path():
            raise ValueError("`path` is undefined")
        if path.exists() and not path.is_file():
            raise ValueError(f"Path '{path}' is not a file")
        return path
