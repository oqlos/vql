# vql

VQL — Visual Query Language for vector description of photographs and drawings

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Workflows](#workflows)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Makefile Targets](#makefile-targets)
- [Code Analysis](#code-analysis)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `vql`
- **version**: `0.1.3`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Makefile, testql(2), app.doql.less, goal.yaml, .env.example, project/(3 analysis files)

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

## Interfaces

### testql Scenarios

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -m vql
  timeout_ms, 10000

# Test 1: CLI help command
SHELL "python -m vql --help" 5000
ASSERT_EXIT_CODE 0
ASSERT_STDOUT_CONTAINS "usage"

# Test 2: CLI version command
SHELL "python -m vql --version" 5000
ASSERT_EXIT_CODE 0

# Test 3: CLI main workflow (dry-run)
SHELL "python -m vql --help" 10000
ASSERT_EXIT_CODE 0
```

#### `testql-scenarios/generated-from-pytests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-from-pytests.testql.toon.yaml
# SCENARIO: Auto-generated from Python Tests
# TYPE: integration
# GENERATED: true

CONFIG[2]{key, value}:
  base_url, ${api_url:-http://localhost:8101}
  timeout_ms, 10000

# Converted 2 assertions from pytest
ASSERT[2]{field, operator, expected}:
  out.ocr.source, ==, "rapidocr"
  out.ocr.source, ==, "rapidocr"
```

## Workflows

## Configuration

```yaml
project:
  name: vql
  version: 0.1.3
  env: local
```

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

## Deployment

```bash markpact:run
pip install vql

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `*(not set)*` | Required: OpenRouter API key (https://openrouter.ai/keys) |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | Model (default: openrouter/qwen/qwen3-coder-next) |
| `PFIX_AUTO_APPLY` | `true` | true = apply fixes without asking |
| `PFIX_AUTO_INSTALL_DEPS` | `true` | true = auto pip/uv install |
| `PFIX_AUTO_RESTART` | `false` | true = os.execv restart after fix |
| `PFIX_MAX_RETRIES` | `3` |  |
| `PFIX_DRY_RUN` | `false` |  |
| `PFIX_ENABLED` | `true` |  |
| `PFIX_GIT_COMMIT` | `false` | true = auto-commit fixes |
| `PFIX_GIT_PREFIX` | `pfix:` | commit message prefix |
| `PFIX_CREATE_BACKUPS` | `false` | false = disable .pfix_backups/ directory |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`vql`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `.venv/lib/python3.12/site-packages/cryptography/__init__.py:__version__`

## Makefile Targets

- `PACKAGES`
- `PYTEST`
- `help`
- `venv`
- `install`
- `install-dev`
- `proto`
- `test`
- `test-cov`
- `test-all`
- `test-roundtrip`
- `validate-schema`
- `compile`
- `serve`
- `clean`
- `build`
- `publish`
- `publish-confirm`
- `version`
- `goal`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# vql | 156f 13502L | python:147,shell:8,less:1 | 2026-06-09
# stats: 315 func | 97 cls | 156 mod | CC̄=5.2 | critical:35 | cycles:0
# alerts[5]: CC query_window=69; CC resolve_prompt_to_vql_uri=54; CC main=53; CC capture_diagnose=33; CC envelope_to_dict=31
# hotspots[5]: main fan=29; query_window fan=29; screenshot_to_program fan=28; create_app fan=25; capture_diagnose fan=25
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[156]:
  app.doql.less,148
  examples/full-pipeline.sh,81
  examples/generate-demo-screen.py,77
  examples/img2nl-vql-flow.sh,215
  examples/live-capture-test.sh,95
  examples/photo-roundtrip-test.py,407
  examples/scope-window.py,54
  install-dev.sh,38
  packages/cli2vql/src/cli2vql/__init__.py,2
  packages/cli2vql/src/cli2vql/cli.py,69
  packages/dsl2img2svg/src/dsl2img2svg/__init__.py,6
  packages/dsl2img2svg/src/dsl2img2svg/cli.py,22
  packages/dsl2img2svg/src/dsl2img2svg/dispatch.py,116
  packages/dsl2img2svg/tests/test_dispatch.py,32
  packages/dsl2vql/scripts/generate-proto.sh,8
  packages/dsl2vql/src/dsl2vql/__init__.py,7
  packages/dsl2vql/src/dsl2vql/bus.py,78
  packages/dsl2vql/src/dsl2vql/cli.py,98
  packages/dsl2vql/src/dsl2vql/codec.py,36
  packages/dsl2vql/src/dsl2vql/engine.py,9
  packages/dsl2vql/src/dsl2vql/events.py,109
  packages/dsl2vql/src/dsl2vql/grammar.py,97
  packages/dsl2vql/src/dsl2vql/handlers/__init__.py,6
  packages/dsl2vql/src/dsl2vql/handlers/command.py,131
  packages/dsl2vql/src/dsl2vql/handlers/query.py,110
  packages/dsl2vql/src/dsl2vql/pb_codec.py,158
  packages/dsl2vql/src/dsl2vql/result.py,29
  packages/dsl2vql/src/dsl2vql/schema_registry.py,47
  packages/dsl2vql/src/dsl2vql/v1/__init__.py,6
  packages/dsl2vql/src/dsl2vql/v1/command_pb2.py,53
  packages/dsl2vql/src/dsl2vql/v1/result_pb2.py,40
  packages/dsl2vql/tests/test_parity.py,29
  packages/img2svg/src/img2svg/__init__.py,14
  packages/img2svg/src/img2svg/cli.py,72
  packages/img2svg/src/img2svg/svg_emit.py,135
  packages/img2svg/src/img2svg/to_vql.py,142
  packages/img2svg/src/img2svg/trace.py,264
  packages/img2svg/tests/test_img2svg.py,101
  packages/img2vql/src/img2vql/__init__.py,27
  packages/img2vql/src/img2vql/adopt.py,64
  packages/img2vql/src/img2vql/cli.py,88
  packages/img2vql/src/img2vql/describe_ui.py,122
  packages/img2vql/src/img2vql/detect.py,380
  packages/img2vql/src/img2vql/diagnose.py,126
  packages/img2vql/src/img2vql/fingerprint.py,105
  packages/img2vql/src/img2vql/metadata.py,340
  packages/img2vql/src/img2vql/program.py,142
  packages/img2vql/tests/test_auto_ocr.py,45
  packages/img2vql/tests/test_detect.py,75
  packages/img2vql/tests/test_diagnose.py,31
  packages/img2vql/tests/test_fingerprint.py,93
  packages/img2vql/tests/test_metadata_imgl.py,49
  packages/mcp2vql/src/mcp2vql/__init__.py,6
  packages/mcp2vql/src/mcp2vql/cli.py,9
  packages/mcp2vql/src/mcp2vql/server.py,136
  packages/nlp2vql/src/nlp2vql/__init__.py,7
  packages/nlp2vql/src/nlp2vql/apply.py,49
  packages/nlp2vql/src/nlp2vql/cli.py,54
  packages/nlp2vql/src/nlp2vql/to_dsl.py,43
  packages/rest2vql/src/rest2vql/__init__.py,6
  packages/rest2vql/src/rest2vql/app.py,73
  packages/rest2vql/src/rest2vql/cli.py,25
  packages/rest2vql/src/rest2vql/window.py,125
  packages/rest2vql/src/rest2vql/window_routes.py,111
  packages/rest2vql/tests/test_window_api.py,121
  packages/uri2img2svg/src/uri2img2svg/__init__.py,7
  packages/uri2img2svg/src/uri2img2svg/cli.py,29
  packages/uri2img2svg/src/uri2img2svg/query.py,145
  packages/uri2img2svg/src/uri2img2svg/uri.py,60
  packages/uri2img2svg/tests/test_uri2img2svg.py,42
  packages/uri2vql/src/uri2vql/__init__.py,46
  packages/uri2vql/src/uri2vql/cli.py,353
  packages/uri2vql/src/uri2vql/compile.py,37
  packages/uri2vql/src/uri2vql/nlp2uri.py,330
  packages/uri2vql/src/uri2vql/patch.py,41
  packages/uri2vql/src/uri2vql/query.py,96
  packages/uri2vql/src/uri2vql/run.py,65
  packages/uri2vql/src/uri2vql/uri.py,184
  packages/uri2vql/src/uri2vql/window.py,654
  packages/uri2vql/tests/test_nlp2uri_window.py,31
  packages/uri2vql/tests/test_window_refresh.py,79
  project.sh,59
  scripts/test-goal.sh,7
  src/vql/__init__.py,57
  src/vql/adopt/__init__.py,20
  src/vql/adopt/portal_capture.py,110
  src/vql/adopt/window.py,805
  src/vql/api.py,56
  src/vql/compiler/__init__.py,16
  src/vql/compiler/legacy_drawcommand.py,143
  src/vql/compiler/nl_to_vql.py,70
  src/vql/drawing/__init__.py,17
  src/vql/drawing/arrow_generator.py,47
  src/vql/drawing/bird_generator.py,50
  src/vql/drawing/boat_generator.py,41
  src/vql/drawing/butterfly_generator.py,51
  src/vql/drawing/car_generator.py,49
  src/vql/drawing/castle_generator.py,64
  src/vql/drawing/cat_generator.py,56
  src/vql/drawing/circle_generator.py,30
  src/vql/drawing/cloud_detailed_generator.py,48
  src/vql/drawing/colors.py,136
  src/vql/drawing/commands.py,272
  src/vql/drawing/crescent_generator.py,37
  src/vql/drawing/cross_generator.py,34
  src/vql/drawing/diamond_generator.py,37
  src/vql/drawing/dot_generator.py,30
  src/vql/drawing/ellipse_generator.py,31
  src/vql/drawing/event_store.py,102
  src/vql/drawing/events.py,143
  src/vql/drawing/fish_generator.py,47
  src/vql/drawing/flower_generator.py,36
  src/vql/drawing/grid_generator.py,37
  src/vql/drawing/heart_generator.py,31
  src/vql/drawing/hexagon_generator.py,28
  src/vql/drawing/house_generator.py,31
  src/vql/drawing/line_generator.py,26
  src/vql/drawing/mountain_generator.py,40
  src/vql/drawing/nl_parser.py,226
  src/vql/drawing/octagon_generator.py,28
  src/vql/drawing/path_generator.py,26
  src/vql/drawing/pentagon_generator.py,28
  src/vql/drawing/rectangle_generator.py,27
  src/vql/drawing/renderers/__init__.py,10
  src/vql/drawing/renderers/base.py,85
  src/vql/drawing/renderers/playwright.py,216
  src/vql/drawing/renderers/svg.py,94
  src/vql/drawing/rocket_generator.py,53
  src/vql/drawing/shape_generator.py,38
  src/vql/drawing/shape_registry.py,104
  src/vql/drawing/shapes.py,79
  src/vql/drawing/spiral_generator.py,33
  src/vql/drawing/square_generator.py,26
  src/vql/drawing/star_generator.py,34
  src/vql/drawing/sun_generator.py,37
  src/vql/drawing/svg_path_parser.py,206
  src/vql/drawing/tree_generator.py,34
  src/vql/drawing/triangle_generator.py,27
  src/vql/drawing/wave_generator.py,35
  src/vql/facade.py,96
  src/vql/library/__init__.py,15
  src/vql/renderers/__init__.py,24
  src/vql/renderers/base.py,66
  src/vql/renderers/playwright.py,23
  src/vql/renderers/svg.py,52
  src/vql/schema/__init__.py,34
  src/vql/schema/program.py,424
  src/vql/validation/__init__.py,14
  src/vql/validation/metadata.py,58
  src/vql/validation/spec.py,92
  tests/test_adopt_window_capture.py,37
  tests/test_metadata_validation.py,41
  tests/test_photo_roundtrip.py,116
  tests/test_screenshot_merge.py,31
  tests/test_vql.py,245
  tree.sh,2
D:
  examples/generate-demo-screen.py:
    e: _load_font,write_demo_screen,main
    _load_font(size)
    write_demo_screen(path)
    main()
  examples/photo-roundtrip-test.py:
    e: _require_pil,sample_flat_shapes,sample_gradient,sample_product_photo,sample_natural_scene,sample_nl_drawing,test_img2svg_roundtrip,test_ui_grid_adopt,test_vtracer_roundtrip,test_opencv_contours,test_metadata_only_reconstruction,test_img2vql_detect,main
    _require_pil()
    sample_flat_shapes(out)
    sample_gradient(out)
    sample_product_photo(out)
    sample_natural_scene(out)
    sample_nl_drawing(out)
    test_img2svg_roundtrip(image;out)
    test_ui_grid_adopt(out)
    test_vtracer_roundtrip(image;out)
    test_opencv_contours(image;out)
    test_metadata_only_reconstruction(out)
    test_img2vql_detect(out)
    main()
  examples/scope-window.py:
    e: main
    main()
  packages/cli2vql/src/cli2vql/__init__.py:
  packages/cli2vql/src/cli2vql/cli.py:
    e: _repl,main
    _repl(default_file)
    main(argv)
  packages/dsl2img2svg/src/dsl2img2svg/__init__.py:
  packages/dsl2img2svg/src/dsl2img2svg/cli.py:
    e: main
    main(argv)
  packages/dsl2img2svg/src/dsl2img2svg/dispatch.py:
    e: _parse_kv_args,dispatch,DispatchResult
    DispatchResult: to_dict(0)
    _parse_kv_args(tokens)
    dispatch(line)
  packages/dsl2img2svg/tests/test_dispatch.py:
    e: test_vectorize,test_query_uri
    test_vectorize(tmp_path)
    test_query_uri(tmp_path)
  packages/dsl2vql/src/dsl2vql/__init__.py:
  packages/dsl2vql/src/dsl2vql/bus.py:
    e: _dispatch_cmd,_bytes_to_cmd,dispatch,execute_dsl_line,execute_dsl
    _dispatch_cmd(cmd)
    _bytes_to_cmd(data)
    dispatch(envelope)
    execute_dsl_line(line)
    execute_dsl(text)
  packages/dsl2vql/src/dsl2vql/cli.py:
    e: _main_legacy,_main_subcommand,main
    _main_legacy(argv)
    _main_subcommand(argv)
    main(argv)
  packages/dsl2vql/src/dsl2vql/codec.py:
    e: encode_text,roundtrip_text,encode_protobuf,decode_protobuf
    encode_text(line)
    roundtrip_text(line)
    encode_protobuf(line)
    decode_protobuf(data)
  packages/dsl2vql/src/dsl2vql/engine.py:
  packages/dsl2vql/src/dsl2vql/events.py:
    e: default_event_store,DslEvent,EventStore
    DslEvent: to_dict(0)
    EventStore: __init__(1),append(2),replay(0)
    default_event_store(default_file)
  packages/dsl2vql/src/dsl2vql/grammar.py:
    e: split_command,pick_flag,parse_line,to_text
    split_command(line)
    pick_flag(tokens;flag)
    parse_line(line)
    to_text(cmd)
  packages/dsl2vql/src/dsl2vql/handlers/__init__.py:
  packages/dsl2vql/src/dsl2vql/handlers/command.py:
    e: _read_json,handle_generate,handle_compile,handle_patch,handle_export,handle_from_tokens
    _read_json(path)
    handle_generate(cmd)
    handle_compile(cmd)
    handle_patch(cmd)
    handle_export(cmd)
    handle_from_tokens(line;tokens)
  packages/dsl2vql/src/dsl2vql/handlers/query.py:
    e: _load_program,handle_query,handle_validate,handle_render,handle_resolve
    _load_program(path)
    handle_query(cmd)
    handle_validate(cmd)
    handle_render(cmd)
    handle_resolve(cmd)
  packages/dsl2vql/src/dsl2vql/pb_codec.py:
    e: _set_body,envelope_to_dict,encode_protobuf,decode_protobuf,encode_text_to_protobuf,decode_protobuf_to_text,result_to_pb,encode_result_protobuf
    _set_body(envelope;cmd)
    envelope_to_dict(envelope)
    encode_protobuf(cmd)
    decode_protobuf(data)
    encode_text_to_protobuf(line)
    decode_protobuf_to_text(data)
    result_to_pb(result)
    encode_result_protobuf(result)
  packages/dsl2vql/src/dsl2vql/result.py:
    e: DslResult
    DslResult: to_dict(0)
  packages/dsl2vql/src/dsl2vql/schema_registry.py:
    e: _load_schemas,schema_for_verb,all_schemas,validate_command_dict,validate_schema_registry
    _load_schemas()
    schema_for_verb(verb)
    all_schemas()
    validate_command_dict(cmd)
    validate_schema_registry()
  packages/dsl2vql/src/dsl2vql/v1/__init__.py:
  packages/dsl2vql/src/dsl2vql/v1/command_pb2.py:
  packages/dsl2vql/src/dsl2vql/v1/result_pb2.py:
  packages/dsl2vql/tests/test_parity.py:
    e: test_parity_text_vs_dict,test_validate_schema_registry,test_encode_decode_roundtrip
    test_parity_text_vs_dict()
    test_validate_schema_registry()
    test_encode_decode_roundtrip()
  packages/img2svg/src/img2svg/__init__.py:
  packages/img2svg/src/img2svg/cli.py:
    e: main
    main(argv)
  packages/img2svg/src/img2svg/svg_emit.py:
    e: regions_to_svg,_vtracer_paths_to_svg,paths_to_svg,image_to_svg
    regions_to_svg(trace)
    _vtracer_paths_to_svg(trace)
    paths_to_svg(trace)
    image_to_svg(image_path)
  packages/img2svg/src/img2svg/to_vql.py:
    e: _background_from_regions,trace_to_vql_program,image_to_vql
    _background_from_regions(regions)
    trace_to_vql_program(trace)
    image_to_vql(image_path)
  packages/img2svg/src/img2svg/trace.py:
    e: _hex_color,_merge_grid_cells,trace_image_regions,trace_contours_opencv,_parse_translate,_parse_vtracer_svg,trace_vtracer,TracedRegion
    TracedRegion: to_dict(0)  # A merged rectangular region from the image.
    _hex_color(rgb)
    _merge_grid_cells(colors)
    trace_image_regions(image_path)
    trace_contours_opencv(image_path)
    _parse_translate(transform)
    _parse_vtracer_svg(svg_path)
    trace_vtracer(image_path)
  packages/img2svg/tests/test_img2svg.py:
    e: test_trace_regions,test_image_to_svg,test_image_to_vql,test_trace_vtracer,test_image_to_vql_vtracer,test_image_to_vql_sets_background
    test_trace_regions(tmp_path)
    test_image_to_svg(tmp_path)
    test_image_to_vql(tmp_path)
    test_trace_vtracer(tmp_path)
    test_image_to_vql_vtracer(tmp_path)
    test_image_to_vql_sets_background(tmp_path)
  packages/img2vql/src/img2vql/__init__.py:
  packages/img2vql/src/img2vql/adopt.py:
    e: adopt_screenshot
    adopt_screenshot(image_path)
  packages/img2vql/src/img2vql/cli.py:
    e: main
    main(argv)
  packages/img2vql/src/img2vql/describe_ui.py:
    e: _role_name,_loc_name,describe_ui_layout
    _role_name(role;locale)
    _loc_name(loc;locale)
    describe_ui_layout(detection)
  packages/img2vql/src/img2vql/detect.py:
    e: _hex_color,_location_label,_avg_color,_detect_titlebar,_detect_panels,_flood_rects,_detect_buttons,_detect_toolbar,_iou,_dedupe,detect_ui_elements,UIElement
    UIElement: width(0),height(0),center(0),bbox_norm(0),to_dict(0)  # Detected UI region with role and location.
    _hex_color(rgb)
    _location_label(cx;cy;w;h)
    _avg_color(im;x0;y0;x1;y1)
    _detect_titlebar(im;w;h)
    _detect_panels(im;w;h)
    _flood_rects(mask)
    _detect_buttons(im;w;h)
    _detect_toolbar(buttons;w;h)
    _iou(a;b)
    _dedupe(elements)
    detect_ui_elements(image_path)
  packages/img2vql/src/img2vql/diagnose.py:
    e: _normalize_locale,diagnose_image,diagnose_for_vql,_recommendation
    _normalize_locale(locale)
    diagnose_image(image_path)
    diagnose_for_vql(image_path)
    _recommendation(diag)
  packages/img2vql/src/img2vql/fingerprint.py:
    e: fingerprint_for_image,load_program_fingerprint,_json_safe,compare_with_program
    fingerprint_for_image(image_path)
    load_program_fingerprint(vql_program)
    _json_safe(value)
    compare_with_program(image_path;vql_program)
  packages/img2vql/src/img2vql/metadata.py:
    e: _json_safe,_compact_special_hits,_text_likely,rapidocr_special_hits,auto_ocr_special_hits,imgl_ocr_special_hits,_merge_special_hits,img2nl_metadata_slice,merge_program_metadata,refresh_program_metadata,metadata_from_diagnose,save_diagnose_to_program
    _json_safe(value)
    _compact_special_hits(special)
    _text_likely(features;special)
    rapidocr_special_hits(image_path)
    auto_ocr_special_hits(image_path;features)
    imgl_ocr_special_hits(image_path)
    _merge_special_hits(img2nl_special;imgl_special)
    img2nl_metadata_slice(image_path)
    merge_program_metadata(metadata;image_path)
    refresh_program_metadata(vql_program;image_path)
    metadata_from_diagnose(diag)
    save_diagnose_to_program(vql_program;diag)
  packages/img2vql/src/img2vql/program.py:
    e: _role_style,elements_to_vql_program,_bbox_contains,_build_contains_relations
    _role_style(role)
    elements_to_vql_program(detection)
    _bbox_contains(outer;inner)
    _build_contains_relations(objects)
  packages/img2vql/tests/test_auto_ocr.py:
    e: test_text_likely_when_edges_suggest_text,test_text_likely_false_when_has_text,test_auto_ocr_uses_rapidocr_when_available
    test_text_likely_when_edges_suggest_text()
    test_text_likely_false_when_has_text()
    test_auto_ocr_uses_rapidocr_when_available(tmp_path)
  packages/img2vql/tests/test_detect.py:
    e: _make_ui_fixture,test_detect_finds_titlebar_and_buttons,test_describe_ui_polish,test_adopt_writes_contains_relations,test_adopt_writes_vql_program
    _make_ui_fixture(path)
    test_detect_finds_titlebar_and_buttons(tmp_path)
    test_describe_ui_polish(tmp_path)
    test_adopt_writes_contains_relations(tmp_path)
    test_adopt_writes_vql_program(tmp_path)
  packages/img2vql/tests/test_diagnose.py:
    e: test_diagnose_blank_vs_rich
    test_diagnose_blank_vs_rich(tmp_path)
  packages/img2vql/tests/test_fingerprint.py:
    e: _solid,test_screenshot_to_program_stores_fingerprint,test_diagnose_uses_program_fingerprint,test_analyze_skips_adopt_when_unchanged,test_screenshot_stores_special_hits_metadata,test_compare_with_program
    _solid(path;color;size)
    test_screenshot_to_program_stores_fingerprint(tmp_path)
    test_diagnose_uses_program_fingerprint(tmp_path)
    test_analyze_skips_adopt_when_unchanged(tmp_path)
    test_screenshot_stores_special_hits_metadata(tmp_path)
    test_compare_with_program(tmp_path)
  packages/img2vql/tests/test_metadata_imgl.py:
    e: _text_image,test_imgl_ocr_special_hits_finds_text,test_merge_program_metadata_uses_imgl_when_img2nl_misses,test_refresh_program_metadata_persists_imgl_ocr
    _text_image(path;text)
    test_imgl_ocr_special_hits_finds_text(tmp_path)
    test_merge_program_metadata_uses_imgl_when_img2nl_misses(tmp_path)
    test_refresh_program_metadata_persists_imgl_ocr(tmp_path)
  packages/mcp2vql/src/mcp2vql/__init__.py:
  packages/mcp2vql/src/mcp2vql/cli.py:
  packages/mcp2vql/src/mcp2vql/server.py:
    e: _require_fastmcp,main,VqlMCPServer
    VqlMCPServer: __post_init__(0),_register_tools(0),run(0)
    _require_fastmcp()
    main()
  packages/nlp2vql/src/nlp2vql/__init__.py:
  packages/nlp2vql/src/nlp2vql/apply.py:
    e: apply_nl,ApplyResult
    ApplyResult: to_dict(0)
    apply_nl(prompt)
  packages/nlp2vql/src/nlp2vql/cli.py:
    e: main
    main(argv)
  packages/nlp2vql/src/nlp2vql/to_dsl.py:
    e: _intent,nl_to_dsl_line,to_dsl
    _intent(prompt)
    nl_to_dsl_line(prompt)
    to_dsl(prompt)
  packages/rest2vql/src/rest2vql/__init__.py:
  packages/rest2vql/src/rest2vql/app.py:
    e: create_app
    create_app()
  packages/rest2vql/src/rest2vql/cli.py:
    e: main
    main(argv)
  packages/rest2vql/src/rest2vql/window.py:
    e: window_detect,window_compare,window_refresh,window_diagnose,window_analyze,window_adopt,window_summary,WindowImageBody
    WindowImageBody:
    window_detect(image)
    window_compare(image)
    window_refresh(image)
    window_diagnose(image)
    window_analyze(image)
    window_adopt(image)
    window_summary()
  packages/rest2vql/src/rest2vql/window_routes.py:
    e: _window_response,post_window_detect,post_window_compare,post_window_refresh,post_window_diagnose,post_window_analyze,post_window_adopt,post_window_summary
    _window_response(payload)
    post_window_detect(req)
    post_window_compare(req)
    post_window_refresh(req)
    post_window_diagnose(req)
    post_window_analyze(req)
    post_window_adopt(req)
    post_window_summary(req)
  packages/rest2vql/tests/test_window_api.py:
    e: client,_solid_image,_program_with_fingerprint,test_health,test_window_detect_missing_dep,test_window_compare,test_window_refresh,test_window_diagnose
    client()
    _solid_image(path;color)
    _program_with_fingerprint(path;fingerprint)
    test_health(client)
    test_window_detect_missing_dep(client;tmp_path)
    test_window_compare(client;tmp_path)
    test_window_refresh(client;tmp_path)
    test_window_diagnose(client;tmp_path)
  packages/uri2img2svg/src/uri2img2svg/__init__.py:
  packages/uri2img2svg/src/uri2img2svg/cli.py:
    e: main
    main(argv)
  packages/uri2img2svg/src/uri2img2svg/query.py:
    e: query_uri,QueryResult
    QueryResult: to_dict(0)
    query_uri(uri)
  packages/uri2img2svg/src/uri2img2svg/uri.py:
    e: is_img2svg_uri,uri_for_vectorize,parse_img2svg_uri,Img2SvgUri
    Img2SvgUri: target(0)
    is_img2svg_uri(uri)
    uri_for_vectorize(path)
    parse_img2svg_uri(uri)
  packages/uri2img2svg/tests/test_uri2img2svg.py:
    e: test_parse_uri,test_vectorize,test_svg_uri
    test_parse_uri()
    test_vectorize(tmp_path)
    test_svg_uri(tmp_path)
  packages/uri2vql/src/uri2vql/__init__.py:
  packages/uri2vql/src/uri2vql/cli.py:
    e: main
    main(argv)
  packages/uri2vql/src/uri2vql/compile.py:
    e: _dsl_from_uri,compile_vql_uri
    _dsl_from_uri(uri)
    compile_vql_uri(uri;host)
  packages/uri2vql/src/uri2vql/nlp2uri.py:
    e: resolve_prompt_to_vql_uri,_extract_click_target,_extract_type_parts,nlp2uri,best_uri,ResolvedVqlUri
    ResolvedVqlUri: to_dict(0)
    resolve_prompt_to_vql_uri(prompt)
    _extract_click_target(normalized)
    _extract_type_parts(normalized)
    nlp2uri(prompt)
    best_uri(prompt)
  packages/uri2vql/src/uri2vql/patch.py:
    e: patch_uri,PatchResult
    PatchResult: to_dict(0)
    patch_uri(uri)
  packages/uri2vql/src/uri2vql/query.py:
    e: _load_program,query_uri,QueryResult
    QueryResult: to_dict(0)
    _load_program(path)
    query_uri(uri)
  packages/uri2vql/src/uri2vql/run.py:
    e: run_uri,run_uri_json,RunResult
    RunResult: to_dict(0)
    run_uri(uri)
    run_uri_json(uri)
  packages/uri2vql/src/uri2vql/uri.py:
    e: is_vql_uri,_with_file,uri_for_program,uri_for_scene,uri_for_objects,uri_for_object,uri_for_window_analyze,uri_for_window_summary,uri_for_window_imgl,uri_for_imgl_list,uri_for_imgl_click,uri_for_imgl_type,uri_for_window_diagnose,uri_for_window_compare,uri_for_window_refresh,parse_vql_uri,VqlUri
    VqlUri: target(0)
    is_vql_uri(uri)
    _with_file(selector)
    uri_for_program(file)
    uri_for_scene(file)
    uri_for_objects(file)
    uri_for_object(obj_id)
    uri_for_window_analyze()
    uri_for_window_summary(file)
    uri_for_window_imgl()
    uri_for_imgl_list()
    uri_for_imgl_click()
    uri_for_imgl_type()
    uri_for_window_diagnose()
    uri_for_window_compare()
    uri_for_window_refresh()
    parse_vql_uri(uri)
  packages/uri2vql/src/uri2vql/window.py:
    e: _resolve_image_param,_normalize_locale,_diagnose_fallback,_resolve_window_image,refresh_window_metadata,compare_window_image,diagnose_window_image,_query_window_imgl,analyze_window_uri,query_window,WindowAnalyzeResult
    WindowAnalyzeResult: to_dict(0)
    _resolve_image_param(image)
    _normalize_locale(locale)
    _diagnose_fallback(image)
    _resolve_window_image(out_file;image)
    refresh_window_metadata(image)
    compare_window_image(image)
    diagnose_window_image(image)
    _query_window_imgl()
    analyze_window_uri(uri)
    query_window(uri)
  packages/uri2vql/tests/test_nlp2uri_window.py:
    e: test_nlp_refresh_window,test_nlp_compare_window,test_nlp_diagnose_window,test_nlp_unchanged_suggests_compare
    test_nlp_refresh_window()
    test_nlp_compare_window()
    test_nlp_diagnose_window()
    test_nlp_unchanged_suggests_compare()
  packages/uri2vql/tests/test_window_refresh.py:
    e: _solid,test_diagnose_save_to_program,test_save_diagnose_to_program_helper,test_window_refresh_uri
    _solid(path;color;size)
    test_diagnose_save_to_program(tmp_path)
    test_save_diagnose_to_program_helper(tmp_path)
    test_window_refresh_uri(tmp_path)
  src/vql/__init__.py:
  src/vql/adopt/__init__.py:
  src/vql/adopt/portal_capture.py:
    e: capture_via_portal,main
    capture_via_portal(out)
    main(argv)
  src/vql/adopt/window.py:
    e: _require_pillow,_session_type,_is_wayland,_capture_interactive_mode,_should_use_interactive_portal,_portal_python,image_stats,_image_is_blank,_finalize_capture,_run_capture,_capture_with_gnome_shell,_capture_with_grim,_capture_with_gnome_screenshot,_capture_with_portal,_capture_with_scrot,_capture_with_mss,_capture_backends,capture_diagnose,_capture_permission_hint,_active_window_title,capture_screen,_hex_color,_optional_fingerprint,_enrich_program_metadata,_merge_grid_colors,screenshot_to_program,analyze_screenshot,CaptureError,CaptureInfo,CaptureAttempt
    CaptureError:  # Raised when no capture backend produced a usable image.
    CaptureInfo: to_dict(0)
    CaptureAttempt: to_dict(0)
    _require_pillow()
    _session_type()
    _is_wayland()
    _capture_interactive_mode()
    _should_use_interactive_portal()
    _portal_python()
    image_stats(path)
    _image_is_blank(path)
    _finalize_capture(out)
    _run_capture(out)
    _capture_with_gnome_shell(out)
    _capture_with_grim(out)
    _capture_with_gnome_screenshot(out)
    _capture_with_portal(out)
    _capture_with_scrot(out)
    _capture_with_mss(out)
    _capture_backends()
    capture_diagnose(out)
    _capture_permission_hint()
    _active_window_title()
    capture_screen(out)
    _hex_color(rgb)
    _optional_fingerprint(image_path)
    _enrich_program_metadata(base;path)
    _merge_grid_colors(colors)
    screenshot_to_program(image_path)
    analyze_screenshot(image_path)
  src/vql/api.py:
  src/vql/compiler/__init__.py:
  src/vql/compiler/legacy_drawcommand.py:
    e: program_to_commands,commands_to_program,compile_to_events
    program_to_commands(program)
    commands_to_program(commands)
    compile_to_events(program)
  src/vql/compiler/nl_to_vql.py:
    e: nl_to_program
    nl_to_program(text)
  src/vql/drawing/__init__.py:
  src/vql/drawing/arrow_generator.py:
    e: ArrowGenerator
    ArrowGenerator: generate(3)
  src/vql/drawing/bird_generator.py:
    e: BirdGenerator
    BirdGenerator: generate(3)
  src/vql/drawing/boat_generator.py:
    e: BoatGenerator
    BoatGenerator: generate(3)
  src/vql/drawing/butterfly_generator.py:
    e: ButterflyGenerator
    ButterflyGenerator: generate(3)
  src/vql/drawing/car_generator.py:
    e: CarGenerator
    CarGenerator: generate(3)
  src/vql/drawing/castle_generator.py:
    e: CastleGenerator
    CastleGenerator: generate(3)
  src/vql/drawing/cat_generator.py:
    e: CatGenerator
    CatGenerator: generate(3)
  src/vql/drawing/circle_generator.py:
    e: CircleGenerator
    CircleGenerator: generate(3)
  src/vql/drawing/cloud_detailed_generator.py:
    e: CloudDetailedGenerator
    CloudDetailedGenerator: generate(3)
  src/vql/drawing/colors.py:
    e: ColorResolver
    ColorResolver: __init__(0),register(2),resolve(2),extract_colors(1),available(0),unique_colors(0)  # Resolves color names to hex codes with Polish + English supp
  src/vql/drawing/commands.py:
    e: DrawCommand,InitCanvas,DrawShape,SetColor,SelectTool,ClearCanvas,CommandHandler,CommandBus
    DrawCommand: validate(0)  # Abstract base for all drawing commands.
    InitCanvas: validate(0)  # Initialize a drawing canvas.
    DrawShape: validate(0)  # Draw a shape on the canvas.
    SetColor: validate(0)  # Change the active drawing color.
    SelectTool: validate(0)  # Select a drawing tool.
    ClearCanvas: validate(0)  # Clear the entire canvas.
    CommandHandler: __call__(3)  # Protocol for command handlers.
    CommandBus: __init__(1),state(0),register_handler(2),add_pre_hook(1),add_post_hook(1),dispatch(1),rebuild_state(0),_apply_event(1),_handle_init_canvas(1),_handle_draw_shape(1),_handle_set_color(1),_handle_select_tool(1),_handle_clear_canvas(1)  # Dispatches commands to handlers, validates, and emits events
  src/vql/drawing/crescent_generator.py:
    e: CrescentGenerator
    CrescentGenerator: generate(3)
  src/vql/drawing/cross_generator.py:
    e: CrossGenerator
    CrossGenerator: generate(3)
  src/vql/drawing/diamond_generator.py:
    e: DiamondGenerator
    DiamondGenerator: generate(3)
  src/vql/drawing/dot_generator.py:
    e: DotGenerator
    DotGenerator: generate(3)
  src/vql/drawing/ellipse_generator.py:
    e: EllipseGenerator
    EllipseGenerator: generate(3)
  src/vql/drawing/event_store.py:
    e: EventStore
    EventStore: __init__(0),events(0),count(0),append(1),subscribe(1),unsubscribe(1),replay(1),events_since(1),events_of_type(1),clear(0),to_dict(0),save(1),load(2),__len__(0),__repr__(0)  # Append-only event store with optional persistence and subscr
  src/vql/drawing/events.py:
    e: EventType,DrawingEvent,CanvasInitialized,CanvasCleared,ShapeDrawn,ColorChanged,ToolSelected
    EventType:
    DrawingEvent: to_dict(0),from_dict(2)  # Base immutable event — all drawing events inherit from this.
    CanvasInitialized: __post_init__(0)  # Fired when a canvas is created or discovered.
    CanvasCleared: __post_init__(0)  # Fired when the canvas is cleared.
    ShapeDrawn: __post_init__(0)  # Fired when a shape is drawn on the canvas.
    ColorChanged: __post_init__(0)  # Fired when the active drawing color is changed.
    ToolSelected: __post_init__(0)  # Fired when a drawing tool is selected.
  src/vql/drawing/fish_generator.py:
    e: FishGenerator
    FishGenerator: generate(3)
  src/vql/drawing/flower_generator.py:
    e: FlowerGenerator
    FlowerGenerator: generate(3)
  src/vql/drawing/grid_generator.py:
    e: GridGenerator
    GridGenerator: generate(3)
  src/vql/drawing/heart_generator.py:
    e: HeartGenerator
    HeartGenerator: generate(3)
  src/vql/drawing/hexagon_generator.py:
    e: HexagonGenerator
    HexagonGenerator: generate(3)
  src/vql/drawing/house_generator.py:
    e: HouseGenerator
    HouseGenerator: generate(3)
  src/vql/drawing/line_generator.py:
    e: LineGenerator
    LineGenerator: generate(3)
  src/vql/drawing/mountain_generator.py:
    e: MountainGenerator
    MountainGenerator: generate(3)
  src/vql/drawing/nl_parser.py:
    e: NLDrawingParser
    NLDrawingParser: __init__(1),parse(3),to_vql(5),detect_shape(1),detect_color(2),_extract_shapes(1),_extract_size_params(1),_extract_shape_specific_params(2)  # Parse natural language drawing instructions into DrawCommand
  src/vql/drawing/octagon_generator.py:
    e: OctagonGenerator
    OctagonGenerator: generate(3)
  src/vql/drawing/path_generator.py:
    e: PathGenerator
    PathGenerator: generate(3)
  src/vql/drawing/pentagon_generator.py:
    e: PentagonGenerator
    PentagonGenerator: generate(3)
  src/vql/drawing/rectangle_generator.py:
    e: RectangleGenerator
    RectangleGenerator: generate(3)
  src/vql/drawing/renderers/__init__.py:
  src/vql/drawing/renderers/base.py:
    e: Renderer
    Renderer: init_canvas(4),set_color(1),draw_path(3),draw_shape(1),clear(0),screenshot(1),render_events(1),dispose(0)  # Abstract renderer interface.
  src/vql/drawing/renderers/playwright.py:
    e: PlaywrightRenderer
    PlaywrightRenderer: __init__(2),init_canvas(4),set_color(1),draw_path(3),draw_shape(1),clear(0),screenshot(1),dispose(0)  # Render drawings on a browser canvas via Playwright mouse con
  src/vql/drawing/renderers/svg.py:
    e: SVGRenderer
    SVGRenderer: __init__(0),init_canvas(4),set_color(1),draw_path(3),draw_shape(1),clear(0),screenshot(1),to_svg(0)  # Render drawings as SVG markup.
  src/vql/drawing/rocket_generator.py:
    e: RocketGenerator
    RocketGenerator: generate(3)
  src/vql/drawing/shape_generator.py:
    e: ShapeGenerator
    ShapeGenerator: generate(3)  # Abstract shape generator — one responsibility: produce point
  src/vql/drawing/shape_registry.py:
    e: ShapeRegistry
    ShapeRegistry: register(2),get(2),available(1),_init_defaults(1)  # Registry of all available shape generators.
  src/vql/drawing/shapes.py:
  src/vql/drawing/spiral_generator.py:
    e: SpiralGenerator
    SpiralGenerator: generate(3)
  src/vql/drawing/square_generator.py:
    e: SquareGenerator
    SquareGenerator: generate(3)
  src/vql/drawing/star_generator.py:
    e: StarGenerator
    StarGenerator: generate(3)
  src/vql/drawing/sun_generator.py:
    e: SunGenerator
    SunGenerator: generate(3)
  src/vql/drawing/svg_path_parser.py:
    e: _dispatch_command,_tokenize_path,_scale_groups,parse_svg_path,_PathState
    _PathState: next_num(0),close_subpath(0),start_subpath(2),line_to(2),append_cubic(6),append_quadratic(4)
    _dispatch_command(state;cmd)
    _tokenize_path(d)
    _scale_groups(groups)
    parse_svg_path(d;scale;center)
  src/vql/drawing/tree_generator.py:
    e: TreeGenerator
    TreeGenerator: generate(3)
  src/vql/drawing/triangle_generator.py:
    e: TriangleGenerator
    TriangleGenerator: generate(3)
  src/vql/drawing/wave_generator.py:
    e: WaveGenerator
    WaveGenerator: generate(3)
  src/vql/facade.py:
    e: VQLResult,VQLFacade
    VQLResult:  # Bundle returned by :meth:`VQLFacade.run`.
    VQLFacade: compile(1),validate(1),render_svg(1),render_png(2),to_commands(1),to_events(1),run(1)  # Stateless high-level entry point for the VQL pipeline.
  src/vql/library/__init__.py:
  src/vql/renderers/__init__.py:
    e: __getattr__
    __getattr__(name)
  src/vql/renderers/base.py:
    e: render_program,VQLRenderer,VQLRendererAdapter
    VQLRenderer: render(1)  # Structural protocol for any backend able to render a VQL pro
    VQLRendererAdapter: render(1)  # Mixin granting an existing ``Renderer`` subclass a ``render(
    render_program(renderer;program)
  src/vql/renderers/playwright.py:
    e: PlaywrightVQLRenderer
    PlaywrightVQLRenderer: __init__(2)  # Playwright renderer that can consume a :class:`VQLProgram` d
  src/vql/renderers/svg.py:
    e: render_to_svg,render_to_png,SVGVQLRenderer
    SVGVQLRenderer:  # SVG renderer that can consume a :class:`VQLProgram` directly
    render_to_svg(program)
    render_to_png(program;path)
  src/vql/schema/__init__.py:
  src/vql/schema/program.py:
    e: RenderTarget,Style,Transform,Anchor,Constraint,Relation,Primitive,Object,Layer,Scene,ValidationSpec,VQLProgram
    RenderTarget:  # Supported render backends for a VQL program.
    Style: validate(0),to_dict(0),from_dict(2)  # Visual style for an object/primitive.
    Transform: is_identity(0),to_dict(0),from_dict(2)  # Affine transform applied to an object.
    Anchor: to_dict(0),from_dict(2)  # A named reference point on the canvas/object.
    Constraint: to_dict(0),from_dict(2)  # A declarative constraint on an object (placeholder for solve
    Relation: to_dict(0),from_dict(2)  # A relation between two objects (placeholder for layout engin
    Primitive: validate(0),to_dict(0),from_dict(2)  # A drawable primitive — the smallest unit of geometry.
    Object: validate(0),to_dict(0),from_dict(2)  # A logical drawing object — one or more primitives sharing a 
    Layer: validate(0),to_dict(0),from_dict(2)  # An ordered group of objects.
    Scene: validate(0),iter_objects(0),to_dict(0),from_dict(2)  # The root container — canvas dimensions, background, and laye
    ValidationSpec: to_dict(0),from_dict(2)  # Declarative expectation describing what a correct render mus
    VQLProgram: validate(0),is_valid(0),object_count(0),to_dict(0),from_dict(2)  # Top-level VQL program — the contract between NL parsing and 
  src/vql/validation/__init__.py:
  src/vql/validation/metadata.py:
    e: _load_imgl_metadata_schema,validate_program_metadata
    _load_imgl_metadata_schema()
    validate_program_metadata(metadata)
  src/vql/validation/spec.py:
    e: _program_shapes,_program_colors,_match_items,validate_program,VQLValidationReport
    VQLValidationReport: to_dict(0)  # Outcome of validating a program against a spec.
    _program_shapes(program)
    _program_colors(program)
    _match_items(expected;present;label)
    validate_program(program;spec)
  tests/test_adopt_window_capture.py:
    e: test_image_is_blank_detects_black,test_image_is_blank_accepts_colored,test_image_stats_reports_blank
    test_image_is_blank_detects_black(tmp_path)
    test_image_is_blank_accepts_colored(tmp_path)
    test_image_stats_reports_blank(tmp_path)
  tests/test_metadata_validation.py:
    e: test_empty_metadata_valid,test_valid_imgl_metadata,test_invalid_capture_type,test_invalid_window_os
    test_empty_metadata_valid()
    test_valid_imgl_metadata()
    test_invalid_capture_type()
    test_invalid_window_os(meta)
  tests/test_photo_roundtrip.py:
    e: _flat_shapes_image,test_nl_drawing_roundtrip,test_img2svg_sets_scene_background,test_img2svg_vql_render_roundtrip,test_vtracer_roundtrip_when_installed,test_metadata_only_program_renders_background_only,test_trace_contours_graceful_without_opencv
    _flat_shapes_image(path)
    test_nl_drawing_roundtrip(tmp_path)
    test_img2svg_sets_scene_background(tmp_path)
    test_img2svg_vql_render_roundtrip(tmp_path)
    test_vtracer_roundtrip_when_installed(tmp_path)
    test_metadata_only_program_renders_background_only(tmp_path)
    test_trace_contours_graceful_without_opencv(tmp_path)
  tests/test_screenshot_merge.py:
    e: test_screenshot_merge_reduces_object_count
    test_screenshot_merge_reduces_object_count(tmp_path)
  tests/test_vql.py:
    e: test_empty_program_is_structurally_valid,test_invalid_scene_dimensions_fail,test_program_roundtrip_to_dict,test_commands_program_roundtrip_preserves_shapes_and_colors,test_program_to_commands_starts_with_init_canvas,test_commands_to_program_is_inverse_of_program_to_commands,test_compile_to_events_produces_shape_drawn,test_render_to_svg_returns_markup,test_render_to_png_without_cairosvg_raises_clear_error,test_validate_program_passes_with_matching_spec,test_validate_program_reports_missing_shape,test_facade_run_full_pipeline,test_facade_run_without_render_skips_svg,test_nl_parser_to_vql_returns_program,test_nl_parser_parse_still_returns_commands,test_vql_library_exposes_primitives,test_playwright_vql_renderer_render_delegates_to_events,test_playwright_vql_renderer_is_renderer_subclass
    test_empty_program_is_structurally_valid()
    test_invalid_scene_dimensions_fail()
    test_program_roundtrip_to_dict()
    test_commands_program_roundtrip_preserves_shapes_and_colors()
    test_program_to_commands_starts_with_init_canvas()
    test_commands_to_program_is_inverse_of_program_to_commands()
    test_compile_to_events_produces_shape_drawn()
    test_render_to_svg_returns_markup()
    test_render_to_png_without_cairosvg_raises_clear_error(tmp_path)
    test_validate_program_passes_with_matching_spec()
    test_validate_program_reports_missing_shape()
    test_facade_run_full_pipeline()
    test_facade_run_without_render_skips_svg()
    test_nl_parser_to_vql_returns_program()
    test_nl_parser_parse_still_returns_commands()
    test_vql_library_exposes_primitives()
    test_playwright_vql_renderer_render_delegates_to_events()
    test_playwright_vql_renderer_is_renderer_subclass()
```

### `project/logic.pl`

```prolog markpact:analysis path=project/logic.pl
% ── Project Metadata ─────────────────────────────────────
project_metadata('vql', '0.1.4', 'python').

% ── Project Files ────────────────────────────────────────
project_file('app.doql.less', 148, 'less').
project_file('examples/full-pipeline.sh', 81, 'shell').
project_file('examples/generate-demo-screen.py', 77, 'python').
project_file('examples/img2nl-vql-flow.sh', 215, 'shell').
project_file('examples/live-capture-test.sh', 95, 'shell').
project_file('examples/photo-roundtrip-test.py', 407, 'python').
project_file('examples/scope-window.py', 54, 'python').
project_file('install-dev.sh', 38, 'shell').
project_file('packages/cli2vql/src/cli2vql/__init__.py', 2, 'python').
project_file('packages/cli2vql/src/cli2vql/cli.py', 69, 'python').
project_file('packages/dsl2img2svg/src/dsl2img2svg/__init__.py', 6, 'python').
project_file('packages/dsl2img2svg/src/dsl2img2svg/cli.py', 22, 'python').
project_file('packages/dsl2img2svg/src/dsl2img2svg/dispatch.py', 116, 'python').
project_file('packages/dsl2img2svg/tests/test_dispatch.py', 32, 'python').
project_file('packages/dsl2vql/scripts/generate-proto.sh', 8, 'shell').
project_file('packages/dsl2vql/src/dsl2vql/__init__.py', 7, 'python').
project_file('packages/dsl2vql/src/dsl2vql/bus.py', 78, 'python').
project_file('packages/dsl2vql/src/dsl2vql/cli.py', 98, 'python').
project_file('packages/dsl2vql/src/dsl2vql/codec.py', 36, 'python').
project_file('packages/dsl2vql/src/dsl2vql/engine.py', 9, 'python').
project_file('packages/dsl2vql/src/dsl2vql/events.py', 109, 'python').
project_file('packages/dsl2vql/src/dsl2vql/grammar.py', 97, 'python').
project_file('packages/dsl2vql/src/dsl2vql/handlers/__init__.py', 6, 'python').
project_file('packages/dsl2vql/src/dsl2vql/handlers/command.py', 131, 'python').
project_file('packages/dsl2vql/src/dsl2vql/handlers/query.py', 110, 'python').
project_file('packages/dsl2vql/src/dsl2vql/pb_codec.py', 158, 'python').
project_file('packages/dsl2vql/src/dsl2vql/result.py', 29, 'python').
project_file('packages/dsl2vql/src/dsl2vql/schema_registry.py', 47, 'python').
project_file('packages/dsl2vql/src/dsl2vql/v1/__init__.py', 6, 'python').
project_file('packages/dsl2vql/src/dsl2vql/v1/command_pb2.py', 53, 'python').
project_file('packages/dsl2vql/src/dsl2vql/v1/result_pb2.py', 40, 'python').
project_file('packages/dsl2vql/tests/test_parity.py', 29, 'python').
project_file('packages/img2svg/src/img2svg/__init__.py', 14, 'python').
project_file('packages/img2svg/src/img2svg/cli.py', 72, 'python').
project_file('packages/img2svg/src/img2svg/svg_emit.py', 135, 'python').
project_file('packages/img2svg/src/img2svg/to_vql.py', 142, 'python').
project_file('packages/img2svg/src/img2svg/trace.py', 264, 'python').
project_file('packages/img2svg/tests/test_img2svg.py', 101, 'python').
project_file('packages/img2vql/src/img2vql/__init__.py', 27, 'python').
project_file('packages/img2vql/src/img2vql/adopt.py', 64, 'python').
project_file('packages/img2vql/src/img2vql/cli.py', 88, 'python').
project_file('packages/img2vql/src/img2vql/describe_ui.py', 122, 'python').
project_file('packages/img2vql/src/img2vql/detect.py', 380, 'python').
project_file('packages/img2vql/src/img2vql/diagnose.py', 126, 'python').
project_file('packages/img2vql/src/img2vql/fingerprint.py', 105, 'python').
project_file('packages/img2vql/src/img2vql/metadata.py', 340, 'python').
project_file('packages/img2vql/src/img2vql/program.py', 142, 'python').
project_file('packages/img2vql/tests/test_auto_ocr.py', 45, 'python').
project_file('packages/img2vql/tests/test_detect.py', 75, 'python').
project_file('packages/img2vql/tests/test_diagnose.py', 31, 'python').
project_file('packages/img2vql/tests/test_fingerprint.py', 93, 'python').
project_file('packages/img2vql/tests/test_metadata_imgl.py', 49, 'python').
project_file('packages/mcp2vql/src/mcp2vql/__init__.py', 6, 'python').
project_file('packages/mcp2vql/src/mcp2vql/cli.py', 9, 'python').
project_file('packages/mcp2vql/src/mcp2vql/server.py', 136, 'python').
project_file('packages/nlp2vql/src/nlp2vql/__init__.py', 7, 'python').
project_file('packages/nlp2vql/src/nlp2vql/apply.py', 49, 'python').
project_file('packages/nlp2vql/src/nlp2vql/cli.py', 54, 'python').
project_file('packages/nlp2vql/src/nlp2vql/to_dsl.py', 43, 'python').
project_file('packages/rest2vql/src/rest2vql/__init__.py', 6, 'python').
project_file('packages/rest2vql/src/rest2vql/app.py', 73, 'python').
project_file('packages/rest2vql/src/rest2vql/cli.py', 25, 'python').
project_file('packages/rest2vql/src/rest2vql/window.py', 125, 'python').
project_file('packages/rest2vql/src/rest2vql/window_routes.py', 111, 'python').
project_file('packages/rest2vql/tests/test_window_api.py', 121, 'python').
project_file('packages/uri2img2svg/src/uri2img2svg/__init__.py', 7, 'python').
project_file('packages/uri2img2svg/src/uri2img2svg/cli.py', 29, 'python').
project_file('packages/uri2img2svg/src/uri2img2svg/query.py', 145, 'python').
project_file('packages/uri2img2svg/src/uri2img2svg/uri.py', 60, 'python').
project_file('packages/uri2img2svg/tests/test_uri2img2svg.py', 42, 'python').
project_file('packages/uri2vql/src/uri2vql/__init__.py', 46, 'python').
project_file('packages/uri2vql/src/uri2vql/cli.py', 353, 'python').
project_file('packages/uri2vql/src/uri2vql/compile.py', 37, 'python').
project_file('packages/uri2vql/src/uri2vql/nlp2uri.py', 330, 'python').
project_file('packages/uri2vql/src/uri2vql/patch.py', 41, 'python').
project_file('packages/uri2vql/src/uri2vql/query.py', 96, 'python').
project_file('packages/uri2vql/src/uri2vql/run.py', 65, 'python').
project_file('packages/uri2vql/src/uri2vql/uri.py', 184, 'python').
project_file('packages/uri2vql/src/uri2vql/window.py', 654, 'python').
project_file('packages/uri2vql/tests/test_nlp2uri_window.py', 31, 'python').
project_file('packages/uri2vql/tests/test_window_refresh.py', 79, 'python').
project_file('project.sh', 59, 'shell').
project_file('scripts/test-goal.sh', 7, 'shell').
project_file('src/vql/__init__.py', 57, 'python').
project_file('src/vql/adopt/__init__.py', 20, 'python').
project_file('src/vql/adopt/portal_capture.py', 110, 'python').
project_file('src/vql/adopt/window.py', 805, 'python').
project_file('src/vql/api.py', 56, 'python').
project_file('src/vql/compiler/__init__.py', 16, 'python').
project_file('src/vql/compiler/legacy_drawcommand.py', 143, 'python').
project_file('src/vql/compiler/nl_to_vql.py', 70, 'python').
project_file('src/vql/drawing/__init__.py', 17, 'python').
project_file('src/vql/drawing/arrow_generator.py', 47, 'python').
project_file('src/vql/drawing/bird_generator.py', 50, 'python').
project_file('src/vql/drawing/boat_generator.py', 41, 'python').
project_file('src/vql/drawing/butterfly_generator.py', 51, 'python').
project_file('src/vql/drawing/car_generator.py', 49, 'python').
project_file('src/vql/drawing/castle_generator.py', 64, 'python').
project_file('src/vql/drawing/cat_generator.py', 56, 'python').
project_file('src/vql/drawing/circle_generator.py', 30, 'python').
project_file('src/vql/drawing/cloud_detailed_generator.py', 48, 'python').
project_file('src/vql/drawing/colors.py', 136, 'python').
project_file('src/vql/drawing/commands.py', 272, 'python').
project_file('src/vql/drawing/crescent_generator.py', 37, 'python').
project_file('src/vql/drawing/cross_generator.py', 34, 'python').
project_file('src/vql/drawing/diamond_generator.py', 37, 'python').
project_file('src/vql/drawing/dot_generator.py', 30, 'python').
project_file('src/vql/drawing/ellipse_generator.py', 31, 'python').
project_file('src/vql/drawing/event_store.py', 102, 'python').
project_file('src/vql/drawing/events.py', 143, 'python').
project_file('src/vql/drawing/fish_generator.py', 47, 'python').
project_file('src/vql/drawing/flower_generator.py', 36, 'python').
project_file('src/vql/drawing/grid_generator.py', 37, 'python').
project_file('src/vql/drawing/heart_generator.py', 31, 'python').
project_file('src/vql/drawing/hexagon_generator.py', 28, 'python').
project_file('src/vql/drawing/house_generator.py', 31, 'python').
project_file('src/vql/drawing/line_generator.py', 26, 'python').
project_file('src/vql/drawing/mountain_generator.py', 40, 'python').
project_file('src/vql/drawing/nl_parser.py', 226, 'python').
project_file('src/vql/drawing/octagon_generator.py', 28, 'python').
project_file('src/vql/drawing/path_generator.py', 26, 'python').
project_file('src/vql/drawing/pentagon_generator.py', 28, 'python').
project_file('src/vql/drawing/rectangle_generator.py', 27, 'python').
project_file('src/vql/drawing/renderers/__init__.py', 10, 'python').
project_file('src/vql/drawing/renderers/base.py', 85, 'python').
project_file('src/vql/drawing/renderers/playwright.py', 216, 'python').
project_file('src/vql/drawing/renderers/svg.py', 94, 'python').
project_file('src/vql/drawing/rocket_generator.py', 53, 'python').
project_file('src/vql/drawing/shape_generator.py', 38, 'python').
project_file('src/vql/drawing/shape_registry.py', 104, 'python').
project_file('src/vql/drawing/shapes.py', 79, 'python').
project_file('src/vql/drawing/spiral_generator.py', 33, 'python').
project_file('src/vql/drawing/square_generator.py', 26, 'python').
project_file('src/vql/drawing/star_generator.py', 34, 'python').
project_file('src/vql/drawing/sun_generator.py', 37, 'python').
project_file('src/vql/drawing/svg_path_parser.py', 206, 'python').
project_file('src/vql/drawing/tree_generator.py', 34, 'python').
project_file('src/vql/drawing/triangle_generator.py', 27, 'python').
project_file('src/vql/drawing/wave_generator.py', 35, 'python').
project_file('src/vql/facade.py', 96, 'python').
project_file('src/vql/library/__init__.py', 15, 'python').
project_file('src/vql/renderers/__init__.py', 24, 'python').
project_file('src/vql/renderers/base.py', 66, 'python').
project_file('src/vql/renderers/playwright.py', 23, 'python').
project_file('src/vql/renderers/svg.py', 52, 'python').
project_file('src/vql/schema/__init__.py', 34, 'python').
project_file('src/vql/schema/program.py', 424, 'python').
project_file('src/vql/validation/__init__.py', 14, 'python').
project_file('src/vql/validation/metadata.py', 58, 'python').
project_file('src/vql/validation/spec.py', 92, 'python').
project_file('tests/test_adopt_window_capture.py', 37, 'python').
project_file('tests/test_metadata_validation.py', 41, 'python').
project_file('tests/test_photo_roundtrip.py', 116, 'python').
project_file('tests/test_screenshot_merge.py', 31, 'python').
project_file('tests/test_vql.py', 245, 'python').
project_file('tree.sh', 2, 'shell').

% ── Python Functions ─────────────────────────────────────
python_function('examples/generate-demo-screen.py', '_load_font', 1, 3, 2).
python_function('examples/generate-demo-screen.py', 'write_demo_screen', 1, 1, 9).
python_function('examples/generate-demo-screen.py', 'main', 0, 1, 6).
python_function('examples/photo-roundtrip-test.py', '_require_pil', 0, 2, 1).
python_function('examples/photo-roundtrip-test.py', 'sample_flat_shapes', 1, 1, 8).
python_function('examples/photo-roundtrip-test.py', 'sample_gradient', 1, 3, 12).
python_function('examples/photo-roundtrip-test.py', 'sample_product_photo', 1, 1, 7).
python_function('examples/photo-roundtrip-test.py', 'sample_natural_scene', 1, 4, 8).
python_function('examples/photo-roundtrip-test.py', 'sample_nl_drawing', 1, 2, 9).
python_function('examples/photo-roundtrip-test.py', 'test_img2svg_roundtrip', 2, 8, 21).
python_function('examples/photo-roundtrip-test.py', 'test_ui_grid_adopt', 1, 2, 12).
python_function('examples/photo-roundtrip-test.py', 'test_vtracer_roundtrip', 2, 10, 17).
python_function('examples/photo-roundtrip-test.py', 'test_opencv_contours', 2, 2, 9).
python_function('examples/photo-roundtrip-test.py', 'test_metadata_only_reconstruction', 1, 1, 9).
python_function('examples/photo-roundtrip-test.py', 'test_img2vql_detect', 1, 5, 4).
python_function('examples/photo-roundtrip-test.py', 'main', 0, 5, 24).
python_function('examples/scope-window.py', 'main', 0, 6, 7).
python_function('packages/cli2vql/src/cli2vql/cli.py', '_repl', 1, 6, 5).
python_function('packages/cli2vql/src/cli2vql/cli.py', 'main', 1, 14, 16).
python_function('packages/dsl2img2svg/src/dsl2img2svg/cli.py', 'main', 1, 4, 5).
python_function('packages/dsl2img2svg/src/dsl2img2svg/dispatch.py', '_parse_kv_args', 1, 4, 3).
python_function('packages/dsl2img2svg/src/dsl2img2svg/dispatch.py', 'dispatch', 1, 14, 16).
python_function('packages/dsl2img2svg/tests/test_dispatch.py', 'test_vectorize', 1, 3, 4).
python_function('packages/dsl2img2svg/tests/test_dispatch.py', 'test_query_uri', 1, 2, 3).
python_function('packages/dsl2vql/src/dsl2vql/bus.py', '_dispatch_cmd', 1, 5, 12).
python_function('packages/dsl2vql/src/dsl2vql/bus.py', '_bytes_to_cmd', 1, 3, 5).
python_function('packages/dsl2vql/src/dsl2vql/bus.py', 'dispatch', 1, 6, 11).
python_function('packages/dsl2vql/src/dsl2vql/bus.py', 'execute_dsl_line', 1, 1, 1).
python_function('packages/dsl2vql/src/dsl2vql/bus.py', 'execute_dsl', 1, 4, 5).
python_function('packages/dsl2vql/src/dsl2vql/cli.py', '_main_legacy', 1, 9, 14).
python_function('packages/dsl2vql/src/dsl2vql/cli.py', '_main_subcommand', 1, 9, 17).
python_function('packages/dsl2vql/src/dsl2vql/cli.py', 'main', 1, 4, 2).
python_function('packages/dsl2vql/src/dsl2vql/codec.py', 'encode_text', 1, 2, 2).
python_function('packages/dsl2vql/src/dsl2vql/codec.py', 'roundtrip_text', 1, 3, 5).
python_function('packages/dsl2vql/src/dsl2vql/codec.py', 'encode_protobuf', 1, 1, 1).
python_function('packages/dsl2vql/src/dsl2vql/codec.py', 'decode_protobuf', 1, 1, 1).
python_function('packages/dsl2vql/src/dsl2vql/events.py', 'default_event_store', 1, 1, 3).
python_function('packages/dsl2vql/src/dsl2vql/grammar.py', 'split_command', 1, 4, 3).
python_function('packages/dsl2vql/src/dsl2vql/grammar.py', 'pick_flag', 2, 3, 2).
python_function('packages/dsl2vql/src/dsl2vql/grammar.py', 'parse_line', 1, 28, 7).
python_function('packages/dsl2vql/src/dsl2vql/grammar.py', 'to_text', 1, 6, 6).
python_function('packages/dsl2vql/src/dsl2vql/handlers/command.py', '_read_json', 1, 1, 4).
python_function('packages/dsl2vql/src/dsl2vql/handlers/command.py', 'handle_generate', 1, 4, 10).
python_function('packages/dsl2vql/src/dsl2vql/handlers/command.py', 'handle_compile', 1, 4, 7).
python_function('packages/dsl2vql/src/dsl2vql/handlers/command.py', 'handle_patch', 1, 3, 8).
python_function('packages/dsl2vql/src/dsl2vql/handlers/command.py', 'handle_export', 1, 7, 11).
python_function('packages/dsl2vql/src/dsl2vql/handlers/command.py', 'handle_from_tokens', 2, 11, 14).
python_function('packages/dsl2vql/src/dsl2vql/handlers/query.py', '_load_program', 1, 1, 5).
python_function('packages/dsl2vql/src/dsl2vql/handlers/query.py', 'handle_query', 1, 4, 6).
python_function('packages/dsl2vql/src/dsl2vql/handlers/query.py', 'handle_validate', 1, 6, 10).
python_function('packages/dsl2vql/src/dsl2vql/handlers/query.py', 'handle_render', 1, 9, 11).
python_function('packages/dsl2vql/src/dsl2vql/handlers/query.py', 'handle_resolve', 1, 3, 4).
python_function('packages/dsl2vql/src/dsl2vql/pb_codec.py', '_set_body', 2, 12, 5).
python_function('packages/dsl2vql/src/dsl2vql/pb_codec.py', 'envelope_to_dict', 1, 31, 4).
python_function('packages/dsl2vql/src/dsl2vql/pb_codec.py', 'encode_protobuf', 1, 1, 6).
python_function('packages/dsl2vql/src/dsl2vql/pb_codec.py', 'decode_protobuf', 1, 1, 3).
python_function('packages/dsl2vql/src/dsl2vql/pb_codec.py', 'encode_text_to_protobuf', 1, 2, 3).
python_function('packages/dsl2vql/src/dsl2vql/pb_codec.py', 'decode_protobuf_to_text', 1, 1, 2).
python_function('packages/dsl2vql/src/dsl2vql/pb_codec.py', 'result_to_pb', 1, 4, 4).
python_function('packages/dsl2vql/src/dsl2vql/pb_codec.py', 'encode_result_protobuf', 1, 1, 2).
python_function('packages/dsl2vql/src/dsl2vql/schema_registry.py', '_load_schemas', 0, 3, 9).
python_function('packages/dsl2vql/src/dsl2vql/schema_registry.py', 'schema_for_verb', 1, 1, 3).
python_function('packages/dsl2vql/src/dsl2vql/schema_registry.py', 'all_schemas', 0, 1, 2).
python_function('packages/dsl2vql/src/dsl2vql/schema_registry.py', 'validate_command_dict', 1, 3, 7).
python_function('packages/dsl2vql/src/dsl2vql/schema_registry.py', 'validate_schema_registry', 0, 3, 4).
python_function('packages/dsl2vql/tests/test_parity.py', 'test_parity_text_vs_dict', 0, 3, 1).
python_function('packages/dsl2vql/tests/test_parity.py', 'test_validate_schema_registry', 0, 2, 1).
python_function('packages/dsl2vql/tests/test_parity.py', 'test_encode_decode_roundtrip', 0, 3, 3).
python_function('packages/img2svg/src/img2svg/cli.py', 'main', 1, 11, 13).
python_function('packages/img2svg/src/img2svg/svg_emit.py', 'regions_to_svg', 1, 4, 5).
python_function('packages/img2svg/src/img2svg/svg_emit.py', '_vtracer_paths_to_svg', 1, 6, 4).
python_function('packages/img2svg/src/img2svg/svg_emit.py', 'paths_to_svg', 1, 3, 4).
python_function('packages/img2svg/src/img2svg/svg_emit.py', 'image_to_svg', 1, 7, 15).
python_function('packages/img2svg/src/img2svg/to_vql.py', '_background_from_regions', 1, 3, 3).
python_function('packages/img2svg/src/img2svg/to_vql.py', 'trace_to_vql_program', 1, 15, 20).
python_function('packages/img2svg/src/img2svg/to_vql.py', 'image_to_vql', 1, 5, 14).
python_function('packages/img2svg/src/img2svg/trace.py', '_hex_color', 1, 1, 0).
python_function('packages/img2svg/src/img2svg/trace.py', '_merge_grid_cells', 1, 15, 4).
python_function('packages/img2svg/src/img2svg/trace.py', 'trace_image_regions', 1, 6, 14).
python_function('packages/img2svg/src/img2svg/trace.py', 'trace_contours_opencv', 1, 8, 17).
python_function('packages/img2svg/src/img2svg/trace.py', '_parse_translate', 1, 3, 3).
python_function('packages/img2svg/src/img2svg/trace.py', '_parse_vtracer_svg', 1, 5, 9).
python_function('packages/img2svg/src/img2svg/trace.py', 'trace_vtracer', 1, 6, 11).
python_function('packages/img2svg/tests/test_img2svg.py', 'test_trace_regions', 1, 3, 5).
python_function('packages/img2svg/tests/test_img2svg.py', 'test_image_to_svg', 1, 5, 5).
python_function('packages/img2svg/tests/test_img2svg.py', 'test_image_to_vql', 1, 4, 6).
python_function('packages/img2svg/tests/test_img2svg.py', 'test_trace_vtracer', 1, 5, 10).
python_function('packages/img2svg/tests/test_img2svg.py', 'test_image_to_vql_vtracer', 1, 3, 4).
python_function('packages/img2svg/tests/test_img2svg.py', 'test_image_to_vql_sets_background', 1, 2, 6).
python_function('packages/img2vql/src/img2vql/adopt.py', 'adopt_screenshot', 1, 2, 12).
python_function('packages/img2vql/src/img2vql/cli.py', 'main', 1, 10, 13).
python_function('packages/img2vql/src/img2vql/describe_ui.py', '_role_name', 2, 2, 2).
python_function('packages/img2vql/src/img2vql/describe_ui.py', '_loc_name', 2, 2, 2).
python_function('packages/img2vql/src/img2vql/describe_ui.py', 'describe_ui_layout', 1, 14, 11).
python_function('packages/img2vql/src/img2vql/detect.py', '_hex_color', 1, 1, 0).
python_function('packages/img2vql/src/img2vql/detect.py', '_location_label', 4, 9, 0).
python_function('packages/img2vql/src/img2vql/detect.py', '_avg_color', 5, 5, 6).
python_function('packages/img2vql/src/img2vql/detect.py', '_detect_titlebar', 3, 5, 10).
python_function('packages/img2vql/src/img2vql/detect.py', '_detect_panels', 3, 5, 10).
python_function('packages/img2vql/src/img2vql/detect.py', '_flood_rects', 1, 14, 7).
python_function('packages/img2vql/src/img2vql/detect.py', '_detect_buttons', 3, 25, 23).
python_function('packages/img2vql/src/img2vql/detect.py', '_detect_toolbar', 3, 10, 10).
python_function('packages/img2vql/src/img2vql/detect.py', '_iou', 2, 3, 2).
python_function('packages/img2vql/src/img2vql/detect.py', '_dedupe', 1, 8, 4).
python_function('packages/img2vql/src/img2vql/detect.py', 'detect_ui_elements', 1, 8, 16).
python_function('packages/img2vql/src/img2vql/diagnose.py', '_normalize_locale', 1, 4, 4).
python_function('packages/img2vql/src/img2vql/diagnose.py', 'diagnose_image', 1, 2, 3).
python_function('packages/img2vql/src/img2vql/diagnose.py', 'diagnose_for_vql', 1, 10, 13).
python_function('packages/img2vql/src/img2vql/diagnose.py', '_recommendation', 1, 6, 1).
python_function('packages/img2vql/src/img2vql/fingerprint.py', 'fingerprint_for_image', 1, 4, 6).
python_function('packages/img2vql/src/img2vql/fingerprint.py', 'load_program_fingerprint', 1, 6, 7).
python_function('packages/img2vql/src/img2vql/fingerprint.py', '_json_safe', 1, 7, 6).
python_function('packages/img2vql/src/img2vql/fingerprint.py', 'compare_with_program', 2, 5, 5).
python_function('packages/img2vql/src/img2vql/metadata.py', '_json_safe', 1, 7, 6).
python_function('packages/img2vql/src/img2vql/metadata.py', '_compact_special_hits', 1, 1, 4).
python_function('packages/img2vql/src/img2vql/metadata.py', '_text_likely', 2, 4, 1).
python_function('packages/img2vql/src/img2vql/metadata.py', 'rapidocr_special_hits', 1, 10, 13).
python_function('packages/img2vql/src/img2vql/metadata.py', 'auto_ocr_special_hits', 2, 3, 6).
python_function('packages/img2vql/src/img2vql/metadata.py', 'imgl_ocr_special_hits', 1, 8, 9).
python_function('packages/img2vql/src/img2vql/metadata.py', '_merge_special_hits', 2, 2, 4).
python_function('packages/img2vql/src/img2vql/metadata.py', 'img2nl_metadata_slice', 1, 9, 9).
python_function('packages/img2vql/src/img2vql/metadata.py', 'merge_program_metadata', 2, 1, 8).
python_function('packages/img2vql/src/img2vql/metadata.py', 'refresh_program_metadata', 2, 4, 11).
python_function('packages/img2vql/src/img2vql/metadata.py', 'metadata_from_diagnose', 1, 6, 7).
python_function('packages/img2vql/src/img2vql/metadata.py', 'save_diagnose_to_program', 2, 4, 12).
python_function('packages/img2vql/src/img2vql/program.py', '_role_style', 1, 1, 2).
python_function('packages/img2vql/src/img2vql/program.py', 'elements_to_vql_program', 1, 11, 19).
python_function('packages/img2vql/src/img2vql/program.py', '_bbox_contains', 2, 4, 0).
python_function('packages/img2vql/src/img2vql/program.py', '_build_contains_relations', 1, 8, 4).
python_function('packages/img2vql/tests/test_auto_ocr.py', 'test_text_likely_when_edges_suggest_text', 0, 2, 1).
python_function('packages/img2vql/tests/test_auto_ocr.py', 'test_text_likely_false_when_has_text', 0, 2, 1).
python_function('packages/img2vql/tests/test_auto_ocr.py', 'test_auto_ocr_uses_rapidocr_when_available', 1, 3, 5).
python_function('packages/img2vql/tests/test_detect.py', '_make_ui_fixture', 1, 1, 4).
python_function('packages/img2vql/tests/test_detect.py', 'test_detect_finds_titlebar_and_buttons', 1, 6, 2).
python_function('packages/img2vql/tests/test_detect.py', 'test_describe_ui_polish', 1, 3, 4).
python_function('packages/img2vql/tests/test_detect.py', 'test_adopt_writes_contains_relations', 1, 4, 3).
python_function('packages/img2vql/tests/test_detect.py', 'test_adopt_writes_vql_program', 1, 7, 4).
python_function('packages/img2vql/tests/test_diagnose.py', 'test_diagnose_blank_vs_rich', 1, 4, 5).
python_function('packages/img2vql/tests/test_fingerprint.py', '_solid', 3, 1, 2).
python_function('packages/img2vql/tests/test_fingerprint.py', 'test_screenshot_to_program_stores_fingerprint', 1, 3, 4).
python_function('packages/img2vql/tests/test_fingerprint.py', 'test_diagnose_uses_program_fingerprint', 1, 4, 8).
python_function('packages/img2vql/tests/test_fingerprint.py', 'test_analyze_skips_adopt_when_unchanged', 1, 7, 4).
python_function('packages/img2vql/tests/test_fingerprint.py', 'test_screenshot_stores_special_hits_metadata', 1, 3, 3).
python_function('packages/img2vql/tests/test_fingerprint.py', 'test_compare_with_program', 1, 5, 7).
python_function('packages/img2vql/tests/test_metadata_imgl.py', '_text_image', 2, 1, 4).
python_function('packages/img2vql/tests/test_metadata_imgl.py', 'test_imgl_ocr_special_hits_finds_text', 1, 3, 3).
python_function('packages/img2vql/tests/test_metadata_imgl.py', 'test_merge_program_metadata_uses_imgl_when_img2nl_misses', 1, 3, 3).
python_function('packages/img2vql/tests/test_metadata_imgl.py', 'test_refresh_program_metadata_persists_imgl_ocr', 1, 3, 5).
python_function('packages/mcp2vql/src/mcp2vql/server.py', '_require_fastmcp', 0, 2, 1).
python_function('packages/mcp2vql/src/mcp2vql/server.py', 'main', 0, 1, 2).
python_function('packages/nlp2vql/src/nlp2vql/apply.py', 'apply_nl', 1, 2, 3).
python_function('packages/nlp2vql/src/nlp2vql/cli.py', 'main', 1, 11, 11).
python_function('packages/nlp2vql/src/nlp2vql/to_dsl.py', '_intent', 1, 11, 2).
python_function('packages/nlp2vql/src/nlp2vql/to_dsl.py', 'nl_to_dsl_line', 1, 8, 1).
python_function('packages/nlp2vql/src/nlp2vql/to_dsl.py', 'to_dsl', 1, 1, 1).
python_function('packages/rest2vql/src/rest2vql/app.py', 'create_app', 0, 1, 25).
python_function('packages/rest2vql/src/rest2vql/cli.py', 'main', 1, 1, 5).
python_function('packages/rest2vql/src/rest2vql/window.py', 'window_detect', 1, 2, 3).
python_function('packages/rest2vql/src/rest2vql/window.py', 'window_compare', 1, 1, 1).
python_function('packages/rest2vql/src/rest2vql/window.py', 'window_refresh', 1, 1, 1).
python_function('packages/rest2vql/src/rest2vql/window.py', 'window_diagnose', 1, 2, 1).
python_function('packages/rest2vql/src/rest2vql/window.py', 'window_analyze', 1, 1, 1).
python_function('packages/rest2vql/src/rest2vql/window.py', 'window_adopt', 1, 1, 1).
python_function('packages/rest2vql/src/rest2vql/window.py', 'window_summary', 0, 7, 1).
python_function('packages/rest2vql/src/rest2vql/window_routes.py', '_window_response', 1, 2, 2).
python_function('packages/rest2vql/src/rest2vql/window_routes.py', 'post_window_detect', 1, 2, 5).
python_function('packages/rest2vql/src/rest2vql/window_routes.py', 'post_window_compare', 1, 2, 5).
python_function('packages/rest2vql/src/rest2vql/window_routes.py', 'post_window_refresh', 1, 2, 5).
python_function('packages/rest2vql/src/rest2vql/window_routes.py', 'post_window_diagnose', 1, 2, 5).
python_function('packages/rest2vql/src/rest2vql/window_routes.py', 'post_window_analyze', 1, 2, 5).
python_function('packages/rest2vql/src/rest2vql/window_routes.py', 'post_window_adopt', 1, 2, 5).
python_function('packages/rest2vql/src/rest2vql/window_routes.py', 'post_window_summary', 1, 2, 5).
python_function('packages/rest2vql/tests/test_window_api.py', 'client', 0, 1, 2).
python_function('packages/rest2vql/tests/test_window_api.py', '_solid_image', 2, 1, 2).
python_function('packages/rest2vql/tests/test_window_api.py', '_program_with_fingerprint', 2, 1, 2).
python_function('packages/rest2vql/tests/test_window_api.py', 'test_health', 1, 3, 2).
python_function('packages/rest2vql/tests/test_window_api.py', 'test_window_detect_missing_dep', 2, 5, 5).
python_function('packages/rest2vql/tests/test_window_api.py', 'test_window_compare', 2, 5, 8).
python_function('packages/rest2vql/tests/test_window_api.py', 'test_window_refresh', 2, 5, 8).
python_function('packages/rest2vql/tests/test_window_api.py', 'test_window_diagnose', 2, 4, 8).
python_function('packages/uri2img2svg/src/uri2img2svg/cli.py', 'main', 1, 4, 9).
python_function('packages/uri2img2svg/src/uri2img2svg/query.py', 'query_uri', 1, 13, 12).
python_function('packages/uri2img2svg/src/uri2img2svg/uri.py', 'is_img2svg_uri', 1, 1, 2).
python_function('packages/uri2img2svg/src/uri2img2svg/uri.py', 'uri_for_vectorize', 1, 2, 2).
python_function('packages/uri2img2svg/src/uri2img2svg/uri.py', 'parse_img2svg_uri', 1, 9, 7).
python_function('packages/uri2img2svg/tests/test_uri2img2svg.py', 'test_parse_uri', 0, 4, 1).
python_function('packages/uri2img2svg/tests/test_uri2img2svg.py', 'test_vectorize', 1, 3, 6).
python_function('packages/uri2img2svg/tests/test_uri2img2svg.py', 'test_svg_uri', 1, 3, 4).
python_function('packages/uri2vql/src/uri2vql/cli.py', 'main', 1, 53, 29).
python_function('packages/uri2vql/src/uri2vql/compile.py', '_dsl_from_uri', 1, 4, 5).
python_function('packages/uri2vql/src/uri2vql/compile.py', 'compile_vql_uri', 2, 7, 6).
python_function('packages/uri2vql/src/uri2vql/nlp2uri.py', 'resolve_prompt_to_vql_uri', 1, 54, 23).
python_function('packages/uri2vql/src/uri2vql/nlp2uri.py', '_extract_click_target', 1, 3, 2).
python_function('packages/uri2vql/src/uri2vql/nlp2uri.py', '_extract_type_parts', 1, 5, 2).
python_function('packages/uri2vql/src/uri2vql/nlp2uri.py', 'nlp2uri', 1, 1, 1).
python_function('packages/uri2vql/src/uri2vql/nlp2uri.py', 'best_uri', 1, 2, 1).
python_function('packages/uri2vql/src/uri2vql/patch.py', 'patch_uri', 1, 7, 12).
python_function('packages/uri2vql/src/uri2vql/query.py', '_load_program', 1, 1, 5).
python_function('packages/uri2vql/src/uri2vql/query.py', 'query_uri', 1, 15, 15).
python_function('packages/uri2vql/src/uri2vql/run.py', 'run_uri', 1, 7, 6).
python_function('packages/uri2vql/src/uri2vql/run.py', 'run_uri_json', 1, 1, 3).
python_function('packages/uri2vql/src/uri2vql/uri.py', 'is_vql_uri', 1, 1, 2).
python_function('packages/uri2vql/src/uri2vql/uri.py', '_with_file', 1, 4, 4).
python_function('packages/uri2vql/src/uri2vql/uri.py', 'uri_for_program', 1, 1, 1).
python_function('packages/uri2vql/src/uri2vql/uri.py', 'uri_for_scene', 1, 1, 1).
python_function('packages/uri2vql/src/uri2vql/uri.py', 'uri_for_objects', 1, 1, 1).
python_function('packages/uri2vql/src/uri2vql/uri.py', 'uri_for_object', 1, 1, 1).
python_function('packages/uri2vql/src/uri2vql/uri.py', 'uri_for_window_analyze', 0, 2, 1).
python_function('packages/uri2vql/src/uri2vql/uri.py', 'uri_for_window_summary', 1, 1, 1).
python_function('packages/uri2vql/src/uri2vql/uri.py', 'uri_for_window_imgl', 0, 3, 1).
python_function('packages/uri2vql/src/uri2vql/uri.py', 'uri_for_imgl_list', 0, 1, 1).
python_function('packages/uri2vql/src/uri2vql/uri.py', 'uri_for_imgl_click', 0, 6, 1).
python_function('packages/uri2vql/src/uri2vql/uri.py', 'uri_for_imgl_type', 0, 6, 1).
python_function('packages/uri2vql/src/uri2vql/uri.py', 'uri_for_window_diagnose', 0, 2, 1).
python_function('packages/uri2vql/src/uri2vql/uri.py', 'uri_for_window_compare', 0, 3, 1).
python_function('packages/uri2vql/src/uri2vql/uri.py', 'uri_for_window_refresh', 0, 2, 1).
python_function('packages/uri2vql/src/uri2vql/uri.py', 'parse_vql_uri', 1, 5, 6).
python_function('packages/uri2vql/src/uri2vql/window.py', '_resolve_image_param', 1, 6, 8).
python_function('packages/uri2vql/src/uri2vql/window.py', '_normalize_locale', 1, 4, 4).
python_function('packages/uri2vql/src/uri2vql/window.py', '_diagnose_fallback', 1, 15, 13).
python_function('packages/uri2vql/src/uri2vql/window.py', '_resolve_window_image', 2, 8, 6).
python_function('packages/uri2vql/src/uri2vql/window.py', 'refresh_window_metadata', 1, 2, 2).
python_function('packages/uri2vql/src/uri2vql/window.py', 'compare_window_image', 1, 2, 2).
python_function('packages/uri2vql/src/uri2vql/window.py', 'diagnose_window_image', 1, 2, 3).
python_function('packages/uri2vql/src/uri2vql/window.py', '_query_window_imgl', 0, 17, 20).
python_function('packages/uri2vql/src/uri2vql/window.py', 'analyze_window_uri', 1, 4, 6).
python_function('packages/uri2vql/src/uri2vql/window.py', 'query_window', 1, 69, 29).
python_function('packages/uri2vql/tests/test_nlp2uri_window.py', 'test_nlp_refresh_window', 0, 4, 1).
python_function('packages/uri2vql/tests/test_nlp2uri_window.py', 'test_nlp_compare_window', 0, 3, 1).
python_function('packages/uri2vql/tests/test_nlp2uri_window.py', 'test_nlp_diagnose_window', 0, 3, 2).
python_function('packages/uri2vql/tests/test_nlp2uri_window.py', 'test_nlp_unchanged_suggests_compare', 0, 3, 1).
python_function('packages/uri2vql/tests/test_window_refresh.py', '_solid', 3, 1, 2).
python_function('packages/uri2vql/tests/test_window_refresh.py', 'test_diagnose_save_to_program', 1, 6, 10).
python_function('packages/uri2vql/tests/test_window_refresh.py', 'test_save_diagnose_to_program_helper', 1, 4, 6).
python_function('packages/uri2vql/tests/test_window_refresh.py', 'test_window_refresh_uri', 1, 4, 7).
python_function('src/vql/adopt/portal_capture.py', 'capture_via_portal', 1, 4, 23).
python_function('src/vql/adopt/portal_capture.py', 'main', 1, 2, 7).
python_function('src/vql/adopt/window.py', '_require_pillow', 0, 2, 1).
python_function('src/vql/adopt/window.py', '_session_type', 0, 2, 3).
python_function('src/vql/adopt/window.py', '_is_wayland', 0, 2, 3).
python_function('src/vql/adopt/window.py', '_capture_interactive_mode', 0, 2, 3).
python_function('src/vql/adopt/window.py', '_should_use_interactive_portal', 0, 4, 2).
python_function('src/vql/adopt/window.py', '_portal_python', 0, 7, 5).
python_function('src/vql/adopt/window.py', 'image_stats', 1, 4, 20).
python_function('src/vql/adopt/window.py', '_image_is_blank', 1, 8, 11).
python_function('src/vql/adopt/window.py', '_finalize_capture', 1, 1, 4).
python_function('src/vql/adopt/window.py', '_run_capture', 1, 7, 7).
python_function('src/vql/adopt/window.py', '_capture_with_gnome_shell', 1, 2, 4).
python_function('src/vql/adopt/window.py', '_capture_with_grim', 1, 2, 4).
python_function('src/vql/adopt/window.py', '_capture_with_gnome_screenshot', 1, 2, 4).
python_function('src/vql/adopt/window.py', '_capture_with_portal', 1, 15, 15).
python_function('src/vql/adopt/window.py', '_capture_with_scrot', 1, 2, 4).
python_function('src/vql/adopt/window.py', '_capture_with_mss', 1, 4, 6).
python_function('src/vql/adopt/window.py', '_capture_backends', 0, 7, 6).
python_function('src/vql/adopt/window.py', 'capture_diagnose', 1, 33, 25).
python_function('src/vql/adopt/window.py', '_capture_permission_hint', 0, 2, 1).
python_function('src/vql/adopt/window.py', '_active_window_title', 0, 4, 3).
python_function('src/vql/adopt/window.py', 'capture_screen', 1, 7, 14).
python_function('src/vql/adopt/window.py', '_hex_color', 1, 1, 0).
python_function('src/vql/adopt/window.py', '_optional_fingerprint', 1, 3, 3).
python_function('src/vql/adopt/window.py', '_enrich_program_metadata', 2, 2, 5).
python_function('src/vql/adopt/window.py', '_merge_grid_colors', 1, 15, 2).
python_function('src/vql/adopt/window.py', 'screenshot_to_program', 1, 12, 28).
python_function('src/vql/adopt/window.py', 'analyze_screenshot', 1, 13, 20).
python_function('src/vql/compiler/legacy_drawcommand.py', 'program_to_commands', 1, 4, 6).
python_function('src/vql/compiler/legacy_drawcommand.py', 'commands_to_program', 1, 9, 10).
python_function('src/vql/compiler/legacy_drawcommand.py', 'compile_to_events', 1, 3, 6).
python_function('src/vql/compiler/nl_to_vql.py', 'nl_to_program', 1, 6, 7).
python_function('src/vql/drawing/svg_path_parser.py', '_dispatch_command', 2, 16, 7).
python_function('src/vql/drawing/svg_path_parser.py', '_tokenize_path', 1, 1, 1).
python_function('src/vql/drawing/svg_path_parser.py', '_scale_groups', 1, 15, 3).
python_function('src/vql/drawing/svg_path_parser.py', 'parse_svg_path', 3, 7, 7).
python_function('src/vql/renderers/__init__.py', '__getattr__', 1, 2, 1).
python_function('src/vql/renderers/base.py', 'render_program', 2, 1, 3).
python_function('src/vql/renderers/svg.py', 'render_to_svg', 1, 1, 4).
python_function('src/vql/renderers/svg.py', 'render_to_png', 2, 2, 7).
python_function('src/vql/validation/metadata.py', '_load_imgl_metadata_schema', 0, 1, 3).
python_function('src/vql/validation/metadata.py', 'validate_program_metadata', 1, 14, 8).
python_function('src/vql/validation/spec.py', '_program_shapes', 1, 3, 1).
python_function('src/vql/validation/spec.py', '_program_colors', 1, 2, 2).
python_function('src/vql/validation/spec.py', '_match_items', 3, 4, 2).
python_function('src/vql/validation/spec.py', 'validate_program', 2, 4, 9).
python_function('tests/test_adopt_window_capture.py', 'test_image_is_blank_detects_black', 1, 2, 3).
python_function('tests/test_adopt_window_capture.py', 'test_image_is_blank_accepts_colored', 1, 2, 4).
python_function('tests/test_adopt_window_capture.py', 'test_image_stats_reports_blank', 1, 4, 3).
python_function('tests/test_metadata_validation.py', 'test_empty_metadata_valid', 0, 3, 1).
python_function('tests/test_metadata_validation.py', 'test_valid_imgl_metadata', 0, 2, 1).
python_function('tests/test_metadata_validation.py', 'test_invalid_capture_type', 0, 2, 2).
python_function('tests/test_metadata_validation.py', 'test_invalid_window_os', 1, 2, 2).
python_function('tests/test_photo_roundtrip.py', '_flat_shapes_image', 1, 1, 4).
python_function('tests/test_photo_roundtrip.py', 'test_nl_drawing_roundtrip', 1, 4, 4).
python_function('tests/test_photo_roundtrip.py', 'test_img2svg_sets_scene_background', 1, 4, 6).
python_function('tests/test_photo_roundtrip.py', 'test_img2svg_vql_render_roundtrip', 1, 4, 10).
python_function('tests/test_photo_roundtrip.py', 'test_vtracer_roundtrip_when_installed', 1, 4, 8).
python_function('tests/test_photo_roundtrip.py', 'test_metadata_only_program_renders_background_only', 1, 3, 8).
python_function('tests/test_photo_roundtrip.py', 'test_trace_contours_graceful_without_opencv', 1, 4, 4).
python_function('tests/test_screenshot_merge.py', 'test_screenshot_merge_reduces_object_count', 1, 5, 8).
python_function('tests/test_vql.py', 'test_empty_program_is_structurally_valid', 0, 3, 4).
python_function('tests/test_vql.py', 'test_invalid_scene_dimensions_fail', 0, 3, 4).
python_function('tests/test_vql.py', 'test_program_roundtrip_to_dict', 0, 3, 9).
python_function('tests/test_vql.py', 'test_commands_program_roundtrip_preserves_shapes_and_colors', 0, 7, 2).
python_function('tests/test_vql.py', 'test_program_to_commands_starts_with_init_canvas', 0, 4, 3).
python_function('tests/test_vql.py', 'test_commands_to_program_is_inverse_of_program_to_commands', 0, 3, 5).
python_function('tests/test_vql.py', 'test_compile_to_events_produces_shape_drawn', 0, 4, 3).
python_function('tests/test_vql.py', 'test_render_to_svg_returns_markup', 0, 3, 3).
python_function('tests/test_vql.py', 'test_render_to_png_without_cairosvg_raises_clear_error', 1, 6, 7).
python_function('tests/test_vql.py', 'test_validate_program_passes_with_matching_spec', 0, 3, 2).
python_function('tests/test_vql.py', 'test_validate_program_reports_missing_shape', 0, 3, 4).
python_function('tests/test_vql.py', 'test_facade_run_full_pipeline', 0, 4, 4).
python_function('tests/test_vql.py', 'test_facade_run_without_render_skips_svg', 0, 3, 3).
python_function('tests/test_vql.py', 'test_nl_parser_to_vql_returns_program', 0, 4, 5).
python_function('tests/test_vql.py', 'test_nl_parser_parse_still_returns_commands', 0, 2, 4).
python_function('tests/test_vql.py', 'test_vql_library_exposes_primitives', 0, 7, 6).
python_function('tests/test_vql.py', 'test_playwright_vql_renderer_render_delegates_to_events', 0, 3, 7).
python_function('tests/test_vql.py', 'test_playwright_vql_renderer_is_renderer_subclass', 0, 3, 2).

% ── Python Classes ───────────────────────────────────────
python_class('packages/dsl2img2svg/src/dsl2img2svg/dispatch.py', 'DispatchResult').
python_method('DispatchResult', 'to_dict', 0, 1, 0).
python_class('packages/dsl2vql/src/dsl2vql/events.py', 'DslEvent').
python_method('DslEvent', 'to_dict', 0, 1, 1).
python_class('packages/dsl2vql/src/dsl2vql/events.py', 'EventStore').
python_method('EventStore', '__init__', 1, 3, 1).
python_method('EventStore', 'append', 2, 3, 21).
python_method('EventStore', 'replay', 0, 6, 11).
python_class('packages/dsl2vql/src/dsl2vql/result.py', 'DslResult').
python_method('DslResult', 'to_dict', 0, 1, 0).
python_class('packages/img2svg/src/img2svg/trace.py', 'TracedRegion').
python_method('TracedRegion', 'to_dict', 0, 1, 1).
python_class('packages/img2vql/src/img2vql/detect.py', 'UIElement').
python_method('UIElement', 'width', 0, 1, 0).
python_method('UIElement', 'height', 0, 1, 0).
python_method('UIElement', 'center', 0, 1, 0).
python_method('UIElement', 'bbox_norm', 0, 1, 2).
python_method('UIElement', 'to_dict', 0, 1, 2).
python_class('packages/mcp2vql/src/mcp2vql/server.py', 'VqlMCPServer').
python_method('VqlMCPServer', '__post_init__', 0, 1, 3).
python_method('VqlMCPServer', '_register_tools', 0, 1, 19).
python_method('VqlMCPServer', 'run', 0, 1, 1).
python_class('packages/nlp2vql/src/nlp2vql/apply.py', 'ApplyResult').
python_method('ApplyResult', 'to_dict', 0, 1, 0).
python_class('packages/rest2vql/src/rest2vql/window.py', 'WindowImageBody').
python_class('packages/uri2img2svg/src/uri2img2svg/query.py', 'QueryResult').
python_method('QueryResult', 'to_dict', 0, 1, 0).
python_class('packages/uri2img2svg/src/uri2img2svg/uri.py', 'Img2SvgUri').
python_method('Img2SvgUri', 'target', 0, 1, 0).
python_class('packages/uri2vql/src/uri2vql/nlp2uri.py', 'ResolvedVqlUri').
python_method('ResolvedVqlUri', 'to_dict', 0, 1, 0).
python_class('packages/uri2vql/src/uri2vql/patch.py', 'PatchResult').
python_method('PatchResult', 'to_dict', 0, 1, 0).
python_class('packages/uri2vql/src/uri2vql/query.py', 'QueryResult').
python_method('QueryResult', 'to_dict', 0, 1, 0).
python_class('packages/uri2vql/src/uri2vql/run.py', 'RunResult').
python_method('RunResult', 'to_dict', 0, 1, 0).
python_class('packages/uri2vql/src/uri2vql/uri.py', 'VqlUri').
python_method('VqlUri', 'target', 0, 1, 0).
python_class('packages/uri2vql/src/uri2vql/window.py', 'WindowAnalyzeResult').
python_method('WindowAnalyzeResult', 'to_dict', 0, 1, 0).
python_class('src/vql/adopt/window.py', 'CaptureError').
python_class('src/vql/adopt/window.py', 'CaptureInfo').
python_method('CaptureInfo', 'to_dict', 0, 1, 0).
python_class('src/vql/adopt/window.py', 'CaptureAttempt').
python_method('CaptureAttempt', 'to_dict', 0, 1, 0).
python_class('src/vql/drawing/arrow_generator.py', 'ArrowGenerator').
python_method('ArrowGenerator', 'generate', 3, 3, 1).
python_class('src/vql/drawing/bird_generator.py', 'BirdGenerator').
python_method('BirdGenerator', 'generate', 3, 2, 4).
python_class('src/vql/drawing/boat_generator.py', 'BoatGenerator').
python_method('BoatGenerator', 'generate', 3, 1, 0).
python_class('src/vql/drawing/butterfly_generator.py', 'ButterflyGenerator').
python_method('ButterflyGenerator', 'generate', 3, 5, 4).
python_class('src/vql/drawing/car_generator.py', 'CarGenerator').
python_method('CarGenerator', 'generate', 3, 3, 4).
python_class('src/vql/drawing/castle_generator.py', 'CastleGenerator').
python_method('CastleGenerator', 'generate', 3, 3, 5).
python_class('src/vql/drawing/cat_generator.py', 'CatGenerator').
python_method('CatGenerator', 'generate', 3, 4, 4).
python_class('src/vql/drawing/circle_generator.py', 'CircleGenerator').
python_method('CircleGenerator', 'generate', 3, 2, 5).
python_class('src/vql/drawing/cloud_detailed_generator.py', 'CloudDetailedGenerator').
python_method('CloudDetailedGenerator', 'generate', 3, 4, 4).
python_class('src/vql/drawing/colors.py', 'ColorResolver').
python_method('ColorResolver', '__init__', 0, 1, 1).
python_method('ColorResolver', 'register', 2, 1, 2).
python_method('ColorResolver', 'resolve', 2, 3, 4).
python_method('ColorResolver', 'extract_colors', 1, 6, 9).
python_method('ColorResolver', 'available', 0, 1, 1).
python_method('ColorResolver', 'unique_colors', 0, 4, 2).
python_class('src/vql/drawing/commands.py', 'DrawCommand').
python_method('DrawCommand', 'validate', 0, 1, 0).
python_class('src/vql/drawing/commands.py', 'InitCanvas').
python_method('InitCanvas', 'validate', 0, 1, 1).
python_class('src/vql/drawing/commands.py', 'DrawShape').
python_method('DrawShape', 'validate', 0, 1, 1).
python_class('src/vql/drawing/commands.py', 'SetColor').
python_method('SetColor', 'validate', 0, 1, 0).
python_class('src/vql/drawing/commands.py', 'SelectTool').
python_method('SelectTool', 'validate', 0, 1, 0).
python_class('src/vql/drawing/commands.py', 'ClearCanvas').
python_method('ClearCanvas', 'validate', 0, 1, 0).
python_class('src/vql/drawing/commands.py', 'CommandHandler').
python_method('CommandHandler', '__call__', 3, 1, 0).
python_class('src/vql/drawing/commands.py', 'CommandBus').
python_method('CommandBus', '__init__', 1, 1, 0).
python_method('CommandBus', 'state', 0, 1, 1).
python_method('CommandBus', 'register_handler', 2, 1, 0).
python_method('CommandBus', 'add_pre_hook', 1, 1, 1).
python_method('CommandBus', 'add_post_hook', 1, 1, 1).
python_method('CommandBus', 'dispatch', 1, 5, 9).
python_method('CommandBus', 'rebuild_state', 0, 1, 1).
python_method('CommandBus', '_apply_event', 1, 5, 2).
python_method('CommandBus', '_handle_init_canvas', 1, 1, 2).
python_method('CommandBus', '_handle_draw_shape', 1, 8, 5).
python_method('CommandBus', '_handle_set_color', 1, 1, 2).
python_method('CommandBus', '_handle_select_tool', 1, 1, 2).
python_method('CommandBus', '_handle_clear_canvas', 1, 1, 2).
python_class('src/vql/drawing/crescent_generator.py', 'CrescentGenerator').
python_method('CrescentGenerator', 'generate', 3, 3, 4).
python_class('src/vql/drawing/cross_generator.py', 'CrossGenerator').
python_method('CrossGenerator', 'generate', 3, 1, 0).
python_class('src/vql/drawing/diamond_generator.py', 'DiamondGenerator').
python_method('DiamondGenerator', 'generate', 3, 1, 0).
python_class('src/vql/drawing/dot_generator.py', 'DotGenerator').
python_method('DotGenerator', 'generate', 3, 2, 5).
python_class('src/vql/drawing/ellipse_generator.py', 'EllipseGenerator').
python_method('EllipseGenerator', 'generate', 3, 2, 5).
python_class('src/vql/drawing/event_store.py', 'EventStore').
python_method('EventStore', '__init__', 0, 1, 0).
python_method('EventStore', 'events', 0, 1, 1).
python_method('EventStore', 'count', 0, 1, 1).
python_method('EventStore', 'append', 1, 2, 2).
python_method('EventStore', 'subscribe', 1, 1, 1).
python_method('EventStore', 'unsubscribe', 1, 3, 0).
python_method('EventStore', 'replay', 1, 2, 1).
python_method('EventStore', 'events_since', 1, 3, 0).
python_method('EventStore', 'events_of_type', 1, 3, 0).
python_method('EventStore', 'clear', 0, 1, 1).
python_method('EventStore', 'to_dict', 0, 2, 1).
python_method('EventStore', 'save', 1, 1, 5).
python_method('EventStore', 'load', 2, 3, 7).
python_method('EventStore', '__len__', 0, 1, 1).
python_method('EventStore', '__repr__', 0, 1, 1).
python_class('src/vql/drawing/events.py', 'EventType').
python_class('src/vql/drawing/events.py', 'DrawingEvent').
python_method('DrawingEvent', 'to_dict', 0, 1, 0).
python_method('DrawingEvent', 'from_dict', 2, 1, 6).
python_class('src/vql/drawing/events.py', 'CanvasInitialized').
python_method('CanvasInitialized', '__post_init__', 0, 1, 1).
python_class('src/vql/drawing/events.py', 'CanvasCleared').
python_method('CanvasCleared', '__post_init__', 0, 1, 1).
python_class('src/vql/drawing/events.py', 'ShapeDrawn').
python_method('ShapeDrawn', '__post_init__', 0, 1, 1).
python_class('src/vql/drawing/events.py', 'ColorChanged').
python_method('ColorChanged', '__post_init__', 0, 1, 1).
python_class('src/vql/drawing/events.py', 'ToolSelected').
python_method('ToolSelected', '__post_init__', 0, 1, 1).
python_class('src/vql/drawing/fish_generator.py', 'FishGenerator').
python_method('FishGenerator', 'generate', 3, 3, 4).
python_class('src/vql/drawing/flower_generator.py', 'FlowerGenerator').
python_method('FlowerGenerator', 'generate', 3, 3, 5).
python_class('src/vql/drawing/grid_generator.py', 'GridGenerator').
python_method('GridGenerator', 'generate', 3, 3, 3).
python_class('src/vql/drawing/heart_generator.py', 'HeartGenerator').
python_method('HeartGenerator', 'generate', 3, 2, 5).
python_class('src/vql/drawing/hexagon_generator.py', 'HexagonGenerator').
python_method('HexagonGenerator', 'generate', 3, 2, 4).
python_class('src/vql/drawing/house_generator.py', 'HouseGenerator').
python_method('HouseGenerator', 'generate', 3, 1, 0).
python_class('src/vql/drawing/line_generator.py', 'LineGenerator').
python_method('LineGenerator', 'generate', 3, 1, 1).
python_class('src/vql/drawing/mountain_generator.py', 'MountainGenerator').
python_method('MountainGenerator', 'generate', 3, 1, 2).
python_class('src/vql/drawing/nl_parser.py', 'NLDrawingParser').
python_method('NLDrawingParser', '__init__', 1, 2, 1).
python_method('NLDrawingParser', 'parse', 3, 8, 14).
python_method('NLDrawingParser', 'to_vql', 5, 1, 1).
python_method('NLDrawingParser', 'detect_shape', 1, 2, 2).
python_method('NLDrawingParser', 'detect_color', 2, 2, 1).
python_method('NLDrawingParser', '_extract_shapes', 1, 3, 3).
python_method('NLDrawingParser', '_extract_size_params', 1, 4, 3).
python_method('NLDrawingParser', '_extract_shape_specific_params', 2, 11, 3).
python_class('src/vql/drawing/octagon_generator.py', 'OctagonGenerator').
python_method('OctagonGenerator', 'generate', 3, 2, 4).
python_class('src/vql/drawing/path_generator.py', 'PathGenerator').
python_method('PathGenerator', 'generate', 3, 5, 4).
python_class('src/vql/drawing/pentagon_generator.py', 'PentagonGenerator').
python_method('PentagonGenerator', 'generate', 3, 2, 4).
python_class('src/vql/drawing/rectangle_generator.py', 'RectangleGenerator').
python_method('RectangleGenerator', 'generate', 3, 1, 1).
python_class('src/vql/drawing/renderers/base.py', 'Renderer').
python_method('Renderer', 'init_canvas', 4, 1, 0).
python_method('Renderer', 'set_color', 1, 1, 0).
python_method('Renderer', 'draw_path', 3, 1, 0).
python_method('Renderer', 'draw_shape', 1, 1, 0).
python_method('Renderer', 'clear', 0, 1, 0).
python_method('Renderer', 'screenshot', 1, 1, 0).
python_method('Renderer', 'render_events', 1, 3, 2).
python_method('Renderer', 'dispose', 0, 1, 0).
python_class('src/vql/drawing/renderers/playwright.py', 'PlaywrightRenderer').
python_method('PlaywrightRenderer', '__init__', 2, 1, 0).
python_method('PlaywrightRenderer', 'init_canvas', 4, 8, 9).
python_method('PlaywrightRenderer', 'set_color', 1, 8, 7).
python_method('PlaywrightRenderer', 'draw_path', 3, 9, 6).
python_method('PlaywrightRenderer', 'draw_shape', 1, 3, 2).
python_method('PlaywrightRenderer', 'clear', 0, 3, 2).
python_method('PlaywrightRenderer', 'screenshot', 1, 2, 4).
python_method('PlaywrightRenderer', 'dispose', 0, 1, 0).
python_class('src/vql/drawing/renderers/svg.py', 'SVGRenderer').
python_method('SVGRenderer', '__init__', 0, 1, 0).
python_method('SVGRenderer', 'init_canvas', 4, 1, 1).
python_method('SVGRenderer', 'set_color', 1, 1, 0).
python_method('SVGRenderer', 'draw_path', 3, 6, 3).
python_method('SVGRenderer', 'draw_shape', 1, 3, 1).
python_method('SVGRenderer', 'clear', 0, 1, 1).
python_method('SVGRenderer', 'screenshot', 1, 1, 6).
python_method('SVGRenderer', 'to_svg', 0, 1, 1).
python_class('src/vql/drawing/rocket_generator.py', 'RocketGenerator').
python_method('RocketGenerator', 'generate', 3, 2, 4).
python_class('src/vql/drawing/shape_generator.py', 'ShapeGenerator').
python_method('ShapeGenerator', 'generate', 3, 1, 0).
python_class('src/vql/drawing/shape_registry.py', 'ShapeRegistry').
python_method('ShapeRegistry', 'register', 2, 1, 0).
python_method('ShapeRegistry', 'get', 2, 3, 3).
python_method('ShapeRegistry', 'available', 1, 2, 3).
python_method('ShapeRegistry', '_init_defaults', 1, 2, 2).
python_class('src/vql/drawing/spiral_generator.py', 'SpiralGenerator').
python_method('SpiralGenerator', 'generate', 3, 2, 5).
python_class('src/vql/drawing/square_generator.py', 'SquareGenerator').
python_method('SquareGenerator', 'generate', 3, 1, 1).
python_class('src/vql/drawing/star_generator.py', 'StarGenerator').
python_method('StarGenerator', 'generate', 3, 2, 5).
python_class('src/vql/drawing/sun_generator.py', 'SunGenerator').
python_method('SunGenerator', 'generate', 3, 3, 5).
python_class('src/vql/drawing/svg_path_parser.py', '_PathState').
python_method('_PathState', 'next_num', 0, 4, 2).
python_method('_PathState', 'close_subpath', 0, 2, 1).
python_method('_PathState', 'start_subpath', 2, 2, 1).
python_method('_PathState', 'line_to', 2, 1, 1).
python_method('_PathState', 'append_cubic', 6, 2, 1).
python_method('_PathState', 'append_quadratic', 4, 2, 1).
python_class('src/vql/drawing/tree_generator.py', 'TreeGenerator').
python_method('TreeGenerator', 'generate', 3, 2, 4).
python_class('src/vql/drawing/triangle_generator.py', 'TriangleGenerator').
python_method('TriangleGenerator', 'generate', 3, 1, 0).
python_class('src/vql/drawing/wave_generator.py', 'WaveGenerator').
python_method('WaveGenerator', 'generate', 3, 2, 4).
python_class('src/vql/facade.py', 'VQLResult').
python_class('src/vql/facade.py', 'VQLFacade').
python_method('VQLFacade', 'compile', 1, 1, 1).
python_method('VQLFacade', 'validate', 1, 1, 1).
python_method('VQLFacade', 'render_svg', 1, 1, 1).
python_method('VQLFacade', 'render_png', 2, 1, 1).
python_method('VQLFacade', 'to_commands', 1, 1, 1).
python_method('VQLFacade', 'to_events', 1, 1, 1).
python_method('VQLFacade', 'run', 1, 2, 4).
python_class('src/vql/renderers/base.py', 'VQLRenderer').
python_method('VQLRenderer', 'render', 1, 1, 0).
python_class('src/vql/renderers/base.py', 'VQLRendererAdapter').
python_method('VQLRendererAdapter', 'render', 1, 1, 1).
python_class('src/vql/renderers/playwright.py', 'PlaywrightVQLRenderer').
python_method('PlaywrightVQLRenderer', '__init__', 2, 1, 1).
python_class('src/vql/renderers/svg.py', 'SVGVQLRenderer').
python_class('src/vql/schema/program.py', 'RenderTarget').
python_class('src/vql/schema/program.py', 'Style').
python_method('Style', 'validate', 0, 1, 1).
python_method('Style', 'to_dict', 0, 2, 0).
python_method('Style', 'from_dict', 2, 2, 4).
python_class('src/vql/schema/program.py', 'Transform').
python_method('Transform', 'is_identity', 0, 5, 0).
python_method('Transform', 'to_dict', 0, 2, 0).
python_method('Transform', 'from_dict', 2, 2, 3).
python_class('src/vql/schema/program.py', 'Anchor').
python_method('Anchor', 'to_dict', 0, 2, 0).
python_method('Anchor', 'from_dict', 2, 2, 3).
python_class('src/vql/schema/program.py', 'Constraint').
python_method('Constraint', 'to_dict', 0, 2, 0).
python_method('Constraint', 'from_dict', 2, 2, 3).
python_class('src/vql/schema/program.py', 'Relation').
python_method('Relation', 'to_dict', 0, 2, 0).
python_method('Relation', 'from_dict', 2, 2, 3).
python_class('src/vql/schema/program.py', 'Primitive').
python_method('Primitive', 'validate', 0, 1, 0).
python_method('Primitive', 'to_dict', 0, 2, 0).
python_method('Primitive', 'from_dict', 2, 2, 3).
python_class('src/vql/schema/program.py', 'Object').
python_method('Object', 'validate', 0, 1, 3).
python_method('Object', 'to_dict', 0, 2, 1).
python_method('Object', 'from_dict', 2, 2, 5).
python_class('src/vql/schema/program.py', 'Layer').
python_method('Layer', 'validate', 0, 1, 2).
python_method('Layer', 'to_dict', 0, 2, 1).
python_method('Layer', 'from_dict', 2, 2, 4).
python_class('src/vql/schema/program.py', 'Scene').
python_method('Scene', 'validate', 0, 1, 3).
python_method('Scene', 'iter_objects', 0, 2, 0).
python_method('Scene', 'to_dict', 0, 2, 1).
python_method('Scene', 'from_dict', 2, 2, 4).
python_class('src/vql/schema/program.py', 'ValidationSpec').
python_method('ValidationSpec', 'to_dict', 0, 2, 1).
python_method('ValidationSpec', 'from_dict', 2, 2, 5).
python_class('src/vql/schema/program.py', 'VQLProgram').
python_method('VQLProgram', 'validate', 0, 1, 1).
python_method('VQLProgram', 'is_valid', 0, 1, 1).
python_method('VQLProgram', 'object_count', 0, 2, 2).
python_method('VQLProgram', 'to_dict', 0, 2, 1).
python_method('VQLProgram', 'from_dict', 2, 2, 5).
python_class('src/vql/validation/spec.py', 'VQLValidationReport').
python_method('VQLValidationReport', 'to_dict', 0, 1, 1).

% ── Dependencies ─────────────────────────────────────────

% ── Makefile Targets ─────────────────────────────────────
makefile_target('PACKAGES', '').
makefile_target('PYTEST', '').
makefile_target('help', '').
makefile_target('venv', '').
makefile_target('install', '').
makefile_target('install-dev', '').
makefile_target('proto', '').
makefile_target('test', '').
makefile_target('test-cov', '').
makefile_target('test-all', '').
makefile_target('test-roundtrip', '').
makefile_target('validate-schema', '').
makefile_target('compile', '').
makefile_target('serve', '').
makefile_target('clean', '').
makefile_target('build', '').
makefile_target('publish', '').
makefile_target('publish-confirm', '').
makefile_target('version', '').
makefile_target('goal', '').

% ── Taskfile Tasks ───────────────────────────────────────

% ── Environment Variables ────────────────────────────────
env_variable('OPENROUTER_API_KEY', '*(not set)*', 'Required: OpenRouter API key (https://openrouter.ai/keys)').
env_variable('LLM_MODEL', 'openrouter/qwen/qwen3-coder-next', 'Model (default: openrouter/qwen/qwen3-coder-next)').
env_variable('PFIX_AUTO_APPLY', 'true', 'true = apply fixes without asking').
env_variable('PFIX_AUTO_INSTALL_DEPS', 'true', 'true = auto pip/uv install').
env_variable('PFIX_AUTO_RESTART', 'false', 'true = os.execv restart after fix').
env_variable('PFIX_MAX_RETRIES', '3', '').
env_variable('PFIX_DRY_RUN', 'false', '').
env_variable('PFIX_ENABLED', 'true', '').
env_variable('PFIX_GIT_COMMIT', 'false', 'true = auto-commit fixes').
env_variable('PFIX_GIT_PREFIX', 'pfix:', 'commit message prefix').
env_variable('PFIX_CREATE_BACKUPS', 'false', 'false = disable .pfix_backups/ directory').

% ── TestQL Scenarios ─────────────────────────────────────
testql_scenario('generated-cli-tests.testql.toon.yaml', 'cli').
testql_scenario('generated-from-pytests.testql.toon.yaml', 'integration').

% ── Semantic Facts from SUMD.md ──────────────────────────
sumd_declared_file('app.doql.less', 'doql').
sumd_declared_file('testql-scenarios/generated-cli-tests.testql.toon.yaml', 'testql').
sumd_declared_file('testql-scenarios/generated-from-pytests.testql.toon.yaml', 'testql').
sumd_declared_file('project/map.toon.yaml', 'analysis').
sumd_declared_file('project/logic.pl', 'analysis').
sumd_declared_file('project/calls.toon.yaml', 'analysis').
sumd_interface('api', '').
sumd_workflow('venv', 'manual').
sumd_workflow_step('venv', 1, 'test -d .venv || python3 -m venv .venv').
sumd_workflow_step('venv', 2, 'echo "venv ready: .venv/"').
sumd_workflow('install', 'manual').
sumd_workflow_step('install', 1, '$(PIP) install -e .').
sumd_workflow('install-dev', 'manual').
sumd_workflow_step('install-dev', 1, '$(PIP) install -e .').
sumd_workflow_step('install-dev', 2, '$(PIP) install -e packages/uri2vql').
sumd_workflow_step('install-dev', 3, '$(PIP) install -e packages/nlp2vql').
sumd_workflow_step('install-dev', 4, '$(PIP) install -e packages/dsl2vql').
sumd_workflow_step('install-dev', 5, '$(PIP) install -e packages/cli2vql').
sumd_workflow_step('install-dev', 6, '$(PIP) install -e packages/rest2vql').
sumd_workflow_step('install-dev', 7, '-$(PIP) install -e packages/mcp2vql').
sumd_workflow_step('install-dev', 8, '$(PIP) install -e ".[dev,png]" jsonschema protobuf fastapi uvicorn httpx').
sumd_workflow_step('install-dev', 9, 'echo "dev stack installed"').
sumd_workflow('proto', 'manual').
sumd_workflow_step('proto', 1, '$(PIP) install -q grpcio-tools').
sumd_workflow_step('proto', 2, 'bash packages/dsl2vql/scripts/generate-proto.sh').
sumd_workflow('test', 'manual').
sumd_workflow_step('test', 1, 'echo "Running tests..."').
sumd_workflow_step('test', 2, '$(PYTEST)').
sumd_workflow('test-cov', 'manual').
sumd_workflow_step('test-cov', 1, '$(PYTHON) -m pytest tests/ packages/dsl2vql/tests -v \').
sumd_workflow_step('test-cov', 2, '--cov=vql --cov=dsl2vql --cov-report=term-missing').
sumd_workflow('test-all', 'manual').
sumd_workflow_step('test-all', 1, '$(PYTHON) -m pytest tests/ packages/ -q --tb=short').
sumd_workflow('test-roundtrip', 'manual').
sumd_workflow_step('test-roundtrip', 1, '$(PYTHON) -m pytest tests/test_photo_roundtrip.py -q --tb=short').
sumd_workflow_step('test-roundtrip', 2, '$(PYTHON) examples/photo-roundtrip-test.py --out /tmp/vql-roundtrip').
sumd_workflow('validate-schema', 'manual').
sumd_workflow_step('validate-schema', 1, 'dsl2vql validate-schema').
sumd_workflow('compile', 'manual').
sumd_workflow_step('compile', 1, 'dsl2vql -c \'COMPILE "narysuj czerwone koło"\' --json').
sumd_workflow('serve', 'manual').
sumd_workflow_step('serve', 1, 'rest2vql serve --port $(PORT) --host 127.0.0.1').
sumd_workflow('clean', 'manual').
sumd_workflow_step('clean', 1, 'find . -type f -name \'*.pyc\' -delete').
sumd_workflow('build', 'manual').
sumd_workflow_step('build', 1, '$(PIP) install -q build').
sumd_workflow_step('build', 2, 'rm -rf dist/ build/').
sumd_workflow_step('build', 3, '$(PYTHON) -m build').
sumd_workflow('publish', 'manual').
sumd_workflow_step('publish', 1, '$(PIP) install -q twine').
sumd_workflow_step('publish', 2, '$(PYTHON) -m twine check dist/*').
sumd_workflow('publish-confirm', 'manual').
sumd_workflow_step('publish-confirm', 1, '$(PYTHON) -m twine upload dist/*').
sumd_workflow('version', 'manual').
sumd_workflow_step('version', 1, 'echo -n "VERSION file: "').
sumd_workflow_step('version', 2, 'cat VERSION').
sumd_workflow_step('version', 3, '$(PYTHON) -c "from importlib.metadata import version').
sumd_workflow('goal', 'manual').
sumd_workflow_step('goal', 1, 'goal -a').
```

## Call Graph

*218 nodes · 256 edges · 53 modules · CC̄=4.1*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `query_window` *(in packages.uri2vql.src.uri2vql.window)* | 69 ⚠ | 2 | 147 | **149** |
| `resolve_prompt_to_vql_uri` *(in packages.uri2vql.src.uri2vql.nlp2uri)* | 54 ⚠ | 2 | 68 | **70** |
| `trace_to_vql_program` *(in packages.img2svg.src.img2svg.to_vql)* | 15 ⚠ | 3 | 46 | **49** |
| `_dispatch_command` *(in src.vql.drawing.svg_path_parser)* | 16 ⚠ | 1 | 47 | **48** |
| `screenshot_to_program` *(in src.vql.adopt.window)* | 12 ⚠ | 3 | 44 | **47** |
| `analyze_screenshot` *(in src.vql.adopt.window)* | 13 ⚠ | 2 | 45 | **47** |
| `_set_body` *(in packages.dsl2vql.src.dsl2vql.pb_codec)* | 12 ⚠ | 1 | 45 | **46** |
| `_query_window_imgl` *(in packages.uri2vql.src.uri2vql.window)* | 17 ⚠ | 1 | 45 | **46** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/oqlos/vql
# generated in 0.10s
# nodes: 218 | edges: 256 | modules: 53
# CC̄=4.1

HUBS[20]:
  packages.uri2vql.src.uri2vql.window.query_window
    CC=69  in:2  out:147  total:149
  packages.uri2vql.src.uri2vql.nlp2uri.resolve_prompt_to_vql_uri
    CC=54  in:2  out:68  total:70
  packages.img2svg.src.img2svg.to_vql.trace_to_vql_program
    CC=15  in:3  out:46  total:49
  src.vql.drawing.svg_path_parser._dispatch_command
    CC=16  in:1  out:47  total:48
  src.vql.adopt.window.screenshot_to_program
    CC=12  in:3  out:44  total:47
  src.vql.adopt.window.analyze_screenshot
    CC=13  in:2  out:45  total:47
  packages.dsl2vql.src.dsl2vql.pb_codec._set_body
    CC=12  in:1  out:45  total:46
  packages.uri2vql.src.uri2vql.window._query_window_imgl
    CC=17  in:1  out:45  total:46
  packages.img2vql.src.img2vql.detect._detect_buttons
    CC=25  in:1  out:45  total:46
  packages.img2vql.src.img2vql.describe_ui.describe_ui_layout
    CC=14  in:6  out:39  total:45
  src.vql.adopt.window.capture_diagnose
    CC=33  in:1  out:44  total:45
  examples.photo-roundtrip-test.main
    CC=5  in:0  out:45  total:45
  packages.rest2vql.src.rest2vql.app.create_app
    CC=1  in:1  out:43  total:44
  packages.dsl2img2svg.src.dsl2img2svg.dispatch.dispatch
    CC=14  in:0  out:41  total:41
  packages.img2vql.src.img2vql.program.elements_to_vql_program
    CC=11  in:1  out:40  total:41
  packages.uri2img2svg.src.uri2img2svg.query.query_uri
    CC=13  in:6  out:28  total:34
  packages.dsl2vql.src.dsl2vql.grammar.parse_line
    CC=28  in:6  out:27  total:33
  packages.dsl2vql.src.dsl2vql.events.EventStore.append
    CC=3  in:0  out:33  total:33
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
  src.vql.drawing.svg_path_parser  [4 funcs]
    _dispatch_command  CC=16  out:47
    _scale_groups  CC=15  out:6
    _tokenize_path  CC=1  out:1
    parse_svg_path  CC=7  out:7
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
  src.vql.validation.metadata  [2 funcs]
    _load_imgl_metadata_schema  CC=1  out:3
    validate_program_metadata  CC=14  out:14
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

## Intent

VQL — Visual Query Language for vector description of photographs and drawings
