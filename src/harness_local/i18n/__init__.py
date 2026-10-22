"""Catalogs of the service's own messages (P011-T007, D166).

English is the base and the fallback. A key names a complete message; parameters are plain `{name}` fields,
never expressions or fragments of another message. Codes, states and original evidence are not translated here.
"""
from functools import cache
from importlib.resources import files
import json
import re

LANGUAGES = ('en', 'es')
DEFAULT_LANGUAGE = 'en'
PARAMETER = re.compile(r'\{([a-z_][a-z0-9_]*)\}')


@cache
def catalog(language: str) -> dict[str, str]:
    return json.loads(files(__package__).joinpath(f'{language}.json').read_text(encoding='utf-8'))


def supported(language) -> str:
    """The language itself if valid; otherwise the English fallback."""
    return language if language in LANGUAGES else DEFAULT_LANGUAGE


def message(key: str, language, /, **params) -> str:
    """Localized text; a missing translation falls back to English and a missing key returns the key itself.

    An absent parameter keeps its `{name}` field visible: nothing is evaluated and no other value is revealed.
    """
    text = catalog(supported(language)).get(key) or catalog(DEFAULT_LANGUAGE).get(key)
    if text is None:
        return key
    return PARAMETER.sub(lambda match: str(params[match[1]]) if match[1] in params else match[0], text)
