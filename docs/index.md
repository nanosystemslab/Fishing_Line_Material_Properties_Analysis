# Fishing Line Material Properties Analysis

A comprehensive Python package for analyzing material properties of fishing lines from tensile test data.

```{toctree}
:maxdepth: 2
:hidden:

usage
reference
contributing
codeofconduct
license
```

## Overview

Fishing Line Material Properties Analysis is a scientific computing tool designed to extract mechanical properties from tensile testing data of fishing line materials. The package provides automated analysis of stress-strain curves, calculation of material constants, and generation of publication-ready visualizations.

## Key Features

::::{grid} 2
:::{grid-item-card} 🔬 Material Properties Analysis
:text-align: center

Calculate modulus, yield stress, and maximum force from tensile test data with automated curve fitting and analysis.
:::

:::{grid-item-card} ⚡ Kinetic Energy Estimation  
:text-align: center

Compute kinetic energy and velocity from stress-strain curves using validated mechanical models.
:::

:::{grid-item-card} 📊 Publication-Ready Visualization
:text-align: center

Generate high-quality stress-strain plots with material property annotations suitable for scientific publications.
:::

:::{grid-item-card} 🚀 Batch Processing
:text-align: center

Process entire directory structures of test data automatically with parallel processing capabilities.
:::
::::

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

| Property | Value | Units | Description |
|----------|-------|-------|-------------|
| Young's Modulus | 2.45 | MPa | Material stiffness |
| Yield Stress | 1.85 | MPa | Onset of plastic deformation |
| Maximum Force | 45.23 | N | Peak load capacity |
| Kinetic Energy | 0.0234 | J | Energy storage capacity |
| Break Velocity | 1.03 | m/s | Calculated failure velocity |

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

If you use this software in your research, please cite:

```bibtex
@software{fishing_line_analysis,
  title = {Fishing Line Material Properties Analysis},
  author = {Nanosystems Lab},
  year = {2025},
  url = {https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis},
  version = {0.0.1}
}
```

## License

This project is licensed under the GPL-3.0 License - see the {doc}`license` page for details.

---

*Developed by the [Nanosystems Lab](https://github.com/nanosystemslab) for the scientific community.*
