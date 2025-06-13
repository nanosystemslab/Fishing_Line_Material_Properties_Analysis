# Fishing_Line_Material_Properties_Analysis

[![Status](https://img.shields.io/badge/status-development-orange)][repository]
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)][repository]
[![License](https://img.shields.io/badge/license-GPL--3.0-green)][license]

[![Read the documentation at https://Fishing_Line_Material_Properties_Analysis.readthedocs.io/](https://img.shields.io/readthedocs/Fishing_Line_Material_Properties_Analysis/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/nanosystemslab/Fishing_Line_Material_Properties_Analysis/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[repository]: https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis
[read the docs]: https://Fishing_Line_Material_Properties_Analysis.readthedocs.io/
[tests]: https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/nanosystemslab/Fishing_Line_Material_Properties_Analysis
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Features

- **Material Properties Analysis**: Calculate modulus, yield stress, and maximum force from tensile test data
- **Kinetic Energy Estimation**: Compute kinetic energy and velocity from stress-strain curves
- **Visualization**: Generate publication-ready stress-strain plots with material property annotations
- **Batch Processing**: Process entire directory structures of test data automatically
- **Multiple Output Formats**: Single trace plots, multi-trace overlays, and summary statistics
- **Command Line Interface**: Easy-to-use CLI for all analysis functions

## Requirements

- Python 3.9+
- Poetry (for dependency management)
- Required packages: numpy, pandas, matplotlib, seaborn, scipy, kneed

## Installation

You can install _Fishing_Line_Material_Properties_Analysis_ by cloning this repository:

```console
$ git clone https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis
$ cd Fishing_Line_Material_Properties_Analysis
$ poetry install
```

Alternatively, you can install it in development mode:

```console
$ git clone https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis
$ cd Fishing_Line_Material_Properties_Analysis
$ pip install -e .
```

## Usage

The tool provides three main commands: `analyze`, `visualize`, and `batch`.

### Single File Analysis

Analyze a single test file and generate a stress-strain plot:

```console
$ poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/group_1/5in/test--line-crimp-21--0.csv
```

**Output:**
```
File: data/group_1/5in/test--line-crimp-21--0.csv | Force: 45.23N | Modulus: 2.45MPa | Yield: 1.85MPa | KE: 0.0234J | Velocity: 1.03m/s | Length: 127.0mm | Diameter: 21mm
```

### Multi-Sample Analysis

Analyze multiple files together for comparison:

```console
$ poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/group_1/5in/*.csv --plot-type multi
```

**Output:**
```
Multi-sample | Samples: 10 | Avg KE: 0.0245±0.0034J | Avg Velocity: 1.05±0.15m/s | Avg Force: 46.12±3.45N
```

### Batch Processing

Process entire directory structure automatically:

```console
$ poetry run Fishing_Line_Material_Properties_Analysis batch -d data --summary
```

This will:
- Process all groups (group_1, group_2, group_3)
- Process all lengths (5in, 10in, 20in) within each group
- Generate multi-trace plots for each group/length combination
- Create a summary report with statistics across all tests

### Custom Analysis Parameters

Specify different parameters for plotting:

```console
# Force vs Stroke plot
$ poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/group_1/5in/*.csv --x-param Stroke --y-param Force

# Custom output directory
$ poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/group_1/5in/*.csv -o results/
```

### Visualize Output Data

For plotting pre-computed results:

```console
$ poetry run Fishing_Line_Material_Properties_Analysis visualize -i output_data.csv --x-param D --y-param KE
```

### Complete Workflow Example

Process all your data systematically:

```console
# 1. Analyze individual samples in each group/length
$ poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/group_1/5in/*.csv --plot-type multi -o results/group1_5in/
$ poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/group_1/10in/*.csv --plot-type multi -o results/group1_10in/
$ poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/group_1/20in/*.csv --plot-type multi -o results/group1_20in/

# 2. Process everything with batch command
$ poetry run Fishing_Line_Material_Properties_Analysis batch -d data --summary -o results/summary/

# 3. Extract key results
$ poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/group_*/*/test*.csv --plot-type multi > results/all_results.txt
```

### Available Parameters

**Analysis Parameters:**
- `--x-param`: Time, Force, Stroke, Stress, Strain (default: Strain)
- `--y-param`: Time, Force, Stroke, Stress, Strain (default: Stress)
- `--plot-type`: single, multi (default: single)
- `-o, --output`: Output directory (default: out)

**Visualization Parameters:**
- `--x-param`: KE, V, D, L (default: D)  
- `--y-param`: KE, V, D, L (default: KE)

## Output Files

The tool generates:
- **Plots**: PNG files with stress-strain curves and material properties
- **Console Output**: Material properties in readable format
- **Summary Reports**: Text files with statistical analysis (when using `--summary`)

## Data Format

Expected CSV format for input files:
```
"Time","Force","Stroke"
"sec","N","mm"
"0","0.002384186","0.0001"
"0.01","0.0055631","0.002333333"
...
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [GPL 3.0 license][license],
_Fishing_Line_Material_Properties_Analysis_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@nanosystemslab]'s [Nanosystems Lab Python Cookiecutter] template.

[@nanosystemslab]: https://github.com/nanosystemslab
[Nanosystems Lab Python Cookiecutter]: https://github.com/nanosystemslab/cookiecutter-nanosystemslab
[file an issue]: https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis/issues

<!-- github-only -->

[license]: https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis/blob/main/LICENSE
[contributor guide]: https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis/blob/main/CONTRIBUTING.md
[command-line reference]: https://Fishing_Line_Material_Properties_Analysis.readthedocs.io/en/latest/usage.html
