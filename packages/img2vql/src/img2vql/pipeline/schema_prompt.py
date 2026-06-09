"""VQL JSON schema excerpt for LLM extraction prompts."""

from __future__ import annotations

import json
from typing import Any


VQL_PROGRAM_SCHEMA_EXCERPT: dict[str, Any] = {
    "version": "1.0",
    "render_target": "svg",
    "scene": {
        "width": "float — canvas width in px",
        "height": "float — canvas height in px",
        "background": "#RRGGBB optional",
        "app": "string optional",
        "url": "file:// or vql:// optional",
        "layers": [
            {
                "id": "ui_elements | screen_regions | llm_extracted",
                "objects": [
                    {
                        "id": "unique string",
                        "primitives": [
                            {
                                "shape_type": "rectangle | circle | ellipse | polygon | path",
                                "params": {"width": 0, "height": 0, "radius": 0, "points": []},
                            }
                        ],
                        "style": {
                            "color": "#RRGGBB",
                            "fill": True,
                            "stroke_width": 1.0,
                            "opacity": 1.0,
                        },
                        "center_x": 0,
                        "center_y": 0,
                        "metadata": {
                            "role": "button | panel | window | text | icon | region",
                            "label": "visible text if any",
                            "bbox": ["x0", "y0", "x1", "y1"],
                            "source": "llm_extract",
                        },
                    }
                ],
            }
        ],
        "relations": [],
    },
    "metadata": {
        "source": "pipeline_llm",
        "scene_class": "from img2nl",
        "dominant_colors": ["#RRGGBB"],
        "llm_extract": {"model": "", "confidence": 0.0},
    },
}


def build_vql_schema_prompt(*, scene_width: int, scene_height: int) -> str:
    schema = json.dumps(VQL_PROGRAM_SCHEMA_EXCERPT, ensure_ascii=False, indent=2)
    return (
        "Return ONE JSON object matching this VQLProgram schema (no markdown prose):\n"
        f"{schema}\n\n"
        f"Canvas size MUST be width={scene_width}, height={scene_height}.\n"
        "Use layers[].objects[] with center_x/center_y and rectangle primitives for UI regions.\n"
        "Put readable text in object.metadata.label. Preserve semantic roles in metadata.role.\n"
        "Do not wrap the JSON in code fences."
    )
