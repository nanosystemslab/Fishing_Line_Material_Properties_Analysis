#!/usr/bin/env python3
"""Inspect the individual_results.csv file."""

import pandas as pd

# Load the CSV
df = pd.read_csv('out/individual_results.csv')
df["group"] = df["group"].str.split("_").str[-1]
df["length_mm"] = df["length_mm"].astype(int)
df["run_number"] = df["file"].str.extract(r"--(\d+)\.csv$").astype(int)
df["id"] = df.apply(lambda r: f"G{r.group}-{int(r.length_mm)}-{r.run_number}", axis=1)
# Failure Mode, Failure Location
failure_data = {
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

df[["Failure_Mode", "Failure_Location"]] = pd.DataFrame(
    df["id"].map(failure_data).tolist(), index=df.index
)

print(df.columns)
