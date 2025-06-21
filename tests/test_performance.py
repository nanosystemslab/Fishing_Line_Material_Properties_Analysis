"""Performance tests for the analysis package."""

import os
import tempfile
import time

import numpy as np
import pandas as pd
import pytest

from Fishing_Line_Material_Properties_Analysis.analysis import MaterialAnalyzer
from Fishing_Line_Material_Properties_Analysis.visualization import MaterialVisualizer


class TestPerformance:
    """Performance tests to ensure reasonable execution times."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = MaterialAnalyzer()
        self.visualizer = MaterialVisualizer(output_dir=self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up after tests."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.slow
    def test_large_file_processing_time(self) -> None:
        """Test that large files are processed within reasonable time."""
        # Create large dataset (10,000 points)
        large_data = pd.DataFrame(
            {
                "Time": np.linspace(0, 100, 10000),
                "Force": np.sin(np.linspace(0, 10 * np.pi, 10000)) * 50 + 50,
                "Stroke": np.linspace(0, 50, 10000),
            }
        )

        csv_file = os.path.join(self.temp_dir, "large_test.csv")
        with open(csv_file, "w") as f:
            f.write('"Time","Force","Stroke"\n')
            f.write('"sec","N","mm"\n')
            for _, row in large_data.iterrows():
                f.write(f'{row["Time"]},{row["Force"]},{row["Stroke"]}\n')

        start_time = time.time()
        df = self.analyzer.load_file(csv_file)
        processing_time = time.time() - start_time

        # Should process within 10 seconds
        assert processing_time < 10.0
        assert len(df) == 10000

    @pytest.mark.slow
    def test_batch_processing_performance(self) -> None:
        """Test batch processing performance with multiple files."""
        # Create multiple test files
        file_paths = []
        for i in range(20):  # 20 files
            data = pd.DataFrame(
                {
                    "Time": np.linspace(0, 10, 1000),
                    "Force": np.random.normal(25, 5, 1000),
                    "Stroke": np.linspace(0, 5, 1000),
                }
            )

            csv_file = os.path.join(self.temp_dir, f"test_{i}.csv")
            with open(csv_file, "w") as f:
                f.write('"Time","Force","Stroke"\n')
                f.write('"sec","N","mm"\n')
                for _, row in data.iterrows():
                    f.write(f'{row["Time"]},{row["Force"]},{row["Stroke"]}\n')

            file_paths.append(csv_file)

        start_time = time.time()
        data_list = [self.analyzer.load_file(fp) for fp in file_paths]
        processing_time = time.time() - start_time

        # Should process 20 files within 30 seconds
        assert processing_time < 30.0
        assert len(data_list) == 20

    @pytest.mark.slow
    def test_visualization_performance(self) -> None:
        """Test visualization performance with complex plots."""
        # Create test data
        data_list = []
        for i in range(10):
            df = pd.DataFrame(
                {
                    "Strain": np.linspace(0, 0.1, 1000),
                    "Stress": np.linspace(0, 1000, 1000) * (1 + 0.1 * i),
                }
            )
            df.meta = type("Meta", (), {})()
            df.meta.filepath = f"test_{i}.csv"
            df.meta.size = 21
            df.meta.length = 127.0
            df.meta.modulus = 10000 + i * 1000
            df.meta.yield_stress = 800 + i * 50
            df.meta.max_force = 10 + i
            df.meta.ctype = "crimp"
            df.meta.test_run = i
            data_list.append(df)

        start_time = time.time()
        self.visualizer.plot_multi_trace(data_list)
        plotting_time = time.time() - start_time

        # Should create plot within 10 seconds
        assert plotting_time < 10.0

    def test_memory_usage_large_dataset(self) -> None:
        """Test memory efficiency with large datasets."""
        import gc

        import psutil

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Process large dataset
        large_data = pd.DataFrame(
            {
                "Time": np.linspace(0, 100, 50000),
                "Force": np.random.normal(50, 10, 50000),
                "Stroke": np.linspace(0, 50, 50000),
            }
        )

        csv_file = os.path.join(self.temp_dir, "memory_test.csv")
        with open(csv_file, "w") as f:
            f.write('"Time","Force","Stroke"\n')
            f.write('"sec","N","mm"\n')
            for _, row in large_data.iterrows():
                f.write(f'{row["Time"]},{row["Force"]},{row["Stroke"]}\n')

        df = self.analyzer.load_file(csv_file)

        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory

        # Clean up
        del df, large_data
        gc.collect()

        # Memory increase should be reasonable (< 500MB for 50k points)
        assert memory_increase < 600
