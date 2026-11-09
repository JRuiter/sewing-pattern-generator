"""Output language (option `language` / `--lang`): one central string table.

The code is written in English. Every text that ends up in an output file goes through
:func:`t` at the place where it is put together (piece labels, sewing steps, report rows,
diagram titles, …). With the language "en" `t` returns the text unchanged; with "de" it
looks the text up in the German table (``i18n_de.py``):

1. exact entry: ``"Side seam": "Seitennaht"``
2. number template: every number in the text is replaced by ``{n}``, e.g.
   ``"Press {n} cm to the inside."``; the numbers are put back in order (``{n1}``, ``{n2}``
   … for another order) and written with a decimal comma
3. pattern template with ``{s}`` slots for names that are translated on their own, e.g.
   ``"{s}: outline & seam allowance"``

Untranslated texts are passed through and recorded in :data:`MISSING` (the tests check that
the reference orders leave nothing behind). Construction value keys (``hip_width`` …) and
option names stay English.
"""
from __future__ import annotations

import re
from contextlib import contextmanager

LANGUAGES = ("en", "de")
_state = {"lang": "en"}
MISSING: set[str] = set()

_NUM = re.compile(r"(?<![\w.])[-−+]?\d+(?:[.,]\d+)?(?![\w])")
_tables: dict[str, tuple[dict, dict, list]] = {}


def check(lang: str | None) -> str:
    lang = (lang or "en").strip().lower()
    lang = {"deutsch": "de", "german": "de", "english": "en", "englisch": "en"}.get(lang, lang)
    if lang not in LANGUAGES:
        raise ValueError(f"language must be one of {', '.join(LANGUAGES)}")
    return lang


def set_language(lang: str | None) -> str:
    _state["lang"] = check(lang)
    return _state["lang"]


def lang() -> str:
    return _state["lang"]


def is_de() -> bool:
    return _state["lang"] == "de"


@contextmanager
def language(lang: str | None):
    old = _state["lang"]
    set_language(lang)
    try:
        yield
    finally:
        _state["lang"] = old


def _load(code: str):
    if code not in _tables:
        import i18n_de
        exact, templ = {}, {}
        pats = []
        for k, v in i18n_de.TABLE.items():
            if "{s}" in k:
                rx = "^" + re.escape(k).replace(r"\{s\}", "(.+?)").replace(r"\{n\}", r"([-−+]?\d+(?:[.,]\d+)?)") + "$"
                pats.append((re.compile(rx, re.S), k, v))
            elif "{n" in k:
                templ[k] = v
            else:
                exact[k] = v
        pats.sort(key=lambda p: -len(p[1]))       # most specific first
        for k, v in list(templ.items()):           # "{n} mm" and "{n} cm" share one entry
            ku, vu = _UNIT_RX.sub("{n} <u>", k), _UNIT_RX.sub("{n} <u>", v)
            if ku != k and ku.count("<u>") == vu.count("<u>"):
                _units[code].setdefault(ku, vu)
        _tables[code] = (exact, templ, pats)
        _values[code] = set(i18n_de.TABLE.values())
        _tvalues[code] = {re.sub(r"\{n\d*\}", "{n}", v).replace(",", ".") for v in i18n_de.TABLE.values()
                          if "{n" in v}
    return _tables[code]


_values: dict[str, set] = {}
_tvalues: dict[str, set] = {}
_units: dict[str, dict] = {"de": {}}
_UNIT_RX = re.compile(r"\{n\d*\} (?:mm|cm)\b")
_UNIT_TXT = re.compile(r"(?<![\w.])([-−+]?\d+(?:[.,]\d+)?) (mm|cm)\b")


def num(x: float | str, decimals: int | None = None) -> str:
    """A number in the output language (decimal comma in German)."""
    if isinstance(x, str):
        s = x
    elif decimals is None:
        s = f"{x:g}"
    else:
        s = f"{x:.{decimals}f}"
    return s.replace(".", ",") if is_de() else s


def _fill(template: str, numbers: list[str]) -> str:
    out, i = [], 0
    pos = 0
    for m in re.finditer(r"\{n(\d*)\}", template):
        out.append(template[pos:m.start()])
        idx = int(m.group(1)) - 1 if m.group(1) else i
        i += 1
        val = numbers[idx] if idx < len(numbers) else ""
        out.append(val.replace(".", ","))
        pos = m.end()
    out.append(template[pos:])
    return "".join(out)


def t(text: str) -> str:
    """Translate one output text into the current language."""
    if _state["lang"] == "en" or not text or not isinstance(text, str):
        return text
    exact, templ, pats = _load(_state["lang"])
    if text in exact:
        return exact[text]
    if text in _values[_state["lang"]]:          # already translated
        return text
    stripped = text.strip()
    if stripped != text and stripped in exact:
        return text.replace(stripped, exact[stripped])
    numbers = _NUM.findall(text)
    if numbers:
        key = _NUM.sub("{n}", text)
        if key in templ:
            return _fill(templ[key], numbers)
        ku = _UNIT_RX.sub("{n} <u>", key)
        if ku in _units.get(_state["lang"], {}):
            units = [u for _n, u in _UNIT_TXT.findall(text)]
            v = _units[_state["lang"]][ku]
            for u in units:
                v = v.replace("<u>", u, 1)
            return _fill(v, numbers)
    for rx, _k, v in pats:
        m = rx.match(text)
        if m:
            parts = list(m.groups())
            res, gi = [], 0
            pos = 0
            for mm in re.finditer(r"\{s\}|\{n\d*\}", v):
                res.append(v[pos:mm.start()])
                if gi < len(parts):
                    g = parts[gi]
                    res.append(t(g) if mm.group(0) == "{s}" else g.replace(".", ","))
                gi += 1
                pos = mm.end()
            res.append(v[pos:])
            return "".join(res)
    joined = _by_sentence(text)
    if joined is not None:
        return joined
    if numbers and _NUM.sub("{n}", text).replace(",", ".") in _tvalues.get(_state["lang"], ()):
        return text                               # already translated (a German number template)
    if _done(text) or ("; " in text and all(_done(p) for p in text.split("; "))):
        return text                               # already translated (joined parts, labels, prefixes)
    if _wordy(text):
        if text not in MISSING:
            _LAST.append(text)
        MISSING.add(text)
    return _DEC.sub(",", text)          # numbers without a table entry still get the decimal comma


def _done(part: str, depth: int = 0) -> bool:
    """A text that is already in the target language: a table value, a number template value,
    "<translated label>: <number> <unit>", a list of translated labels, or a translated {s}
    pattern (e.g. "Hose: …") whose slot is itself translated."""
    lang = _state["lang"]
    if part in _values[lang] or _NUM.sub("{n}", part).replace(",", ".") in _tvalues.get(lang, ()):
        return True
    m = re.fullmatch(r"(.+): [-−+]?[\d.,]+ ?(?:cm|mm|in|″)?", part)
    if m:
        return _done(m.group(1), depth)
    items = _top_level_split(part)
    if len(items) > 1 and all(_done(x, depth) for x in items):
        return True
    if depth < 2:
        for rx in _rev_pats(lang):
            mm = rx.match(part)
            if mm and all(_done(g, depth + 1) for g in mm.groups()):
                return True
    return False


def _top_level_split(text: str) -> list[str]:
    """Split at ", " outside parentheses."""
    out, buf, depth = [], "", 0
    i = 0
    while i < len(text):
        c = text[i]
        depth += (c == "(") - (c == ")")
        if depth == 0 and text.startswith(", ", i):
            out.append(buf)
            buf = ""
            i += 2
            continue
        buf += c
        i += 1
    return out + [buf]


_REV: dict[str, list] = {}


def _rev_pats(lang: str) -> list:
    """The {s} patterns matched against their translations (only those with {s} slots and no {n})."""
    if lang not in _REV:
        _REV[lang] = [re.compile("^" + re.escape(v).replace(r"\{s\}", "(.+?)") + "$", re.S)
                      for _rx, k, v in _load(lang)[2] if "{n" not in v and v.count("{s}") >= 1 and v != "{s}"]
    return _REV[lang]


_SENT = (re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9„\"(])"),           # sentences first,
         re.compile(r"(?<=[.;!?])\s+(?=[A-Za-z0-9„\"(])"))      # then also the parts of a sentence


def _by_sentence(text: str) -> str | None:
    """A text of several sentences without an entry of its own: translate it sentence by sentence
    (then, if needed, split at ";" too; such a part is looked up with a full stop). None unless every
    part has an entry, so step texts that combine known sentences (e.g. with or without an overlocker)
    need no entry of their own."""
    for rx in _SENT:
        parts = rx.split(text.strip())
        if len(parts) < 2:
            continue
        n = len(MISSING)
        out = []
        for p in parts:
            semi = p.endswith(";")
            tr = t(p[:-1] + "." if semi else p)
            if len(MISSING) > n:
                _undo(n, None)
                out = []
                break
            out.append(tr[:-1] + ";" if semi and tr.endswith(".") else tr)
        if out:
            return " ".join(out)
    return None


def _undo(n: int, value):
    """Forget the sentences recorded as missing while trying the sentence-wise translation."""
    while len(MISSING) > n and _LAST:
        MISSING.discard(_LAST.pop())
    return value


_LAST: list[str] = []          # missing texts in the order they were recorded (for _undo)


_DEC = re.compile(r"(?<=\d)\.(?=\d)")


_UNITS = re.compile(r"\b(cm|mm|m|in|yd|pt|ok|OK|px|A4|A0|A1)\b")


def _wordy(text: str) -> bool:
    """Does the text contain words (not just numbers, units and symbols)?"""
    rest = _UNITS.sub("", _NUM.sub("", re.sub(r"`[^`]*`|\w*_\w*", "", text)))
    return bool(re.search(r"[A-Za-z]{2,}", rest))


def tl(texts):
    return [t(x) for x in texts]


def localize_pattern(pat) -> None:
    """Translate the display texts of a drafted pattern in place (names, labels, notes …).

    The English originals stay available where code looks things up by them:
    ``piece.fabric_key`` (fabric groups of the cutting layout) and ``mark.key``. Seam names
    (``pattern.seams``) stay English; they are translated where they are shown."""
    if not is_de() or getattr(pat, "_localized", False):
        return
    pat.title = t(pat.title)
    pat.size_label = t(pat.size_label)
    for pc in pat.pieces:
        pc.fabric_key = getattr(pc, "fabric_key", None) or pc.fabric
        pc.name = t(pc.name)
        pc.fabric = t(pc.fabric)
        pc.stretch_dir = t(pc.stretch_dir)
        pc.info = [t(i) for i in pc.info]
        for e in pc.edges:
            e.label = t(e.label)
        for m in pc.marks:
            m.key = getattr(m, "key", None) or m.label
            m.label = t(m.label)
    pat.notes_en = list(pat.notes)
    pat.notes = [t(n) for n in pat.notes]
    pat._localized = True


# file names of the outputs
FILE_NAMES = {
    "de": {
        "validation_report.md": "pruefbericht.md", "sewing_instructions.md": "naehanleitung.md",
        "sewing_instructions.pdf": "naehanleitung.pdf", "cutting_layout.png": "zuschnittplan.png",
        "pattern.json": "schnitt.json", "body_measurements.smis": "koerpermasse.smis", "steps": "schritte",
        "_master_1to1.svg": "_master_1zu1.svg", "_preview.png": "_vorschau.png", "_tiled.pdf": "_kleben.pdf",
        "_roll": "_rolle", "_strips.pdf": "_streifen.pdf", "_projector": "_beamer", "_dark": "_dunkel",
        "size": "gr", "_sizes_": "_groessen_", "step_": "schritt_",
    },
}


def fname(name: str) -> str:
    """Output file name (or name part) in the current language."""
    return FILE_NAMES.get(_state["lang"], {}).get(name, name)
