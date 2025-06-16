from matplotlib.spines import Spine

BoxType = tuple[float, float, float, float]
MarginType = tuple[float, float, float, float]
PointType = tuple[float, float]
SizeType = tuple[float, float]


class Rect:

    dpi: int
    figsize: tuple[float, float]
    rectangle: tuple[float, float, float, float]

    def __init__(self, width: int, height: int, dpi: int) -> None:
        self.figsize = self._calculate_figsize((width, height), dpi)
        self.dpi = dpi

    def __call__(
        self, left: int, bottom: int, width: int, height: int
    ) -> tuple[float, float, float, float]:
        return self._calculate_rectangle((left, bottom, width, height))

    def corners(self, left: int, bottom: int, right: int, top: int) -> None:
        margins = self._calculate_corners((left, bottom, right, top))
        self.rectangle = self._get_rectangle(margins)

    def margins(
        self, left: int, bottom: int, right: int, top: int
    ) -> tuple[float, float, float, float]:
        margins = self._calculate_margins((left, bottom, right, top))
        return self._get_rectangle(margins)

    def pos(self, x: float, y: float) -> tuple[float, float]:
        return self.x_pos(x), self.y_pos(y)

    def x_pos(self, x: float) -> float:
        pos_in = x / self.dpi
        return pos_in / self.figsize[0]

    def y_pos(self, x: float) -> float:
        pos_in = x / self.dpi
        return pos_in / self.figsize[1]

    def _calculate_corners(
        self, corners: tuple[int, int, int, int]
    ) -> tuple[float, float, float, float]:
        # figure dimensions in inches
        width, height = self.figsize

        # rectangle corners in inches
        left, bottom, right, top = (size / self.dpi for size in corners)

        # rectangle corners in relative units
        left, right = (size / width for size in (left, right))
        bottom, top = (size / height for size in (bottom, top))

        # rectangle margins in relative units
        return left, bottom, 1.0 - right, 1.0 - top

    @staticmethod
    def _calculate_figsize(
        figsize: tuple[int, int], dpi: int
    ) -> tuple[float, float]:
        # figure dimensions in pixels per side
        width_px, height_px = figsize

        # figure dimensions in inches
        width_in, height_in = (size / dpi for size in (width_px, height_px))

        return width_in, height_in

    def _calculate_margins(
        self, margins: tuple[int, int, int, int]
    ) -> tuple[float, float, float, float]:
        # figure dimensions in inches
        width, height = self.figsize

        # rectangle margins in inches
        left, bottom, right, top = (size / self.dpi for size in margins)

        # rectangle margins in relative units
        left, right = (size / width for size in (left, right))
        bottom, top = (size / height for size in (bottom, top))

        return left, bottom, right, top

    def _calculate_rectangle(
        self, rect: tuple[int, int, int, int]
    ) -> tuple[float, float, float, float]:
        # figure dimensions in inches
        width, height = self.figsize

        # rectangle parameters in inches (from pixels per side)
        left, bottom, width, height = (size / self.dpi for size in rect)

        # rectangle parameters in relative units
        left, width = (size / width for size in (left, width))
        bottom, height = (size / height for size in (bottom, height))

        return left, bottom, width, height

    @staticmethod
    def _get_rectangle(
        margins: tuple[float, float, float, float],
    ) -> tuple[float, float, float, float]:
        # rectangle margins in relative units
        left, bottom, right, top = margins

        # rectangle dimensions in relative units
        width = 1.0 - right - left
        height = 1.0 - top - bottom

        # rectangle parameters in relative units
        return left, bottom, width, height


class Size:

    dpr: float = 100
    ppi: float = 72

    pt_scale: float
    px_scale: float

    def __init__(self, dpi: int) -> None:
        self.pt_scale = self.dpr / dpi
        self.px_scale = self.dpr * self.ppi / dpi**2

    def pt(self, x: float) -> float:
        return x * self.pt_scale

    def px(self, x: float) -> float:
        return x * self.px_scale


class MarginGeometry:

    left: float
    bottom: float
    rigth: float
    top: float

    def __init__(
        self, left: float, bottom: float, rigth: float, top: float
    ) -> None:
        self.left = left
        self.bottom = bottom
        self.rigth = rigth
        self.top = top

    @property
    def left_bottom(self) -> PointType:
        return self.left, self.bottom

    @property
    def margins(self) -> MarginType:
        return self.left, self.bottom, self.rigth, self.top

    @property
    def rigth_top(self) -> PointType:
        return self.rigth, self.top


class SizeGeometry:

    width: float
    height: float

    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def __add__(self, margin: MarginGeometry) -> "SizeGeometry":
        width = self.width + margin.left + margin.rigth
        height = self.height + margin.bottom + margin.top

        return SizeGeometry(width, height)

    def __sub__(self, margin: MarginGeometry) -> "SizeGeometry":
        width = self.width - margin.left - margin.rigth
        height = self.height - margin.bottom - margin.top

        return SizeGeometry(width, height)

    def __truediv__(self, dpi: float) -> "SizeGeometry":
        return SizeGeometry(self.width / dpi, self.height / dpi)

    @property
    def size(self) -> SizeType:
        return self.width, self.height


class BoxGeometry:

    left: float
    bottom: float
    width: float
    height: float

    def __init__(
        self, left: float, bottom: float, width: float, height: float
    ) -> None:
        self.left = left
        self.bottom = bottom
        self.width = width
        self.height = height

    def __truediv__(self, figsize: SizeGeometry) -> "BoxGeometry":
        left = self.left / figsize.width
        bottom = self.bottom / figsize.height
        width = self.width / figsize.width
        height = self.height / figsize.height

        return BoxGeometry(left, bottom, width, height)

    @property
    def box(self) -> BoxType:
        return self.left, self.bottom, self.width, self.height

    @property
    def origin(self) -> PointType:
        return self.left, self.bottom

    @property
    def size(self) -> SizeType:
        return self.width, self.height


class FigureGeometry:

    dpi: int
    margin: MarginGeometry
    size: SizeGeometry

    def __init__(
        self,
        size: SizeGeometry | SizeType,
        margin: MarginGeometry | MarginType,
        dpi: int = 100,
    ) -> None:
        if not isinstance(margin, MarginGeometry):
            margin = MarginGeometry(*margin)

        if not isinstance(size, SizeGeometry):
            size = SizeGeometry(*size)

        self.dpi = dpi
        self.margin = margin
        self.size = size

    @classmethod
    def from_plot_size(
        cls, size: SizeGeometry | SizeType, margin: MarginGeometry | MarginType
    ) -> "FigureGeometry":
        if not isinstance(margin, MarginGeometry):
            margin = MarginGeometry(*margin)

        if not isinstance(size, SizeGeometry):
            size = SizeGeometry(*size)

        return cls(size + margin, margin)

    @classmethod
    def from_plot_area(
        cls, size: SizeGeometry | SizeType, rect: BoxGeometry | BoxType
    ) -> "FigureGeometry":
        if not isinstance(rect, BoxGeometry):
            rect = BoxGeometry(*rect)

        if not isinstance(size, SizeGeometry):
            size = SizeGeometry(*size)

        left, bottom = rect.origin
        right = size.width - rect.width - left
        top = size.height - rect.height - bottom

        margin = MarginGeometry(left, bottom, right, top)

        return cls(size, margin)

    def get_plot_area(
        self, margin: MarginGeometry | MarginType
    ) -> BoxGeometry:
        if not isinstance(margin, MarginGeometry):
            margin = MarginGeometry(*margin)

        plot_size = self.size - margin

        # Relative units
        return BoxGeometry(*margin.left_bottom, *plot_size.size)

    @property
    def box(self) -> BoxType:
        plot_area = self.get_plot_area(self.margin) / self.size
        return plot_area.box

    @property
    def figsize(self) -> SizeType:
        # Return inches
        figsize = self.size / self.dpi
        return figsize.size

    @property
    def scale(self) -> Size:
        return Size(self.dpi)


class GSPlotParameter:

    title: str | tuple[str, str] | tuple[str, str, str] = ""
    title_size: float = 6.5

    # shading;
    #   - center : lon.shape == image.shape -> "nearest" | "gouraud"
    #   - corners: lon.shape != image.shape -> "flat"
    shadding: str = "gouraud"

    nat_earth_scale: str = "10m"
    nat_earth_features: list[str] = [
        "cultural:admin_1_states_provinces",
        "cultural:admin_0_countries",
    ]
    nat_earth_style: list[tuple[float, str, str]] = [
        (0.25, "gray", "none"),
        (0.25, "black", "none"),
    ]

    cbar_label: str = ""
    cbar_extend = "both"
    cbar_orientation: str = "horizontal"
    cbar_linewidth: float = 0.4

    cbar_labelsize: float = 5.0
    cbar_labelcolor: str = "black"
    cbar_labelweight: str = "normal"

    cbar_tick_labelsize: float = 4.0
    cbar_tick_labelcolor: str = "black"
    cbar_tick_direction: str = "out"
    cbar_tick_pad: float = 1.0

    cbar_tick_major_length: float = 2.0
    cbar_tick_major_width: float = 0.5

    cbar_tick_minor_step: int = 5
    cbar_tick_minor_length: float = 1.5
    cbar_tick_minor_width: float = 0.4

    axis_label: tuple[str, str] = "", ""
    axis_tick_draw: tuple[bool, bool, bool, bool] = True, False, True, False
    axis_tick_label: tuple[bool, bool, bool, bool] = True, False, True, False

    axis_tick_length: float = 0.0
    axis_tick_width: float = 0.05

    fig_width_px = 712
    fig_height_px = 800
    top_margin_px = 50
    bottom_margin_px = 150
    left_margin_px = 88
    right_margin_px = 24
    cbar_bottom_px = 64
    cbar_height_px = 16
    watermark_bottom_px = 7
    fig_dpi = 100

    def __init__(
        self,
        title: str | tuple[str, str] = "",
        axis_label: tuple[str, str] = ("", ""),
        cbar_label: str = "",
    ) -> None:
        self.title = title
        self.axis_label = axis_label
        self.cbar_label = cbar_label


def set_outline(outline: Spine, linewidth: float) -> None:
    outline.set_linewidth(linewidth)
    outline.set_color("black")
    outline.set_alpha(1.0)
