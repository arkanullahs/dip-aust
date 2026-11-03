"""Shared helpers for the DIP deck lesson pages (graphs, grids, answer-script boxes, CSS)."""
import math
from fractions import Fraction as F
rhu = lambda v: math.floor(v + 0.5)  # slide rule: .5 rounds up

# ---------------------------------------------------------------- svg plot helper
def plot(xmax, ymax, curves=(), points=(), bands=(), notes=(), xticks=None, yticks=None,
         xlabel="r (input)", ylabel="s (output)", w=320, h=250, diag=False, caption=""):
    L, R, T, B = 46, 16, 14, 38
    pw, ph = w - L - R, h - T - B
    X = lambda x: L + x / xmax * pw
    Y = lambda y: T + ph - y / ymax * ph
    o = [f'<svg viewBox="0 0 {w} {h}" role="img" class="plot">']
    for b in bands:  # vertical band on x range, or horizontal on y range
        if b.get("axis", "x") == "x":
            o.append(f'<rect x="{X(b["a"]):.1f}" y="{T}" width="{X(b["b"]) - X(b["a"]):.1f}" height="{ph}" class="{b.get("cls", "band")}"/>')
        else:
            o.append(f'<rect x="{L}" y="{Y(b["b"]):.1f}" width="{pw}" height="{Y(b["a"]) - Y(b["b"]):.1f}" class="{b.get("cls", "band")}"/>')
    xticks = xticks if xticks is not None else [0, xmax]
    yticks = yticks if yticks is not None else [0, ymax]
    for t in xticks:
        v, lab = (t if isinstance(t, tuple) else (t, str(t)))
        o.append(f'<line x1="{X(v):.1f}" y1="{T}" x2="{X(v):.1f}" y2="{T + ph}" class="grid"/>')
        o.append(f'<text x="{X(v):.1f}" y="{T + ph + 14}" class="tick" text-anchor="middle">{lab}</text>')
    for t in yticks:
        v, lab = (t if isinstance(t, tuple) else (t, str(t)))
        o.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{L + pw}" y2="{Y(v):.1f}" class="grid"/>')
        o.append(f'<text x="{L - 6}" y="{Y(v) + 4:.1f}" class="tick" text-anchor="end">{lab}</text>')
    if diag:
        o.append(f'<line x1="{X(0)}" y1="{Y(0)}" x2="{X(xmax)}" y2="{Y(ymax)}" class="diag"/>')
    o.append(f'<line x1="{L}" y1="{T + ph}" x2="{L + pw}" y2="{T + ph}" class="axis"/>')
    o.append(f'<line x1="{L}" y1="{T}" x2="{L}" y2="{T + ph}" class="axis"/>')
    o.append(f'<text x="{L + pw / 2}" y="{h - 4}" class="axlab" text-anchor="middle">{xlabel}</text>')
    o.append(f'<text x="12" y="{T + ph / 2}" class="axlab" text-anchor="middle" transform="rotate(-90 12 {T + ph / 2})">{ylabel}</text>')
    for c in curves:
        pts = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in c["pts"])
        o.append(f'<polyline points="{pts}" class="cv {c.get("cls", "c1")}" fill="none"/>')
        if "label" in c:
            lx, ly = c["at"]
            o.append(f'<text x="{X(lx):.1f}" y="{Y(ly):.1f}" class="clab {c.get("cls", "c1")}t" text-anchor="{c.get("anchor", "start")}">{c["label"]}</text>')
    for p in points:
        o.append(f'<circle cx="{X(p[0]):.1f}" cy="{Y(p[1]):.1f}" r="3.6" class="pt {p[3] if len(p) > 3 else ""}"/>')
        if p[2]:
            o.append(f'<text x="{X(p[0]) + 6:.1f}" y="{Y(p[1]) - 6:.1f}" class="plab">{p[2]}</text>')
    for n in notes:
        o.append(f'<text x="{X(n[0]):.1f}" y="{Y(n[1]):.1f}" class="note" text-anchor="{n[3] if len(n) > 3 else "start"}">{n[2]}</text>')
    o.append("</svg>")
    svg = "".join(o)
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return f'<figure class="fig">{svg}{cap}</figure>'


def fn(f, xmax, n=120):
    return [(xmax * i / n, f(xmax * i / n)) for i in range(n + 1)]


def figs(*f):
    return '<div class="figrow">' + "".join(f) + "</div>"

# ---------------------------------------------------------------- html helpers
def mat(m, cap="", hi=None, small=False, pad=None, ctr=None):
    hi, pad = hi or set(), pad or set()
    cls = lambda r, c: " ".join(x for x, on in (("hi", (r, c) in hi), ("pad", (r, c) in pad), ("ctr", (r, c) == ctr)) if on)
    rows = "".join("<tr>" + "".join(f'<td class="{cls(r, c)}">{v}</td>' for c, v in enumerate(row)) + "</tr>" for r, row in enumerate(m))
    return f'<figure class="mat{" sm" if small else ""}"><table>{rows}</table>{f"<figcaption>{cap}</figcaption>" if cap else ""}</figure>'


def mats(*m):
    return '<div class="matrow">' + "".join(m) + "</div>"


def tbl(head, rows, cls=""):
    h = "".join(f"<th>{x}</th>" for x in head)
    b = "".join("<tr>" + "".join(f"<td>{x}</td>" for x in r) + "</tr>" for r in rows)
    return f'<div class="tw"><table class="t {cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def cases(lhs, rows):
    r = "".join(f'<div class="cv1">{a}</div><div class="cv2">{b}</div>' for a, b in rows)
    return f'<div class="cases"><span class="lhs">{lhs} =</span><div class="brace">{r}</div></div>'


def paper(tag, marks, body):
    return f'<section class="paper"><header><span class="ptag">{tag}</span><span class="pmarks">{marks}</span></header><div class="pbody">{body}</div></section>'


def idea(body):
    return f'<div class="idea"><span class="k">In plain words</span>{body}</div>'


def formula(body):
    return f'<div class="formula">{body}</div>'


def trap(body):
    return f'<div class="trap"><span class="k">Trap</span>{body}</div>'


def ans(body):
    return f'<div class="ans"><span class="k">Answer</span>{body}</div>'


def sec(id_, title, slides, tag, body):
    tg = f'<span class="tag {tag[0]}">{tag[1]}</span>' if tag else ""
    return f'<section class="sec" id="{id_}"><div class="sechead"><h2>{title}</h2><div class="meta"><span class="slides">slides {slides}</span>{tg}</div></div>{body}</section>'

EXAM, LIKELY, SHORT = ("exam", "Came in past papers"), ("likely", "On study list"), ("short", "Know in 2 lines")

CSS = """
/* Layout: one reading column; graphs and grids sit inline where the text uses them; paper answers look like an exam script with a margin rule */
:root{
  --bg:#f3f5f8; --surface:#ffffff; --fg:#1b2330; --fg2:#566173; --line:#d9dee6; --ink:#1f4fd1; --mark:#c2410c;
  --c1:#1f4fd1; --c2:#0f8a6a; --c3:#c2410c; --c4:#8b3fc7; --c5:#9a6a00; --band:rgba(31,79,209,.10); --band2:rgba(194,65,12,.10);
  --hi:#fde9c8; --paper:#fffefb; --margin:#e7a4a4;
  --f-display:"Bricolage Grotesque", "Segoe UI", system-ui, sans-serif;
  --f-body:"Atkinson Hyperlegible", "Segoe UI", system-ui, sans-serif;
  --f-mono:"JetBrains Mono", ui-monospace, Consolas, monospace;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#11151c; --surface:#181e27; --fg:#e4e8ef; --fg2:#9aa4b4; --line:#2b3441; --ink:#7ea2ff; --mark:#ff9b5e;
  --c1:#7ea2ff; --c2:#4fd1a8; --c3:#ff9b5e; --c4:#c792ff; --c5:#e6c15a; --band:rgba(126,162,255,.16); --band2:rgba(255,155,94,.14);
  --hi:#4a3517; --paper:#161b23; --margin:#7a3a3a; color-scheme:dark }}
:root[data-theme="dark"]{
  --bg:#11151c; --surface:#181e27; --fg:#e4e8ef; --fg2:#9aa4b4; --line:#2b3441; --ink:#7ea2ff; --mark:#ff9b5e;
  --c1:#7ea2ff; --c2:#4fd1a8; --c3:#ff9b5e; --c4:#c792ff; --c5:#e6c15a; --band:rgba(126,162,255,.16); --band2:rgba(255,155,94,.14);
  --hi:#4a3517; --paper:#161b23; --margin:#7a3a3a; color-scheme:dark }
body{background:var(--bg);color:var(--fg);font-family:var(--f-body);font-size:16.5px;line-height:1.6;
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:0 64px}
.wrap{max-width:860px;margin:0 auto}
header.top{padding-block:36px 8px}
header.top .eyebrow{font-family:var(--f-mono);font-size:12.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--fg2)}
h1{font-family:var(--f-display);font-weight:700;font-size:clamp(30px,5vw,44px);line-height:1.1;margin:6px 0 10px;text-wrap:balance}
h2{font-family:var(--f-display);font-weight:650;font-size:26px;line-height:1.2;margin:0;text-wrap:balance}
h3{font-family:var(--f-display);font-weight:600;font-size:19px;margin:26px 0 6px}
p,li{max-width:68ch} ul,ol{padding-left:1.3em} li{margin:3px 0}
b{font-weight:700}
nav.toc{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);display:flex;gap:6px;overflow-x:auto;padding-block:10px;border-bottom:1px solid var(--line);margin-bottom:8px}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--bg)}
nav.toc a{flex:none;font-size:13.5px;color:var(--fg);text-decoration:none;padding:4px 10px;border:1px solid var(--line);border-radius:999px;background:var(--surface)}
nav.toc a:hover,nav.toc a:focus-visible{border-color:var(--ink);color:var(--ink);outline:none}
.sec{padding-block:30px 6px;border-bottom:1px solid var(--line);scroll-margin-top:60px}
.sechead{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:8px 16px;margin-bottom:12px}
.meta{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.slides{font-family:var(--f-mono);font-size:12.5px;color:var(--fg2)}
.tag{font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:2px 8px;border-radius:4px}
.tag.exam{background:var(--mark);color:var(--bg)} .tag.likely{border:1px solid var(--ink);color:var(--ink)} .tag.short{border:1px solid var(--fg2);color:var(--fg2)}
.idea{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:12px 16px;margin:12px 0}
.k{display:block;font-family:var(--f-mono);font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--ink);margin-bottom:4px}
.formula{font-family:var(--f-mono);font-size:18px;padding:10px 16px;margin:12px 0;background:var(--surface);border:1.5px solid var(--ink);border-radius:6px;display:inline-block;max-width:100%;overflow-x:auto}
.trap{border-left:4px solid var(--mark);padding:6px 14px;margin:14px 0;background:var(--surface)} .trap .k{color:var(--mark)}
.ans{border:1.5px solid var(--c2);border-radius:6px;padding:8px 14px;margin:12px 0} .ans .k{color:var(--c2)}
.two{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:8px 24px;align-items:start}
.two>div{min-width:0}
@media (max-width:720px){.two{grid-template-columns:minmax(0,1fr)}}
.fig{margin:10px 0;max-width:100%} .fig.wide{max-width:420px}
.figrow{display:flex;flex-wrap:wrap;gap:12px 18px;align-items:flex-start}
.figrow .fig{flex:1 1 230px;max-width:340px}
figcaption{font-size:13.5px;color:var(--fg2);line-height:1.45;margin-top:4px;max-width:46ch}
svg.plot{width:100%;max-width:340px;height:auto;display:block}
.plot .grid{stroke:var(--line);stroke-width:1} .plot .axis{stroke:var(--fg2);stroke-width:1.4}
.plot .diag{stroke:var(--fg2);stroke-width:1;stroke-dasharray:4 4}
.plot .tick{fill:var(--fg2);font:11px var(--f-mono)} .plot .axlab{fill:var(--fg);font:600 12px var(--f-body)}
.plot .note{fill:var(--fg2);font:11.5px var(--f-body)} .plot .plab{fill:var(--fg);font:600 11.5px var(--f-mono)}
.plot .cv{stroke-width:2.6;stroke-linejoin:round;stroke-linecap:round}
.plot .c1{stroke:var(--c1)} .plot .c2{stroke:var(--c2)} .plot .c3{stroke:var(--c3)} .plot .c4{stroke:var(--c4)} .plot .c5{stroke:var(--c5)}
.plot .clab{font:600 12px var(--f-body)} .c1t{fill:var(--c1)} .c2t{fill:var(--c2)} .c3t{fill:var(--c3)} .c4t{fill:var(--c4)} .c5t{fill:var(--c5)}
.plot .pt{fill:var(--c1);stroke:var(--surface);stroke-width:1.5} .plot .pt.acc{fill:var(--mark)} .plot .pt.c3p{fill:var(--c3)}
.plot .band{fill:var(--band)} .plot .band2{fill:var(--band2)}
.plot .cellon{fill:var(--ink)} .plot .celloff{fill:var(--surface);stroke:var(--line)} .plot .cellout{fill:var(--mark)}
.plot .layer{fill:var(--surface);stroke:var(--ink);stroke-width:1.2} .plot .layer.hi{fill:var(--band);stroke-width:2}
.matrow{display:flex;flex-wrap:wrap;gap:12px 22px;align-items:flex-start;margin:10px 0}
figure.mat{margin:6px 0;max-width:100%;overflow-x:auto}
figure.mat table{border-collapse:collapse;font-family:var(--f-mono);font-size:14.5px;font-variant-numeric:tabular-nums}
figure.mat td{border:1px solid var(--fg2);min-width:2.3em;height:2em;text-align:center;padding:0 6px;background:var(--surface)}
figure.mat.sm td{min-width:1.7em;height:1.7em;font-size:13px}
figure.mat td.hi{background:var(--hi)}
.tw{overflow-x:auto;margin:10px 0;max-width:100%}
table.t{border-collapse:collapse;font-size:14.5px;font-variant-numeric:tabular-nums}
table.t th,table.t td{border-bottom:1px solid var(--line);padding:5px 12px;text-align:left;vertical-align:top}
table.t th{font-family:var(--f-mono);font-size:12px;letter-spacing:.04em;text-transform:uppercase;color:var(--fg2);font-weight:600}
table.t.narrow td{font-family:var(--f-mono);font-size:13.5px}
table.bits td{text-align:center;font-family:var(--f-mono)} table.bits th{text-align:left}
.cases{display:flex;align-items:center;gap:10px;margin:10px 0;font-family:var(--f-mono);font-size:15px;max-width:100%;overflow-x:auto}
.cases .lhs{flex:none}
.brace{display:grid;grid-template-columns:auto auto;gap:2px 20px;border-left:2.5px solid var(--fg);border-radius:12px 0 0 12px;padding:4px 0 4px 14px}
.paper{background:var(--paper);border:1px solid var(--line);border-radius:6px;margin:18px 0;position:relative;
  background-image:linear-gradient(to right,transparent 30px,var(--margin) 30px,var(--margin) 31.5px,transparent 31.5px)}
.paper header{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;padding:8px 14px 8px 44px;border-bottom:1px solid var(--line)}
.ptag{font-family:var(--f-mono);font-size:13px;font-weight:700;color:var(--mark)} .pmarks{font-family:var(--f-mono);font-size:12.5px;color:var(--fg2)}
.pbody{padding:6px 16px 12px 44px;min-width:0}
.q{font-style:italic;color:var(--fg2)}
.traps li{margin:6px 0}
a{color:var(--ink)}
@media (prefers-reduced-motion:no-preference){nav.toc a{transition:border-color .15s,color .15s}}
"""


def bars(vals, labels=None, caption="", ylabel="n<sub>k</sub>", xlabel="gray level", w=330, h=210, fmt=str, hi=(), cls="c1", show_zero=False):
    """Histogram bar chart. vals: list of heights; labels: x labels (default 0..n-1)."""
    labels = labels if labels is not None else list(range(len(vals)))
    n = len(vals)
    L, R, T, B = 40, 10, 18, 34
    pw, ph = w - L - R, h - T - B
    top = max(vals) or 1
    step = pw / n
    bw = max(2.0, step * 0.62)
    o = [f'<svg viewBox="0 0 {w} {h}" role="img" class="plot">']
    for f in (0.5, 1.0):
        y = T + ph - f * ph
        o.append(f'<line x1="{L}" y1="{y:.1f}" x2="{L + pw}" y2="{y:.1f}" class="grid"/>')
        o.append(f'<text x="{L - 6}" y="{y + 4:.1f}" class="tick" text-anchor="end">{fmt(top * f) if fmt is not str else (int(top * f) if (top * f) == int(top * f) else round(top * f, 2))}</text>')
    o.append(f'<line x1="{L}" y1="{T + ph}" x2="{L + pw}" y2="{T + ph}" class="axis"/><line x1="{L}" y1="{T}" x2="{L}" y2="{T + ph}" class="axis"/>')
    dense = n > 12
    for i, v in enumerate(vals):
        x = L + i * step + (step - bw) / 2
        bh = v / top * ph
        c = "barhi" if i in hi else "bar " + cls
        if v:
            o.append(f'<rect x="{x:.1f}" y="{T + ph - bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" class="{c}"/>')
            if not dense or True:
                o.append(f'<text x="{x + bw / 2:.1f}" y="{T + ph - bh - 4:.1f}" class="bval" text-anchor="middle">{fmt(v)}</text>')
        elif show_zero:
            o.append(f'<text x="{x + bw / 2:.1f}" y="{T + ph - 4:.1f}" class="bval" text-anchor="middle">0</text>')
        if not dense or v or i in (0, n - 1):
            o.append(f'<text x="{x + bw / 2:.1f}" y="{T + ph + 13:.1f}" class="tick" text-anchor="middle">{labels[i]}</text>')
    o.append(f'<text x="{L + pw / 2}" y="{h - 3}" class="axlab" text-anchor="middle">{xlabel}</text>')
    o.append(f'<text x="11" y="{T + ph / 2}" class="axlab" text-anchor="middle" transform="rotate(-90 11 {T + ph / 2})">{ylabel}</text></svg>')
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return f'<figure class="fig">{"".join(o)}{cap}</figure>'


def stairs(s, caption="", xlabel="input r<sub>k</sub>", ylabel="output s<sub>k</sub>", w=320, h=250):
    """Transformation function as the slide-40 staircase: s[r] held on [r, r+1)."""
    Lm = len(s) - 1
    pts = []
    for r, v in enumerate(s):
        if pts:
            pts.append((r, pts[-1][1]))
        pts += [(r, v), (r + 1 if r < Lm else r + 0.7, v)]
    big = Lm > 10
    tk = [t for t in range(0, Lm + 1, 4 if big else 1)]
    if tk[-1] != Lm:
        tk.append(Lm)
    return plot(Lm + 0.7, Lm, curves=[{"pts": pts, "cls": "c1"}], points=[(r, v, "") for r, v in enumerate(s)],
                xticks=tk, yticks=tk, xlabel=xlabel, ylabel=ylabel, w=w, h=h, caption=caption)


def page(title, eyebrow, h1, intro, toc, sections, extra=""):
    nav = "".join(f'<a href="#{i}">{t}</a>' for i, t in toc)
    return f"""<meta charset="utf-8"><title>{title}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=JetBrains+Mono:wght@400;600;700&display=swap">
<style>{CSS}
.plot .bar{{fill:var(--c1)}} .plot .bar.c2{{fill:var(--c2)}} .plot .bar.c3{{fill:var(--c3)}} .plot .barhi{{fill:var(--mark)}}
.plot .bval{{fill:var(--fg);font:600 10.5px var(--f-mono)}}
figure.mat td.pad{{color:var(--fg2);background:var(--bg);border-style:dashed}} figure.mat td.ctr{{outline:2.5px solid var(--mark);outline-offset:-3px;font-weight:700}}
</style>
<div class="wrap">
<header class="top"><div class="eyebrow">{eyebrow}</div><h1>{h1}</h1><p>{intro}</p></header>
<nav class="toc" aria-label="Sections">{nav}</nav>
{''.join(sections)}
{extra}
</div>"""


# ---------------------------------------------------------------- filter engine (decks 06, 07)
def win(img, r, c, mode="zero"):
    H, W = len(img), len(img[0])
    def at(i, j):
        if 0 <= i < H and 0 <= j < W:
            return img[i][j]
        if mode == "zero":
            return 0
        return img[min(max(i, 0), H - 1)][min(max(j, 0), W - 1)]
    return [[at(r + dr, c + dc) for dc in (-1, 0, 1)] for dr in (-1, 0, 1)]


def show_window(img, r, c, cap):
    """Image drawn with a ring of zero padding; the 3×3 window shaded, the centre outlined."""
    H, W = len(img), len(img[0])
    P = [[0] * (W + 2)] + [[0] + row + [0] for row in img] + [[0] * (W + 2)]
    pad = {(i, j) for i in range(H + 2) for j in range(W + 2) if i in (0, H + 1) or j in (0, W + 1)}
    hi = {(r + 1 + dr, c + 1 + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)}
    return mat(P, cap, hi=hi, pad=pad, ctr=(r + 1, c + 1), small=True)


flat = lambda w: [v for row in w for v in row]


def mean_line(w):
    v = flat(w)
    return f"({' + '.join(map(str, v))}) / 9 = {sum(v)}/9 = {sum(v) / 9:.2f}", F(sum(v), 9)


def med_line(w):
    v = sorted(flat(w))
    return f"sorted: {', '.join(map(str, v))} → 5th value = <b>{v[4]}</b>", v[4]


def mask_line(w, m):
    terms = [(m[i][j], w[i][j]) for i in range(3) for j in range(3) if m[i][j]]
    tot = sum(a * b for a, b in terms)
    return " + ".join(f"({a})({b})" for a, b in terms) + f" = <b>{tot}</b>", tot


def corr(img, m, r, c):
    w = win(img, r, c)
    return sum(m[i][j] * w[i][j] for i in range(3) for j in range(3))




# ---------------------------------------------------------------- step-by-step simulators (sim_kit.js)
import json as _json, html as _html, pathlib as _pl

SIM_FILTERS = {
    "mean": {"name": "Mean (box) 1/9", "k": [1] * 9, "n": 9},
    "weighted": {"name": "Weighted average 1/16", "k": [1, 2, 1, 2, 4, 2, 1, 2, 1], "n": 16},
    "median": {"name": "Median", "rank": 4, "rankName": "5th value (the median: 4 values below it, 4 above)", "rule": "No multiplying. Sort the 9 values and take the 5th."},
    "min": {"name": "Min", "rank": 0, "rankName": "1st value (the minimum)", "rule": "No multiplying. Sort the 9 values and take the 1st (smallest)."},
    "max": {"name": "Max", "rank": 8, "rankName": "9th value (the maximum)", "rule": "No multiplying. Sort the 9 values and take the 9th (largest)."},
    "four": {"name": "4-neighbour average 1/4", "k": [0, 1, 0, 1, 0, 1, 0, 1, 0], "n": 4},
    "identity": {"name": "Identity [0 0 0; 0 1 0; 0 0 0]", "k": [0, 0, 0, 0, 1, 0, 0, 0, 0], "n": 1},
    "shift": {"name": "Shift [0 0 0; 0 0 1; 0 0 0]", "k": [0, 0, 0, 0, 0, 1, 0, 0, 0], "n": 1},
    "sharpen": {"name": "Sharpen 2δ − box", "k": [-1, -1, -1, -1, 17, -1, -1, -1, -1], "n": 9},
    "slide8": {"name": "Slide 8 kernel [−1 0 1; 2 1 2; 1 −2 0]", "k": [-1, 0, 1, 2, 1, 2, 1, -2, 0], "n": 1},
    "lappos": {"name": "Positive Laplacian [0 1 0; 1 −4 1; 0 1 0]", "k": [0, 1, 0, 1, -4, 1, 0, 1, 0], "n": 1},
    "lapneg": {"name": "Negative Laplacian [0 −1 0; −1 4 −1; 0 −1 0]", "k": [0, -1, 0, -1, 4, -1, 0, -1, 0], "n": 1},
    "lappos8": {"name": "Laplacian 8-nbr [1 1 1; 1 −8 1; 1 1 1]", "k": [1, 1, 1, 1, -8, 1, 1, 1, 1], "n": 1},
    "lapneg8": {"name": "Laplacian 8-nbr [−1 −1 −1; −1 8 −1; −1 −1 −1]", "k": [-1, -1, -1, -1, 8, -1, -1, -1, -1], "n": 1},
    "sharp_neg": {"name": "Sharpen in 2 steps: negative Laplacian, then g = f + ∇²f", "k": [0, -1, 0, -1, 4, -1, 0, -1, 0], "n": 1, "post": 1},
    "sharp_pos": {"name": "Sharpen in 2 steps: positive Laplacian, then g = f − ∇²f", "k": [0, 1, 0, 1, -4, 1, 0, 1, 0], "n": 1, "post": -1},
    "comp4": {"name": "Single-pass sharpen [0 −1 0; −1 5 −1; 0 −1 0]", "k": [0, -1, 0, -1, 5, -1, 0, -1, 0], "n": 1},
    "comp8": {"name": "Single-pass sharpen [−1 −1 −1; −1 9 −1; −1 −1 −1]", "k": [-1, -1, -1, -1, 9, -1, -1, -1, -1], "n": 1},
    "sobel": {"name": "Sobel |Gx| + |Gy|", "kx": [-1, 0, 1, -2, 0, 2, -1, 0, 1], "ky": [-1, -2, -1, 0, 0, 0, 1, 2, 1]},
    "prewitt": {"name": "Prewitt |Gx| + |Gy|", "kx": [-1, 0, 1, -1, 0, 1, -1, 0, 1], "ky": [-1, -1, -1, 0, 0, 0, 1, 1, 1]},
    "roberts": {"name": "Roberts |z9 − z5| + |z8 − z6|", "kx": [0, 0, 0, 0, -1, 0, 0, 0, 1], "ky": [0, 0, 0, 0, 0, -1, 0, 1, 0]},
    "sobelx": {"name": "Sobel Gx only [−1 0 1; −2 0 2; −1 0 1]", "k": [-1, 0, 1, -2, 0, 2, -1, 0, 1], "n": 1},
    "sobely": {"name": "Sobel Gy only [−1 −2 −1; 0 0 0; 1 2 1]", "k": [-1, -2, -1, 0, 0, 0, 1, 2, 1], "n": 1},
    "lineh": {"name": "Line mask R1 horizontal [−1 −1 −1; 2 2 2; −1 −1 −1]", "k": [-1, -1, -1, 2, 2, 2, -1, -1, -1], "n": 1},
    "linep45": {"name": "Line mask R2 +45° [−1 −1 2; −1 2 −1; 2 −1 −1]", "k": [-1, -1, 2, -1, 2, -1, 2, -1, -1], "n": 1},
    "linev": {"name": "Line mask R3 vertical [−1 2 −1; −1 2 −1; −1 2 −1]", "k": [-1, 2, -1, -1, 2, -1, -1, 2, -1], "n": 1},
    "linem45": {"name": "Line mask R4 −45° [2 −1 −1; −1 2 −1; −1 −1 2]", "k": [2, -1, -1, -1, 2, -1, -1, -1, 2], "n": 1},
}

SIM_CSS = """
.simwrap{margin:14px 0}
.simcap{margin:0 0 6px;font-size:15px}
.sim{border:1.5px solid var(--ink);border-radius:8px;background:var(--surface);padding:12px 14px}
.sim:focus{outline:none}
.sim .ctl{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:end}
.sim .ctl:empty{display:none}
.sim label{display:flex;flex-direction:column;gap:3px;font-size:12px;color:var(--fg2);font-family:var(--f-mono);text-transform:uppercase;letter-spacing:.04em}
.sim select{font:14.5px var(--f-body);color:var(--fg);background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:5px 8px;max-width:100%}
.sim .btns{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 4px;align-items:center}
.sim button{font:600 14px var(--f-body);color:var(--fg);background:var(--bg);border:1px solid var(--fg2);border-radius:6px;padding:7px 12px;cursor:pointer}
.sim button.main{background:var(--ink);border-color:var(--ink);color:var(--surface)}
.sim button:disabled{opacity:.4;cursor:default}
.sim button:focus-visible,.sim select:focus-visible{outline:2px solid var(--mark);outline-offset:2px}
.sim .prog{font-family:var(--f-mono);font-size:12.5px;color:var(--fg2)}
.sim .simnote{font-size:14px;color:var(--fg2);margin:4px 0 0}
.sim .simnote:empty{display:none}
.sim .stage{display:flex;flex-wrap:wrap;gap:10px 20px;align-items:flex-start;margin-top:8px}
.sim .stage figure{margin:0;max-width:100%;overflow-x:auto}
.sim .stage .fig{flex:0 1 300px}
.sim td[data-jump]{cursor:pointer}
.sim td.new{background:var(--mark);color:var(--surface);font-weight:700}
.sim .rule{max-width:15em;font-size:14px;padding:8px 10px;border:1px dashed var(--fg2);border-radius:6px}
.sim .work{margin:10px 0 0;padding-left:1.2em}
.sim .work li{margin:5px 0;padding:4px 8px;border-left:3px solid transparent;max-width:none}
.sim .work li.now{border-left-color:var(--mark);background:var(--bg)}
.sim .work code{font-family:var(--f-mono);font-size:13.5px;white-space:normal}
.sim .work mark{background:var(--mark);color:var(--surface);padding:0 4px;border-radius:3px}
.sim .prodlist{display:grid;grid-template-columns:repeat(3,max-content);gap:2px 18px;font-family:var(--f-mono);font-size:13.5px;margin:4px 0}
.sim .plot .band2{fill:var(--band2)}
.sim td.on{background:var(--ink);color:var(--surface)}
.sim td.cov{outline:2.5px solid var(--mark);outline-offset:-3px}
.sim td.key{background:var(--mark);color:var(--surface)}
.sim td.off{border:none;background:transparent}
.sim td.ctr{box-shadow:inset 0 0 0 4px var(--c2)}
@media (max-width:520px){.sim .prodlist{grid-template-columns:repeat(2,max-content)}}
"""


def sim(cfg, caption=""):
    cap = f'<p class="simcap"><b>Try it, step by step:</b> {caption}</p>' if caption else ""
    return f'<div class="simwrap">{cap}<div class="sim" data-sim="{_html.escape(_json.dumps(cfg), quote=True)}"></div></div>'


def sim_assets(images=None, filters=None):
    data = _json.dumps({"images": images or {}, "filters": filters or SIM_FILTERS})
    js = _pl.Path(__file__).with_name("sim_kit.js").read_text(encoding="utf-8")
    return f"<style>{SIM_CSS}</style><script>window.SIM_DATA = {data};</script><script>{js}</script>"
