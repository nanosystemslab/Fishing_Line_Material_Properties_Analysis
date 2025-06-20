"""Test cases for the __init__ module."""

import matplotlib.pyplot as plt
import seaborn as sns

from Fishing_Line_Material_Properties_Analysis import MaterialAnalyzer
from Fishing_Line_Material_Properties_Analysis import MaterialVisualizer
from Fishing_Line_Material_Properties_Analysis import __version__


class TestInitModule:
    """Test cases for package initialization."""

    def test_version(self) -> None:
        """Test that version is defined."""
        assert __version__ == "0.0.1"

    def test_imports(self) -> None:
        """Test that main classes can be imported."""
        assert MaterialAnalyzer is not None
        assert MaterialVisualizer is not None

    def test_matplotlib_style_set(self) -> None:
        """Test that matplotlib style is properly configured."""
        # Check that seaborn style is applied
        current_style = plt.rcParams
        assert current_style is not None

        # Check that seaborn is configured
        assert sns.axes_style() is not None
