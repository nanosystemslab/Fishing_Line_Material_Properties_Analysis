#!/usr/bin/env python3
"""Generate LaTeX summary tables from multi_run_averages.csv."""

import argparse
from pathlib import Path

import pandas as pd


class SummaryTablesGenerator:
    """Generate formatted LaTeX summary tables from analysis results."""
    
    def __init__(self, csv_path: str, output_path: str = "summary_tables.tex"):
        """Initialize the generator.
        
        Args:
            csv_path: Path to multi_run_averages.csv
            output_path: Path for output LaTeX file
        """
        self.csv_path = Path(csv_path)
        self.output_path = Path(output_path)
        self.df = None
        
    def load_data(self) -> None:
        """Load and prepare the CSV data."""
        self.df = pd.read_csv(self.csv_path)
        
        # Extract group number
        self.df['group_num'] = self.df['group'].str.extract(r'group_(\d+)')[0].astype(int)
        
        # Convert length to mm (extract from string like "5in")
        self.df['length_inches'] = self.df['length'].str.extract(r'(\d+)in')[0].astype(int)
        self.df['length_mm_calc'] = (self.df['length_inches'] * 25.4).round(0).astype(int)
        
        # Sort by group and length
        self.df = self.df.sort_values(['group_num', 'length_mm_calc'])
        
    def generate_tensile_results_table(self) -> str:
        """Generate Table 1: Tensile testing results."""
        lines = []
        
        lines.append(r"\begin{table}[H]")
        lines.append(r"\centering")
        lines.append(r"\scriptsize")
        lines.append(r"\begin{tabular}{l|c|c|c|c}")
        lines.append(r"\hline")
        lines.append(r"    Group & Line Diameter [mm]& Gauge Length [mm]& Average Max Force [N]& Average Stroke [mm] \\")
        lines.append(r"\hline")
        
        # Group data by group number
        for group_num in sorted(self.df['group_num'].unique()):
            group_data = self.df[self.df['group_num'] == group_num].copy()
            
            # Determine crimp type
            if group_num == 3:
                crimp_type = "Bench Crimped"
            else:
                crimp_type = "Hand Crimped"
            
            # Get diameter (should be same for all rows in group)
            diameter = group_data['diameter_mm'].iloc[0]
            
            # First row of group
            first_row = group_data.iloc[0]
            
            # Calculate average stroke from E_sample and max_force
            # Stroke ≈ 2 * E_sample / F_max (approximation from triangular load curve)
            avg_stroke_0 = (2 * first_row['avg_kinetic_energy_1m_J'] * 1000 / first_row['avg_max_force_N'])
            
            lines.append(
                f"{group_num} ({crimp_type}) & "
                f"{diameter:.1f} & "
                f"{int(first_row['length_mm'])} & "
                f"{first_row['avg_max_force_N']:.1f} & "
                f"{avg_stroke_0:.1f} \\\\"
            )
            
            # Remaining rows (no group label, just indent)
            for idx in range(1, len(group_data)):
                row = group_data.iloc[idx]
                avg_stroke = (2 * row['avg_kinetic_energy_1m_J'] * 1000 / row['avg_max_force_N'])
                
                lines.append(
                    f"                 & "
                    f"    & "
                    f"{int(row['length_mm'])} & "
                    f"{row['avg_max_force_N']:.1f} & "
                    f"{avg_stroke:.1f} \\\\"
                )
            
            lines.append(r"\hline")
        
        lines.append(r"\end{tabular}")
        lines.append(r"\caption{Tensile testing results for monofilament fishing lines across different crimping methods and line diameters. By testing different gauge lengths we see that the maximum force does not experience large variation, indicating that the crimp serves as the limiting factor in failure rather than the bulk line properties.}")
        lines.append(r"\label{tab:tensile_results}")
        lines.append(r"\end{table}")
        
        return "\n".join(lines)
    
    def generate_energy_calc_table_for_group(self, group_num: int) -> str:
        """Generate energy storage and velocity calculations table for a specific group.

        Args:
            group_num: Group number to generate table for (2 or 3)

        Returns:
            LaTeX table string
        """
        lines = []

        # Filter for specified group
        group_data = self.df[self.df['group_num'] == group_num].copy()

        if len(group_data) == 0:
            print(f"Warning: No Group {group_num} data found")
            return ""

        # Get group details
        diameter = group_data['diameter_mm'].iloc[0]
        crimp_type = "bench-crimped" if group_num == 3 else "hand-crimped"
        label_suffix = "group3" if group_num == 3 else "group2"

        lines.append(r"\vspace{1em}")
        lines.append(r"\begin{table}[H]")
        lines.append(r"\centering")
        lines.append(r"\scriptsize")
        lines.append(r"\begin{tabular}{l|c|c|c}")
        lines.append(r"\hline")
        lines.append(r"    Gauge Length [mm]& Average Max Force [N]& Energy per Meter [J/m]& Velocity at 20m [m/s]\\")
        lines.append(r"\hline")

        # Add rows for each length
        total_force = 0
        total_e_per_m = 0
        total_vel = 0
        n_rows = len(group_data)

        for _, row in group_data.iterrows():
            # Calculate SEM from SD
            n = row['sample_count']
            sem_force = row['std_max_force_N'] / (n ** 0.5)
            sem_e_per_m = row['std_E_per_m_J_m'] / (n ** 0.5)
            sem_vel_20m = row['std_velocity_20m_m_s'] / (n ** 0.5)

            lines.append(
                f"{int(row['length_mm'])} & "
                f"{row['avg_max_force_N']:.1f} ± {sem_force:.1f} & "
                f"{row['avg_E_per_m_J_m']:.2f} ± {sem_e_per_m:.2f} & "
                f"{row['avg_velocity_20m_m_s']:.1f} ± {sem_vel_20m:.1f} \\\\"
            )

            total_force += row['avg_max_force_N']
            total_e_per_m += row['avg_E_per_m_J_m']
            total_vel += row['avg_velocity_20m_m_s']

        # Add overall average row
        lines.append(r"\hline")
        lines.append(
            f"\\textbf{{Overall Average}} & "
            f"\\textbf{{{total_force/n_rows:.0f}}} & "
            f"\\textbf{{{total_e_per_m/n_rows:.2f}}} & "
            f"\\textbf{{{total_vel/n_rows:.1f}}} \\\\"
        )
        lines.append(r"\hline")

        lines.append(r"\end{tabular}")
        lines.append(
            f"    \\caption{{Energy storage and flyback velocity calculations for a {diameter:.1f} mm "
            f"{crimp_type} monofilament line with a 45 g weight. Values are calculated using the "
            f"maximum force data from Group {group_num} in Table~\\ref{{tab:tensile_results}}, "
            f"assuming a 20 m line length and that all stored energy is fully transferred to the "
            f"45 g mass. Uncertainties shown are standard errors of the mean (SEM)."
            "}}"
        )
        lines.append(f"\\label{{tab:energy_calc_{label_suffix}}}")
        lines.append(r"\end{table}")

        return "\n".join(lines)

    def generate_energy_calc_table(self) -> str:
        """Generate Table 2: Energy storage and velocity calculations for Group 3."""
        return self.generate_energy_calc_table_for_group(3)
    
    def generate_all_tables(self) -> str:
        """Generate all summary tables."""
        table1 = self.generate_tensile_results_table()
        table2_group2 = self.generate_energy_calc_table_for_group(2)  # 2.3mm hand-crimped
        table2_group3 = self.generate_energy_calc_table_for_group(3)  # 2.1mm bench-crimped

        return f"{table1}\n{table2_group2}\n{table2_group3}"
    
    def save_tables(self, content: str) -> None:
        """Save the generated tables to file."""
        self.output_path.write_text(content)
        print(f"\n✓ Summary tables saved to: {self.output_path}")
        print(f"  Groups processed: {sorted(self.df['group_num'].unique())}")
        print(f"  Total rows: {len(self.df)}")
    
    def run(self) -> None:
        """Run the complete table generation process."""
        print(f"Loading data from: {self.csv_path}")
        self.load_data()
        
        print("Generating summary tables...")
        tables_content = self.generate_all_tables()
        
        self.save_tables(tables_content)
        
        print("\n✓ Done! You can now \\input{} this file in your LaTeX document.")
        print("\nGenerated tables:")
        print("  - Table 1: Tensile testing results (all groups)")
        print("  - Table 2: Energy calculations (Group 2 - 2.3mm hand-crimped)")
        print("  - Table 3: Energy calculations (Group 3 - 2.1mm bench-crimped)")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate LaTeX summary tables from multi_run_averages.csv"
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to multi_run_averages.csv"
    )
    parser.add_argument(
        "-o", "--output",
        default="summary_tables.tex",
        help="Output LaTeX file path (default: summary_tables.tex)"
    )
    
    args = parser.parse_args()
    
    generator = SummaryTablesGenerator(args.input, args.output)
    generator.run()


if __name__ == "__main__":
    main()
