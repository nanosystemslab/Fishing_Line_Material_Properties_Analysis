#!/usr/bin/env python3
"""Generate LaTeX longtable from individual_results.csv for publication."""

import argparse
from pathlib import Path

import pandas as pd


class LaTeXTableGenerator:
    """Generate formatted LaTeX longtable from analysis results."""
    
    def __init__(self, csv_path: str, output_path: str = "results_table.tex"):
        """Initialize the generator.
        
        Args:
            csv_path: Path to individual_results.csv
            output_path: Path for output LaTeX file
        """
        self.csv_path = Path(csv_path)
        self.output_path = Path(output_path)
        self.df = None
        
        # Manual failure data dictionary
        # Format: "G{group}-{length_mm}-{run_number}": ("Mode", "Location")
        self.failure_data = {
            # Group 1 - 127mm (5in)
            "G1-127-0": ("Break", "Top Crimp"),
            "G1-127-1": ("Slip", "Bot Crimp"),
            "G1-127-2": ("Break", "Top Crimp"),
            "G1-127-3": ("Break", "Bot Crimp"),
            "G1-127-4": ("Slip", "Bot Crimp"),
            "G1-127-5": ("Slip", "Bot Crimp"),
            "G1-127-6": ("Slip", "Bot Crimp"),
            "G1-127-7": ("Slip", "Bot Crimp"),
            "G1-127-8": ("Slip", "Bot Crimp"),
            "G1-127-9": ("Slip", "Top Crimp"),
            
            # Group 1 - 254mm (10in)
            "G1-254-0": ("Break", "Bot Crimp"),
            "G1-254-1": ("Break", "Bot Crimp"),
            "G1-254-2": ("Slip", "Top Crimp"),
            "G1-254-3": ("Break", "Top Crimp"),
            "G1-254-4": ("Slip", "Bot Crimp"),
            "G1-254-5": ("Slip", "Bot Crimp"),
            "G1-254-6": ("Break", "Bot Crimp"),
            "G1-254-7": ("Slip", "Bot Crimp"),
            "G1-254-8": ("Slip", "Top Crimp"),
            "G1-254-9": ("Slip", "Bot Crimp"),
            
            # Group 1 - 508mm (20in)
            "G1-508-0": ("Slip", "Top Crimp"),
            "G1-508-1": ("Slip", "Bot Crimp"),
            "G1-508-2": ("Slip", "Top Crimp"),
            "G1-508-3": ("Slip", "Top Crimp"),
            "G1-508-4": ("Break", "Top Loop"),
            "G1-508-5": ("Break", "Top Crimp"),
            "G1-508-6": ("Slip", "Bot Crimp"),
            "G1-508-7": ("Slip", "Bot Crimp"),
            "G1-508-8": ("Slip", "Top Crimp"),
            "G1-508-9": ("Slip", "Top Crimp"),
            
            # Group 2 - 127mm (5in)
            "G2-127-0": ("Slip", "Bot Crimp"),
            "G2-127-1": ("Slip", "Top Crimp"),
            "G2-127-2": ("Break", "Top Crimp"),
            "G2-127-3": ("Slip", "Top Crimp"),
            "G2-127-4": ("Break", "Top Crimp"),
            "G2-127-5": ("Slip", "Bot Crimp"),
            "G2-127-6": ("Break", "Bot Crimp"),
            "G2-127-7": ("Break", "Top Crimp"),
            "G2-127-8": ("Slip", "Top Crimp"),
            "G2-127-9": ("Break", "Top Crimp"),
            
            # Group 2 - 254mm (10in)
            "G2-254-0": ("Break", "Top Crimp"),
            "G2-254-1": ("Break", "Top Crimp"),
            "G2-254-2": ("Slip", "Top Crimp"),
            "G2-254-3": ("Slip", "Bot Crimp"),
            "G2-254-4": ("Slip", "Top Crimp"),
            "G2-254-5": ("Break", "Bot Crimp"),
            "G2-254-6": ("Slip", "Top Crimp"),
            "G2-254-7": ("Slip", "Bot Crimp"),
            "G2-254-8": ("Slip", "Bot Crimp"),
            "G2-254-9": ("Break", "Top Crimp"),
            
            # Group 2 - 508mm (20in)
            "G2-508-0": ("Break", "Top Crimp"),
            "G2-508-1": ("Break", "Bot Crimp"),
            "G2-508-2": ("Break", "Top Crimp"),
            "G2-508-3": ("Break", "Top Crimp"),
            "G2-508-4": ("Break", "Bot Crimp"),
            "G2-508-5": ("Break", "Bot Crimp"),
            "G2-508-6": ("Break", "Top Crimp"),
            "G2-508-7": ("Break", "Bot Crimp"),
            "G2-508-8": ("Break", "Bot Crimp"),
            "G2-508-9": ("Break", "Bot Crimp"),
            
            # Group 3 - 127mm (5in)
            "G3-127-0": ("Slip", "Bot Crimp"),
            "G3-127-1": ("Slip", "Bot Crimp"),
            "G3-127-2": ("Slip", "Bot Crimp"),
            "G3-127-3": ("Slip", "Top Crimp"),
            "G3-127-4": ("Slip", "Top Crimp"),
            "G3-127-5": ("Slip", "Bot Crimp"),
            "G3-127-6": ("Slip", "Bot Crimp"),
            "G3-127-7": ("Slip", "Top Crimp"),
            "G3-127-8": ("Slip", "Top Crimp"),
            "G3-127-9": ("Slip", "Top Crimp"),
            
            # Group 3 - 254mm (10in)
            "G3-254-0": ("Slip", "Bot Crimp"),
            "G3-254-1": ("Slip", "Bot Crimp"),
            "G3-254-2": ("Slip", "Top Crimp"),
            "G3-254-3": ("Slip", "Bot Crimp"),
            "G3-254-4": ("Slip", "Bot Crimp"),
            "G3-254-5": ("Slip", "Top Crimp"),
            "G3-254-6": ("Slip", "Bot Crimp"),
            "G3-254-7": ("Slip", "Top Crimp"),
            "G3-254-8": ("Slip", "Top Crimp"),
            "G3-254-9": ("Slip", "Top Crimp"),
            
            # Group 3 - 508mm (20in)
            "G3-508-0": ("Slip", "Top Crimp"),
            "G3-508-1": ("Slip", "Bot Crimp"),
            "G3-508-2": ("Slip", "Top Crimp"),
            "G3-508-3": ("Slip", "Bot Crimp"),
            "G3-508-4": ("Slip", "Bot Crimp"),
            "G3-508-5": ("Slip", "Bot Crimp"),
            "G3-508-6": ("Slip", "Top Crimp"),
            "G3-508-7": ("Slip", "Top Crimp"),
            "G3-508-8": ("Slip", "Bot Crimp"),
            "G3-508-9": ("Slip", "Top Crimp"),
        }
        
    def load_data(self) -> None:
        """Load and prepare the CSV data."""
        df = pd.read_csv(self.csv_path)
        
        # Extract group number (e.g., "group_1" -> "1")
        df["group"] = df["group"].str.split("_").str[-1]
        
        # Convert length_mm to integer
        df["length_mm"] = df["length_mm"].astype(int)
        
        # Extract run number from filename (e.g., "test--line-crimp-21--0.csv" -> 0)
        df["run_number"] = df["file"].str.extract(r"--(\d+)\.csv$").astype(int)
        
        # Create sample ID (e.g., "G1-127-0")
        df["id"] = df.apply(lambda r: f"G{r.group}-{int(r.length_mm)}-{r.run_number}", axis=1)
        
        # Map failure data
        df[["Failure_Mode", "Failure_Location"]] = pd.DataFrame(
            df["id"].map(self.failure_data).tolist(), index=df.index
        )
        
        # Sort by group, length, and run number
        df["group_num"] = df["group"].astype(int)
        df = df.sort_values(['group_num', 'length_mm', 'run_number'])
        
        self.df = df
        
    def generate_table(self) -> str:
        """Generate the complete LaTeX longtable."""
        lines = []
        
        # Add landscape environment with smaller font
        lines.append(r"\begin{landscape}")
        lines.append(r"\small")  # or use \footnotesize for even smaller
        lines.append("")
        
        # Table header
        lines.append(r"\begin{longtable}{@{}ccccccccccccccc@{}}")
        lines.append(r"\caption{Complete tensile testing dataset for all crimped line samples showing specimen dimensions, mechanical properties (force, modulus, yield strength), energy storage characteristics, and calculated kinetic energy and velocity for 1m and 20m effective lengths with a 45g projectile mass} \\")
        lines.append(r"\toprule")
        lines.append(r"Sample & Diameter & Length & Max Force & Modulus & Yield & $E_{sample}$ & $E/m$ & $L_{gauge}$ & KE$_{1m}$ & V$_{1m}$ & KE$_{20m}$ & V$_{20m}$ & Failure & Failure \\")
        lines.append(r"ID & [mm] & [mm] & [N] & [MPa] & [MPa] & [J] & [J/m] & [m] & [J] & [m/s] & [J] & [m/s] & Mode & Location\\")
        lines.append(r"\midrule")
        lines.append(r"\endfirsthead")
        
        # Continued header
        lines.append(r"\multicolumn{15}{c}{\tablename\ \thetable\ -- \textit{Continued from previous page}} \\")
        lines.append(r"\toprule")
        lines.append(r"Sample & Diameter & Length & Max Force & Modulus & Yield & $E_{sample}$ & $E/m$ & $L_{gauge}$ & KE$_{1m}$ & V$_{1m}$ & KE$_{20m}$ & V$_{20m}$ & Failure & Failure \\")
        lines.append(r"ID & [mm] & [mm] & [N] & [MPa] & [MPa] & [J] & [J/m] & [m] & [J] & [m/s] & [J] & [m/s] & Mode & Location\\")
        lines.append(r"\midrule")
        lines.append(r"\endhead")
        
        # Footer for continuation
        lines.append(r"\midrule")
        lines.append(r"\multicolumn{15}{r}{\textit{Continued on next page}} \\")
        lines.append(r"\endfoot")
        
        # Last footer
        lines.append(r"\bottomrule")
        lines.append(r"\endlastfoot")
        lines.append("")
        
        # Data rows grouped by group and length
        current_group = None
        current_length = None
        
        for _, row in self.df.iterrows():
            group_num = row['group_num']
            length_mm = row['length_mm']
            
            # Add section comments for readability
            if group_num != current_group or length_mm != current_length:
                if current_group is not None:
                    lines.append("")
                    
                # Determine crimp type from group
                crimp_type = "Hand Crimped"
                if group_num == 3:
                    crimp_type = "Bench Crimped"
                
                # Calculate inches for comment
                length_inches = int(length_mm / 25.4)
                
                lines.append(f"% Group {group_num} Data ({row['diameter_mm']}mm, {crimp_type}) - {length_mm}mm gauge length ({length_inches}in)")
                
                current_group = group_num
                current_length = length_mm
            
            # Format the data row with all columns
            data_row = (
                f"{row['id']} & "
                f"{row['diameter_mm']:.1f} & "
                f"{int(row['length_mm'])} & "
                f"{row['max_force_N']:.1f} & "
                f"{row['modulus_MPa']:.2f} & "
                f"{row['yield_stress_MPa']:.2f} & "
                f"{row['E_sample_J']:.2f} & "
                f"{row['E_per_m_J_m']:.4f} & "
                f"{row['L_gauge_m']:.4f} & "
                f"{row['kinetic_energy_1m_J']:.2f} & "
                f"{row['velocity_1m_m_s']:.2f} & "
                f"{row['kinetic_energy_20m_J']:.2f} & "
                f"{row['velocity_20m_m_s']:.2f} & "
                f"{row['Failure_Mode']} & "
                f"{row['Failure_Location']} \\\\"
            )
            
            lines.append(data_row)
        
        # Table footer
        lines.append("")
        lines.append(r"\label{tab:complete_tensile_data}")
        lines.append(r"\end{longtable}")
        lines.append("")
        lines.append(r"\end{landscape}")
        
        return "\n".join(lines)
    
    def save_table(self, content: str) -> None:
        """Save the generated table to file."""
        self.output_path.write_text(content)
        print(f"\n✓ LaTeX table saved to: {self.output_path}")
        print(f"  Total samples: {len(self.df)}")
        print(f"  Groups: {sorted(self.df['group_num'].unique())}")
        
        # Calculate unique lengths in inches
        unique_lengths = sorted([int(l/25.4) for l in self.df['length_mm'].unique()])
        print(f"  Lengths: {unique_lengths} inches")
    
    def generate_summary_stats(self) -> str:
        """Generate summary statistics by group and length."""
        lines = ["\n% Summary Statistics\n"]
        
        for group_num in sorted(self.df['group_num'].unique()):
            group_data = self.df[self.df['group_num'] == group_num]
            lines.append(f"% Group {group_num}:")
            
            for length_mm in sorted(group_data['length_mm'].unique()):
                length_data = group_data[group_data['length_mm'] == length_mm]
                
                n = len(length_data)
                avg_force = length_data['max_force_N'].mean()
                std_force = length_data['max_force_N'].std()
                avg_modulus = length_data['modulus_MPa'].mean()
                std_modulus = length_data['modulus_MPa'].std()
                avg_e_per_m = length_data['E_per_m_J_m'].mean()
                std_e_per_m = length_data['E_per_m_J_m'].std()
                avg_vel_1m = length_data['velocity_1m_m_s'].mean()
                std_vel_1m = length_data['velocity_1m_m_s'].std()
                avg_vel_20m = length_data['velocity_20m_m_s'].mean()
                std_vel_20m = length_data['velocity_20m_m_s'].std()
                
                lines.append(
                    f"%   {length_mm}mm (n={n}): "
                    f"Force = {avg_force:.1f}±{std_force:.1f}N, "
                    f"Modulus = {avg_modulus:.2f}±{std_modulus:.2f}MPa, "
                    f"E/m = {avg_e_per_m:.4f}±{std_e_per_m:.4f}J/m"
                )
                lines.append(
                    f"%      V@1m = {avg_vel_1m:.1f}±{std_vel_1m:.1f}m/s, "
                    f"V@20m = {avg_vel_20m:.1f}±{std_vel_20m:.1f}m/s"
                )
            lines.append("%")
        
        return "\n".join(lines)
    
    def run(self, include_stats: bool = True) -> None:
        """Run the complete table generation process."""
        print(f"Loading data from: {self.csv_path}")
        self.load_data()
        
        print("Generating LaTeX table...")
        table_content = self.generate_table()
        
        if include_stats:
            stats_content = self.generate_summary_stats()
            table_content = table_content + "\n" + stats_content
        
        self.save_table(table_content)
        
        # Check for any missing failure data
        missing_count = self.df['Failure_Mode'].isna().sum()
        
        if missing_count > 0:
            print(f"\n⚠ WARNING: Missing failure data for {missing_count} samples")
            missing_ids = self.df[self.df['Failure_Mode'].isna()]['id'].tolist()
            for sample_id in missing_ids[:10]:
                print(f"    {sample_id}")
            if len(missing_ids) > 10:
                print(f"    ... and {len(missing_ids) - 10} more")
        else:
            print(f"\n✓ All {len(self.df)} samples have failure data!")
        
        print("\n✓ Done! You can now \\input{} this file in your LaTeX document.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate LaTeX longtable from individual_results.csv"
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to individual_results.csv"
    )
    parser.add_argument(
        "-o", "--output",
        default="results_table.tex",
        help="Output LaTeX file path (default: results_table.tex)"
    )
    parser.add_argument(
        "--no-stats",
        action="store_true",
        help="Don't include summary statistics comments"
    )
    
    args = parser.parse_args()
    
    generator = LaTeXTableGenerator(args.input, args.output)
    generator.run(include_stats=not args.no_stats)


if __name__ == "__main__":
    main()
