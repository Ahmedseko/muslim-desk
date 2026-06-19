"""Tajweed color renderer for alquran.cloud 'quran-tajweed' edition.

The edition encodes rules as inline tags: [code[chars] or [code:id[chars]
These are parsed and converted to HTML colored spans.
"""
from __future__ import annotations
import re

# Rule code → (label_id, label_en, hex_color)
RULES: dict[str, tuple[str, str, str]] = {
    'o': ('Mad Munfasil',          'Madd Munfasil',         '#29B6F6'),  # light blue
    'n': ('Mad Muttasil',          'Madd Muttasil',          '#0288D1'),  # blue
    'p': ('Mad Arid Lissukun',     'Madd Arid',              '#81D4FA'),  # pale blue
    'm': ('Mad',                   'Madd',                   '#90CAF9'),  # blue-gray
    'q': ('Qalqalah',              'Qalqalah',               '#CE93D8'),  # purple
    'f': ('Ikhfa',                 'Ikhfa',                  '#FF9800'),  # orange
    'a': ('Idgham Bighunnah',      'Idgham with Ghunnah',    '#4CAF50'),  # green
    'd': ('Idgham Mutajanisain',   'Idgham Mutajanisain',    '#009688'),  # teal
    'g': ('Ghunnah',               'Ghunnah',                '#EF5350'),  # red
    'i': ('Iqlab',                 'Iqlab',                  '#E91E63'),  # pink
    'l': ('Lam',                   'Lam',                    '#FFC107'),  # amber
    'r': ("Ra'",                   "Ra'",                    '#FF6F00'),  # dark orange
    'h': ('Hamzat Wasl',           'Hamzat Wasl',            '#9E9E9E'),  # gray
}

# Codes shown in the legend (excluding hamza wasl which is subtle)
LEGEND_CODES = ['o', 'n', 'p', 'q', 'f', 'a', 'd', 'g', 'i']

_TAG_RE = re.compile(r'\[([a-z])(?::\d+)?\[([^\]]*)\]')


def to_html(tajweed_text: str, base_color: str = '#e2e8f0') -> str:
    """Convert tajweed-encoded text to HTML with inline color spans.

    Untagged characters keep the base_color; tagged characters get rule color.
    """
    def _replace(m: re.Match) -> str:
        code    = m.group(1)
        content = m.group(2)
        color   = RULES.get(code, ('', '', base_color))[2]
        return f'<span style="color:{color};">{content}</span>'

    return _TAG_RE.sub(_replace, tajweed_text)


def legend_html(lang: str = 'id') -> str:
    """Return a compact HTML string of colored rule names for the legend."""
    idx = 0 if lang == 'id' else 1
    parts: list[str] = []
    for code in LEGEND_CODES:
        name, _, color = RULES[code]
        label = RULES[code][idx]
        parts.append(
            f'<span style="color:{color}; white-space:nowrap;">■ {label}</span>'
        )
    return '&nbsp;&nbsp;'.join(parts)
