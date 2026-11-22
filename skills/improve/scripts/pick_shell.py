#!/usr/bin/env python3
"""Pick shell: the list + reader page layout for pick pages (here: the /improve findings page).

Part of the /improve skill (scripts/ folder).
Loaded by absolute path like blocks.py (python3 -I blocks sibling imports; VISUAL_BLOCKS_DIR swaps the folder):
    d = os.environ.get("VISUAL_BLOCKS_DIR") or os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location("pick_shell", os.path.join(d, "pick_shell.py"))
    ps = importlib.util.module_from_spec(spec); spec.loader.exec_module(ps)
It loads blocks.py from its own folder. Each builder keeps its own parsing and its own copy-back (export) code:
the shell only lays out the cards it is given and never builds the paste-back text.

Page: every card listed on the left (pick, picture kind, status), the chosen card in full on the right, the
builder's copy box under the list, progress "N of M looked at, K to discuss", keys (arrows or J/K move; one
letter per mark, e.g. A accept, D discuss; N note). A card counts as looked at once it was shown.
Card: headline, picture, 2 to 4 bullets, pick bar, one Details fold, marks. The card element is
<article class="card pc" id="<item id>" data-pick="<preset>">, with radios named "<prefix>-<id>" and one
input.note, so the builders' existing export code (which reads .card, its checked radio and .note) runs unchanged.
Untouched cards stay on the pre-set mark (my pick).
Standard library only (blocks.shot imports Pillow itself).
"""
import html
import importlib.util
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))


def _load_blocks():
    spec = importlib.util.spec_from_file_location("visual_blocks", os.path.join(HERE, "blocks.py"))
    vb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vb)
    return vb


VB = _load_blocks()
LIMIT = 140          # a bullet longer than this splits (about 2 lines in the reader pane at 900 px)
PICTURE_KEYS = ("shots", "table", "ta", "options", "expected_actual", "picture", "drop_seen", "compact", "headline")


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def inline(s):
    return VB.inline(s)


def flat(v):
    """A list (nested allowed) as one ' · ' line; a string as it is."""
    if isinstance(v, (list, tuple)):
        return " · ".join(flat(x) for x in v)
    return "" if v is None else str(v)


def fields(item):
    """The item's fields with a 'compact' block (an older nesting) laid over the flat ones."""
    cp = item.get("compact")
    return dict(item, **cp) if isinstance(cp, dict) else dict(item)


# ---------- text: sentences to bullets ----------

def sentences(s):
    s = re.sub(r"\bPat\. ", "Pat⁣", str(s or ""))   # keep a label such as 'Verlauf (Pat. Protokolle)' whole
    return [x.replace("Pat⁣", "Pat. ").strip() for x in re.split(r"(?<=[.!?])\s+(?=[A-Z'#\"(0-9])", s) if x.strip()]


def top_split(s, sep):
    """Split at sep outside parentheses."""
    out, depth, cur, i = [], 0, "", 0
    while i < len(s):
        ch = s[i]
        depth += ch == "("
        depth -= ch == ")"
        if depth == 0 and s.startswith(sep, i):
            out.append(cur)
            cur, i = "", i + len(sep)
            continue
        cur += ch
        i += 1
    return [x.strip() for x in out + [cur] if x.strip()]


def split_long(s, depth=0):
    """A sentence over LIMIT -> bullet items: first at '; ' (siblings), else at ': ' (head + sub-bullets),
    else at ', ' (first part + sub-bullets); all outside parentheses."""
    if len(s) <= LIMIT or depth > 2:
        return [s]
    parts = top_split(s, "; ")
    if len(parts) > 1:
        out = []
        for p in parts:
            out += split_long(p, depth + 1)
        return out
    parts = top_split(s, ": ")
    if len(parts) > 1:
        rest = ": ".join(parts[1:])
        return [parts[0] + ":", split_long(rest, depth + 1) if len(rest) > LIMIT else [rest]]
    parts = top_split(s, ", ")
    if len(parts) > 1:
        return [parts[0], parts[1:]]
    return [s]


def bullet(label, text, drop=()):
    """'**Label:** text' as one bullet, or the label with one sub-bullet per sentence (long ones split again).
    drop: sentence starts to leave out (the picture already shows them)."""
    if not text:
        return []
    if isinstance(text, (list, tuple)):
        if len(text) == 1 and isinstance(text[0], str) and len(text[0]) <= LIMIT:
            return [f"**{label}:** {text[0]}"]
        return [f"**{label}:**", [x if isinstance(x, (list, tuple)) else str(x) for x in text]]
    sents = [x for x in sentences(text) if not any(x.startswith(d) for d in drop or ())]
    if not sents:
        return []
    if len(sents) == 1 and len(sents[0]) <= LIMIT:
        return [f"**{label}:** {sents[0]}"]
    sub = []
    for x in sents:
        sub += split_long(x)
    return [f"**{label}:**", sub]


STORY_BULLETS = (("saw", "Seen"), ("problem", "Problem"), ("fix", "Fix"), ("change", "For users"))


def story_bullets(story, drop=(), skip=()):
    """The story dict (saw / problem / fix / change) as 2 to 4 bullets; a plain string as one 'Story' bullet.
    A 'change' line that already names users shows without the 'For users' label."""
    if isinstance(story, dict):
        out = []
        for k, label in STORY_BULLETS:
            v = story.get(k)
            if not v or k in skip:
                continue
            if k == "change" and isinstance(v, str) and "user" in v.lower():
                out.append(v)
            else:
                out += bullet(label, v, drop if k == "saw" else ())
        return out
    return bullet("Story", story) if story else []


# ---------- verbatim check ----------

def own_text(item, skip=PICTURE_KEYS):
    """All of the item's own words (every field but the picture fields), lower case, spaces collapsed."""
    def walk(v):
        if isinstance(v, dict):
            return " ".join(walk(x) for x in v.values())
        if isinstance(v, (list, tuple)):
            return " ".join(walk(x) for x in v)
        return "" if v is None or isinstance(v, bool) else str(v)
    return norm(" ".join(walk(v) for k, v in item.items() if k not in skip))


def norm(s):
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def verbatim(cid, text, haystack, where, warn):
    if text and norm(text) not in haystack:
        warn.append(f"{cid}: '{text}' ({where}) is not in the item's own text")


# ---------- pictures ----------

def ta_block(cid, rows, item, warn):
    """rows: [[label, [field, excerpt], [field, excerpt]]]: Today -> After my pick, key words only.
    field: a story part (saw, problem, fix, change) or a top-level field (ask, title, before, after ...)."""
    story = item.get("story") if isinstance(item.get("story"), dict) else {}
    src = {k: flat(v) for k, v in item.items() if k not in PICTURE_KEYS and not isinstance(v, dict)}
    src.update({k: flat(v) for k, v in story.items()})
    out = ['<div class="vb-ba pc-ba"><span class="vb-bah"></span><span class="vb-bah">Today</span><span></span>'
           '<span class="vb-bah">After my pick</span>']
    for r in rows or []:
        if not isinstance(r, (list, tuple)) or len(r) < 3:
            warn.append(f"{cid}: a 'ta' row needs [label, [field, excerpt], [field, excerpt]]")
            continue
        label, cells = r[0], []
        for side in r[1:3]:
            f, t = (list(side) + ["", ""])[:2] if isinstance(side, (list, tuple)) else ("", side)
            if t and norm(t) not in norm(src.get(f, "")):
                warn.append(f"{cid}: '{t}' is not in the item's '{f}'")
            cells.append((f, t))
        (f1, t1), (f2, t2) = cells
        out.append(f'<span class="vb-bat">{inline(label)}</span>'
                   f'<div class="vb-bab" title="{esc(src.get(f1, ""))}">{inline(t1) or "—"}</div>'
                   f'<span class="vb-baa">→</span>'
                   f'<div class="vb-baf" title="{esc(src.get(f2, ""))}">{inline(t2) or "—"}</div>')
    out.append('</div><div class="pc-cap">Key words from the card; hover a box for the full sentence '
               '(also in the bullets and Details).</div>')
    return "".join(out)


MARK_LEGEND = {"ok": "✓ yes, passed or meets", "mid": "~ partly, open or not tested", "no": "✗ no or misses"}


def table_block(cid, t, haystack, warn):
    """t: {"caption", "head": [...], "rows": [[cell, ...]], "legend" (optional)}; a cell is a string or
    {"t": text, "m": "ok|no|mid"}. The legend lists only the marks the rows use."""
    head = "".join(f"<th>{inline(h)}</th>" for h in t.get("head") or [])
    rows, used = [], []
    for r in t.get("rows") or []:
        tds = []
        for c in (r if isinstance(r, (list, tuple)) else [r]):
            text, mark = (c.get("t", ""), c.get("m", "")) if isinstance(c, dict) else (c, "")
            verbatim(cid, text, haystack, "table cell", warn)
            cls = ""
            if mark in ("ok", "no", "mid"):
                cls = f' class="vb-{mark}"'
                if mark not in used:
                    used.append(mark)
            tds.append(f"<td{cls}>{inline(text)}</td>")
        rows.append(f"<tr>{''.join(tds)}</tr>")
    cap = f'<div class="vb-lab">{inline(t["caption"])}</div>' if t.get("caption") else ""
    legend = t.get("legend") or " · ".join(MARK_LEGEND[m] for m in ("ok", "mid", "no") if m in used)
    legend = f'<div class="pc-cap">{inline(legend)}</div>' if legend else ""
    return (f'{cap}<table class="vb-opt pc-tab"><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>{legend}')


def list_block(saw):
    """A card whose point is a list: the 'saw' text as numbered points ('1) ... 2) ...', or sentences)."""
    if isinstance(saw, (list, tuple)):
        items = list(saw)
    else:
        parts = [p.strip() for p in re.split(r"(?:^|\s)\d\)\s", str(saw or "")) if p.strip()]
        if len(parts) < 2:
            parts = sentences(saw)
        items = []
        for p in parts:
            sub = top_split(p, "; ")
            items += [sub[0]] + ([sub[1:]] if len(sub) > 1 else [])
    return '<div class="vb-lab">What you should know</div>' + VB.bullets(items, ordered=True)


PIC_ICON = {"Screenshot": "▣", "Table": "▤", "Today → After": "⇢", "List": "☰", "Change": "±", "Options": "▤",
            "Expected vs actual": "◐"}


def picture(cid, item, resolve=None, warn=None):
    """The card's picture: shots, else table, else ta (Today -> After), else picture: list; then expected_actual
    and options. Returns (kind, html); kind '' when the card has none."""
    warn = warn if warn is not None else []
    f = fields(item)
    story = f.get("story") if isinstance(f.get("story"), dict) else {}
    kind, out = "", []
    shots = [s for s in f.get("shots") or [] if isinstance(s, dict) and s.get("path")]
    if shots:
        kind = "Screenshot"
        out += [VB.shot(resolve(s["path"]) if resolve else s["path"], s.get("crop"), s.get("marks"),
                        s.get("caption", "")) for s in shots]
    elif isinstance(f.get("table"), dict) and f["table"].get("rows"):
        kind = "Table"
        out.append(table_block(cid, f["table"], own_text(item), warn))
    elif f.get("ta"):
        kind = "Today → After"
        out.append(ta_block(cid, f["ta"], item, warn))
    elif f.get("picture") == "list" and story.get("saw"):
        kind = "List"
        out.append(list_block(story["saw"]))
    if f.get("expected_actual"):
        kind = kind or "Expected vs actual"
        out.append(VB.expected_actual(f["expected_actual"]))
    o = f.get("options")
    if isinstance(o, dict) and o.get("names"):
        rows = [r for r in o.get("rows") or [] if isinstance(r, (list, tuple)) and len(r) > 1]
        if rows:
            kind = kind or "Options"
            out.append(VB.option_table(o["names"], rows, o.get("pick")))
    return kind, "".join(out)


def has_picture_field(item):
    """True when the card has a picture, or says it has none on purpose (picture: none|list)."""
    f = fields(item)
    return any(f.get(k) for k in ("shots", "table", "ta", "options", "expected_actual")) or \
        f.get("picture") in ("none", "list")


# ---------- one card ----------

def details(rows):
    """[(label, html)] -> one 'Details: a, b, c' fold; empty values left out."""
    rows = [(k, v) for k, v in rows if v]
    if not rows:
        return ""
    names = ", ".join(k.lower() for k, _ in rows)
    body = "".join(f"<div><b>{esc(k)}:</b> {v}</div>" for k, v in rows)
    return f'<details class="pc-more"><summary>Details: {esc(names)}</summary><div class="pc-foot">{body}</div></details>'


def text_html(v):
    """A string -> inline HTML; a list -> bullets."""
    if isinstance(v, (list, tuple)):
        return VB.bullets(list(v))
    return inline(v)


def marks_html(cid, prefix, marks, default):
    """marks: [(value, label, symbol, key)]."""
    out = [f'<div class="pc-marks mark" role="group" aria-label="Your mark for {esc(cid)}"><span class="pc-your">Your mark</span>']
    for val, lab, sym, key in marks:
        chk = " checked" if val == default else ""
        out.append(f'<label class="mk mk-{esc(val)}"><input type="radio" name="{esc(prefix)}-{esc(cid)}" value="{esc(val)}"{chk}>'
                   f'<span>{esc(sym)} {esc(lab)}<kbd>{esc(key)}</kbd></span></label>')
    out.append(f'<input class="note" type="text" placeholder="note (optional)" aria-label="Note for {esc(cid)}">'
               f'<span class="pc-preset">pre-set to my pick until you mark it</span></div>')
    return "".join(out)


def card(cid, *, kick="", headline="", title="", pic="", bullets=None, pick="", pick_sub="", details_rows=(),
         marks=(), prefix="m", default="accept", extra_class="", top=""):
    """One card as HTML. kick: the small line above the headline (HTML); pic: picture HTML; bullets: a list for
    blocks.bullets; pick: my pick (HTML); pick_sub: the line under it (HTML); top: HTML right under the headline
    (a builder's own block, such as the /improve change)."""
    sub = f'<div class="pc-title">{inline(title)}</div>' if title and title != headline else ""
    bl = f'<div class="pc-bul">{VB.bullets(bullets)}</div>' if bullets else ""
    bar = (f'<div class="pc-pick"><div><span class="pc-star">★ My pick</span> <b>{pick}</b></div>'
           + (f'<div class="pc-sub">{pick_sub}</div>' if pick_sub else "") + "</div>") if pick else ""
    return (f'<article class="card pc{(" " + extra_class) if extra_class else ""}" id="{esc(cid)}" data-pick="{esc(default)}">'
            f'<div class="pc-kick">{kick}</div>{sub}<h2 class="pc-h">{inline(headline or title)}</h2>'
            f'{top}{pic}{bl}{bar}{details(details_rows)}{marks_html(cid, prefix, marks, default)}</article>')


# ---------- page ----------

def css():
    return VB.css() + CSS


CSS = r"""
:root{--acc:#2563eb;--ok:#1f7a3f;--bad:#b42318;--amb:#a15c00;--line:#d9dee5;--mut:#5f6b7a;--bg:#f6f7f9}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--bg);font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;color:#1d2330;overflow:hidden}
button{font:inherit;cursor:pointer}
kbd{font:600 10.5px ui-monospace,Menlo,monospace;border:1px solid #c9d0d9;border-bottom-width:2px;border-radius:4px;padding:0 4px;margin-left:6px;color:#5f6b7a;background:#fff}
.bw{display:grid;grid-template-columns:350px minmax(0,1fr);height:100vh}
.side{display:flex;flex-direction:column;background:#fff;border-right:1px solid var(--line);min-height:0}
.side-h{padding:10px 14px 8px;border-bottom:1px solid var(--line)}
.side-h .t{font-weight:700;font-size:14.5px;margin-bottom:4px}
.pg{display:grid;grid-template-columns:1fr 64px;gap:8px;align-items:center;font-size:13.5px;margin:2px 0}
.pg-bar{display:inline-block;width:64px;height:8px;border-radius:4px;background:#e3e7ec;overflow:hidden}
.pg-bar i{display:block;height:100%;width:0;background:var(--ok)}
.side-h .k{font-size:12px;color:var(--mut);margin-top:4px}
.list{flex:1;overflow:auto;min-height:0}
.lg{position:sticky;top:0;background:#f1f4f8;font-size:11.5px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--mut);padding:5px 14px;border-bottom:1px solid var(--line);z-index:1}
.li{scroll-margin-top:30px;display:grid;grid-template-columns:42px minmax(0,1fr);gap:2px 6px;padding:8px 12px 8px 14px;border:0;border-bottom:1px solid #eef1f4;cursor:pointer;width:100%;text-align:left;background:#fff;font-size:13.5px;line-height:1.35}
.li:hover{background:#f7f9fc}
.li.cur{background:#eef4ff;box-shadow:inset 4px 0 var(--acc)}
.li .num{font:600 12px/1.6 ui-monospace,Menlo,monospace;color:var(--mut);overflow-wrap:anywhere}
.li .tt{color:#1d2330;overflow-wrap:anywhere}
.li .mt{grid-column:2;display:flex;flex-wrap:wrap;gap:4px 6px;margin-top:3px;align-items:center}
.chip{font-size:11.5px;border-radius:4px;padding:1px 6px;background:#eef4ff;color:#1e40af;overflow-wrap:anywhere}
.chip.pic{background:#f1f4f8;color:#46505e}
.st{font-size:11.5px;font-weight:700;border-radius:4px;padding:1px 6px;white-space:nowrap}
.st-open{border:1px dashed #9aa4b2;color:var(--mut)}
.st.pre{border:1px dashed currentColor}
.st-accept{background:#e8f5ec;color:var(--ok)}.st-discuss,.st-flag{background:#fff4e0;color:var(--amb)}.st-skip{background:#eef1f4;color:#46505e}
.side-copy{border-top:2px solid var(--line);padding:8px 12px 10px;background:#fafbfc}
.side-copy button{background:var(--acc);color:#fff;border:0;border-radius:8px;padding:7px 14px;font-weight:600;font-size:14px;margin-right:8px}
.side-copy #cnt{font-size:13px;color:var(--mut)}
.side-copy textarea{display:block;width:100%;height:52px;margin-top:6px;font:12px/1.4 ui-monospace,Menlo,monospace;border:1px solid #c9d0d9;border-radius:6px;padding:6px;resize:vertical}
.pane{overflow:auto;min-height:0;padding:16px 24px 24px}
.pane-in{max-width:940px;margin:0 auto}
.pane-nav{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:0 0 10px;font-size:13px;color:var(--mut)}
.pane-nav button{border:1px solid #c9d0d9;background:#fff;border-radius:8px;padding:5px 12px;font-size:13.5px}
.intro{display:none;background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 18px;margin:0 0 14px;font-size:14px;overflow-wrap:anywhere}
.intro.show{display:block}
.intro h1{font-size:18px;margin:2px 0 6px;line-height:1.3}
.intro ul.vb-ul{margin:4px 0 8px}
.in-kick{font-size:12px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--acc)}
.in-counts{font-weight:600;margin:4px 0}
.in-built{font-size:12px;color:var(--mut)}
.in-due{border:1px solid #f0a050;background:#fff6ea;border-radius:8px;padding:8px 12px;margin:6px 0}
.in-msgs{border-collapse:collapse;font-size:12.5px;width:100%}.in-msgs td,.in-msgs th{border:1px solid var(--line);padding:3px 5px;text-align:left;vertical-align:top}
.pc{display:none;background:#fff;border:1px solid var(--line);border-radius:12px;padding:18px 22px 0;container-type:inline-size;overflow-wrap:anywhere}
.pc.show{display:block}
.pc.discussing,.pc.flagged{border:2px solid #d97706}
.pc-kick{display:flex;flex-wrap:wrap;gap:4px 10px;align-items:center;font-size:12px;font-weight:700;letter-spacing:.04em;color:var(--acc)}
.pc-id{font-family:ui-monospace,Menlo,monospace;background:#eef4ff;border-radius:4px;padding:0 6px}
.pc-grp{color:var(--mut);font-weight:600;letter-spacing:0}
.pc-file{font:12px ui-monospace,Menlo,monospace;color:var(--mut);font-weight:400}
.pc-title{font-size:13.5px;color:var(--mut);margin-top:4px}
.pc-h{font-size:20px;line-height:1.3;margin:6px 0 8px}
.pc-bul{font-size:14.5px;margin:10px 0 0}
.pc-bul ul.vb-ul{margin:2px 0;padding-left:20px}.pc-bul li{margin:3px 0}
.pc-bul ul.vb-ul ul.vb-ul{color:#46505e}
.pc-ba{grid-template-columns:minmax(80px,.45fr) 1fr 22px 1fr}
.pc-ba .vb-bab,.pc-ba .vb-baf{cursor:help;font-weight:600}
.pc-cap{font-size:12px;color:var(--mut);margin:2px 0 4px}
.pc-tab td,.pc-tab th{padding:5px 9px;white-space:normal}
.vb-shot{max-width:900px}
.pc-pick{background:#eef4ff;border-left:4px solid var(--acc);border-radius:8px;padding:10px 14px;margin:14px 0 8px;font-size:14px}
.pc-star{color:var(--acc);font-weight:700;font-size:12px;letter-spacing:.05em;text-transform:uppercase;margin-right:4px}
.pc-pick b{font-size:16px}
.pc-sub{font-size:13px;color:#46505e;margin-top:3px}
.pc-sub ul{margin:2px 0;padding-left:20px}
.pc-badge{font-size:11.5px;background:#e0f2f1;color:#00695c;border-radius:4px;padding:1px 6px;font-weight:600;letter-spacing:0}
.pc-badge.plan{background:#fff3cd;color:#7a5600;border:1px solid #e0c060}
.pc-more{margin-top:10px}
.pc-more summary{font-size:13px;color:var(--mut);cursor:pointer}
.pc-foot{font-size:12.5px;color:var(--mut);margin-top:4px}
.pc-foot>div{margin:2px 0}.pc-foot b{color:#46505e;font-weight:600}
.pc-foot ul{margin:2px 0;padding-left:18px}
.pc-marks{position:sticky;bottom:-24px;z-index:2;background:#fff;display:flex;flex-wrap:wrap;gap:8px 10px;align-items:center;margin-top:12px;padding:12px 0 14px;border-top:1px solid var(--line)}
.pc-your{font-size:12px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--mut)}
.mk{position:relative}
.mk input{position:absolute;opacity:0;width:1px;height:1px}
.mk span{display:inline-flex;align-items:center;border:1.5px solid #c9d0d9;border-radius:999px;padding:6px 14px;font-weight:600;font-size:14px;cursor:pointer;background:#fff;color:#46505e}
.mk input:focus-visible+span{outline:3px solid var(--acc);outline-offset:2px}
.mk-accept input:checked+span{background:#e8f5ec;border-color:var(--ok);color:var(--ok)}
.mk-discuss input:checked+span,.mk-flag input:checked+span{background:#fff4e0;border-color:#d97706;color:var(--amb)}
.mk-skip input:checked+span{background:#eef1f4;border-color:#5f6b7a;color:#46505e}
.pc:not([data-touched]) .mk input:checked+span{border-style:dashed}
.pc-marks .note{flex:1;min-width:200px;padding:7px 10px;border:1px solid #c9d0d9;border-radius:8px;font-size:14px}
.pc-preset{font-size:12px;color:var(--mut);flex-basis:100%}
.pc[data-touched] .pc-preset{display:none}
pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.55 ui-monospace,Menlo,monospace;margin:4px 0;padding:8px 10px;border-radius:8px}
@container (max-width:640px){
 .vb-ba{grid-template-columns:1fr 18px 1fr}.vb-ba>span:nth-child(-n+4){display:none}.vb-bat{grid-column:1/-1;margin-top:6px}
}
@media (max-width:1000px){.bw{grid-template-columns:300px minmax(0,1fr)}.pane{padding:12px 14px 20px}.pc{padding:14px 16px 0}}
@media (max-width:700px){body{overflow:auto}.bw{display:block;height:auto}.side{max-height:none}.list{max-height:40vh}
 .side-copy{position:sticky;bottom:0;z-index:3}.pane{overflow:visible}.pc-marks{bottom:0}}
"""

JS = r"""
(function () {
const CARDS = Array.from(document.querySelectorAll('.pane .pc'));
const LIS = Array.from(document.querySelectorAll('.li'));
const HOT = __HOT__, HOT_WORD = __HOT_WORD__, KEYS = __KEYS__, LAB = __LAB__;
const val = c => (c.querySelector('input[type=radio]:checked') || {}).value;
let cur = 0;
function refresh() {
  const seen = CARDS.filter(c => c.dataset.seen).length;
  const hot = CARDS.filter(c => HOT.includes(val(c))).length;
  document.querySelectorAll('.pg-n').forEach(e => e.textContent = seen + ' of ' + CARDS.length + ' looked at, ' + hot + ' ' + HOT_WORD);
  document.querySelectorAll('.pg-bar i').forEach(e => e.style.width = (CARDS.length ? 100 * seen / CARDS.length : 0) + '%');
  CARDS.forEach((c, j) => {
    const e = LIS[j] && LIS[j].querySelector('.st');
    if (!e) return;
    const v = val(c);
    if (!c.dataset.seen && !c.dataset.touched) { e.className = 'st st-open'; e.textContent = '○ open'; return; }
    e.className = 'st st-' + v + (c.dataset.touched ? '' : ' pre');
    e.textContent = (LAB[v] || v) + (c.dataset.touched ? '' : ' (pre-set)');
  });
}
function sel(k) {
  cur = Math.max(0, Math.min(CARDS.length - 1, k));
  CARDS.forEach((c, j) => c.classList.toggle('show', j === cur));
  LIS.forEach((l, j) => l.classList.toggle('cur', j === cur));
  const intro = document.querySelector('.pane .intro');
  if (intro) intro.classList.toggle('show', cur === 0);
  if (!CARDS.length) return;
  CARDS[cur].dataset.seen = '1';
  document.getElementById('pos').textContent = 'Card ' + (cur + 1) + ' of ' + CARDS.length + ' · ' + CARDS[cur].id;
  LIS[cur].scrollIntoView({block: 'nearest'});
  document.querySelector('.pane').scrollTop = 0;
  refresh();
}
document.addEventListener('change', e => {
  const c = e.target.closest && e.target.closest('.pc');
  if (c && e.target.type === 'radio') c.dataset.touched = '1';
  refresh();
});
document.addEventListener('input', refresh);
function setMark(c, v) {
  const r = c && c.querySelector('input[type=radio][value="' + v + '"]');
  if (!r) return false;
  r.checked = true; r.dispatchEvent(new Event('change', {bubbles: true})); return true;
}
function typing(e) { const t = e.target; return t && (t.tagName === 'INPUT' && t.type === 'text' || t.tagName === 'TEXTAREA'); }
LIS.forEach((l, j) => l.addEventListener('click', () => sel(j)));
document.getElementById('prev').addEventListener('click', () => sel(cur - 1));
document.getElementById('next').addEventListener('click', () => sel(cur + 1));
document.addEventListener('keydown', e => {
  if (e.metaKey || e.ctrlKey || e.altKey || !CARDS.length) return;
  const c = CARDS[cur];
  if (typing(e)) { if (e.key === 'Enter' || e.key === 'Escape') { e.target.blur(); if (e.key === 'Enter') sel(cur + 1); } return; }
  const k = e.key.toLowerCase();
  if (k === 'arrowdown' || k === 'j' || k === 'arrowright') { sel(cur + 1); e.preventDefault(); }
  else if (k === 'arrowup' || k === 'k' || k === 'arrowleft') { sel(cur - 1); e.preventDefault(); }
  else if (k === 'n') { c.querySelector('.note').focus(); e.preventDefault(); }
  else if (KEYS[k]) {
    const [v, next] = KEYS[k];
    if (setMark(c, v)) { if (next) sel(cur + 1); else { c.querySelector('.note').focus(); e.preventDefault(); } }
  }
});
sel(0);
})();
"""


def list_item(entry):
    """entry: {"id", "title", "pick" (text), "pic" (kind or '')}."""
    pic = entry.get("pic")
    return (f'<button class="li" type="button" data-id="{esc(entry["id"])}"><span class="num">{esc(entry["id"])}</span>'
            f'<span class="tt">{inline(entry.get("title", ""))}</span><span class="mt">'
            f'<span class="chip" title="My pick">★ {inline(entry.get("pick", ""))}</span>'
            + (f'<span class="chip pic" title="This card has a picture">{PIC_ICON.get(pic, "▣")} {esc(pic)}</span>' if pic else "")
            + '<span class="st st-open">○ open</span></span></button>')


def page(title, *, intro, groups, copy_html, export_js, marks, hot=("discuss",), hot_word="to discuss",
         side_title="", extra_css="", lang="en"):
    """The whole page.
    groups: [(group name, [entry])], entry = {"id", "title", "pick", "pic", "html" (from card())}; cards keep
    the order given (the builders' old order, so the copy-back text lists ids as before).
    copy_html: the builder's copy button, count span and textarea (its old ids); export_js: the builder's own
    export script, unchanged. marks: [(value, label, symbol, key, next)]: key letter per mark; next=True moves on
    after marking, False puts the cursor in the note."""
    entries = [e for _, es in groups for e in es]
    lst = "".join(f'<div class="lg">{esc(name)} ({len(es)})</div>' + "".join(list_item(e) for e in es)
                  for name, es in groups if es)
    keys = {m[3].lower(): [m[0], bool(m[4])] for m in marks}
    lab = {m[0]: f"{m[2]} {m[1]}" for m in marks}
    key_line = " · ".join(f"{m[3]} {m[1].lower()}" for m in marks)
    js = (JS.replace("__HOT__", json.dumps(list(hot))).replace("__HOT_WORD__", json.dumps(hot_word))
          .replace("__KEYS__", json.dumps(keys)).replace("__LAB__", json.dumps(lab, ensure_ascii=False)))
    return (f'<!doctype html><html lang="{esc(lang)}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title>'
            f'<style>{css()}{extra_css}</style></head><body class="vb">'
            f'<div class="bw"><aside class="side"><div class="side-h"><div class="t">{esc(side_title or title)}</div>'
            f'<div class="pg"><span class="pg-t"><span class="pg-n"></span></span><span class="pg-bar"><i></i></span></div>'
            f'<div class="k">Keys: ↑ ↓ or J K move · {esc(key_line)} · N note</div></div>'
            f'<nav class="list">{lst}</nav><div class="side-copy">{copy_html}</div></aside>'
            f'<section class="pane"><div class="pane-in"><div class="pane-nav"><button id="prev" type="button">← Previous</button>'
            f'<span id="pos"></span><button id="next" type="button">Next →</button></div>{intro}'
            f'{"".join(e["html"] for e in entries)}</div></section></div>'
            f'<script>{export_js}</script><script>{js}</script></body></html>')
