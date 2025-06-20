"""Integration tests for the complete workflow."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from Fishing_Line_Material_Properties_Analysis.analysis import MaterialAnalyzer
from Fishing_Line_Material_Properties_Analysis.visualization import MaterialVisualizer


class TestIntegration:
    """Integration tests for complete workflows."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self._create_test_data()

    def teardown_method(self) -> None:
        """Clean up after tests."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_test_data(self) -> None:
        """Create realistic test data."""
        # Create directory structure
        for group in ["group_1", "group_2"]:
            for length in ["5in", "10in", "20in"]:
                group_dir = Path(self.temp_dir) / "data" / group / length
                group_dir.mkdir(parents=True, exist_ok=True)

                # Create multiple test files
                for i in range(5):
                    csv_file = group_dir / f"test--line-crimp-21--{i}.csv"

                    # Generate realistic tensile test data
                    time_data = [i * 0.01 for i in range(100)]
                    # Fixed the string comparison issue
                    group_factor = 1.1 if group == "group_2" else 1.0
                    force_data = [i * 0.1 * group_factor for i in range(50)] + [
                        5 - i * 0.05 for i in range(50)
                    ]
                    stroke_data = [i * 0.05 for i in range(100)]

                    with open(csv_file, "w") as f:
                        f.write('"Time","Force","Stroke"\n')
                        f.write('"sec","N","mm"\n')
                        for t, force, stroke in zip(
                            time_data, force_data, stroke_data, strict=False
                        ):
                            f.write(f"{t},{max(0, force)},{stroke}\n")

    def test_complete_workflow_single(self) -> None:
        """Test complete workflow with single file analysis."""
        analyzer = MaterialAnalyzer()
        visualizer = MaterialVisualizer(output_dir=self.temp_dir)

        # Get a test file
        test_file = list(Path(self.temp_dir).rglob("*.csv"))[0]

        # Load and analyze
        data = analyzer.load_file(str(test_file))

        # Verify data loading
        assert isinstance(data, pd.DataFrame)
        assert "Stress" in data.columns
        assert "Strain" in data.columns
        assert hasattr(data.meta, "modulus")

        # Create visualization
        visualizer.plot_single_trace(data)

        # Verify plot was created
        plot_files = list(Path(self.temp_dir).rglob("*.png"))
        assert len(plot_files) > 0

    def test_complete_workflow_multi(self) -> None:
        """Test complete workflow with multiple file analysis."""
        analyzer = MaterialAnalyzer()
        visualizer = MaterialVisualizer(output_dir=self.temp_dir)

        # Get multiple test files from same group/length
        test_files = list(
            (Path(self.temp_dir) / "data" / "group_1" / "5in").glob("*.csv")
        )

        # Load and analyze all files
        data_list = []
        for file_path in test_files[:3]:  # Use first 3 files
            data = analyzer.load_file(str(file_path))
            data_list.append(data)

        # Calculate summary statistics
        stats = analyzer.calculate_summary_stats(data_list)

        # Verify statistics
        assert stats["sample_count"] == 3
        assert "modulus_avg" in stats
        assert "modulus_std" in stats

        # Create multi-trace visualization
        visualizer.plot_multi_trace(data_list)

        # Verify plot was created
        plot_files = list(Path(self.temp_dir).rglob("*multi*.png"))
        assert len(plot_files) > 0

    def test_complete_workflow_batch(self) -> None:
        """Test complete batch processing workflow."""
        analyzer = MaterialAnalyzer()
        visualizer = MaterialVisualizer(output_dir=self.temp_dir)

        data_dir = Path(self.temp_dir) / "data"
        group_results = {}

        # Process each group directory (simulating batch command)
        for group_dir in data_dir.glob("group_*"):
            group_results[group_dir.name] = {}

            for length_dir in group_dir.glob("*in"):
                csv_files = list(length_dir.glob("*.csv"))

                if csv_files:
                    # Load all files for this group/length combination
                    data_list = [analyzer.load_file(str(f)) for f in csv_files]

                    # Calculate statistics
                    stats = analyzer.calculate_summary_stats(data_list)
                    group_results[group_dir.name][length_dir.name] = stats

                    # Create multi-trace plot
                    visualizer.plot_multi_trace(data_list)

        # Generate summary report
        analyzer.generate_summary_report(group_results, self.temp_dir)

        # Create summary plots
        visualizer.create_summary_plot(group_results, self.temp_dir)

        # Verify outputs
        summary_report = Path(self.temp_dir) / "summary_report.txt"
        assert summary_report.exists()

        summary_plots = list(Path(self.temp_dir).glob("summary_*.png"))
        assert len(summary_plots) > 0

    def test_error_handling_invalid_data(self) -> None:
        """Test error handling with invalid data."""
        analyzer = MaterialAnalyzer()

        # Create invalid CSV file
        invalid_csv = Path(self.temp_dir) / "invalid.csv"
        with open(invalid_csv, "w") as f:
            f.write("invalid,data,format\n1,2,3\n")

        # Should handle gracefully or raise appropriate exception
        with pytest.raises((ValueError, pd.errors.EmptyDataError)):
            analyzer.load_file(str(invalid_csv))

    def test_edge_case_empty_directory(self) -> None:
        """Test handling of empty directories."""
        # Create empty directory structure
        empty_dir = Path(self.temp_dir) / "empty" / "group_1" / "5in"
        empty_dir.mkdir(parents=True, exist_ok=True)

        # Should handle empty directory gracefully
        csv_files = list(empty_dir.glob("*.csv"))
        assert len(csv_files) == 0

    def test_edge_case_single_data_point(self) -> None:
        """Test handling of files with minimal data."""
        analyzer = MaterialAnalyzer()

        # Create CSV with minimal data
        minimal_csv = Path(self.temp_dir) / "minimal.csv"
        with open(minimal_csv, "w") as f:
            f.write('"Time","Force","Stroke"\n')
            f.write('"sec","N","mm"\n')
            f.write("0.0,0.0,0.0\n")
            f.write("0.1,1.0,0.1\n")

        # Should handle minimal data
        data = analyzer.load_file(str(minimal_csv))
        assert isinstance(data, pd.DataFrame)
        assert len(data) >= 1
