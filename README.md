# Mimosa Detection from Sentinel-2 Satellite Imagery

This project develops algorithms and tools to detect and highlight concentrations of *Acacia dealbata* (mimosa) using satellite imagery from the Copernicus Sentinel-2 mission.

## Background

**Acacia dealbata** (mimosa) produces bright yellow blooms along the French Riviera in late winter/early spring. This project uses satellite imagery to detect and map mimosa blooms, making it easier to find the best spots for cycling routes with mimosa and sea views. The distinctive yellow flowers create unique spectral signatures detectable from Sentinel-2 imagery.

**Copernicus Sentinel-2** is a European Space Agency (ESA) Earth observation mission providing high-resolution multispectral imagery. The mission consists of two satellites delivering optical imagery across 13 spectral bands, enabling vegetation monitoring and land cover classification. Data is freely accessible through the [Copernicus Open Access Hub](https://scihub.copernicus.eu/) and [Copernicus Browser](https://browser.dataspace.copernicus.eu/).

## Project Goals

1. **Develop Python algorithms** to process Sentinel-2 multispectral data and identify mimosa blooms
2. **Validate detection methods** using time-series data capturing the mimosa bloom cycle
3. **Create reusable tools** packaged in the `mimosa` library for geospatial analysis
4. **Generate Copernicus Browser scripts** for real-time mimosa visualization to discover the best cycling routes and scenic spots

## Study Area and Data

The analysis focuses on **Mandelieu-la-Napoule** (French Riviera), a region with documented mimosa presence and annual bloom festivals.

### Included Dataset

The [analysis/data/](analysis/data/) directory contains five Sentinel-2 L2A acquisitions spanning the 2024-2025 mimosa bloom cycle:

| Date | Mimosa Status | Description |
|------|---------------|-------------|
| **2024-12-16** | Pre-bloom | No visible mimosa presence |
| **2025-01-28** | Early bloom | First signs of flowering |
| **2025-02-14** | Peak bloom | Maximum flower coverage |
| **2025-03-04** | Declining | Flowers fading |
| **2025-03-31** | Post-bloom | No visible flowers |

Each acquisition includes:
- **True color composite** (JPEG and TIFF): Visual reference imagery
- **All spectral bands** (B01-B12, B8A): Raw multispectral data with data mask applied
- **10-60m spatial resolution**: Depending on the spectral band

This temporal series enables testing detection algorithms across all growth phases of the mimosa bloom cycle.

## Project Structure

```
mimosa/
├── analysis/
│   ├── data/              # Sentinel-2 imagery for Mandelieu-la-Napoule
│   └── notebooks/         # Jupyter notebooks showcasing analysis and results
├── src/
│   └── mimosa/            # Python package for mimosa detection
│       └── ...            # TIFF processing, spectral analysis, visualization
└── tests/                 # Unit tests for the mimosa package
```

- **[analysis/notebooks/](analysis/notebooks/)**: Interactive exploration, algorithm development, and visualization
- **[src/mimosa/](src/mimosa/)**: Production-ready code for processing multispectral TIFF data and highlighting mimosa areas
- **[analysis/data/](analysis/data/)**: Reference dataset for validation and testing

## Getting Started

### Prerequisites

- Python ≥ 3.13
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd mimosa

# Install dependencies
uv sync

# Install development tools
uv sync --group dev
```

### Running Analysis

```bash
# Launch Jupyter for interactive exploration
uv run jupyter lab

# Run tests
uv run pytest
```

## References

- **Copernicus Sentinel-2**: https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-2
- **Copernicus Data Space**: https://dataspace.copernicus.eu/
- **La Route du Mimosa**: https://www.routedumimosa.com/
- **Sentinel-2 Band Specifications**: [ESA Sentinel-2 User Guide](https://sentinels.copernicus.eu/web/sentinel/user-guides/sentinel-2-msi/resolutions/spatial)
