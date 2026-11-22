#!/usr/bin/env python3
"""Build the /improve findings page (one HTML file) from a findings JSON file.

Usage: python3 <this skill's folder>/scripts/review_page.py <findings.json> [--out <page.html>]
Writes the page next to the JSON (same name, .html) unless --out is given, and prints its path.
The JSON format is in references/review-page.md. Your calls first, removals first in each group;
the rest keep the order given. The page's "Copy my answer" button builds the paste-back text.
Two groups: "Your calls" (cards that change what you see, do or decide) on top, then "My technical picks"
(housekeeping you never see), folded when it has more than 5 cards. A card's "call" field ("you" or "tech") puts
it in a group; without it, is_tech() decides. The intro also says how many cards need a plan and, when the net
size grows, that adds outweigh cuts.

The page (list + reader, pick_shell.py in this folder): every card listed on the left, the chosen
card on the right: headline, the marked change (struck red / green) with the clean After, a "When" bullet from
"moment", my pick with "Because" (why), one Details fold (Checked, tier, confidence, words), then Accept / Skip /
Flag and a note; one copy box under the list. Optional card fields, flat on the card (a "compact" block with the
same keys is also read): "headline" (one-line takeaway; falls back to title), and a picture below the change:
"shots", "table", "ta", "options", "expected_actual" (formats: the docstrings in pick_shell.py;
ta fields name a card field such as before, after, moment or why). Excerpts and table cells must be verbatim
pieces of the card's own text (stderr warning otherwise). /improve cards need no picture (the change is the
picture), so there is no missing-picture warning. When pick_shell.py or blocks.py cannot load
(VISUAL_BLOCKS_DIR swaps the folder) or the shell fails, the page is built as before (stacked cards).
The copy-back answer is the same on both.
"""
import datetime
import difflib
import html
import importlib.util
import os
import re
import json
import sys
from pathlib import Path

TYPES = ["remove", "move", "edit", "add"]
PICKS = {"accept": "Accept", "skip": "Skip", "flag": "Flag"}


def load_shell():
    """The shared pick shell (list + reader), loaded by absolute path (python3 -I blocks sibling imports);
    None when it or blocks.py is missing, so the page falls back to the stacked cards."""
    d = os.environ.get("VISUAL_BLOCKS_DIR") or os.path.dirname(os.path.abspath(__file__))
    try:
        spec = importlib.util.spec_from_file_location("pick_shell", os.path.join(d, "pick_shell.py"))
        ps = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ps)
        return ps
    except Exception:
        return None


PS = load_shell()


def esc(v):
    return html.escape(str(v if v is not None else ""), quote=True)


def order(cards):
    removes = [c for c in cards if c.get("type") == "remove"]
    rest = [c for c in cards if c.get("type") != "remove"]
    return removes + rest


YOURS, TECH = "Your calls", "My technical picks"
FOLD_AT = 5   # the technical group starts folded when it has more than this many cards


def is_tech(c):
    """My technical pick (housekeeping you never see) or your call. The card's "call" field decides; without it:
    a remove, edit or move with High confidence (any case) that I pick to accept."""
    if c.get("call") == "tech":
        return True
    if c.get("call") == "you":
        return False
    return (c.get("type") in ("remove", "edit", "move") and str(c.get("confidence", "")).lower() == "high"
            and c.get("pick", "accept") == "accept")


def split_groups(cards):
    """[(group name, cards)]: your calls first, then my technical picks; removals first in each; empty groups out."""
    yours = order([c for c in cards if not is_tech(c)])
    tech = order([c for c in cards if is_tech(c)])
    return [(name, cs) for name, cs in ((YOURS, yours), (TECH, tech)) if cs]


def intro_lines(cards, size):
    """The plan-count line, and the adds line only when the always-loaded words grow."""
    lines = [f"{sum(1 for c in cards if c.get('plan'))} of {len(cards)} cards need a plan"]
    before, after = size.get("before"), size.get("after")
    if isinstance(before, int) and isinstance(after, int) and after > before:
        lines.append(f"Adds outweigh cuts by {after - before:,} words: each add card says what it pairs with "
                     "or why it earns its place")
    return lines


def marked_change(before, after):
    """Word-level marked change: removed words struck in red, added words in green (the clean After stays below)."""
    a, b = re.split(r"(\s+)", before), re.split(r"(\s+)", after)
    out = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            out.append(esc("".join(a[i1:i2])))
            continue
        if i2 > i1:
            out.append("<del>%s</del>" % esc("".join(a[i1:i2])))
        if j2 > j1:
            out.append("<ins>%s</ins>" % esc("".join(b[j1:j2])))
    return "".join(out)


def text_or_list(v):
    """A list renders as bullets; a string as before."""
    if isinstance(v, list):
        return "<ul>%s</ul>" % "".join("<li>%s</li>" % esc(x) for x in v)
    return esc(v)


def card_html(c):
    cid = esc(c["id"])
    typ = c.get("type", "edit")
    pick = c.get("pick", "accept")
    if pick not in PICKS:
        pick = "accept"
    words = c.get("words")
    wtxt = "" if words is None else (f"{words:+d} words" if isinstance(words, int) else esc(words))
    plan = '<span class="badge plan">needs a plan</span>' if c.get("plan") else ""
    radios = "".join(
        f'<label><input type="radio" name="p-{cid}" value="{k}"{" checked" if k == pick else ""}> {v}</label>'
        for k, v in PICKS.items())
    parts = [
        f'<section class="card t-{esc(typ)}" id="{cid}" data-pick="{esc(pick)}">',
        f'<div class="head"><span class="type">{esc(typ)}</span> <b>{cid}</b> {esc(c.get("title", ""))} {plan}</div>',
        f'<div class="meta">{esc(c.get("tier", ""))} · {esc(c.get("confidence", ""))} confidence · <code>{esc(c.get("file", ""))}</code> · {wtxt}</div>',
    ]
    if c.get("before") and c.get("after"):
        parts.append(f'<div class="lbl">What changes</div><div class="diff">{marked_change(c["before"], c["after"])}</div>')
    if c.get("before") and c.get("after"):
        parts.append(f'<details><summary class="lbl">Before (the old text in full)</summary><pre class="before">{esc(c["before"])}</pre></details>')
    elif c.get("before"):
        parts.append(f'<div class="lbl">Before</div><pre class="before">{esc(c["before"])}</pre>')
    if c.get("after"):
        parts.append(f'<div class="lbl">After</div><pre class="after">{esc(c["after"])}</pre>')
    if c.get("moment"):
        parts.append(f'<div class="moment"><b>Moment:</b> {esc(c["moment"])}</div>')
    if c.get("evidence"):
        parts.append(f'<div class="evidence"><b>Checked:</b> {text_or_list(c["evidence"])}</div>')
    if c.get("why"):
        parts.append(f'<div class="why"><b>My pick, because:</b> {text_or_list(c["why"])}</div>')
    parts.append(f'<div class="mark">{radios}<input class="note" placeholder="note (optional)"></div></section>')
    return "\n".join(parts)


# the copy-back code (both layouts use it unchanged, so the pasted answer is the same on either page)
EXPORT_JS = """function answer() {
  const acc = [], skip = [], flag = [], notes = [];
  let changed = false;
  document.querySelectorAll('.card').forEach(c => {
    const v = (c.querySelector('input[type=radio]:checked') || {}).value;
    const n = c.querySelector('.note').value.trim();
    if (v !== c.dataset.pick) changed = true;
    c.classList.toggle('flagged', v === 'flag');
    if (v === 'flag') flag.push(c.id + (n ? ' (' + n + ')' : ''));
    else { (v === 'skip' ? skip : acc).push(c.id); if (n) notes.push(c.id + ': ' + n); }
  });
  let t;
  if (!changed && !notes.length) t = '/improve page answer: accept all picks as shown.';
  else {
    t = '/improve page answer: accept ' + (acc.join(', ') || 'none') + '; skip ' + (skip.join(', ') || 'none') + '; flag ' + (flag.join('; ') || 'none') + '.';
    if (notes.length) t += ' Notes: ' + notes.join('; ') + '.';
  }
  document.getElementById('out').value = t;
  document.getElementById('cnt').textContent = flag.length + ' flagged';
}
function copyAnswer() { answer(); const o = document.getElementById('out'); o.select(); navigator.clipboard.writeText(o.value).catch(() => document.execCommand('copy')); }
document.addEventListener('change', answer); document.addEventListener('input', answer); answer();
"""
COPY_HTML = """<button onclick="copyAnswer()">Copy my answer</button><span id="cnt"></span>
<textarea id="out" readonly></textarea>"""


def build(data):
    """Today's page (stacked cards): the fallback when the pick shell cannot load or fails."""
    groups = split_groups(data.get("cards", []))
    cards = [c for _, cs in groups for c in cs]
    counts = {t: sum(1 for c in cards if c.get("type") == t) for t in TYPES}
    size = data.get("size", {})
    before, after = size.get("before"), size.get("after")
    if isinstance(before, int) and isinstance(after, int):
        net = f"Always-loaded words if you accept every pick: {before:,} → {after:,} ({after - before:+,d})"
    else:
        net = "Always-loaded words: not measured"
    count_line = " · ".join(f"{counts[t]} {t}" for t in TYPES)
    lines = "".join(f"<p>{esc(x)}</p>" for x in intro_lines(cards, size))
    due = "".join(f"<li>{esc(d)}</li>" for d in data.get("due", []))
    due_html = f'<div class="box due"><b>Follow-ups due now:</b><ul>{due}</ul></div>' if due else ""
    extra = "".join(f"<p>{esc(x)}</p>" for x in data.get("notes", []))
    built = datetime.datetime.now().astimezone().strftime("%d %b %Y %H:%M %Z")
    body = []
    for name, cs in groups:
        inner = "\n".join(card_html(c) for c in cs)
        if name == TECH and len(cs) > FOLD_AT:
            body.append(f'<details class="grp"><summary><span class="gh">{esc(name)} ({len(cs)})</span> (click to show)</summary>\n{inner}\n</details>')
        else:
            body.append(f'<h2 class="grp">{esc(name)} ({len(cs)})</h2>\n{inner}')
    body = "\n".join(body)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(data.get('title', '/improve findings'))}</title>
<style>
body {{ font-family: -apple-system, system-ui, sans-serif; margin: 0; color: #222; background: #f6f6f4; }}
main {{ max-width: 920px; margin: 0 auto; padding: 16px 14px 150px; }}
h1 {{ font-size: 22px; margin: 6px 0 10px; }}
.box {{ background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 10px 14px; margin-bottom: 12px; }}
.net {{ font-size: 17px; font-weight: 600; }}
.due {{ border-color: #f0a050; background: #fff6ea; }}
.card {{ background: #fff; border: 1px solid #ddd; border-left: 5px solid #999; border-radius: 8px; padding: 10px 14px; margin: 10px 0; }}
.t-remove {{ border-left-color: #c62828; }} .t-move {{ border-left-color: #6a1b9a; }}
.t-edit {{ border-left-color: #1565c0; }} .t-add {{ border-left-color: #2e7d32; }}
.type {{ text-transform: uppercase; font-size: 11px; font-weight: 700; background: #eee; border-radius: 3px; padding: 1px 6px; }}
.badge.plan {{ white-space: nowrap; font-size: 11px; background: #fff3cd; border: 1px solid #e0c060; border-radius: 3px; padding: 1px 6px; }}
.meta {{ color: #666; font-size: 12.5px; margin: 4px 0 6px; overflow-wrap: anywhere; }}
.lbl {{ font-size: 11px; color: #777; margin-top: 6px; }}
pre {{ white-space: pre-wrap; overflow-wrap: anywhere; font-size: 13px; margin: 2px 0; padding: 6px 8px; border-radius: 4px; }}
pre.before {{ background: #fdecea; }}
.diff {{ white-space: pre-wrap; font: 13px ui-monospace, Menlo, monospace; background: #fff; border: 1px solid #d9dee5; border-radius: 6px; padding: 8px 10px; }}
.diff del {{ background: #fdecea; color: #b42318; }} .diff ins {{ background: #e6f4ea; color: #1f7a3f; text-decoration: none; }} pre.after {{ background: #e8f5e9; }}
.moment, .evidence, .why {{ font-size: 13.5px; margin-top: 6px; }}
.mark {{ margin-top: 8px; display: flex; flex-wrap: wrap; gap: 12px; align-items: center; font-size: 14px; }}
.note {{ flex: 1; min-width: 160px; padding: 4px 6px; border: 1px solid #ccc; border-radius: 4px; font-size: 13px; }}
.flagged {{ outline: 2px solid #ff9500; }}
h2.grp {{ font-size: 17px; margin: 18px 0 6px; }} details.grp {{ margin: 18px 0 6px; }}
details.grp summary {{ cursor: pointer; color: #555; font-size: 13px; }} details.grp .gh {{ font-size: 17px; font-weight: 700; color: #222; }}
.bar {{ position: fixed; left: 0; right: 0; bottom: 0; background: #fff; border-top: 2px solid #ccc; padding: 8px 12px; }}
.bar .inner {{ max-width: 920px; margin: 0 auto; }}
.bar textarea {{ width: 100%; height: 56px; font-family: ui-monospace, Menlo, monospace; font-size: 12px; box-sizing: border-box; }}
.bar button {{ font-size: 14px; padding: 5px 12px; margin-right: 8px; }}
@media (max-width: 600px) {{ h1 {{ font-size: 19px; }} .bar textarea {{ height: 44px; }} }}
</style></head><body><main>
<h1>{esc(data.get('title', '/improve findings'))}</h1>
<div class="box"><div class="net">{esc(net)}</div>
<p>{len(cards)} cards: {esc(count_line)}. Your calls first, then my technical picks; removals first in each. Each card shows my pick; change any pick or flag it, then copy your answer.</p>{lines}
<p>Your accept approves only the text edits shown word for word here. Cards marked "needs a plan" (a new hook, a new skill, a multi-file restructure) go into a plan first.</p>
<p>{esc(data.get('coverage', ''))}</p>{extra}</div>
{due_html}
{body}
<p style="color:#888;font-size:12px">Built {built} by the /improve findings page script.</p>
</main>
<div class="bar"><div class="inner">
{COPY_HTML}
</div></div>
<script>
{EXPORT_JS}</script></body></html>"""


# ---------- the pick page (list + reader, pick_shell.py) ----------

MARKS = [("accept", "Accept", "✓", "A", True), ("skip", "Skip", "–", "S", True), ("flag", "Flag", "⚑", "F", False)]
TYPE_NAMES = {"remove": ("−", "Remove"), "edit": ("Δ", "Edit"), "add": ("+", "Add"), "move": ("→", "Move")}
B2_CSS = r"""
.ty{font-size:11.5px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;border-radius:4px;padding:1px 7px;color:#fff}
.ty-remove{background:var(--bad)}.ty-edit{background:var(--acc)}.ty-add{background:var(--ok)}.ty-move{background:#6a1b9a}
.ip-diff{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.55 ui-monospace,Menlo,monospace;border:1px solid var(--line);border-radius:8px;padding:10px 12px;background:#fff}
.ip-diff del,.ip-legend del{background:#fdecea;color:var(--bad)}
.ip-diff ins,.ip-legend ins{background:#e6f4ea;color:var(--ok);text-decoration:underline;text-decoration-thickness:1.5px}
.ip-legend{font-size:12px;color:var(--mut);margin:4px 0 2px}
pre.ip-before{background:#fdecea}pre.ip-gone{text-decoration:line-through;text-decoration-color:rgba(180,35,24,.45)}
pre.ip-after{background:#e8f5e9}
.ip-det summary{font-size:12.5px;color:var(--mut);cursor:pointer;margin-top:6px}
.in-net{font-size:17px;font-weight:600;margin:4px 0}
.lg.ip-fold{cursor:pointer;user-select:none}.lg.ip-fold:hover{background:#e6ebf2}
.lg.ip-fold::before{content:"▾ "}.lg.ip-fold:not(.open)::before{content:"▸ "}
.lg.ip-fold:not(.open)::after{content:" · click to show";text-transform:none;letter-spacing:0;font-weight:400}
.li.ip-hid{display:none}
"""

# the technical group's fold (pick page only; appended to the export script, which runs before the shell's own
# script). The shell's sel() and cur are private, so a MutationObserver watches the list items' "cur" class and
# opens the group when the reader moves to a folded card.
FOLD_JS = r"""
/* improve-fold */
(function () {
  const NAME = __NAME__, FOLD_AT = __FOLD_AT__;
  document.querySelectorAll('.list .lg').forEach(h => {
    if (h.textContent.indexOf(NAME + ' (') !== 0) return;
    const items = [];
    for (let n = h.nextElementSibling; n && !n.classList.contains('lg'); n = n.nextElementSibling) items.push(n);
    function set(open) {
      h.classList.toggle('open', open); h.setAttribute('aria-expanded', open ? 'true' : 'false');
      items.forEach(i => i.classList.toggle('ip-hid', !open));
    }
    h.classList.add('ip-fold'); h.setAttribute('role', 'button'); h.tabIndex = 0;
    set(items.length <= FOLD_AT);
    h.addEventListener('click', () => set(!h.classList.contains('open')));
    h.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { set(!h.classList.contains('open')); e.preventDefault(); e.stopPropagation(); }
    });
    const obs = new MutationObserver(() => {
      const c = items.find(i => i.classList.contains('cur'));
      if (c && !h.classList.contains('open')) { set(true); c.scrollIntoView({block: 'nearest'}); }
    });
    items.forEach(i => obs.observe(i, {attributes: true, attributeFilter: ['class']}));
  });
})();
""".replace("__NAME__", json.dumps(TECH)).replace("__FOLD_AT__", str(FOLD_AT))


def b2_card(c, warn):
    cid = str(c["id"])
    typ = c.get("type", "edit")
    pick = c.get("pick", "accept")
    if pick not in PICKS:
        pick = "accept"
    sym, tname = TYPE_NAMES.get(typ, ("", typ))
    words = c.get("words")
    wtxt = "" if words is None else (f"{words:+d} words" if isinstance(words, int) else str(words))
    plan = '<span class="pc-badge plan">needs a plan</span>' if c.get("plan") else ""
    kick = (f'<span class="ty ty-{esc(typ)}">{sym} {esc(tname)}</span><span class="pc-id">{esc(cid)}</span>'
            f'<span class="pc-file">{esc(c.get("file", ""))}</span>{plan}')
    top = []
    b, a = c.get("before"), c.get("after")
    if b and a:
        diff = marked_change(b, a)
        pure_add = "<del>" not in diff
        top.append(f'<div class="vb-lab">{"What changes: the After text, added part in green" if pure_add else "What changes"}</div>'
                   f'<div class="ip-diff">{diff}</div>'
                   '<div class="ip-legend"><del>struck red</del> = removed · <ins>underlined green</ins> = added</div>')
        if not pure_add:
            top.append(f'<div class="vb-lab">After (the text you approve)</div><pre class="ip-after">{esc(a)}</pre>')
        top.append(f'<details class="ip-det"><summary>Before (the old text in full)</summary><pre class="ip-before">{esc(b)}</pre></details>')
    elif b:
        top.append(f'<div class="vb-lab">− Text removed</div><pre class="ip-before ip-gone">{esc(b)}</pre>')
    elif a:
        top.append(f'<div class="vb-lab">+ Text added</div><pre class="ip-after">{esc(a)}</pre>')
    kind, pic = PS.picture(cid, c, warn=warn)
    bl = PS.bullet("When", c["moment"]) if c.get("moment") else []
    rows = [("Checked", text_or_list(c["evidence"]) if c.get("evidence") else ""),
            ("Card", esc(" · ".join(x for x in (c.get("tier", ""), (c.get("confidence", "") + " confidence")
                                                 if c.get("confidence") else "", wtxt) if x)))]
    html_ = PS.card(cid, kick=kick, headline=PS.fields(c).get("headline") or c.get("title", ""), title=c.get("title", ""),
                    top="".join(top), pic=pic, bullets=bl, pick=esc(PICKS[pick]),
                    pick_sub=f"Because: {text_or_list(c['why'])}" if c.get("why") else "", details_rows=rows,
                    marks=[m[:4] for m in MARKS], prefix="p", default=pick, extra_class=f"t-{esc(typ)}")
    return {"id": cid, "title": c.get("title", ""), "pick": PICKS[pick], "pic": "Change" if (b or a) else kind, "html": html_}


def b2_build(data, warn):
    groups = split_groups(data.get("cards", []))
    cards = [c for _, cs in groups for c in cs]
    counts = {t: sum(1 for c in cards if c.get("type") == t) for t in TYPES}
    size = data.get("size", {})
    before, after = size.get("before"), size.get("after")
    if isinstance(before, int) and isinstance(after, int):
        net = f"Always-loaded words if you accept every pick: {before:,} → {after:,} ({after - before:+,d})"
    else:
        net = "Always-loaded words: not measured"
    bl = [f"{len(cards)} cards: " + " · ".join(f"{counts[t]} {t}" for t in TYPES)
          + f"; your calls first, then my technical picks (folded when more than {FOLD_AT}), removals first in each",
          *intro_lines(cards, size),
          "Your accept approves only the text edits shown word for word here",
          "Cards marked \"needs a plan\" (a new hook, a new skill, a multi-file restructure) go into a plan first"]
    due = "".join(f"<li>{esc(d)}</li>" for d in data.get("due", []))
    more = "".join(f"<p>{esc(x)}</p>" for x in [data.get("coverage", "")] + list(data.get("notes", [])) if x)
    built = datetime.datetime.now().astimezone().strftime("%d %b %Y %H:%M %Z")
    title = data.get("title", "/improve findings")
    intro = (f'<section class="intro"><div class="in-kick">/improve findings page</div><h1>{esc(title)}</h1>'
             f'<div class="in-net">{esc(net)}</div>'
             f'<p class="in-counts">Each card shows my pick; change any pick or flag it, then copy your answer.</p>'
             f'{PS.VB.bullets(bl)}' + (f'<div class="in-due"><b>Follow-ups due now:</b><ul>{due}</ul></div>' if due else "")
             + (f'<details><summary>Coverage and notes</summary>{more}</details>' if more else "")
             + f'<p class="in-built">Built {built} by the /improve findings page script.</p></section>')
    return PS.page(title, intro=intro, groups=[(name, [b2_card(c, warn) for c in cs]) for name, cs in groups],
                   copy_html=COPY_HTML, export_js=EXPORT_JS + FOLD_JS, marks=MARKS, hot=("flag",), hot_word="flagged", extra_css=B2_CSS)


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    src = Path(argv[1])
    out = src.with_suffix(".html")
    if "--out" in argv:
        out = Path(argv[argv.index("--out") + 1])
    if out.suffix != ".html" or out.resolve() == src.resolve():
        print("--out must end in .html and differ from the JSON file", file=sys.stderr)
        return 2
    data = json.loads(src.read_text(encoding="utf-8"))
    for c in data.get("cards", []):
        if "id" not in c:
            print("every card needs an id", file=sys.stderr)
            return 2
    page, warn = None, []
    if PS is not None:
        try:
            page = b2_build(data, warn)
        except Exception as e:  # a shell failure must never cost the page: build today's page instead
            page, warn = None, []
            print(f"note: pick page layout failed ({type(e).__name__}: {e}); built the stacked page instead", file=sys.stderr)
    if page is None:
        page = build(data)
    out.write_text(page, encoding="utf-8")
    print(out)
    for w in warn:
        print("warning:", w, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
