"""Material analysis module for fishing line properties."""

import logging
import os
import types
from pathlib import Path
from typing import Any
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

    def __init__(
        self,
        efficiency: float = 0.5,
        alpha_mass_fraction: float = 0.3,
        projectile_mass_kg: float = 0.045,
    ) -> None:
        """Initialize the MaterialAnalyzer.

        Args:
            efficiency: Energy conversion efficiency (0-1), accounts for losses
            alpha_mass_fraction: Fraction of local line mass engaged (0-1)
            projectile_mass_kg: Mass of projectile in kg (default 45g)
        """
        self.log = logging.getLogger(__name__)
        self.efficiency = efficiency
        self.alpha_mass_fraction = alpha_mass_fraction
        self.projectile_mass_kg = projectile_mass_kg

        # Line density estimate (kg/m) - adjust based on actual material
        # Typical monofilament: ~1100 kg/m³ density
        self.line_density_kg_m3 = 1100.0

    def load_file(self, filepath: str) -> pd.DataFrame:
        """Load material test data from CSV file.

        Args:
            filepath: Path to CSV file

        Returns:
            DataFrame with material test data and metadata

        Raises:
            ValueError: If file is not in CSV format
        """
        self.log.debug("Loading file: %s", filepath)
        if not filepath.endswith(".csv"):
            raise ValueError(f"File must be CSV format: {filepath}")

        # First, read the file to check for the extra header row
        with open(filepath) as f:
            first_line = f.readline().strip()
            second_line = f.readline().strip()

        # Check if first line is the problematic header
        skip_rows = 0
        if (
            first_line.startswith('"1 _ 1"')
            or first_line.startswith("1 _ 1")
            or "Unnamed" in first_line
            or (
                '"Time"' not in first_line
                and "Time" not in first_line
                and ('"Time"' in second_line or "Time" in second_line)
            )
        ):
            skip_rows = 1
            self.log.debug(
                f"Detected extra header row: {first_line!r}, skipping first line"
            )

        # Read CSV file, skipping the extra header if present
        df = pd.read_csv(filepath, skiprows=skip_rows)

        # Check if first row contains units instead of data
        if len(df) > 0:
            first_row = df.iloc[0].astype(str)
            if any(
                unit in " ".join(first_row.values).lower()
                for unit in ["sec", "mm", "n", "pa"]
            ):
                df = df.drop(0).reset_index(drop=True)
                self.log.debug("Removed units row from data")

        required_columns = ["Force", "Stroke"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            available_cols = list(df.columns)
            raise ValueError(
                f"Missing required columns: {missing_columns}. "
                f"Available columns: {available_cols}"
            )

        # Parse metadata from filename and directory structure
        metadata = self._parse_metadata(filepath)

        # Convert data types
        df["Force"] = pd.to_numeric(df["Force"], errors="coerce")
        df["Stroke"] = pd.to_numeric(df["Stroke"], errors="coerce")

        # Remove any rows with NaN values
        df = df.dropna(subset=["Force", "Stroke"]).reset_index(drop=True)

        # Calculate stress and strain (still useful for visualization)
        area = np.pi * 0.25 * (metadata.size * 1e-3) ** 2  # Fixed: mm to m

        if area <= 0:
            self.log.warning("Zero or negative area detected, using default")
            area = np.pi * 0.25 * (2.1 * 1e-3) ** 2

        stress = (df["Force"] - df["Force"].min()) / area
        strain = (df["Stroke"] - df["Stroke"].min()) / metadata.length
        df["Stress"] = stress
        df["Strain"] = strain

        # Add metadata to dataframe
        df.meta = metadata

        # Calculate derived properties using force-stroke method
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
                size = 21
                ctype = "crimp"

            try:
                run_num = int(slugs[2].split(".")[0])
            except (ValueError, IndexError):
                run_num = 0
        else:
            size = 21
            ctype = "crimp"
            run_num = 0

        # Parse length from directory structure
        dname_parts = dname.split("/")
        length = self._parse_length(dname_parts, run_num)

        metadata = types.SimpleNamespace()
        metadata.filepath = filepath
        metadata.size = size  # diameter in mm
        metadata.ctype = ctype
        metadata.test_run = run_num
        metadata.length = length  # gauge length in mm

        return metadata

    def _parse_length(self, dname_parts: List[str], run_num: int) -> float:
        """Parse specimen length from directory structure."""
        for part in dname_parts:
            if "in" in part and any(char.isdigit() for char in part):
                length_str = part.replace("in", "")
                try:
                    length_inches = int(length_str)
                    return length_inches * 25.4  # Convert to mm
                except ValueError:
                    pass

        return 254.0  # 10 inches in mm

    def _calculate_material_properties(self, df: pd.DataFrame) -> None:
        """Calculate material properties using force-stroke method.

        This method:
        1. Finds elastic cutoff using knee detection
        2. Computes recoverable energy from F-S curve (J)
        3. Normalizes to energy per meter (J/m)
        4. Scales to effective lengths with realistic parameters
        """
        force = df["Force"].values
        stroke_mm = df["Stroke"].values
        stroke_m = (stroke_mm - stroke_mm.min()) / 1000.0  # Convert to meters

        stress = df["Stress"].values
        strain = df["Strain"].values

        # Find elastic cutoff using knee detection on stress-strain
        knee_strain = self._find_yield_point(df, "Stress", "Strain")

        # Store yield point for visualization
        yield_point_strain = None
        yield_point_stress = None
        modulus = 0

        # Find cutoff index in original data
        if knee_strain and len(knee_strain) > 0:
            knee_strain_val = knee_strain[0]
            yield_point_strain = knee_strain_val

            # Find index closest to knee strain
            cutoff_idx = np.argmin(np.abs(strain - knee_strain_val))
            closest_idx = (df["Strain"] - knee_strain_val).abs().idxmin()
            yield_point_stress = df.loc[closest_idx, "Stress"]

            # Calculate modulus from elastic region
            elastic_data = df[df["Strain"] <= knee_strain_val]
            if len(elastic_data) > 5:
                modulus, _ = np.polyfit(
                    elastic_data["Strain"], elastic_data["Stress"], 1
                )
            else:
                max_stress_idx = df[df["Stress"] == stress.max()].index.values[0]
                fit_max = int(max_stress_idx * 0.2)
                if fit_max > 1:
                    modulus, _ = np.polyfit(strain[0:fit_max], stress[0:fit_max], 1)
        else:
            # Fallback: use 70% of max strain
            max_strain_idx = np.argmax(strain)
            cutoff_idx = int(max_strain_idx * 0.7)
            max_stress_idx = df[df["Stress"] == stress.max()].index.values[0]
            fit_max = int(max_stress_idx * 0.2)
            if fit_max > 1:
                modulus, _ = np.polyfit(strain[0:fit_max], stress[0:fit_max], 1)

        # === NEW: Force-Stroke Energy Calculation ===

        # 1. Compute recoverable energy from F-S curve (up to elastic cutoff)
        e_sample_j = trapz(force[:cutoff_idx], stroke_m[:cutoff_idx])

        # 2. Normalize by gauge length to get energy per meter
        l_gauge_m = df.meta.length / 1000.0  # mm to m
        e_per_m = e_sample_j / l_gauge_m

        # 3. Calculate line properties
        diameter_m = df.meta.size / 1000.0  # mm to m
        area_m2 = np.pi * 0.25 * diameter_m**2
        line_mass_per_m = self.line_density_kg_m3 * area_m2

        # 4. Scale to multiple effective lengths for sensitivity analysis
        l_eff_options = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0]  # meters

        # Effective mass includes projectile + small amount of accelerating line
        # Assume ~1m of line accelerates with the projectile
        l_line_accelerates = 1.0  # meters
        m_line_accelerates = line_mass_per_m * l_line_accelerates
        m_eff = self.projectile_mass_kg + m_line_accelerates

        velocities = []
        kinetic_energies = []

        for l_eff in l_eff_options:
            # Total recoverable energy at this effective length
            e_total = e_per_m * l_eff

            # Convert to velocity with efficiency factor
            # v = sqrt(2 * η * E / m_eff)
            if m_eff > 0 and e_total > 0:
                v = np.sqrt(2 * self.efficiency * e_total / m_eff)
                ke = 0.5 * self.projectile_mass_kg * v**2
            else:
                v = 0
                ke = 0

            velocities.append(v)
            kinetic_energies.append(ke)

        # Store primary results (using 1m effective length as reference)
        idx_1m = l_eff_options.index(1.0)

        # Store all properties in metadata
        df.meta.modulus = modulus
        df.meta.yield_stress = stress.max()
        df.meta.max_force = force.max()
        df.meta.yield_point_strain = yield_point_strain
        df.meta.yield_point_stress = yield_point_stress

        # Store energy calculation results
        df.meta.E_sample_J = e_sample_j
        df.meta.E_per_m = e_per_m
        df.meta.L_gauge_m = l_gauge_m
        df.meta.line_mass_per_m = line_mass_per_m

        # Store velocity/energy for different effective lengths
        df.meta.L_eff_options = l_eff_options
        df.meta.velocities = velocities
        df.meta.kinetic_energies = kinetic_energies

        # Store primary values (1m reference)
        df.meta.velocity = velocities[idx_1m]
        df.meta.kinetic_energy = kinetic_energies[idx_1m]

        # Log the range for user awareness
        self.log.info(
            f"Energy per meter: {e_per_m:.4f} J/m | "
            f"Velocity range: {min(velocities):.2f}-{max(velocities):.2f} m/s "
            f"(L_eff: {min(l_eff_options):.1f}-{max(l_eff_options):.1f} m)"
        )

    def _find_yield_point(  # noqa: C901
        self, df: pd.DataFrame, stress_col: str, strain_col: str
    ) -> List[float]:
        """Find yield point using smoothed derivative method."""
        try:
            stress = df[stress_col]
            strain = df[strain_col]

            max_stress_idx = df[df[stress_col] == stress.max()].index.values[0]

            start_idx = int(max_stress_idx * 0.4)
            end_idx = int(max_stress_idx * 0.85)

            if end_idx - start_idx < 20:
                return [strain.max() * 0.7]

            subset_stress = stress[start_idx:end_idx]
            subset_strain = strain[start_idx:end_idx]

            # Method 1: Knee detection
            try:
                kn = KneeLocator(
                    subset_strain,
                    subset_stress,
                    curve="concave",
                    direction="increasing",
                    S=50,
                )
                if kn.knee is not None:
                    max_strain = strain.max()
                    if 0.15 < kn.knee < (max_strain * 0.9):
                        return [kn.knee]
            except Exception as e:
                self.log.warning(f"Knee detection failed: {e}")

            # Method 2: Modulus drop detection
            try:
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
                    moduli_array = np.array(moduli)
                    strain_points_array = np.array(strain_points)

                    initial_modulus = np.mean(moduli_array[:5])
                    threshold_modulus = initial_modulus * 0.7

                    drop_indices = np.where(moduli_array < threshold_modulus)[0]
                    if len(drop_indices) > 0:
                        yield_strain = strain_points_array[drop_indices[0]]
                        if 0.15 < yield_strain < (strain.max() * 0.9):
                            return [yield_strain]
            except Exception as e:
                self.log.warning(f"Modulus drop detection failed: {e}")

            # Fallback
            max_strain = strain.max()
            if max_strain > 0.4:
                return [max_strain * 0.65]
            else:
                return [max_strain * 0.75]

        except Exception as e:
            self.log.warning(f"Yield detection failed: {e}")
            return [df[strain_col].max() * 0.7]

    def calculate_summary_stats(self, data_list: List[pd.DataFrame]) -> Dict[str, Any]:
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

        # New: E_per_m statistics
        e_per_m_values = [
            df.meta.E_per_m for df in data_list if hasattr(df.meta, "E_per_m")
        ]

        stats = {
            "sample_count": len(data_list),
            "modulus_avg": np.mean(moduli) if moduli else 0,
            "modulus_std": np.std(moduli) if moduli else 0,
            "yield_stress_avg": np.mean(yield_stresses) if yield_stresses else 0,
            "yield_stress_std": np.std(yield_stresses) if yield_stresses else 0,
            "max_force_avg": np.mean(max_forces) if max_forces else 0,
            "max_force_std": np.std(max_forces) if max_forces else 0,
            "E_per_m_avg": np.mean(e_per_m_values) if e_per_m_values else 0,
            "E_per_m_std": np.std(e_per_m_values) if e_per_m_values else 0,
        }

        if data_list:
            first_meta = data_list[0].meta
            stats["length"] = getattr(first_meta, "length", 254.0)
            stats["size"] = getattr(first_meta, "size", 21)
            stats["ctype"] = getattr(first_meta, "ctype", "crimp")

        return stats

    def generate_summary_report(
        self, group_results: Dict[str, Any], output_dir: str
    ) -> None:
        """Generate a summary report of all test results."""
        output_path = Path(output_dir) / "summary_report.txt"

        with open(output_path, "w") as f:
            f.write("Fishing Line Material Properties Analysis Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write("Energy Calculation Method: Force-Stroke Integration\n")
            f.write(f"Efficiency Factor: {self.efficiency}\n")
            f.write(f"Line Mass Fraction: {self.alpha_mass_fraction}\n")
            f.write(f"Projectile Mass: {self.projectile_mass_kg * 1000:.1f}g\n\n")

            for group_name, group_data in group_results.items():
                f.write(f"Group: {group_name}\n")
                f.write("-" * 30 + "\n")

                for length_name, stats in group_data.items():
                    f.write(f"  Length: {length_name}\n")
                    f.write(f"    Sample Count: {stats.get('sample_count', 0)}\n")
                    f.write(
                        f"    Energy/meter: {stats.get('E_per_m_avg', 0):.4f} ± "
                        f"{stats.get('E_per_m_std', 0):.4f} J/m\n"
                    )
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
