"""img2nl + screenshot UI detection for VQL."""

from img2vql.adopt import adopt_screenshot
from img2vql.describe_ui import describe_ui_layout
from img2vql.detect import UIElement, detect_ui_elements
from img2vql.diagnose import diagnose_for_vql, diagnose_image
from img2vql.fingerprint import compare_with_program, fingerprint_for_image, load_program_fingerprint
from img2vql.metadata import img2nl_metadata_slice, merge_program_metadata, refresh_program_metadata, save_diagnose_to_program
from img2vql.pipeline import analyze_image_to_vql, image_to_vql, roundtrip_compare, vql_to_image
from img2vql.program import elements_to_vql_program

__all__ = [
    "UIElement",
    "adopt_screenshot",
    "analyze_image_to_vql",
    "compare_with_program",
    "describe_ui_layout",
    "detect_ui_elements",
    "diagnose_for_vql",
    "diagnose_image",
    "elements_to_vql_program",
    "fingerprint_for_image",
    "image_to_vql",
    "img2nl_metadata_slice",
    "load_program_fingerprint",
    "merge_program_metadata",
    "refresh_program_metadata",
    "roundtrip_compare",
    "save_diagnose_to_program",
    "vql_to_image",
]
