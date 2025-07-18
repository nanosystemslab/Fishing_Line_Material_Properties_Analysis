# Fishing Line Material Properties Analysis

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15693814.svg)](https://doi.org/10.5281/zenodo.15693814)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15694088.svg)](https://doi.org/10.5281/zenodo.15694088)

A comprehensive Python package for analyzing material properties of fishing lines from tensile test data.

```{toctree}
:maxdepth: 2
:caption: Documentation

usage
reference
```

```{toctree}
:maxdepth: 1
:caption: Project Info

contributing
codeofconduct
license
```

## Overview

Fishing Line Material Properties Analysis is a scientific computing tool designed to extract mechanical properties from tensile testing data of fishing line materials. The package provides automated analysis of stress-strain curves, calculation of material constants, and generation of publication-ready visualizations.

## Key Features

### 🔬 Material Properties Analysis

Calculate modulus, yield stress, and maximum force from tensile test data with automated curve fitting and analysis.

### ⚡ Kinetic Energy Estimation

Compute kinetic energy and velocity from stress-strain curves using validated mechanical models.

### 📊 Publication-Ready Visualization

Generate high-quality stress-strain plots with material property annotations suitable for scientific publications.

### 🚀 Batch Processing

Process entire directory structures of test data automatically with parallel processing capabilities.

## Quick Start

### Installation

```bash
git clone https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis
cd Fishing_Line_Material_Properties_Analysis
poetry install
```

### Basic Usage

Analyze a single tensile test file:

```bash
poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/test.csv
```

Process multiple samples with statistical analysis:

```bash
poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/group_1/5in/*.csv --plot-type multi
```

## Scientific Applications

This package is designed for researchers and engineers working with:

- **Fishing line materials** - monofilament, braided, and fluorocarbon lines
- **Textile fibers** - synthetic and natural fiber analysis
- **Thin film materials** - mechanical characterization of thin films
- **Biomedical materials** - suture materials and medical fibers

## Sample Output

The analysis provides comprehensive material characterization:

| Property        | Value  | Units | Description                  |
| --------------- | ------ | ----- | ---------------------------- |
| Young's Modulus | 2.45   | MPa   | Material stiffness           |
| Yield Stress    | 1.85   | MPa   | Onset of plastic deformation |
| Maximum Force   | 45.23  | N     | Peak load capacity           |
| Kinetic Energy  | 0.0234 | J     | Energy storage capacity      |
| Break Velocity  | 1.03   | m/s   | Calculated failure velocity  |

## Data Requirements

Compatible with standard tensile testing equipment output:

```
"Time","Force","Stroke"
"sec","N","mm"
"0","0.002384186","0.0001"
"0.01","0.0055631","0.002333333"
...
```

## Research Applications

This package has been used in research published in materials science and engineering journals for:

- Characterizing mechanical properties of commercial fishing lines
- Developing new composite fiber materials
- Quality control in manufacturing processes
- Comparative studies of material performance

## Getting Help

- **Usage Guide**: Detailed examples and workflows → {doc}`usage`
- **API Reference**: Complete function documentation → {doc}`reference`
- **Contributing**: How to contribute to the project → {doc}`contributing`
- **Issues**: Report bugs or request features on [GitHub](https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis/issues)

## Citation

If you use this software or dataset in your research, please cite:

### Software

```bibtex
@software{matthew_nakamura_2025_15693814,
	author = {Matthew Nakamura},
	doi = {10.5281/zenodo.15693814},
	month = jun,
	publisher = {Zenodo},
	swhid = {swh:1:dir:9774416bfd0a3b64c546eeb74198f6abab0f55a4 ;origin=https://doi.org/10.5281/zenodo.15693813;vi sit=swh:1:snp:6196b6c9398e5737fef543af6732644c54c9 b97a;anchor=swh:1:rel:629adf510f09c35bc02be5156b08 598c85588ba7;path=nanosystemslab- Fishing\_Line\_Material\_Properties\_Analysis-da1d584},
	title = {nanosystemslab/Fishing\_Line\_Material\_Properties\_Analysis: v1.0.0 - Initial Release},
	url = {https://doi.org/10.5281/zenodo.15693814},
	version = {v1.0.0},
	year = 2025,
	bdsk-url-1 = {https://doi.org/10.5281/zenodo.15693814}}
```

### Dataset

```bibtex
@dataset{nakamura_2025_15694088,
	author = {Nakamura, Matthew and Grogget, Jacob and HEYES, CORRISA and Okura, Kailer and Matsunaga, Kaitlyn and Brown, Joseph},
	doi = {10.5281/zenodo.15694088},
	month = jun,
	publisher = {Zenodo},
	title = {Fishing Line Material Properties Dataset},
	url = {https://doi.org/10.5281/zenodo.15694088},
	year = 2025,
	bdsk-url-1 = {https://doi.org/10.5281/zenodo.15694088}}
```

**Software DOI**: [10.5281/zenodo.15693814](https://doi.org/10.5281/zenodo.15693814)
**Dataset DOI**: [10.5281/zenodo.15694088](https://doi.org/10.5281/zenodo.15694088)

## License

This project is licensed under the GPL-3.0 License - see the {doc}`license` page for details.

---

_Developed by the [Nanosystems Lab](https://github.com/nanosystemslab) for the scientific community._
