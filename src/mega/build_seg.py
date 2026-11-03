# Decks 08–09 fast track: only what she asks, in answer-script form. Numbers checked below.
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from kit import page, formula, idea, trap, tbl, mat, mats, paper, cases, bars

OUT = HERE / "seg_fast_track.html"


def ask(items):
    li = "".join(f"<li>{q} <span class=\"src\">{src}</span></li>" for q, src in items)
    return f'<div class="asks"><span class="k">If the exam asks this, use this section</span><ul>{li}</ul></div>'


def S2(id_, title, meta, body):
    return f'<section class="sec" id="{id_}"><div class="sechead"><h2>{title}</h2><div class="meta"><span class="slides">{meta}</span></div></div>{body}</section>'


# 1st / 2nd derivative of the slide 15 ramp
f = [5, 5, 4, 3, 2, 1, 0, 0]
d1 = [f[i + 1] - f[i] for i in range(len(f) - 1)]
d2 = [f[i + 1] + f[i - 1] - 2 * f[i] for i in range(1, len(f) - 1)]
assert d1 == [0, -1, -1, -1, -1, -1, 0] and d2 == [-1, 0, 0, 0, 0, 1]
J = lambda s: " ".join(map(str, s))
dtab = tbl(["x", *range(8)], [["f(x)", *f], ["1st = f(x+1) − f(x)", *d1, ""], ["2nd = f(x+1) + f(x−1) − 2f(x)", "", *d2, ""]], "narrow")

# Canny slide 59
gN = [[200, 0, 57], [0, 45, 101], [50, 0, 0]]
TH, TL = 100, 45
strong = {(r, c) for r in range(3) for c in range(3) if gN[r][c] >= TH}
weak = {(r, c) for r in range(3) for c in range(3) if TL <= gN[r][c] < TH}
keep = {p for p in weak if any((p[0] + dr, p[1] + dc) in strong for dr in (-1, 0, 1) for dc in (-1, 0, 1))}
final = [[gN[r][c] if (r, c) in strong | keep else 0 for c in range(3)] for r in range(3)]
assert keep == {(0, 2), (1, 1)} and final == [[200, 0, 57], [0, 45, 101], [0, 0, 0]]

# iterative threshold
vals = [10, 20, 30, 200, 210, 220]
T0 = sum(vals) / 6
m1 = sum(v for v in vals if v > T0) / 3; m2 = sum(v for v in vals if v <= T0) / 3
assert T0 == 115 and (m1 + m2) / 2 == 115

# region growing, slide 14, |diff| <= 5 against the pixel it grows from
G = [[10] * 7, [10, 10, 10, 69, 70, 10, 10], [59, 10, 60, 64, 59, 56, 60], [10, 59, 10, 60, 70, 10, 62],
     [10, 60, 59, 65, 67, 10, 65], [10] * 7, [10] * 7]


def grow(conn, img=None, seed=(3, 3), T=5):
    img = img or G
    nb = [(-1, 0), (1, 0), (0, -1), (0, 1)] + ([(-1, -1), (-1, 1), (1, -1), (1, 1)] if conn == 8 else [])
    reg, todo, log = {seed}, [seed], []
    while todo:
        r, c = todo.pop(0)
        for dr, dc in nb:
            q = (r + dr, c + dc)
            if 0 <= q[0] < len(img) and 0 <= q[1] < len(img[0]) and q not in reg and abs(img[q[0]][q[1]] - img[r][c]) <= T:
                reg.add(q); todo.append(q); log.append(((r, c), q))
    return reg, log


(R4, L4), (R8, L8) = grow(4), grow(8)
assert len(R4) == 13 and len(R8) == 17
logrows = lambda img, log, T: [[f"({a[0]},{a[1]}) = {img[a[0]][a[1]]}", f"({b[0]},{b[1]}) = {img[b[0]][b[1]]}",
                                f"|{img[b[0]][b[1]]} − {img[a[0]][a[1]]}| = {abs(img[b[0]][b[1]] - img[a[0]][a[1]])} ≤ {T} ✓"] for a, b in log]
extra8 = [row for row in logrows(G, L8, 5) if row[1] not in {r[1] for r in logrows(G, L4, 5)}]

# F22 B5(a): seed at the centre, 8-direction growth, |diff| <= 4
G22 = [[15] * 7, [15, 15, 15, 68, 69, 15, 15], [64, 64, 63, 67, 70, 68, 15], [15, 15, 70, 65, 61, 71, 66],
       [15, 15, 69, 73, 58, 15, 15], [15] * 7, [15] * 7]
R22, L22 = grow(8, G22, (3, 3), 4)
assert len(R22) == 16

# Canny with numbers, F23 Q3(a): magnitude + gradient arrow
ARW = {"↓": (1, 0), "↑": (-1, 0), "→": (0, 1), "←": (0, -1), "↙": (1, -1), "↘": (1, 1), "↖": (-1, -1), "↗": (-1, 1)}
CM = [[200, 40, 57], [10, 20, 101], [50, 41, 74]]
CA = [["↓", "↓", "↙"], ["→", "↑", "←"], ["↑", "↑", "←"]]
nms_rows, CN = [], [[0] * 3 for _ in range(3)]
for r in range(3):
    for c in range(3):
        dr, dc = ARW[CA[r][c]]
        nbs = [(r + dr, c + dc), (r - dr, c - dc)]
        inside = [(a, b) for a, b in nbs if 0 <= a < 3 and 0 <= b < 3]
        ok = all(CM[r][c] >= CM[a][b] for a, b in inside)
        CN[r][c] = CM[r][c] if ok else 0
        desc = ", ".join(f"({a},{b}) = {CM[a][b]}" for a, b in inside) + ("" if len(inside) == 2 else " (other side is outside)")
        nms_rows.append([f"({r},{c})", CM[r][c], CA[r][c], desc, "kept" if ok else "<b>smaller → 0</b>"])
CH = [[v if v >= 100 else 0 for v in row] for row in CN]
CW = [[v if 45 <= v < 100 else 0 for v in row] for row in CN]
hy_rows, CF = [], [row[:] for row in CH]
for r in range(3):
    for c in range(3):
        if CW[r][c]:
            st = [(a, b) for a in range(r - 1, r + 2) for b in range(c - 1, c + 2) if (a, b) != (r, c) and 0 <= a < 3 and 0 <= b < 3 and CH[a][b]]
            if st:
                CF[r][c] = CW[r][c]
            hy_rows.append([f"({r},{c})", CW[r][c], ", ".join(f"{CH[a][b]} at ({a},{b})" for a, b in st) or "none", "<b>kept</b>" if st else "<b>dropped</b>"])
assert CN == [[200, 40, 57], [0, 0, 101], [50, 41, 74]] and CF == [[200, 0, 57], [0, 0, 101], [0, 0, 74]]

# Sobel with numbers, SP22 Q6(b)(i), zero padding
SI = [[3, 7, 6], [2, 5, 8], [3, 4, 7]]
z = lambda r, c: SI[r][c] if 0 <= r < 3 and 0 <= c < 3 else 0
sgx = lambda r, c: (z(r - 1, c + 1) + 2 * z(r, c + 1) + z(r + 1, c + 1)) - (z(r - 1, c - 1) + 2 * z(r, c - 1) + z(r + 1, c - 1))
sgy = lambda r, c: (z(r + 1, c - 1) + 2 * z(r + 1, c) + z(r + 1, c + 1)) - (z(r - 1, c - 1) + 2 * z(r - 1, c) + z(r - 1, c + 1))
SGX = [[sgx(r, c) for c in range(3)] for r in range(3)]
SGY = [[sgy(r, c) for c in range(3)] for r in range(3)]
SM = [[abs(SGX[r][c]) + abs(SGY[r][c]) for c in range(3)] for r in range(3)]
assert SGX[1][1] == 19 and SGY[1][1] == -5 and SM == [[28, 32, 40], [24, 24, 22], [22, 34, 34]]
import math
alpha = math.degrees(math.atan2(-5, 19))

S = []
S.append(S2("why", "What to learn from these two decks", "decks 08–09", """
<p>Everything she has asked from decks 08 and 09 is on this page. Skip the rest of the decks (point detection, split &amp; merge, Hough).</p>
<ol><li>Two approaches of segmentation (7 finals, Fall 25 quiz).</li><li>1st vs 2nd derivative on a ramp (SP24) and why Gaussian + Laplacian / LoG (Fall 25 quiz).</li>
<li>Canny: criteria and steps, Canny with numbers, false positives / negatives, Sobel with numbers, line masks, the Canny schematic (SP22–SP25, F23).</li>
<li>Thresholding (SP23, SP25 cases).</li><li>Region growing, with two full numeric examples (SP23 case, F22).</li></ol>
<p><b>How each section works:</b> the orange box lists the exam questions it answers. Then: the idea in one line, the lines to write (with a grey "means" line under each), and every numeric worked in full.</p>
<p><b>Your own words are fine.</b> She marks the idea, not the exact sentence. Make sure the <b>bold keywords</b> appear in your answer.</p>
"""))

def wm(tag, marks, rows):
    body = "".join(f'<p class="w">{w}</p><p class="m">{m}</p>' for w, m in rows)
    return paper(tag, marks, '<p class="wmhead">Normal line = write it on the paper. Grey "means" line under it = what it means (do not write that).</p>' + body)


S.append(S2("two", "1 · Two approaches of segmentation", "★ 7 finals · F23 Q1(e), F25 quiz", f"""
{ask([("\"What are the two principal approaches to image segmentation?\"", "F25 quiz"),
      ("\"Write down the types of image segmentation based on two basic properties of intensity values.\"", "F23, F22"),
      ("\"What do you understand by image segmentation?\" Answer: dividing an image into meaningful regions (objects vs background), the first step of image analysis.", "F21")])}
{idea("To cut an image into objects you either look for where brightness <b>suddenly jumps</b> (borders) or for pixels that are <b>alike</b> (groups).")}
{wm("Write this", "2–5 marks", [
    ("Segmentation algorithms use one of two basic properties of intensity values:", "There are only two ways to split a picture into objects. Say that first."),
    ("<b>1. Discontinuity:</b> partition the image where intensity changes sharply, i.e. at edges.", "Look for places where brightness suddenly jumps (dark to bright). Those jumps are the borders of objects."),
    ("Methods: point, line and edge detection (gradient, LoG, Canny), watershed.", "The tools that find those jumps: Sobel gradient, Canny and so on."),
    ("<b>2. Similarity:</b> partition the image into regions that are similar according to a predefined criterion.", "Instead of borders, put pixels that look alike into the same group (e.g. all bright pixels = object)."),
    ("Methods: thresholding, region growing, region splitting and merging.", "The tools that make groups: one cut-off value (threshold), or spreading from a seed (region growing).")])}
<p><b>Memory hook:</b> discontinuity finds <b>borders</b>, similarity finds <b>groups</b>.</p>
"""))

S.append(S2("deriv", "2 · 1st vs 2nd derivative on a ramp", "★ SP24 Q1(b)", f"""
{ask([("\"Define the first-order and second-order derivatives of a 1-D function f(x).\"", "SP24"),
      ("\"What relation is there between 1st and 2nd derivatives for an edge that is a ramp?\"", "SP24"),
      ("\"Why is the 2nd derivative bad with noise?\" / \"What is a zero crossing?\"", "slides 16–19")])}
{idea("An edge is where brightness changes. The 1st derivative is the change between neighbours, so on a ramp it is non-zero all the way along: a <b>thick</b> edge. The 2nd derivative is the change of the change, so it fires only where the ramp starts and stops, with opposite signs: a <b>thin double</b> edge. Halfway between those two it crosses zero: that is the edge centre.")}
{dtab}
{wm("Write this", "3 + 2 marks", [
    ("∂f/∂x = f(x+1) − f(x)", "1st derivative = next pixel minus this pixel: how much the brightness changes in one step."),
    ("∂²f/∂x² = f(x+1) + f(x−1) − 2f(x)", "2nd derivative = how much that change itself changes: right + left − 2 × middle."),
    (f"Example ramp {J(f)}: 1st = {J(d1)}; 2nd = {J(d2)}.", "Brightness slides down 5 to 0 one step at a time (a ramp). Work out both rows with the formulas above; this example earns marks."),
    ("(1) The 1st derivative is non-zero along the entire ramp, giving a <b>thick</b> edge.", "It is −1 at every step of the slope, so the whole slope lights up: the edge looks wide."),
    ("(2) The 2nd derivative is non-zero only at the start and end of the ramp, with <b>opposite signs</b> (a <b>double</b> edge), and zero along the ramp.", "It only reacts where the slope begins (−1) and ends (+1): two thin lines, one negative and one positive."),
    ("(3) It crosses zero at the <b>edge centre</b>, where the 1st derivative is maximum. Its sign tells dark→light or light→dark.", "Between the −1 and the +1 it passes through 0: that crossing point is the middle of the edge. Which sign comes first tells which way the brightness goes."),
    ("The 2nd derivative responds strongly to isolated points and is very <b>sensitive to noise</b>, so the image is smoothed first.", "A single noisy dot gives a huge 2nd-derivative value, so we blur the image a bit before using it.")])}
"""))

LOGM = [[0, 0, -1, 0, 0], [0, -1, -2, -1, 0], [-1, -2, 16, -2, -1], [0, -1, -2, -1, 0], [0, 0, -1, 0, 0]]
assert sum(map(sum, LOGM)) == 0
S.append(S2("logq", "2b · Why Gaussian + Laplacian (LoG): the quiz question", "★ F25 quiz (set D) Q1 · 4 + 2 marks", f"""
{ask([("\"Why is a Laplacian combined with Gaussian smoothing (LoG) before edge detection in noisy images?\"", "F25 quiz"),
      ("\"What is LoG / Marr–Hildreth?\" Answer: Gaussian smoothing + Laplacian, edges at zero crossings, g = ∇²[G ★ f].", "slides 33–37")])}
<p class="q">What are the two principal approaches to image segmentation? Why is a Laplacian filter typically combined with a Gaussian smoothing filter (LoG operator) before performing edge detection in noisy environments? [4 + 2 = 6]</p>
{idea("The Laplacian is a 2nd derivative, and 2nd derivatives go wild on noise: one bad pixel looks like an edge. So blur first with a Gaussian to wipe the noise away, then apply the Laplacian, and mark where the result crosses zero. Blur + Laplacian can be merged into one mask: the LoG (the \"Mexican hat\").")}
{wm("Write this", "4 + 2 marks", [
    ("<b>(a) Two principal approaches</b>, based on two basic properties of intensity values:", "Same answer as section 1. Write both approaches with their methods; that's the 4 marks."),
    ("<b>1. Discontinuity:</b> partition the image where intensity changes abruptly, e.g. at edges. Methods: point, line and edge detection (gradient, Laplacian / LoG, Canny).", "Find where brightness suddenly jumps; those jumps are the borders."),
    ("<b>2. Similarity:</b> partition the image into regions that are similar according to a predefined criterion. Methods: thresholding, region growing, region splitting and merging.", "Group pixels that look alike."),
    ("<b>(b) Why Gaussian before Laplacian:</b> the Laplacian ∇²f is a <b>second derivative</b>, which is extremely <b>sensitive to noise</b>: every noisy pixel gives a strong response and <b>false zero crossings</b> (false edges).", "The Laplacian reacts hugely to any single odd pixel, so noise shows up as fake edges."),
    ("Smoothing with a Gaussian G(x,y) = e<sup>−(x²+y²)/2σ²</sup> first <b>suppresses the noise</b>, so the zero crossings of the Laplacian mark only <b>real edges</b>: g(x,y) = ∇²[G(x,y) ★ f(x,y)].", "Blur first to kill the noise, then take the Laplacian. Now the zero crossings are real edges."),
    ("Both are linear, so they combine into <b>one mask</b>, the LoG (\"Mexican hat\"): ∇²[G ★ f] = [∇²G] ★ f. This is <b>cheaper</b>, and the zero crossings give <b>well-localised</b> edges. σ controls the scale: larger σ = more smoothing, only coarse edges.", "You can pre-combine blur + Laplacian into a single mask and slide it once. Bigger σ = more blur = only the big edges remain.")])}
{mat(LOGM, "5×5 LoG mask (slide 34): positive centre, negative ring, sums to 0", small=True)}
"""))

S.append(S2("canny", "3 · Canny edge detector", "★ SP25, F23", f"""
{ask([("\"How many steps are in Canny edge detection and what are they?\"", "F23, SP22, F21"),
      ("\"Explain the three main criteria of the Canny algorithm.\"", "F22"),
      ("\"Explain non-maximum suppression\" / \"What is the role of NMS in Canny?\"", "F21, SP23, SP25"),
      ("\"What is hysteresis thresholding?\"", "SP24")])}
{idea("Canny is the careful edge detector: blur away noise, find how strong and which way each edge is, thin every edge to one pixel, then keep the sure edges plus the weak pixels that touch a sure edge.")}
<div class="flow"><span>1 · Smooth<br><small>Gaussian</small></span><span>2 · Gradient<br><small>Sobel: M, α</small></span><span>3 · Non-max suppression<br><small>thin to 1 pixel</small></span><span>4 · Double threshold<br><small>strong / weak</small></span><span>5 · Hysteresis<br><small>weak joins strong</small></span></div>
{wm("Write this", "5 marks", [
    ("<b>Three criteria:</b>", "Canny promises three things. Write all three."),
    ("(1) <b>Good detection:</b> mark all real edges, few missed, few false.", "Find every real edge, and don't invent fake ones from noise."),
    ("(2) <b>Good localisation:</b> detected edge as close as possible to the true edge.", "The line you draw sits exactly on the real border, not shifted to the side."),
    ("(3) <b>Single response:</b> only one response per edge.", "One edge = one thin line, not three parallel lines."),
    ("<b>Five steps:</b>", "Then list the 5 steps in order."),
    ("1. <b>Smoothing:</b> f<sub>s</sub> = G ★ f, with Gaussian G(x,y) = e<sup>−(x²+y²)/2σ²</sup>, to remove noise.", "Blur the picture a little so tiny noise dots don't look like edges. ★ = slide the Gaussian mask over the image; σ = how strong the blur is."),
    ("2. <b>Gradient</b> with Sobel masks: M = √(g<sub>x</sub>² + g<sub>y</sub>²), α = tan⁻¹(g<sub>y</sub>/g<sub>x</sub>).", "g<sub>x</sub> = how fast brightness changes left to right, g<sub>y</sub> = top to bottom (the two Sobel masks). M = edge strength (big M = strong edge). α = the direction in which brightness increases."),
    ("3. <b>Non-maximum suppression:</b> round α to 0°, 45°, 90° or 135°; keep a pixel only if its M is not smaller than both neighbours along that direction, else set it to 0.", "After step 2 an edge is several pixels thick, like a hill. Walk across the hill (direction α) and keep only the top; set the slopes to 0. Now every edge is 1 pixel thin."),
    ("4. <b>Double threshold</b> T<sub>H</sub> : T<sub>L</sub> = 2:1 or 3:1. M ≥ T<sub>H</sub> → strong; T<sub>L</sub> ≤ M &lt; T<sub>H</sub> → weak; M &lt; T<sub>L</sub> → discarded.", "Two cut-off values. Above the high one = sure edge. Below the low one = sure NOT an edge. In between = \"maybe\". The high one is 2 to 3 times the low one."),
    ("5. <b>Hysteresis:</b> keep a weak pixel only if it is 8-connected to a strong pixel.", "A \"maybe\" pixel survives only if it touches a \"sure\" pixel (in any of the 8 directions). Real edges are long lines, so a maybe next to a sure is part of it; a lonely maybe is just noise."),
    ("<b>Why two thresholds:</b> one high T loses real edges (false negatives); one low T keeps noise (false positives). Hysteresis keeps the weak pixels that continue a real edge, giving thin, continuous edges.", "Only a high cut-off: faint parts of real edges disappear and leave gaps. Only a low cut-off: noise becomes edges. Two cut-offs + the touch rule keep faint parts that connect to strong ones and throw away lonely noise.")])}
<h3>Tiny worked example (slide 59, T<sub>H</sub> = 100, T<sub>L</sub> = 45)</h3>
{mats(mat(gN, "g<sub>N</sub> after step 3", small=True), mat(final, "final edges", hi={p for p in strong | keep}, small=True))}
<ul><li><b>Strong</b> (≥ 100): 200 and 101, kept. <span class="mm">They pass the high cut-off: sure edges.</span></li><li><b>Weak</b> (45–99): 57, 45, 50. <span class="mm">Between the two cut-offs: "maybe" pixels.</span></li>
<li>57 touches 101 → kept. 45 touches 200 → kept. 50 touches only 0s and the weak 45 → <b>dropped</b>. <span class="mm">A maybe must touch a SURE pixel; touching another maybe is not enough.</span></li></ul>
"""))

S.append(S2("cnum", "3b · Canny with numbers", "★ F23 Q3(a) 10 marks · SP25 Q2(d)(ii)", f"""
{ask([("\"Given the result of the first two Canny steps (magnitude + direction), complete the remaining 3 steps with high = 100, low = 45.\"", "F23"),
      ("\"Identify false positive / false negative edges.\" \"What happens with high = 245, low = 10?\"", "F23"),
      ("\"A pixel has magnitude 80 after NMS; low = 50, high = 100. How is it classified?\"", "SP25")])}
{idea("Three moves. (1) <b>NMS:</b> look at the two neighbours along each pixel's arrow; if the pixel is smaller than either one, it becomes 0. (2) <b>Double threshold:</b> ≥ high = strong, between = weak, below low = 0. (3) <b>Hysteresis:</b> a weak pixel stays only if it touches a strong one.")}
{mats(tbl(["", "c0", "c1", "c2"], [[f"r{r}"] + [f"{CM[r][c]} {CA[r][c]}" for c in range(3)] for r in range(3)], "narrow"))}
<p class="q">Given: magnitude M and gradient arrow at each pixel (F23 Q3(a)). T<sub>H</sub> = 100, T<sub>L</sub> = 45.</p>
<h3>Step 3 · Non-maximum suppression</h3>
<p>For each pixel, check the two neighbours in the arrow direction (forward and backward). Neighbours outside the 3×3 are ignored.</p>
{tbl(["pixel", "M", "arrow", "neighbours along the arrow", "result"], nms_rows, "narrow")}
{mat(CN, "g<sub>N</sub> after NMS", small=True)}
<h3>Step 4 · Double threshold</h3>
<p>≥ 100 → strong. 45 to 99 → weak. Below 45 → 0 (so 40 and 41 are gone).</p>
{mats(mat(CH, "g<sub>NH</sub>: strong (≥ 100)", small=True), mat(CW, "g<sub>NL</sub>: weak (45–99)", small=True))}
<h3>Step 5 · Hysteresis</h3>
{tbl(["weak pixel", "value", "strong 8-neighbours", "decision"], hy_rows, "narrow")}
{mat(CF, "final edge map g", hi={(r, c) for r in range(3) for c in range(3) if CF[r][c]}, small=True)}
{wm("(ii) and (iii): write this", "2 + 3 marks", [
    ("<b>(ii)</b> 74 at (2,2) is weak but kept because it touches the strong 101. If it was really noise, it is a <b>false positive</b>. 50 at (2,0) is weak with no strong neighbour, so it is dropped. If it was a real edge, it is a <b>false negative</b>.", "Name one pixel that might be a fake edge that got in, and one that might be a real edge that got thrown out."),
    ("<b>(iii)</b> With T<sub>H</sub> = 245 no pixel is strong, so hysteresis keeps nothing: the output is <b>empty</b>, every real edge is lost (false negatives). T<sub>L</sub> = 10 would let almost every pixel in as weak (false positives). The ratio 245:10 breaks the usual 2:1 to 3:1 rule.", "Too high a top cut-off: nothing is \"sure\", so nothing survives. Too low a bottom cut-off: everything becomes a \"maybe\"."),
    ("<b>SP25:</b> 50 ≤ 80 &lt; 100, so the pixel is a <b>weak</b> edge. It becomes an edge only if it is 8-connected to a strong pixel; otherwise it is discarded.", "80 is between the two cut-offs, so it is a \"maybe\".")])}
"""))

S.append(S2("fpfn", "3c · False positives and false negatives", "★ SP22, SP24, F21", f"""
{ask([("\"What are false positive and false negative edge pixels? How does Canny reduce (overcome) these errors?\"", "SP22, SP24, F21")])}
{idea("A false positive is a fake edge that got drawn (usually noise). A false negative is a real edge that got missed. Canny thins away the extras and rescues the faint real parts.")}
{wm("Write this", "2 + 2 marks", [
    ("<b>False positive:</b> a pixel marked as an edge that is not a real edge (e.g. noise). Caused by a threshold that is <b>too low</b>.", "Fake edge drawn."),
    ("<b>False negative:</b> a real edge pixel that is missed. Caused by a threshold that is <b>too high</b>.", "Real edge lost."),
    ("<b>How Canny reduces them:</b> Gaussian smoothing removes noise before the gradient (fewer false positives). <b>NMS</b> keeps only the local maxima, so thick edges become thin (fewer false positives).", "Blur kills noise; NMS deletes the extra pixels around each edge."),
    ("<b>Double threshold + hysteresis</b> keeps a weak pixel only when it is connected to a strong edge: faint parts of real edges are kept (fewer false negatives) and isolated weak noise is dropped (fewer false positives).", "The touch rule rescues faint real edges and throws away lonely noise.")])}
"""))

S.append(S2("sobel", "3d · Sobel with numbers", "★ SP22 Q6(b)(i) · SP25 Q2(d)(i) · SP25 Q1(e)", f"""
{ask([("\"Find the Sobel gradient-magnitude image and the edge direction of the central pixel.\"", "SP22"),
      ("\"Apply the Sobel operator in the horizontal direction; gradient value at the centre pixel?\"", "SP25"),
      ("\"What is the primary goal of edge detection? Name two gradient-based operators.\" Answer: find the boundaries where intensity changes sharply; Sobel and Prewitt (also Roberts).", "SP25")])}
{idea("Two masks. G<sub>x</sub> = right column minus left column (weights 1, 2, 1). G<sub>y</sub> = bottom row minus top row (weights 1, 2, 1). Edge strength = |G<sub>x</sub>| + |G<sub>y</sub>|.")}
{mats(mat([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], "G<sub>x</sub> mask", small=True), mat([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], "G<sub>y</sub> mask", small=True), mat(SI, "SP22 image", small=True))}
<h3>Centre pixel, in full</h3>
<p>Label the 3×3 window z1 … z9 row by row: z1 = 3, z2 = 7, z3 = 6, z4 = 2, z5 = 5, z6 = 8, z7 = 3, z8 = 4, z9 = 7.</p>
<p>G<sub>x</sub> = (z3 + 2z6 + z9) − (z1 + 2z4 + z7) = (6 + 16 + 7) − (3 + 4 + 3) = 29 − 10 = <b>19</b></p>
<p>G<sub>y</sub> = (z7 + 2z8 + z9) − (z1 + 2z2 + z3) = (3 + 8 + 7) − (3 + 14 + 6) = 18 − 23 = <b>−5</b></p>
<p>|∇f| ≈ |G<sub>x</sub>| + |G<sub>y</sub>| = 19 + 5 = <b>24</b> &nbsp;(exact √(19² + 5²) = 19.65)</p>
<p>Gradient angle α = tan⁻¹(G<sub>y</sub>/G<sub>x</sub>) = tan⁻¹(−5/19) = <b>{alpha:.2f}°</b>. The edge runs at right angles to the gradient: <b>edge direction = α − 90° = {alpha - 90:.2f}°</b>.</p>
<h3>Corner pixel (0,0), to show zero padding</h3>
<p>Window around (0,0), outside = 0: z1, z2, z3, z4, z7 = 0; z5 = 3, z6 = 7, z8 = 2, z9 = 5.</p>
<p>G<sub>x</sub> = (0 + 2×7 + 5) − (0 + 0 + 0) = <b>19</b>; G<sub>y</sub> = (0 + 2×2 + 5) − (0 + 0 + 0) = <b>9</b>; |∇f| = 19 + 9 = <b>28</b>.</p>
<h3>The whole magnitude image (same formulas at every pixel)</h3>
{mats(mat(SGX, "G<sub>x</sub>", small=True), mat(SGY, "G<sub>y</sub>", small=True), mat(SM, "|G<sub>x</sub>| + |G<sub>y</sub>|", small=True))}
<h3>SP25: the bright dot</h3>
<p>Patch [10 10 10; 10 50 10; 10 10 10]: G<sub>x</sub> = (10 + 20 + 10) − (10 + 20 + 10) = <b>0</b> (G<sub>y</sub> = 0 too). The left and right columns are equal and Sobel's centre weight is 0, so the dot is not seen. A Laplacian would give 4×50 − 4×10 = 160.</p>
"""))

S.append(S2("lines", "3e · Four line-detection masks", "★ SP23 Q3(e)(iii) · 2 marks", f"""
{ask([("\"Draw four line detection masks: horizontal, +45°, vertical, −45°.\"", "SP23")])}
{idea("Draw a line of 2s in the direction you want to detect and fill every other cell with −1. Each mask then sums to 0, so a flat area gives 0.")}
{mats(mat([[-1, -1, -1], [2, 2, 2], [-1, -1, -1]], "horizontal", small=True), mat([[-1, -1, 2], [-1, 2, -1], [2, -1, -1]], "+45°", small=True),
      mat([[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]], "vertical", small=True), mat([[2, -1, -1], [-1, 2, -1], [-1, -1, 2]], "−45°", small=True))}
{wm("Write this", "2 marks", [
    ("Draw the four masks above and label each.", "The 2s show the line's direction."),
    ("The coefficients sum to 0, so a constant area gives 0; a line in the mask's direction gives the largest response.", "Flat area: no answer. Line along the 2s: big answer.")])}
"""))

S.append(S2("schem", "3f · Canny schematic and hysteresis algorithm", "★ SP23 Q3(e)(i)(ii)", f"""
{ask([("\"Apply Canny to extract edges from f(x,y) of size m × n; draw a schematic of the whole process up to g(x,y).\"", "SP23"),
      ("\"Explain non-maxima suppression g<sub>N</sub>(x,y) OR hysteresis thresholding g<sub>NH</sub>, g<sub>NL</sub>.\"", "SP23")])}
<div class="flow"><span>f(x,y)<br><small>input</small></span><span>Gaussian<br><small>f<sub>s</sub> = G ★ f</small></span><span>Sobel<br><small>g<sub>x</sub>, g<sub>y</sub> → M, α</small></span><span>NMS<br><small>g<sub>N</sub></small></span><span>T<sub>H</sub>, T<sub>L</sub><br><small>g<sub>NH</sub>, g<sub>NL</sub></small></span><span>Connectivity<br><small>→ g(x,y)</small></span></div>
{wm("Write this", "3 + 3 marks", [
    ("<b>(i)</b> Draw the boxes above in a row with arrows, and write each box's formula under it.", "The schematic is the 5 steps as boxes; the formulas earn the marks."),
    ("<b>(ii) Hysteresis:</b> g<sub>NH</sub>(x,y) = g<sub>N</sub>(x,y) ≥ T<sub>H</sub>; g<sub>NL</sub>(x,y) = g<sub>N</sub>(x,y) ≥ T<sub>L</sub>; then g<sub>NL</sub> = g<sub>NL</sub> − g<sub>NH</sub>.", "Make a \"strong\" image and a \"weak\" image. Remove the strong pixels from the weak image so each pixel is in only one."),
    ("(a) Locate the next unvisited edge pixel p in g<sub>NH</sub>. (b) Mark as valid all weak pixels in g<sub>NL</sub> connected to p (8-connectivity). (c) Repeat until all pixels of g<sub>NH</sub> are visited. (d) Set to 0 all unmarked pixels of g<sub>NL</sub>.", "Start at each strong pixel and follow touching weak pixels; every weak pixel you can reach stays, the rest are deleted."),
    ("Output = g<sub>NH</sub> + the marked pixels of g<sub>NL</sub>.", "Final edges = strong ones + rescued weak ones."),
    ("<b>Or NMS:</b> round α to 0°, 45°, 90° or 135°; if M(x,y) is less than at least one of its two neighbours along that direction, g<sub>N</sub>(x,y) = 0, otherwise g<sub>N</sub>(x,y) = M(x,y).", "Keep only the top of each edge \"hill\".")])}
"""))

hist = [1, 3, 7, 9, 7, 3, 1, 0, 0, 1, 3, 6, 8, 6, 3, 1]
S.append(S2("thr", "4 · Thresholding", "★ SP23, SP25 cases", f"""
{ask([("\"Which method partitions pixels depending on their intensity values?\"", "SP23"),
      ("\"Segment the text from the paper\" in a document with uneven illumination", "SP25"),
      ("\"Global vs local vs adaptive threshold\" / \"How is T found automatically?\"", "slides 35–53")])}
{idea("Pick one number T. Brighter than T is object, the rest is background. On a histogram with two humps (background and object), T goes in the valley between them.")}
{bars(hist, caption="Two peaks: dark background (left) and bright object (right). T goes in the empty valley at level 7–8.", hi=set(range(9, 16)), ylabel="count", xlabel="gray level")}
{wm("Write this", "2–5 marks", [
    ("g(x,y) = 1 if f(x,y) &gt; T (object point); 0 if f(x,y) ≤ T (background point).", "Every pixel brighter than T becomes white (object); everything else becomes black (background)."),
    ("<b>Global:</b> one T for the whole image, T = T[f(x,y)].", "One cut-off number for the entire picture."),
    ("<b>Local / regional:</b> T = T[p(x,y), f(x,y)], p = a neighbourhood property such as its mean.", "Each small area picks its own cut-off from its own pixels (e.g. its average brightness)."),
    ("<b>Adaptive (dynamic):</b> T = T[x, y, p(x,y), f(x,y)].", "The cut-off also changes with the position in the picture, so it can follow a shadow."),
    ("<b>Iterative global threshold:</b> (1) initial T = mean intensity;", "Start with a guess: the average brightness."),
    ("(2) split: G₁ = pixels &gt; T, G₂ = pixels ≤ T; (3) means μ₁, μ₂;", "Split the pixels into a bright group and a dark group, and average each group."),
    ("(4) new T = ½(μ₁ + μ₂); (5) repeat until the change in T &lt; ΔT.", "The new cut-off is halfway between the two averages. Repeat until it stops moving.")])}
<p><b>Mini example</b> (values 10, 20, 30, 200, 210, 220): T₀ = 690 / 6 = <b>115</b>. G₁ = {{200, 210, 220}}, μ₁ = 210; G₂ = {{10, 20, 30}}, μ₂ = 20. T₁ = ½(210 + 20) = <b>115</b>, no change → stop, T = 115.</p>
{trap("Uneven illumination or a shadow: one global T fails (the shadowed part of the object drops below T). Write: use a <b>local / adaptive threshold</b>, so every region gets its own T.")}
"""))

S.append(S2("grow", "5 · Region growing", "★ SP23 tumor case · slides 9–17", f"""
{ask([("\"What segmentation method groups similar pixels?\"", "SP23"),
      ("\"What is region growing in image segmentation?\"", "SP25"),
      ("\"Apply region growing with the seed at the centre, |diff| ≤ T (4- or 8-direction)\"", "slide 14, F22")])}
{idea("Drop a seed inside the object. A neighbour joins if its value is close enough to the pixel it grows from. New members invite their own neighbours, like a stain spreading, until nobody else qualifies.")}
<p>Slide 14: seed = 60 at the centre, rule |difference| ≤ 5. Highlighted = the grown region.</p>
{mats(mat(G, "4-connectivity: 13 pixels", hi=R4, ctr=(3, 3), small=True), mat(G, "8-connectivity: 17 pixels", hi=R8, ctr=(3, 3), small=True))}
<p>8-connectivity also steps diagonally, so the 59, 60, 59, 59 on the left join. The 10s never join: |10 − 60| = 50 &gt; 5.</p>
<h3>Slide 14 worked in full: every pixel that joins</h3>
<p><b>(a) 4-connectivity</b> (up, down, left, right). Each new pixel is compared with the pixel it grows from:</p>
{tbl(["grows from", "neighbour", "test"], logrows(G, L4, 5), "narrow")}
<p>Region = seed + these 12 = <b>13 pixels</b>. Every other neighbour is a 10: |10 − 60| = 50 &gt; 5, so it can't join.</p>
<p><b>(b) 8-connectivity</b> also checks diagonals. Everything above joins again, plus these:</p>
{tbl(["grows from", "neighbour", "test"], extra8, "narrow")}
<p>Region = <b>17 pixels</b>.</p>
<h3>Another numeric (F22 B5(a)): seed at the centre, 8-direction, |diff| ≤ 4</h3>
{mat(G22, "input; seed (3,3) = 65", ctr=(3, 3), small=True)}
{tbl(["grows from", "neighbour", "test"], logrows(G22, L22, 4), "narrow")}
{mat(G22, f"final region: {len(R22)} pixels", hi=R22, ctr=(3, 3), small=True)}
<p>All 16 non-15 pixels join, each through a chain of steps of 4 or less (e.g. 65 → 61 → 58). The 15s never join: the closest gap is |58 − 15| = 43 &gt; 4.</p>
{wm("Write this", "2–5 marks", [
    ("Region growing groups pixels into larger regions, starting from <b>seed</b> points and appending neighbouring pixels with <b>similar properties</b> (gray level, texture, colour).", "Start from one pixel you know is inside the object, and keep adding neighbours that look like it."),
    ("(1) Choose the seed(s).", "Pick the starting pixel (the question usually gives it)."),
    ("(2) A 4- or 8-neighbour joins if it satisfies the predicate, e.g. |f(neighbour) − f(pixel it grows from)| ≤ T.", "Check the neighbours (4 = up/down/left/right, 8 = also the diagonals). A neighbour joins if its value is within T of the pixel next to it."),
    ("(3) Repeat with the new members.", "Every new member checks its own neighbours, so the region spreads like a stain."),
    ("(4) <b>Stop</b> when no more pixels satisfy the predicate.", "When no neighbour is close enough any more, you are done."),
    ("Works better than edge-based methods on noisy images. Problems: good seeds are hard to choose, hard to automate, needs a good similarity rule.", "One plus point and three problems: easy marks."),
    ("<b>With numbers:</b> table \"grows from | neighbour | test\", e.g. (3,3)=60 → (2,3)=64: |64 − 60| = 4 ≤ 5 ✓; then the final grid and the pixel count.", "Show every joining pixel as one row of the table, then draw the final region. 8-connectivity always gives an equal or bigger region than 4.")])}
"""))

S.append(S2("q3", "Q3 one-liners: cheap, sure marks", "case questions", tbl(["the story says", "write"], [
    ["\"partition pixels depending on intensity\"", "<b>thresholding</b>, g = 1 if f &gt; T"],
    ["\"group similar pixels\", \"tumor region from a point\"", "<b>region growing</b> from a seed, |diff| ≤ T"],
    ["\"uneven illumination\", \"shadow\", \"faded document\"", "<b>adaptive / local threshold</b>"],
    ["\"noisy image, need clean thin edges\"", "<b>Canny</b> (smooth first, then hysteresis)"],
    ["\"find boundaries of an organ / crack\"", "<b>Sobel</b> gradient or <b>Canny</b>"],
    ["\"straight lines: road, lane, fracture\"", "<b>Hough</b>: votes for lines in (ρ, θ), ρ = x cos θ + y sin θ"]])))

EXTRA = """<style>
.flow{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,130px),1fr));gap:8px;margin:12px 0}
.flow span{background:var(--surface);border:1px solid var(--ink);border-radius:8px;padding:8px 10px;font-weight:700;font-size:14.5px;line-height:1.35}
.flow small{font-weight:400;color:var(--fg2);font-size:13px}
.paper p.w{margin:12px 0 2px}
.paper p.m{margin:0 0 10px;padding:4px 10px;border-left:3px solid var(--line);border-radius:0;color:var(--fg2);font-size:15px}
.paper p.m::before{content:"means: ";font-weight:700;color:var(--ink)}
.paper p.wmhead{font-size:13.5px;color:var(--fg2);margin:4px 0 6px}
.mm{display:block;color:var(--fg2);font-size:15px}
.asks{border:2px solid var(--mark);border-radius:8px;padding:8px 14px;margin:10px 0 14px;background:var(--surface)}
.asks .k{color:var(--mark)} .asks ul{margin:4px 0 0} .asks li{margin:5px 0}
.asks .src{font-family:var(--f-mono);font-size:12px;color:var(--fg2);white-space:nowrap}
</style>"""
toc = [("why", "What to learn"), ("two", "Two approaches"), ("deriv", "Derivatives"), ("logq", "LoG question"), ("canny", "Canny"), ("cnum", "Canny numbers"), ("fpfn", "FP / FN"), ("sobel", "Sobel numbers"), ("lines", "Line masks"), ("schem", "Canny schematic"), ("thr", "Thresholding"), ("grow", "Region growing"), ("q3", "Q3 one-liners")]
OUT.write_text(page("Segmentation Fast Track", "CSE 4227 · decks 08–09 · only what she asks", "Edges and regions, the short way",
                    "Five topics from decks 08 and 09, each with a picture and the exact lines to write in the exam.", toc, S, extra=EXTRA), encoding="utf-8")
print(OUT, OUT.stat().st_size)
