#!/usr/bin/env python3

"""Fishing Line Material Properties Analysis Tool.

Unified command-line interface for analyzing and
visualizing fishing line material properties.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

import numpy as np

from . import __version__
from .analysis import MaterialAnalyzer
from .visualization import MaterialVisualizer


def setup_logging(verbosity: int) -> None:
    """Setup logging configuration."""
    log_fmt = "%(levelname)s - %(module)s - %(funcName)s @%(lineno)d: %(message)s"
    logging.basicConfig(
        filename=None, format=log_fmt, level=logging.getLevelName(verbosity)
    )


def parse_command_line() -> Dict[str, Any]:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Analyze and visualize fishing line material properties",
        prog="Fishing_Line_Material_Properties_Analysis",
    )

    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        dest="verbosity",
        help="Verbose output (use -vv for more verbose)",
    )

    # Energy calculation parameters
    parser.add_argument(
        "--efficiency",
        type=float,
        default=0.5,
        help="Energy conversion efficiency (0-1, default: 0.5)",
    )

    parser.add_argument(
        "--alpha",
        type=float,
        default=0.3,
        help="Fraction of local line mass engaged (0-1, default: 0.3)",
    )

    parser.add_argument(
        "--projectile-mass",
        type=float,
        default=0.045,
        help="Projectile mass in kg (default: 0.045 = 45g)",
    )

    # Subcommands
    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    # Material analysis command
    material_parser = subparsers.add_parser(
        "analyze", help="Analyze material properties from test data"
    )
    material_parser.add_argument(
        "-i", "--input", nargs="+", required=True, help="Path(s) to input CSV files"
    )
    material_parser.add_argument(
        "-o", "--output", default="out", help="Output directory (default: out)"
    )
    material_parser.add_argument(
        "--plot-type",
        choices=["single", "multi"],
        default="single",
        help="Plot type: single trace or multiple traces (default: single)",
    )
    material_parser.add_argument(
        "--x-param",
        choices=["Time", "Force", "Stroke", "Stress", "Strain"],
        default="Strain",
        help="X-axis parameter (default: Strain)",
    )
    material_parser.add_argument(
        "--y-param",
        choices=["Time", "Force", "Stroke", "Stress", "Strain"],
        default="Stress",
        help="Y-axis parameter (default: Stress)",
    )

    # Output visualization command
    output_parser = subparsers.add_parser(
        "visualize", help="Visualize analysis output data"
    )
    output_parser.add_argument(
        "-i", "--input", nargs="+", required=True, help="Path(s) to output CSV files"
    )
    output_parser.add_argument(
        "-o", "--output", default="out", help="Output directory (default: out)"
    )
    output_parser.add_argument(
        "--x-param",
        choices=["KE", "V", "D", "L"],
        default="D",
        help="X-axis parameter (default: D)",
    )
    output_parser.add_argument(
        "--y-param",
        choices=["KE", "V", "D", "L"],
        default="KE",
        help="Y-axis parameter (default: KE)",
    )

    # Batch processing command
    batch_parser = subparsers.add_parser(
        "batch", help="Process all data in directory structure"
    )
    batch_parser.add_argument(
        "-d",
        "--data-dir",
        required=True,
        help="Root data directory containing group subdirectories",
    )
    batch_parser.add_argument(
        "-o", "--output", default="out", help="Output directory (default: out)"
    )
    batch_parser.add_argument(
        "--summary",
        action="store_true",
        help="Generate summary statistics across all groups",
    )

    args = vars(parser.parse_args())
    args["verbosity"] = max(0, 30 - 10 * args["verbosity"])

    return args


def handle_analyze_command(args: Dict[str, Any]) -> int:
    """Handle the analyze command."""
    analyzer = MaterialAnalyzer(
        efficiency=args.get("efficiency", 0.5),
        alpha_mass_fraction=args.get("alpha", 0.3),
        projectile_mass_kg=args.get("projectile_mass", 0.045),
    )
    visualizer = MaterialVisualizer(output_dir=args["output"])

    individual_results = []

    try:
        if args["plot_type"] == "single":
            for input_file in args["input"]:
                data = analyzer.load_file(input_file)

                # Print enhanced material properties
                print(
                    f"File: {input_file} | "
                    f"Force: {data.meta.max_force:.2f}N | "
                    f"Modulus: {data.meta.modulus * 1e-6:.2f}MPa | "
                    f"Yield: {data.meta.yield_stress * 1e-6:.2f}MPa | "
                    f"E/m: {data.meta.E_per_m:.4f}J/m | "
                    f"V@1m: {data.meta.velocities[1]:.2f}m/s | "
                    f"V@20m: {data.meta.velocities[5]:.2f}m/s | "
                    f"Length: {data.meta.length:.1f}mm | "
                    f"Diameter: {data.meta.size}mm"
                )

                # Collect data for CSV with both 1m and 20m velocities
                individual_results.append(
                    {
                        "file": input_file,
                        "group": visualizer._extract_group_from_path(input_file),
                        "length": visualizer._extract_length_from_path(input_file),
                        "max_force_N": data.meta.max_force,
                        "modulus_MPa": data.meta.modulus * 1e-6,
                        "yield_stress_MPa": data.meta.yield_stress * 1e-6,
                        "E_sample_J": data.meta.E_sample_J,
                        "E_per_m_J_m": data.meta.E_per_m,
                        "L_gauge_m": data.meta.L_gauge_m,
                        "velocity_1m_m_s": data.meta.velocities[1],
                        "velocity_20m_m_s": data.meta.velocities[5],
                        "kinetic_energy_1m_J": data.meta.kinetic_energies[1],
                        "kinetic_energy_20m_J": data.meta.kinetic_energies[5],
                        "length_mm": data.meta.length,
                        "diameter_mm": data.meta.size,
                    }
                )

                visualizer.plot_single_trace(
                    data=data, x_param=args["x_param"], y_param=args["y_param"]
                )
        else:  # multi
            data_list = [analyzer.load_file(f) for f in args["input"]]

            # Print summary statistics
            e_per_m_values = [d.meta.E_per_m for d in data_list]

            # Get velocities at different lengths - index 5 is 20m
            # L_eff_options = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0]
            vel_1m_values = [d.meta.velocities[1] for d in data_list]  # 1m is index 1
            vel_20m_values = [d.meta.velocities[5] for d in data_list]  # 20m is index 5

            force_values = [d.meta.max_force for d in data_list]
            modulus_values = [d.meta.modulus for d in data_list]
            yield_values = [d.meta.yield_stress for d in data_list]

            print(
                f"Multi-sample | Samples: {len(data_list)} | "
                f"Avg E/m: {np.mean(e_per_m_values):.4f}±{np.std(e_per_m_values):.4f}J/m | "  # noqa: B950
                f"Avg V@20m: {np.mean(vel_20m_values):.2f}±{np.std(vel_20m_values):.2f}m/s | "  # noqa: B950
                f"Avg Force: {np.mean(force_values):.2f}±{np.std(force_values):.2f}N"
            )

            # Collect individual data for CSV
            for data in data_list:
                individual_results.append(
                    {
                        "file": data.meta.filepath,
                        "group": visualizer._extract_group_from_path(
                            data.meta.filepath
                        ),
                        "length": visualizer._extract_length_from_path(
                            data.meta.filepath
                        ),
                        "max_force_N": data.meta.max_force,
                        "modulus_MPa": data.meta.modulus * 1e-6,
                        "yield_stress_MPa": data.meta.yield_stress * 1e-6,
                        "E_sample_J": data.meta.E_sample_J,
                        "E_per_m_J_m": data.meta.E_per_m,
                        "L_gauge_m": data.meta.L_gauge_m,
                        "velocity_1m_m_s": data.meta.velocities[1],  # 1m
                        "velocity_20m_m_s": data.meta.velocities[5],  # 20m
                        "kinetic_energy_1m_J": data.meta.kinetic_energies[1],
                        "kinetic_energy_20m_J": data.meta.kinetic_energies[5],
                        "length_mm": data.meta.length,
                        "diameter_mm": data.meta.size,
                    }
                )

            # Collect multi-run average for separate CSV
            if data_list:
                first_data = data_list[0]
                multi_result = {
                    "group": visualizer._extract_group_from_path(
                        first_data.meta.filepath
                    ),
                    "length": visualizer._extract_length_from_path(
                        first_data.meta.filepath
                    ),
                    "sample_count": len(data_list),
                    "avg_max_force_N": np.mean(force_values),
                    "std_max_force_N": np.std(force_values),
                    "avg_modulus_MPa": np.mean(modulus_values) * 1e-6,
                    "std_modulus_MPa": np.std(modulus_values) * 1e-6,
                    "avg_yield_stress_MPa": np.mean(yield_values) * 1e-6,
                    "std_yield_stress_MPa": np.std(yield_values) * 1e-6,
                    "avg_E_per_m_J_m": np.mean(e_per_m_values),
                    "std_E_per_m_J_m": np.std(e_per_m_values),
                    "avg_velocity_1m_m_s": np.mean(vel_1m_values),
                    "std_velocity_1m_m_s": np.std(vel_1m_values),
                    "avg_velocity_20m_m_s": np.mean(vel_20m_values),
                    "std_velocity_20m_m_s": np.std(vel_20m_values),
                    "avg_kinetic_energy_1m_J": np.mean(
                        [d.meta.kinetic_energy for d in data_list]
                    ),
                    "std_kinetic_energy_1m_J": np.std(
                        [d.meta.kinetic_energy for d in data_list]
                    ),
                    "length_mm": first_data.meta.length,
                    "diameter_mm": first_data.meta.size,
                }

                # Save multi-run average to CSV
                _save_multi_results_csv([multi_result], args["output"])

            visualizer.plot_multi_trace(
                data_list=data_list, x_param=args["x_param"], y_param=args["y_param"]
            )

        # Save individual results to CSV
        if individual_results:
            _save_individual_results_csv(individual_results, args["output"])

        logging.info(f"Analysis complete. Results saved to {args['output']}")
        return 0

    except Exception as e:
        logging.error(f"Analysis failed: {e}")
        return 1


def _save_individual_results_csv(results: List[Any], output_dir: str) -> None:
    """Save individual test results to CSV file."""
    import pandas as pd

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    df = pd.DataFrame(results)
    csv_path = output_path / "individual_results.csv"

    # Append to existing file or create new one
    if csv_path.exists():
        existing_df = pd.read_csv(csv_path)
        df = pd.concat([existing_df, df], ignore_index=True)

    df.to_csv(csv_path, index=False)
    logging.info(f"Individual results saved to {csv_path}")


def _save_multi_results_csv(results: List[Any], output_dir: str) -> None:
    """Save multi-run average results to CSV file."""
    import pandas as pd

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    df = pd.DataFrame(results)
    csv_path = output_path / "multi_run_averages.csv"

    # Append to existing file or create new one
    if csv_path.exists():
        existing_df = pd.read_csv(csv_path)
        df = pd.concat([existing_df, df], ignore_index=True)

    df.to_csv(csv_path, index=False)
    logging.info(f"Multi-run averages saved to {csv_path}")


def handle_visualize_command(args: Dict[str, Any]) -> int:
    """Handle the visualize command."""
    visualizer = MaterialVisualizer(output_dir=args["output"])

    try:
        for input_file in args["input"]:
            visualizer.plot_output_data(
                filepath=input_file, x_param=args["x_param"], y_param=args["y_param"]
            )

        logging.info(f"Visualization complete. Results saved to {args['output']}")
        return 0

    except Exception as e:
        logging.error(f"Visualization failed: {e}")
        return 1


def handle_batch_command(args: Dict[str, Any]) -> int:
    """Handle the batch processing command."""
    analyzer = MaterialAnalyzer(
        efficiency=args.get("efficiency", 0.5),
        alpha_mass_fraction=args.get("alpha", 0.3),
        projectile_mass_kg=args.get("projectile_mass", 0.045),
    )
    visualizer = MaterialVisualizer(output_dir=args["output"])

    try:
        data_dir = Path(args["data_dir"])
        if not data_dir.exists():
            logging.error(f"Data directory {data_dir} does not exist")
            return 1

        # Process each group directory
        group_results: Dict[str, Any] = {}
        for group_dir in data_dir.glob("group_*"):
            if not group_dir.is_dir():
                continue

            logging.info(f"Processing {group_dir.name}")
            group_results[group_dir.name] = {}

            # Process each length subdirectory
            for length_dir in group_dir.glob("*in"):
                if not length_dir.is_dir():
                    continue

                logging.info(f"  Processing {length_dir.name}")

                # Get all CSV files in this length directory
                csv_files = list(length_dir.glob("*.csv"))
                if not csv_files:
                    continue

                # Convert Path objects to strings for the analyzer
                csv_file_paths = [str(f) for f in csv_files]

                # Load and analyze data
                data_list = [analyzer.load_file(f) for f in csv_file_paths]

                # Generate multi-trace plot for this length/group combination
                visualizer.plot_multi_trace(
                    data_list=data_list,
                    x_param="Strain",
                    y_param="Stress",
                    title_suffix=f"{group_dir.name}_{length_dir.name}",
                )

                # Calculate summary statistics
                stats = analyzer.calculate_summary_stats(data_list)
                group_results[group_dir.name][length_dir.name] = stats

        if args["summary"]:
            # Generate summary report
            analyzer.generate_summary_report(group_results, args["output"])

        logging.info(f"Batch processing complete. Results saved to {args['output']}")
        return 0

    except Exception as e:
        logging.error(f"Batch processing failed: {e}")
        return 1


def main() -> int:
    """Main entry point."""
    try:
        args = parse_command_line()
        setup_logging(args["verbosity"])

        logging.info(f"Starting command: {args['command']}")
        logging.info(f"Arguments: {args}")

        # Create output directory
        output_dir = Path(args.get("output", "out"))
        output_dir.mkdir(exist_ok=True)
        logging.info(f"Output directory: {output_dir}")

        # Route to appropriate handler
        if args["command"] == "analyze":
            result = handle_analyze_command(args)
            logging.info(f"Analyze command completed with result: {result}")
            return result
        elif args["command"] == "visualize":
            result = handle_visualize_command(args)
            logging.info(f"Visualize command completed with result: {result}")
            return result
        elif args["command"] == "batch":
            result = handle_batch_command(args)
            logging.info(f"Batch command completed with result: {result}")
            return result
        else:
            logging.error(f"Unknown command: {args['command']}")
            return 1
    except Exception as e:
        logging.error(f"Main function failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nExited by user")
        sys.exit(1)
