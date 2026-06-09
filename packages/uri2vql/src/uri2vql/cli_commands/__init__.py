"""CLI command runner registry."""

from __future__ import annotations

import argparse
from collections.abc import Callable

from uri2vql.cli_commands.capture import run_capture_screen
from uri2vql.cli_commands.core import run_patch, run_query, run_resolve, run_run
from uri2vql.cli_commands.pipeline import run_capture_and_analyze
from uri2vql.cli_commands.pipeline_analyze import run_pipeline_analyze, run_roundtrip, run_vql_to_image
from uri2vql.cli_commands.window import (
    run_adopt_imgl,
    run_adopt_ui,
    run_analyze_window,
    run_compare_window,
    run_detect_window,
    run_diagnose_window,
    run_refresh_window,
)

CommandRunner = Callable[[argparse.Namespace], int]

COMMAND_RUNNERS: dict[str, CommandRunner] = {
    "query": run_query,
    "patch": run_patch,
    "run": run_run,
    "resolve": run_resolve,
    "capture-screen": run_capture_screen,
    "analyze-window": run_analyze_window,
    "detect-window": run_detect_window,
    "adopt-ui": run_adopt_ui,
    "adopt-imgl": run_adopt_imgl,
    "diagnose-window": run_diagnose_window,
    "compare-window": run_compare_window,
    "refresh-window": run_refresh_window,
    "capture-and-analyze": run_capture_and_analyze,
    "pipeline-analyze": run_pipeline_analyze,
    "vql-to-image": run_vql_to_image,
    "roundtrip": run_roundtrip,
}
