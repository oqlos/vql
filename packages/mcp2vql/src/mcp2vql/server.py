"""FastMCP server exposing VQL control tools."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


def _require_fastmcp():
    try:
        from mcp.server.fastmcp import FastMCP
        return FastMCP
    except ImportError as exc:
        raise RuntimeError(
            "MCP support requires optional dependency 'mcp'. Install with: pip install mcp",
        ) from exc


@dataclass
class VqlMCPServer:
    name: str = "vql"

    def __post_init__(self) -> None:
        FastMCP = _require_fastmcp()
        self.app = FastMCP(self.name)
        self._register_tools()

    def _register_tools(self) -> None:
        from dsl2vql import dispatch, execute_dsl, execute_dsl_line
        from dsl2vql.pb_codec import encode_result_protobuf
        from nlp2vql.apply import apply_nl
        from nlp2vql.to_dsl import to_dsl
        from uri2vql.patch import patch_uri
        from uri2vql.query import query_uri

        @self.app.tool()
        def vql_query(uri: str, file: str = "", fmt: str = "json") -> dict[str, Any]:
            result = query_uri(uri, file=file or None, fmt=fmt)
            return result.to_dict()

        @self.app.tool()
        def vql_run_dsl(script: str, default_file: str = "") -> list[dict[str, Any]]:
            results = execute_dsl(script, default_file=default_file or None)
            return [r.to_dict() for r in results]

        @self.app.tool()
        def vql_run_command(command: str, default_file: str = "") -> dict[str, Any]:
            result = execute_dsl_line(command, default_file=default_file or None)
            return result.to_dict()

        @self.app.tool()
        def vql_run_command_pb(envelope_bytes: bytes, default_file: str = "") -> bytes:
            result = dispatch(envelope_bytes, default_file=default_file or None)
            return encode_result_protobuf(result)

        @self.app.tool()
        def vql_to_dsl(prompt: str) -> str:
            return to_dsl(prompt)

        @self.app.tool()
        def vql_apply_nl(prompt: str, default_file: str = "") -> dict[str, Any]:
            return apply_nl(prompt, file=default_file or None).to_dict()

        @self.app.tool()
        def vql_patch(uri: str, with_path: str, file: str = "") -> dict[str, Any]:
            content = open(with_path, encoding="utf-8").read()
            return patch_uri(uri, content=content, file=file or None).to_dict()

        @self.app.tool()
        def vql_detect_ui(image: str, locale: str = "pl") -> dict[str, Any]:
            """Detect windows, panels, buttons on a screenshot (img2vql)."""
            from img2vql.describe_ui import describe_ui_layout
            from img2vql.detect import detect_ui_elements

            payload = detect_ui_elements(image)
            if payload.get("ok"):
                payload["description"] = describe_ui_layout(payload, locale=locale)
            return payload

        @self.app.tool()
        def vql_compare_window(image: str, vql_program: str = "app.vql.json") -> dict[str, Any]:
            """Compare screenshot fingerprint vs stored VQL program baseline."""
            from img2vql.fingerprint import compare_with_program

            payload = compare_with_program(image, vql_program)
            payload["vql_program"] = vql_program
            return payload

        @self.app.tool()
        def vql_diagnose_window(
            image: str,
            vql_program: str = "",
            locale: str = "pl",
            save: bool = False,
            translate_mode: str = "auto",
        ) -> dict[str, Any]:
            """img2nl diagnose for screenshot; optionally persist to VQL program metadata."""
            from img2vql.diagnose import diagnose_for_vql

            return diagnose_for_vql(
                image,
                vql_program=vql_program or None,
                locale=locale,
                translate_mode=translate_mode,
                save_to_program=save,
            )

        @self.app.tool()
        def vql_refresh_window_metadata(
            vql_program: str = "app.vql.json",
            image: str = "",
            locale: str = "pl",
        ) -> dict[str, Any]:
            """Refresh img2nl metadata in VQL program without rebuilding grid."""
            from img2vql.metadata import refresh_program_metadata
            from uri2vql.window import _resolve_window_image

            img = _resolve_window_image(vql_program, image or None)
            if not img:
                return {"ok": False, "error": "image missing; pass image or set metadata.image"}
            payload = refresh_program_metadata(vql_program, img, locale=locale)
            payload["vql_program"] = vql_program
            return payload

    def run(self) -> None:
        self.app.run()


def main() -> None:
    VqlMCPServer().run()


if __name__ == "__main__":
    main()
