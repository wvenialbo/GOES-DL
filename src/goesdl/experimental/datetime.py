from datetime import datetime


def iso_to_timestamp(iso_strings):
    """Convierte una lista de cadenas ISO a una lista de timestamps en segundos desde la época."""
    # Convertir fechas ISO a timestamps en segundos desde la época
    return [
        datetime.fromisoformat(iso_string).timestamp()
        for iso_string in iso_strings
    ]
