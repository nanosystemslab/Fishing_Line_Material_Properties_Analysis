"""Test cases for the analysis module."""

import os
import tempfile
import types
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from Fishing_Line_Material_Properties_Analysis.analysis import MaterialAnalyzer


class TestMaterialAnalyzer:
    """Test cases for MaterialAnalyzer class."""

    def setup_method(self) -> None:
        """Set up test fixtures before each test method."""
        self.analyzer = MaterialAnalyzer()

        # Create sample test data
        self.sample_data = pd.DataFrame(
            {
                "Time": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
                "Force": [0.0, 1.0, 2.0, 3.0, 2.5, 1.0],
                "Stroke": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
            }
        )

        # Create temporary CSV file
        self.temp_dir = tempfile.mkdtemp()
        self.temp_csv = os.path.join(self.temp_dir, "test--line-crimp-21--0.csv")

        # Write CSV with proper header format
        with open(self.temp_csv, "w") as f:
            f.write('"Time","Force","Stroke"\n')
            f.write('"sec","N","mm"\n')
            for _, row in self.sample_data.iterrows():
                f.write(f'{row["Time"]},{row["Force"]},{row["Stroke"]}\n')

    def teardown_method(self) -> None:
        """Clean up after each test method."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self) -> None:
        """Test MaterialAnalyzer initialization."""
        analyzer = MaterialAnalyzer()
        assert hasattr(analyzer, "log")

    def test_load_file_success(self) -> None:
        """Test successful file loading."""
        # Create CSV in data/group_1/5in/ structure for proper metadata parsing
        group_dir = os.path.join(self.temp_dir, "data", "group_1", "5in")
        os.makedirs(group_dir, exist_ok=True)
        csv_path = os.path.join(group_dir, "test--line-crimp-21--0.csv")

        with open(csv_path, "w") as f:
            f.write('"Time","Force","Stroke"\n')
            f.write('"sec","N","mm"\n')
            for _, row in self.sample_data.iterrows():
                f.write(f'{row["Time"]},{row["Force"]},{row["Stroke"]}\n')

        df = self.analyzer.load_file(csv_path)

        assert isinstance(df, pd.DataFrame)
        assert "Stress" in df.columns
        assert "Strain" in df.columns
        assert hasattr(df, "meta")
        assert hasattr(df.meta, "size")
        assert hasattr(df.meta, "length")
        assert hasattr(df.meta, "modulus")

    def test_load_file_invalid_format(self) -> None:
        """Test loading file with invalid format."""
        txt_file = os.path.join(self.temp_dir, "test.txt")
        with open(txt_file, "w") as f:
            f.write("test content")

        with pytest.raises(ValueError, match="File must be CSV format"):
            self.analyzer.load_file(txt_file)

    def test_load_file_unquoted_header(self) -> None:
        """Test loading file with unquoted extra header."""
        csv_file = os.path.join(self.temp_dir, "test_unquoted.csv")
        with open(csv_file, "w") as f:
            f.write("1 _ 1,,\n")  # Unquoted header like your problematic files
            f.write("Time,Force,Stroke\n")
            f.write("sec,N,mm\n")
            f.write("0.0,0.0,0.0\n")
            f.write("0.1,1.0,0.1\n")
            f.write("0.2,2.0,0.2\n")

        df = self.analyzer.load_file(csv_file)
        assert isinstance(df, pd.DataFrame)
        assert "Force" in df.columns
        assert "Stroke" in df.columns
        assert len(df) > 0

    def test_load_file_mixed_header_formats(self) -> None:
        """Test detection logic with mixed quote formats."""
        # Test case where first line has no quotes but second line does
        csv_file = os.path.join(self.temp_dir, "test_mixed.csv")
        with open(csv_file, "w") as f:
            f.write("1 _ 1,,\n")  # No quotes
            f.write('"Time","Force","Stroke"\n')  # With quotes
            f.write('"sec","N","mm"\n')
            f.write("0.0,0.0,0.0\n")

        df = self.analyzer.load_file(csv_file)
        assert isinstance(df, pd.DataFrame)
        assert "Force" in df.columns
        assert "Stroke" in df.columns

    def test_parse_metadata_standard_format(self) -> None:
        """Test metadata parsing with standard filename format."""
        filepath = "data/group_1/5in/test--line-crimp-21--0.csv"
        metadata = self.analyzer._parse_metadata(filepath)

        assert metadata.size == 21
        assert metadata.ctype == "crimp"
        assert metadata.test_run == 0
        assert metadata.length == 127.0  # 5 inches * 25.4 mm/inch

    def test_parse_metadata_fallback(self) -> None:
        """Test metadata parsing with non-standard format."""
        filepath = "data/test.csv"
        metadata = self.analyzer._parse_metadata(filepath)

        assert metadata.size == 21  # default
        assert metadata.ctype == "crimp"  # default
        assert metadata.test_run == 0
        assert metadata.length == 254.0  # default 10 inches

    def test_parse_length_various_formats(self) -> None:
        """Test length parsing from directory paths."""
        # Test 5in
        dname_parts = ["data", "group_1", "5in"]
        length = self.analyzer._parse_length(dname_parts, 0)
        assert length == 127.0

        # Test 10in
        dname_parts = ["data", "group_1", "10in"]
        length = self.analyzer._parse_length(dname_parts, 0)
        assert length == 254.0

        # Test 20in
        dname_parts = ["data", "group_1", "20in"]
        length = self.analyzer._parse_length(dname_parts, 0)
        assert length == 508.0

        # Test fallback
        dname_parts = ["data", "group_1", "unknown"]
        length = self.analyzer._parse_length(dname_parts, 0)
        assert length == 254.0

    def test_calculate_material_properties(self) -> None:
        """Test material properties calculation."""
        df = self.sample_data.copy()
        df.meta = types.SimpleNamespace()
        df.meta.size = 21
        df.meta.length = 127.0

        # Add required columns
        area = np.pi * 0.25 * (21 * 10**-3) ** 2
        df["Stress"] = df["Force"] / area
        df["Strain"] = df["Stroke"] / 127.0

        self.analyzer._calculate_material_properties(df)

        assert hasattr(df.meta, "modulus")
        assert hasattr(df.meta, "yield_stress")
        assert hasattr(df.meta, "max_force")
        assert hasattr(df.meta, "kinetic_energy")
        assert hasattr(df.meta, "velocity")

    @patch("Fishing_Line_Material_Properties_Analysis.analysis.KneeLocator")
    def test_find_yield_point_knee_detection(self, mock_knee: Any) -> None:
        """Test yield point detection using knee method."""
        # Setup mock
        mock_knee_instance = MagicMock()
        mock_knee_instance.knee = 0.1
        mock_knee.return_value = mock_knee_instance

        df = self.sample_data.copy()
        df["Stress"] = df["Force"] * 1000
        df["Strain"] = df["Stroke"] * 0.01

        result = self.analyzer._find_yield_point(df, "Stress", "Strain")

        assert isinstance(result, list)
        assert len(result) > 0

    def test_find_yield_point_fallback(self) -> None:
        """Test yield point detection fallback methods."""
        df = self.sample_data.copy()
        df["Stress"] = df["Force"] * 1000
        df["Strain"] = df["Stroke"] * 0.01

        # Test with data that should trigger fallback
        with patch(
            "Fishing_Line_Material_Properties_Analysis.analysis.KneeLocator",
            side_effect=Exception("Mock error"),
        ):
            result = self.analyzer._find_yield_point(df, "Stress", "Strain")

        assert isinstance(result, list)
        assert len(result) > 0

    def test_calculate_summary_stats(self) -> None:
        """Test summary statistics calculation."""
        # Create test data with metadata
        data_list = []
        for i in range(3):
            df = self.sample_data.copy()
            df.meta = types.SimpleNamespace()
            df.meta.modulus = 1000 + i * 100
            df.meta.yield_stress = 500 + i * 50
            df.meta.max_force = 10 + i
            df.meta.length = 127.0
            df.meta.size = 21
            df.meta.ctype = "crimp"
            data_list.append(df)

        stats = self.analyzer.calculate_summary_stats(data_list)

        assert stats["sample_count"] == 3
        assert "modulus_avg" in stats
        assert "modulus_std" in stats
        assert "yield_stress_avg" in stats
        assert "max_force_avg" in stats
        assert stats["length"] == 127.0

    def test_calculate_summary_stats_empty(self) -> None:
        """Test summary statistics with empty data."""
        stats = self.analyzer.calculate_summary_stats([])
        assert stats == {}

    def test_generate_summary_report(self) -> None:
        """Test summary report generation."""
        group_results = {
            "group_1": {
                "5in": {
                    "sample_count": 10,
                    "modulus_avg": 1000,
                    "modulus_std": 100,
                    "yield_stress_avg": 500,
                    "yield_stress_std": 50,
                    "max_force_avg": 25,
                    "max_force_std": 5,
                }
            }
        }

        output_dir = self.temp_dir
        self.analyzer.generate_summary_report(group_results, output_dir)

        report_path = Path(output_dir) / "summary_report.txt"
        assert report_path.exists()

        with open(report_path) as f:
            content = f.read()
            assert "Fishing Line Material Properties Analysis Summary" in content
            assert "group_1" in content
            assert "5in" in content
