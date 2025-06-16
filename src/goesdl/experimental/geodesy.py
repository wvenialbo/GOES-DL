import math

import cartopy.crs as ccrs
from cartopy.crs import AzimuthalEquidistant, Globe, PlateCarree, Projection
from pyproj import CRS, Geod, Transformer

WGS84_SEMIMAJOR_AXIS = ccrs.WGS84_SEMIMAJOR_AXIS


def get_ellipsoid_name(projection: Projection) -> str:
    if not projection.globe and not projection.ellipsoid:
        return "WGS84"

    if not isinstance(projection.globe, Globe):
        raise TypeError("Unknown Globe type")

    if projection.globe.ellipse:
        return projection.globe.ellipse

    if projection.ellipsoid:
        return projection.ellipsoid.name

    if projection.globe.datum:
        crs = CRS(proj="utm", zone=10, datum=projection.globe.datum)
    else:
        return "WGS84"

    return crs.ellipsoid.name if crs.ellipsoid else "WGS84"


def get_semimajor_axis(projection: Projection) -> float:
    # Get the ellipsoid semimajor axis in metres
    if not projection.globe:
        return WGS84_SEMIMAJOR_AXIS

    if not isinstance(projection.globe, Globe):
        raise TypeError("Unknown Globe type")

    if projection.globe.semimajor_axis:
        return projection.globe.semimajor_axis

    if ellipsoid := projection.ellipsoid:
        return ellipsoid.semi_major_metre

    if projection.globe.ellipse:
        crs = CRS(proj="utm", zone=10, ellps=projection.globe.ellipse)
    elif projection.globe.datum:
        crs = CRS(proj="utm", zone=10, datum=projection.globe.datum)
    else:
        return WGS84_SEMIMAJOR_AXIS

    return (
        crs.ellipsoid.semi_major_metre
        if crs.ellipsoid
        else WGS84_SEMIMAJOR_AXIS
    )


def get_extent_metre(
    extent_deg: tuple[float, float], projection: Projection
) -> tuple[float, float]:
    # Get the ellipsoid semimajor axis in metres
    semimajor_axis = get_semimajor_axis(projection)

    # Compute the extent size in metres
    deg_to_m = math.pi * semimajor_axis / 180.0
    width_deg, height_deg = extent_deg
    width_m = width_deg * deg_to_m
    height_m = height_deg * deg_to_m

    return width_m, height_m


def get_centered_domain(
    extent_deg: tuple[float, float],
    centre_deg: tuple[float, float],
    target: Projection | None = None,
    source: Projection | None = None,
) -> tuple[
    tuple[float, float, float, float],
    tuple[float, float, float, float],
]:
    lon, lat = centre_deg

    if not target:
        target = AzimuthalEquidistant(
            central_longitude=lon, central_latitude=lat
        )

    if not source:
        source = PlateCarree()

    intermediate = AzimuthalEquidistant(
        central_longitude=lon, central_latitude=lat, globe=target.globe
    )

    width_m, height_m = get_extent_metre(extent_deg, target)

    half_width_m = 0.5 * width_m
    half_height_m = 0.5 * height_m

    p_int = [
        (-half_width_m, -half_height_m),
        (-half_width_m, 0.0),
        (-half_width_m, half_height_m),
        (0.0, -half_height_m),
        (0.0, half_height_m),
        (half_width_m, -half_height_m),
        (half_width_m, 0.0),
        (half_width_m, half_height_m),
    ]

    x_int, y_int = zip(*p_int)

    transform_dst = Transformer.from_crs(intermediate, target, always_xy=True)
    x_dst, y_dst = transform_dst.transform(x_int, y_int)

    x_min_dst, x_max_dst = min(x_dst), max(x_dst)
    y_min_dst, y_max_dst = min(y_dst), max(y_dst)

    x_mid_dst = 0.5 * (x_min_dst + x_max_dst)
    y_mid_dst = 0.5 * (y_min_dst + y_max_dst)

    p_dst = [
        (x_min_dst, y_min_dst),
        (x_min_dst, y_mid_dst),
        (x_min_dst, y_max_dst),
        (x_mid_dst, y_min_dst),
        (x_mid_dst, y_max_dst),
        (x_max_dst, y_min_dst),
        (x_max_dst, y_mid_dst),
        (x_max_dst, y_max_dst),
    ]

    x_dst, y_dst = zip(*p_dst)

    transform_src = Transformer.from_crs(target, source, always_xy=True)
    x_src, y_src = transform_src.transform(x_dst, y_dst)

    x_min_src, x_max_src = min(x_src), max(x_src)
    y_min_src, y_max_src = min(y_src), max(y_src)

    return (
        (x_min_src, x_max_src, y_min_src, y_max_src),
        (x_min_dst, x_max_dst, y_min_dst, y_max_dst),
    )


def get_output_image_dimensions(
    extent_deg: tuple[float, float],
    centre_deg: tuple[float, float],
    data_resolution: float,  # Resolución de los datos, e.g., 0.04 (deg) o 2000 (m)
    data_resolution_unit: str,  # "deg" o "m"
    target: Projection | None = None,
    source: Projection | None = None,
) -> tuple[int, int]:
    """
    Calcula las dimensiones en píxeles de la imagen de salida para una proyección de destino arbitraria,
    manteniendo la relación de aspecto y respetando la resolución de los datos originales.

    Args:
        extent_deg: Tupla (ancho, alto) de la extensión de la región en grados de circunferencia máxima.
        centre_deg: Tupla (lon, lat) de la coordenada geográfica central.
        data_resolution: La resolución numérica de los datos originales (e.g., 0.04 para grados, 2000 para metros).
        data_resolution_unit: La unidad de la resolución de los datos originales ("deg" o "m").
        target: La proyección de destino (cartopy.crs.Projection). Si es None, usa AzimuthalEquidistant.
        source: La proyección de origen (cartopy.crs.Projection). Si es None, usa PlateCarree.

    Returns:
        Tupla (width_px, height_px) con las dimensiones de la imagen en píxeles.
    """
    lon, lat = centre_deg

    if not target:
        target = AzimuthalEquidistant(
            central_longitude=lon, central_latitude=lat
        )
    if not source:
        source = PlateCarree()

    # Obtener los límites del rectángulo delimitador en la proyección de destino
    _, target_bounds = get_centered_domain(
        extent_deg, centre_deg, target, source
    )
    x_min_dst, x_max_dst, y_min_dst, y_max_dst = target_bounds

    # Ancho y alto del dominio en la proyección de destino (en sus unidades, e.g., metros)
    width_dst = x_max_dst - x_min_dst
    height_dst = y_max_dst - y_min_dst
    print(width_dst, height_dst)

    # 1. Determinar la resolución efectiva de los datos en la proyección de destino
    #    Evaluamos la resolución en el centro de la región para una aproximación.
    transformer_target = Transformer.from_crs(source, target, always_xy=True)
    geod = Geod(
        ellps=(
            target.proj4_params["ellps"] if target.proj4_params else "WGS84"
        )
    )

    # Punto central en grados
    center_lon, center_lat = centre_deg

    effective_pixel_size_target = 0.0  # Tamaño de un píxel de los datos originales en la proyección de destino (en metros)

    if data_resolution_unit == "deg":
        # Para datos con resolución en grados (ej. GridSat-GOES: 0.04 deg)
        # Necesitamos saber cómo se "estira" o "comprime" un grado en la proyección de destino.
        # Hacemos esto midiendo el tamaño de un pequeño desplazamiento en la proyección de destino
        # y dividiéndolo por la distancia real de ese desplazamiento.

        # Proyectar el punto central
        x_c_dst, y_c_dst = transformer_target.transform(center_lon, center_lat)

        # Proyectar un punto ligeramente al este del centro (0.001 grados al este)
        lon_plus_small_deg = center_lon + 0.001
        x_e_dst, y_e_dst = transformer_target.transform(
            lon_plus_small_deg, center_lat
        )

        # Proyectar un punto ligeramente al norte del centro (0.001 grados al norte)
        lat_plus_small_deg = center_lat + 0.001
        x_n_dst, y_n_dst = transformer_target.transform(
            center_lon, lat_plus_small_deg
        )

        # Distancia proyectada de ese pequeño desplazamiento en la proyección de destino
        dist_proj_x = math.sqrt(
            (x_e_dst - x_c_dst) ** 2 + (y_e_dst - y_c_dst) ** 2
        )
        dist_proj_y = math.sqrt(
            (x_n_dst - x_c_dst) ** 2 + (y_n_dst - y_c_dst) ** 2
        )

        # Distancia real en metros de ese pequeño desplazamiento angular (usando geodesic)
        _, _, actual_dist_x_m = geod.inv(
            center_lon, center_lat, lon_plus_small_deg, center_lat
        )
        _, _, actual_dist_y_m = geod.inv(
            center_lon, center_lat, center_lon, lat_plus_small_deg
        )

        # Escala local de la proyección en el centro (unidad_destino / metro_geodesico)
        # Esto indica cuántos metros en la proyección de destino corresponden a un metro real.
        scale_factor_x = (
            dist_proj_x / actual_dist_x_m if actual_dist_x_m > 0 else 1.0
        )
        scale_factor_y = (
            dist_proj_y / actual_dist_y_m if actual_dist_y_m > 0 else 1.0
        )

        # La resolución de los datos (e.g., 0.04 grados) convertida a metros geodésicos
        _, _, data_res_m_x = geod.inv(
            center_lon, center_lat, center_lon + data_resolution, center_lat
        )
        _, _, data_res_m_y = geod.inv(
            center_lon, center_lat, center_lon, center_lat + data_resolution
        )

        # La resolución efectiva en la proyección de destino (metros_en_destino / píxel_original)
        # Tomamos la resolución más fina para no perder detalle en ninguna dirección.
        effective_pixel_size_target = min(
            data_res_m_x * scale_factor_x, data_res_m_y * scale_factor_y
        )

    elif data_resolution_unit == "m":
        # Para datos con resolución en metros (ej. GOES-R: 2km)
        # La resolución ya está en metros reales. Necesitamos saber cómo se proyecta esa distancia en la proyección de destino.

        # Proyectar el punto central
        x_c_dst, y_c_dst = transformer_target.transform(center_lon, center_lat)

        # Proyectar un punto a 'data_resolution' metros al este del centro
        # pyproj.Geod.fwd(lon, lat, azimuth, distance) -> (lon2, lat2, back_azimuth)
        lon_e, lat_e, _ = geod.fwd(
            center_lon, center_lat, 90, data_resolution
        )  # 90 grados es este
        x_e_dst, y_e_dst = transformer_target.transform(lon_e, lat_e)

        # Proyectar un punto a 'data_resolution' metros al norte del centro
        lon_n, lat_n, _ = geod.fwd(
            center_lon, center_lat, 0, data_resolution
        )  # 0 grados es norte
        x_n_dst, y_n_dst = transformer_target.transform(lon_n, lat_n)

        # Distancia entre el centro proyectado y el punto "resolución" proyectado
        # Esto nos da directamente el tamaño que ocupa un "píxel" de datos en la proyección de destino
        effective_pixel_size_target_x = math.sqrt(
            (x_e_dst - x_c_dst) ** 2 + (y_e_dst - y_c_dst) ** 2
        )
        effective_pixel_size_target_y = math.sqrt(
            (x_n_dst - x_c_dst) ** 2 + (y_n_dst - y_c_dst) ** 2
        )

        # Tomamos la resolución más fina para no perder detalle
        effective_pixel_size_target = min(
            effective_pixel_size_target_x, effective_pixel_size_target_y
        )

    else:
        raise ValueError("data_resolution_unit must be 'deg' or 'm'")

    # Asegurarse de que effective_pixel_size_target no sea cero o muy pequeño
    effective_pixel_size_target = max(effective_pixel_size_target, 0.1)
    print(effective_pixel_size_target)

    # 2. Calcular las dimensiones de la imagen en píxeles
    #    Dividimos las dimensiones del dominio proyectado por la resolución efectiva.
    num_pixels_width_float = width_dst / effective_pixel_size_target
    num_pixels_height_float = height_dst / effective_pixel_size_target

    # Para mantener la relación de aspecto y tener números enteros de píxeles:
    # Elegimos la dimensión más larga basada en la resolución calculada,
    # y la otra dimensión se escala para mantener la relación de aspecto
    # del dominio.

    if num_pixels_width_float > num_pixels_height_float:
        output_width_px = int(math.ceil(num_pixels_width_float))
        output_height_px = int(
            math.ceil(output_width_px * (height_dst / width_dst))
        )
    else:
        output_height_px = int(math.ceil(num_pixels_height_float))
        output_width_px = int(
            math.ceil(output_height_px * (width_dst / height_dst))
        )

    # Asegurarse de que las dimensiones sean al menos 1 píxel
    output_width_px = max(1, output_width_px)
    output_height_px = max(1, output_height_px)

    return output_width_px, output_height_px
