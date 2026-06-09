# vql

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Workflows](#workflows)
- [Dependencies](#dependencies)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `vql`
- **version**: `0.1.3`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(2), app.doql.less, goal.yaml, .env.example, project/(5 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: vql;
  version: 0.1.3;
}

dependencies {
  png: "cairosvg>=2.7, pillow>=10.0";
  desktop: "pillow>=10.0, mss>=9.0";
  playwright: playwright>=1.40.0;
  dev: "pytest>=8.0, cairosvg>=2.7, pillow>=10.0, protobuf>=5.0, jsonschema>=4.0, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
}

interface[type="api"] {
  type: rest;
  framework: fastapi;
}

workflow[name="venv"] {
  trigger: manual;
  step-1: run cmd=test -d .venv || python3 -m venv .venv;
  step-2: run cmd=echo "venv ready: .venv/";
}

workflow[name="install"] {
  trigger: manual;
  step-1: run cmd=$(PIP) install -e .;
}

workflow[name="install-dev"] {
  trigger: manual;
  step-1: run cmd=$(PIP) install -e .;
  step-2: run cmd=$(PIP) install -e packages/uri2vql;
  step-3: run cmd=$(PIP) install -e packages/nlp2vql;
  step-4: run cmd=$(PIP) install -e packages/dsl2vql;
  step-5: run cmd=$(PIP) install -e packages/cli2vql;
  step-6: run cmd=$(PIP) install -e packages/rest2vql;
  step-7: run cmd=-$(PIP) install -e packages/mcp2vql;
  step-8: run cmd=$(PIP) install -e ".[dev,png]" jsonschema protobuf fastapi uvicorn httpx;
  step-9: run cmd=echo "dev stack installed";
}

workflow[name="proto"] {
  trigger: manual;
  step-1: run cmd=$(PIP) install -q grpcio-tools;
  step-2: run cmd=bash packages/dsl2vql/scripts/generate-proto.sh;
}

workflow[name="test"] {
  trigger: manual;
  step-1: run cmd=echo "Running tests...";
  step-2: run cmd=$(PYTEST);
}

workflow[name="test-cov"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/ packages/dsl2vql/tests -v \;
  step-2: run cmd=--cov=vql --cov=dsl2vql --cov-report=term-missing;
}

workflow[name="test-all"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/ packages/ -q --tb=short;
}

workflow[name="test-roundtrip"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m pytest tests/test_photo_roundtrip.py -q --tb=short;
  step-2: run cmd=$(PYTHON) examples/photo-roundtrip-test.py --out /tmp/vql-roundtrip;
}

workflow[name="validate-schema"] {
  trigger: manual;
  step-1: run cmd=dsl2vql validate-schema;
}

workflow[name="compile"] {
  trigger: manual;
  step-1: run cmd=dsl2vql -c 'COMPILE "narysuj czerwone koło"' --json;
}

workflow[name="serve"] {
  trigger: manual;
  step-1: run cmd=rest2vql serve --port $(PORT) --host 127.0.0.1;
}

workflow[name="clean"] {
  trigger: manual;
  step-1: run cmd=find . -type f -name '*.pyc' -delete;
  step-2: run cmd=find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true;
  step-3: run cmd=find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true;
  step-4: run cmd=rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache .goal_test_report.xml;
  step-5: run cmd=echo "clean done";
}

workflow[name="build"] {
  trigger: manual;
  step-1: run cmd=$(PIP) install -q build;
  step-2: run cmd=rm -rf dist/ build/;
  step-3: run cmd=$(PYTHON) -m build;
}

workflow[name="publish"] {
  trigger: manual;
  step-1: run cmd=$(PIP) install -q twine;
  step-2: run cmd=$(PYTHON) -m twine check dist/*;
}

workflow[name="publish-confirm"] {
  trigger: manual;
  step-1: run cmd=$(PYTHON) -m twine upload dist/*;
}

workflow[name="version"] {
  trigger: manual;
  step-1: run cmd=echo -n "VERSION file: ";
  step-2: run cmd=cat VERSION;
  step-3: run cmd=$(PYTHON) -c "from importlib.metadata import version; print('installed:', version('vql'))" 2>/dev/null || echo "installed: (not installed)";
}

workflow[name="goal"] {
  trigger: manual;
  step-1: run cmd=goal -a;
}

tests {
  import: testql-scenarios/**/*.testql.toon.yaml;
}

env_vars {
  keys: OPENROUTER_API_KEY, LLM_MODEL, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_MAX_RETRIES, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_CREATE_BACKUPS, XDG_SESSION_TYPE, WAYLAND_DISPLAY, VQL_CAPTURE_INTERACTIVE, VQL_PORTAL_PYTHON, VQL_CAPTURE_BACKEND;
}

deploy {
  target: makefile;
}

environment[name="local"] {
  runtime: python;
  env_file: .env;
  template_file: .env.example;
  python_version: >=3.10;
  vars: LLM_MODEL, OPENROUTER_API_KEY, PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_CREATE_BACKUPS, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_MAX_RETRIES;
  runtime_llm: OPENROUTER_API_KEY;
  runtime_pfix: PFIX_AUTO_APPLY, PFIX_AUTO_INSTALL_DEPS, PFIX_AUTO_RESTART, PFIX_CREATE_BACKUPS, PFIX_DRY_RUN, PFIX_ENABLED, PFIX_GIT_COMMIT, PFIX_GIT_PREFIX, PFIX_MAX_RETRIES;
}
```

## Workflows

## Dependencies

### Runtime

*(see pyproject.toml)*

### Development

```text markpact:deps python scope=dev
pytest>=8.0
cairosvg>=2.7
pillow>=10.0
protobuf>=5.0
jsonschema>=4.0
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Call Graph

*213 nodes · 252 edges · 52 modules · CC̄=4.1*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `query_window` *(in packages.uri2vql.src.uri2vql.window)* | 69 ⚠ | 2 | 147 | **149** |
| `resolve_prompt_to_vql_uri` *(in packages.uri2vql.src.uri2vql.nlp2uri)* | 54 ⚠ | 2 | 68 | **70** |
| `parse_svg_path` *(in src.vql.drawing.svg_path_parser)* | 43 ⚠ | 1 | 64 | **65** |
| `trace_to_vql_program` *(in packages.img2svg.src.img2svg.to_vql)* | 15 ⚠ | 3 | 46 | **49** |
| `analyze_screenshot` *(in src.vql.adopt.window)* | 13 ⚠ | 2 | 45 | **47** |
| `screenshot_to_program` *(in src.vql.adopt.window)* | 12 ⚠ | 3 | 44 | **47** |
| `_set_body` *(in packages.dsl2vql.src.dsl2vql.pb_codec)* | 12 ⚠ | 1 | 45 | **46** |
| `_detect_buttons` *(in packages.img2vql.src.img2vql.detect)* | 25 ⚠ | 1 | 45 | **46** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/oqlos/vql
# generated in 0.14s
# nodes: 213 | edges: 252 | modules: 52
# CC̄=4.1

HUBS[20]:
  packages.uri2vql.src.uri2vql.window.query_window
    CC=69  in:2  out:147  total:149
  packages.uri2vql.src.uri2vql.nlp2uri.resolve_prompt_to_vql_uri
    CC=54  in:2  out:68  total:70
  src.vql.drawing.svg_path_parser.parse_svg_path
    CC=43  in:1  out:64  total:65
  packages.img2svg.src.img2svg.to_vql.trace_to_vql_program
    CC=15  in:3  out:46  total:49
  src.vql.adopt.window.analyze_screenshot
    CC=13  in:2  out:45  total:47
  src.vql.adopt.window.screenshot_to_program
    CC=12  in:3  out:44  total:47
  packages.dsl2vql.src.dsl2vql.pb_codec._set_body
    CC=12  in:1  out:45  total:46
  packages.img2vql.src.img2vql.detect._detect_buttons
    CC=25  in:1  out:45  total:46
  packages.uri2vql.src.uri2vql.window._query_window_imgl
    CC=17  in:1  out:45  total:46
  packages.img2vql.src.img2vql.describe_ui.describe_ui_layout
    CC=14  in:6  out:39  total:45
  src.vql.adopt.window.capture_diagnose
    CC=33  in:1  out:44  total:45
  examples.photo-roundtrip-test.main
    CC=5  in:0  out:45  total:45
  packages.rest2vql.src.rest2vql.app.create_app
    CC=1  in:1  out:43  total:44
  packages.img2vql.src.img2vql.program.elements_to_vql_program
    CC=11  in:1  out:40  total:41
  packages.dsl2img2svg.src.dsl2img2svg.dispatch.dispatch
    CC=14  in:0  out:41  total:41
  packages.uri2img2svg.src.uri2img2svg.query.query_uri
    CC=13  in:6  out:28  total:34
  packages.dsl2vql.src.dsl2vql.events.EventStore.append
    CC=3  in:0  out:33  total:33
  packages.dsl2vql.src.dsl2vql.grammar.parse_line
    CC=28  in:6  out:27  total:33
  src.vql.adopt.portal_capture.capture_via_portal
    CC=4  in:1  out:30  total:31
  examples.photo-roundtrip-test.test_img2svg_roundtrip
    CC=8  in:2  out:29  total:31

MODULES:
  examples.generate-demo-screen  [3 funcs]
    _load_font  CC=3  out:2
    main  CC=1  out:6
    write_demo_screen  CC=1  out:18
  examples.photo-roundtrip-test  [10 funcs]
    _require_pil  CC=2  out:1
    main  CC=5  out:45
    sample_flat_shapes  CC=1  out:8
    sample_gradient  CC=3  out:21
    sample_nl_drawing  CC=2  out:12
    test_img2svg_roundtrip  CC=8  out:29
    test_img2vql_detect  CC=5  out:5
    test_opencv_contours  CC=2  out:13
    test_ui_grid_adopt  CC=2  out:17
    test_vtracer_roundtrip  CC=10  out:27
  packages.cli2vql.src.cli2vql.cli  [1 funcs]
    _repl  CC=6  out:8
  packages.dsl2img2svg.src.dsl2img2svg.cli  [1 funcs]
    main  CC=4  out:5
  packages.dsl2img2svg.src.dsl2img2svg.dispatch  [2 funcs]
    _parse_kv_args  CC=4  out:4
    dispatch  CC=14  out:41
  packages.dsl2vql.src.dsl2vql.bus  [5 funcs]
    _bytes_to_cmd  CC=3  out:5
    _dispatch_cmd  CC=5  out:12
    dispatch  CC=6  out:15
    execute_dsl  CC=4  out:6
    execute_dsl_line  CC=1  out:1
  packages.dsl2vql.src.dsl2vql.cli  [3 funcs]
    _main_legacy  CC=9  out:20
    _main_subcommand  CC=9  out:21
    main  CC=4  out:2
  packages.dsl2vql.src.dsl2vql.codec  [4 funcs]
    decode_protobuf  CC=1  out:1
    encode_protobuf  CC=1  out:1
    encode_text  CC=2  out:2
    roundtrip_text  CC=3  out:6
  packages.dsl2vql.src.dsl2vql.events  [2 funcs]
    append  CC=3  out:33
    default_event_store  CC=1  out:4
  packages.dsl2vql.src.dsl2vql.grammar  [4 funcs]
    parse_line  CC=28  out:27
    pick_flag  CC=3  out:2
    split_command  CC=4  out:4
    to_text  CC=6  out:11
  packages.dsl2vql.src.dsl2vql.handlers.command  [6 funcs]
    _read_json  CC=1  out:4
    handle_compile  CC=4  out:11
    handle_export  CC=7  out:15
    handle_from_tokens  CC=11  out:15
    handle_generate  CC=4  out:12
    handle_patch  CC=3  out:12
  packages.dsl2vql.src.dsl2vql.handlers.query  [5 funcs]
    _load_program  CC=1  out:5
    handle_query  CC=4  out:8
    handle_render  CC=9  out:16
    handle_resolve  CC=3  out:5
    handle_validate  CC=6  out:11
  packages.dsl2vql.src.dsl2vql.pb_codec  [8 funcs]
    _set_body  CC=12  out:45
    decode_protobuf  CC=1  out:3
    decode_protobuf_to_text  CC=1  out:2
    encode_protobuf  CC=1  out:6
    encode_result_protobuf  CC=1  out:2
    encode_text_to_protobuf  CC=2  out:3
    envelope_to_dict  CC=31  out:4
    result_to_pb  CC=4  out:4
  packages.dsl2vql.src.dsl2vql.schema_registry  [5 funcs]
    _load_schemas  CC=3  out:9
    all_schemas  CC=1  out:2
    schema_for_verb  CC=1  out:3
    validate_command_dict  CC=3  out:7
    validate_schema_registry  CC=3  out:6
  packages.img2svg.src.img2svg.svg_emit  [2 funcs]
    image_to_svg  CC=7  out:24
    paths_to_svg  CC=3  out:9
  packages.img2svg.src.img2svg.to_vql  [2 funcs]
    image_to_vql  CC=5  out:17
    trace_to_vql_program  CC=15  out:46
  packages.img2svg.src.img2svg.trace  [7 funcs]
    _hex_color  CC=1  out:0
    _merge_grid_cells  CC=15  out:9
    _parse_translate  CC=3  out:5
    _parse_vtracer_svg  CC=5  out:16
    trace_contours_opencv  CC=8  out:23
    trace_image_regions  CC=6  out:17
    trace_vtracer  CC=6  out:17
  packages.img2vql.src.img2vql.adopt  [1 funcs]
    adopt_screenshot  CC=2  out:20
  packages.img2vql.src.img2vql.describe_ui  [1 funcs]
    describe_ui_layout  CC=14  out:39
  packages.img2vql.src.img2vql.detect  [10 funcs]
    _avg_color  CC=5  out:8
    _dedupe  CC=8  out:6
    _detect_buttons  CC=25  out:45
    _detect_panels  CC=5  out:14
    _detect_titlebar  CC=5  out:11
    _detect_toolbar  CC=10  out:21
    _flood_rects  CC=14  out:13
    _hex_color  CC=1  out:0
    _iou  CC=3  out:5
    detect_ui_elements  CC=8  out:19
  packages.img2vql.src.img2vql.diagnose  [4 funcs]
    _normalize_locale  CC=4  out:4
    _recommendation  CC=6  out:10
    diagnose_for_vql  CC=10  out:21
    diagnose_image  CC=2  out:3
  packages.img2vql.src.img2vql.fingerprint  [3 funcs]
    _json_safe  CC=7  out:8
    compare_with_program  CC=5  out:19
    load_program_fingerprint  CC=6  out:9
  packages.img2vql.src.img2vql.metadata  [12 funcs]
    _compact_special_hits  CC=1  out:10
    _json_safe  CC=7  out:8
    _merge_special_hits  CC=2  out:8
    _text_likely  CC=4  out:7
    auto_ocr_special_hits  CC=3  out:7
    img2nl_metadata_slice  CC=9  out:17
    imgl_ocr_special_hits  CC=8  out:12
    merge_program_metadata  CC=1  out:8
    metadata_from_diagnose  CC=6  out:21
    rapidocr_special_hits  CC=10  out:16
  packages.img2vql.src.img2vql.program  [3 funcs]
    _bbox_contains  CC=4  out:0
    _build_contains_relations  CC=8  out:9
    elements_to_vql_program  CC=11  out:40
  packages.mcp2vql.src.mcp2vql.server  [2 funcs]
    __post_init__  CC=1  out:3
    _require_fastmcp  CC=2  out:1
  packages.nlp2vql.src.nlp2vql.apply  [1 funcs]
    apply_nl  CC=2  out:4
  packages.nlp2vql.src.nlp2vql.to_dsl  [3 funcs]
    _intent  CC=11  out:6
    nl_to_dsl_line  CC=8  out:1
    to_dsl  CC=1  out:1
  packages.rest2vql.src.rest2vql.app  [1 funcs]
    create_app  CC=1  out:43
  packages.rest2vql.src.rest2vql.cli  [1 funcs]
    main  CC=1  out:7
  packages.rest2vql.src.rest2vql.window  [7 funcs]
    window_adopt  CC=1  out:1
    window_analyze  CC=1  out:1
    window_compare  CC=1  out:1
    window_detect  CC=2  out:3
    window_diagnose  CC=2  out:1
    window_refresh  CC=1  out:1
    window_summary  CC=7  out:1
  packages.rest2vql.src.rest2vql.window_routes  [8 funcs]
    _window_response  CC=2  out:2
    post_window_adopt  CC=2  out:5
    post_window_analyze  CC=2  out:5
    post_window_compare  CC=2  out:5
    post_window_detect  CC=2  out:5
    post_window_diagnose  CC=2  out:5
    post_window_refresh  CC=2  out:5
    post_window_summary  CC=2  out:5
  packages.uri2img2svg.src.uri2img2svg.cli  [1 funcs]
    main  CC=4  out:9
  packages.uri2img2svg.src.uri2img2svg.query  [1 funcs]
    query_uri  CC=13  out:28
  packages.uri2img2svg.src.uri2img2svg.uri  [1 funcs]
    parse_img2svg_uri  CC=9  out:11
  packages.uri2vql.src.uri2vql.compile  [2 funcs]
    _dsl_from_uri  CC=4  out:5
    compile_vql_uri  CC=7  out:8
  packages.uri2vql.src.uri2vql.nlp2uri  [3 funcs]
    best_uri  CC=2  out:1
    nlp2uri  CC=1  out:1
    resolve_prompt_to_vql_uri  CC=54  out:68
  packages.uri2vql.src.uri2vql.patch  [1 funcs]
    patch_uri  CC=7  out:15
  packages.uri2vql.src.uri2vql.query  [2 funcs]
    _load_program  CC=1  out:5
    query_uri  CC=15  out:20
  packages.uri2vql.src.uri2vql.run  [2 funcs]
    run_uri  CC=7  out:8
    run_uri_json  CC=1  out:3
  packages.uri2vql.src.uri2vql.uri  [16 funcs]
    _with_file  CC=4  out:4
    is_vql_uri  CC=1  out:2
    parse_vql_uri  CC=5  out:6
    uri_for_imgl_click  CC=6  out:1
    uri_for_imgl_list  CC=1  out:1
    uri_for_imgl_type  CC=6  out:1
    uri_for_object  CC=1  out:1
    uri_for_objects  CC=1  out:1
    uri_for_program  CC=1  out:1
    uri_for_scene  CC=1  out:1
  packages.uri2vql.src.uri2vql.window  [9 funcs]
    _diagnose_fallback  CC=15  out:29
    _normalize_locale  CC=4  out:4
    _query_window_imgl  CC=17  out:45
    _resolve_image_param  CC=6  out:12
    analyze_window_uri  CC=4  out:9
    compare_window_image  CC=2  out:3
    diagnose_window_image  CC=2  out:3
    query_window  CC=69  out:147
    refresh_window_metadata  CC=2  out:2
  src.vql.adopt.portal_capture  [2 funcs]
    capture_via_portal  CC=4  out:30
    main  CC=2  out:9
  src.vql.adopt.window  [25 funcs]
    _active_window_title  CC=4  out:3
    _capture_backends  CC=7  out:7
    _capture_interactive_mode  CC=2  out:3
    _capture_permission_hint  CC=2  out:1
    _capture_with_gnome_screenshot  CC=2  out:4
    _capture_with_gnome_shell  CC=2  out:4
    _capture_with_grim  CC=2  out:4
    _capture_with_mss  CC=4  out:8
    _capture_with_portal  CC=15  out:21
    _capture_with_scrot  CC=2  out:4
  src.vql.compiler.legacy_drawcommand  [3 funcs]
    commands_to_program  CC=9  out:15
    compile_to_events  CC=3  out:6
    program_to_commands  CC=4  out:7
  src.vql.compiler.nl_to_vql  [1 funcs]
    nl_to_program  CC=6  out:9
  src.vql.drawing.nl_parser  [1 funcs]
    to_vql  CC=1  out:1
  src.vql.drawing.path_generator  [1 funcs]
    generate  CC=5  out:7
  src.vql.drawing.svg_path_parser  [1 funcs]
    parse_svg_path  CC=43  out:64
  src.vql.facade  [6 funcs]
    compile  CC=1  out:1
    render_png  CC=1  out:1
    render_svg  CC=1  out:1
    to_commands  CC=1  out:1
    to_events  CC=1  out:1
    validate  CC=1  out:1
  src.vql.renderers.base  [2 funcs]
    render  CC=1  out:1
    render_program  CC=1  out:3
  src.vql.renderers.svg  [2 funcs]
    render_to_png  CC=2  out:8
    render_to_svg  CC=1  out:4
  src.vql.validation.spec  [4 funcs]
    _match_items  CC=4  out:3
    _program_colors  CC=2  out:2
    _program_shapes  CC=3  out:1
    validate_program  CC=4  out:12

EDGES:
  packages.uri2img2svg.src.uri2img2svg.cli.main → packages.uri2img2svg.src.uri2img2svg.query.query_uri
  packages.uri2img2svg.src.uri2img2svg.query.query_uri → packages.uri2img2svg.src.uri2img2svg.uri.parse_img2svg_uri
  packages.uri2img2svg.src.uri2img2svg.query.query_uri → packages.img2svg.src.img2svg.svg_emit.image_to_svg
  packages.uri2img2svg.src.uri2img2svg.query.query_uri → packages.img2svg.src.img2svg.to_vql.image_to_vql
  packages.dsl2vql.src.dsl2vql.bus._dispatch_cmd → packages.dsl2vql.src.dsl2vql.schema_registry.validate_command_dict
  packages.dsl2vql.src.dsl2vql.bus._dispatch_cmd → packages.dsl2vql.src.dsl2vql.grammar.split_command
  packages.dsl2vql.src.dsl2vql.bus._dispatch_cmd → packages.dsl2vql.src.dsl2vql.handlers.command.handle_from_tokens
  packages.dsl2vql.src.dsl2vql.bus._dispatch_cmd → packages.dsl2vql.src.dsl2vql.events.default_event_store
  packages.dsl2vql.src.dsl2vql.bus._bytes_to_cmd → packages.dsl2vql.src.dsl2vql.pb_codec.decode_protobuf
  packages.dsl2vql.src.dsl2vql.bus._bytes_to_cmd → packages.dsl2vql.src.dsl2vql.grammar.to_text
  packages.dsl2vql.src.dsl2vql.bus._bytes_to_cmd → packages.dsl2vql.src.dsl2vql.grammar.parse_line
  packages.dsl2vql.src.dsl2vql.bus.dispatch → packages.dsl2vql.src.dsl2vql.grammar.split_command
  packages.dsl2vql.src.dsl2vql.bus.dispatch → packages.dsl2vql.src.dsl2vql.bus._dispatch_cmd
  packages.dsl2vql.src.dsl2vql.bus.dispatch → packages.dsl2vql.src.dsl2vql.bus._bytes_to_cmd
  packages.dsl2vql.src.dsl2vql.bus.dispatch → packages.dsl2vql.src.dsl2vql.grammar.to_text
  packages.dsl2vql.src.dsl2vql.bus.execute_dsl_line → packages.dsl2vql.src.dsl2vql.bus.dispatch
  packages.dsl2vql.src.dsl2vql.bus.execute_dsl → packages.dsl2vql.src.dsl2vql.bus.execute_dsl_line
  packages.dsl2vql.src.dsl2vql.cli._main_legacy → packages.dsl2vql.src.dsl2vql.bus.execute_dsl_line
  packages.dsl2vql.src.dsl2vql.cli._main_legacy → packages.dsl2vql.src.dsl2vql.bus.execute_dsl
  packages.dsl2vql.src.dsl2vql.cli._main_subcommand → packages.dsl2vql.src.dsl2vql.schema_registry.validate_schema_registry
  packages.dsl2vql.src.dsl2vql.cli.main → packages.dsl2vql.src.dsl2vql.cli._main_legacy
  packages.dsl2vql.src.dsl2vql.cli.main → packages.dsl2vql.src.dsl2vql.cli._main_subcommand
  packages.dsl2vql.src.dsl2vql.events.EventStore.append → packages.dsl2vql.src.dsl2vql.pb_codec.encode_protobuf
  packages.dsl2vql.src.dsl2vql.pb_codec.encode_protobuf → packages.dsl2vql.src.dsl2vql.pb_codec._set_body
  packages.dsl2vql.src.dsl2vql.pb_codec.decode_protobuf → packages.dsl2vql.src.dsl2vql.pb_codec.envelope_to_dict
  packages.dsl2vql.src.dsl2vql.pb_codec.encode_text_to_protobuf → packages.dsl2vql.src.dsl2vql.grammar.parse_line
  packages.dsl2vql.src.dsl2vql.pb_codec.encode_text_to_protobuf → packages.dsl2vql.src.dsl2vql.pb_codec.encode_protobuf
  packages.dsl2vql.src.dsl2vql.pb_codec.decode_protobuf_to_text → packages.dsl2vql.src.dsl2vql.grammar.to_text
  packages.dsl2vql.src.dsl2vql.pb_codec.decode_protobuf_to_text → packages.dsl2vql.src.dsl2vql.pb_codec.decode_protobuf
  packages.dsl2vql.src.dsl2vql.pb_codec.encode_result_protobuf → packages.dsl2vql.src.dsl2vql.pb_codec.result_to_pb
  packages.dsl2vql.src.dsl2vql.schema_registry.schema_for_verb → packages.dsl2vql.src.dsl2vql.schema_registry._load_schemas
  packages.dsl2vql.src.dsl2vql.schema_registry.all_schemas → packages.dsl2vql.src.dsl2vql.schema_registry._load_schemas
  packages.dsl2vql.src.dsl2vql.schema_registry.validate_command_dict → packages.dsl2vql.src.dsl2vql.schema_registry.schema_for_verb
  packages.dsl2vql.src.dsl2vql.schema_registry.validate_schema_registry → packages.dsl2vql.src.dsl2vql.schema_registry._load_schemas
  packages.dsl2vql.src.dsl2vql.grammar.parse_line → packages.dsl2vql.src.dsl2vql.grammar.split_command
  packages.dsl2vql.src.dsl2vql.grammar.parse_line → packages.dsl2vql.src.dsl2vql.grammar.pick_flag
  packages.dsl2vql.src.dsl2vql.codec.encode_text → packages.dsl2vql.src.dsl2vql.grammar.parse_line
  packages.dsl2vql.src.dsl2vql.codec.encode_text → packages.dsl2vql.src.dsl2vql.schema_registry.validate_command_dict
  packages.dsl2vql.src.dsl2vql.codec.roundtrip_text → packages.dsl2vql.src.dsl2vql.grammar.parse_line
  packages.dsl2vql.src.dsl2vql.codec.roundtrip_text → packages.dsl2vql.src.dsl2vql.schema_registry.validate_command_dict
  packages.dsl2vql.src.dsl2vql.codec.roundtrip_text → packages.dsl2vql.src.dsl2vql.grammar.to_text
  packages.dsl2vql.src.dsl2vql.codec.encode_protobuf → packages.dsl2vql.src.dsl2vql.pb_codec.encode_text_to_protobuf
  packages.dsl2vql.src.dsl2vql.codec.decode_protobuf → packages.dsl2vql.src.dsl2vql.pb_codec.decode_protobuf_to_text
  packages.dsl2vql.src.dsl2vql.handlers.command.handle_generate → src.vql.compiler.nl_to_vql.nl_to_program
  packages.dsl2vql.src.dsl2vql.handlers.command.handle_compile → src.vql.compiler.nl_to_vql.nl_to_program
  packages.dsl2vql.src.dsl2vql.handlers.command.handle_patch → packages.uri2vql.src.uri2vql.patch.patch_uri
  packages.dsl2vql.src.dsl2vql.handlers.command.handle_export → packages.dsl2vql.src.dsl2vql.handlers.command._read_json
  packages.dsl2vql.src.dsl2vql.handlers.command.handle_export → src.vql.renderers.svg.render_to_png
  packages.dsl2vql.src.dsl2vql.handlers.command.handle_export → src.vql.renderers.svg.render_to_svg
  packages.dsl2vql.src.dsl2vql.handlers.command.handle_from_tokens → packages.dsl2vql.src.dsl2vql.grammar.parse_line
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

### Integration (1)

**`Auto-generated from Python Tests`**

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/oqlos/vql
# generated in 0.14s
# nodes: 213 | edges: 252 | modules: 52
# CC̄=4.1

HUBS[20]:
  packages.uri2vql.src.uri2vql.window.query_window
    CC=69  in:2  out:147  total:149
  packages.uri2vql.src.uri2vql.nlp2uri.resolve_prompt_to_vql_uri
    CC=54  in:2  out:68  total:70
  src.vql.drawing.svg_path_parser.parse_svg_path
    CC=43  in:1  out:64  total:65
  packages.img2svg.src.img2svg.to_vql.trace_to_vql_program
    CC=15  in:3  out:46  total:49
  src.vql.adopt.window.analyze_screenshot
    CC=13  in:2  out:45  total:47
  src.vql.adopt.window.screenshot_to_program
    CC=12  in:3  out:44  total:47
  packages.dsl2vql.src.dsl2vql.pb_codec._set_body
    CC=12  in:1  out:45  total:46
  packages.img2vql.src.img2vql.detect._detect_buttons
    CC=25  in:1  out:45  total:46
  packages.uri2vql.src.uri2vql.window._query_window_imgl
    CC=17  in:1  out:45  total:46
  packages.img2vql.src.img2vql.describe_ui.describe_ui_layout
    CC=14  in:6  out:39  total:45
  src.vql.adopt.window.capture_diagnose
    CC=33  in:1  out:44  total:45
  examples.photo-roundtrip-test.main
    CC=5  in:0  out:45  total:45
  packages.rest2vql.src.rest2vql.app.create_app
    CC=1  in:1  out:43  total:44
  packages.img2vql.src.img2vql.program.elements_to_vql_program
    CC=11  in:1  out:40  total:41
  packages.dsl2img2svg.src.dsl2img2svg.dispatch.dispatch
    CC=14  in:0  out:41  total:41
  packages.uri2img2svg.src.uri2img2svg.query.query_uri
    CC=13  in:6  out:28  total:34
  packages.dsl2vql.src.dsl2vql.events.EventStore.append
    CC=3  in:0  out:33  total:33
  packages.dsl2vql.src.dsl2vql.grammar.parse_line
    CC=28  in:6  out:27  total:33
  src.vql.adopt.portal_capture.capture_via_portal
    CC=4  in:1  out:30  total:31
  examples.photo-roundtrip-test.test_img2svg_roundtrip
    CC=8  in:2  out:29  total:31

MODULES:
  examples.generate-demo-screen  [3 funcs]
    _load_font  CC=3  out:2
    main  CC=1  out:6
    write_demo_screen  CC=1  out:18
  examples.photo-roundtrip-test  [10 funcs]
    _require_pil  CC=2  out:1
    main  CC=5  out:45
    sample_flat_shapes  CC=1  out:8
    sample_gradient  CC=3  out:21
    sample_nl_drawing  CC=2  out:12
    test_img2svg_roundtrip  CC=8  out:29
    test_img2vql_detect  CC=5  out:5
    test_opencv_contours  CC=2  out:13
    test_ui_grid_adopt  CC=2  out:17
    test_vtracer_roundtrip  CC=10  out:27
  packages.cli2vql.src.cli2vql.cli  [1 funcs]
    _repl  CC=6  out:8
  packages.dsl2img2svg.src.dsl2img2svg.cli  [1 funcs]
    main  CC=4  out:5
  packages.dsl2img2svg.src.dsl2img2svg.dispatch  [2 funcs]
    _parse_kv_args  CC=4  out:4
    dispatch  CC=14  out:41
  packages.dsl2vql.src.dsl2vql.bus  [5 funcs]
    _bytes_to_cmd  CC=3  out:5
    _dispatch_cmd  CC=5  out:12
    dispatch  CC=6  out:15
    execute_dsl  CC=4  out:6
    execute_dsl_line  CC=1  out:1
  packages.dsl2vql.src.dsl2vql.cli  [3 funcs]
    _main_legacy  CC=9  out:20
    _main_subcommand  CC=9  out:21
    main  CC=4  out:2
  packages.dsl2vql.src.dsl2vql.codec  [4 funcs]
    decode_protobuf  CC=1  out:1
    encode_protobuf  CC=1  out:1
    encode_text  CC=2  out:2
    roundtrip_text  CC=3  out:6
  packages.dsl2vql.src.dsl2vql.events  [2 funcs]
    append  CC=3  out:33
    default_event_store  CC=1  out:4
  packages.dsl2vql.src.dsl2vql.grammar  [4 funcs]
    parse_line  CC=28  out:27
    pick_flag  CC=3  out:2
    split_command  CC=4  out:4
    to_text  CC=6  out:11
  packages.dsl2vql.src.dsl2vql.handlers.command  [6 funcs]
    _read_json  CC=1  out:4
    handle_compile  CC=4  out:11
    handle_export  CC=7  out:15
    handle_from_tokens  CC=11  out:15
    handle_generate  CC=4  out:12
    handle_patch  CC=3  out:12
  packages.dsl2vql.src.dsl2vql.handlers.query  [5 funcs]
    _load_program  CC=1  out:5
    handle_query  CC=4  out:8
    handle_render  CC=9  out:16
    handle_resolve  CC=3  out:5
    handle_validate  CC=6  out:11
  packages.dsl2vql.src.dsl2vql.pb_codec  [8 funcs]
    _set_body  CC=12  out:45
    decode_protobuf  CC=1  out:3
    decode_protobuf_to_text  CC=1  out:2
    encode_protobuf  CC=1  out:6
    encode_result_protobuf  CC=1  out:2
    encode_text_to_protobuf  CC=2  out:3
    envelope_to_dict  CC=31  out:4
    result_to_pb  CC=4  out:4
  packages.dsl2vql.src.dsl2vql.schema_registry  [5 funcs]
    _load_schemas  CC=3  out:9
    all_schemas  CC=1  out:2
    schema_for_verb  CC=1  out:3
    validate_command_dict  CC=3  out:7
    validate_schema_registry  CC=3  out:6
  packages.img2svg.src.img2svg.svg_emit  [2 funcs]
    image_to_svg  CC=7  out:24
    paths_to_svg  CC=3  out:9
  packages.img2svg.src.img2svg.to_vql  [2 funcs]
    image_to_vql  CC=5  out:17
    trace_to_vql_program  CC=15  out:46
  packages.img2svg.src.img2svg.trace  [7 funcs]
    _hex_color  CC=1  out:0
    _merge_grid_cells  CC=15  out:9
    _parse_translate  CC=3  out:5
    _parse_vtracer_svg  CC=5  out:16
    trace_contours_opencv  CC=8  out:23
    trace_image_regions  CC=6  out:17
    trace_vtracer  CC=6  out:17
  packages.img2vql.src.img2vql.adopt  [1 funcs]
    adopt_screenshot  CC=2  out:20
  packages.img2vql.src.img2vql.describe_ui  [1 funcs]
    describe_ui_layout  CC=14  out:39
  packages.img2vql.src.img2vql.detect  [10 funcs]
    _avg_color  CC=5  out:8
    _dedupe  CC=8  out:6
    _detect_buttons  CC=25  out:45
    _detect_panels  CC=5  out:14
    _detect_titlebar  CC=5  out:11
    _detect_toolbar  CC=10  out:21
    _flood_rects  CC=14  out:13
    _hex_color  CC=1  out:0
    _iou  CC=3  out:5
    detect_ui_elements  CC=8  out:19
  packages.img2vql.src.img2vql.diagnose  [4 funcs]
    _normalize_locale  CC=4  out:4
    _recommendation  CC=6  out:10
    diagnose_for_vql  CC=10  out:21
    diagnose_image  CC=2  out:3
  packages.img2vql.src.img2vql.fingerprint  [3 funcs]
    _json_safe  CC=7  out:8
    compare_with_program  CC=5  out:19
    load_program_fingerprint  CC=6  out:9
  packages.img2vql.src.img2vql.metadata  [12 funcs]
    _compact_special_hits  CC=1  out:10
    _json_safe  CC=7  out:8
    _merge_special_hits  CC=2  out:8
    _text_likely  CC=4  out:7
    auto_ocr_special_hits  CC=3  out:7
    img2nl_metadata_slice  CC=9  out:17
    imgl_ocr_special_hits  CC=8  out:12
    merge_program_metadata  CC=1  out:8
    metadata_from_diagnose  CC=6  out:21
    rapidocr_special_hits  CC=10  out:16
  packages.img2vql.src.img2vql.program  [3 funcs]
    _bbox_contains  CC=4  out:0
    _build_contains_relations  CC=8  out:9
    elements_to_vql_program  CC=11  out:40
  packages.mcp2vql.src.mcp2vql.server  [2 funcs]
    __post_init__  CC=1  out:3
    _require_fastmcp  CC=2  out:1
  packages.nlp2vql.src.nlp2vql.apply  [1 funcs]
    apply_nl  CC=2  out:4
  packages.nlp2vql.src.nlp2vql.to_dsl  [3 funcs]
    _intent  CC=11  out:6
    nl_to_dsl_line  CC=8  out:1
    to_dsl  CC=1  out:1
  packages.rest2vql.src.rest2vql.app  [1 funcs]
    create_app  CC=1  out:43
  packages.rest2vql.src.rest2vql.cli  [1 funcs]
    main  CC=1  out:7
  packages.rest2vql.src.rest2vql.window  [7 funcs]
    window_adopt  CC=1  out:1
    window_analyze  CC=1  out:1
    window_compare  CC=1  out:1
    window_detect  CC=2  out:3
    window_diagnose  CC=2  out:1
    window_refresh  CC=1  out:1
    window_summary  CC=7  out:1
  packages.rest2vql.src.rest2vql.window_routes  [8 funcs]
    _window_response  CC=2  out:2
    post_window_adopt  CC=2  out:5
    post_window_analyze  CC=2  out:5
    post_window_compare  CC=2  out:5
    post_window_detect  CC=2  out:5
    post_window_diagnose  CC=2  out:5
    post_window_refresh  CC=2  out:5
    post_window_summary  CC=2  out:5
  packages.uri2img2svg.src.uri2img2svg.cli  [1 funcs]
    main  CC=4  out:9
  packages.uri2img2svg.src.uri2img2svg.query  [1 funcs]
    query_uri  CC=13  out:28
  packages.uri2img2svg.src.uri2img2svg.uri  [1 funcs]
    parse_img2svg_uri  CC=9  out:11
  packages.uri2vql.src.uri2vql.compile  [2 funcs]
    _dsl_from_uri  CC=4  out:5
    compile_vql_uri  CC=7  out:8
  packages.uri2vql.src.uri2vql.nlp2uri  [3 funcs]
    best_uri  CC=2  out:1
    nlp2uri  CC=1  out:1
    resolve_prompt_to_vql_uri  CC=54  out:68
  packages.uri2vql.src.uri2vql.patch  [1 funcs]
    patch_uri  CC=7  out:15
  packages.uri2vql.src.uri2vql.query  [2 funcs]
    _load_program  CC=1  out:5
    query_uri  CC=15  out:20
  packages.uri2vql.src.uri2vql.run  [2 funcs]
    run_uri  CC=7  out:8
    run_uri_json  CC=1  out:3
  packages.uri2vql.src.uri2vql.uri  [16 funcs]
    _with_file  CC=4  out:4
    is_vql_uri  CC=1  out:2
    parse_vql_uri  CC=5  out:6
    uri_for_imgl_click  CC=6  out:1
    uri_for_imgl_list  CC=1  out:1
    uri_for_imgl_type  CC=6  out:1
    uri_for_object  CC=1  out:1
    uri_for_objects  CC=1  out:1
    uri_for_program  CC=1  out:1
    uri_for_scene  CC=1  out:1
  packages.uri2vql.src.uri2vql.window  [9 funcs]
    _diagnose_fallback  CC=15  out:29
    _normalize_locale  CC=4  out:4
    _query_window_imgl  CC=17  out:45
    _resolve_image_param  CC=6  out:12
    analyze_window_uri  CC=4  out:9
    compare_window_image  CC=2  out:3
    diagnose_window_image  CC=2  out:3
    query_window  CC=69  out:147
    refresh_window_metadata  CC=2  out:2
  src.vql.adopt.portal_capture  [2 funcs]
    capture_via_portal  CC=4  out:30
    main  CC=2  out:9
  src.vql.adopt.window  [25 funcs]
    _active_window_title  CC=4  out:3
    _capture_backends  CC=7  out:7
    _capture_interactive_mode  CC=2  out:3
    _capture_permission_hint  CC=2  out:1
    _capture_with_gnome_screenshot  CC=2  out:4
    _capture_with_gnome_shell  CC=2  out:4
    _capture_with_grim  CC=2  out:4
    _capture_with_mss  CC=4  out:8
    _capture_with_portal  CC=15  out:21
    _capture_with_scrot  CC=2  out:4
  src.vql.compiler.legacy_drawcommand  [3 funcs]
    commands_to_program  CC=9  out:15
    compile_to_events  CC=3  out:6
    program_to_commands  CC=4  out:7
  src.vql.compiler.nl_to_vql  [1 funcs]
    nl_to_program  CC=6  out:9
  src.vql.drawing.nl_parser  [1 funcs]
    to_vql  CC=1  out:1
  src.vql.drawing.path_generator  [1 funcs]
    generate  CC=5  out:7
  src.vql.drawing.svg_path_parser  [1 funcs]
    parse_svg_path  CC=43  out:64
  src.vql.facade  [6 funcs]
    compile  CC=1  out:1
    render_png  CC=1  out:1
    render_svg  CC=1  out:1
    to_commands  CC=1  out:1
    to_events  CC=1  out:1
    validate  CC=1  out:1
  src.vql.renderers.base  [2 funcs]
    render  CC=1  out:1
    render_program  CC=1  out:3
  src.vql.renderers.svg  [2 funcs]
    render_to_png  CC=2  out:8
    render_to_svg  CC=1  out:4
  src.vql.validation.spec  [4 funcs]
    _match_items  CC=4  out:3
    _program_colors  CC=2  out:2
    _program_shapes  CC=3  out:1
    validate_program  CC=4  out:12

EDGES:
  packages.uri2img2svg.src.uri2img2svg.cli.main → packages.uri2img2svg.src.uri2img2svg.query.query_uri
  packages.uri2img2svg.src.uri2img2svg.query.query_uri → packages.uri2img2svg.src.uri2img2svg.uri.parse_img2svg_uri
  packages.uri2img2svg.src.uri2img2svg.query.query_uri → packages.img2svg.src.img2svg.svg_emit.image_to_svg
  packages.uri2img2svg.src.uri2img2svg.query.query_uri → packages.img2svg.src.img2svg.to_vql.image_to_vql
  packages.dsl2vql.src.dsl2vql.bus._dispatch_cmd → packages.dsl2vql.src.dsl2vql.schema_registry.validate_command_dict
  packages.dsl2vql.src.dsl2vql.bus._dispatch_cmd → packages.dsl2vql.src.dsl2vql.grammar.split_command
  packages.dsl2vql.src.dsl2vql.bus._dispatch_cmd → packages.dsl2vql.src.dsl2vql.handlers.command.handle_from_tokens
  packages.dsl2vql.src.dsl2vql.bus._dispatch_cmd → packages.dsl2vql.src.dsl2vql.events.default_event_store
  packages.dsl2vql.src.dsl2vql.bus._bytes_to_cmd → packages.dsl2vql.src.dsl2vql.pb_codec.decode_protobuf
  packages.dsl2vql.src.dsl2vql.bus._bytes_to_cmd → packages.dsl2vql.src.dsl2vql.grammar.to_text
  packages.dsl2vql.src.dsl2vql.bus._bytes_to_cmd → packages.dsl2vql.src.dsl2vql.grammar.parse_line
  packages.dsl2vql.src.dsl2vql.bus.dispatch → packages.dsl2vql.src.dsl2vql.grammar.split_command
  packages.dsl2vql.src.dsl2vql.bus.dispatch → packages.dsl2vql.src.dsl2vql.bus._dispatch_cmd
  packages.dsl2vql.src.dsl2vql.bus.dispatch → packages.dsl2vql.src.dsl2vql.bus._bytes_to_cmd
  packages.dsl2vql.src.dsl2vql.bus.dispatch → packages.dsl2vql.src.dsl2vql.grammar.to_text
  packages.dsl2vql.src.dsl2vql.bus.execute_dsl_line → packages.dsl2vql.src.dsl2vql.bus.dispatch
  packages.dsl2vql.src.dsl2vql.bus.execute_dsl → packages.dsl2vql.src.dsl2vql.bus.execute_dsl_line
  packages.dsl2vql.src.dsl2vql.cli._main_legacy → packages.dsl2vql.src.dsl2vql.bus.execute_dsl_line
  packages.dsl2vql.src.dsl2vql.cli._main_legacy → packages.dsl2vql.src.dsl2vql.bus.execute_dsl
  packages.dsl2vql.src.dsl2vql.cli._main_subcommand → packages.dsl2vql.src.dsl2vql.schema_registry.validate_schema_registry
  packages.dsl2vql.src.dsl2vql.cli.main → packages.dsl2vql.src.dsl2vql.cli._main_legacy
  packages.dsl2vql.src.dsl2vql.cli.main → packages.dsl2vql.src.dsl2vql.cli._main_subcommand
  packages.dsl2vql.src.dsl2vql.events.EventStore.append → packages.dsl2vql.src.dsl2vql.pb_codec.encode_protobuf
  packages.dsl2vql.src.dsl2vql.pb_codec.encode_protobuf → packages.dsl2vql.src.dsl2vql.pb_codec._set_body
  packages.dsl2vql.src.dsl2vql.pb_codec.decode_protobuf → packages.dsl2vql.src.dsl2vql.pb_codec.envelope_to_dict
  packages.dsl2vql.src.dsl2vql.pb_codec.encode_text_to_protobuf → packages.dsl2vql.src.dsl2vql.grammar.parse_line
  packages.dsl2vql.src.dsl2vql.pb_codec.encode_text_to_protobuf → packages.dsl2vql.src.dsl2vql.pb_codec.encode_protobuf
  packages.dsl2vql.src.dsl2vql.pb_codec.decode_protobuf_to_text → packages.dsl2vql.src.dsl2vql.grammar.to_text
  packages.dsl2vql.src.dsl2vql.pb_codec.decode_protobuf_to_text → packages.dsl2vql.src.dsl2vql.pb_codec.decode_protobuf
  packages.dsl2vql.src.dsl2vql.pb_codec.encode_result_protobuf → packages.dsl2vql.src.dsl2vql.pb_codec.result_to_pb
  packages.dsl2vql.src.dsl2vql.schema_registry.schema_for_verb → packages.dsl2vql.src.dsl2vql.schema_registry._load_schemas
  packages.dsl2vql.src.dsl2vql.schema_registry.all_schemas → packages.dsl2vql.src.dsl2vql.schema_registry._load_schemas
  packages.dsl2vql.src.dsl2vql.schema_registry.validate_command_dict → packages.dsl2vql.src.dsl2vql.schema_registry.schema_for_verb
  packages.dsl2vql.src.dsl2vql.schema_registry.validate_schema_registry → packages.dsl2vql.src.dsl2vql.schema_registry._load_schemas
  packages.dsl2vql.src.dsl2vql.grammar.parse_line → packages.dsl2vql.src.dsl2vql.grammar.split_command
  packages.dsl2vql.src.dsl2vql.grammar.parse_line → packages.dsl2vql.src.dsl2vql.grammar.pick_flag
  packages.dsl2vql.src.dsl2vql.codec.encode_text → packages.dsl2vql.src.dsl2vql.grammar.parse_line
  packages.dsl2vql.src.dsl2vql.codec.encode_text → packages.dsl2vql.src.dsl2vql.schema_registry.validate_command_dict
  packages.dsl2vql.src.dsl2vql.codec.roundtrip_text → packages.dsl2vql.src.dsl2vql.grammar.parse_line
  packages.dsl2vql.src.dsl2vql.codec.roundtrip_text → packages.dsl2vql.src.dsl2vql.schema_registry.validate_command_dict
  packages.dsl2vql.src.dsl2vql.codec.roundtrip_text → packages.dsl2vql.src.dsl2vql.grammar.to_text
  packages.dsl2vql.src.dsl2vql.codec.encode_protobuf → packages.dsl2vql.src.dsl2vql.pb_codec.encode_text_to_protobuf
  packages.dsl2vql.src.dsl2vql.codec.decode_protobuf → packages.dsl2vql.src.dsl2vql.pb_codec.decode_protobuf_to_text
  packages.dsl2vql.src.dsl2vql.handlers.command.handle_generate → src.vql.compiler.nl_to_vql.nl_to_program
  packages.dsl2vql.src.dsl2vql.handlers.command.handle_compile → src.vql.compiler.nl_to_vql.nl_to_program
  packages.dsl2vql.src.dsl2vql.handlers.command.handle_patch → packages.uri2vql.src.uri2vql.patch.patch_uri
  packages.dsl2vql.src.dsl2vql.handlers.command.handle_export → packages.dsl2vql.src.dsl2vql.handlers.command._read_json
  packages.dsl2vql.src.dsl2vql.handlers.command.handle_export → src.vql.renderers.svg.render_to_png
  packages.dsl2vql.src.dsl2vql.handlers.command.handle_export → src.vql.renderers.svg.render_to_svg
  packages.dsl2vql.src.dsl2vql.handlers.command.handle_from_tokens → packages.dsl2vql.src.dsl2vql.grammar.parse_line
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 165f 119602L | python:129,toml:11,json:9,shell:8,yaml:5,proto:2 | 2026-06-09
# generated in 0.05s
# CC̅=4.1 | critical:15/410 | dups:0 | cycles:0

HEALTH[15]:
  🟡 CC    envelope_to_dict CC=31 (limit:15)
  🟡 CC    parse_line CC=28 (limit:15)
  🟡 CC    main CC=53 (limit:15)
  🟡 CC    resolve_prompt_to_vql_uri CC=54 (limit:15)
  🟡 CC    query_uri CC=15 (limit:15)
  🟡 CC    _diagnose_fallback CC=15 (limit:15)
  🟡 CC    _query_window_imgl CC=17 (limit:15)
  🟡 CC    query_window CC=69 (limit:15)
  🟡 CC    _detect_buttons CC=25 (limit:15)
  🟡 CC    _capture_with_portal CC=15 (limit:15)
  🟡 CC    capture_diagnose CC=33 (limit:15)
  🟡 CC    _merge_grid_colors CC=15 (limit:15)
  🟡 CC    _merge_grid_cells CC=15 (limit:15)
  🟡 CC    trace_to_vql_program CC=15 (limit:15)
  🟡 CC    parse_svg_path CC=43 (limit:15)

REFACTOR[1]:
  1. split 15 high-CC methods  (CC>15)

PIPELINES[167]:
  [1] Src [main]: main → query_uri → parse_img2svg_uri
      PURITY: 100% pure
  [2] Src [is_img2svg_uri]: is_img2svg_uri
      PURITY: 100% pure
  [3] Src [uri_for_vectorize]: uri_for_vectorize
      PURITY: 100% pure
  [4] Src [main]: main → _main_legacy → execute_dsl_line → dispatch → ...(1 more)
      PURITY: 100% pure
  [5] Src [to_dict]: to_dict
      PURITY: 100% pure
  [6] Src [__init__]: __init__
      PURITY: 100% pure
  [7] Src [append]: append → encode_protobuf → _set_body
      PURITY: 100% pure
  [8] Src [replay]: replay
      PURITY: 100% pure
  [9] Src [encode_text]: encode_text → parse_line → split_command
      PURITY: 100% pure
  [10] Src [roundtrip_text]: roundtrip_text → parse_line → split_command
      PURITY: 100% pure
  [11] Src [encode_protobuf]: encode_protobuf → encode_text_to_protobuf → parse_line → split_command
      PURITY: 100% pure
  [12] Src [decode_protobuf]: decode_protobuf → decode_protobuf_to_text → to_text
      PURITY: 100% pure
  [13] Src [main]: main → _repl → dispatch → split_command
      PURITY: 100% pure
  [14] Src [__post_init__]: __post_init__ → _require_fastmcp
      PURITY: 100% pure
  [15] Src [_register_tools]: _register_tools → query_uri → parse_img2svg_uri
      PURITY: 100% pure
  [16] Src [run]: run
      PURITY: 100% pure
  [17] Src [main]: main
      PURITY: 100% pure
  [18] Src [main]: main → query_uri → parse_img2svg_uri
      PURITY: 100% pure
  [19] Src [best_uri]: best_uri → nlp2uri → resolve_prompt_to_vql_uri → _extract_click_target
      PURITY: 100% pure
  [20] Src [query_uri]: query_uri → query_window → analyze_window_uri → analyze_screenshot → ...(2 more)
      PURITY: 100% pure
  [21] Src [uri_for_object]: uri_for_object → _with_file
      PURITY: 100% pure
  [22] Src [compile_vql_uri]: compile_vql_uri → _dsl_from_uri
      PURITY: 100% pure
  [23] Src [run_uri_json]: run_uri_json → run_uri → parse_vql_uri
      PURITY: 100% pure
  [24] Src [main]: main → apply_nl → nl_to_dsl_line → _intent
      PURITY: 100% pure
  [25] Src [main]: main → create_app → schema_for_verb → _load_schemas
      PURITY: 100% pure
  [26] Src [post_window_detect]: post_window_detect → _window_response
      PURITY: 100% pure
  [27] Src [post_window_compare]: post_window_compare → _window_response
      PURITY: 100% pure
  [28] Src [post_window_refresh]: post_window_refresh → _window_response
      PURITY: 100% pure
  [29] Src [post_window_diagnose]: post_window_diagnose → _window_response
      PURITY: 100% pure
  [30] Src [post_window_analyze]: post_window_analyze → _window_response
      PURITY: 100% pure
  [31] Src [post_window_adopt]: post_window_adopt → _window_response
      PURITY: 100% pure
  [32] Src [post_window_summary]: post_window_summary → _window_response
      PURITY: 100% pure
  [33] Src [main]: main → dispatch → split_command
      PURITY: 100% pure
  [34] Src [dispatch]: dispatch → _parse_kv_args
      PURITY: 100% pure
  [35] Src [main]: main → detect_ui_elements → _detect_titlebar → _avg_color
      PURITY: 100% pure
  [36] Src [to_dict]: to_dict
      PURITY: 100% pure
  [37] Src [fingerprint_for_image]: fingerprint_for_image
      PURITY: 100% pure
  [38] Src [main]: main → write_demo_screen → _load_font
      PURITY: 100% pure
  [39] Src [main]: main
      PURITY: 100% pure
  [40] Src [compile]: compile → nl_to_program → commands_to_program
      PURITY: 100% pure
  [41] Src [validate]: validate → validate_program → _match_items
      PURITY: 100% pure
  [42] Src [render_svg]: render_svg → render_to_svg → render_program → compile_to_events → ...(1 more)
      PURITY: 100% pure
  [43] Src [render_png]: render_png → render_to_png → render_to_svg → render_program → ...(2 more)
      PURITY: 100% pure
  [44] Src [to_commands]: to_commands → program_to_commands
      PURITY: 100% pure
  [45] Src [to_events]: to_events → compile_to_events → program_to_commands
      PURITY: 100% pure
  [46] Src [run]: run
      PURITY: 100% pure
  [47] Src [render]: render → render_program → compile_to_events → program_to_commands
      PURITY: 100% pure
  [48] Src [__getattr__]: __getattr__
      PURITY: 100% pure
  [49] Src [__init__]: __init__
      PURITY: 100% pure
  [50] Src [validate]: validate
      PURITY: 100% pure

LAYERS:
  packages/                       CC̄=5.6    ←in:0  →out:0
  │ !! window                     653L  1C   11m  CC=69     ←4
  │ !! detect                     379L  1C   12m  CC=25     ←7
  │ !! cli                        352L  0C    1m  CC=53     ←0
  │ metadata                   339L  0C   12m  CC=10     ←6
  │ !! nlp2uri                    329L  1C    6m  CC=54     ←1
  │ !! trace                      263L  1C    8m  CC=15     ←6
  │ uri                        183L  1C   16m  CC=6      ←5
  │ !! pb_codec                   157L  0C    8m  CC=31     ←6
  │ query                      144L  1C    2m  CC=13     ←6
  │ program                    141L  0C    4m  CC=11     ←1
  │ !! to_vql                     141L  0C    3m  CC=15     ←4
  │ server                     135L  1C    5m  CC=2      ←0
  │ svg_emit                   134L  0C    4m  CC=7      ←4
  │ command                    130L  0C    6m  CC=11     ←1
  │ diagnose                   125L  0C    4m  CC=10     ←4
  │ window                     124L  1C    7m  CC=7      ←1
  │ describe_ui                121L  0C    3m  CC=14     ←6
  │ dispatch                   115L  1C    3m  CC=14     ←0
  │ window_routes              110L  0C    8m  CC=2      ←0
  │ query                      109L  0C    5m  CC=9      ←1
  │ events                     108L  2C    5m  CC=6      ←2
  │ fingerprint                104L  0C    4m  CC=7      ←6
  │ cli                         97L  0C    3m  CC=9      ←0
  │ !! grammar                     96L  0C    4m  CC=28     ←4
  │ !! query                       95L  1C    3m  CC=15     ←0
  │ cli                         87L  0C    1m  CC=10     ←0
  │ bus                         77L  0C    5m  CC=6      ←9
  │ app                         72L  0C    1m  CC=1      ←1
  │ cli                         71L  0C    1m  CC=11     ←0
  │ cli                         68L  0C    2m  CC=14     ←0
  │ run                         64L  1C    3m  CC=7      ←0
  │ adopt                       63L  0C    1m  CC=2      ←4
  │ command.proto               62L  0C    0m  CC=0.0    ←0
  │ uri                         59L  1C    3m  CC=9      ←1
  │ cli                         53L  0C    1m  CC=11     ←0
  │ command_pb2                 52L  0C    0m  CC=0.0    ←0
  │ apply                       48L  1C    2m  CC=2      ←2
  │ schema_registry             46L  0C    5m  CC=3      ←4
  │ __init__                    45L  0C    0m  CC=0.0    ←0
  │ to_dsl                      42L  0C    3m  CC=11     ←4
  │ patch                       40L  1C    2m  CC=7      ←3
  │ result_pb2                  39L  0C    0m  CC=0.0    ←0
  │ compile                     36L  0C    2m  CC=7      ←0
  │ codec                       35L  0C    4m  CC=3      ←0
  │ pyproject.toml              33L  0C    0m  CC=0.0    ←0
  │ cli                         28L  0C    1m  CC=4      ←0
  │ result                      28L  1C    1m  CC=1      ←0
  │ pyproject.toml              26L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              26L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              26L  0C    0m  CC=0.0    ←0
  │ __init__                    26L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              26L  0C    0m  CC=0.0    ←0
  │ cli                         24L  0C    1m  CC=1      ←0
  │ pyproject.toml              24L  0C    0m  CC=0.0    ←0
  │ result.proto                23L  0C    0m  CC=0.0    ←0
  │ cli                         21L  0C    1m  CC=4      ←0
  │ pyproject.toml              18L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              18L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              18L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              18L  0C    0m  CC=0.0    ←0
  │ __init__                    13L  0C    0m  CC=0.0    ←0
  │ patch.schema.json           12L  0C    0m  CC=0.0    ←0
  │ compile.schema.json         12L  0C    0m  CC=0.0    ←0
  │ query.schema.json           12L  0C    0m  CC=0.0    ←0
  │ render.schema.json          12L  0C    0m  CC=0.0    ←0
  │ generate.schema.json        11L  0C    0m  CC=0.0    ←0
  │ validate.schema.json        10L  0C    0m  CC=0.0    ←0
  │ engine                       8L  0C    0m  CC=0.0    ←0
  │ cli                          8L  0C    0m  CC=0.0    ←0
  │ generate-proto.sh            7L  0C    0m  CC=0.0    ←0
  │ __init__                     6L  0C    0m  CC=0.0    ←0
  │ __init__                     6L  0C    0m  CC=0.0    ←0
  │ __init__                     6L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __init__                     5L  0C    0m  CC=0.0    ←0
  │ __init__                     1L  0C    0m  CC=0.0    ←0
  │
  src/                            CC̄=2.9    ←in:0  →out:0
  │ !! window                     804L  3C   29m  CC=33     ←5
  │ program                    423L  12C   32m  CC=5      ←0
  │ commands                   271L  8C   19m  CC=8      ←0
  │ nl_parser                  225L  1C    8m  CC=11     ←0
  │ playwright                 215L  1C    8m  CC=9      ←0
  │ !! svg_path_parser            192L  0C    1m  CC=43     ←1
  │ events                     142L  7C    7m  CC=1      ←0
  │ legacy_drawcommand         142L  0C    3m  CC=9      ←3
  │ colors                     135L  1C    6m  CC=6      ←0
  │ portal_capture             109L  0C    2m  CC=4      ←0
  │ shape_registry             103L  1C    4m  CC=3      ←0
  │ event_store                101L  1C   13m  CC=3      ←0
  │ facade                      95L  2C    7m  CC=2      ←0
  │ svg                         93L  1C    8m  CC=6      ←0
  │ spec                        91L  1C    5m  CC=4      ←2
  │ base                        84L  1C    8m  CC=3      ←0
  │ shapes                      78L  0C    0m  CC=0.0    ←0
  │ nl_to_vql                   69L  0C    1m  CC=6      ←4
  │ base                        65L  2C    3m  CC=1      ←1
  │ castle_generator            63L  1C    1m  CC=3      ←0
  │ cat_generator               55L  1C    1m  CC=4      ←0
  │ __init__                    54L  0C    0m  CC=0.0    ←0
  │ api                         54L  0C    0m  CC=0.0    ←0
  │ rocket_generator            52L  1C    1m  CC=2      ←0
  │ svg                         51L  1C    2m  CC=2      ←4
  │ butterfly_generator         50L  1C    1m  CC=5      ←0
  │ bird_generator              49L  1C    1m  CC=2      ←0
  │ car_generator               48L  1C    1m  CC=3      ←0
  │ cloud_detailed_generator    47L  1C    1m  CC=4      ←0
  │ fish_generator              46L  1C    1m  CC=3      ←0
  │ arrow_generator             46L  1C    1m  CC=3      ←0
  │ boat_generator              40L  1C    1m  CC=1      ←0
  │ mountain_generator          39L  1C    1m  CC=1      ←0
  │ shape_generator             37L  1C    1m  CC=1      ←0
  │ diamond_generator           36L  1C    1m  CC=1      ←0
  │ crescent_generator          36L  1C    1m  CC=3      ←0
  │ sun_generator               36L  1C    1m  CC=3      ←0
  │ grid_generator              36L  1C    1m  CC=3      ←0
  │ flower_generator            35L  1C    1m  CC=3      ←0
  │ wave_generator              34L  1C    1m  CC=2      ←0
  │ tree_generator              33L  1C    1m  CC=2      ←0
  │ star_generator              33L  1C    1m  CC=2      ←0
  │ cross_generator             33L  1C    1m  CC=1      ←0
  │ __init__                    33L  0C    0m  CC=0.0    ←0
  │ spiral_generator            32L  1C    1m  CC=2      ←0
  │ house_generator             30L  1C    1m  CC=1      ←0
  │ ellipse_generator           30L  1C    1m  CC=2      ←0
  │ heart_generator             30L  1C    1m  CC=2      ←0
  │ dot_generator               29L  1C    1m  CC=2      ←0
  │ circle_generator            29L  1C    1m  CC=2      ←0
  │ octagon_generator           27L  1C    1m  CC=2      ←0
  │ hexagon_generator           27L  1C    1m  CC=2      ←0
  │ pentagon_generator          27L  1C    1m  CC=2      ←0
  │ triangle_generator          26L  1C    1m  CC=1      ←0
  │ rectangle_generator         26L  1C    1m  CC=1      ←0
  │ line_generator              25L  1C    1m  CC=1      ←0
  │ square_generator            25L  1C    1m  CC=1      ←0
  │ path_generator              25L  1C    1m  CC=5      ←0
  │ __init__                    23L  0C    1m  CC=2      ←0
  │ playwright                  22L  1C    1m  CC=1      ←0
  │ __init__                    19L  0C    0m  CC=0.0    ←0
  │ __init__                    16L  0C    0m  CC=0.0    ←0
  │ __init__                    15L  0C    0m  CC=0.0    ←0
  │ __init__                    14L  0C    0m  CC=0.0    ←0
  │ __init__                    11L  0C    0m  CC=0.0    ←0
  │ __init__                     9L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=2.5    ←in:0  →out:18  !! split
  │ photo-roundtrip-test       338L  0C   10m  CC=10     ←0
  │ img2nl-vql-flow.sh         214L  0C    6m  CC=0.0    ←0
  │ live-capture-test.sh        94L  0C    0m  CC=0.0    ←0
  │ full-pipeline.sh            80L  0C    0m  CC=0.0    ←0
  │ generate-demo-screen        76L  0C    3m  CC=3      ←0
  │ scope-window                53L  0C    1m  CC=6      ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! layout.vql.json          78775L  0C    0m  CC=0.0    ←0
  │ !! layout.vql.imgl.json     21939L  0C    0m  CC=0.0    ←0
  │ !! app.vql.json              5803L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  511L  0C    0m  CC=0.0    ←0
  │ Makefile                   112L  0C    0m  CC=0.0    ←0
  │ prefact.yaml                94L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              65L  0C    0m  CC=0.0    ←0
  │ project.sh                  59L  0C    0m  CC=0.0    ←0
  │ install-dev.sh              37L  0C    0m  CC=0.0    ←0
  │ nlp2uri.yaml                 8L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │
  scripts/                        CC̄=0.0    ←in:0  →out:0
  │ test-goal.sh                 6L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-cli-tests.testql.toon.yaml    20L  0C    0m  CC=0.0    ←0
  │ generated-from-pytests.testql.toon.yaml    12L  0C    0m  CC=0.0    ←0
  │

COUPLING:
                            packages.dsl2vql               src.vql      packages.img2vql      packages.uri2vql              examples      packages.img2svg     packages.rest2vql      packages.mcp2vql  packages.uri2img2svg  packages.dsl2img2svg      packages.nlp2vql      packages.cli2vql
      packages.dsl2vql                    ──                     7                                           1                                                                ←7                    ←4                     1                    ←1                     1                    ←3  hub
               src.vql                    ←7                    ──                     3                    ←5                   ←10                                          ←1                                                                                                                hub
      packages.img2vql                                           1                    ──                    ←9                    ←1                                          ←6                    ←5                                                                                          hub
      packages.uri2vql                     2                     5                     9                    ──                                                                ←1                    ←2                     2                                                                    !! fan-out
              examples                                          10                     1                                          ──                     7                                                                                                                                      !! fan-out
      packages.img2svg                                                                                                            ←7                    ──                                                                ←4                    ←4                                              hub
     packages.rest2vql                     7                     1                     6                     1                                                                ──                                                                                                                !! fan-out
      packages.mcp2vql                     4                                           5                     2                                                                                      ──                     1                                           2                        !! fan-out
  packages.uri2img2svg                    ←1                                                                ←2                                           4                                          ←1                    ──                    ←1                                              hub
  packages.dsl2img2svg                     1                                                                                                             4                                                                 1                    ──                                            
      packages.nlp2vql                     2                                                                                                                                                        ←2                                                                ──                      
      packages.cli2vql                     3                                                                                                                                                                                                                                                ──
  CYCLES: none
  HUB: packages.img2svg/ (fan-in=15)
  HUB: packages.img2vql/ (fan-in=24)
  HUB: src.vql/ (fan-in=24)
  HUB: packages.dsl2vql/ (fan-in=19)
  HUB: packages.uri2img2svg/ (fan-in=5)
  SMELL: examples/ fan-out=18 → split needed
  SMELL: packages.mcp2vql/ fan-out=14 → split needed
  SMELL: packages.uri2vql/ fan-out=18 → split needed
  SMELL: packages.dsl2vql/ fan-out=10 → split needed
  SMELL: packages.rest2vql/ fan-out=15 → split needed

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 10 groups | 128f 11040L | 2026-06-09

SUMMARY:
  files_scanned: 128
  total_lines:   11040
  dup_groups:    10
  dup_fragments: 20
  saved_lines:   82
  scan_ms:       5712

HOTSPOTS[7] (files with most duplication):
  src/vql/adopt/window.py  dup=48L  groups=2  frags=4  (0.4%)
  packages/rest2vql/src/rest2vql/window_routes.py  dup=36L  groups=2  frags=4  (0.3%)
  packages/uri2vql/src/uri2vql/uri.py  dup=20L  groups=1  frags=2  (0.2%)
  packages/img2vql/src/img2vql/fingerprint.py  dup=11L  groups=1  frags=1  (0.1%)
  packages/img2vql/src/img2vql/metadata.py  dup=11L  groups=1  frags=1  (0.1%)
  packages/img2vql/src/img2vql/diagnose.py  dup=8L  groups=1  frags=1  (0.1%)
  packages/uri2vql/src/uri2vql/window.py  dup=8L  groups=1  frags=1  (0.1%)

DUPLICATES[10] (ranked by impact):
  [a493779543db54d2]   STRU  _capture_with_grim  L=15 N=2 saved=15 sim=1.00
      src/vql/adopt/window.py:217-231  (_capture_with_grim)
      src/vql/adopt/window.py:289-303  (_capture_with_scrot)
  [b0bee04d87d1dcf7]   STRU  post_window_diagnose  L=13 N=2 saved=13 sim=1.00
      packages/rest2vql/src/rest2vql/window_routes.py:52-64  (post_window_diagnose)
      packages/rest2vql/src/rest2vql/window_routes.py:83-95  (post_window_adopt)
  [1c4cf578f377406c]   EXAC  _json_safe  L=11 N=2 saved=11 sim=1.00
      packages/img2vql/src/img2vql/fingerprint.py:43-53  (_json_safe)
      packages/img2vql/src/img2vql/metadata.py:13-23  (_json_safe)
  [085bde726092c26c]   STRU  uri_for_window_diagnose  L=10 N=2 saved=10 sim=1.00
      packages/uri2vql/src/uri2vql/uri.py:141-150  (uri_for_window_diagnose)
      packages/uri2vql/src/uri2vql/uri.py:164-173  (uri_for_window_refresh)
  [de5cf8cb508ec617]   STRU  runner  L=9 N=2 saved=9 sim=1.00
      src/vql/adopt/window.py:221-229  (runner)
      src/vql/adopt/window.py:293-301  (runner)
  [99163857767f8c3d]   EXAC  _normalize_locale  L=8 N=2 saved=8 sim=1.00
      packages/img2vql/src/img2vql/diagnose.py:9-16  (_normalize_locale)
      packages/uri2vql/src/uri2vql/window.py:32-39  (_normalize_locale)
  [6369695505dbbdc9]   EXAC  _load_program  L=5 N=2 saved=5 sim=1.00
      packages/dsl2vql/src/dsl2vql/handlers/query.py:12-16  (_load_program)
      packages/uri2vql/src/uri2vql/query.py:39-43  (_load_program)
  [d0f06494257d1187]   STRU  post_window_detect  L=5 N=2 saved=5 sim=1.00
      packages/rest2vql/src/rest2vql/window_routes.py:28-32  (post_window_detect)
      packages/rest2vql/src/rest2vql/window_routes.py:36-40  (post_window_compare)
  [5a0ff58926871c07]   EXAC  dispose  L=3 N=2 saved=3 sim=1.00
      src/vql/drawing/renderers/base.py:82-84  (dispose)
      src/vql/drawing/renderers/playwright.py:213-215  (dispose)
  [ee7230ffe84d4777]   STRU  _role_name  L=3 N=2 saved=3 sim=1.00
      packages/img2vql/src/img2vql/describe_ui.py:57-59  (_role_name)
      packages/img2vql/src/img2vql/describe_ui.py:62-64  (_loc_name)

REFACTOR[10] (ranked by priority):
  [1] ○ extract_function   → src/vql/adopt/utils/_capture_with_grim.py
      WHY: 2 occurrences of 15-line block across 1 files — saves 15 lines
      FILES: src/vql/adopt/window.py
  [2] ○ extract_function   → packages/rest2vql/src/rest2vql/utils/post_window_diagnose.py
      WHY: 2 occurrences of 13-line block across 1 files — saves 13 lines
      FILES: packages/rest2vql/src/rest2vql/window_routes.py
  [3] ○ extract_function   → packages/img2vql/src/img2vql/utils/_json_safe.py
      WHY: 2 occurrences of 11-line block across 2 files — saves 11 lines
      FILES: packages/img2vql/src/img2vql/fingerprint.py, packages/img2vql/src/img2vql/metadata.py
  [4] ○ extract_function   → packages/uri2vql/src/uri2vql/utils/uri_for_window_diagnose.py
      WHY: 2 occurrences of 10-line block across 1 files — saves 10 lines
      FILES: packages/uri2vql/src/uri2vql/uri.py
  [5] ○ extract_function   → src/vql/adopt/utils/runner.py
      WHY: 2 occurrences of 9-line block across 1 files — saves 9 lines
      FILES: src/vql/adopt/window.py
  [6] ○ extract_function   → packages/utils/_normalize_locale.py
      WHY: 2 occurrences of 8-line block across 2 files — saves 8 lines
      FILES: packages/img2vql/src/img2vql/diagnose.py, packages/uri2vql/src/uri2vql/window.py
  [7] ○ extract_function   → packages/utils/_load_program.py
      WHY: 2 occurrences of 5-line block across 2 files — saves 5 lines
      FILES: packages/dsl2vql/src/dsl2vql/handlers/query.py, packages/uri2vql/src/uri2vql/query.py
  [8] ○ extract_function   → packages/rest2vql/src/rest2vql/utils/post_window_detect.py
      WHY: 2 occurrences of 5-line block across 1 files — saves 5 lines
      FILES: packages/rest2vql/src/rest2vql/window_routes.py
  [9] ○ extract_function   → src/vql/drawing/renderers/utils/dispose.py
      WHY: 2 occurrences of 3-line block across 2 files — saves 3 lines
      FILES: src/vql/drawing/renderers/base.py, src/vql/drawing/renderers/playwright.py
  [10] ○ extract_function   → packages/img2vql/src/img2vql/utils/_role_name.py
      WHY: 2 occurrences of 3-line block across 1 files — saves 3 lines
      FILES: packages/img2vql/src/img2vql/describe_ui.py

QUICK_WINS[6] (low risk, high savings — do first):
  [1] extract_function   saved=15L  → src/vql/adopt/utils/_capture_with_grim.py
      FILES: window.py
  [2] extract_function   saved=13L  → packages/rest2vql/src/rest2vql/utils/post_window_diagnose.py
      FILES: window_routes.py
  [3] extract_function   saved=11L  → packages/img2vql/src/img2vql/utils/_json_safe.py
      FILES: fingerprint.py, metadata.py
  [4] extract_function   saved=10L  → packages/uri2vql/src/uri2vql/utils/uri_for_window_diagnose.py
      FILES: uri.py
  [5] extract_function   saved=9L  → src/vql/adopt/utils/runner.py
      FILES: window.py
  [6] extract_function   saved=8L  → packages/utils/_normalize_locale.py
      FILES: diagnose.py, window.py

EFFORT_ESTIMATE (total ≈ 2.7h):
  medium _capture_with_grim                  saved=15L  ~30min
  easy   post_window_diagnose                saved=13L  ~26min
  easy   _json_safe                          saved=11L  ~22min
  easy   uri_for_window_diagnose             saved=10L  ~20min
  easy   runner                              saved=9L  ~18min
  easy   _normalize_locale                   saved=8L  ~16min
  easy   _load_program                       saved=5L  ~10min
  easy   post_window_detect                  saved=5L  ~10min
  easy   dispose                             saved=3L  ~6min
  easy   _role_name                          saved=3L  ~6min

METRICS-TARGET:
  dup_groups:  10 → 0
  saved_lines: 82 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 390 func | 100f | 2026-06-09
# generated in 0.00s

NEXT[10] (ranked by impact):
  [1] !! SPLIT-FUNC      query_window  CC=69  fan=34
      WHY: CC=69 exceeds 15
      EFFORT: ~1h  IMPACT: 2346

  [2] !! SPLIT-FUNC      main  CC=53  fan=44
      WHY: CC=53 exceeds 15
      EFFORT: ~1h  IMPACT: 2332

  [3] !! SPLIT-FUNC      resolve_prompt_to_vql_uri  CC=54  fan=24
      WHY: CC=54 exceeds 15
      EFFORT: ~1h  IMPACT: 1296

  [4] !! SPLIT-FUNC      capture_diagnose  CC=33  fan=29
      WHY: CC=33 exceeds 15
      EFFORT: ~1h  IMPACT: 957

  [5] !! SPLIT-FUNC      _detect_buttons  CC=25  fan=25
      WHY: CC=25 exceeds 15
      EFFORT: ~1h  IMPACT: 625

  [6] !! SPLIT-FUNC      parse_svg_path  CC=43  fan=12
      WHY: CC=43 exceeds 15
      EFFORT: ~1h  IMPACT: 516

  [7] !  SPLIT-FUNC      _query_window_imgl  CC=17  fan=22
      WHY: CC=17 exceeds 15
      EFFORT: ~1h  IMPACT: 374

  [8] !  SPLIT-FUNC      trace_to_vql_program  CC=15  fan=22
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 330

  [9] !  SPLIT-FUNC      query_uri  CC=15  fan=17
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 255

  [10] !  SPLIT-FUNC      _capture_with_portal  CC=15  fan=15
      WHY: CC=15 exceeds 15
      EFFORT: ~1h  IMPACT: 225


RISKS[3]:
  ⚠ Splitting layout.vql.json may break 0 import paths
  ⚠ Splitting layout.vql.imgl.json may break 0 import paths
  ⚠ Splitting app.vql.json may break 0 import paths

METRICS-TARGET:
  CC̄:          4.2 → ≤2.9
  max-CC:      69 → ≤20
  god-modules: 6 → 0
  high-CC(≥15): 15 → ≤7
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=4.2 → now CC̄=4.2
```

## Intent

VQL — Visual Query Language for vector description of photographs and drawings
