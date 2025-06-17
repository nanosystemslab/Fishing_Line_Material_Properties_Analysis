"""Test cases for the __main__ module."""

import sys
from typing import Any
from unittest.mock import patch

from Fishing_Line_Material_Properties_Analysis import __main__


def test_main_help(capfd: Any) -> None:
    """It prints help and exits successfully."""
    # Mock sys.argv to provide the --help argument
    with patch.object(
        sys, "argv", ["Fishing_Line_Material_Properties_Analysis", "--help"]
    ):
        try:
            __main__.main()
        except SystemExit as e:
            # --help exits with code 0, which is expected
            assert e.code == 0

    out, err = capfd.readouterr()
    # Check that help output was printed
    output = out + err
    assert "usage:" in output
    assert "Analyze and visualize fishing line material properties" in output


def test_main_version(capfd: Any) -> None:
    """It prints version and exits successfully."""
    # Test the version flag
    with patch.object(
        sys, "argv", ["Fishing_Line_Material_Properties_Analysis", "--version"]
    ):
        try:
            __main__.main()
        except SystemExit as e:
            # --version exits with code 0
            assert e.code == 0

    out, err = capfd.readouterr()
    # Check that version was printed
    output = out + err
    assert "0.0.1" in output or "Fishing_Line_Material_Properties_Analysis" in output


def test_main_no_args(capfd: Any) -> None:
    """It shows error when no command is provided."""
    # Test with no arguments (should show error)
    with patch.object(sys, "argv", ["Fishing_Line_Material_Properties_Analysis"]):
        try:
            __main__.main()
        except SystemExit as e:
            # Should exit with error code 2 (argparse error)
            assert e.code == 2

    out, err = capfd.readouterr()
    # Check that error about missing command was printed
    output = out + err
    assert (
        "required: command" in output
        or "the following arguments are required" in output
    )


def test_main_analyze_missing_input() -> None:
    """It returns error code when analyze command is missing required input."""
    # Test analyze command without required --input argument
    with patch.object(
        sys, "argv", ["Fishing_Line_Material_Properties_Analysis", "analyze"]
    ):
        try:
            __main__.main()
        except SystemExit as e:
            # Should exit with error code 2 (argparse error)
            assert e.code == 2
