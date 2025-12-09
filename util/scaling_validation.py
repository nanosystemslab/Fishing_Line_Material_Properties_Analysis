#!/usr/bin/env python3
"""Validation tool to check if linear scaling is appropriate.

This script plots E_sample vs L_gauge to verify:
1. Linear relationship through origin (validates scaling)
2. Any intercept (indicates clamp/crimp losses)
3. Scatter/deviation (indicates material variability)
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


def analyze_scaling_validity(csv_path: str, output_dir: str = "out") -> None:
    """Analyze whether linear scaling from test specimens is valid.

    Args:
        csv_path: Path to individual_results.csv
        output_dir: Directory to save validation plots
    """
    # Load results
    df = pd.read_csv(csv_path)

    # Check if we have the required columns
    required_cols = ["E_sample_J", "L_gauge_m", "group", "length"]
    if not all(col in df.columns for col in required_cols):
        print(f"Error: CSV must contain columns: {required_cols}")
        return

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Get unique groups
    groups = df["group"].unique()

    # Create figure with subplots for each group
    n_groups = len(groups)
    fig, axes = plt.subplots(1, n_groups, figsize=(6 * n_groups, 5), squeeze=False)
    axes = axes.flatten()

    print("\n" + "=" * 60)
    print("SCALING VALIDATION ANALYSIS")
    print("=" * 60)

    for idx, group in enumerate(groups):
        ax = axes[idx]
        group_data = df[df["group"] == group]

        # Extract data
        l_gauge = group_data["L_gauge_m"].values
        e_sample = group_data["E_sample_J"].values
        lengths = group_data["length"].values

        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            l_gauge, e_sample
        )

        # Calculate what percentage the intercept is of typical E_sample
        mean_e = np.mean(e_sample)
        intercept_percent = (abs(intercept) / mean_e) * 100 if mean_e > 0 else 0

        # Plot data points colored by length
        unique_lengths = np.unique(lengths)
        colors = plt.cm.viridis(np.linspace(0, 1, len(unique_lengths)))

        for i, length in enumerate(unique_lengths):
            mask = lengths == length
            ax.scatter(
                l_gauge[mask],
                e_sample[mask],
                color=colors[i],
                s=100,
                alpha=0.7,
                label=f"{length}",
                edgecolors="black",
                linewidth=1,
            )

        # Plot fit line
        l_fit = np.linspace(0, l_gauge.max() * 1.1, 100)
        e_fit = slope * l_fit + intercept
        ax.plot(
            l_fit,
            e_fit,
            "r--",
            linewidth=2,
            label=f"Fit: E = {slope:.3f}L + {intercept:.3f}",
        )

        # Plot line through origin for comparison
        e_origin = slope * l_fit
        ax.plot(
            l_fit,
            e_origin,
            "g:",
            linewidth=2,
            alpha=0.5,
            label=f"Through origin: E = {slope:.3f}L",
        )

        # Formatting
        ax.set_xlabel("Gauge Length L (m)", fontsize=12)
        ax.set_ylabel("Recoverable Energy E (J)", fontsize=12)
        ax.set_title(f"{group}\nR² = {r_value**2:.4f}", fontsize=14, fontweight="bold")
        ax.legend(fontsize=9, loc="upper left")
        ax.grid(True, alpha=0.3)
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)

        # Print analysis
        print(f"\n{group}")
        print("-" * 60)
        print(f"  Slope (E per meter):     {slope:.4f} J/m")
        print(
            f"  Intercept:               {intercept:.4f} J "
            f"({intercept_percent:.1f}% of mean E)"
        )
        print(f"  R² value:                {r_value**2:.4f}")
        print(f"  Standard error:          {std_err:.4f}")

        # Interpretation
        if r_value**2 > 0.95:
            print("  ✓ Excellent linear fit - scaling is VALID")
        elif r_value**2 > 0.85:
            print("  ⚠ Good linear fit - scaling is reasonable")
        else:
            print("  ✗ Poor linear fit - scaling may not be appropriate")

        if abs(intercept_percent) < 5:
            print("  ✓ Negligible intercept - no significant clamp losses")
        elif abs(intercept_percent) < 15:
            print("  ⚠ Small intercept - minor clamp/crimp losses detected")
        else:
            print("  ✗ Significant intercept - substantial clamp losses")
            print(f"    → Use slope {slope:.4f} J/m, " "ignore intercept for scaling")

    # Save plot
    plt.tight_layout()
    plot_path = output_path / "scaling_validation.png"
    fig.savefig(plot_path, dpi=600, bbox_inches="tight")
    plt.close()

    print("\n" + "=" * 60)
    print(f"Validation plot saved: {plot_path}")
    print("=" * 60 + "\n")

    # Create summary table
    summary_data = []
    for group in groups:
        group_data = df[df["group"] == group]
        l_gauge = group_data["L_gauge_m"].values
        e_sample = group_data["E_sample_J"].values

        slope, intercept, r_value, _, _ = stats.linregress(l_gauge, e_sample)

        summary_data.append(
            {
                "Group": group,
                "E_per_m (J/m)": f"{slope:.4f}",
                "Intercept (J)": f"{intercept:.4f}",
                "R²": f"{r_value**2:.4f}",
                "Scaling Valid?": "Yes" if r_value**2 > 0.85 else "No",
            }
        )

    summary_df = pd.DataFrame(summary_data)
    summary_path = output_path / "scaling_validation_summary.csv"
    summary_df.to_csv(summary_path, index=False)
    print(f"Summary table saved: {summary_path}\n")


def main():
    """Main entry point for scaling validation tool."""
    parser = argparse.ArgumentParser(
        description="Validate linear scaling assumption for energy calculations"
    )
    parser.add_argument(
        "-i", "--input", required=True, help="Path to individual_results.csv"
    )
    parser.add_argument(
        "-o", "--output", default="out", help="Output directory (default: out)"
    )

    args = parser.parse_args()

    analyze_scaling_validity(args.input, args.output)


if __name__ == "__main__":
    main()
