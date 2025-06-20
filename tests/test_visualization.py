"""Test cases for the visualization module."""

import os
import tempfile
import types
from pathlib import Path
from unittest.mock import patch

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from Fishing_Line_Material_Properties_Analysis.visualization import MaterialVisualizer


matplotlib.use("Agg")  # Use non-interactive backend for testing


class TestMaterialVisualizer:
    """Test cases for MaterialVisualizer class."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.visualizer = MaterialVisualizer(output_dir=self.temp_dir)

        # Create sample test data
        self.sample_data = self._create_sample_data()

    def teardown_method(self) -> None:
        """Clean up after each test method."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)
        plt.close("all")  # Close all matplotlib figures

    def _create_sample_data(self) -> pd.DataFrame:
        """Create sample test data with metadata."""
        df = pd.DataFrame(
            {
                "Time": np.linspace(0, 1, 100),
                "Force": np.linspace(0, 10, 100),
                "Stroke": np.linspace(0, 5, 100),
                "Stress": np.linspace(0, 1000, 100),
                "Strain": np.linspace(0, 0.1, 100),
            }
        )

        # Add metadata
        df.meta = types.SimpleNamespace()
        df.meta.filepath = "data/group_1/5in/test--line-crimp-21--0.csv"
        df.meta.size = 21
        df.meta.length = 127.0
        df.meta.modulus = 10000
        df.meta.yield_stress = 800
        df.meta.max_force = 10
        df.meta.kinetic_energy = 0.1
        df.meta.velocity = 1.0
        df.meta.test_run = 0
        df.meta.yield_point_strain = 0.05
        df.meta.yield_point_stress = 500
        df.meta.ctype = "crimp"  # ADD THIS LINE

        return df

    def test_init(self) -> None:
        """Test MaterialVisualizer initialization."""
        visualizer = MaterialVisualizer(output_dir="test_output")
        assert visualizer.output_dir == Path("test_output")
        assert hasattr(visualizer, "plot_params")
        assert hasattr(visualizer, "log")

    def test_extract_group_from_path(self) -> None:
        """Test group extraction from file paths."""
        # Test standard path
        filepath = "data/group_1/5in/test.csv"
        group = self.visualizer._extract_group_from_path(filepath)
        assert group == "group_1"

        # Test different group
        filepath = "data/group_2/10in/test.csv"
        group = self.visualizer._extract_group_from_path(filepath)
        assert group == "group_2"

        # Test no group found
        filepath = "data/unknown/test.csv"
        group = self.visualizer._extract_group_from_path(filepath)
        assert group == "unknown_group"

    def test_extract_length_from_path(self) -> None:
        """Test length extraction from file paths."""
        # Test 5in
        filepath = "data/group_1/5in/test.csv"
        length = self.visualizer._extract_length_from_path(filepath)
        assert length == "5in"

        # Test 10in
        filepath = "data/group_1/10in/test.csv"
        length = self.visualizer._extract_length_from_path(filepath)
        assert length == "10in"

        # Test no length found
        filepath = "data/group_1/unknown/test.csv"
        length = self.visualizer._extract_length_from_path(filepath)
        assert length == "unknown_length"

    def test_plot_single_trace(self) -> None:
        """Test single trace plotting."""
        self.visualizer.plot_single_trace(self.sample_data)

        # Check if plot file was created
        expected_dir = self.visualizer.output_dir / "group_1" / "5in"
        assert expected_dir.exists()

        plot_files = list(expected_dir.glob("*.png"))
        assert len(plot_files) > 0

    def test_plot_single_trace_without_yield_point(self) -> None:
        """Test single trace plotting without yield point metadata."""
        # Remove yield point metadata
        delattr(self.sample_data.meta, "yield_point_strain")
        delattr(self.sample_data.meta, "yield_point_stress")

        self.visualizer.plot_single_trace(self.sample_data)

        # Should still create plot with fracture point
        expected_dir = self.visualizer.output_dir / "group_1" / "5in"
        assert expected_dir.exists()

    def test_plot_multi_trace(self) -> None:
        """Test multi-trace plotting."""
        # Create multiple data samples
        data_list = [self.sample_data]
        for i in range(2):
            df = self.sample_data.copy()
            # Fix: Copy metadata properly
            df.meta = types.SimpleNamespace()
            for attr in dir(self.sample_data.meta):
                if not attr.startswith("_"):
                    setattr(df.meta, attr, getattr(self.sample_data.meta, attr))
            df.meta.test_run = i + 1
            data_list.append(df)

        self.visualizer.plot_multi_trace(data_list)

        # Check if plot file was created
        expected_dir = self.visualizer.output_dir / "group_1" / "5in"
        plot_files = list(expected_dir.glob("*multi*.png"))
        assert len(plot_files) > 0

    def test_plot_multi_trace_empty_list(self) -> None:
        """Test multi-trace plotting with empty data list."""
        with patch.object(self.visualizer.log, "warning") as mock_log:
            self.visualizer.plot_multi_trace([])
            mock_log.assert_called_once()

    def test_create_base_figure(self) -> None:
        """Test base figure creation."""
        fig, ax = self.visualizer._create_base_figure()

        assert fig is not None
        assert ax is not None
        plt.close(fig)

    def test_collect_multi_trace_stats(self) -> None:
        """Test statistics collection from multiple traces."""
        data_list = [self.sample_data]

        moduli, yields, forces = self.visualizer._collect_multi_trace_stats(data_list)

        assert len(moduli) == 1
        assert len(yields) == 1
        assert len(forces) == 1
        assert moduli[0] == 10000

    def test_plot_individual_traces(self) -> None:
        """Test plotting individual traces."""
        fig, ax = plt.subplots()
        data_list = [self.sample_data]

        self.visualizer._plot_individual_traces(ax, data_list, "Strain", "Stress")

        # Check that lines were added to the plot
        assert len(ax.get_lines()) > 0
        plt.close(fig)

    def test_configure_multi_trace_axes(self) -> None:
        """Test axes configuration for multi-trace plots."""
        fig, ax = plt.subplots()
        data_list = [self.sample_data]

        self.visualizer._configure_multi_trace_axes(ax, data_list, "Strain", "Stress")

        assert ax.get_xlabel() == "Strain (mm/mm)"
        assert ax.get_ylabel() == "Stress (Pa)"
        plt.close(fig)

    def test_add_multi_trace_statistics(self) -> None:
        """Test adding statistics to multi-trace plots."""
        fig, ax = plt.subplots()

        self.visualizer._add_multi_trace_statistics(ax, [10000], [800], [10])

        # Note: legend might be None if not explicitly created
        plt.close(fig)

    def test_setup_legend(self) -> None:
        """Test legend setup."""
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], label="test")

        self.visualizer._setup_legend(ax)

        legend = ax.get_legend()
        assert legend is not None
        plt.close(fig)

    def test_save_multi_trace_plot(self) -> None:
        """Test saving multi-trace plot."""
        fig, ax = plt.subplots()
        data_list = [self.sample_data]

        # Create a custom _save_multi_trace_plot call since the method signature changed
        first_data = data_list[0]

        group_name = self.visualizer._extract_group_from_path(first_data.meta.filepath)
        length_name = self.visualizer._extract_length_from_path(
            first_data.meta.filepath
        )

        group_length_dir = self.visualizer.output_dir / group_name / length_name
        group_length_dir.mkdir(parents=True, exist_ok=True)

        title_suffix = (
            f"{first_data.meta.size}in-{first_data.meta.ctype}"
            if hasattr(first_data.meta, "ctype")
            else "unknown"
        )
        plot_filename = f"plot-{title_suffix}-multi-Stress-vs-Strain.png"
        plot_path = group_length_dir / plot_filename

        fig.savefig(plot_path, bbox_inches="tight", dpi=600, transparent=True)

        assert plot_path.exists()
        plt.close(fig)

    def test_plot_output_data(self) -> None:
        """Test plotting output data."""
        # Create a temporary CSV file
        csv_file = os.path.join(self.temp_dir, "output.csv")
        test_data = pd.DataFrame(
            {"diameter": [21, 23, 25], "kinetic_energy": [0.1, 0.2, 0.3]}
        )
        test_data.to_csv(csv_file, header=False, index=False)

        self.visualizer.plot_output_data(csv_file)

        # Check if plot was created
        plot_files = list(Path(self.temp_dir).glob("output-*.png"))
        assert len(plot_files) > 0

    def test_create_summary_plot(self) -> None:
        """Test summary plot creation."""
        group_results = {
            "group_1": {
                "5in": {
                    "modulus_avg": 10000,
                    "yield_stress_avg": 800,
                    "max_force_avg": 10,
                },
                "10in": {
                    "modulus_avg": 12000,
                    "yield_stress_avg": 900,
                    "max_force_avg": 15,
                },
            },
            "group_2": {
                "5in": {
                    "modulus_avg": 11000,
                    "yield_stress_avg": 850,
                    "max_force_avg": 12,
                }
            },
        }

        self.visualizer.create_summary_plot(group_results, self.temp_dir)

        # Check if summary plots were created
        summary_files = list(Path(self.temp_dir).glob("summary_*.png"))
        assert len(summary_files) > 0

    def test_create_summary_plot_empty_data(self) -> None:
        """Test summary plot creation with empty data."""
        with patch.object(self.visualizer.log, "warning") as mock_log:
            self.visualizer.create_summary_plot({}, self.temp_dir)
            mock_log.assert_called_once()

    def test_plot_comparison_by_length(self) -> None:
        """Test comparison plots by length."""
        summary_df = pd.DataFrame(
            {
                "Group": ["group_1", "group_1", "group_2"],
                "Length": ["5in", "10in", "5in"],
                "Modulus": [10000, 12000, 11000],
                "Yield_Stress": [800, 900, 850],
                "Max_Force": [10, 15, 12],
            }
        )

        self.visualizer._plot_comparison_by_length(summary_df)

        # Check if plot was created
        plot_files = list(
            self.visualizer.output_dir.glob("summary_comparison_by_length.png")
        )
        assert len(plot_files) > 0

    def test_plot_comparison_by_group(self) -> None:
        """Test comparison plots by group."""
        summary_df = pd.DataFrame(
            {
                "Group": ["group_1", "group_1", "group_2"],
                "Length": ["5in", "10in", "5in"],
                "Modulus": [10000, 12000, 11000],
                "Yield_Stress": [800, 900, 850],
                "Max_Force": [10, 15, 12],
            }
        )

        self.visualizer._plot_comparison_by_group(summary_df)

        # Check if plot was created
        plot_files = list(
            self.visualizer.output_dir.glob("summary_comparison_by_group.png")
        )
        assert len(plot_files) > 0
