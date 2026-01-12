"""Data loading functions for Sentinel-2 TIFF files."""

from datetime import datetime
from pathlib import Path

import numpy as np
import rasterio
from numpy.typing import NDArray


def discover_dates(data_dir: Path) -> list[datetime]:
    """Discover all available Sentinel-2 acquisition dates.

    Parameters
    ----------
    data_dir : Path
        Root directory containing Sentinel-2 date subdirectories.

    Returns
    -------
    list[datetime]
        Sorted list of acquisition dates extracted from directory names.

    """
    dates = []
    for subdir in data_dir.iterdir():
        if subdir.is_dir() and "Sentinel-2_L2A" in subdir.name:
            # Parse date from directory name format:
            # YYYY-MM-DD-HH_MM_YYYY-MM-DD-HH_MM_Sentinel-2_L2A
            date_str = subdir.name.split("-00_00")[0]
            # Naive datetime is appropriate - these are acquisition dates only
            date = datetime.strptime(date_str, "%Y-%m-%d")  # noqa: DTZ007
            dates.append(date)
    return sorted(dates)


def get_date_directory(data_dir: Path, date: datetime) -> Path:
    """Get the directory path for a specific Sentinel-2 acquisition date.

    Parameters
    ----------
    data_dir : Path
        Root directory containing Sentinel-2 date subdirectories.
    date : datetime
        Target acquisition date.

    Returns
    -------
    Path
        Directory path for the specified date.

    Raises
    ------
    FileNotFoundError
        If no directory exists for the specified date.

    """
    date_str = date.strftime("%Y-%m-%d")
    # Find directory matching the date pattern
    for subdir in data_dir.iterdir():
        if subdir.is_dir() and subdir.name.startswith(date_str):
            return subdir
    msg = f"No directory found for date {date_str}"
    raise FileNotFoundError(msg)


def load_true_color(
    data_dir: Path, date: datetime
) -> tuple[NDArray[np.uint8], NDArray[np.uint8]]:
    """Load true color RGB TIFF and its mask for a given date.

    Parameters
    ----------
    data_dir : Path
        Root directory containing Sentinel-2 data.
    date : datetime
        Acquisition date to load.

    Returns
    -------
    tuple[NDArray[np.uint8], NDArray[np.uint8]]
        RGB image array (H, W, 3) and mask array (H, W) where 255=valid, 0=masked.

    """
    date_dir = get_date_directory(data_dir, date)

    # Find true color TIFF (pattern: *_True_color.tiff)
    true_color_files = list(date_dir.glob("*_True_color.tiff"))
    if not true_color_files:
        msg = f"No true color TIFF found in {date_dir}"
        raise FileNotFoundError(msg)

    with rasterio.open(true_color_files[0]) as src:
        # Read RGB data (3 bands, float32 in 0-1 range)
        data = src.read()  # Shape: (3, H, W)

        # Convert to uint8 for display
        img = (data * 255).astype(np.uint8)
        img = np.transpose(img, (1, 2, 0))  # Convert to HWC format

        # Read mask (255=valid, 0=invalid)
        # Use first band's mask (all bands should have same mask)
        mask = src.read_masks(1)

    return img, mask


def load_band(
    data_dir: Path, date: datetime, band: str
) -> tuple[NDArray[np.float32], NDArray[np.uint8]]:
    """Load a single spectral band and its mask for a given date.

    Parameters
    ----------
    data_dir : Path
        Root directory containing Sentinel-2 data.
    date : datetime
        Acquisition date to load.
    band : str
        Band identifier (e.g., 'B04', 'B8A').

    Returns
    -------
    tuple[NDArray[np.float32], NDArray[np.uint8]]
        Band data array (H, W) and mask array (H, W) where 255=valid, 0=masked.

    """
    date_dir = get_date_directory(data_dir, date)

    # Find band TIFF (pattern: *_B##_(Raw).tiff)
    band_files = list(date_dir.glob(f"*_{band}_*.tiff"))
    if not band_files:
        msg = f"No TIFF found for band {band} in {date_dir}"
        raise FileNotFoundError(msg)

    with rasterio.open(band_files[0]) as src:
        # Read band data (float32, already normalized to 0-1 range)
        data = src.read(1).astype(np.float32)

        # Read mask (255=valid, 0=invalid)
        mask = src.read_masks(1)

    return data, mask


def load_all_bands(
    data_dir: Path, date: datetime
) -> tuple[dict[str, NDArray[np.float32]], dict[str, NDArray[np.uint8]]]:
    """Load all spectral bands and their masks for a given date.

    Parameters
    ----------
    data_dir : Path
        Root directory containing Sentinel-2 data.
    date : datetime
        Acquisition date to load.

    Returns
    -------
    tuple[dict[str, NDArray[np.float32]], dict[str, NDArray[np.uint8]]]
        Dictionary of band data arrays and dictionary of mask arrays.
        Band keys: 'B01', 'B02', ..., 'B12', 'B8A'.

    """
    band_ids = [
        "B01",
        "B02",
        "B03",
        "B04",
        "B05",
        "B06",
        "B07",
        "B08",
        "B8A",
        "B09",
        "B11",
        "B12",
    ]

    bands = {}
    masks = {}

    for band_id in band_ids:
        data, mask = load_band(data_dir, date, band_id)
        bands[band_id] = data
        masks[band_id] = mask

    return bands, masks
