"""Test cases for edge cases and error conditions."""

import os
import tempfile
import types
from unittest.mock import MagicMock
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from Fishing_Line_Material_Properties_Analysis.visualization import MaterialVisualizer


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.visualizer = MaterialVisualizer(output_dir=self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up after tests."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_analyzer_with_nan_values(self) -> None:
        """Test analyzer handling of NaN values in data."""
        # Create CSV with NaN values
        csv_file = os.path.join(self.temp_dir, "test_nan.csv")
        with open(csv_file, "w") as f:
            f.write('"Time","Force","Stroke"\n')
            f.write('"sec","N","mm"\n')
            f.write("0.0,0.0,0.0\n")
            f.write("0.1,nan,0.1\n")
            f.write("0.2,2.0,0.2\n")

        # Should handle NaN values gracefully
        df = self.analyzer.load_file(csv_file)
        assert isinstance(df, pd.DataFrame)

    def test_analyzer_with_zero_area(self) -> None:
        """Test analyzer with zero or very small diameter."""
        csv_file = os.path.join(self.temp_dir, "test_zero.csv")
        with open(csv_file, "w") as f:
            f.write('"Time","Force","Stroke"\n')
            f.write('"sec","N","mm"\n')
            f.write("0.0,0.0,0.0\n")
            f.write("0.1,1.0,0.1\n")

        # Mock metadata to have zero size
        with patch.object(self.analyzer, "_parse_metadata") as mock_meta:
            metadata = types.SimpleNamespace()
            metadata.filepath = csv_file
            metadata.size = 0  # Zero diameter
            metadata.length = 127.0
            metadata.ctype = "crimp"
            metadata.test_run = 0
            mock_meta.return_value = metadata

            # Should handle zero area case
            df = self.analyzer.load_file(csv_file)
            assert isinstance(df, pd.DataFrame)

    def test_analyzer_with_negative_values(self) -> None:
        """Test analyzer with negative force/stroke values."""
        csv_file = os.path.join(self.temp_dir, "test_negative.csv")
        with open(csv_file, "w") as f:
            f.write('"Time","Force","Stroke"\n')
            f.write('"sec","N","mm"\n')
            f.write("0.0,-1.0,-0.1\n")
            f.write("0.1,1.0,0.1\n")
            f.write("0.2,2.0,0.2\n")

        df = self.analyzer.load_file(csv_file)
        assert isinstance(df, pd.DataFrame)
        # Stress and strain should be calculated relative to minimum values
        assert df["Stress"].min() >= 0
        assert df["Strain"].min() >= 0

    def test_yield_point_detection_edge_cases(self) -> None:
        """Test yield point detection with edge case data."""
        # Test with very short data
        short_data = pd.DataFrame({"Stress": [1, 2], "Strain": [0.1, 0.2]})

        result = self.analyzer._find_yield_point(short_data, "Stress", "Strain")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_yield_point_detection_constant_stress(self) -> None:
        """Test yield point detection with constant stress values."""
        constant_data = pd.DataFrame(
            {"Stress": [100] * 50, "Strain": np.linspace(0, 0.1, 50)}
        )

        result = self.analyzer._find_yield_point(constant_data, "Stress", "Strain")
        assert isinstance(result, list)
        assert len(result) > 0

    def test_visualization_with_missing_metadata(self) -> None:
        """Test visualization when metadata is missing."""
        df = pd.DataFrame(
            {"Strain": np.linspace(0, 0.1, 100), "Stress": np.linspace(0, 1000, 100)}
        )

        # Create minimal metadata
        df.meta = types.SimpleNamespace()
        df.meta.filepath = "test.csv"

        # Should handle missing metadata gracefully
        self.visualizer.plot_single_trace(df)

    def test_visualization_with_empty_data(self) -> None:
        """Test visualization with empty DataFrame."""
        empty_df = pd.DataFrame(columns=["Strain", "Stress"])
        empty_df.meta = types.SimpleNamespace()
        empty_df.meta.filepath = "empty.csv"

        # Should handle empty data gracefully
        with pytest.raises((ValueError, pd.errors.EmptyDataError)):
            self.visualizer.plot_single_trace(empty_df)

    def test_parse_metadata_malformed_filename(self) -> None:
        """Test metadata parsing with malformed filenames."""
        # Test various malformed filename patterns
        malformed_files = [
            "test.csv",
            "test--line.csv",
            "test--line--crimp.csv",
            "completely_different_format.csv",
        ]

        for filename in malformed_files:
            filepath = f"data/group_1/5in/{filename}"
            metadata = self.analyzer._parse_metadata(filepath)

            # Should provide fallback values
            assert hasattr(metadata, "size")
            assert hasattr(metadata, "ctype")
            assert hasattr(metadata, "test_run")
            assert hasattr(metadata, "length")

    def test_summary_stats_with_missing_attributes(self) -> None:
        """Test summary statistics when some data lacks certain attributes."""
        data_list = []

        for i in range(3):
            df = pd.DataFrame({"Force": [1, 2, 3]})
            df.meta = types.SimpleNamespace()

            # Only some data has certain attributes
            if i == 0:
                df.meta.modulus = 1000
                df.meta.yield_stress = 500
            elif i == 1:
                df.meta.modulus = 1100
                # Missing yield_stress
            else:
                # Missing both modulus and yield_stress
                df.meta.max_force = 10

            data_list.append(df)

        stats = self.analyzer.calculate_summary_stats(data_list)
        assert stats["sample_count"] == 3

    def test_file_path_edge_cases(self) -> None:
        """Test file path parsing with various edge cases."""
        edge_case_paths = [
            "/absolute/path/to/file.csv",
            "relative/path/file.csv",
            "file.csv",
            "path/with spaces/file.csv",
            "path/with-dashes/file.csv",
            "path/with_underscores/file.csv",
        ]

        for path in edge_case_paths:
            group = self.visualizer._extract_group_from_path(path)
            length = self.visualizer._extract_length_from_path(path)

            # Should return fallback values for unknown patterns
            assert isinstance(group, str)
            assert isinstance(length, str)

    def test_integration_scipy_import_fallback(self) -> None:
        """Test fallback when scipy.integrate.trapezoid is not available."""
        # This tests the import fallback in analysis.py
        import sys
        from unittest.mock import patch

        # Mock scipy.integrate to simulate older version
        with patch.dict("sys.modules", {"scipy.integrate": MagicMock()}):
            # Remove trapezoid to simulate older scipy
            if hasattr(sys.modules["scipy.integrate"], "trapezoid"):
                delattr(sys.modules["scipy.integrate"], "trapezoid")

            # Should fall back to trapz
            from Fishing_Line_Material_Properties_Analysis.analysis import (
                MaterialAnalyzer,
            )

            analyzer = MaterialAnalyzer()
            assert analyzer is not None

    def test_large_dataset_performance(self) -> None:
        """Test analyzer performance with large datasets."""
        # Create large dataset
        large_data = pd.DataFrame(
            {
                "Time": np.linspace(0, 100, 10000),
                "Force": np.random.normal(50, 10, 10000),
                "Stroke": np.linspace(0, 50, 10000),
            }
        )

        # Save to file
        csv_file = os.path.join(self.temp_dir, "large_test.csv")
        with open(csv_file, "w") as f:
            f.write('"Time","Force","Stroke"\n')
            f.write('"sec","N","mm"\n')
            for _, row in large_data.iterrows():
                f.write(f'{row["Time"]},{row["Force"]},{row["Stroke"]}\n')

        # Should handle large datasets without issues
        df = self.analyzer.load_file(csv_file)
        assert len(df) > 5000

    def test_unicode_and_special_characters(self) -> None:
        """Test handling of unicode and special characters in file paths."""
        # Test with unicode characters (if supported by filesystem)
        try:
            unicode_dir = os.path.join(self.temp_dir, "test_ñ_ü")
            os.makedirs(unicode_dir, exist_ok=True)

            csv_file = os.path.join(unicode_dir, "test.csv")
            with open(csv_file, "w") as f:
                f.write('"Time","Force","Stroke"\n')
                f.write('"sec","N","mm"\n')
                f.write("0.0,0.0,0.0\n")
                f.write("0.1,1.0,0.1\n")

            metadata = self.analyzer._parse_metadata(csv_file)
            assert metadata is not None

        except (UnicodeError, OSError):
            # Skip if filesystem doesn't support unicode
            pytest.skip("Filesystem doesn't support unicode characters")
