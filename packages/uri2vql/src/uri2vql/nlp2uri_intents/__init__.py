"""Registry of NL intent handlers."""

from __future__ import annotations

from uri2vql.nlp2uri_intents.imgl import IMGL_HANDLERS
from uri2vql.nlp2uri_intents.program import PROGRAM_HANDLERS
from uri2vql.nlp2uri_intents.window import WINDOW_HANDLERS
from uri2vql.nlp2uri_types import IntentHandler

INTENT_HANDLERS: list[IntentHandler] = [
    *IMGL_HANDLERS,
    *WINDOW_HANDLERS,
    *PROGRAM_HANDLERS,
]
