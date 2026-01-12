"""Band manipulation and RGB composite creation functions."""

import numpy as np
from numpy.typing import NDArray

# Copernicus Browser standard layer presets
# Based on https://browser.dataspace.copernicus.eu/ Sentinel-2 layers
COMPOSITE_PRESETS: dict[str, dict[str, str]] = {
    "True Color": {"r": "B04", "g": "B03", "b": "B02"},
    "False Color": {"r": "B08", "g": "B04", "b": "B03"},
    "Highlight Optimized Natural Color": {"r": "B04", "g": "B03", "b": "B02"},
    "False Color Urban": {"r": "B12", "g": "B11", "b": "B04"},
    "SWIR": {"r": "B12", "g": "B8A", "b": "B04"},
}

# Index-based layers that require calculation
INDEX_LAYERS = [
    "NDVI",
    "Moisture Index",
    "NDWI",
    "NDSI",
]


def normalize_band(
    band: NDArray[np.float32],
    mask: NDArray[np.uint8] | None = None,
    percentile_clip: tuple[float, float] = (2, 98),
) -> NDArray[np.float32]:
    """Normalize band values to 0-1 range using percentile clipping.

    Parameters
    ----------
    band : NDArray[np.float32]
        Band data array (H, W).
    mask : NDArray[np.uint8] | None
        Optional mask where 255=valid, 0=invalid. If provided, only valid
        pixels are used for percentile calculation.
    percentile_clip : tuple[float, float]
        Lower and upper percentiles for clipping, by default (2, 98).

    Returns
    -------
    NDArray[np.float32]
        Normalized band values in 0-1 range, masked pixels set to 0.

    """
    # Create boolean mask for valid pixels
    if mask is not None:
        valid_mask = mask == 255
        valid_pixels = band[valid_mask]
    else:
        valid_pixels = band.ravel()

    # Calculate percentiles using only valid pixels
    if len(valid_pixels) > 0:
        p_low, p_high = np.percentile(valid_pixels, percentile_clip)
    else:
        # Fallback if no valid pixels
        p_low, p_high = 0.0, 1.0

    # Clip and normalize
    normalized = np.clip(band, p_low, p_high)
    if p_high > p_low:
        normalized = (normalized - p_low) / (p_high - p_low)
    else:
        normalized = np.zeros_like(normalized)

    # Set masked pixels to 0
    if mask is not None:
        normalized[~valid_mask] = 0

    return normalized.astype(np.float32)


def create_rgb_composite(
    bands: dict[str, NDArray[np.float32]],
    masks: dict[str, NDArray[np.uint8]],
    r_band: str,
    g_band: str,
    b_band: str,
    normalize: bool = True,
) -> NDArray[np.uint8]:
    """Create an RGB composite from three spectral bands.

    Parameters
    ----------
    bands : dict[str, NDArray[np.float32]]
        Dictionary of band data arrays.
    masks : dict[str, NDArray[np.uint8]]
        Dictionary of mask arrays where 255=valid, 0=invalid.
    r_band : str
        Band ID to use for red channel.
    g_band : str
        Band ID to use for green channel.
    b_band : str
        Band ID to use for blue channel.
    normalize : bool
        Whether to apply percentile-based normalization, by default True.

    Returns
    -------
    NDArray[np.uint8]
        RGB composite image (H, W, 3) with masked pixels set to black.

    """
    # Extract bands
    r_data = bands[r_band]
    g_data = bands[g_band]
    b_data = bands[b_band]

    # Extract masks
    r_mask = masks[r_band]
    g_mask = masks[g_band]
    b_mask = masks[b_band]

    # Normalize each channel if requested
    if normalize:
        r_norm = normalize_band(r_data, r_mask)
        g_norm = normalize_band(g_data, g_mask)
        b_norm = normalize_band(b_data, b_mask)
    else:
        r_norm = r_data
        g_norm = g_data
        b_norm = b_data

    # Combine masks (pixel is valid only if valid in all bands)
    combined_mask = (r_mask == 255) & (g_mask == 255) & (b_mask == 255)

    # Convert to uint8 (0-255)
    r_uint8 = (r_norm * 255).astype(np.uint8)
    g_uint8 = (g_norm * 255).astype(np.uint8)
    b_uint8 = (b_norm * 255).astype(np.uint8)

    # Stack into RGB image
    rgb = np.stack([r_uint8, g_uint8, b_uint8], axis=-1)

    # Set masked pixels to black
    rgb[~combined_mask] = 0

    return rgb


def get_composite_preset(name: str) -> dict[str, str]:
    """Get predefined band assignments for a composite preset.

    Parameters
    ----------
    name : str
        Name of the composite preset.

    Returns
    -------
    dict[str, str]
        Dictionary with 'r', 'g', 'b' keys mapping to band IDs.

    Raises
    ------
    KeyError
        If preset name is not recognized.

    """
    return COMPOSITE_PRESETS[name]


def calculate_ndvi(
    bands: dict[str, NDArray[np.float32]],
    masks: dict[str, NDArray[np.uint8]],
) -> NDArray[np.float32]:
    """Calculate NDVI (Normalized Difference Vegetation Index).

    Formula: (B8 - B4) / (B8 + B4)

    Parameters
    ----------
    bands : dict[str, NDArray[np.float32]]
        Dictionary of band data arrays.
    masks : dict[str, NDArray[np.uint8]]
        Dictionary of mask arrays.

    Returns
    -------
    NDArray[np.float32]
        NDVI values in range [-1, 1], masked pixels set to 0.

    """
    nir = bands["B08"]
    red = bands["B04"]
    combined_mask = (masks["B08"] == 255) & (masks["B04"] == 255)

    # Avoid division by zero
    denominator = nir + red
    ndvi = np.zeros_like(nir)
    valid = combined_mask & (denominator != 0)
    ndvi[valid] = (nir[valid] - red[valid]) / denominator[valid]

    # Set masked pixels to 0
    ndvi[~combined_mask] = 0

    return ndvi.astype(np.float32)


def calculate_moisture_index(
    bands: dict[str, NDArray[np.float32]],
    masks: dict[str, NDArray[np.uint8]],
) -> NDArray[np.float32]:
    """Calculate Moisture Index (Normalized Difference Moisture Index).

    Formula: (B8A - B11) / (B8A + B11)

    Parameters
    ----------
    bands : dict[str, NDArray[np.float32]]
        Dictionary of band data arrays.
    masks : dict[str, NDArray[np.uint8]]
        Dictionary of mask arrays.

    Returns
    -------
    NDArray[np.float32]
        Moisture index values in range [-1, 1], masked pixels set to 0.

    """
    nir_narrow = bands["B8A"]
    swir1 = bands["B11"]
    combined_mask = (masks["B8A"] == 255) & (masks["B11"] == 255)

    # Avoid division by zero
    denominator = nir_narrow + swir1
    moisture = np.zeros_like(nir_narrow)
    valid = combined_mask & (denominator != 0)
    moisture[valid] = (nir_narrow[valid] - swir1[valid]) / denominator[valid]

    # Set masked pixels to 0
    moisture[~combined_mask] = 0

    return moisture.astype(np.float32)


def calculate_ndwi(
    bands: dict[str, NDArray[np.float32]],
    masks: dict[str, NDArray[np.uint8]],
) -> NDArray[np.float32]:
    """Calculate NDWI (Normalized Difference Water Index).

    Formula: (B3 - B8) / (B3 + B8)

    Parameters
    ----------
    bands : dict[str, NDArray[np.float32]]
        Dictionary of band data arrays.
    masks : dict[str, NDArray[np.uint8]]
        Dictionary of mask arrays.

    Returns
    -------
    NDArray[np.float32]
        NDWI values in range [-1, 1], masked pixels set to 0.

    """
    green = bands["B03"]
    nir = bands["B08"]
    combined_mask = (masks["B03"] == 255) & (masks["B08"] == 255)

    # Avoid division by zero
    denominator = green + nir
    ndwi = np.zeros_like(green)
    valid = combined_mask & (denominator != 0)
    ndwi[valid] = (green[valid] - nir[valid]) / denominator[valid]

    # Set masked pixels to 0
    ndwi[~combined_mask] = 0

    return ndwi.astype(np.float32)


def calculate_ndsi(
    bands: dict[str, NDArray[np.float32]],
    masks: dict[str, NDArray[np.uint8]],
) -> NDArray[np.float32]:
    """Calculate NDSI (Normalized Difference Snow Index).

    Formula: (B3 - B11) / (B3 + B11)

    Parameters
    ----------
    bands : dict[str, NDArray[np.float32]]
        Dictionary of band data arrays.
    masks : dict[str, NDArray[np.uint8]]
        Dictionary of mask arrays.

    Returns
    -------
    NDArray[np.float32]
        NDSI values in range [-1, 1], masked pixels set to 0.

    """
    green = bands["B03"]
    swir1 = bands["B11"]
    combined_mask = (masks["B03"] == 255) & (masks["B11"] == 255)

    # Avoid division by zero
    denominator = green + swir1
    ndsi = np.zeros_like(green)
    valid = combined_mask & (denominator != 0)
    ndsi[valid] = (green[valid] - swir1[valid]) / denominator[valid]

    # Set masked pixels to 0
    ndsi[~combined_mask] = 0

    return ndsi.astype(np.float32)


def create_index_visualization(
    index_data: NDArray[np.float32],
    colormap: str = "RdYlGn",  # noqa: ARG001
) -> NDArray[np.uint8]:
    """Create RGB visualization of an index using a colormap.

    Parameters
    ----------
    index_data : NDArray[np.float32]
        Index values typically in range [-1, 1].
    colormap : str
        Colormap name (currently supports 'RdYlGn' for vegetation indices).

    Returns
    -------
    NDArray[np.uint8]
        RGB image (H, W, 3) with color-mapped index values.

    """
    # Normalize to 0-1 range
    normalized = (index_data + 1) / 2  # [-1, 1] -> [0, 1]
    normalized = np.clip(normalized, 0, 1)

    # Simple RdYlGn colormap implementation
    # Red (low) -> Yellow (mid) -> Green (high)
    rgb = np.zeros((*index_data.shape, 3), dtype=np.uint8)

    # Red channel: high at low values, decreases
    rgb[..., 0] = ((1 - normalized) * 255).astype(np.uint8)

    # Green channel: increases throughout
    rgb[..., 1] = (normalized * 255).astype(np.uint8)

    # Blue channel: minimal (creates red-yellow-green gradient)
    rgb[..., 2] = 0

    return rgb
