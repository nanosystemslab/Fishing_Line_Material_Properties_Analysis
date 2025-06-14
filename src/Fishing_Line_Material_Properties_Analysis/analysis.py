"""Material analysis module for fishing line properties."""

import logging
import os
import types
from pathlib import Path
from typing import Dict
from typing import List

import numpy as np
import pandas as pd
from kneed import KneeLocator


try:
    from scipy.integrate import trapezoid as trapz
except ImportError:
    # Fallback for older scipy versions
    from scipy.integrate import trapz


class MaterialAnalyzer:
    """Analyzer for fishing line material properties."""

    def __init__(self):
        """Initialize the MaterialAnalyzer."""
        self.log = logging.getLogger(__name__)

    def load_file(self, filepath: str) -> pd.DataFrame:
        """Load material test data from CSV file.

        Args:
            filepath: Path to CSV file

        Returns:
            DataFrame with material test data and metadata
        """
        self.log.debug("Loading file: %s", filepath)

        if not filepath.endswith(".csv"):
            raise ValueError(f"File must be CSV format: {filepath}")

        # Read CSV file
        df = pd.read_csv(filepath, skiprows=1)
        df.drop(0, axis=0, inplace=True)

        # Parse metadata from filename and directory structure
        metadata = self._parse_metadata(filepath)

        # Convert data types
        df["Force"] = df["Force"].astype(float)
        df["Stroke"] = df["Stroke"].astype(float)

        # Calculate stress and strain
        area = np.pi * 0.25 * (metadata.size * 10**-3) ** 2
        stress = (df["Force"] - df["Force"].min()) / area
        strain = (df["Stroke"] - df["Stroke"].min()) / metadata.length

        df["Stress"] = stress
        df["Strain"] = strain

        # Add metadata to dataframe
        df.meta = metadata

        # Calculate derived properties
        self._calculate_material_properties(df)

        self.log.debug("File loaded successfully")
        return df

    def _parse_metadata(self, filepath: str) -> types.SimpleNamespace:
        """Parse metadata from file path and name."""
        fname = os.path.basename(filepath)
        dname = os.path.dirname(filepath)

        # Parse filename: test--line-crimp-XX--Y.csv
        slugs = fname.split("--")
        if len(slugs) >= 3:
            size_part = slugs[1].split("-")
            if len(size_part) >= 3:
                size = int(size_part[2])
                ctype = size_part[1]
            else:
                size = 21  # default
                ctype = "crimp"

            run_num = int(slugs[2].split(".")[0])
        else:
            # Fallback parsing
            size = 21
            ctype = "crimp"
            run_num = 0

        # Parse length from directory structure
        dname_parts = dname.split("/")
        length = self._parse_length(dname_parts, run_num)

        metadata = types.SimpleNamespace()
        metadata.filepath = filepath
        metadata.size = size
        metadata.ctype = ctype
        metadata.test_run = run_num
        metadata.length = length

        return metadata

    def _parse_length(self, dname_parts: List[str], run_num: int) -> float:
        """Parse specimen length from directory structure."""
        for part in dname_parts:
            if "in" in part and any(char.isdigit() for char in part):
                # Extract number before "in"
                length_str = part.replace("in", "")
                try:
                    length_inches = int(length_str)
                    return length_inches * 25.4  # Convert to mm
                except ValueError:
                    pass

        # Fallback to default
        return 254.0  # 10 inches in mm

    def _calculate_material_properties(self, df: pd.DataFrame) -> None:
        """Calculate material properties like modulus and yield strength."""
        stress = df["Stress"]
        strain = df["Strain"]

        # Find yield point using knee detection (returns strain value)
        knee_strain = self._find_yield_point(df, "Stress", "Strain")

        # Store yield point coordinates for visualization
        yield_point_strain = None
        yield_point_stress = None
        modulus = 0

        if knee_strain and len(knee_strain) > 0:
            # knee_strain contains strain values, not stress values
            knee_strain_val = knee_strain[0]
            yield_point_strain = knee_strain_val

            # Find corresponding stress value at yield point
            closest_idx = (df["Strain"] - knee_strain_val).abs().idxmin()
            yield_point_stress = df.loc[closest_idx, "Stress"]

            # Calculate modulus from data UP TO the yield point (true elastic region)
            elastic_data = df[df["Strain"] <= knee_strain_val]

            if len(elastic_data) > 5:  # Need enough points for good fit
                modulus, _ = np.polyfit(
                    elastic_data["Strain"], elastic_data["Stress"], 1
                )
            else:
                # Fallback to first 20% if yield point is too early
                max_stress_idx = df[df["Stress"] == stress.max()].index.values[0]
                fit_max = int(max_stress_idx * 0.2)
                if fit_max > 1:
                    modulus, _ = np.polyfit(strain[0:fit_max], stress[0:fit_max], 1)
        else:
            # Fallback: use first 20% of data for modulus calculation
            max_stress_idx = df[df["Stress"] == stress.max()].index.values[0]
            fit_max = int(max_stress_idx * 0.2)
            if fit_max > 1:
                modulus, _ = np.polyfit(strain[0:fit_max], stress[0:fit_max], 1)

        # Calculate kinetic energy and velocity
        area = np.pi * 0.25 * (df.meta.size * 10**-3) ** 2

        if knee_strain and len(knee_strain) > 0:
            knee_strain_val = knee_strain[0]

            # Filter data up to the knee strain point
            strain_subset = df[df["Strain"] <= knee_strain_val]

            if not strain_subset.empty and len(strain_subset) > 1:
                # Calculate area under stress-strain curve using trapezoidal integration
                trap_energy = trapz(strain_subset["Stress"], strain_subset["Strain"])
                kinetic_energy = trap_energy * area * (df.meta.length * 10**-3)
                velocity = np.sqrt((2 * kinetic_energy) / 0.045)  # Assuming 45g mass
            else:
                kinetic_energy = 0
                velocity = 0
        else:
            kinetic_energy = 0
            velocity = 0

        # Store properties in metadata
        df.meta.modulus = modulus
        df.meta.yield_stress = stress.max()
        df.meta.max_force = df["Force"].max()
        df.meta.kinetic_energy = kinetic_energy
        df.meta.velocity = velocity
        df.meta.yield_point_strain = yield_point_strain
        df.meta.yield_point_stress = yield_point_stress

    def _find_yield_point(  # noqa: C901
        self, df: pd.DataFrame, stress_col: str, strain_col: str
    ) -> List[float]:
        """Find yield point using smoothed derivative method.

        This method ignores early inflections to find the real yield point.
        """
        try:
            stress = df[stress_col]
            strain = df[strain_col]

            max_stress_idx = df[df[stress_col] == stress.max()].index.values[0]

            # Focus on the region where real yield occurs
            # Skip early 40% to avoid noise
            start_idx = int(max_stress_idx * 0.4)
            end_idx = int(max_stress_idx * 0.85)  # End before failure

            if end_idx - start_idx < 20:
                return [strain.max() * 0.7]

            subset_stress = stress[start_idx:end_idx]
            subset_strain = strain[start_idx:end_idx]

            # Method 1: Try knee detection on this focused region
            try:
                kn = KneeLocator(
                    subset_strain,
                    subset_stress,
                    curve="concave",
                    direction="increasing",
                    S=50,  # Lower sensitivity to avoid early small inflections
                )
                if kn.knee is not None:
                    # Validate the result is in reasonable range
                    max_strain = strain.max()
                    # Must be between 15% and 90% of max strain
                    if 0.15 < kn.knee < (max_strain * 0.9):
                        return [kn.knee]

            except Exception as e:
                # Log the error or handle specific exceptions
                self.log.warning(f"Failed to find knee point: {e}")

            # Method 2: Find where modulus drops significantly
            try:
                # Calculate rolling modulus (slope) over small windows
                window_size = max(5, len(subset_stress) // 20)
                moduli = []
                strain_points = []

                for i in range(window_size, len(subset_stress) - window_size):
                    start_window = i - window_size
                    end_window = i + window_size

                    window_strain = subset_strain.iloc[start_window:end_window]
                    window_stress = subset_stress.iloc[start_window:end_window]

                    if len(window_strain) > 3:
                        slope, _ = np.polyfit(window_strain, window_stress, 1)
                        moduli.append(slope)
                        strain_points.append(subset_strain.iloc[i])

                if len(moduli) > 10:
                    moduli = np.array(moduli)
                    strain_points = np.array(strain_points)

                    # Find where modulus drops to 70% of initial value
                    initial_modulus = np.mean(moduli[:5])  # First 5 points
                    threshold_modulus = initial_modulus * 0.7

                    drop_indices = np.where(moduli < threshold_modulus)[0]
                    if len(drop_indices) > 0:
                        yield_strain = strain_points[drop_indices[0]]
                        if 0.15 < yield_strain < (strain.max() * 0.9):
                            return [yield_strain]
            except Exception as e:
                # Log the error or handle specific exceptions
                self.log.warning(f"Failed to find knee point: {e}")

            # Method 3: Conservative fallback based on curve shape
            max_strain = strain.max()
            if max_strain > 0.4:
                return [max_strain * 0.65]  # Around 65% of max strain
            else:
                return [max_strain * 0.75]  # Around 75% for shorter curves

        except Exception as e:
            self.log.warning(f"Yield detection failed: {e}")
            return [df[strain_col].max() * 0.7]

    def calculate_summary_stats(self, data_list: List[pd.DataFrame]) -> Dict:
        """Calculate summary statistics for a group of test data."""
        if not data_list:
            return {}

        moduli = [df.meta.modulus for df in data_list if hasattr(df.meta, "modulus")]
        yield_stresses = [
            df.meta.yield_stress for df in data_list if hasattr(df.meta, "yield_stress")
        ]
        max_forces = [
            df.meta.max_force for df in data_list if hasattr(df.meta, "max_force")
        ]

        stats = {
            "sample_count": len(data_list),
            "modulus_avg": np.mean(moduli) if moduli else 0,
            "modulus_std": np.std(moduli) if moduli else 0,
            "yield_stress_avg": np.mean(yield_stresses) if yield_stresses else 0,
            "yield_stress_std": np.std(yield_stresses) if yield_stresses else 0,
            "max_force_avg": np.mean(max_forces) if max_forces else 0,
            "max_force_std": np.std(max_forces) if max_forces else 0,
        }

        if data_list:
            stats["length"] = data_list[0].meta.length
            stats["size"] = data_list[0].meta.size
            stats["ctype"] = data_list[0].meta.ctype

        return stats

    def generate_summary_report(self, group_results: Dict, output_dir: str) -> None:
        """Generate a summary report of all test results."""
        output_path = Path(output_dir) / "summary_report.txt"

        with open(output_path, "w") as f:
            f.write("Fishing Line Material Properties Analysis Summary\n")
            f.write("=" * 50 + "\n\n")

            for group_name, group_data in group_results.items():
                f.write(f"Group: {group_name}\n")
                f.write("-" * 30 + "\n")

                for length_name, stats in group_data.items():
                    f.write(f"  Length: {length_name}\n")
                    f.write(f"    Sample Count: {stats.get('sample_count', 0)}\n")
                    f.write(
                        f"    Modulus: {stats.get('modulus_avg', 0):.2e} ± "
                        f"{stats.get('modulus_std', 0):.2e} Pa\n"
                    )
                    f.write(
                        f"    Yield Stress: {stats.get('yield_stress_avg', 0):.2e} ± "
                        f"{stats.get('yield_stress_std', 0):.2e} Pa\n"
                    )
                    f.write(
                        f"    Max Force: {stats.get('max_force_avg', 0):.2f} ± "
                        f"{stats.get('max_force_std', 0):.2f} N\n"
                    )
                    f.write("\n")

                f.write("\n")

        self.log.info(f"Summary report saved to {output_path}")
