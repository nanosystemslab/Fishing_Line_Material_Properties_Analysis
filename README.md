# Fishing_Line_Material_Properties_Analysis

[![Status](https://img.shields.io/badge/status-stable-brightgreen)][repository]
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)][repository]
[![License](https://img.shields.io/badge/license-GPL--3.0-green)][license]
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15693814.svg)](https://doi.org/10.5281/zenodo.15693814)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.15694088.svg)](https://doi.org/10.5281/zenodo.15694088)

[![Tests](https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/nanosystemslab/Fishing_Line_Material_Properties_Analysis/branch/main/graph/badge.svg)][codecov]
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[![Read the documentation at https://Fishing_Line_Material_Properties_Analysis.readthedocs.io/](https://img.shields.io/readthedocs/Fishing_Line_Material_Properties_Analysis/latest.svg?label=Read%20the%20Docs)][read the docs]
![Analysis Types](https://img.shields.io/badge/Analysis-Material%20Properties-blue)
![Calculations](https://img.shields.io/badge/Calculates-Modulus%20%7C%20Yield%20%7C%20KE-green)
![CLI](https://img.shields.io/badge/Interface-CLI-red)
![Output Types](https://img.shields.io/badge/Outputs-Plots%20%7C%20Data%20%7C%20Reports-orange)

[repository]: https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis
[read the docs]: https://fishing-line-material-properties-analysis.readthedocs.io/en/latest//
[tests]: https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/nanosystemslab/Fishing_Line_Material_Properties_Analysis
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black
[license]: https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis/blob/main/LICENSE

## Features

- **Material Properties Analysis**: Calculate modulus, yield stress, and maximum force from tensile test data
- **Kinetic Energy Estimation**: Compute kinetic energy and velocity from stress-strain curves
- **Visualization**: Generate publication-ready stress-strain plots with material property annotations
- **Batch Processing**: Process entire directory structures of test data automatically
- **Command Line Interface**: Easy-to-use CLI for all analysis functions

## Installation

```console
  git clone https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis
  cd Fishing_Line_Material_Properties_Analysis
  poetry install
```

## Usage

### Single File Analysis

```console
  poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/group_1/5in/test--line-crimp-21--0.csv
```

**Output:** `File: data/group_1/5in/test--line-crimp-21--0.csv | Force: 45.23N | Modulus: 2.45MPa | Yield: 1.85MPa | KE: 0.0234J | Velocity: 1.03m/s | Length: 127.0mm | Diameter: 21mm`

### Multi-Sample Analysis

```console
  poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/group_1/5in/*.csv --plot-type multi
```

**Output:** `Multi-sample | Samples: 10 | Avg KE: 0.0245±0.0034J | Avg Velocity: 1.05±0.15m/s | Avg Force: 46.12±3.45N`

### Efficient Batch Processing

**Generate single plots for all trials:**

```console
  poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/group_*/*in/test--line-crimp-*
```

**Generate multi-trace plots for each group/length combination:**

```console
  find data -name "*in" -type d | while read dir; do echo "Processing $dir..."; poetry run Fishing_Line_Material_Properties_Analysis analyze -i $dir/test--line-crimp-* --plot-type multi; done
```

### Alternative Batch Command

```console
  poetry run Fishing_Line_Material_Properties_Analysis batch -d data --summary
```

## Output

- **Plots**: Organized in `out/group_X/length/` structure with stress-strain curves
- **Console**: Material properties and statistics for each analysis
- **CSV Files**: Automatically generated data exports
  - `individual_results.csv`: Every single test result with material properties
  - `multi_run_averages.csv`: Group/length averages with standard deviations (multi-runs only)
- **Reports**: Summary statistics (with `--summary` flag)

## Data Format

Expected CSV format:

```
"Time","Force","Stroke"
"sec","N","mm"
"0","0.002384186","0.0001"
"0.01","0.0055631","0.002333333"
...
```

## Parameters

- `--plot-type`: `single` (default) or `multi`
- `--x-param`, `--y-param`: Time, Force, Stroke, Stress, Strain
- `-o, --output`: Output directory (default: `out`)

## Citation

If you use this software in your research, please cite:

### Software

```bibtex
@software{matthew_nakamura_2025_15693814,
	author = {Matthew Nakamura},
	doi = {10.5281/zenodo.15693814},
	month = jun,
	publisher = {Zenodo},
	swhid = {swh:1:dir:9774416bfd0a3b64c546eeb74198f6abab0f55a4 ;origin=https://doi.org/10.5281/zenodo.15693813;vi sit=swh:1:snp:6196b6c9398e5737fef543af6732644c54c9 b97a;anchor=swh:1:rel:629adf510f09c35bc02be5156b08 598c85588ba7;path=nanosystemslab- Fishing\_Line\_Material\_Properties\_Analysis-da1d584},
	title = {nanosystemslab/Fishing\_Line\_Material\_Properties\_An alysis: v1.0.0 - Initial Release},
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

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the [GPL 3.0 license][license]. This project was generated from [@nanosystemslab]'s [Nanosystems Lab Python Cookiecutter] template.

[@nanosystemslab]: https://github.com/nanosystemslab
[nanosystems lab python cookiecutter]: https://github.com/nanosystemslab/cookiecutter-nanosystemslab
[file an issue]: https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis/issues
[contributor guide]: https://github.com/nanosystemslab/Fishing_Line_Material_Properties_Analysis/blob/main/CONTRIBUTING.md
[command-line reference]: https://Fishing_Line_Material_Properties_Analysis.readthedocs.io/en/latest/usage.html
