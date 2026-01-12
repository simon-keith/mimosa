"""Sentinel-2 band metadata and helper functions."""

SENTINEL2_BANDS: dict[str, dict[str, str | int]] = {
    "B01": {"name": "Coastal aerosol", "resolution": 60, "wavelength": "443nm"},
    "B02": {"name": "Blue", "resolution": 10, "wavelength": "490nm"},
    "B03": {"name": "Green", "resolution": 10, "wavelength": "560nm"},
    "B04": {"name": "Red", "resolution": 10, "wavelength": "665nm"},
    "B05": {"name": "Red Edge 1", "resolution": 20, "wavelength": "705nm"},
    "B06": {"name": "Red Edge 2", "resolution": 20, "wavelength": "740nm"},
    "B07": {"name": "Red Edge 3", "resolution": 20, "wavelength": "783nm"},
    "B08": {"name": "NIR", "resolution": 10, "wavelength": "842nm"},
    "B8A": {"name": "NIR Narrow", "resolution": 20, "wavelength": "865nm"},
    "B09": {"name": "Water vapor", "resolution": 60, "wavelength": "945nm"},
    "B11": {"name": "SWIR 1", "resolution": 20, "wavelength": "1610nm"},
    "B12": {"name": "SWIR 2", "resolution": 20, "wavelength": "2190nm"},
}


def get_band_label(band_id: str) -> str:
    """Get human-readable label for a Sentinel-2 band.

    Parameters
    ----------
    band_id : str
        Band identifier (e.g., 'B04', 'B8A').

    Returns
    -------
    str
        Formatted label including band ID, name, and wavelength.
        Example: 'B04 - Red (665nm)'.

    Raises
    ------
    KeyError
        If band_id is not a valid Sentinel-2 band.

    """
    metadata = SENTINEL2_BANDS[band_id]
    return f"{band_id} - {metadata['name']} ({metadata['wavelength']})"
