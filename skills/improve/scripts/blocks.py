#!/usr/bin/env python3
"""Visual blocks: small fixed picture blocks for local HTML pages (here: the /improve findings page).

Part of the /improve skill (scripts/ folder); loaded by pick_shell.py from its own folder.
Load by absolute path (python3 -I blocks sibling imports):
    import importlib.util, os
    d = os.environ.get("VISUAL_BLOCKS_DIR") or os.path.dirname(os.path.abspath(__file__))
    spec = importlib.util.spec_from_file_location("visual_blocks", os.path.join(d, "blocks.py"))
    vb = importlib.util.module_from_spec(spec); spec.loader.exec_module(vb)

Every function returns an HTML string (diagram returns (html, warnings)). Class names start with
"vb-" so they never clash with the host page; put css() once in the page's <style>.
Standard library only; Pillow is imported inside shot() alone.
"""
import base64
import html
import io
import os
import re

MAX_BOXES = 9
ACCENT = "#2563eb"


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def inline(s):
    """Escape, then keep **bold** and `code`."""
    e = esc(s)
    e = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", e)
    e = re.sub(r"`([^`]+)`", r"<code>\1</code>", e)
    return e


def css():
    return """
.vb{font:14px/1.45 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;color:#1d2330}
.vb-lab{font-size:12px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:#5f6b7a;margin:12px 0 6px}
table.vb-opt{width:100%;border-collapse:separate;border-spacing:0;font-size:13.5px;margin:6px 0}
.vb-opt th,.vb-opt td{border-bottom:1px solid #d9dee5;padding:7px 9px;text-align:left;vertical-align:top}
.vb-opt thead th{border-bottom:2px solid #d9dee5}
.vb-opt th.vb-row{color:#5f6b7a;font-weight:600;width:22%}
.vb-opt .vb-pick{background:#eef4ff}.vb-opt thead th.vb-pick{border-top:3px solid #2563eb}
.vb-star{display:block;color:#2563eb;font-size:12px;font-weight:700}
.vb-ok::before{content:"\\2713  ";color:#1f7a3f;font-weight:700}
.vb-no::before{content:"\\2717  ";color:#b42318;font-weight:700}
.vb-mid::before{content:"~  ";color:#a15c00;font-weight:700}
.vb-shot{border:1px solid #d9dee5;border-radius:8px;overflow:hidden;background:#fff;margin:6px 0}
.vb-shot .vb-bar{background:#eef1f4;font-size:12px;padding:4px 8px;color:#5f6b7a}
.vb-shot img{display:block;max-width:100%;height:auto}
.vb-notes{list-style:none;margin:6px 0 0;padding:0 8px 8px;font-size:13px}
.vb-notes li{margin:3px 0}
.vb-num{display:inline-block;min-width:18px;height:18px;border-radius:9px;background:#c81e28;color:#fff;
 text-align:center;font-size:11px;font-weight:700;line-height:18px;margin-right:6px}
.vb-missing{color:#5f6b7a;font-size:13px;font-style:italic;margin:6px 0}
.vb-delta{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px;margin:6px 0}
.vb-col{border:1px solid #d9dee5;border-radius:10px;padding:8px 12px;background:#fff}
.vb-col h4{margin:0 0 6px;font-size:12.5px;letter-spacing:.04em;text-transform:uppercase}
.vb-col ul{margin:0;padding:0;list-style:none;font-size:13.5px}.vb-col li{padding:2px 0}
.vb-add{border-top:4px solid #1f7a3f}.vb-add h4{color:#1f7a3f}
.vb-chg{border-top:4px solid #a15c00}.vb-chg h4{color:#a15c00}
.vb-same{border-top:4px dashed #9aa4b2}.vb-same h4{color:#5f6b7a}
.vb-flow{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:6px 0}
.vb-frame{min-width:96px;max-width:150px;min-height:52px;border:1px solid #c9d0d9;border-radius:8px;background:#fff;
 font-size:12.5px;padding:6px 8px;display:flex;align-items:center}
.vb-frame.vb-hi{outline:3px solid #2563eb;outline-offset:1px}
.vb-arrow{color:#9aa4b2}
.vb-ea{display:grid;grid-template-columns:max-content 1fr;gap:6px 12px;align-items:center;font-size:13.5px;margin:6px 0}
.vb-dots{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.vb-dot{width:22px;height:22px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;
 font-size:11px;font-weight:700;color:#fff}
.vb-on{background:#3b6fd8}.vb-off{background:#fff;border:2px dashed #9aa4b2;color:#9aa4b2}
.vb-dok{background:#1f7a3f}.vb-dno{background:#b42318}
.vb-cap{color:#5f6b7a;font-size:12.5px}
.vb-cap.vb-bad{color:#b42318}.vb-cap.vb-good{color:#1f7a3f}
.vb-diagram{overflow-x:auto;margin:6px 0}.vb-dv{display:none}
@media (max-width:760px){.vb-dh{display:none}.vb-dv{display:block}}
.vb-words{font-size:12.5px;color:#5f6b7a;margin:4px 0 0;padding-left:18px}
ul.vb-ul{margin:4px 0;padding-left:20px}ul.vb-ul ul.vb-ul,ul.vb-ul ol.vb-ul{margin:2px 0}
ol.vb-ul{margin:4px 0;padding-left:22px}
.vb-ba{display:grid;grid-template-columns:minmax(90px,.7fr) 1fr 22px 1.2fr;gap:8px 8px;align-items:stretch;font-size:13.5px;margin:6px 0}
.vb-bah{font-size:12px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:#5f6b7a}
.vb-bat{font-weight:700;align-self:center}
.vb-bab{border:1px dashed #9aa4b2;border-radius:8px;padding:7px 10px;background:#f6f7f9;color:#46505e}
.vb-baf{border:1.5px solid #2563eb;border-radius:8px;padding:7px 10px;background:#eef4ff}
.vb-baa{align-self:center;text-align:center;color:#5f6b7a;font-size:18px}
@media (max-width:620px){.vb-ba{grid-template-columns:1fr 18px 1fr}.vb-ba>span:nth-child(-n+4){display:none}.vb-bat{grid-column:1/-1;margin-top:6px}}
.vb-legend{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:#5f6b7a;border-top:1px solid #d9dee5;
 margin-top:8px;padding-top:6px}
"""


# ---------- text ----------

def bullets(items, ordered=False):
    """A list (strings, or nested lists after a string = its sub-bullets) to nested <ul>/<ol>.
    A plain string comes back as one paragraph, unchanged, so old inputs render as before."""
    if items is None or items == "" or items == []:
        return ""
    if isinstance(items, str):
        return "<p>%s</p>" % inline(items)
    tag = "ol" if ordered else "ul"
    out = ['<%s class="vb-ul">' % tag]
    open_li = False
    for it in items:
        if isinstance(it, (list, tuple)):
            if open_li:
                out.append(bullets(list(it)))
                continue
            out.append("<li>%s</li>" % bullets(list(it)))
            continue
        if open_li:
            out.append("</li>")
        out.append("<li>%s" % inline(it))
        open_li = True
    if open_li:
        out.append("</li>")
    out.append("</%s>" % tag)
    return "".join(out)


# ---------- option table ----------

def option_table(options, rows, pick=None):
    """options: names; rows: [label, [cell per option], optional [mark per option: ok|no|mid|'']].
    pick: index of Claude's pick (tinted, labelled)."""
    if not options or not rows:
        return ""
    head = ['<th class="vb-row"></th>']
    for i, o in enumerate(options):
        cls = ' class="vb-pick"' if pick == i else ""
        star = '<span class="vb-star">★ MY PICK</span>' if pick == i else ""
        head.append("<th%s>%s%s</th>" % (cls, star, inline(o)))
    body = []
    for r in rows:
        label, cells = r[0], list(r[1])
        marks = list(r[2]) if len(r) > 2 and r[2] else [""] * len(cells)
        tds = []
        for i in range(len(options)):
            c = cells[i] if i < len(cells) else ""
            m = marks[i] if i < len(marks) else ""
            cls = []
            if pick == i:
                cls.append("vb-pick")
            if m in ("ok", "no", "mid"):
                cls.append("vb-" + m)
            tds.append('<td%s>%s</td>' % ((' class="%s"' % " ".join(cls)) if cls else "", inline(c)))
        body.append('<tr><th class="vb-row">%s</th>%s</tr>' % (inline(label), "".join(tds)))
    return '<table class="vb-opt"><thead><tr>%s</tr></thead><tbody>%s</tbody></table>' % ("".join(head), "".join(body))


# ---------- screenshot ----------

def _font(size):
    from PIL import ImageFont
    for f in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


def shot_image(path, crop=None, marks=None, max_width=900):
    """Return PNG bytes of the cropped, scaled and marked screenshot (marks in ORIGINAL pixels)."""
    from PIL import Image, ImageDraw
    im = Image.open(path).convert("RGB")
    x0, y0 = 0, 0
    if crop:
        x1, y1, x2, y2 = [int(v) for v in crop]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(im.width, x2), min(im.height, y2)
        im = im.crop((x1, y1, x2, y2))
        x0, y0 = x1, y1
    scale = min(1.5, max_width / float(im.width)) if im.width < max_width else max_width / float(im.width)
    if abs(scale - 1.0) > 0.01:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    red = (200, 30, 40)
    font = _font(max(14, int(16 * min(scale, 1.6))))
    r = max(11, int(12 * min(scale, 1.6)))
    for n, m in enumerate(marks or [], 1):
        box = m.get("box")
        if not box:
            continue
        bx1, by1, bx2, by2 = [(v - o) * scale for v, o in zip(box, (x0, y0, x0, y0))]
        d.rounded_rectangle((bx1 - 4, by1 - 4, bx2 + 4, by2 + 4), radius=8, outline=red, width=max(3, int(2 * scale)))
        # badge on the box's top-right corner, kept inside the image
        cx = min(max(bx2 + 4, r + 1), im.width - r - 1)
        cy = min(max(by1 - 4, r + 1), im.height - r - 1)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=red)
        t = str(n)
        tw = d.textlength(t, font=font)
        d.text((cx - tw / 2, cy - r * 0.75), t, fill="white", font=font)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue()


def shot(path, crop=None, marks=None, caption=""):
    """A real screenshot, cropped and marked, embedded as base64, with one line per numbered marker."""
    name = os.path.basename(str(path or ""))
    p = os.path.expanduser(str(path or ""))
    if not p or not os.path.isfile(p):
        return '<div class="vb-missing">screenshot not found: %s</div>' % esc(name or "(no path)")
    try:
        data = shot_image(p, crop, marks)
    except ImportError:
        return '<div class="vb-missing">screenshot not shown (Pillow missing): %s</div>' % esc(name)
    except Exception as e:  # a broken image must never break the page
        return '<div class="vb-missing">screenshot not shown (%s): %s</div>' % (esc(type(e).__name__), esc(name))
    b64 = base64.b64encode(data).decode("ascii")
    notes = "".join('<li><span class="vb-num">%d</span>%s</li>' % (n, inline(m.get("note", "")))
                    for n, m in enumerate(marks or [], 1) if m.get("note"))
    bar = '<div class="vb-bar">%s</div>' % inline(caption or name)
    return ('<div class="vb-shot">%s<img alt="%s" src="data:image/png;base64,%s">%s</div>'
            % (bar, esc(caption or name), b64, ('<ul class="vb-notes">%s</ul>' % notes) if notes else ""))


# ---------- what changes ----------

def delta(added=None, changed=None, untouched=None):
    cols = []
    for items, cls, head in ((added, "vb-add", "+ Added"), (changed, "vb-chg", "Δ Changed"),
                             (untouched, "vb-same", "= Not touched")):
        if items:
            cols.append('<div class="vb-col %s"><h4>%s</h4><ul>%s</ul></div>'
                        % (cls, head, "".join("<li>%s</li>" % inline(x) for x in items)))
    return '<div class="vb-delta">%s</div>' % "".join(cols) if cols else ""


# ---------- flow row ----------

def flow(steps, highlight=None):
    """A row of frames with arrows (a straight chain: storyboard, step rail). highlight: index or set."""
    if not steps:
        return ""
    hi = {highlight} if isinstance(highlight, int) else set(highlight or [])
    parts = []
    for i, s in enumerate(steps[:MAX_BOXES]):
        if i:
            parts.append('<span class="vb-arrow">→</span>')
        parts.append('<div class="vb-frame%s">%s</div>' % (" vb-hi" if i in hi else "", inline(s)))
    if len(steps) > MAX_BOXES:
        parts.append('<span class="vb-cap">+%d more</span>' % (len(steps) - MAX_BOXES))
    return '<div class="vb-flow">%s</div>' % "".join(parts)


# ---------- expected vs actual ----------

def expected_actual(rows):
    """rows: [{"label": "Message says", "items": [["1","on"],["2","on"],["3","off"]], "note": "...", "tone": "bad|good|"}]
    item states: on (blue), off (dashed: absent or deleted), ok (green tick), no (red cross)."""
    if not rows:
        return ""
    # Dots hold at most 3 characters; any longer item turns the block into a plain two-column table,
    # because sentences squeezed into dots are unreadable.
    def _txt(it):
        return str(it[0] if isinstance(it, (list, tuple)) else it)
    if any(len(_txt(it)) > 3 for r in rows for it in r.get("items", [])):
        trs = []
        for r in rows:
            lines = []
            for it in r.get("items", []):
                if isinstance(it, (list, tuple)) and len(it) > 1:
                    lines.append("<b>%s</b>: %s" % (inline(it[0]), inline(it[1])))
                else:
                    lines.append(inline(_txt(it)))
            if r.get("note"):
                lines.append("<i>%s</i>" % inline(r.get("note")))
            bad = ' style="color:#b42318"' if r.get("tone") == "bad" else ""
            trs.append('<tr><th style="text-align:left;vertical-align:top;padding:6px 12px 6px 0;white-space:nowrap">%s</th>'
                       '<td%s style="padding:6px 0">%s</td></tr>' % (inline(r.get("label", "")), bad, "<br>".join(lines)))
        return '<table class="vb-eat" style="border-collapse:collapse;margin:6px 0 10px;font-size:15px">%s</table>' % "".join(trs)
    out = []
    for r in rows:
        dots = []
        for it in r.get("items", []):
            text, state = (it[0], it[1]) if isinstance(it, (list, tuple)) else (it, "on")
            cls = {"on": "vb-on", "off": "vb-off", "ok": "vb-dok", "no": "vb-dno"}.get(state, "vb-on")
            dots.append('<span class="vb-dot %s">%s</span>' % (cls, esc(text)))
        tone = {"bad": " vb-bad", "good": " vb-good"}.get(r.get("tone", ""), "")
        mark = {"bad": "✗ ", "good": "✓ "}.get(r.get("tone", ""), "")
        note = ('<span class="vb-cap%s">%s%s</span>' % (tone, mark, inline(r.get("note")))) if r.get("note") else ""
        out.append('<span>%s</span><span class="vb-dots">%s%s</span>' % (inline(r.get("label", "")), "".join(dots), note))
    return '<div class="vb-ea">%s</div>' % "".join(out)


# ---------- custom diagram (boxes and arrows from text) ----------

EDGE_RE = re.compile(r"^\s*(.+?)\s*->\s*(.+?)\s*(?::\s*(.*))?$")


def parse_edges(lines):
    """'A -> B: label' lines to [(a, b, label)]; other lines ignored."""
    out = []
    for ln in lines:
        ln = re.sub(r"^\s*[-*]\s+", "", ln.strip()).strip("`")
        m = EDGE_RE.match(ln)
        if m and m.group(1) and m.group(2):
            out.append((m.group(1).strip(), m.group(2).strip(), (m.group(3) or "").strip()))
    return out


def _wrap(text, width=18, lines=2):
    words, out, cur = str(text).split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= width:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    if len(out) > lines:
        out = out[:lines]
        out[-1] = out[-1][: width - 1] + "…"
    return out


def diagram(edges, words=None, highlight=None, meta=None, need_words=True, max_boxes=MAX_BOXES):
    """edges: [(a, b, label)] or 'A -> B: label' strings. Returns (html, warnings).
    meta: optional {node: {"kind": "stop"|"done"|"work", "sub": "est. 60 min"}}: stops amber (the person's turns),
    done green, sub = a small second line (time, who). With meta, a straight chain still draws as boxes.
    Straight chain -> flow row; more than MAX_BOXES boxes -> warning and a plain list."""
    if edges and isinstance(edges[0], str):
        edges = parse_edges(edges)
    warnings = []
    if not edges:
        return "", ["Diagram has no 'A -> B' lines"]
    nodes = []
    for a, b, _ in edges:
        for n in (a, b):
            if n not in nodes:
                nodes.append(n)
    words = [w for w in (words or []) if str(w).strip()]
    if not words and need_words:
        warnings.append("Diagram has no 'In words:' sentences (each arrow should be said in words under it)")
    words_html = ('<ul class="vb-words">%s</ul>' % "".join("<li>%s</li>" % inline(w) for w in words)) if words else ""
    if len(nodes) > max_boxes:
        warnings.append("Diagram has %d boxes (limit %d): shown as a list; split it" % (len(nodes), max_boxes))
        lab = lambda x: (meta or {}).get(x, {}).get("label", x)
        lst = "".join("<li>%s → %s%s</li>" % (inline(lab(a)), inline(lab(b)), (" (" + inline(l) + ")") if l else "")
                      for a, b, l in edges)
        return '<ul class="vb-ul">%s</ul>%s' % (lst, words_html), warnings
    outs = {n: [b for a, b, _ in edges if a == n] for n in nodes}
    ins = {n: [a for a, b, _ in edges if b == n] for n in nodes}
    chain = (not meta and all(len(outs[n]) <= 1 and len(ins[n]) <= 1 for n in nodes)
             and sum(1 for n in nodes if not ins[n]) == 1 and len(edges) == len(nodes) - 1)
    if chain:
        start = next(n for n in nodes if not ins[n])
        seq = [start]
        while outs[seq[-1]]:
            seq.append(outs[seq[-1]][0])
        hi = [seq.index(h) for h in ([highlight] if isinstance(highlight, str) else (highlight or [])) if h in seq]
        return flow(seq, hi) + words_html, warnings
    # depth = longest path from a source (cycle-safe: at most len(nodes) passes)
    depth = {n: 0 for n in nodes}
    for _ in range(len(nodes)):
        changed = False
        for a, b, _l in edges:
            if depth[b] < depth[a] + 1 and depth[a] + 1 < len(nodes):
                depth[b] = depth[a] + 1
                changed = True
        if not changed:
            break
    lab_warn = []
    h_svg = _draw(nodes, edges, depth, highlight, vertical=False, warn=lab_warn, meta=meta)
    v_svg = _draw(nodes, edges, depth, highlight, vertical=True, warn=[], meta=meta)
    warnings += lab_warn
    # wide panes show left to right; narrow panes show whichever direction is narrower (a long chain goes top
    # down, a fan of many boxes into one stays left to right)
    def width(svg):
        m = re.search(r'width="(\d+)"', svg)
        return int(m.group(1)) if m else 0
    narrow = v_svg if width(v_svg) <= width(h_svg) else h_svg
    if max(depth.values()) + 1 > 6:  # more than 6 columns can't fit side by side: top to bottom everywhere
        h_svg = v_svg
    return ('<div class="vb-diagram"><div class="vb-dh">%s</div><div class="vb-dv">%s</div></div>%s'
            % (h_svg, narrow, words_html)), warnings


def _draw(nodes, edges, depth, highlight, vertical=False, warn=None, meta=None):
    """One SVG. Horizontal: columns by depth, arrows left to right. Vertical: rows by depth, arrows top down."""
    warn = warn if warn is not None else []
    cols = {}
    for n in nodes:
        cols.setdefault(depth[n], []).append(n)
    meta = meta or {}
    bw, bh, pad = 156, (60 if any(m.get('sub') for m in meta.values()) else 46), 14
    gx, gy = (34, 54 if len(nodes) <= 9 else 36) if vertical else (74, 22)
    nlev = max(cols) + 1
    nmax = max(len(v) for v in cols.values())
    back = any(depth[b] <= depth[a] for a, b, _ in edges)
    if not vertical and nlev > 1:  # shrink boxes and gaps so up to about 6 columns fit a 1,000 px pane
        fit = (1000 - pad * 2) / float(nlev * 156 + (nlev - 1) * 74)
        if fit < 1:
            bw, gx = max(112, int(156 * fit)), max(40, int(74 * fit))
    if vertical and nmax > 1:  # side-by-side boxes must fit a narrow pane (about 520 px)
        fit = (520 - pad * 2) / float(nmax * 156 + (nmax - 1) * 34)
        if fit < 1:
            bw, gx = max(118, int(156 * fit)), max(18, int(34 * fit))
    if vertical:
        W = pad * 2 + nmax * bw + (nmax - 1) * gx + (40 if back else 0)
        H = pad * 2 + nlev * bh + (nlev - 1) * gy
    else:
        W = pad * 2 + nlev * bw + (nlev - 1) * gx
        H = pad * 2 + nmax * bh + (nmax - 1) * gy + (30 if back else 0)
    pos = {}
    for c, ns in cols.items():
        for r, n in enumerate(ns):
            if vertical:
                left = pad + (nmax - len(ns)) * (bw + gx) / 2.0
                pos[n] = (left + r * (bw + gx), pad + c * (bh + gy))
            else:
                top = pad + (nmax - len(ns)) * (bh + gy) / 2.0
                pos[n] = (pad + c * (bw + gx), top + r * (bh + gy))
    hiset = {highlight} if isinstance(highlight, str) else set(highlight or [])
    mid = "vbarrow%s" % ("v" if vertical else "h")
    svg = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="Diagram" '
           'font-family="-apple-system,Helvetica,Arial,sans-serif">' % (W, H, W, H),
           '<defs><marker id="%s" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto">'
           '<path d="M0,0 L7,3.5 L0,7 z" fill="#5f6b7a"/></marker></defs>' % mid]
    labels = []
    for a, b, lab in edges:
        ax, ay = pos[a]
        bx, by = pos[b]
        fwd = depth[b] > depth[a]
        if fwd and not vertical:
            x1, y1, x2, y2 = ax + bw, ay + bh / 2, bx - 2, by + bh / 2
            m = (x1 + x2) / 2
            d = "M%.0f,%.0f C%.0f,%.0f %.0f,%.0f %.0f,%.0f" % (x1, y1, m, y1, m, y2, x2, y2)
            lx, ly = m, (y1 + y2) / 2
        elif fwd:
            x1, y1, x2, y2 = ax + bw / 2, ay + bh, bx + bw / 2, by - 2
            m = (y1 + y2) / 2
            d = "M%.0f,%.0f C%.0f,%.0f %.0f,%.0f %.0f,%.0f" % (x1, y1, x1, m, x2, m, x2, y2)
            lx, ly = (x1 + x2) / 2, m + 4
        elif not vertical:  # back arrow: loop under the boxes
            x1, y1, x2, y2 = ax + bw / 2, ay + bh, bx + bw / 2, by + bh + 2
            low = max(y1, y2) + 24
            d = "M%.0f,%.0f C%.0f,%.0f %.0f,%.0f %.0f,%.0f" % (x1, y1, x1, low, x2, low, x2, y2)
            lx, ly = (x1 + x2) / 2, low - 4
        else:  # back arrow: loop to the right of the boxes
            x1, y1, x2, y2 = ax + bw, ay + bh / 2, bx + bw + 2, by + bh / 2
            right = max(x1, x2) + 32
            d = "M%.0f,%.0f C%.0f,%.0f %.0f,%.0f %.0f,%.0f" % (x1, y1, right, y1, right, y2, x2, y2)
            lx, ly = right - 6, (y1 + y2) / 2
        svg.append('<path d="%s" fill="none" stroke="#5f6b7a" stroke-width="1.6" marker-end="url(#%s)"/>' % (d, mid))
        if lab:
            if len(lab) > 18:
                warn.append("Arrow label over 18 characters, shortened: %s" % lab)
                lab = lab[:17] + "\u2026"
            if not vertical and fwd and 7 * len(lab) + 10 > gx:
                ly -= 13  # a label wider than the gap sits above the line, clear of the boxes
            labels.append((lx, ly, lab))
    for n in nodes:
        x, y = pos[n]
        hi = n in hiset
        m = meta.get(n, {})
        kind = m.get("kind", "")
        fill, stroke, sw = {"stop": ("#fff4e0", "#b45309", "1.8"), "done": ("#e8f5ec", "#1f7a3f", "1.8")}.get(
            kind, ("#eef4ff", ACCENT, "2") if hi else ("#ffffff", "#8a94a3", "1.2"))
        svg.append('<rect x="%.0f" y="%.0f" width="%d" height="%d" rx="8" fill="%s" stroke="%s" stroke-width="%s"%s/>'
                   % (x, y, bw, bh, fill, stroke, sw, ' stroke-dasharray="5 3"' if kind == "stop" else ""))
        lines = _wrap(m.get("label", n), width=max(12, int(bw / 8)))
        sub = m.get("sub", "")
        if len(sub) > int(bw / 6.2) and " · " in sub:  # too long for the box: drop who, keep the time
            sub = sub.split(" · ", 1)[1]
        y0 = y + bh / 2 - (len(lines) - 1) * 8 + 4.5 - (8 if sub else 0)
        if sub:
            svg.append('<text x="%.0f" y="%.0f" font-size="11.5" text-anchor="middle" fill="%s">%s</text>'
                       % (x + bw / 2, y0 + len(lines) * 16 + 1, "#b45309" if kind == "stop" else "#5f6b7a", esc(sub if len(sub) <= int(bw / 6.2) else sub[: int(bw / 6.2) - 1] + "\u2026")))
        for i, t in enumerate(lines):
            svg.append('<text x="%.0f" y="%.0f" font-size="13" text-anchor="middle" fill="#1d2330">%s</text>'
                       % (x + bw / 2, y0 + i * 16, esc(t)))
    for lx, ly, lab in labels:  # labels last, on an opaque mask, so lines never cross the text
        w = 7 * len(lab) + 10
        svg.append('<rect x="%.0f" y="%.0f" width="%d" height="17" rx="3" fill="#ffffff"/>' % (lx - w / 2, ly - 12, w))
        svg.append('<text x="%.0f" y="%.0f" font-size="11.5" text-anchor="middle" fill="#46505e">%s</text>'
                   % (lx, ly + 1, esc(lab)))
    svg.append("</svg>")
    return "".join(svg)



# ---------- before and after (box -> box per row) ----------

def before_after(rows):
    """rows: [[thing, before, after]]: one row per thing, a grey Before box, an arrow, a blue After box."""
    if not rows:
        return ""
    out = ['<div class="vb-ba"><span class="vb-bah"></span><span class="vb-bah">Today</span><span></span>'
           '<span class="vb-bah">After this plan</span>']
    for r in rows:
        thing, before, after = (list(r) + ["", "", ""])[:3]
        out.append('<span class="vb-bat">%s</span><div class="vb-bab">%s</div><span class="vb-baa">\u2192</span>'
                   '<div class="vb-baf">%s</div>' % (inline(thing), inline(before), inline(after)))
    out.append("</div>")
    return "".join(out)


# ---------- standalone page ----------

def page(title, body, extra_css=""):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" '
            'content="width=device-width,initial-scale=1"><title>%s</title><style>'
            'body{margin:0;background:#f6f7f9}.vb-wrap{max-width:1100px;margin:0 auto;padding:20px 18px 48px}'
            '.vb-card{background:#fff;border:1px solid #d9dee5;border-radius:10px;padding:14px 16px;margin:12px 0}'
            'h1{font-size:21px;margin:0 0 6px}h2{font-size:16px;margin:0 0 8px}%s%s</style></head>'
            '<body class="vb"><div class="vb-wrap">%s</div></body></html>' % (esc(title), css(), extra_css, body))
