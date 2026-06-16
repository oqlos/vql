"""img2vql ScreenContext importer tests."""

from __future__ import annotations

from img2vql.vdisplay_context import from_screen_context, reverse_generate


def test_from_screen_context_builds_program_metadata() -> None:
    program = from_screen_context(
        {
            "image_path": "/tmp/missing.png",
            "fingerprint": "deadbeef",
            "capture": {"width": 640, "height": 480, "display": ":0", "source": "vdisplay"},
            "environment": {"routing": {"selected_provider": "vision"}},
            "nl": "Chat application window.",
        }
    )
    payload = program.to_dict()
    assert payload["metadata"]["capture"]["width"] == 640
    assert payload["metadata"]["environment"]["routing"]["selected_provider"] == "vision"
    reverse = reverse_generate(program)
    assert reverse["nl"] == "Chat application window."
    assert reverse["canvas"]["width"] == 640
