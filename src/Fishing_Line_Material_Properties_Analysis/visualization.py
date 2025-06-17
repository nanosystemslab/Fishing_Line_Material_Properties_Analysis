"""Visualization module for fishing line material properties."""

import logging
from pathlib import Path
from typing import Dict
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


class MaterialVisualizer:
    """Visualizer for fishing line material properties."""

    def __init__(self, output_dir: str = "out"):
        """Initialize the MaterialVisualizer.

        Args:
            output_dir: Directory for saving plots and outputs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.log = logging.getLogger(__name__)

        # Plot parameters configuration
        self.plot_params = {
            "Time": {"label": "Time", "unit": "Time (sec)"},
            "Force": {"label": "Force", "unit": "Force (N)"},
            "Stroke": {"label": "Stroke", "unit": "Stroke (mm)"},
            "Stress": {"label": "Stress", "unit": "Stress (Pa)"},
            "Strain": {"label": "Strain", "unit": "Strain (mm/mm)"},
            "KE": {"label": "KE", "unit": "Kinetic Energy (J)"},
            "V": {"label": "Velocity", "unit": "Velocity (m/s)"},
            "D": {"label": "Diameter", "unit": "Diameter (mm)"},
            "L": {"label": "Length", "unit": "Length (mm)"},
        }

        # Global style is now set in __init__.py

    def _extract_group_from_path(self, filepath: str) -> str:
        """Extract group name from file path."""
        # Convert to Path object for easier manipulation
        path = Path(filepath)

        # Look for group_X pattern in the path parts
        for part in path.parts:
            if part.startswith("group_"):
                return part

        # Fallback if no group found
        return "unknown_group"

    def _extract_length_from_path(self, filepath: str) -> str:
        """Extract length name from file path."""
        # Convert to Path object for easier manipulation
        path = Path(filepath)

        # Look for length pattern (5in, 10in, 20in) in the path parts
        for part in path.parts:
            if part.endswith("in") and any(char.isdigit() for char in part):
                return part

        # Fallback if no length found
        return "unknown_length"

    def plot_single_trace(
        self, data: pd.DataFrame, x_param: str = "Strain", y_param: str = "Stress"
    ) -> None:
        """Plot a single data trace.

        Args:
            data: DataFrame with test data
            x_param: Parameter for x-axis
            y_param: Parameter for y-axis
        """
        self.log.debug("Plotting single trace")

        x = data[x_param]
        y = data[y_param]

        # Create figure
        figsize = 4
        figdpi = 600
        hwratio = 4.0 / 3.0
        fig = plt.figure(figsize=(figsize * hwratio, figsize), dpi=figdpi)
        ax = fig.add_subplot(111)

        # Set transparent background and black borders with ticks
        fig.patch.set_facecolor("none")  # Transparent figure background
        ax.set_facecolor("none")  # Transparent axes background

        # Black borders and ticks
        for spine in ax.spines.values():
            spine.set_edgecolor("black")
            spine.set_linewidth(1.0)

        ax.tick_params(colors="black", which="both")
        ax.xaxis.label.set_color("black")
        ax.yaxis.label.set_color("black")

        # Main plot
        line_label = f"{y_param} vs {x_param}"
        ax.plot(x, y, label=line_label, linewidth=1.5)

        # Set labels
        ax.set_xlabel(self.plot_params[x_param]["unit"])
        ax.set_ylabel(self.plot_params[y_param]["unit"])

        # Set limits for stress-strain plots
        if y_param == "Stress":
            ax.set_ylim([0, y.max() * 1.1])

        # Mark yield point instead of fracture point
        if hasattr(data.meta, "yield_point_strain") and hasattr(
            data.meta, "yield_point_stress"
        ):
            ax.scatter(
                data.meta.yield_point_strain,
                data.meta.yield_point_stress,
                s=50,
                label="Yield Point",
                marker="o",
                color="red",
                linewidth=3,
            )
        else:
            # Fallback to fracture point if yield point not available
            ax.scatter(
                x.max(),
                y.max(),
                s=50,
                label="Fracture",
                marker="x",
                color="red",
                linewidth=3,
            )

        # Add fit line for linear region
        if hasattr(data.meta, "modulus") and data.meta.modulus > 0:
            max_y_idx = data[data[y_param] == y.max()].index.values[0]
            fit_max = int(max_y_idx / 2)

            if fit_max > 1:
                m, b = np.polyfit(x[0:fit_max], y[0:fit_max], 1)
                ax.plot(x, m * x + b, "r--", label="Linear Fit", alpha=0.7)

        # Add statistics to legend
        if hasattr(data.meta, "modulus"):
            modulus_mpa = data.meta.modulus * 1e-6  # Convert to MPa
            ax.plot([], [], " ", label=f"Modulus = {modulus_mpa:.2f} MPa")

        if hasattr(data.meta, "yield_stress"):
            yield_mpa = data.meta.yield_stress * 1e-6  # Convert to MPa
            ax.plot([], [], " ", label=f"Yield = {yield_mpa:.2f} MPa")

        if hasattr(data.meta, "max_force"):
            ax.plot([], [], " ", label=f"Max Force = {data.meta.max_force:.2f} N")

        # Legend outside on the right with transparent background
        legend = ax.legend(frameon=True, bbox_to_anchor=(1.05, 1), loc="upper left")
        legend.get_frame().set_facecolor("none")
        legend.get_frame().set_edgecolor("black")

        # Save plot with organized directory structure
        length_in = int(data.meta.length / 25.4) if hasattr(data.meta, "length") else 0
        size = data.meta.size if hasattr(data.meta, "size") else 0
        run_num = data.meta.test_run if hasattr(data.meta, "test_run") else 0

        # Extract group and length info from filepath
        group_name = self._extract_group_from_path(data.meta.filepath)
        length_name = self._extract_length_from_path(data.meta.filepath)

        # Create group and length-specific directory structure
        group_length_dir = self.output_dir / group_name / length_name
        group_length_dir.mkdir(parents=True, exist_ok=True)

        plot_filename = (
            f"plot-{length_in}in-{size}-single-" f"{y_param}-vs-{x_param}-{run_num}.png"
        )
        plot_path = group_length_dir / plot_filename

        fig.savefig(plot_path, bbox_inches="tight", dpi=figdpi, transparent=True)
        plt.close(fig)

        self.log.info(f"Single trace plot saved: {plot_path}")

    def plot_multi_trace(
        self,
        data_list: List[pd.DataFrame],
        x_param: str = "Strain",
        y_param: str = "Stress",
        title_suffix: str = "",
    ) -> None:
        """Plot multiple data traces on the same figure.

        Args:
            data_list: List of DataFrames with test data
            x_param: Parameter for x-axis
            y_param: Parameter for y-axis
            title_suffix: Additional suffix for filename
        """
        self.log.debug("Plotting multiple traces")

        if not data_list:
            self.log.warning("No data provided for multi-trace plot")
            return

        # Create figure and setup
        fig, ax = self._create_base_figure()

        # Collect statistics for legend
        moduli, yield_stresses, max_forces = self._collect_multi_trace_stats(data_list)

        # Plot each trace
        self._plot_individual_traces(ax, data_list, x_param, y_param)

        # Configure axes and limits
        self._configure_multi_trace_axes(ax, data_list, x_param, y_param)

        # Add statistics to legend
        self._add_multi_trace_statistics(ax, moduli, yield_stresses, max_forces)

        # Setup legend
        self._setup_legend(ax)

        # Save plot
        self._save_multi_trace_plot(fig, data_list, x_param, y_param, title_suffix)

    def _create_base_figure(self):
        """Create base figure with styling."""
        figsize = 4
        figdpi = 600
        hwratio = 4.0 / 3.0
        fig = plt.figure(figsize=(figsize * hwratio, figsize), dpi=figdpi)
        ax = fig.add_subplot(111)

        # Set transparent background and black borders with ticks
        fig.patch.set_facecolor("none")
        ax.set_facecolor("none")

        # Black borders and ticks
        for spine in ax.spines.values():
            spine.set_edgecolor("black")
            spine.set_linewidth(1.0)

        ax.tick_params(colors="black", which="both")
        ax.xaxis.label.set_color("black")
        ax.yaxis.label.set_color("black")

        return fig, ax

    def _collect_multi_trace_stats(self, data_list):
        """Collect statistics from multiple traces."""
        moduli = []
        yield_stresses = []
        max_forces = []

        for data in data_list:
            if hasattr(data.meta, "modulus"):
                moduli.append(data.meta.modulus)
            if hasattr(data.meta, "yield_stress"):
                yield_stresses.append(data.meta.yield_stress)
            if hasattr(data.meta, "max_force"):
                max_forces.append(data.meta.max_force)

        return moduli, yield_stresses, max_forces

    def _plot_individual_traces(self, ax, data_list, x_param, y_param):
        """Plot individual traces on the axes."""
        for i, data in enumerate(data_list):
            x = data[x_param]
            y = data[y_param]
            ax.plot(x, y, alpha=0.7, linewidth=1.2, label=f"Sample {i + 1}")

    def _configure_multi_trace_axes(self, ax, data_list, x_param, y_param):
        """Configure axes labels and limits."""
        ax.set_xlabel(self.plot_params[x_param]["unit"])
        ax.set_ylabel(self.plot_params[y_param]["unit"])

        # Set limits
        if y_param == "Stress":
            max_stress = max(data[y_param].max() for data in data_list)
            ax.set_ylim([0, max_stress * 1.1])

        if x_param == "Strain":
            ax.set_xlim([0, 1])

    def _add_multi_trace_statistics(self, ax, moduli, yield_stresses, max_forces):
        """Add average statistics to legend."""
        if moduli:
            avg_modulus_mpa = np.mean(moduli) * 1e-6
            ax.plot([], [], " ", label=f"Avg. Modulus = {avg_modulus_mpa:.2f} MPa")

        if yield_stresses:
            avg_yield_mpa = np.mean(yield_stresses) * 1e-6
            ax.plot([], [], " ", label=f"Avg. Yield = {avg_yield_mpa:.2f} MPa")

        if max_forces:
            avg_force = np.mean(max_forces)
            ax.plot([], [], " ", label=f"Avg. Max Force = {avg_force:.2f} N")

    def _setup_legend(self, ax):
        """Setup legend with styling."""
        legend = ax.legend(frameon=True, bbox_to_anchor=(1.05, 1), loc="upper left")
        legend.get_frame().set_facecolor("none")
        legend.get_frame().set_edgecolor("black")

    def _save_multi_trace_plot(self, fig, data_list, x_param, y_param, title_suffix):
        """Save the multi-trace plot."""
        first_data = data_list[0]
        length_in = (
            int(first_data.meta.length / 25.4)
            if hasattr(first_data.meta, "length")
            else 0
        )
        size = first_data.meta.size if hasattr(first_data.meta, "size") else 0

        # Extract group and length info from filepath
        group_name = self._extract_group_from_path(first_data.meta.filepath)
        length_name = self._extract_length_from_path(first_data.meta.filepath)

        # Create group and length-specific directory structure
        group_length_dir = self.output_dir / group_name / length_name
        group_length_dir.mkdir(parents=True, exist_ok=True)

        if title_suffix:
            plot_filename = f"plot-{title_suffix}-multi-{y_param}-vs-{x_param}.png"
        else:
            plot_filename = (
                f"plot-{length_in}in-{size}-multi-{y_param}-vs-{x_param}.png"
            )

        plot_path = group_length_dir / plot_filename

        fig.savefig(plot_path, bbox_inches="tight", dpi=600, transparent=True)
        plt.close(fig)

        self.log.info(f"Multi-trace plot saved: {plot_path}")

    def plot_output_data(
        self, filepath: str, x_param: str = "D", y_param: str = "KE"
    ) -> None:
        """Plot output/results data.

        Args:
            filepath: Path to output CSV file
            x_param: Parameter for x-axis
            y_param: Parameter for y-axis
        """
        self.log.debug(f"Plotting output data from {filepath}")

        # Load output data
        df = pd.read_csv(filepath, header=None)

        # For now, create a simple placeholder plot
        # You'll need to adapt this based on your actual output data format
        figsize = 4
        figdpi = 600
        hwratio = 4.0 / 3.0
        fig = plt.figure(figsize=(figsize * hwratio, figsize), dpi=figdpi)
        ax = fig.add_subplot(111)

        # Set transparent background and black borders with ticks
        fig.patch.set_facecolor("none")  # Transparent figure background
        ax.set_facecolor("none")  # Transparent axes background

        # Black borders and ticks
        for spine in ax.spines.values():
            spine.set_edgecolor("black")
            spine.set_linewidth(1.0)

        ax.tick_params(colors="black", which="both")
        ax.xaxis.label.set_color("black")
        ax.yaxis.label.set_color("black")

        # This is a placeholder - adapt based on your data format
        ax.plot(df.iloc[:, 0], df.iloc[:, 1], "o-", label=f"{y_param} vs {x_param}")

        ax.set_xlabel(self.plot_params.get(x_param, {"unit": x_param})["unit"])
        ax.set_ylabel(self.plot_params.get(y_param, {"unit": y_param})["unit"])

        # Legend outside on the right with transparent background
        legend = ax.legend(frameon=True, bbox_to_anchor=(1.05, 1), loc="upper left")
        legend.get_frame().set_facecolor("none")
        legend.get_frame().set_edgecolor("black")

        # Save plot
        plot_filename = f"output-{y_param}-vs-{x_param}.png"
        plot_path = self.output_dir / plot_filename

        fig.savefig(plot_path, bbox_inches="tight", dpi=figdpi, transparent=True)
        plt.close(fig)

        self.log.info(f"Output plot saved: {plot_path}")

    def create_summary_plot(self, group_results: Dict, output_dir: str) -> None:
        """Create summary plots comparing results across groups and lengths.

        Args:
            group_results: Dictionary with analysis results
            output_dir: Output directory path
        """
        self.log.debug("Creating summary plots")

        # Prepare data for plotting
        groups = []
        lengths = []
        moduli = []
        yield_stresses = []
        max_forces = []

        for group_name, group_data in group_results.items():
            for length_name, stats in group_data.items():
                groups.append(group_name)
                lengths.append(length_name)
                moduli.append(stats.get("modulus_avg", 0))
                yield_stresses.append(stats.get("yield_stress_avg", 0))
                max_forces.append(stats.get("max_force_avg", 0))

        if not groups:
            self.log.warning("No data available for summary plots")
            return

        # Create summary DataFrame
        summary_df = pd.DataFrame(
            {
                "Group": groups,
                "Length": lengths,
                "Modulus": moduli,
                "Yield_Stress": yield_stresses,
                "Max_Force": max_forces,
            }
        )

        # Create comparison plots
        self._plot_comparison_by_length(summary_df)
        self._plot_comparison_by_group(summary_df)

    def _plot_comparison_by_length(self, summary_df: pd.DataFrame) -> None:
        """Create comparison plots grouped by length."""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Modulus comparison
        for group in summary_df["Group"].unique():
            group_data = summary_df[summary_df["Group"] == group]
            axes[0].plot(
                group_data["Length"],
                group_data["Modulus"] * 1e-6,
                "o-",
                label=group,
                linewidth=2,
                markersize=6,
            )

        axes[0].set_xlabel("Length")
        axes[0].set_ylabel("Modulus (MPa)")
        axes[0].set_title("Modulus vs Length")
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        # Yield stress comparison
        for group in summary_df["Group"].unique():
            group_data = summary_df[summary_df["Group"] == group]
            axes[1].plot(
                group_data["Length"],
                group_data["Yield_Stress"] * 1e-6,
                "o-",
                label=group,
                linewidth=2,
                markersize=6,
            )

        axes[1].set_xlabel("Length")
        axes[1].set_ylabel("Yield Stress (MPa)")
        axes[1].set_title("Yield Stress vs Length")
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

        # Max force comparison
        for group in summary_df["Group"].unique():
            group_data = summary_df[summary_df["Group"] == group]
            axes[2].plot(
                group_data["Length"],
                group_data["Max_Force"],
                "o-",
                label=group,
                linewidth=2,
                markersize=6,
            )

        axes[2].set_xlabel("Length")
        axes[2].set_ylabel("Max Force (N)")
        axes[2].set_title("Max Force vs Length")
        axes[2].legend()
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()

        plot_path = self.output_dir / "summary_comparison_by_length.png"
        fig.savefig(plot_path, bbox_inches="tight", dpi=300)
        plt.close(fig)

        self.log.info(f"Summary comparison plot saved: {plot_path}")

    def _plot_comparison_by_group(self, summary_df: pd.DataFrame) -> None:
        """Create comparison plots grouped by group."""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Convert length to numeric for proper sorting
        length_order = ["5in", "10in", "20in"]
        summary_df["Length_num"] = summary_df["Length"].map(
            {"5in": 5, "10in": 10, "20in": 20}
        )
        summary_df = summary_df.sort_values("Length_num")

        # Modulus comparison
        for length in length_order:
            if length in summary_df["Length"].values:
                length_data = summary_df[summary_df["Length"] == length]
                axes[0].bar(
                    [f"{group}_{length}" for group in length_data["Group"]],
                    length_data["Modulus"] * 1e-6,
                    label=length,
                    alpha=0.7,
                )

        axes[0].set_ylabel("Modulus (MPa)")
        axes[0].set_title("Modulus by Group and Length")
        axes[0].legend()
        axes[0].tick_params(axis="x", rotation=45)

        # Yield stress comparison
        for length in length_order:
            if length in summary_df["Length"].values:
                length_data = summary_df[summary_df["Length"] == length]
                axes[1].bar(
                    [f"{group}_{length}" for group in length_data["Group"]],
                    length_data["Yield_Stress"] * 1e-6,
                    label=length,
                    alpha=0.7,
                )

        axes[1].set_ylabel("Yield Stress (MPa)")
        axes[1].set_title("Yield Stress by Group and Length")
        axes[1].legend()
        axes[1].tick_params(axis="x", rotation=45)

        # Max force comparison
        for length in length_order:
            if length in summary_df["Length"].values:
                length_data = summary_df[summary_df["Length"] == length]
                axes[2].bar(
                    [f"{group}_{length}" for group in length_data["Group"]],
                    length_data["Max_Force"],
                    label=length,
                    alpha=0.7,
                )

        axes[2].set_ylabel("Max Force (N)")
        axes[2].set_title("Max Force by Group and Length")
        axes[2].legend()
        axes[2].tick_params(axis="x", rotation=45)

        plt.tight_layout()

        plot_path = self.output_dir / "summary_comparison_by_group.png"
        fig.savefig(plot_path, bbox_inches="tight", dpi=300)
        plt.close(fig)

        self.log.info(f"Group comparison plot saved: {plot_path}")
