import pytest

from mimosa.constants import SENTINEL2_BANDS, get_band_label


def test_sentinel2_bands_completeness():
    assert len(SENTINEL2_BANDS) == 12
    expected_bands = {
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
    assert set(SENTINEL2_BANDS.keys()) == expected_bands


def test_sentinel2_bands_structure():
    for metadata in SENTINEL2_BANDS.values():
        assert "name" in metadata
        assert "resolution" in metadata
        assert "wavelength" in metadata
        assert isinstance(metadata["name"], str)
        assert isinstance(metadata["resolution"], int)
        assert isinstance(metadata["wavelength"], str)


def test_get_band_label():
    label = get_band_label("B04")
    assert "B04" in label
    assert "Red" in label
    assert "665nm" in label


def test_get_band_label_invalid():
    with pytest.raises(KeyError):
        get_band_label("B99")
