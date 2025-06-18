# Usage

This guide shows you how to use Fishing Line Material Properties Analysis to analyze tensile test data.

## Basic Usage

### Single File Analysis

Analyze a single CSV file containing tensile test data:

```bash
poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/test.csv
```

**Example output:**

```
File: data/group_1/5in/test--line-crimp-21--0.csv | Force: 45.23N | Modulus: 2.45MPa | Yield: 1.85MPa | KE: 0.0234J | Velocity: 1.03m/s | Length: 127.0mm | Diameter: 21mm
```

### Multi-Sample Analysis

Analyze multiple files and generate a combined plot:

```bash
poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/group_1/5in/*.csv --plot-type multi
```

**Example output:**

```
Multi-sample | Samples: 10 | Avg KE: 0.0245±0.0034J | Avg Velocity: 1.05±0.15m/s | Avg Force: 46.12±3.45N
```

## Batch Processing

### Single Plots for All Trials

Generate individual plots for all test files:

```bash
poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/group_*/*in/test--line-crimp-*
```

### Multi-Trace Plots by Group

Generate combined plots for each group/length combination:

```bash
find data -name "*in" -type d | while read dir; do
    echo "Processing $dir..."
    poetry run Fishing_Line_Material_Properties_Analysis analyze -i $dir/test--line-crimp-* --plot-type multi
done
```

### Batch Command

Use the dedicated batch processing command:

```bash
poetry run Fishing_Line_Material_Properties_Analysis batch -d data --summary
```

## Command Line Options

### Analysis Command

- `-i, --input`: Input file(s) or pattern
- `--plot-type`: Choose `single` (default) or `multi`
- `--x-param`: X-axis parameter (Time, Force, Stroke, Stress, Strain)
- `--y-param`: Y-axis parameter (Time, Force, Stroke, Stress, Strain)
- `-o, --output`: Output directory (default: `out`)

### Batch Command

- `-d, --directory`: Data directory to process
- `--summary`: Generate summary statistics

## Data Format Requirements

Your CSV files should have the following format:

```
"Time","Force","Stroke"
"sec","N","mm"
"0","0.002384186","0.0001"
"0.01","0.0055631","0.002333333"
...
```

## Output Files

The analysis generates several types of output:

### Plots

- Organized in `out/group_X/length/` directory structure
- Stress-strain curves with material property annotations
- Individual or multi-sample plots

### CSV Reports

- `individual_results.csv`: Every single test result with material properties
- `multi_run_averages.csv`: Group/length averages with standard deviations (multi-runs only)

### Console Output

- Material properties and statistics for each analysis
- Summary reports (with `--summary` flag)

## Examples

### Analyze a Single Test

```bash
poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/group_1/5in/test--line-crimp-21--0.csv
```

### Compare Multiple Groups

```bash
poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/group_*/5in/test--line-crimp-21--*.csv --plot-type multi
```

### Process All Data with Summary

```bash
poetry run Fishing_Line_Material_Properties_Analysis batch -d data --summary
```

## Material Properties Calculated

The software automatically calculates:

- **Modulus**: Young's modulus from the linear region of the stress-strain curve
- **Yield Stress**: Stress at which permanent deformation begins
- **Maximum Force**: Peak force during the test
- **Kinetic Energy**: Energy stored in the material
- **Velocity**: Calculated from kinetic energy and material properties
