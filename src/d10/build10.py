"""Builds deck10_lesson.html: chain code, first difference, shape number. Every code computed here and checked against data/answers.json."""
import sys, pathlib, math
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from kit import *

OUT = pathlib.Path(__file__).with_name("deck10_lesson.html")

# ---------------------------------------------------------------- chain code maths (same rules as scripts/solvers.py)
DIRS = {8: [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1)], 4: [(0, 1), (-1, 0), (0, -1), (1, 0)]}
NAMES = {8: ["right →", "up-right ↗", "up ↑", "up-left ↖", "left ←", "down-left ↙", "down ↓", "down-right ↘"], 4: ["right →", "up ↑", "left ←", "down ↓"]}


def unit(path):
    """closed list of corner pixels (row, col) -> every pixel on the way"""
    out = []
    for k, a in enumerate(path):
        b = path[(k + 1) % len(path)]
        dr, dc = (b[0] > a[0]) - (b[0] < a[0]), (b[1] > a[1]) - (b[1] < a[1])
        out += [(a[0] + s * dr, a[1] + s * dc) for s in range(max(abs(b[0] - a[0]), abs(b[1] - a[1])))]
    return out


def chain(U, n=8):
    return [DIRS[n].index((U[(k + 1) % len(U)][0] - a[0], U[(k + 1) % len(U)][1] - a[1])) for k, a in enumerate(U)]


def code_path(code, n=8):
    p = [(0, 0)]
    for c in code[:-1]:
        p.append((p[-1][0] + DIRS[n][c][0], p[-1][1] + DIRS[n][c][1]))
    r0, c0 = min(x[0] for x in p), min(x[1] for x in p)
    return [(r - r0, c - c0) for r, c in p]


def cfd(code, n=8, rule="next"):
    m = len(code)
    return [((code[(i + 1) % m] - code[i]) if rule == "next" else (code[i] - code[(i + 1) % m])) % n for i in range(m)]


def rots(seq):
    return [seq[k:] + seq[:k] for k in range(len(seq))]


def minrot(seq):
    R = rots(seq)
    return min(R), R.index(min(R))


def S(seq):
    return "".join(map(str, seq))


def D(s):
    return [int(ch) for ch in s]


# ---------------------------------------------------------------- drawings
def arrow(x1, y1, x2, y2, color, wd, cut):
    L = math.hypot(x2 - x1, y2 - y1)
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    ax, ay, bx, by = x1 + ux * cut, y1 + uy * cut, x2 - ux * cut, y2 - uy * cut
    h, w = 4 + wd * 1.6, 2 + wd
    pts = [(bx, by), (bx - ux * h - uy * w, by - uy * h + ux * w), (bx - ux * h + uy * w, by - uy * h - ux * w)]
    return (f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx - ux * h * .6:.1f}" y2="{by - uy * h * .6:.1f}" stroke="{color}" stroke-width="{wd}"/>'
            f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{color}"/>')


def compass(n=8, cap=None):
    o = '<svg viewBox="0 0 150 150" width="150" style="max-width:150px" role="img" class="plot">'
    for k in range(n):
        t = 2 * math.pi * k / n
        o += arrow(75, 75, 75 + 46 * math.cos(t), 75 - 46 * math.sin(t), "var(--c1)", 1.8, 0)
        o += f'<text x="{75 + 60 * math.cos(t):.1f}" y="{79 - 60 * math.sin(t):.1f}" text-anchor="middle" font-size="14" font-weight="700" fill="var(--fg)">{k}</text>'
    o += '<circle cx="75" cy="75" r="4.5" fill="var(--fg)"/></svg>'
    return f'<figure class="fig">{o}<figcaption>{cap or f"{n}-direction code: 0 = right, counting counterclockwise, {360 // n}° apart"}</figcaption></figure>'


def bfig(U, n=8, grid=None, cap="", xy=False, off=0, H=None, W=None, labels=True):
    """boundary drawing: shaded boundary pixels, numbered arrows, ringed start"""
    code = chain(U, n)
    H = H or max([len(grid) if grid else 0] + [p[0] + 1 for p in U])
    W = W or max([len(grid[0]) if grid else 0] + [p[1] + 1 for p in U])
    s, L, T = max(22, min(36, 330 // max(W, H))), 22, 16
    X, Y = (lambda p: L + p[1] * s + s / 2), (lambda p: T + p[0] * s + s / 2)
    on = set(U)
    o = [f'<svg viewBox="0 0 {L + W * s + 4} {T + H * s + 4}" width="{L + W * s + 4}" style="max-width:{L + W * s + 4}px" role="img" class="plot">']
    o += [f'<text x="{L + c * s + s / 2}" y="{T - 4}" text-anchor="middle" font-size="10" fill="var(--fg2)">{c + off}</text>' for c in range(W)]
    o += [f'<text x="{L - 5}" y="{T + r * s + s / 2 + 3}" text-anchor="end" font-size="10" fill="var(--fg2)">{(H - 1 - r) if xy else r + off}</text>' for r in range(H)]
    for r in range(H):
        for c in range(W):
            g = grid and r < len(grid) and grid[r][c] in "#1"
            fill = "var(--band)" if (r, c) in on else "var(--line)" if g else "none"
            o.append(f'<rect x="{L + c * s}" y="{T + r * s}" width="{s}" height="{s}" fill="{fill}" stroke="var(--line)"/>')
    for p in U:
        o.append(f'<circle cx="{X(p)}" cy="{Y(p)}" r="{s * .14:.1f}" fill="var(--fg)"/>')
    o.append(f'<circle cx="{X(U[0])}" cy="{Y(U[0])}" r="{s * .38:.1f}" fill="none" stroke="var(--c2)" stroke-width="2.5"/>')
    for k, a in enumerate(U):
        b = U[(k + 1) % len(U)]
        o.append(arrow(X(a), Y(a), X(b), Y(b), "var(--c1)", 1.6, s * .2))
        if labels:
            mx, my, dx, dy = (X(a) + X(b)) / 2, (Y(a) + Y(b)) / 2, X(b) - X(a), Y(b) - Y(a)
            ln = math.hypot(dx, dy)
            o.append(f'<text x="{mx - dy / ln * s * .3:.1f}" y="{my + dx / ln * s * .3 + 4:.1f}" text-anchor="middle" font-size="11" font-weight="700" fill="var(--mark)">{code[k]}</text>')
    o.append("</svg>")
    return f'<figure class="fig">{"".join(o)}<figcaption>{cap}</figcaption></figure>'


def shifts(seq, cap):
    R = rots(seq)
    b = R.index(min(R))
    M = [[f"from {k + 1}"] + r for k, r in enumerate(R)]
    return mat(M, cap, hi={(b, j) for j in range(1, len(seq) + 1)}, pad={(k, 0) for k in range(len(R))}, small=True), R[b], b


def diff_grid(code, n=8, rule="next"):
    m, d = len(code), cfd(code, n, rule)
    nxt = [code[(i + 1) % m] for i in range(m)]
    raw = [(nxt[i] - code[i]) if rule == "next" else (code[i] - nxt[i]) for i in range(m)]
    M = [["i"] + list(range(1, m + 1)), ["this c<sub>i</sub>"] + code, ["next c<sub>i+1</sub>"] + nxt,
         ["next − this" if rule == "next" else "this − next"] + raw, [f"mod {n} = CFD"] + d]
    return mat(M, f"first difference, last column wraps round (next of the last digit = the first digit)", hi={(4, j) for j in range(1, m + 1)},
               pad={(r, 0) for r in range(5)} | {(0, j) for j in range(1, m + 1)} | {(2, m)}, small=True), d


def lab_rc(off=0):
    return lambda p: f"({p[0] + off},{p[1] + off})"


def lab_xy(H):
    return lambda p: f"({p[1]},{H - 1 - p[0]})"


def moves(U, n, lab):
    code, m = chain(U, n), len(U)
    return tbl(["move", "from → to", "direction", "code"], [[k + 1, f"{lab(U[k])} → {lab(U[(k + 1) % m])}", NAMES[n][c], f"<b>{c}</b>"] for k, c in enumerate(code)], "tight")


def solve(U, n=8, lab=lab_rc(), start="", walk="clockwise", parts=("start", "both"), grid=None, xy=False, off=0, H=None, W=None, show_moves=True):
    code = chain(U, n)
    m = len(code)
    o = [f"<p><b>Step 1 · chain code.</b> Start at {start} and walk {walk} round the boundary. Each move to the next boundary pixel gets the number of its direction ({n}-direction compass: 0 = right, then counterclockwise).</p>",
         figs(bfig(U, n, grid, f"boundary with each move's code · ringed = start{' · axes x →, y ↑' if xy else ''}", xy, off, H, W), compass(n))]
    if show_moves:
        o.append(moves(U, n, lab))
    o.append(formula(f"CC = {S(code)} &nbsp;({m} moves)"))
    sn_html, sn, sk = shifts(code, "all circular shifts of the CC · highlighted = smallest")
    d = cfd(code, n)
    dg, _ = diff_grid(code, n)
    nc_html, nc, nk = shifts(d, "all circular shifts of the CFD · highlighted = smallest")
    if "start" in parts:
        o.append(f"<p><b>Step 2 · start-point invariance (shape number of slide 18).</b> The boundary is a loop, so any digit can be the first. Write the code from every start (circular shifts) and pick the one that reads as the smallest number.</p>")
        o.append(sn_html)
        o.append(ans(f"Start-point invariant chain code = <b>{S(sn)}</b> (smallest shift, starting at digit {sk + 1})."))
    if "both" in parts:
        o.append(f"<p><b>Step {3 if 'start' in parts else 2} · circular first difference (CFD).</b> Slide 22 rule: CFD<sub>i</sub> = (c<sub>i+1</sub> − c<sub>i</sub>) mod {n}; the last digit wraps round to the first. This removes rotation.</p>")
        o.append(dg)
        o.append(formula(f"CFD = {S(d)}"))
        o.append(f"<p><b>Step {4 if 'start' in parts else 3} · normalise (NCFD).</b> Smallest circular shift of the CFD. This removes the start point too.</p>")
        o.append(nc_html)
        o.append(ans(f"Chain code invariant to start point <b>and</b> rotation (NCFD, shape number of slides 21–22) = <b>{S(nc)}</b>."))
    return "".join(o), {"cc": code, "sn": sn, "cfd": d, "ncfd": nc}


def csim(cap, **cfg):
    cfg = {"type": "chain", **cfg}
    if "path" in cfg:
        cfg["path"] = [list(p) for p in cfg["path"]]
    return sim(cfg, cap)


S_ = []

# ================================================================ 1. representation and description
S_.append(sec("start", "Start here: representation and description", "3–9", SHORT, f"""
{idea("After segmentation you have a blob of pixels: \"this is the object\". To compare it with other objects (is it a 0 or a 6? a bone or a crack?) you need a short, fixed way to <b>write the shape down</b> (representation) and a few numbers that <b>describe</b> it (description). A chain code writes the outline as a list of arrow directions.")}
<p><b>Slide 3. Where it fits:</b> segmentation → raw data (pixels) → <b>representation</b> → computation of <b>descriptors</b>. A representation uses either <b>external</b> characteristics (the boundary: shape) or <b>internal</b> characteristics (the pixels inside: regional properties such as colour and texture).</p>
<p><b>Slide 4. Image representation</b> = how an image is stored and modelled for analysis. <b>Image description</b> = how we characterise and communicate its content.</p>
{tbl(["representation (slides 5–7)", "what it is", "example"], [
    ["1. pixel-based", "ordered arrays of pixel values (grayscale or RGB); each pixel = intensity/colour at a spatial location", "convolution, filtering (low-level operations)"],
    ["2. region-based", "after segmentation the image is a set of regions, described by their boundary (external) or the pixels inside (internal)", "a tumour described by its boundary curve or its inside pixels"],
    ["3. feature-based", "extracted features (edges, corners, textures, shapes) instead of raw pixels; compact and robust for recognition", "SIFT, HOG, deep-learning embeddings"]])}
{tbl(["descriptor (slide 8)", "what it holds"], [
    ["<b>boundary descriptors</b>", "<b>chain codes</b>: the boundary as a sequence of line segments with direction and length; useful for shape analysis"],
    ["region descriptors", "statistics: mean intensity, variance, texture; colour histograms of a region"],
    ["structural descriptors", "graph-based models: parts as nodes and their relationships as edges"],
    ["semantic description", "high-level meaning (\"a cat sitting on a chair\"), done by deep-learning models that map features to language"]])}
"""))

# ================================================================ 2. chain code basics
SQ = unit([(2, 0), (2, 2), (0, 2), (0, 0)])
ZERO = ["..###..", "..#..#.", ".#....#", ".#...#.", ".#...#.", ".#..#..", "..##..."]
U12 = [(0, 2), (0, 3), (0, 4), (1, 5), (2, 6), (3, 5), (4, 5), (5, 4), (6, 3), (6, 2), (5, 1), (4, 1), (3, 1), (2, 1), (1, 2)]
HEX = [".###.", ".###.", "#####", "#####", ".###."]
U13 = unit([(4, 1), (4, 3), (3, 4), (2, 4), (1, 3), (0, 3), (0, 1), (1, 1), (2, 0), (3, 0)])
S_.append(sec("cc", "Chain code: what it is and how to write one", "10–13", EXAM, f"""
{idea("Stand on one pixel of the outline. Look at where the next outline pixel is: right, up-right, up… Write that direction as a number. Step there and repeat until you are back where you started. The list of numbers <b>is</b> the chain code. You no longer need the picture: start pixel + numbers redraw the whole outline.")}
<p><b>Slide 10.</b> A <b>chain code</b> is a <b>boundary representation technique</b> used to <b>describe the shape of an object</b>. Instead of storing all pixels of a boundary, it <b>encodes the contour as a sequence of directional steps</b>.</p>
<p><b>Slide 11. How it works:</b> (1) <b>boundary extraction</b>: find the contour of the object; (2) <b>starting point selection</b>: pick one boundary pixel; (3) <b>directional encoding</b>: trace the boundary pixel by pixel and write each step as a direction number.</p>
{figs(compass(8, "8-directional chain code (8-connectivity): 0 right, 1 up-right, 2 up, 3 up-left, 4 left, 5 down-left, 6 down, 7 down-right"), compass(4, "4-directional code (slide 11 calls it crack code): 0 right, 1 up, 2 left, 3 down"))}
{trap("Direction numbers go round <b>counterclockwise</b> starting from 0 = right, like angles in maths: code k means angle k × 45° (8-dir) or k × 90° (4-dir). Up is 2 in 8-dir but 1 in 4-dir. Draw the compass in every answer.")}
<p><b>Slide 10 example.</b> A square boundary traced counterclockwise from the bottom-left pixel: two steps right, two up, two left, two down.</p>
{figs(bfig(SQ, 8, ["###"] * 3, "slide 10 square: CC = 00224466"))}
<p><b>Slide 12. Chain code example</b> (the digit "0"): start at the blue pixel at the top and walk clockwise. Code: <b>0, 0, 7, 7, 5, 6, 5, 5, 4, 3, 2, 2, 2, 1, 2</b>. This is also the SP24 final figure (solved below).</p>
{figs(bfig(U12, 8, ZERO, "slide 12: CC = 007756554322212 (15 moves)"))}
{csim("slide 12, the digit 0. Watch each move get its number, then the first difference and the normalisation.", path=U12, grid=ZERO, dir="clockwise", startLabel="the blue pixel at the top")}
<p><b>Slide 12. Advantages:</b> compact representation of boundaries; easy to store and manipulate; useful for shape analysis and recognition.</p>
<p><b>Slide 13. Simulation</b> on a region of dots: start at the red dot (bottom-left of the bottom row) and walk counterclockwise. Chain code <b>001232446567</b>.</p>
{figs(bfig(U13, 8, HEX, "slide 13: CC = 001232446567"))}
{csim("slide 13 simulation, counterclockwise from the red dot.", path=U13, grid=HEX, dir="counterclockwise", startLabel="the red dot")}
<p><b>Slide 13. Is the chain code translation invariant? YES.</b> Moving the whole shape somewhere else in the image does not change any step, because the code stores only <i>relative</i> moves, never absolute positions.</p>
"""))

# ================================================================ 3. invariance problems
L4 = ["03032211", "03221103", "01033221", "10033212"]
L4name = ["original", "start point changed", "reflected", "rotated"]
SQ18 = D("000666444222")
U18 = code_path(SQ18)
S_.append(sec("inv", "Why the plain chain code is not enough", "14–19", EXAM, f"""
{idea("The same shape can give many different chain codes: start at another pixel and the list is shifted; turn the shape and every digit changes; make it bigger and the list gets longer. For recognition we want <b>one</b> code per shape. That is what the next section fixes.")}
<p><b>Slide 14. Is invariance needed?</b> The letter F appears moved, scaled and rotated: we want <b>translation, scale and rotation invariance</b> so all of them are recognised as F.</p>
<p><b>Slide 15. Is it invariant to rotation, scaling or reflection?</b> An L-shaped boundary with the <b>4-direction code</b>:</p>
{tbl(["case (slide 15)", "chain code"], [[L4name[k], L4[k]] for k in range(4)])}
<p>Every case gives a different code even though it is the same L. <b>Slide 16. Why invariance matters:</b> shape recognition, classification and matching need a representation that stays the same despite rotation, scaling or reflection.</p>
<p><b>Slide 17. Problems in chain code representation</b> (learn this list, it is a 3-mark theory question):</p>
<ul>
<li><b>Starting point sensitivity:</b> different starting points → different codes.</li>
<li><b>Rotation dependence:</b> rotating the shape changes the sequence.</li>
<li><b>Scaling issues:</b> enlarging/reducing alters the code length.</li>
<li><b>Noise sensitivity:</b> small irregularities in the boundary cause large changes.</li>
<li><b>Ambiguity:</b> different traversal paths or connectivity choices (4 vs 8) yield different codes.</li>
</ul>
<p><b>Slide 18. Starting point solution using shape number (same direction).</b> A square traced clockwise from three different corners:</p>
{tbl(["start", "chain code"], [["top-left", "000666444222"], ["top-right", "666444222000"], ["bottom-left", "222000666444"]])}
<p>The <b>shape number</b> is the <b>smallest sequence among all circular shifts</b> of the CC, here <b>000666444222</b>. It is <b>starting-point invariant</b>.</p>
{csim("slide 18 square. Change the start point, then normalise the CC: the smallest shift is the same every time.", path=U18, grid=["####"] * 4, dir="clockwise", starts=[["top-left", [0, 0]], ["top-right", [0, 3]], ["bottom-left", [3, 0]]], target="cc")}
<p><b>Slide 19. Rotation and scaling comparison:</b> rotating the square by 45° turns every 0/2/4/6 into 1/3/5/7 (different code); scaling it up makes the code longer. The shape number alone does not fix either.</p>
{trap("Slides 18, 19, 21 and 24 have AI-made pictures (\"Made with AI\") and a few printed digits are sloppy (e.g. slide 24 shows an 11-digit CFD for a 12-move square). Trust the method, not those digits. For the 12-move square 000222444666 the CFD is 002002002002.")}
"""))

# ================================================================ 4. normalisation
L4r = {c: (cfd(D(c), 4), minrot(cfd(D(c), 4))[0]) for c in L4}
G23 = ["444201066", "066444201", "067644222"]
g23 = {c: (cfd(D(c), 8, "prev"), minrot(cfd(D(c), 8, "prev"))[0], cfd(D(c), 8), minrot(cfd(D(c), 8))[0]) for c in G23}
raw23 = [(D(c)[i] - D(c)[(i + 1) % 9]) for c in G23 for i in range(9)]
S_.append(sec("norm", "The fix: CC → CFD → NCFD (shape number)", "20–24", EXAM, f"""
{idea("Rotation changes every direction by the same amount. So instead of storing the directions, store the <b>turns</b>: how much you turn at each corner. A turn does not care which way the shape faces. That is the first difference. Then, to forget the start point, read the ring of turns from the place that gives the smallest number.")}
<p><b>Slide 20. Chain code changes with:</b> (1) changing the start point, (2) reflection, (3) rotation. <b>Solution is normalisation, in 3 steps:</b></p>
{formula("1. Chain code (CC) &nbsp;→&nbsp; 2. Circular First Difference (CFD) &nbsp;→&nbsp; 3. Normalised CFD (NCFD, aka <b>shape number</b>)")}
<h3>Step 2: circular first difference</h3>
{formula("CFD<sub>i</sub> = (c<sub>i+1</sub> − c<sub>i</sub>) mod n &nbsp; for i = 1 … N, &nbsp; with c<sub>N+1</sub> = c<sub>1</sub> (wrap round)")}
<p>n = 8 for an 8-direction code, 4 for a 4-direction code. "Circular" means the last digit compares the last code with the <b>first</b> one, because the boundary is a closed loop. So the CFD has exactly as many digits as the CC.</p>
<p>Why it works: rotating the shape by 90° adds 2 (8-dir) to every code digit. In (c<sub>i+1</sub> + 2) − (c<sub>i</sub> + 2) the 2 cancels. So the CFD is <b>rotation invariant</b> (for multiples of 45° in 8-dir, 90° in 4-dir).</p>
<p>Meaning of a CFD digit (8-dir): 0 = straight on, 1 = 45° left turn, 2 = 90° left, 4 = U-turn, 6 = 90° right, 7 = 45° right.</p>
<h3>Step 3: normalise (minimum magnitude)</h3>
<p>Write the CFD from every start (all circular shifts) and pick the smallest number. This is the <b>NCFD</b>, also called the <b>shape number</b>: invariant to start point <b>and</b> rotation.</p>
<p><b>Slide 21 example (4-direction, slide 15 L shapes):</b> all four codes end at the same NCFD:</p>
{tbl(["case", "CC", "CFD (next − this) mod 4", "NCFD"], [[L4name[k], c, S(L4r[c][0]), f"<b>{S(L4r[c][1])}</b>"] for k, c in enumerate(L4)])}
<p><b>NCFD known as SHAPE NUMBER, an invariant code: 03033133</b> (slide 22).</p>
{csim("slide 21–22 L shape, 4-direction code 03032211. Use the compass with 4 arrows.", code=D("03032211"), n=4, dir="clockwise", startLabel="the circled corner")}
{paper("Slide 22 · worked in full (4-direction)", "worked", f'''
<p>CC = 0 3 0 3 2 2 1 1 (start at the circled corner).</p>
{diff_grid(D("03032211"), 4)[0]}
<p>CFD = 31330303. Circular shifts: 31330303, 13303033, 33030331, 30303313, 03033133, 30331330, 03313303, 33133030. Smallest = <b>03033133</b>.</p>''')}
<h3>Slide 23: Gonzalez's version (different subtraction!)</h3>
<p>Three shapes (the third is rotated 90°) with chain codes 444201066, 066444201, 067644222. "Curvature = differences in chain code values", then "normalise curvature = mod 8", then "code is the cyclic permutation which produces the smallest number": <b>002271202</b> for all three.</p>
{tbl(["chain code", "this − next (slide 23)", "mod 8", "smallest shift"], [[c, " ".join(str(c_ - n_) for c_, n_ in zip(D(c), D(c)[1:] + D(c)[:1])), S(g23[c][0]), f"<b>{S(g23[c][1])}</b>"] for c in G23])}
{trap("Slide 23 subtracts <b>this − next</b>; slide 22 subtracts <b>next − this</b>. Each digit of one is 8 minus the other (mod 8), so the final numbers differ (slide-22 rule on these shapes gives " + S(g23[G23[0]][3]) + "). Both are invariant. In the exam use slide 22's rule (next − this, the textbook rule), write the formula, and the marker can follow you.")}
{csim("slide 23 shape 1 (444201066). The difference rule is set to slide 23's this − next; switch it to see the slide-22 answer.", code=D("444201066"), dir="along the boundary", rule="prev", startLabel="the arrowed corner")}
<p><b>Slide 24. Comparison table:</b></p>
{tbl(["representation", "start-point invariant", "rotation invariant", "notes"], [
    ["chain code (CC)", "✗", "✗", "basic, sensitive to start and rotation"],
    ["shape number (smallest circular shift of CC)", "✓", "✗", "fixes start-point ambiguity only"],
    ["CFD (differential chain code)", "✗", "✓", "encodes direction changes"],
    ["NCFD (normalised CFD)", "✓", "✓", "fixes both start point and rotation"]])}
{trap("\"Shape number\" means two things in this deck: slide 18/24 use it for the smallest shift of the <b>CC</b>; slides 21–22 use it for the <b>NCFD</b>. In an answer, write both lines with their names (\"start-point invariant CC = …\", \"NCFD = …\") and you cannot lose the mark.")}
"""))

# ================================================================ 5. resampling, applications, class work
CW = unit([(0, 3), (0, 4), (1, 5), (5, 5), (7, 3), (5, 1), (4, 1), (3, 2), (2, 2), (1, 3)])
cwA, cwR = solve(CW, start="the top dot (0,3), the arrow", walk="clockwise", H=8, W=7)
S_.append(sec("resample", "Long codes, noise and resampling; applications; class work", "25–29", LIKELY, f"""
<p><b>Slides 25–26. Problems</b> with a raw pixel boundary: (1) <b>long chains of codes</b>; (2) <b>no invariance</b> to rotation and scale; (3) <b>sensitive to noise</b>: easily disturbed by small bumps; plus the <b>start point</b> problem.</p>
<p><b>Solution: re-sample</b> the boundary to a <b>lower resolution</b> (a coarser grid) before calculating the code. Each boundary point is moved to the nearest node of the coarse grid; the code is then written between those nodes.</p>
<p><b>Slide 27. Examples:</b> object boundary → resampled boundary vertices → 4-directional or 8-directional chain code. Before resampling the code is long (000000766…1111); after resampling it is short (076666…12). Fewer digits, and tiny bumps disappear.</p>
{idea("Resampling is like tracing the outline with a thick marker on graph paper: you only keep the big turns, not every wiggle of the pen.")}
<p><b>Slide 28. Applications:</b></p>
{tbl(["field", "use case", "how chain codes help"], [
    ["object detection", "find shapes (circles, squares, L-shapes) in documents or industrial parts", "trace the boundary; shape numbers match templates regardless of orientation"],
    ["character recognition (OCR)", "handwritten or printed characters", "each character's contour is a chain code; shape numbers recognise it even if rotated or slightly distorted"],
    ["medical imaging", "tumours, organs, bones in scans", "the code describes the boundary; shape numbers compare across patients or time"],
    ["remote sensing", "lakes, buildings in satellite images", "contours as codes; shape numbers classify despite rotation or scale"]])}
{paper("Slide 29 · Class work", "worked", f'''
<p class="q">An image is given (dots on a grid). Write down the 8-chain code and find the shape number of it. Starting point: the top dot marked by the arrow.</p>
{cwA}''')}
{csim("slide 29 class work, from the arrowed top dot.", path=CW, dir="clockwise", startLabel="the arrow", rule="next")}
"""))

# ================================================================ 6. past papers
F25p = [(1, 2), (2, 1), (3, 0), (4, 1), (5, 1), (6, 2), (5, 3), (4, 4), (3, 4), (2, 3)]
F25g = [".....", "..#..", ".#.#.", "#...#", ".#..#", ".#.#.", "..#.."]
f25A, f25R = solve(F25p, start="the top pixel (1,2)", walk="anticlockwise", grid=F25g)

sp24A, sp24R = solve(U12, start="the arrowed pixel (0,2)", walk="clockwise", grid=ZERO, parts=("both",))
alt = 5
c2 = sp24R["cc"][alt:] + sp24R["cc"][:alt]
rot = [(c + 2) % 8 for c in sp24R["cc"]]
proof = f"""
<p><b>Proof (illustration).</b> <i>(a) Start point.</i> Start instead at pixel {lab_rc()(U12[alt])} (move {alt + 1}): CC′ = {S(c2)}. Its CFD is {S(cfd(c2))}, a circular shift of the CFD above, and its smallest shift is again <b>{S(minrot(cfd(c2))[0])}</b>.</p>
<p><i>(b) Rotation.</i> Rotate the object 90° counterclockwise: every move turns by 90°, so every code digit increases by 2 (mod 8): CC″ = {S(rot)}. CFD″ = {S(cfd(rot))}, <b>identical</b> to the CFD above, because (c<sub>i+1</sub> + 2) − (c<sub>i</sub> + 2) = c<sub>i+1</sub> − c<sub>i</sub>. So NCFD″ = <b>{S(minrot(cfd(rot))[0])}</b>.</p>
<p>Same final code in both cases, so the NCFD is invariant to the start point and to rotation.</p>"""

SP22xy = [(3, 5), (4, 6), (5, 5), (6, 4), (5, 3), (4, 2), (3, 1), (2, 2), (1, 3), (0, 4), (1, 5), (2, 6)]
SP22rc = [(6 - y, x) for x, y in SP22xy]
SP22g = ["......."] * 7
SP22g = [row if r != 6 - 4 else row[:1] + "#" + row[2:] for r, row in enumerate(SP22g)]
sp22A, sp22R = solve(SP22rc, lab=lab_xy(7), start="the arrow pixel (3,5)", walk="clockwise (the arrow enters (3,5) from (2,6))", grid=SP22g, xy=True)

c23 = D("1100223344557766")
U23 = code_path(c23)
sp23A, sp23R = solve(U23, start="the bottom vertex", walk="counterclockwise", parts=("start",), show_moves=False)

F21g = ["....####...", "...#....#..", "...#.....#.", "..#.......#", ".#......###", ".#.....#...", ".#...###...", "..#.#......", "...#......."]
F21p = [(8, 3), (7, 4), (6, 5), (6, 6), (6, 7), (5, 7), (4, 8), (4, 9), (4, 10), (3, 10), (2, 9), (1, 8), (0, 7), (0, 6), (0, 5), (0, 4), (1, 3), (2, 3), (3, 2), (4, 1), (5, 1), (6, 1), (7, 2)]
f21A, f21R = solve(F21p, start="the arrowed bottom pixel (8,3)", walk="anticlockwise", grid=F21g, parts=("both",))

S_.append(sec("papers", "Past questions solved like the answer script", "all", EXAM, f"""
<p>Every chain-code question so far is the same recipe: <b>(1)</b> write the CC with a labelled figure and compass, <b>(2)</b> smallest shift of the CC if they ask \"invariant to starting point\", <b>(3)</b> CFD, <b>(4)</b> smallest shift of the CFD if they ask \"starting point and rotation\". The figures below are redrawn from the question papers (row, column counted from 0 at the top-left unless the paper prints x–y axes).</p>

{paper("F25 Quiz (Q3D) Q2", "7 + 7 marks", f'''
<p class="q">For the boundary in the grid figure (anticlockwise), compute the 8-directional chain code that is (i) invariant to the starting point; (ii) invariant to both the starting point and rotation.</p>
{f25A}''')}
{csim("F25 quiz boundary. Set “Normalise” to CC for part (i), CFD for part (ii).", path=F25p, grid=F25g, dir="anticlockwise", startLabel="the top pixel")}

{paper("SP24 Final Q3(d)", "4 + 4 marks", f'''
<p class="q">Write the chain code for the boundary of the object (grid figure, clockwise, start at the arrow). Compute the chain code which is invariant to both the starting point and rotation. Show the final chain code and illustrate the proof.</p>
<p>This is the slide 12 digit-0 boundary.</p>
{sp24A}{proof}''')}
{csim("SP24 boundary (same as slide 12). After the run, change the difference rule to see why you must name it.", path=U12, grid=ZERO, dir="clockwise", startLabel="the arrow")}

{paper("SP22 Final Q6(b)(ii)", "4 marks", f'''
<p class="q">Grid image of black points (axes x to the right, y upward) with an arrow at the reference pixel. Find the chain code that is invariant to the starting point and rotation, 8-neighbour.</p>
<p><b>Reading the figure.</b> Points are written (x, y). (1,4) is filled but lies inside the outer boundary, so the outer chain passes through (0,4). In (x, y) form \"up\" means y + 1.</p>
{sp22A}''')}
{csim("SP22 points, labelled in (x, y) like the paper.", path=SP22rc, grid=SP22g, xy=True, dir="clockwise", startLabel="the arrow")}

{paper("SP23 Final Q2(c)", "1 + 4 marks", f'''
<p class="q">What is chain code? For the boundary figure (counterclockwise), compute the chain code that is invariant to the starting point (8-direction).</p>
<p><b>Chain code</b> is a boundary representation: starting from a boundary pixel, the contour is written as a sequence of direction numbers (0–7 for 8-connectivity, 0 = right, counterclockwise), one per step to the next boundary pixel. It is compact and translation invariant.</p>
<p><b>Reading the figure.</b> Polygon edges counterclockwise from the bottom vertex: up-right ×2, right ×2, up ×2, up-left ×2, left ×2, down-left ×2, down-right ×2, down ×2.</p>
{sp23A}
<p>(Not asked, but if they add rotation: CFD = {S(sp23R["cfd"])}, NCFD = {S(sp23R["ncfd"])}.)</p>''')}
{csim("SP23 polygon (code 1100223344557766). Normalise is set to CC because the question asks only for start-point invariance.", code=c23, dir="counterclockwise", target="cc", startLabel="the bottom vertex")}

{paper("F21 Final B1(b)", "3 + 3 marks", f'''
<p class="q">(i) What is chain code? Problems in chain code representation. (ii) For the boundary (grid figure, anticlockwise), find the chain code invariant to both starting point and rotation, 8-neighbour.</p>
<p><b>(i)</b> A chain code represents a boundary by a start pixel and a sequence of direction numbers (8-dir: 0 = right, 1 = up-right, … 7 = down-right), one per step along the contour. <b>Problems:</b> it depends on the <b>starting point</b>; it changes with <b>rotation</b>; its length changes with <b>scale</b>; it is <b>sensitive to noise</b> (small bumps change many digits); codes get <b>long</b> for big boundaries; different traversal/connectivity choices give different codes (<b>ambiguity</b>). Fixes: shape number / NCFD and resampling.</p>
<p><b>(ii)</b></p>
{f21A}''')}
{csim("F21 boundary, anticlockwise from the arrow at the bottom (23 moves).", path=F21p, grid=F21g, dir="anticlockwise", startLabel="the arrow")}

{paper("SP25 Final (CLO3 case study)", "case study", '''
<p class="q">A medical imaging team analyses X-ray images of bones to detect fractures. They apply chain code representation, histogram analysis, the Hough transform and power-law transformation. Discuss how each technique contributes to detecting fractures and enhancing the image, with applications, advantages or limitations.</p>
<p><b>Power-law (gamma) transformation</b> s = c·r<sup>γ</sup> first adjusts contrast: γ &lt; 1 brightens dark regions so thin, faint fracture lines in dense bone become visible; γ &gt; 1 darkens washed-out regions. Cheap, pointwise; limitation: one γ for the whole image, needs tuning.</p>
<p><b>Histogram analysis</b> (and equalisation) shows how gray levels are spread; it helps choose a threshold to separate bone from soft tissue and spreads crowded levels to raise contrast. Limitation: global, can amplify noise.</p>
<p><b>Chain code representation:</b> after segmenting the bone, its outer boundary is written as a chain code. A healthy bone outline is smooth (CFD mostly 0, small turns); a fracture shows as a sudden break or sharp turns (large CFD digits such as 2–6) or a gap in the boundary. The normalised CFD (shape number) lets the team compare the bone's shape with a template or an earlier scan regardless of start point or rotation (patient position). Advantages: compact, translation and (after normalisation) rotation invariant. Limitations: sensitive to noise and scale; resample the boundary first.</p>
<p><b>Hough transform</b> finds straight lines (and other parametric shapes) even when broken: fracture lines are often line-like, so peaks in the (ρ, θ) accumulator locate them and their angle, and bone shafts can be fitted as lines to spot misalignment. Robust to gaps and noise; limitation: heavier computation, needs good edge maps.</p>
<p><b>Together:</b> power-law + histogram → clearer image; segmentation and chain code → bone outline and shape change; Hough → fracture line position and orientation.</p>''')}
"""))

# ================================================================ 7. traps
S_.append(sec("traps", "Traps and one-minute sheet", "all", None, f"""
<ul class="traps">
<li>Draw the compass in every answer: 0 = right, counting <b>counterclockwise</b>. 8-dir: 2 = up, 6 = down. 4-dir: 1 = up, 3 = down.</li>
<li>Grid rows count downward: going to a smaller row number is \"up\". If the paper prints x–y axes (SP22), up is y + 1.</li>
<li>Walk in the direction the question says (clockwise / anticlockwise). Wrong direction = wrong code.</li>
<li>The chain is closed: the last move returns to the start pixel, and the CFD's last digit wraps to the first code. CC and CFD have the same number of digits.</li>
<li>Negative difference: add n (8 or 4). (2 − 7) mod 8 = 3.</li>
<li>\"Invariant to start point\" = smallest shift of the <b>CC</b>. \"Invariant to start point and rotation\" = smallest shift of the <b>CFD</b> (NCFD).</li>
<li>Slide 22 uses next − this, slide 23 uses this − next. Name your rule.</li>
<li>Smallest shift: compare digit by digit from the left; the first digit that differs decides. Show the list of shifts, it is where the marks are.</li>
</ul>
{tbl(["what", "how", "invariant to"], [["chain code CC", "one direction number per boundary step", "translation"], ["smallest shift of CC", "min over circular shifts", "+ start point"], ["CFD", "(c<sub>i+1</sub> − c<sub>i</sub>) mod n, wrap round", "+ rotation (multiples of 45°/90°)"], ["NCFD (shape number)", "min over circular shifts of CFD", "start point + rotation"], ["resampling", "coarser grid before coding", "less noise, shorter code (helps scale)"]])}
"""))

toc = [("start", "Start"), ("cc", "Chain code"), ("inv", "Problems"), ("norm", "CFD & NCFD"), ("resample", "Resampling & class work"), ("papers", "Past papers"), ("traps", "Traps")]
OUT.write_text(page("DIP Deck 10 Lesson", "CSE 4227 · Chapter 11 · Deck 10", "Chain code, first difference and shape number",
                    "How to write a chain code, why it changes with start point and rotation, and the CC → CFD → NCFD fix. Every past question is solved in answer-script form, with a step-by-step simulator next to each one.",
                    toc, S_, extra=sim_assets()), encoding="utf-8")

# ---------------------------------------------------------------- self-check against data/answers.json and the slides
assert S(chain(SQ)) == "00224466" and S(chain(U12)) == "007756554322212" and S(chain(U13)) == "001232446567"
assert all(S(L4r[c][1]) == "03033133" for c in L4) and S(L4r["03032211"][0]) == "31330303"
assert all(S(g23[c][1]) == "002271202" for c in G23) and S(g23["444201066"][0]) == "002271202"
assert [S(f25R[k]) for k in ("cc", "sn", "cfd", "ncfd")] == ["5576711233", "1123355767", "0271201102", "0110202712"]
assert [S(sp24R[k]) for k in ("cc", "cfd", "ncfd")] == ["007756554322212", "070617077700716", "007160706170777"]
assert minrot(cfd(c2))[0] == sp24R["ncfd"] and cfd(rot) == sp24R["cfd"]
assert [S(sp22R[k]) for k in ("cc", "sn", "cfd", "ncfd")] == ["177555333117", "117177555333", "606006006062", "006006062606"]
assert chain(U23) == c23 and S(sp23R["sn"]) == "0022334455776611" and S(sp23R["ncfd"]) == "0101010207030702"
assert [S(f21R[k]) for k in ("cc", "cfd", "ncfd")] == ["11002100233344456556677", "07027702100100117010102", "00100117010102070277021"]
assert S(cwR["cc"]) == "076666553321212"
print(OUT, OUT.stat().st_size, "class work", S(cwR["sn"]), S(cwR["cfd"]), S(cwR["ncfd"]))
