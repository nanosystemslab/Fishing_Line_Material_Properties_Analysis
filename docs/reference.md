# API Reference

This page provides detailed documentation for all modules, classes, and functions in the Fishing Line Material Properties Analysis package.

## Package Overview

```{eval-rst}
.. automodule:: Fishing_Line_Material_Properties_Analysis
   :members:
   :undoc-members:
   :show-inheritance:
```

### Package Structure

The Fishing Line Material Properties Analysis package consists of three main modules:

- **Analysis Module**: Core functionality for processing material test data
- **Visualization Module**: Plotting and data visualization capabilities  
- **Main Module**: Command-line interface and application entry point

### Quick Start

```python
from Fishing_Line_Material_Properties_Analysis.analysis import MaterialAnalyzer
from Fishing_Line_Material_Properties_Analysis.visualization import MaterialVisualizer

# Initialize analyzer and visualizer
analyzer = MaterialAnalyzer()
visualizer = MaterialVisualizer(output_dir='results')

# Load and analyze data
data = analyzer.load_file('test_data.csv')
visualizer.plot_single_trace(data)
```

---

## Analysis Module

The analysis module contains the core functionality for processing material test data and calculating material properties.

```{eval-rst}
.. automodule:: Fishing_Line_Material_Properties_Analysis.analysis
   :members:
   :undoc-members:
   :show-inheritance:
```

### Usage Examples

```python
from Fishing_Line_Material_Properties_Analysis.analysis import MaterialAnalyzer

# Initialize analyzer
analyzer = MaterialAnalyzer()

# Load test data
data = analyzer.load_file('tensile_test.csv')

# Calculate summary statistics for multiple tests
test_data = [data1, data2, data3]
stats = analyzer.calculate_summary_stats(test_data)

# Generate summary report
analyzer.generate_summary_report(group_results, 'output_directory')
```

---

## Visualization Module

The visualization module provides plotting and data visualization capabilities for material property analysis.

```{eval-rst}
.. automodule:: Fishing_Line_Material_Properties_Analysis.visualization
   :members:
   :undoc-members:
   :show-inheritance:
```

### Usage Examples

```python
from Fishing_Line_Material_Properties_Analysis.visualization import MaterialVisualizer

# Initialize visualizer
visualizer = MaterialVisualizer(output_dir='plots')

# Plot single stress-strain curve
visualizer.plot_single_trace(data, x_param='Strain', y_param='Stress')

# Plot multiple traces for comparison
visualizer.plot_multi_trace([data1, data2, data3], title_suffix='Comparison')

# Create summary plots
visualizer.create_summary_plot(group_results, 'output_directory')

# Plot output data
visualizer.plot_output_data('results.csv', x_param='D', y_param='KE')
```

---

## Command Line Interface

The main module provides the command-line interface for the application.

```{eval-rst}
.. automodule:: Fishing_Line_Material_Properties_Analysis.__main__
   :members:
   :undoc-members:
   :show-inheritance:
```

### Command Line Usage

The package provides several command-line commands:

#### Analyze Command

```bash
poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/test.csv
poetry run Fishing_Line_Material_Properties_Analysis analyze -i data/*.csv --plot-type multi
```

#### Batch Command

```bash
poetry run Fishing_Line_Material_Properties_Analysis batch -d data --summary
```

#### Visualize Command

```bash
poetry run Fishing_Line_Material_Properties_Analysis visualize -i results.csv
```

### CLI Functions

The following functions handle the command-line interface:

- `main()`: Application entry point
- `parse_command_line()`: Parse command line arguments
- `handle_analyze_command()`: Handle analysis operations
- `handle_batch_command()`: Handle batch processing
- `handle_visualize_command()`: Handle visualization operations
- `setup_logging()`: Configure logging system
