#!/usr/bin/env python3
"""Test bidirectional photo/image ↔ VQL conversion and report fidelity.

Creates synthetic samples, runs image→VQL and VQL→PNG/SVG pipelines,
prints a summary table. No live screenshot required.

Usage:
  python examples/photo-roundtrip-test.py
  python examples/photo-roundtrip-test.py --out /tmp/vql-roundtrip
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for sub in ("src", "packages/img2svg/src", "packages/img2vql/src"):
    p = ROOT / sub
    if p.is_dir() and str(p) not in sys.path:
        sys.path.insert(0, str(p))


def _require_pil():
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise SystemExit("Pillow required: pip install pillow") from exc
    return Image, ImageDraw


def sample_flat_shapes(out: Path) -> Path:
    """Flat-color shapes + text — best case for img2svg regions."""
    Image, ImageDraw = _require_pil()
    path = out / "sample_flat_shapes.png"
    im = Image.new("RGB", (400, 300), (240, 235, 220))
    d = ImageDraw.Draw(im)
    d.ellipse([50, 50, 150, 150], fill=(220, 50, 50))
    d.rectangle([200, 80, 350, 200], fill=(50, 100, 200))
    d.polygon([(100, 200), (180, 250), (60, 260)], fill=(50, 180, 80))
    d.text((20, 20), "VQL flat test", fill=(0, 0, 0))
    im.save(path)
    return path


def sample_gradient(out: Path) -> Path:
    """Gradient + noise — worst case for color-grid VQL."""
    Image, ImageDraw = _require_pil()
    path = out / "sample_gradient.png"
    w, h = 320, 240
    im = Image.new("RGB", (w, h))
    px = im.load()
    random.seed(42)
    for y in range(h):
        for x in range(w):
            r = int(128 + 80 * x / w + random.randint(-8, 8))
            g = int(100 + 60 * y / h + random.randint(-8, 8))
            b = int(180 - 40 * x / w + random.randint(-8, 8))
            px[x, y] = (
                max(0, min(255, r)),
                max(0, min(255, g)),
                max(0, min(255, b)),
            )
    ImageDraw.Draw(im).ellipse([80, 60, 200, 180], fill=(255, 200, 50))
    im.save(path)
    return path


def sample_product_photo(out: Path) -> Path:
    """Class B: single object on flat background (e-commerce style)."""
    Image, ImageDraw = _require_pil()
    path = out / "sample_product.png"
    im = Image.new("RGB", (300, 300), (245, 245, 250))
    d = ImageDraw.Draw(im)
    d.ellipse([75, 60, 225, 210], fill=(230, 120, 40), outline=(180, 80, 20))
    d.rectangle([0, 260, 300, 300], fill=(40, 40, 45))
    d.text((12, 268), "Product sample", fill=(220, 220, 220))
    im.save(path)
    return path


def sample_natural_scene(out: Path) -> Path:
    """Class C: sky gradient + ground + soft blob (simulated outdoor photo)."""
    Image, ImageDraw = _require_pil()
    path = out / "sample_natural.png"
    w, h = 400, 300
    im = Image.new("RGB", (w, h))
    px = im.load()
    for y in range(h):
        for x in range(w):
            if y < h * 0.55:
                t = y / (h * 0.55)
                px[x, y] = (int(80 + 100 * t), int(140 + 80 * t), int(200 + 40 * t))
            else:
                t = (y - h * 0.55) / (h * 0.45)
                px[x, y] = (int(40 + 30 * t), int(90 + 40 * t), int(30 + 20 * t))
    d = ImageDraw.Draw(im)
    d.ellipse([140, 120, 260, 220], fill=(180, 160, 140))
    d.ellipse([155, 135, 245, 205], fill=(200, 180, 160))
    im.save(path)
    return path


def sample_nl_drawing(out: Path) -> dict:
    """NL → parametric VQL — near-perfect roundtrip."""
    from vql import nl_to_program, render_to_png, render_to_svg

    program = nl_to_program(
        "narysuj czerwone koło i niebieski prostokąt",
        width=400,
        height=300,
    )
    svg_path = out / "nl_draw.svg"
    png_path = out / "nl_draw.png"
    svg_path.write_text(render_to_svg(program), encoding="utf-8")
    render_to_png(program, str(png_path))
    vql_path = out / "nl_draw.vql.json"
    vql_path.write_text(json.dumps(program.to_dict(), indent=2), encoding="utf-8")
    shapes = [o.primitives[0].shape_type for o in program.scene.iter_objects()]
    return {
        "name": "nl_parametric",
        "direction": "text→VQL→image",
        "objects": program.object_count(),
        "shapes": shapes,
        "vql": str(vql_path),
        "png": str(png_path),
        "fidelity": "excellent (vector primitives)",
    }


def test_img2svg_roundtrip(image: Path, out: Path, *, grid: int = 20) -> dict:
    from img2svg import image_to_svg, image_to_vql
    from img2svg.trace import trace_image_regions
    from vql import VQLProgram, render_to_png, render_to_svg

    stem = image.stem
    vql_path = out / f"{stem}.vql.json"
    result = image_to_vql(image, out_program=vql_path, grid=grid)
    program = VQLProgram.from_dict(json.loads(vql_path.read_text(encoding="utf-8")))

    svg_recon = out / f"{stem}_reconstructed.svg"
    png_recon = out / f"{stem}_reconstructed.png"
    svg_recon.write_text(render_to_svg(program), encoding="utf-8")
    render_to_png(program, str(png_recon))

    image_to_svg(image, out_path=out / f"{stem}_direct.svg", grid=grid)

    trace = trace_image_regions(image, grid=grid)
    orig_colors = {r["color"] for r in trace.get("regions", [])}
    recon_colors = {o.style.color for o in program.scene.iter_objects()}
    color_overlap = len(orig_colors & recon_colors)

    mse = None
    try:
        import numpy as np
        from PIL import Image

        orig = Image.open(image).convert("RGB")
        a = np.array(orig, dtype=float)
        b = np.array(
            Image.open(png_recon).convert("RGB").resize(orig.size),
            dtype=float,
        )
        mse = float(((a - b) ** 2).mean())
    except ImportError:
        pass

    color_ratio = color_overlap / max(1, len(orig_colors))
    if color_ratio >= 0.95:
        fidelity = "good (color palette preserved; edge/grid fragmentation affects MSE)"
    elif mse is not None and mse > 150:
        fidelity = "poor (gradients/textures — use contours or vtracer)"
    else:
        fidelity = "moderate"

    return {
        "name": stem,
        "direction": "image→VQL→image",
        "method": result.get("method", "regions"),
        "objects": result["object_count"],
        "color_overlap": f"{color_overlap}/{len(orig_colors)}",
        "mse": round(mse, 1) if mse is not None else "n/a (pip install numpy)",
        "vql": str(vql_path),
        "png_recon": str(png_recon),
        "fidelity": fidelity,
    }


def test_ui_grid_adopt(out: Path) -> dict:
    from vql.adopt.window import screenshot_to_program
    from vql import render_to_png, render_to_svg

    demo = out / "sample_ui.png"
    if not demo.is_file():
        import subprocess

        subprocess.run(
            [sys.executable, str(ROOT / "examples/generate-demo-screen.py"), "-o", str(demo)],
            check=True,
        )

    program = screenshot_to_program(demo, grid=12)
    vql_path = out / "sample_ui.vql.json"
    vql_path.write_text(json.dumps(program.to_dict(), indent=2), encoding="utf-8")
    svg_path = out / "sample_ui_reconstructed.svg"
    png_path = out / "sample_ui_reconstructed.png"
    svg_path.write_text(render_to_svg(program), encoding="utf-8")
    render_to_png(program, str(png_path))

    return {
        "name": "ui_screenshot",
        "direction": "image→VQL→image",
        "method": "grid_adopt (merge_regions)",
        "objects": program.object_count(),
        "dominant_colors": len(program.metadata.get("dominant_colors", [])),
        "vql": str(vql_path),
        "png_recon": str(png_path),
        "fidelity": "moderate (color mosaic, no OCR labels in render)",
    }


def test_vtracer_roundtrip(image: Path, out: Path) -> dict:
    from img2svg.trace import trace_vtracer
    from img2svg.to_vql import trace_to_vql_program
    from vql import render_to_png, VQLProgram

    trace = trace_vtracer(image)
    if not trace.get("ok"):
        return {
            "name": f"{image.stem}_vtracer",
            "skipped": trace.get("error", "vtracer unavailable"),
        }
    program = trace_to_vql_program(trace, image_path=image)
    vql_path = out / f"{image.stem}_vtracer.vql.json"
    vql_path.write_text(json.dumps(program.to_dict(), indent=2), encoding="utf-8")
    png_path = out / f"{image.stem}_vtracer.png"
    render_to_png(program, str(png_path))

    mse = None
    try:
        import numpy as np
        from PIL import Image

        orig = Image.open(image).convert("RGB")
        a = np.array(orig, dtype=float)
        b = np.array(
            Image.open(png_path).convert("RGB").resize(orig.size),
            dtype=float,
        )
        mse = float(((a - b) ** 2).mean())
    except ImportError:
        pass

    fills = {p.get("fill") for p in trace.get("paths", []) if p.get("fill")}
    fidelity = "good (filled vector paths)"
    if mse is not None and mse < 100:
        fidelity = "excellent (vtracer color vectors)"
    elif mse is not None and mse > 400:
        fidelity = "moderate (vtracer paths; text/edges may differ)"

    return {
        "name": f"{image.stem}_vtracer",
        "direction": "image→VQL→image",
        "method": "vtracer",
        "objects": program.object_count(),
        "paths": trace.get("path_count", 0),
        "fills": len(fills),
        "mse": round(mse, 1) if mse is not None else "n/a",
        "vql": str(vql_path),
        "png_recon": str(png_path),
        "fidelity": fidelity,
    }


def test_opencv_contours(image: Path, out: Path) -> dict:
    from img2svg.trace import trace_contours_opencv
    from img2svg.to_vql import trace_to_vql_program
    from vql import render_to_png, VQLProgram

    trace = trace_contours_opencv(image)
    if not trace.get("ok"):
        return {
            "name": f"{image.stem}_contours",
            "skipped": trace.get("error", "opencv unavailable"),
        }
    program = trace_to_vql_program(trace, image_path=image)
    vql_path = out / f"{image.stem}_contours.vql.json"
    vql_path.write_text(json.dumps(program.to_dict(), indent=2), encoding="utf-8")
    png_path = out / f"{image.stem}_contours.png"
    render_to_png(program, str(png_path))
    return {
        "name": f"{image.stem}_contours",
        "direction": "image→VQL→image",
        "method": "opencv_contour",
        "objects": program.object_count(),
        "paths": trace.get("path_count", 0),
        "vql": str(vql_path),
        "png_recon": str(png_path),
        "fidelity": "moderate (edge paths, no fill colors)",
    }


def test_metadata_only_reconstruction(out: Path) -> dict:
    """Metadata without scene objects — cannot visually reconstruct a photo."""
    from vql import VQLProgram, render_to_png
    from vql.schema.program import Layer, Scene

    program = VQLProgram(
        scene=Scene(width=400, height=300, background="#E8E8E8", layers=[Layer(id="empty")]),
        metadata={
            "source": "exif_only",
            "exif": {"Make": "Demo", "Model": "VirtualCam", "ISO": 400, "FNumber": 2.8},
            "semantic_description": "outdoor scene at dusk (text only, no geometry)",
        },
    )
    vql_path = out / "metadata_only.vql.json"
    png_path = out / "metadata_only.png"
    vql_path.write_text(json.dumps(program.to_dict(), indent=2), encoding="utf-8")
    render_to_png(program, str(png_path))
    return {
        "name": "metadata_only",
        "direction": "metadata→image",
        "objects": program.object_count(),
        "vql": str(vql_path),
        "png_recon": str(png_path),
        "fidelity": "not reconstructible (empty scene; metadata is context only)",
    }


def test_img2vql_detect(out: Path) -> dict:
    demo = out / "sample_ui.png"
    if not demo.is_file():
        return {"name": "img2vql_detect", "skipped": "no sample_ui.png"}
    try:
        from img2vql.detect import detect_ui_elements
    except ImportError:
        return {"name": "img2vql_detect", "skipped": "img2vql not installed"}

    try:
        det = detect_ui_elements(demo)
    except ImportError as exc:
        return {"name": "img2vql_detect", "skipped": f"img2nl required: {exc}"}
    roles = sorted({e["role"] for e in det.get("elements", [])})
    return {
        "name": "img2vql_detect",
        "direction": "image→VQL metadata",
        "elements": det.get("element_count", 0),
        "roles": roles,
        "fidelity": "good for UI bbox; labels need imgl/OCR",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("/tmp/vql-roundtrip"))
    args = parser.parse_args()
    out: Path = args.out.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)

    print(f"Output: {out}\n")

    flat = sample_flat_shapes(out)
    grad = sample_gradient(out)
    product = sample_product_photo(out)
    natural = sample_natural_scene(out)

    rows: list[dict] = []
    rows.append(sample_nl_drawing(out))
    rows.append(test_img2svg_roundtrip(flat, out))
    rows.append(test_img2svg_roundtrip(grad, out, grid=16))
    rows.append(test_vtracer_roundtrip(flat, out))
    rows.append(test_vtracer_roundtrip(product, out))
    rows.append(test_img2svg_roundtrip(product, out, grid=20))
    rows.append(test_img2svg_roundtrip(natural, out, grid=16))
    rows.append(test_opencv_contours(flat, out))
    rows.append(test_ui_grid_adopt(out))
    rows.append(test_metadata_only_reconstruction(out))
    rows.append(test_img2vql_detect(out))

    report_path = out / "roundtrip_report.json"
    report_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    print("=" * 72)
    print(f"{'sample':<20} {'direction':<22} {'objects':<8} fidelity")
    print("-" * 72)
    for r in rows:
        if r.get("skipped"):
            print(f"{r['name']:<20} SKIPPED: {r['skipped']}")
            continue
        objs = r.get("objects", r.get("elements", "-"))
        print(f"{r['name']:<20} {r.get('direction','?'):<22} {str(objs):<8} {r.get('fidelity','')}")
        if r.get("mse"):
            print(f"  MSE={r['mse']}  colors={r.get('color_overlap','')}")
        if r.get("roles"):
            print(f"  roles={r['roles']}")
    print("-" * 72)
    print(f"Report: {report_path}")
    print("\nSee docs/photo-roundtrip.md for interpretation and library recommendations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
