"""Fishing Line Material Properties Analysis package."""

# Set global plotting style
import matplotlib.pyplot as plt
import seaborn as sns

from .analysis import MaterialAnalyzer
from .visualization import MaterialVisualizer


__version__ = "0.0.1"

__all__ = ["MaterialAnalyzer", "MaterialVisualizer", "__version__"]

# Set global seaborn style
sns.set_style("whitegrid")
plt.style.use("seaborn-v0_8-whitegrid")
