import numpy as np
import pytest

from mimosa.composite import (
    COMPOSITE_PRESETS,
    calculate_moisture_index,
    calculate_ndsi,
    calculate_ndvi,
    calculate_ndwi,
    create_index_visualization,
    create_rgb_composite,
    get_composite_preset,
    normalize_band,
)


def test_normalize_band_no_mask():
    band = np.array([[0.1, 0.5], [0.9, 0.3]], dtype=np.float32)
    normalized = normalize_band(band, mask=None)

    assert normalized.shape == band.shape
    assert normalized.dtype == np.float32
    assert normalized.min() >= 0.0
    assert normalized.max() <= 1.0


def test_normalize_band_with_mask():
    band = np.array([[0.1, 0.5], [0.9, 0.3]], dtype=np.float32)
    mask = np.array([[255, 255], [0, 255]], dtype=np.uint8)

    normalized = normalize_band(band, mask=mask)

    assert normalized.shape == band.shape
    assert normalized[1, 0] == 0.0  # Masked pixel should be 0


def test_composite_presets_structure():
    assert len(COMPOSITE_PRESETS) == 5
    for preset_config in COMPOSITE_PRESETS.values():
        assert "r" in preset_config
        assert "g" in preset_config
        assert "b" in preset_config


def test_get_composite_preset():
    preset = get_composite_preset("True Color")
    assert preset == {"r": "B04", "g": "B03", "b": "B02"}


def test_get_composite_preset_invalid():
    with pytest.raises(KeyError):
        get_composite_preset("Invalid Preset")


def test_create_rgb_composite():
    # Create synthetic band data
    h, w = 10, 10
    rng = np.random.default_rng(42)
    bands = {
        "B04": rng.random((h, w)).astype(np.float32),
        "B03": rng.random((h, w)).astype(np.float32),
        "B02": rng.random((h, w)).astype(np.float32),
    }
    masks = {
        "B04": np.full((h, w), 255, dtype=np.uint8),
        "B03": np.full((h, w), 255, dtype=np.uint8),
        "B02": np.full((h, w), 255, dtype=np.uint8),
    }

    rgb = create_rgb_composite(bands, masks, "B04", "B03", "B02")

    assert rgb.shape == (h, w, 3)
    assert rgb.dtype == np.uint8


def test_create_rgb_composite_with_masked_pixels():
    # Create synthetic band data
    h, w = 5, 5
    bands = {
        "B04": np.ones((h, w), dtype=np.float32),
        "B03": np.ones((h, w), dtype=np.float32),
        "B02": np.ones((h, w), dtype=np.float32),
    }
    masks = {
        "B04": np.full((h, w), 255, dtype=np.uint8),
        "B03": np.full((h, w), 255, dtype=np.uint8),
        "B02": np.full((h, w), 255, dtype=np.uint8),
    }
    # Mask one pixel
    masks["B04"][0, 0] = 0

    rgb = create_rgb_composite(bands, masks, "B04", "B03", "B02")

    # Masked pixel should be black
    assert np.array_equal(rgb[0, 0], [0, 0, 0])


def test_calculate_ndvi():
    h, w = 10, 10
    bands = {
        "B08": np.full((h, w), 0.8, dtype=np.float32),  # High NIR
        "B04": np.full((h, w), 0.2, dtype=np.float32),  # Low Red
    }
    masks = {
        "B08": np.full((h, w), 255, dtype=np.uint8),
        "B04": np.full((h, w), 255, dtype=np.uint8),
    }

    ndvi = calculate_ndvi(bands, masks)

    assert ndvi.shape == (h, w)
    assert ndvi.dtype == np.float32
    # NDVI = (0.8 - 0.2) / (0.8 + 0.2) = 0.6
    assert np.allclose(ndvi, 0.6)


def test_calculate_moisture_index():
    h, w = 10, 10
    bands = {
        "B8A": np.full((h, w), 0.7, dtype=np.float32),
        "B11": np.full((h, w), 0.3, dtype=np.float32),
    }
    masks = {
        "B8A": np.full((h, w), 255, dtype=np.uint8),
        "B11": np.full((h, w), 255, dtype=np.uint8),
    }

    moisture = calculate_moisture_index(bands, masks)

    assert moisture.shape == (h, w)
    assert moisture.dtype == np.float32
    # (0.7 - 0.3) / (0.7 + 0.3) = 0.4
    assert np.allclose(moisture, 0.4)


def test_calculate_ndwi():
    h, w = 10, 10
    bands = {
        "B03": np.full((h, w), 0.6, dtype=np.float32),
        "B08": np.full((h, w), 0.4, dtype=np.float32),
    }
    masks = {
        "B03": np.full((h, w), 255, dtype=np.uint8),
        "B08": np.full((h, w), 255, dtype=np.uint8),
    }

    ndwi = calculate_ndwi(bands, masks)

    assert ndwi.shape == (h, w)
    assert ndwi.dtype == np.float32
    # (0.6 - 0.4) / (0.6 + 0.4) = 0.2
    assert np.allclose(ndwi, 0.2)


def test_calculate_ndsi():
    h, w = 10, 10
    bands = {
        "B03": np.full((h, w), 0.8, dtype=np.float32),
        "B11": np.full((h, w), 0.2, dtype=np.float32),
    }
    masks = {
        "B03": np.full((h, w), 255, dtype=np.uint8),
        "B11": np.full((h, w), 255, dtype=np.uint8),
    }

    ndsi = calculate_ndsi(bands, masks)

    assert ndsi.shape == (h, w)
    assert ndsi.dtype == np.float32
    # (0.8 - 0.2) / (0.8 + 0.2) = 0.6
    assert np.allclose(ndsi, 0.6)


def test_create_index_visualization():
    h, w = 10, 10
    index_data = np.linspace(-1, 1, h * w).reshape(h, w).astype(np.float32)

    rgb = create_index_visualization(index_data)

    assert rgb.shape == (h, w, 3)
    assert rgb.dtype == np.uint8
