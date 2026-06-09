"""CLI for uri2vql."""

from __future__ import annotations

import argparse

from uri2vql.cli_commands import COMMAND_RUNNERS


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="uri2vql", description="vql:// URI query and patch")
    sub = parser.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("query", help="Query a vql:// URI")
    q.add_argument("uri")
    q.add_argument("--file", default="")
    q.add_argument("--format", default="json")

    p = sub.add_parser("patch", help="Patch via vql:// URI")
    p.add_argument("uri")
    p.add_argument("--with", dest="with_path", required=True)
    p.add_argument("--file", default="")

    r = sub.add_parser("run", help="Decode URI and dispatch via dsl2vql")
    r.add_argument("--uri", required=True)
    r.add_argument("--file", default="")

    s = sub.add_parser("resolve", help="Resolve NL prompt to vql:// URIs")
    s.add_argument("prompt")
    s.add_argument("--file", default="")
    s.add_argument("--monitor", type=int, default=1)
    s.add_argument("--grid", type=int, default=12)
    s.add_argument("--image", default="")

    c = sub.add_parser("capture-screen", help="Try desktop capture backends (debug)")
    c.add_argument("--out", default="/tmp/vql-screen.png")
    c.add_argument("--monitor", type=int, default=1)
    c.add_argument(
        "--interactive",
        action="store_true",
        help="Use xdg-desktop-portal interactive screenshot (GNOME/Wayland permission prompt)",
    )
    c.add_argument(
        "--diagnose",
        action="store_true",
        help="Show per-backend capture attempts (blank/denied/missing)",
    )

    w = sub.add_parser("analyze-window", help="Capture screen and adopt to VQL program")
    w.add_argument("--out", default="app.vql.json")
    w.add_argument("--monitor", type=int, default=1)
    w.add_argument("--grid", type=int, default=12)
    w.add_argument("--image", default="", help="Existing PNG instead of live capture")
    w.add_argument(
        "--interactive",
        action="store_true",
        help="GNOME/Wayland: xdg-portal screenshot with permission prompt (use when live capture is black)",
    )

    det = sub.add_parser("detect-window", help="Detect UI elements (windows, buttons) on screenshot")
    det.add_argument("--image", required=True)
    det.add_argument("--locale", default="pl")
    det.add_argument("--describe", action="store_true", default=True)

    ua = sub.add_parser("adopt-ui", help="Detect UI + write VQL program with ui_elements layer")
    ua.add_argument("--image", required=True)
    ua.add_argument("--out", default="ui.vql.json")
    ua.add_argument("--locale", default="pl")
    ua.add_argument("--with-grid", action="store_true")
    ua.add_argument("--grid", type=int, default=12)

    imgl_cmd = sub.add_parser("adopt-imgl", help="OCR + semantic UI layout via imgl → VQL program")
    imgl_cmd.add_argument("--image", required=True)
    imgl_cmd.add_argument("--out", default="layout.vql.json")
    imgl_cmd.add_argument("--lang", default="eng+pol")
    imgl_cmd.add_argument("--with-grid", action="store_true")
    imgl_cmd.add_argument("--grid", type=int, default=12)

    d = sub.add_parser("diagnose-window", help="img2nl-style diagnose: send capture to LLM?")
    d.add_argument("--image", required=True)
    d.add_argument("--vql-program", default="", help="Optional adopted VQL JSON for context")
    d.add_argument(
        "--locale",
        default="pl",
        help="Message language (European ISO 639-1: pl, en, de, fr, es, it, cs, uk, ...)",
    )
    d.add_argument(
        "--translate-mode",
        default="auto",
        choices=["auto", "catalog", "offline"],
        help="img2nl: auto=catalog+argostranslate; offline=require argos; catalog=JSON only",
    )
    d.add_argument(
        "--save",
        action="store_true",
        help="Persist diagnose metadata into --vql-program",
    )

    cmp = sub.add_parser("compare-window", help="Compare capture fingerprint vs VQL program baseline")
    cmp.add_argument("--image", required=True)
    cmp.add_argument("--vql-program", default="app.vql.json")

    ref = sub.add_parser("refresh-window", help="Refresh img2nl metadata in VQL program (no grid rebuild)")
    ref.add_argument("--image", default="", help="PNG path; default: metadata.image from program")
    ref.add_argument("--vql-program", default="app.vql.json")
    ref.add_argument("--locale", default="pl")

    ca = sub.add_parser(
        "capture-and-analyze",
        help="Interactive capture + analyze-window + optional diagnose",
    )
    ca.add_argument("--out", default="app.vql.json")
    ca.add_argument("--capture-out", default="", help="PNG path (default: /tmp/vql-capture.png)")
    ca.add_argument("--grid", type=int, default=12)
    ca.add_argument("--locale", default="pl")
    ca.add_argument("--diagnose", action="store_true", help="Run diagnose-window --save after analyze")
    ca.add_argument("--no-interactive", action="store_true", help="Disable xdg-portal interactive capture")

    pa = sub.add_parser(
        "pipeline-analyze",
        help="Multi-level img2nl → adopt → optional LLM → VQL program (+ render PNG)",
    )
    pa.add_argument("--image", required=True)
    pa.add_argument("--out", default="app.vql.json")
    pa.add_argument("--render", default="", help="PNG render path (default: <out>.render.png)")
    pa.add_argument("--locale", default="pl")
    pa.add_argument("--grid", type=int, default=12)
    pa.add_argument("--method", default="auto", choices=["auto", "grid", "detect", "imgl"])
    pa.add_argument("--llm", action="store_true", help="Force LLM extraction (requires .env keys)")
    pa.add_argument("--no-llm", action="store_true", help="Skip LLM even when VQL_LLM_ENABLED=1")

    vi = sub.add_parser("vql-to-image", help="Render VQL program JSON to PNG")
    vi.add_argument("--program", required=True)
    vi.add_argument("--out", default="render.png")
    vi.add_argument("--scale", type=float, default=1.0)

    rt = sub.add_parser("roundtrip", help="image → VQL → PNG roundtrip with stats")
    rt.add_argument("--image", required=True)
    rt.add_argument("--out", default="roundtrip.vql.json")
    rt.add_argument("--render", default="roundtrip.render.png")
    rt.add_argument("--locale", default="pl")
    rt.add_argument("--llm", action="store_true", help="Include LLM extraction step")

    return parser


def main(argv: list[str] | None = None) -> int:
    from uri2vql._bootstrap import ensure_img2vql

    ensure_img2vql()
    args = build_parser().parse_args(argv)
    runner = COMMAND_RUNNERS.get(args.cmd)
    if runner is None:
        return 1
    return runner(args)


if __name__ == "__main__":
    raise SystemExit(main())
