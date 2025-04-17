import numpy as np


def interpolate_value(x, xp, fp):
    """
    Realiza una interpolación lineal utilizando np.interp y, si el punto
    está fuera del dominio, realiza una extrapolación lineal.
    """
    if x < xp[0]:
        # Extrapolación lineal a la izquierda
        slope = (fp[1] - fp[0]) / (xp[1] - xp[0])
        return fp[0] + slope * (x - xp[0])

    if x > xp[-1]:
        # Extrapolación lineal a la derecha
        slope = (fp[-1] - fp[-2]) / (xp[-1] - xp[-2])
        return fp[-1] + slope * (x - xp[-1])

    # Interpolación dentro del dominio
    return np.interp(x, xp, fp)


def interpolate_coordinates(t, timestamps, longitudes, latitudes):
    """Interpola o extrapola las coordenadas para un timestamp dado."""
    # Convertir a arrays NumPy si aún no lo están
    timestamps = np.array(timestamps)
    latitudes = np.array(latitudes)
    longitudes = np.array(longitudes)

    # Interpolar o extrapolar
    lon_interp = interpolate_value(t, timestamps, longitudes)
    lat_interp = interpolate_value(t, timestamps, latitudes)

    return lon_interp, lat_interp
