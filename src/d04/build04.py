"""Builds deck04_lesson.html: deck 04 lesson with SVG graphs and paper-style solved answers.
All numbers are computed here, so the page cannot disagree with the maths."""
import math, html, pathlib

OUT = pathlib.Path(__file__).with_name("deck04_lesson.html")
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
def mat(m, cap="", hi=None, small=False):
    hi = hi or set()
    rows = "".join("<tr>" + "".join(f'<td class="{"hi" if (r, c) in hi else ""}">{v}</td>' for c, v in enumerate(row)) + "</tr>" for r, row in enumerate(m))
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

S = []  # sections

# ================================================================ 0. start
S.append(sec("start", "Start here: what this chapter is about", "before 4", None, f"""
<p>An image is a <b>grid of numbers</b>. Each number is one pixel's brightness. <b>0 is black</b>. The biggest number is white.</p>
<p>Each pixel is stored in <b>k bits</b>. That gives <b>L = 2<sup>k</sup></b> gray levels, numbered <b>0 to L−1</b>.</p>
{tbl(["bits k", "L = 2<sup>k</sup>", "range", "where you meet it"],
     [["1", "2", "0–1", "binary image (black/white)"], ["3", "8", "0–7", "most exam grids"], ["5", "32", "0–31", "slide 13 exercise"],
      ["8", "256", "0–255", "normal photos"], ["10", "1024", "0–1023", "Fall 25 quiz"]])}
<p>This whole chapter does one thing: take every pixel, put its number through a <b>rule</b>, and write down the new number.
Old number = <b>r</b>, new number = <b>s</b>, rule = <b>T</b>. So <b>s = T(r)</b>. The same rule is used for every pixel.</p>
<h3>How to read a transformation graph</h3>
<p>Every graph in this chapter has the <b>old value r</b> on the x-axis and the <b>new value s</b> on the y-axis.
Find your pixel on the x-axis, go up to the line, then read the new value on the y-axis.</p>
{figs(plot(255, 255, curves=[{"pts": fn(lambda r: 255 * (r / 255) ** 0.5, 255), "cls": "c1", "label": "above diagonal: brighter", "at": (60, 205)},
                              {"pts": fn(lambda r: 255 * (r / 255) ** 2.2, 255), "cls": "c3", "label": "below: darker", "at": (150, 40)}],
            diag=True, notes=[(150, 120, "diagonal: s = r, no change", "start")], xticks=[0, 255], yticks=[0, 255],
            caption="Above the dashed diagonal, output is bigger than input, so the picture gets brighter. Below it, darker."))}
{paper("Fall 25 Quiz 2(b)", "3 marks", f"""
<p class="q">How many shades of gray are possible in a 10-bit grayscale image? Show the numeric range. Write the expression for intensity resolution.</p>
<p>Intensity resolution = number of gray levels a pixel can take. With k bits per pixel:</p>
{formula("L = 2<sup>k</sup>")}
<p>Here k = 10, so L = 2<sup>10</sup> = <b>1024</b> shades.</p>
<p>Range: 0 to L − 1 = <b>0 to 1023</b> (0 = black, 1023 = white).</p>
{ans("1024 gray levels, from 0 to 1023. General expression: L = 2<sup>k</sup>, range [0, 2<sup>k</sup> − 1].")}
""")}
"""))

# ================================================================ 1. enhancement
def opsvg():
    def grid(x0, y0, fill):
        o = []
        for i in range(5):
            for j in range(5):
                cls = "cellon" if fill(i, j) else "celloff"
                o.append(f'<rect x="{x0 + j * 14}" y="{y0 + i * 14}" width="13" height="13" class="{cls}"/>')
        return "".join(o)
    out = '<rect x="0" y="0" width="13" height="13" class="cellout"/>'
    o = ['<svg viewBox="0 0 330 120" class="plot ops" role="img">']
    titles = [("Point", lambda i, j: i == 2 and j == 2), ("Local", lambda i, j: 1 <= i <= 3 and 1 <= j <= 3), ("Global", lambda i, j: True)]
    for k, (t, f) in enumerate(titles):
        x0 = 8 + k * 110
        o.append(grid(x0, 18, f))
        o.append(f'<text x="{x0 + 35}" y="12" class="axlab" text-anchor="middle">{t}</text>')
        o.append(f'<text x="{x0 + 35}" y="104" class="tick" text-anchor="middle">input pixels used</text>')
        o.append(f'<line x1="{x0 + 74}" y1="53" x2="{x0 + 86}" y2="53" class="axis"/>')
        o.append(f'<rect x="{x0 + 88}" y="46" width="13" height="13" class="cellout"/>')
    o.append("</svg>")
    return '<figure class="fig wide">' + "".join(o) + "<figcaption>Dark cells = input pixels the rule looks at. Right square = the one output pixel.</figcaption></figure>"

S.append(sec("enh", "Image enhancement and the 3 kinds of operation", "4–6", LIKELY, f"""
<p><b>Slide 4. Image enhancement</b> means processing an image so the result is <b>more suitable than the original for a specific application</b>.
The slide stresses <b>problem oriented</b>: the best result for an X-ray is not the best result for a satellite photo.</p>
<ul>
<li><b>Spatial domain</b>: change the pixel values directly. This chapter.</li>
<li><b>Frequency domain</b>: change the Fourier transform of the image. Not in your syllabus.</li>
<li><b>Combination methods</b>: both together.</li>
</ul>
<p><b>Slide 5. Three kinds of operation.</b> Ask yourself: to make one new pixel, which old pixels do I look at?</p>
{opsvg()}
<ul>
<li><b>Point / pixel operation</b>: output at (x,y) depends <b>only on the input at (x,y)</b>. Everything in this deck.</li>
<li><b>Local operation</b>: depends on the <b>neighbourhood</b> of (x,y). Filters, decks 06–07.</li>
<li><b>Global operation</b>: depends on <b>all</b> pixels of the image. Histogram equalization, deck 05.</li>
</ul>
<p><b>Slide 6.</b> Intensity transformation functions remap pixel values to new intensities. General form <b>s = T(r)</b>. Used for image <b>enhancement</b> and <b>preprocessing</b>.</p>
"""))

# ================================================================ 2. family
fam = plot(255, 255, curves=[
    {"pts": [(0, 255), (255, 0)], "cls": "c4", "label": "negative", "at": (20, 225)},
    {"pts": fn(lambda r: 255 * math.log(1 + r) / math.log(256), 255), "cls": "c1", "label": "log", "at": (8, 175)},
    {"pts": fn(lambda r: 255 * (r / 255) ** 0.4, 255), "cls": "c2", "label": "nth root", "at": (70, 232)},
    {"pts": fn(lambda r: 255 * (r / 255) ** 2.5, 255), "cls": "c3", "label": "nth power", "at": (185, 70)},
    {"pts": fn(lambda r: 255 * (math.exp(r / 255 * math.log(256)) - 1) / 255, 255), "cls": "c5", "label": "inverse log", "at": (228, 22), "anchor": "end"},
], diag=True, notes=[(118, 128, "identity", "start")], xticks=[0, (64, "L/4"), (128, "L/2"), (192, "3L/4"), (255, "L−1")],
    yticks=[0, (128, "L/2"), (255, "L−1")], w=340, h=280,
    caption="Slide 7 graph. Log and nth root lie above the diagonal (brighten). nth power and inverse log lie below (darken). Negative runs downhill.")

S.append(sec("family", "The family of transformations", "7–9", LIKELY, f"""
<p><b>Slide 7.</b> Intensity transformation functions fall into <b>2 approaches</b>. Learn this list as it is; it answers "classify the intensity transformations".</p>
<div class="two">
<div><ol>
<li><b>Basic intensity transformations</b>
<ul><li>Linear: <b>negative</b>, <b>identity</b></li><li>Logarithmic: <b>log</b>, <b>inverse log</b></li><li>Power-law: <b>nth power</b>, <b>nth root</b></li></ul></li>
<li><b>Piecewise linear transformations</b>
<ul><li>Contrast stretching, thresholding</li><li>Gray-level slicing</li><li>Bit-plane slicing</li></ul></li>
</ol></div>
<div>{fam}</div></div>
<p><b>Slide 8. Identity</b>: <b>s = r</b>. Output = input, so the image does not change. It is on the graph only for completeness.</p>
<p><b>Slide 9. Intensity scaling</b>: <b>s = a·r</b>. Every pixel is multiplied by a. With a &gt; 1 the face image becomes brighter.</p>
"""))

# ================================================================ 3. negative
neg12_in = [[100, 110, 90, 95], [98, 140, 145, 135], [89, 90, 88, 85], [102, 105, 99, 115]]
neg12_out = [[255 - v for v in r] for r in neg12_in]
neg13_in = [[21, 26, 29, 30], [19, 21, 20, 30], [16, 16, 26, 31], [19, 18, 27, 23]]
neg13_out = [[31 - v for v in r] for r in neg13_in]
def negrows(m, top):
    vals = sorted({v for r in m for v in r})
    return [[v, f"{top} − {v}", top - v] for v in vals]

S.append(sec("neg", "Negative transformation", "10–13", EXAM, f"""
{idea("Flip the brightness, like a film negative. Black becomes white, white becomes black, and middle gray stays near the middle.")}
{figs(plot(255, 255, curves=[{"pts": [(0, 255), (255, 0)], "cls": "c4", "label": "s = (L−1) − r", "at": (120, 150)}],
           points=[(0, 255, "(0, L−1)"), (255, 0, ""), (100, 155, "r=100 → s=155", "acc")], xticks=[0, 100, (255, "L−1")], yticks=[0, 155, (255, "L−1")],
           caption="Straight line going down. Black input (0) gives white output (L−1)."))}
{formula("s = (L − 1) − r")}
<p><b>Why use it (slide 11):</b> when an image has big dark areas, small white or gray details inside them are hard to see (X-ray, mammogram).
After the negative they become dark on a light background, which the eye reads more easily.</p>
{paper("Slide 12 · Example 1", "worked", f"""
<p class="q">The matrix gives the pixel values of an 8-bit image r. Apply the negative transform and find the resulting pixel values.</p>
<p><b>Given:</b> 8-bit image, so L = 2<sup>8</sup> = 256.</p>
<p><b>Formula:</b> s = (L − 1) − r = 255 − r. Apply it to every pixel.</p>
{tbl(["r", "255 − r", "s"], negrows(neg12_in, 255), "narrow")}
{mats(mat(neg12_in, "input image r"), mat(neg12_out, "negative image s"))}
""")}
{paper("Slide 13 · Exercise", "solved", f"""
<p class="q">The matrix gives the pixel values of a 5-bit image r. Apply the negative transform.</p>
<p><b>Given:</b> 5-bit image, so L = 2<sup>5</sup> = 32 and L − 1 = 31.</p>
<p><b>Formula:</b> s = 31 − r.</p>
{tbl(["r", "31 − r", "s"], negrows(neg13_in, 31), "narrow")}
{mats(mat(neg13_in, "input r (5-bit)"), mat(neg13_out, "negative s"))}
""")}
{paper("F23 Q1(b), first half", "2 marks", f"""
<p class="q">Write a short note on the Negative transformation.</p>
<p>The negative transformation is a basic linear intensity transformation that <b>reverses the intensity values</b> of an image (light ↔ dark).
For an image with L gray levels in the range [0, L−1]:</p>
{formula("s = (L − 1) − r")}
<p>where r is the input and s the output gray level. Its graph is a straight line from (0, L−1) down to (L−1, 0) <i>[draw it]</i>.</p>
<p>Use: enhancing white or gray detail embedded in dark regions, especially when black areas dominate, e.g. medical X-ray and mammogram images.</p>
<p>Example (8-bit): r = 100 gives s = 255 − 100 = 155.</p>
""")}
{trap("Find L from the bits before anything else. 3-bit: s = 7 − r. 5-bit: s = 31 − r. 8-bit: s = 255 − r.")}
"""))

# ================================================================ 4. threshold
thr_in = [[2, 1, 2, 1, 0], [7, 1, 4, 3, 2], [2, 4, 1, 3, 7], [1, 3, 4, 6, 3], [1, 4, 1, 3, 4]]
thr_out = [[1 if v > 3 else 0 for v in r] for r in thr_in]
S.append(sec("thr", "Thresholding", "14–15", LIKELY, f"""
{idea("Pick one cut value k. Every pixel brighter than k turns white, every other pixel turns black. Like a height check at a gate: taller than k goes in, everyone else stays out.")}
<div class="two"><div>
{cases("s", [("1.0 (white)", "if r &gt; k"), ("0.0 (black)", "if r ≤ k")])}
<ul>
<li>The output has only 2 values, so it is a <b>binary image</b>.</li>
<li>It <b>darkens levels below k</b> and <b>brightens levels above k</b>: the strongest possible contrast enhancement.</li>
<li>Main job: <b>separate the foreground (object) from the background</b>. That is segmentation.</li>
<li>Slide 15: the moon photo becomes a white moon on a black sky.</li>
</ul></div>
<div>{plot(255, 1, curves=[{"pts": [(0, 0), (120, 0), (120, 1), (255, 1)], "cls": "c1"}], xticks=[0, (120, "k"), (255, "L−1")],
           yticks=[0, (1, "1")], notes=[(130, 0.85, "r &gt; k → white"), (10, 0.1, "r ≤ k → black")],
           caption="A step: flat at 0 up to k, then a jump to the top.")}</div></div>
{paper("Mini example (slide 75 image, T = 3)", "worked", f"""
<p><b>Given:</b> 3-bit image, threshold T = 3. Rule: s = 1 if r &gt; 3, otherwise s = 0.</p>
<p>Values 0, 1, 2, 3 become 0. Values 4, 5, 6, 7 become 1.</p>
{mats(mat(thr_in, "input r"), mat(thr_out, "thresholded s"))}
""")}
"""))

# ================================================================ 5. log
c10 = 255 / math.log10(256)
logrows = [[r, 1 + r, f"{math.log10(1 + r):.4f}", f"{c10 * math.log10(1 + r):.1f}", rhu(c10 * math.log10(1 + r))] for r in [0, 1, 5, 10, 50, 100, 200, 255]]
logfig = plot(255, 255, curves=[{"pts": fn(lambda r: c10 * math.log10(1 + r), 255), "cls": "c1", "label": "s = c·log(1+r)", "at": (110, 196)}], diag=True,
              bands=[{"a": 0, "b": 50, "cls": "band"}, {"a": 0, "b": 181, "axis": "y", "cls": "band2"}],
              points=[(50, 181, "50 → 181", "acc"), (100, 212, ""), (255, 255, "")], xticks=[0, 50, 100, 255], yticks=[0, 181, 212, 255],
              caption="Inputs 0–50 (narrow strip) spread over outputs 0–181 (wide strip): dark values expanded. Inputs 100–255 squeeze into 212–255: bright values compressed.")
S.append(sec("log", "Log transformation (and inverse log)", "16–21", EXAM, f"""
{idea("Some images have a huge range of values. A Fourier spectrum runs from 0 to 1,500,000, but a screen shows only 0–255. Shown as it is, you see one bright dot and black everywhere else. The log curve rises fast at first and then flattens, so it spreads the small values apart and squeezes the big ones together.")}
<div class="two"><div>
{formula("s = c · log(1 + r)")}
<ul>
<li>c is a constant and r ≥ 0.</li>
<li>We add <b>1</b> because log(0) does not exist. With +1, r = 0 gives s = 0.</li>
<li><b>Low input values: range expanded.</b> Dark detail becomes visible.</li>
<li><b>High input values: range compressed.</b> Glare in bright regions is reduced.</li>
<li>Slide 17: compresses the range of pixel values, expands detail in dark areas, reduces glare in bright regions (astronomy, brain scan, chess piece).</li>
</ul></div>
<div>{logfig}</div></div>
<p><b>Slide 19. Application.</b> Log is useful when the input gray values have an <b>extremely large range</b>, i.e. when the dynamic range of the image far exceeds what the display can show. Example: <b>displaying the Fourier spectrum</b>. It is also called <b>dynamic-range compression</b>.</p>
<p><b>Slide 20.</b> Fourier spectrum with values from 0 to 1.5×10<sup>6</sup>. After a log transform with c = 1, the whole pattern becomes visible.</p>
<p><b>Slide 21. Inverse log</b> does the opposite: it <b>expands bright values and compresses dark values</b>. Slide formula: s = (1/c)·e<sup>(r+1)</sup>.</p>
{paper("Numeric log example (8-bit)", "worked", f"""
<p><b>Choose c</b> so that the top input stays at the top: c = (L−1) / log(1 + (L−1)) = 255 / log<sub>10</sub>(256) = 255 / 2.4082 = <b>{c10:.2f}</b>.</p>
<p><b>Formula:</b> s = {c10:.2f} × log<sub>10</sub>(1 + r), then round.</p>
{tbl(["r", "1 + r", "log<sub>10</sub>(1+r)", "× c", "s"], logrows, "narrow")}
<p>Inputs 0–50 went to 0–181 (spread out). Inputs 100–255 went to 212–255 (squeezed). Any log base gives the same s, as long as c uses the same base.</p>
""")}
{paper("Fall 25 Quiz 1", "6 marks", f"""
<p class="q">Discuss logarithmic transformations for image enhancement.</p>
<p><b>Definition.</b> The log transformation is a basic intensity transformation given by</p>
{formula("s = c · log(1 + r)")}
<p>where r is the input gray level, s the output gray level, c a constant and r ≥ 0. The 1 is added so that log 0 is avoided.</p>
<p><b>Shape.</b> <i>[Draw the log curve above the diagonal, as in the graph above.]</i> The curve is steep for small r and flat for large r.</p>
<p><b>Properties.</b></p>
<ol><li>For lower amplitudes of the input, the range is <b>expanded</b>: dark regions are spread out and their details become visible.</li>
<li>For higher amplitudes of the input, the range is <b>compressed</b>: bright regions are squeezed and glare is reduced.</li></ol>
<p><b>Application.</b> It is useful when the input values have an extremely large range, i.e. the dynamic range of the image far exceeds the capability of the display. Typical example: displaying the Fourier spectrum, whose values range from 0 to 1.5×10<sup>6</sup>; after the log transform with c = 1 the spectrum becomes visible. Hence it is also called <b>dynamic-range compression</b>.</p>
<p><b>Example.</b> For 8-bit with c = 105.89: r = 10 → 110, r = 50 → 181, r = 100 → 212, r = 255 → 255. A 0–50 input band becomes 0–181, while 100–255 shrinks to 212–255.</p>
<p><b>Inverse log</b> does the opposite: it expands high values and compresses dark ones.</p>
""")}
"""))

# ================================================================ 6. gamma
gim = [[1, 4, 6], [0, 2, 7], [3, 5, 2]]  # own practice image (no past paper), slide 23 gammas
def gmap(g): return {r: rhu(7 * (r / 7) ** g) for r in range(8)}
g04, g25 = gmap(0.5), gmap(2.0)
grow = lambda g: [[r, f"{r / 7:.4f}", f"{(r / 7) ** g:.4f}", f"{7 * (r / 7) ** g:.2f}", rhu(7 * (r / 7) ** g)] for r in range(8)]
gfig = plot(255, 255, curves=[
    {"pts": fn(lambda r: 255 * (r / 255) ** 0.1, 255), "cls": "c2", "label": "γ = 0.1", "at": (10, 238)},
    {"pts": fn(lambda r: 255 * (r / 255) ** 0.4, 255), "cls": "c1", "label": "γ = 0.4", "at": (40, 178)},
    {"pts": fn(lambda r: 255 * (r / 255) ** 2.5, 255), "cls": "c3", "label": "γ = 2.5", "at": (178, 60)},
    {"pts": fn(lambda r: 255 * (r / 255) ** 10, 255), "cls": "c5", "label": "γ = 10", "at": (240, 14), "anchor": "end"}],
    diag=True, notes=[(132, 128, "γ = 1", "start")], xticks=[0, (255, "L−1")], yticks=[0, (255, "L−1")],
    caption="Figure 3.6 idea: γ &lt; 1 curves bulge up (brighter), γ &gt; 1 curves sag down (darker), γ = 1 is the diagonal.")
gdots = plot(7, 7, curves=[{"pts": [(r, g04[r]) for r in range(8)], "cls": "c1", "label": "γ = 0.5", "at": (1.2, 5.6)},
                           {"pts": [(r, g25[r]) for r in range(8)], "cls": "c3", "label": "γ = 2.0", "at": (4.4, 1.2)}],
             points=[(r, g04[r], "") for r in range(8)] + [(r, g25[r], "", "c3p") for r in range(8)], diag=True,
             xticks=list(range(8)), yticks=list(range(8)), caption="Practice mapping drawn: γ = 0.5 points sit above the diagonal, γ = 2.0 below.")
S.append(sec("gamma", "Power-law (gamma) transformation", "22–31", EXAM, f"""
{idea("Log has one fixed shape. Gamma has a knob, γ, so you choose how much to brighten or darken. Turn γ below 1 for a brighter picture, above 1 for a darker one.")}
<div class="two"><div>
{formula("s = c · r<sup>γ</sup>")}
<p>c and γ (gamma) are positive constants. Different curves come from different γ.</p>
<ul>
<li><b>γ &lt; 1: brightens</b> the image (slide wording: "concave upward").</li>
<li><b>γ = 1: original</b>, linear mapping.</li>
<li><b>γ &gt; 1: darkens</b> the image (slide wording: "concave downward").</li>
</ul>
<p>Slide 23 waterfall: γ = 0.5 expands dark regions (brighter), γ = 2.0 compresses bright regions (darker).</p>
</div><div>{gfig}</div></div>
<p><b>How to compute gamma in the exam.</b> Scale the pixel to 0–1 first, apply the power, then scale back. Without scaling, 7<sup>2.5</sup> = 129 falls outside a 3-bit range.</p>
{formula("s = (L − 1) · ( r / (L − 1) )<sup>γ</sup> &nbsp;&nbsp;then round")}
{paper("Practice · gamma on a 3-bit image", "worked", f"""
<p class="q">The 3×3 image below is transformed using the gamma transformation with γ = 0.5 and γ = 2.0. Find the outputs and discuss the effect of changing γ.</p>
{mat(gim, "input image")}
<p><b>Step 1, find L.</b> The largest value is 7, so the image is 3-bit: L = 8, L − 1 = 7. Take c = 1 on the normalized values.</p>
<p><b>Step 2, formula.</b> s = 7 × (r/7)<sup>γ</sup>, rounded to the nearest integer.</p>
<p><b>Step 3, one value in full</b> (r = 3, γ = 0.5): 3/7 = 0.4286; 0.4286<sup>0.5</sup> = 0.6547; 7 × 0.6547 = 4.58 → <b>5</b>.</p>
<p><b>Step 4, table for every gray level, γ = 0.5:</b></p>
{tbl(["r", "r/7", "(r/7)<sup>0.5</sup>", "×7", "s"], grow(0.5), "narrow")}
<p><b>γ = 2.0:</b></p>
{tbl(["r", "r/7", "(r/7)<sup>2.0</sup>", "×7", "s"], grow(2.0), "narrow")}
<p><b>Step 5, replace each pixel.</b></p>
{mats(mat(gim, "input"), mat([[g04[v] for v in r] for r in gim], "γ = 0.5"), mat([[g25[v] for v in r] for r in gim], "γ = 2.0"))}
{gdots}
<p><b>Step 6, effect of γ.</b></p>
<ul><li>γ = 0.5 (&lt; 1) pushes values up: the image becomes <b>brighter</b>. Dark levels 1–3 are spread to 3–5 (more detail in dark areas); bright levels 4–7 bunch at 5–7.</li>
<li>γ = 2.0 (&gt; 1) pushes values down: the image becomes <b>darker</b>. Levels 0–1 collapse to 0 and 2–3 to 1; bright levels 5–7 are spread to 4–7 (more detail in bright areas).</li>
<li>So a smaller γ brightens and gives contrast to dark regions; a larger γ darkens and gives contrast to bright regions. γ = 1 leaves the image unchanged.</li></ul>
""")}
<h3>Gamma correction (slides 24–26)</h3>
{paper("Short note", "theory", """
<ul>
<li>Many devices (image capture, printing, display) respond to intensity according to a <b>power law</b>, so they <b>need to be corrected</b>. A CRT monitor has an intensity-to-voltage response with exponent about <b>1.8 to 2.5</b>, so images look <b>darker</b> than they should.</li>
<li><b>Gamma correction</b> is the process used to correct this power-law response: pre-process the image with s = c·r<sup>1/2.5</sup> so the monitor's darkening cancels out.</li>
<li>Background: human vision is nonlinear (more sensitive to small changes in dark tones than bright ones), while digital sensors are linear.</li>
<li>Different display devices have different gammas, so each needs its own correction.</li>
<li><b>Why needed:</b> to display an image accurately on screen (without correction it looks bleached out or, more likely, too dark); to reproduce colours accurately; and for general-purpose contrast manipulation.</li>
</ul>
""")}
<h3>Example pictures (slides 27–31)</h3>
<ul>
<li><b>MR image of a fractured spine</b> is too dark. With c = 1 and γ = 0.6, 0.4, 0.3 it gets brighter step by step. "Different curves highlight different detail."</li>
<li><b>Aerial photo of a runway</b> is washed out (too bright). γ = 3.0 and 4.0 are suitable; γ = 5.0 gives high contrast but some regions become too dark.</li>
<li>Slide 31 compares one mountain image: original, negative, log, and gamma 2.5.</li>
</ul>
{trap("Rule to remember: dark image → γ &lt; 1. Washed-out image → γ &gt; 1. Always normalize by L−1 before taking the power.")}
"""))

# ================================================================ 7. piecewise
pw = plot(255, 255, curves=[{"pts": [(0, 0), (80, 30)], "cls": "c1", "label": "piece 1", "at": (6, 40)},
                            {"pts": [(80, 30), (170, 225)], "cls": "c2", "label": "piece 2 (steep)", "at": (128, 110)},
                            {"pts": [(170, 225), (255, 255)], "cls": "c3", "label": "piece 3", "at": (182, 212)}],
          points=[(80, 30, "(r1, s1)"), (170, 225, "(r2, s2)")], diag=True, xticks=[0, (80, "r1"), (170, "r2"), (255, "L−1")],
          yticks=[0, (30, "s1"), (225, "s2"), (255, "L−1")], caption="Three straight pieces joined at two bend points. Each piece is the rule for its own range of r.")
S.append(sec("piece", "What does “piecewise” mean?", "32", LIKELY, f"""
{idea("Everything so far used one formula for all pixels. <b>Piecewise</b> means a different rule for different ranges of input. Think of a phone bill: the first 100 minutes cost one rate, every minute after that another rate. Each range has its own rule. <b>Piecewise linear</b> means each rule is a straight line, so the graph is several straight pieces joined at corners.")}
<div class="two"><div>
<p>In the graph, pixels with r from 0 to r1 follow piece 1, pixels from r1 to r2 follow piece 2, and pixels above r2 follow piece 3.
The corners (r1, s1) and (r2, s2) are what <b>you</b> choose. That is why these methods need more input from the user.</p>
<ul>
<li><b>Principal advantage:</b> some important transformations can be formulated <b>only</b> as a piecewise function.</li>
<li><b>Principal disadvantage:</b> their specification requires <b>more user input</b> than the previous transformations.</li>
<li><b>Types:</b> contrast stretching, gray/intensity level slicing, bit-plane slicing.</li>
</ul></div><div>{pw}</div></div>
"""))

# ================================================================ 8. contrast stretching
cs_in = [[100, 105, 107, 100], [120, 125, 120, 130], [115, 117, 112, 118], [130, 140, 145, 151]]
cs_out = [[5 * (v - 100) for v in r] for r in cs_in]
csrows = [[v, f"(255 − 0)/(151 − 100) × ({v} − 100) + 0 = 5 × {v - 100}", 5 * (v - 100)] for v in sorted({v for r in cs_in for v in r})]
def scurve(v):
    if v > 180: return 255
    if v < 90: return 0
    return 255 if v >= 100 else 0
part2 = [[scurve(v) for v in r] for r in cs_out]
def sp24(v):
    if v > 180: return 255
    if v < 90: return 0
    return 255 - v
sp24o = [[sp24(v) for v in r] for r in cs_out]
c_ex = [[[100] * 4] * 4, [[0, 10, 20, 30], [40, 60, 80, 90], [100, 120, 150, 180], [200, 220, 240, 255]],
        [[100, 105, 107, 100], [120, 125, 120, 130], [115, 117, 112, 118], [130, 140, 145, 150]]]
g_id = plot(255, 255, curves=[{"pts": [(0, 0), (255, 255)], "cls": "c1"}], points=[(70, 70, "(r1,s1)"), (185, 185, "(r2,s2)")],
            xticks=[0, (70, "r1"), (185, "r2"), (255, "L−1")], yticks=[0, (70, "s1"), (185, "s2"), (255, "L−1")], w=250, h=220,
            caption="(i) Identity: r1 = s1, r2 = s2")
g_th = plot(255, 255, curves=[{"pts": [(0, 0), (128, 0), (128, 255), (255, 255)], "cls": "c1"}], points=[(128, 0, "(r1, 0)"), (128, 255, "(r2, L−1)")],
            xticks=[0, (128, "r1 = r2"), (255, "L−1")], yticks=[0, (255, "L−1")], w=250, h=220, caption="(ii) Thresholding: r1 = r2, s1 = 0, s2 = L−1")
g_cs = plot(255, 255, curves=[{"pts": [(0, 0), (90, 30), (165, 225), (255, 255)], "cls": "c1"}], diag=True, points=[(90, 30, "(r1,s1)"), (165, 225, "(r2,s2)")],
            xticks=[0, (90, "r1"), (165, "r2"), (255, "L−1")], yticks=[0, (30, "s1"), (225, "s2"), (255, "L−1")], w=250, h=220,
            caption="(iii) Contrast stretching: r1 &lt; r2, s1 &lt; s2")
g_mm = plot(255, 255, curves=[{"pts": [(0, 0), (100, 0), (151, 255), (255, 255)], "cls": "c1", "label": "s = 5(r − 100)", "at": (132, 120)}],
            points=[(100, 0, "(100, 0)"), (151, 255, "(151, 255)"), (125, 125, "125 → 125", "acc")], bands=[{"a": 100, "b": 151}],
            xticks=[0, 100, 151, 255], yticks=[0, 125, 255], caption="Min-max stretch: the band 100–151 is spread across the whole 0–255.")
g_s = plot(255, 255, curves=[{"pts": [(0, 0), (90, 0)] + [(x, 255 / (1 + math.exp(-(x - 100) / 6))) for x in range(90, 181, 2)] + [(180, 255), (255, 255)], "cls": "c1"}],
           points=[(90, 0, "a = 90"), (180, 255, "b = 180")], xticks=[0, 90, (100, "m"), 180, 255], yticks=[0, 255],
           notes=[(104, 150, "steep at m = 100"), (10, 230, "r &gt; 180 → 255")], caption="Slide 42 S-curve: below 90 → 0, above 180 → 255, between them values move away from m.")
g_sp = plot(255, 255, curves=[{"pts": [(0, 0), (89.9, 0)], "cls": "c1"}, {"pts": [(90, 165), (180, 75)], "cls": "c4", "label": "255 − r", "at": (138, 150)},
                              {"pts": [(180.1, 255), (255, 255)], "cls": "c1"}],
            points=[(90, 165, "(90,165)"), (180, 75, "(180,75)")], xticks=[0, 90, 180, 255], yticks=[0, 75, 165, 255],
            caption="SP24 rule: three pieces. 0 below 90, negative between 90 and 180, 255 above 180.")
S.append(sec("cs", "Contrast stretching", "33–47", EXAM, f"""
<p><b>Slide 33.</b> Contrast stretching makes the bright pixels brighter and the dark pixels darker, which gives a higher-contrast image.</p>
<p><b>Slide 34. What is contrast?</b> Contrast is the <b>difference between the maximum and minimum pixel intensity</b> in an image.</p>
{mats(mat(c_ex[0], "100 − 100 = 0 · no contrast", small=True), mat(c_ex[1], "255 − 0 = 255 · high contrast", small=True), mat(c_ex[2], "150 − 100 = 50 · low contrast", small=True))}
{idea("A low-contrast image uses only a narrow band of gray levels, for example 100 to 151 out of 0 to 255. It looks foggy. Contrast stretching pulls that narrow band out to fill the whole range, like stretching a rubber band.")}
<p><b>Slide 35.</b> Contrast stretching is used to <b>expand the range of intensity levels of a low-contrast image</b>. Different ranges of gray levels can be enhanced independently.</p>
{formula("I<sub>new</sub> = (I − Min) × (NewMax − NewMin) / (Max − Min) + NewMin")}
<p>Read it as: how far the pixel is above the old minimum, times how much wider the new range is, plus the new starting point.</p>
<h3>The two control points (slides 36, 46–47)</h3>
<p>The function is controlled by two points, a = (r1, s1) and b = (r2, s2), with <b>r1 ≤ r2</b> and <b>s1 ≤ s2</b>, so the function is always increasing (the order of gray levels never flips). Where you put them decides what the function does:</p>
<ul>
<li>r1 = s1 and r2 = s2: a linear function with <b>no change</b> (identity).</li>
<li>r1 = r2, s1 = 0, s2 = L−1: a <b>thresholding</b> function, which gives a binary image.</li>
<li>In-between values: various degrees of spread in the output gray levels, i.e. <b>contrast stretching</b>.</li>
</ul>
{paper("SP23 2(d) · F22 A1(b)ii · SP22 2(a) · F21 B3(b)", "5–6 marks, asked 5 times", f"""
<p class="q">Points A(r1, s1) and B(r2, s2) control the piecewise linear transformation. Illustrate the relation between (r1, s1) and (r2, s2) for (i) linear identity (ii) thresholding (iii) contrast stretching.</p>
<p>The shape of the piecewise linear function s = T(r) is decided by the two points (r1, s1) and (r2, s2), with r1 ≤ r2 and s1 ≤ s2 so the function stays increasing.</p>
<p><b>(i) Linear identity:</b> r1 = s1 and r2 = s2. Both points lie on the diagonal, so the line is s = r and the gray levels do not change.</p>
<p><b>(ii) Thresholding:</b> r1 = r2, s1 = 0, s2 = L−1. The line jumps vertically at r1, so every pixel below r1 becomes 0 and every pixel above becomes L−1: a binary image.</p>
<p><b>(iii) Contrast stretching:</b> r1 &lt; r2 and s1 &lt; s2. The middle piece between r1 and r2 is steeper than 45°, so those gray levels are spread over a wider output range and contrast increases. Special case, min-max stretching: (r1, s1) = (r<sub>min</sub>, 0), (r2, s2) = (r<sub>max</sub>, L−1).</p>
{figs(g_id, g_th, g_cs)}
""")}
{paper("F23 Q3(d) part 1 = SP24 Q3(e) part 1", "5 marks", f"""
<p class="q">A 4×4 segment of an 8-bit image has range [100–151]. Find the output after contrast stretching to [0–255] using s = T(r), and express s = T(r).</p>
{mat(cs_in, "input image")}
<p><b>Given:</b> Min = 100, Max = 151, NewMin = 0, NewMax = 255.</p>
<p><b>Formula:</b> s = (r − Min) × (NewMax − NewMin)/(Max − Min) + NewMin</p>
<p>(NewMax − NewMin)/(Max − Min) = (255 − 0)/(151 − 100) = 255/51 = <b>5</b></p>
{formula("s = T(r) = 5 (r − 100)")}
<p><b>Apply to every gray level:</b></p>
{tbl(["r", "working", "s"], csrows, "narrow")}
<p><b>Output image:</b></p>
{mats(mat(cs_in, "input r"), mat(cs_out, "stretched s"))}
{g_mm}
<p>Check: the old contrast was 151 − 100 = 51; the new contrast is 255 − 0 = 255. Midpoint m = 125 (slide 40).</p>
""")}
{paper("F23 Q3(d) part 2", "5 marks", f"""
<p class="q">Apply the contrast-stretching graph with a = 90, b = 180, m = 100 to the stretched image: r &gt; 180 → 255; r &lt; 90 → 0; between them, r &lt; 100 moves close to 0 and r &gt; 100 moves close to 255. Show the final image.</p>
{g_s}
{cases("s", [("255", "if r &gt; 180"), ("close to 0 (darker)", "if 90 ≤ r &lt; 100"), ("close to 255 (brighter)", "if 100 &lt; r ≤ 180"), ("0", "if r &lt; 90")])}
<p><b>Apply to each stretched value</b> (taking the curve at its limit: the dark side goes to 0 and the bright side goes to 255):</p>
{tbl(["stretched r", "rule", "s"], [[v, ("&gt; 180" if v > 180 else "&lt; 90" if v < 90 else "90–100, toward 0" if v < 100 else "≥ 100, toward 255"), scurve(v)] for v in sorted({v for r in cs_out for v in r})], "narrow")}
<p>r = 100 sits exactly at m. I place it on the bright side; <b>write your assumption</b> in the script.</p>
{mats(mat(cs_out, "stretched r"), mat(part2, "final output"))}
<p>Bright pixels became brighter and dark pixels darker, so the result has higher contrast (here, the limit is a binary image).</p>
""")}
{paper("SP24 Q3(e) part 2", "4 marks", f"""
<p class="q">Apply to the stretched image: r &gt; 180 → 255; r &lt; 90 → 0; 90 ≤ r ≤ 180 → negative transformation. Show the final image.</p>
{cases("s", [("255", "if r &gt; 180"), ("255 − r", "if 90 ≤ r ≤ 180"), ("0", "if r &lt; 90")])}
{g_sp}
{tbl(["stretched r", "rule", "s"], [[v, ("&gt; 180 → 255" if v > 180 else "&lt; 90 → 0" if v < 90 else f"255 − {v}"), sp24(v)] for v in sorted({v for r in cs_out for v in r})], "narrow")}
{mats(mat(cs_out, "stretched r"), mat(sp24o, "final output"))}
""")}
<h3>Slide 41: thresholding as a special case</h3>
<p>Suppose k = 150. If r &gt; 150 then s = 1; if r &lt; 150 then s = 0. Pixels below 150 become 0 and pixels above become 1. This is thresholding, and it gives a binary image.</p>
<h3>Figure 3.10 (slides 43–47)</h3>
<ul>
<li>(a) the shape of the stretching function; (b) an 8-bit image with low contrast.</li>
<li>(c) <b>Min-max stretching</b>: (r1, s1) = (r<sub>min</sub>, 0), (r2, s2) = (r<sub>max</sub>, L−1), where r<sub>min</sub> and r<sub>max</sub> are the minimum and maximum gray levels in the image. The levels are stretched linearly from their original range to the full [0, L−1]. This is exactly the formula above.</li>
<li>(d) Thresholding at the mean: r1 = r2 = m, s1 = 0, s2 = L−1, where m is the mean gray level. The slide calls it <b>percentile stretching</b>. The result is binary.</li>
</ul>
"""))

# ================================================================ 9. slicing
def slice_fig(A, B, Lm, hi, with_bg, ticks=None, cap="", w=300):
    if with_bg:
        pts = [(0, 0), (A, A), (A, hi), (B, hi), (B, B), (Lm, Lm)]
    else:
        pts = [(0, 0), (A, 0), (A, hi), (B, hi), (B, 0), (Lm, 0)]
    xt = ticks or [0, (A, "A"), (B, "B"), (Lm, "L−1")]
    return plot(Lm, Lm, curves=[{"pts": pts, "cls": "c1" if with_bg else "c2"}], bands=[{"a": A, "b": B}], xticks=xt,
                yticks=[0, (hi, str(hi) if ticks else "L−1")], w=w, h=230, caption=cap)
sl_in = [100, 150, 220]
S.append(sec("gls", "Gray-level (intensity-level) slicing", "48–53", EXAM, f"""
{idea("Sometimes you care about one band of gray values only: bones in an X-ray at 120–200, blood vessels, a tumor. Slicing makes that band light up. Pixels inside [A, B] become bright. For the pixels outside, you choose: drop them to black, or leave them as they were.")}
<p><b>Slide 48.</b> Highlights a specific range of gray levels in an image. Similar to thresholding. Other levels can be <b>suppressed or maintained</b>. Useful when different features of an image are contained in different gray levels.</p>
<p><b>Slide 49. Two basic approaches:</b></p>
{figs(slice_fig(80, 160, 255, 255, False, cap="Approach 1, <b>without background</b>: [A, B] → L−1, everything else → a low level (0)."),
      slice_fig(80, 160, 255, 255, True, cap="Approach 2, <b>with background</b>: [A, B] → L−1, everything else unchanged (s = r)."))}
<p>The shaded strip is the chosen band [A, B]. In approach 2 the graph is the diagonal everywhere except inside the band, where it is lifted to the top.</p>
<p><b>Slides 50–52.</b> MATLAB cameraman: pixels between 100 and 200 become 255 (white). Approach 1: everything else becomes 0 (black). Approach 2: everything else stays the same.</p>
<p><b>Slide 53.</b> Aortic angiogram: slicing highlights the major blood vessels and shows the flow of the contrast medium, to detect blockages.</p>
{paper("Fall 25 Quiz 2(a)", "11 marks", f"""
<p class="q">A medical X-ray image (8-bit) needs its bone structures in the range [120, 200] enhanced. Apply gray-level slicing with both approaches. (i) Write the transformation functions [4] (ii) Show the mapping for pixel values 100, 150 and 220 [4] (iii) Sketch the transformation curves [3].</p>
<p><b>Given:</b> 8-bit, so L − 1 = 255. Band of interest A = 120, B = 200. Highlight level = 255.</p>
<p><b>(i) Transformation functions</b></p>
<p>Approach 1, without background (other levels suppressed):</p>
{cases("s", [("255", "if 120 ≤ r ≤ 200"), ("0", "otherwise")])}
<p>Approach 2, with background (other levels preserved):</p>
{cases("s", [("255", "if 120 ≤ r ≤ 200"), ("r", "otherwise")])}
<p><b>(ii) Mapping</b></p>
{tbl(["r", "inside [120, 200]?", "Approach 1 s", "Approach 2 s"], [[v, "yes" if 120 <= v <= 200 else "no", 255 if 120 <= v <= 200 else 0, 255 if 120 <= v <= 200 else v] for v in sl_in], "narrow")}
<p>r = 100 is below the band: approach 1 gives 0, approach 2 keeps 100. r = 150 is inside: both give 255. r = 220 is above: approach 1 gives 0, approach 2 keeps 220.</p>
<p><b>(iii) Curves</b></p>
{figs(slice_fig(120, 200, 255, 255, False, ticks=[0, 120, 200, 255], cap="Approach 1: 0, jump to 255 on [120, 200], back to 0."),
      slice_fig(120, 200, 255, 255, True, ticks=[0, 120, 200, 255], cap="Approach 2: s = r, lifted to 255 on [120, 200]."))}
<p>Result: approach 1 shows only the bones, white on black. Approach 2 shows the bones in white with the rest of the X-ray still visible.</p>
""")}
{paper("F23 Q1(b), second half", "2 marks", f"""
<p class="q">Write a short note on intensity-level slicing.</p>
<p>Intensity-level (gray-level) slicing <b>highlights a specific range [A, B] of gray levels</b> in an image. It is similar to thresholding, and it is useful when different features of an image lie in different gray levels (e.g. blood vessels in an angiogram).</p>
<p>Two basic approaches: (1) <b>without background</b>: highlight [A, B] and reduce all other levels to a low constant level; (2) <b>with background</b>: highlight [A, B] and preserve all other levels. <i>[Draw both small graphs.]</i></p>
""")}
{paper("SP23 1(b)iii · F22 A1(b)i, tumor case", "3 marks", f"""
<p class="q">For tumor detection from medical scans, which transformation function highlights specific ranges of pixel values?</p>
<p><b>Gray-level (intensity-level) slicing.</b> The tumor tissue occupies a particular band of gray values [A, B]. Slicing maps that band to a high value (L−1), so the tumor stands out.</p>
<p>It can be applied in two ways: without background (all other levels → 0, only the tumor region is visible) or with background (other levels unchanged, so the tumor is seen in its anatomical context).</p>
{cases("s", [("L − 1", "if A ≤ r ≤ B"), ("0  (or r)", "otherwise")])}
""")}
"""))

# ================================================================ 10. bit planes
def bits3(v): return [(v >> 2) & 1, (v >> 1) & 1, v & 1]
bp_img = [[6, 7, 6, 6, 7], [0, 0, 0, 1, 2], [1, 1, 1, 2, 3], [4, 5, 5, 4, 2], [6, 6, 6, 7, 7]]
bp_bin = [[format(v, "03b") for v in r] for r in bp_img]
pl = lambda m, k: [[bits3(v)[k] for v in r] for r in m]
A = [[167, 133, 111], [144, 140, 135], [159, 154, 148]]
Ab = [[format(v, "08b") for v in r] for r in A]
keep = lambda m, bitsl: [[sum(v & (1 << (b - 1)) for b in bitsl) for v in r] for r in m]
p2 = [[1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 0, 1, 1, 1], [1, 1, 0, 0, 0, 1, 1], [1, 0, 0, 0, 0, 0, 1], [1, 1, 0, 0, 0, 1, 1], [0, 0, 0, 0, 0, 0, 0], [1, 1, 1, 1, 1, 1, 1]]
p1 = [[1] * 7, [1] * 7, [1, 0, 0, 0, 0, 0, 1], [0] * 7, [0] * 7, [1] * 7, [1] * 7]
p0 = [[1] * 7, [1, 1, 1, 0, 1, 1, 1], [1, 1, 0, 0, 0, 1, 1], [1, 1, 1, 0, 1, 1, 1], [1, 1, 0, 0, 0, 1, 1], [1, 1, 1, 0, 1, 1, 1], [1] * 7]
sp25 = [[4 * p2[i][j] + 2 * p1[i][j] + p0[i][j] for j in range(7)] for i in range(7)]
combos = sorted({(p2[i][j], p1[i][j], p0[i][j]) for i in range(7) for j in range(7)}, reverse=True)

def stack_svg():
    o = ['<svg viewBox="0 0 330 250" class="plot" role="img">']
    for k in range(8):
        y = 30 + (7 - k) * 24
        o.append(f'<polygon points="40,{y + 18} 150,{y + 18} 190,{y} 80,{y}" class="{"layer hi" if k in (7,) else "layer"}"/>')
        lab = f"bit plane {k + 1}" + (" (MSB, ×128)" if k == 7 else " (LSB, ×1)" if k == 0 else f" (×{2 ** k})")
        o.append(f'<text x="200" y="{y + 13}" class="tick">{lab}</text>')
    o.append('<text x="115" y="20" class="axlab" text-anchor="middle">one 8-bit image</text></svg>')
    return '<figure class="fig">' + "".join(o) + "<figcaption>An 8-bit image is eight 1-bit images stacked like pages.</figcaption></figure>"

wt = '<div class="tw"><table class="t bits"><tr><th>position</th>' + "".join(f"<td>{p}</td>" for p in ["8th", "7th", "6th", "5th", "4th", "3rd", "2nd", "1st"]) + \
     '</tr><tr><th>value</th>' + "".join(f"<td>{2 ** (7 - i)}</td>" for i in range(8)) + \
     '</tr><tr><th>binary 155</th>' + "".join(f"<td>{b}</td>" for b in "10011011") + \
     '</tr><tr><th>decimal</th>' + "".join(f"<td>{int(b) * 2 ** (7 - i)}</td>" for i, b in enumerate("10011011")) + "</tr></table></div>"

S.append(sec("bit", "Bit-plane slicing", "54–74", EXAM, f"""
{idea("Every pixel is stored as bits: 167 is 10100111. Take bit 8 from every pixel and you get one black-and-white image, called bit plane 8. Take bit 7 from every pixel and you get plane 7, and so on. An 8-bit image is eight 1-bit images stacked on top of each other.")}
<div class="two"><div>
<p><b>Slide 54.</b> Bit-plane slicing separates an image into its individual bit layers, so you can see each bit's contribution to the overall image. It is widely used in <b>image compression, data hiding and feature extraction</b>.</p>
<p><b>Slide 55.</b> 0 = 00000000 and 255 = 11111111. Similarly 167 = 10100111 and 144 = 10010000. The left-most bit is the <b>most significant bit (MSB)</b>; the right-most is the <b>least significant bit (LSB)</b>.</p>
<p><b>Slide 59.</b> An 8-bit image is composed of <b>eight 1-bit planes</b>. Plane 1 holds the LSB of every pixel; plane 8 holds the MSB of every pixel.</p>
</div><div>{stack_svg()}</div></div>
<p><b>Slide 56. Binary to decimal.</b> Pixel value = 128 + 16 + 8 + 2 + 1 = <b>155</b>.</p>
{wt}
<p>A change in the MSB changes the value a lot (by 128). A change in the LSB hardly changes it (by 1).</p>
<p><b>Slide 57.</b> Higher-order bits contain most of the significant visual information. Lower-order bits contain subtle details and look like noise. Separating the planes shows the relative importance of each bit.</p>
<p><b>Slide 58. Why bit-plane slicing.</b> Using only the MSB reduces a gray image to a binary image. The three main goals:</p>
<ol><li>Converting a gray-level image to a <b>binary</b> image.</li>
<li>Representing an image with <b>fewer bits</b>, making it smaller: <b>compression</b>.</li>
<li><b>Enhancing</b> the image by focusing on chosen planes.</li></ol>
{paper("Slides 60–61 · 3-bit example", "worked", f"""
<p><b>Step 1.</b> Write each pixel of the 3-bit image in binary.</p>
{mats(mat(bp_img, "3-bit image"), mat(bp_bin, "binary"))}
<p><b>Step 2.</b> Collect the 1st bit of every pixel (MSB plane), the 2nd bit (centre plane), and the 3rd bit (LSB plane).</p>
{mats(mat(pl(bp_img, 0), "MSB plane (×4)"), mat(pl(bp_img, 1), "centre plane (×2)"), mat(pl(bp_img, 2), "LSB plane (×1)"))}
<p>Check one pixel: 6 = 110 gives MSB 1, centre 1, LSB 0.</p>
""")}
{paper("SP25 Q2(b)i · SP24 Q2(b)i", "2–3 marks", f"""
<p class="q">A 7×7 image segment has 3 bits per pixel. The binary images of bit planes 2, 1 and 0 are given. Construct the original image.</p>
{mats(mat(p2, "bit plane 2 (MSB)", small=True), mat(p1, "bit plane 1", small=True), mat(p0, "bit plane 0 (LSB)", small=True))}
<p><b>Rule:</b> in a 3-bit image the planes are 2, 1, 0 with weights 2<sup>2</sup> = 4, 2<sup>1</sup> = 2, 2<sup>0</sup> = 1. So</p>
{formula("f(x,y) = 4·b<sub>2</sub>(x,y) + 2·b<sub>1</sub>(x,y) + 1·b<sub>0</sub>(x,y)")}
<p><b>Every bit pattern that occurs:</b></p>
{tbl(["b2 b1 b0", "working", "value"], [[f"{a} {b} {c}", f"4·{a} + 2·{b} + 1·{c}", 4 * a + 2 * b + c] for a, b, c in combos], "narrow")}
<p>Example: row 2, column 1 has bits 1, 0, 1, so 4 + 0 + 1 = 5.</p>
{mat(sp25, "reconstructed original image")}
""")}
<h3>Rebuilding an image from chosen planes (slides 63–67)</h3>
<p>The nth bit of a pixel is worth <b>2<sup>n−1</sup></b>. To rebuild from some planes, keep only those bits, multiply each by its weight, and add.</p>
{paper("Slides 63–67", "worked", f"""
<p><b>Given:</b> A = [167 133 111; 144 140 135; 159 154 148] and its bit format:</p>
{mat(Ab, "A in binary")}
<p><b>8th plane only.</b> For 10100111, multiply only the 8th bit by 2<sup>7</sup> = 128: (1×128) + (0×0) + (1×0) + (0×0) + (0×0) + (1×0) + (1×0) + (1×0) = 128.
111 = <b>0</b>1101111 has 8th bit 0, so it gives 0.</p>
<p><b>Bitwise AND view</b> (slides 64–65): pixel AND 10000000 (128) keeps the 8th bit only; pixel AND 01000000 (64) keeps the 7th bit only.</p>
{mats(mat(keep(A, [8]), "8th plane image"), mat(keep(A, [7]), "7th plane image"), mat(keep(A, [8, 7]), "8th + 7th planes"))}
<p><b>8th + 7th combined</b> (slide 66): for 10100111, (1×128) + (0×64) = 128. For 01101111, (0×128) + (1×64) = 64.</p>
<p><b>Plane 1 (LSB) and plane 8 (MSB) as 0/1 images</b> (slides 71–72):</p>
{mats(mat([[v & 1 for v in r] for r in A], "plane 1 (LSB)"), mat([[(v >> 7) & 1 for v in r] for r in A], "plane 8 (MSB)"))}
""")}
{paper("Slide 74 · Exercise", "solved", f"""
<p class="q">Using the same A, reconstruct the image using only (a) the 5th and 4th bit planes (b) the 7th and 6th bit planes.</p>
<p><b>(a)</b> weights 2<sup>4</sup> = 16 and 2<sup>3</sup> = 8. Example 01101111 (111): 5th bit 0, 4th bit 1, so 0 + 8 = 8. Example 10011111 (159): 16 + 8 = 24.</p>
<p><b>(b)</b> weights 2<sup>6</sup> = 64 and 2<sup>5</sup> = 32. Example 01101111: 64 + 32 = 96. Example 10100111 (167): 0 + 32 = 32.</p>
{mats(mat(keep(A, [5, 4]), "(a) 5th + 4th"), mat(keep(A, [7, 6]), "(b) 7th + 6th"))}
<p>(a) is dark and noisy-looking because the low planes hold little of the picture; (b) keeps more structure.</p>
""")}
<p><b>Slides 62, 68–73.</b> Pictures (Lena, coins). Planes 1–4 look like noise; planes 5–8 show the picture. Rebuilding from planes 7+8, or 5+6+7+8, already looks close to the original.</p>
"""))

# ================================================================ 11. classwork
I = thr_in
neg = [[7 - v for v in r] for r in I]
s1 = [[5 if 3 <= v <= 5 else 0 for v in r] for r in I]
s2 = [[5 if 3 <= v <= 5 else v for v in r] for r in I]
S.append(sec("cw", "Slide 75 classwork, solved in full", "75", EXAM, paper("Slide 75 · Class work", "all parts", f"""
<p class="q">Apply these enhancement techniques to the 3-bit image I: digital negative; bit planes; thresholding with T = 3; intensity slicing with both approaches, a = 3, b = 5, raising the level to 5. Show the enhanced images.</p>
{mat(I, "I (3-bit)")}
<p><b>Given:</b> 3 bits per pixel, so L = 8 and L − 1 = 7.</p>
<p><b>(1) Digital negative.</b> s = (L − 1) − r = 7 − r. 0→7, 1→6, 2→5, 3→4, 4→3, 6→1, 7→0.</p>
{mat(neg, "negative")}
<p><b>(2) Bit planes.</b> Binary: 0 = 000, 1 = 001, 2 = 010, 3 = 011, 4 = 100, 6 = 110, 7 = 111.</p>
{mats(mat(pl(I, 0), "plane 2 (MSB, ×4)"), mat(pl(I, 1), "plane 1 (×2)"), mat(pl(I, 2), "plane 0 (LSB, ×1)"))}
<p>Check: 4·b2 + 2·b1 + b0 rebuilds I (e.g. 6 → 1, 1, 0 → 4 + 2 = 6).</p>
<p><b>(3) Thresholding, T = 3.</b></p>
{cases("s", [("1", "if r &gt; 3"), ("0", "if r ≤ 3")])}
{mat(thr_out, "thresholded")}
<p>Note: this equals the MSB plane, because r &gt; 3 exactly when the first bit is 1.</p>
<p><b>(4) Intensity slicing, [a, b] = [3, 5], highlight level 5.</b></p>
{cases("Approach 1: s", [("5", "if 3 ≤ r ≤ 5"), ("0", "otherwise")])}
{cases("Approach 2: s", [("5", "if 3 ≤ r ≤ 5"), ("r", "otherwise")])}
{mats(mat(s1, "without background"), mat(s2, "with background"))}
{figs(plot(7, 7, curves=[{"pts": [(0, 0), (3, 0), (3, 5), (5, 5), (5, 0), (7, 0)], "cls": "c2"}], bands=[{"a": 3, "b": 5}], xticks=list(range(8)), yticks=[0, 5, 7], w=250, h=210, caption="Approach 1"),
      plot(7, 7, curves=[{"pts": [(0, 0), (3, 3), (3, 5), (5, 5), (5, 5), (7, 7)], "cls": "c1"}], bands=[{"a": 3, "b": 5}], diag=True, xticks=list(range(8)), yticks=[0, 5, 7], w=250, h=210, caption="Approach 2"))}
""")))

# ================================================================ 12. case + traps
S.append(sec("case", "Case studies: which transformation for which problem", "mixed", LIKELY, f"""
{tbl(["The story says…", "Use", "Why"], [
    ["image too dark, details hidden in shadow", "gamma with γ &lt; 1, or log", "pushes low values up"],
    ["washed out, too bright", "gamma with γ &gt; 1", "pushes values down"],
    ["dull, foggy, faded, low contrast", "contrast stretching", "spreads the narrow range over 0 to L−1"],
    ["separate object from background, binary needed", "thresholding", "two output values"],
    ["highlight one gray range (bone, tumor, vessel)", "gray-level slicing", "lights up [A, B] only"],
    ["huge value range (Fourier spectrum)", "log", "dynamic-range compression"],
    ["white detail inside large dark areas (X-ray)", "negative", "dark ↔ light"],
    ["compression, data hiding, binary from MSB", "bit-plane slicing", "keeps only chosen bits"]])}
{paper("SP25 Q3(a)i", "4 marks", """
<p class="q">A scanned document suffers from uneven illumination, faded ink and background noise. Describe two enhancement techniques suitable for this case.</p>
<p><b>1. Contrast stretching.</b> Faded ink and paper occupy a narrow band of gray levels, so the text has low contrast. Stretching that band to the full [0, L−1] with s = (r − r<sub>min</sub>)(L−1)/(r<sub>max</sub> − r<sub>min</sub>) makes the ink darker and the paper brighter, which improves readability.</p>
<p><b>2. Power-law (gamma) transformation with γ &gt; 1.</b> Faded strokes are light gray. A γ greater than 1 pushes light values down, so faint strokes become darker and clearer against the background.</p>
<p>(Thresholding then turns the enhanced page into black text on white, ready for OCR. For the background noise, a median filter from the smoothing chapter is the usual partner.)</p>
""")}
"""))

S.append(sec("traps", "Traps and one-minute sheet", "all", None, f"""
<ul class="traps">
<li>Find <b>L from the bits</b> first. 3-bit is 0–7, not 0–255.</li>
<li>Gamma: <b>normalize</b> by L−1 before the power, multiply back, then round (.5 rounds up).</li>
<li>Contrast stretching: write the expression <b>s = T(r) = 5(r − 100)</b>, a working table, and the output grid. All three earn marks.</li>
<li>Slicing: always give <b>both approaches</b>, the functions in brace form, and <b>both graphs</b>.</li>
<li>(r1, s1), (r2, s2): three conditions <b>and three graphs</b>.</li>
<li>Bit weights: the nth bit is worth <b>2<sup>n−1</sup></b>. In a 3-bit image the planes are named 2, 1, 0 with weights 4, 2, 1.</li>
<li>When a rule leaves a value undefined (r = m exactly), <b>state your assumption</b> in the answer.</li>
</ul>
{tbl(["method", "formula", "one-line meaning"], [
    ["identity", "s = r", "no change"], ["scaling", "s = a·r", "a &gt; 1 brighter"], ["negative", "s = (L−1) − r", "dark ↔ light"],
    ["threshold", "s = 1 if r &gt; k else 0", "binary, object vs background"], ["log", "s = c·log(1+r)", "expand dark, compress bright"],
    ["inverse log", "s = (1/c)·e<sup>(r+1)</sup>", "expand bright, compress dark"], ["gamma", "s = c·r<sup>γ</sup>", "γ&lt;1 brighter, γ&gt;1 darker"],
    ["stretch", "(I−Min)(NewMax−NewMin)/(Max−Min) + NewMin", "fill whole range"],
    ["slicing", "[A,B] → L−1; else 0 or r", "light up one band"], ["bit plane", "Σ 2<sup>n−1</sup>·bit<sub>n</sub>", "image = stack of bits"]])}
"""))

# ---------------------------------------------------------------- page
toc = "".join(f'<a href="#{i}">{t}</a>' for i, t in [("start", "Start"), ("enh", "Enhancement"), ("family", "Family"), ("neg", "Negative"), ("thr", "Threshold"),
                                                    ("log", "Log"), ("gamma", "Gamma"), ("piece", "Piecewise"), ("cs", "Contrast stretch"), ("gls", "Slicing"),
                                                    ("bit", "Bit planes"), ("cw", "Classwork"), ("case", "Case studies"), ("traps", "Traps")])
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
page = f"""<meta charset="utf-8"><title>DIP Deck 04 Lesson</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=JetBrains+Mono:wght@400;600;700&display=swap">
<style>{CSS}</style>
<div class="wrap">
<header class="top"><div class="eyebrow">CSE 4227 · Chapter 3 · Deck 04</div>
<h1>Intensity Transformation, from zero</h1>
<p>Every slide you need, in plain words, with each graph drawn properly and past-paper questions solved the way you write them in the answer script.
Orange <span class="tag exam">Came in past papers</span> marks topics already asked.</p></header>
<nav class="toc" aria-label="Sections">{toc}</nav>
{''.join(S)}
</div>"""
OUT.write_text(page, encoding="utf-8")
print(OUT, len(page))
