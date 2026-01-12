from pathlib import Path

import numpy as np
import pytest

from mimosa.data import (
    discover_dates,
    get_date_directory,
    load_all_bands,
    load_band,
    load_true_color,
)

DATA_DIR = Path(__file__).parent.parent / "analysis" / "data"


@pytest.mark.integration
def test_discover_dates():
    dates = discover_dates(DATA_DIR)

    assert len(dates) == 5
    assert all(date.year in [2024, 2025] for date in dates)
    # Dates should be sorted
    assert dates == sorted(dates)


@pytest.mark.integration
def test_get_date_directory():
    dates = discover_dates(DATA_DIR)
    first_date = dates[0]

    date_dir = get_date_directory(DATA_DIR, first_date)

    assert date_dir.exists()
    assert date_dir.is_dir()
    assert "Sentinel-2_L2A" in date_dir.name


@pytest.mark.integration
def test_load_true_color():
    dates = discover_dates(DATA_DIR)
    first_date = dates[0]

    img, mask = load_true_color(DATA_DIR, first_date)

    assert img.shape == (819, 1015, 3)
    assert img.dtype == np.uint8
    assert mask.shape == (819, 1015)
    assert mask.dtype == np.uint8
    # Check mask values are 0 or 255
    assert np.all((mask == 0) | (mask == 255))


@pytest.mark.integration
def test_load_band():
    dates = discover_dates(DATA_DIR)
    first_date = dates[0]

    data, mask = load_band(DATA_DIR, first_date, "B04")

    assert data.shape == (819, 1015)
    assert data.dtype == np.float32
    assert mask.shape == (819, 1015)
    assert mask.dtype == np.uint8
    # Data should be normalized (mostly in 0-1 range)
    assert data.min() >= 0.0
    assert data.max() <= 1.0


@pytest.mark.integration
def test_load_all_bands():
    dates = discover_dates(DATA_DIR)
    first_date = dates[0]

    bands, masks = load_all_bands(DATA_DIR, first_date)

    assert len(bands) == 12
    assert len(masks) == 12
    assert set(bands.keys()) == {
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
    }
    # Check one band
    assert bands["B04"].dtype == np.float32
    assert masks["B04"].dtype == np.uint8
