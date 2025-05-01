class Rect:

    dpi: int
    figsize: tuple[float, float]

    def __init__(self, width: int, height: int, dpi: int) -> None:
        self.figsize = self._calculate_figsize((width, height), dpi)
        self.dpi = dpi

    def __call__(
        self, left: int, bottom: int, width: int, height: int
    ) -> tuple[float, float, float, float]:
        return self._calculate_rectangle((left, bottom, width, height))

    def corners(self, left: int, bottom: int, right: int, top: int) -> None:
        margins = self._calculate_corners((left, bottom, right, top))
        self.rect = self._get_rectangle(margins)

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
