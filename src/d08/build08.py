"""Builds deck08_lesson.html: segmentation part I (edge detection, LoG, Canny). Fall 2024 questions left out on purpose."""
import sys, pathlib, math
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from kit import *

OUT = pathlib.Path(__file__).with_name("deck08_lesson.html")

SOB_X = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
SOB_Y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
PRE_X = [[-1, 0, 1]] * 3
PRE_Y = [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]
LINES = [("R1 horizontal", [[-1, -1, -1], [2, 2, 2], [-1, -1, -1]]), ("R2 +45°", [[-1, -1, 2], [-1, 2, -1], [2, -1, -1]]),
         ("R3 vertical", [[-1, 2, -1], [-1, 2, -1], [-1, 2, -1]]), ("R4 −45°", [[2, -1, -1], [-1, 2, -1], [-1, -1, 2]])]

# ---------------------------------------------------------------- Canny steps 3-5 (same rules as solvers.canny_345)
ARROW = {"→": (0, 1), "←": (0, -1), "↑": (-1, 0), "↓": (1, 0), "↗": (-1, 1), "↙": (1, -1), "↖": (-1, -1), "↘": (1, 1)}


def canny_345(M, D, TH, TL):
    H, W = len(M), len(M[0])
    ins = lambda r, c: 0 <= r < H and 0 <= c < W
    gN, rows = [row[:] for row in M], []
    if D:
        for r in range(H):
            for c in range(W):
                dr, dc = ARROW[D[r][c]]
                nb = [(r + s * dr, c + s * dc) for s in (1, -1)]
                vals = [M[a][b] for a, b in nb if ins(a, b)]
                keep = all(M[r][c] >= v for v in vals)
                gN[r][c] = M[r][c] if keep else 0
                rows.append([f"({r},{c})", M[r][c], D[r][c], ", ".join(f"({a},{b}) = {M[a][b]}" if ins(a, b) else f"({a},{b}) outside" for a, b in nb),
                             "kept" if keep else "suppressed → 0"])
    gNH = [[v if v >= TH else 0 for v in row] for row in gN]
    gNL = [[v if TL <= v < TH else 0 for v in row] for row in gN]
    g, weak = [row[:] for row in gNH], []
    for r in range(H):
        for c in range(W):
            if gNL[r][c]:
                touch = [(r + i, c + j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i or j) and ins(r + i, c + j) and gNH[r + i][c + j]]
                if touch:
                    g[r][c] = gNL[r][c]
                weak.append([f"({r},{c})", gNL[r][c], ", ".join(f"{gNH[a][b]} at ({a},{b})" for a, b in touch) or "none", "kept" if touch else "discarded"])
    return dict(rows=rows, gN=gN, gNH=gNH, gNL=gNL, g=g, weak=weak)


def on(M):
    return {(r, c) for r, row in enumerate(M) for c, v in enumerate(row) if v}


def corr0(img, m, r, c):
    H, W = len(img), len(img[0])
    return sum(m[i][j] * (img[r + i - 1][c + j - 1] if 0 <= r + i - 1 < H and 0 <= c + j - 1 < W else 0) for i in range(3) for j in range(3))


# ---------------------------------------------------------------- drawings
def edge_models():
    def one(pts, cap):
        return plot(10, 10, curves=[{"pts": pts, "cls": "c1"}], xticks=[], yticks=[], xlabel="position", ylabel="intensity", w=190, h=130, caption=cap)
    return figs(one([(0, 2), (5, 2), (5, 8), (10, 8)], "step: jumps at one pixel"),
                one([(0, 2), (3.5, 2), (6.5, 8), (10, 8)], "ramp: changes over a few pixels"),
                one([(0, 2), (3, 2), (4, 8), (6, 8), (7, 2), (10, 2)], "ridge / line: up then down"),
                one([(0, 2), (5, 8), (10, 2)], "roof: a peak"))


def nms_dial():
    c, R = 120, 92
    o = ['<svg viewBox="0 0 240 240" width="240" role="img" class="plot">', f'<circle cx="{c}" cy="{c}" r="{R}" fill="none" stroke="var(--line)"/>']
    for a in (22.5, 67.5, 112.5, 157.5):
        for s in (1, -1):
            x, y = c + R * math.cos(math.radians(a)) * s, c - R * math.sin(math.radians(a)) * s
            o.append(f'<line x1="{c}" y1="{c}" x2="{x:.1f}" y2="{y:.1f}" stroke="var(--fg2)" stroke-dasharray="3 3"/>')
    for a, lab in ((0, "0°"), (45, "45°"), (90, "90°"), (135, "135°")):
        for s in (1, -1):
            x, y = c + (R - 22) * math.cos(math.radians(a)) * s, c - (R - 22) * math.sin(math.radians(a)) * s
            o.append(f'<text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-size="12" font-weight="700" fill="var(--mark)">{lab}</text>')
    for a in (22.5, 67.5, 112.5, 157.5):
        x, y = c + (R + 12) * math.cos(math.radians(a)), c - (R + 12) * math.sin(math.radians(a))
        o.append(f'<text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" font-size="9.5" fill="var(--fg2)">{a}°</text>')
    o.append(f'<circle cx="{c}" cy="{c}" r="3" fill="var(--fg)"/></svg>')
    return f'<figure class="fig">{"".join(o)}<figcaption>slide 46: round the gradient angle to the nearest of 0°, 45°, 90°, 135°. Anything in [−22.5°, 22.5°] (or [157.5°, −157.5°]) counts as 0°.</figcaption></figure>'


def flow(steps):
    box = "display:inline-block;border:1.5px solid var(--ink);border-radius:6px;padding:6px 10px;background:var(--surface);font-size:14px"
    return '<div style="display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:8px 0">' + ' <span aria-hidden="true">→</span> '.join(f'<span style="{box}">{s}</span>' for s in steps) + "</div>"


def csim(cap, M, D, TH, TL):
    return sim({"type": "canny", "M": M, "D": D, "TH": TH, "TL": TL}, cap)


S = []

# ================================================================ 1. segmentation
S.append(sec("seg", "What segmentation is, and its two approaches", "3–7", EXAM, f"""
{idea("Segmentation = cutting the picture into meaningful pieces, usually \"object\" and \"background\". You can do it two ways: find where pixels <b>look alike</b> and group them (similarity), or find where the brightness <b>suddenly jumps</b> and draw the borders there (discontinuity). This deck is the second way: edges.")}
<p><b>Slide 3.</b> Image segmentation is part of image processing and of computer vision; it is <b>the first step in image analysis</b>:</p>
{flow(["input image", "segmentation", "annotation of objects", "feature extraction", "classification", "results"])}
<p><b>Slide 4.</b> Example: segmenting rice grains gives a binary image where each pixel gets a label: 0 = not a rice grain, 1 = rice grain.</p>
<p><b>Slide 5. What it does:</b> divides the image into regions; separates objects from the background and gives them labels; partitions the image into meaningful regions for an application. It lets us <b>count objects</b>, <b>measure geometry</b> (area, perimeter) and <b>study properties</b> (intensity, texture) of each object.</p>
<p><b>Slide 6. Principal approaches</b>, based on two basic properties of intensity values:</p>
{tbl(["property", "idea", "methods (slide 7)"], [
    ["<b>similarity</b>", "partition the image into regions that are similar according to predefined criteria", "thresholding (pixel intensities), region based (grouping similar pixels), match based (compare to a template)"],
    ["<b>discontinuity</b>", "partition the image at sharp changes in intensity, such as edges", "edge based (edges that separate regions), watershed (regions of local intensity minima)"]])}
{paper("F23 Final Q1(e)(i) · F25 Quiz Q3D Q1 (part)", "1 + … marks", '''<p class="q">Write down the types of image segmentation based on the two basic properties of intensity values. (F25 quiz: what are the two principal approaches to image segmentation?)</p>
<p>Segmentation algorithms use one of two properties of intensity:</p>
<p><b>1. Discontinuity:</b> partition the image where intensity changes sharply, e.g. at edges. Methods: point, line and edge detection (gradient, LoG, Canny); watershed.</p>
<p><b>2. Similarity:</b> partition the image into regions that are alike by a predefined rule. Methods: thresholding, region growing, region splitting and merging, template matching.</p>''')}
"""))

# ================================================================ 2. points and lines
hl = [[0] * 5, [0] * 5, [10] * 5, [0] * 5, [0] * 5]
dg = [[0, 0, 0, 0, 10], [0, 0, 0, 10, 0], [0, 0, 10, 0, 0], [0, 10, 0, 0, 0], [10, 0, 0, 0, 0]]
resp = [(n, corr0(hl, m, 2, 2), corr0(dg, m, 2, 2)) for n, m in LINES]
S.append(sec("lines", "Points and lines", "8–12", LIKELY, f"""
<p><b>Slide 8.</b> Three basic gray-level discontinuities: <b>points, lines, edges</b>. We look at how derivatives behave at them; the common way is to <b>run a mask through the image</b>.</p>
<p><b>Slides 9–10 (glance). Isolated points:</b> use the Laplacian mask; R = Σ w<sub>k</sub>z<sub>k</sub>; mark g(x,y) = 1 if |R| ≥ T, else 0 (turbine-blade X-ray example).</p>
<p><b>Slide 11. Line detection:</b> these masks extract lines one pixel thick running in a particular direction. The <b>preferred direction is weighted with a larger coefficient (2)</b>:</p>
{mats(*[mat(m, n, hi={(i, j) for i in range(3) for j in range(3) if m[i][j] == 2}, small=True) for n, m in LINES])}
{idea("Each mask has three 2s lying along its direction and −1 everywhere else; the weights add to 0, so a flat area gives 0. Put a mask on a line: if the line lies along the 2s, the response is big. Run all four and the largest |R| tells you the line's direction.")}
<p>Check it on a one-pixel-thick horizontal line (all 10 on the middle row) and a +45° line, at the centre pixel:</p>
{tbl(["mask", "horizontal line", "+45° line"], [[n, f"<b>{a}</b>" if a == max(r[1] for r in resp) else a, f"<b>{b}</b>" if b == max(r[2] for r in resp) else b] for n, a, b in resp])}
{sim({"type": "filter", "images": ["hline", "dline"], "filters": ["lineh", "linep45", "linev", "linem45"], "pad": "zero", "start": [2, 2]}, "run each line mask over a horizontal and a +45° line. The mask along the line gives the biggest number.")}
{paper("SP23 Final Q3(e)(iii)", "2 marks", '<p class="q">Draw the four line detection masks: horizontal, +45°, vertical, −45°.</p>' + mats(*[mat(m, n, small=True) for n, m in LINES]) + "<p>The 2s mark the direction each mask looks for; every mask sums to 0.</p>")}
"""))

# ================================================================ 3. edges and derivatives
strip = [5, 5, 4, 3, 2, 1, 0, 0, 0, 6, 0, 0, 0, 0, 1, 3, 1, 0, 0, 0, 0, 7, 7, 7, 7]
d1 = [strip[i + 1] - strip[i] for i in range(len(strip) - 1)]
d2 = [strip[i + 1] + strip[i - 1] - 2 * strip[i] for i in range(1, len(strip) - 1)]
S.append(sec("edges", "Edges and derivatives", "13–19", EXAM, f"""
{idea("An edge is where brightness changes fast. The 1st derivative (the change from one pixel to the next) is big all along a ramp, so it marks a <b>thick</b> edge. The 2nd derivative (the change of the change) only fires where the ramp starts and stops, with opposite signs, so it gives a <b>thin double</b> edge and the edge's centre is where it crosses zero.")}
<p><b>Slides 13–14.</b> Edges are pixels where the brightness function changes abruptly. Edge models:</p>
{edge_models()}
{formula("1st derivative: ∂f/∂x = f(x + 1) − f(x) &nbsp;&nbsp;&nbsp; 2nd derivative: ∂²f/∂x² = f(x + 1) + f(x − 1) − 2f(x)")}
<p><b>Slide 15.</b> The image strip (ramp, isolated point, thin line, flat segment, step) and its derivatives:</p>
{tbl(["", *range(len(strip))], [["f(x)", *strip], ["1st", *d1, ""], ["2nd", "", *d2, ""]], "narrow")}
<ul>
<li>The <b>1st derivative produces a thick edge</b>: it is nonzero (−1) along the whole ramp.</li>
<li>The <b>2nd derivative produces a much finer one</b>, nonzero only at the ramp's start and end with opposite signs (a double edge), and a <b>strong response at an isolated point</b> (6, −12, 6).</li>
</ul>
{sim({"type": "oned", "sig": strip, "modes": ["d1", "d2"]}, "both derivatives along the slide 15 strip, one position at a time.")}
<p><b>Slides 16–17.</b> Derivatives are used to find discontinuities: the <b>1st derivative tells where an edge is</b> (its maximum is at the centre of the edge); the <b>2nd derivative shows the edge direction</b> by its sign (dark-to-light or light-to-dark) and <b>passes through zero</b> (changes sign) at the centre of the edge.</p>
<p><b>Slide 18. Zero crossing:</b> the point where a function's sign changes. Edge detection with the Laplacian marks the points where the result crosses zero as edge points. It finds edges in all directions but works poorly when there is noise.</p>
<p><b>Slide 19.</b> Derivative-based edge detectors are <b>extremely sensitive to noise</b>: a little noise on a ramp makes the 1st derivative noisy and the 2nd derivative useless. So we smooth first.</p>
{paper("SP24 Final Q1(b)", "3 + 2 marks", f'''<p class="q">Define the first-order and second-order discrete derivatives of a 1-D digital image function f(x). What relation can be obtained between first- and second-order derivatives for an edge that is a ramp of constant slope?</p>
{formula("∂f/∂x = f(x + 1) − f(x) &nbsp;&nbsp;&nbsp;&nbsp; ∂²f/∂x² = f(x + 1) + f(x − 1) − 2f(x)")}
<p>Example ramp 5 5 4 3 2 1 0 0: 1st derivative 0 −1 −1 −1 −1 −1 0; 2nd derivative −1 0 0 0 0 1.</p>
<p><b>Relation on a ramp:</b> (1) the 1st derivative is nonzero (constant) along the entire ramp, so it gives a <b>thick</b> edge; (2) the 2nd derivative is nonzero only at the <b>onset and end</b> of the ramp, with <b>opposite signs</b> (a double edge), and zero along the ramp; (3) the line joining those two values crosses zero near the middle of the ramp: this <b>zero crossing</b> marks the edge centre, where the 1st derivative is largest. The sign of the 2nd derivative also tells whether the edge goes dark→light or light→dark.</p>''')}
"""))

# ================================================================ 4. gradient
sp22 = [[3, 7, 6], [2, 5, 8], [3, 4, 7]]
gx, gy = corr0(sp22, SOB_X, 1, 1), corr0(sp22, SOB_Y, 1, 1)
al = math.degrees(math.atan2(gy, gx))
GX = [[corr0(sp22, SOB_X, r, c) for c in range(3)] for r in range(3)]
GY = [[corr0(sp22, SOB_Y, r, c) for c in range(3)] for r in range(3)]
GM = [[abs(GX[r][c]) + abs(GY[r][c]) for c in range(3)] for r in range(3)]
p25 = [[10, 10, 10], [10, 50, 10], [10, 10, 10]]
S.append(sec("grad", "Gradient-based edge detection (Sobel, Prewitt)", "20–30", EXAM, f"""
<p><b>Slide 20. Two categories:</b> <b>gradient based</b> (look for the maximum and minimum of the 1st derivative) and <b>Laplacian based</b> (look for zero crossings of the 2nd derivative). <b>Slide 21:</b> gradient: Sobel, Roberts cross, Prewitt; Laplacian: Laplacian of Gaussian; hybrid (both): <b>Canny</b>.</p>
<p><b>Slide 22. Three main steps in edge detection:</b> (1) <b>filtering</b> (smoothing) to remove noise; (2) <b>differentiation</b> to highlight where intensity changes; (3) <b>detection</b> (thresholding) to decide which changes are significant; (4) localisation: find the exact edge location.</p>
{formula("∇f = [G<sub>x</sub>, G<sub>y</sub>] = [∂f/∂x, ∂f/∂y] &nbsp;&nbsp; |∇f| = √(G<sub>x</sub>² + G<sub>y</sub>²) ≈ |G<sub>x</sub>| + |G<sub>y</sub>| &nbsp;&nbsp; α(x,y) = tan⁻¹(G<sub>y</sub>/G<sub>x</sub>)")}
<p><b>Slides 23–24.</b> The gradient points toward the <b>maximum increase</b> of intensity. The edge is the boundary between regions of different intensity, so by convention the <b>edge direction is perpendicular to the gradient</b>: <b>edge direction = gradient direction − 90°</b>.</p>
{mats(mat(PRE_X, "Prewitt G<sub>x</sub>", small=True), mat(PRE_Y, "Prewitt G<sub>y</sub>", small=True), mat(SOB_X, "Sobel G<sub>x</sub>", small=True), mat(SOB_Y, "Sobel G<sub>y</sub>", small=True))}
<p><b>Slides 25–27.</b> 3×3 convolution masks; the differences are calculated at the centre pixel. Sobel puts weight 2 on the centre row/column (a little smoothing). Pipeline: image → G<sub>x</sub> and G<sub>y</sub> masks → ∇f → threshold → edges.</p>
<p><b>Slide 29.</b> Gradient methods: <b>simple</b> to implement and give <b>edges and their direction</b>, but are <b>sensitive to noise</b> and <b>not accurate in locating edges</b>. <b>Slides 31–32:</b> too much detail (e.g. brickwork) gives too many edges; smooth the image first.</p>
{paper("SP22 Final Q6(b)(i)", "4 marks", f'''<p class="q">3×3 image [3 7 6; 2 5 8; 3 4 7]. Find the Sobel gradient-magnitude image and the edge direction of the central pixel.</p>
<p>G<sub>x</sub> = (z3 + 2z6 + z9) − (z1 + 2z4 + z7) = (6 + 16 + 7) − (3 + 4 + 3) = <b>{gx}</b>; G<sub>y</sub> = (z7 + 2z8 + z9) − (z1 + 2z2 + z3) = (3 + 8 + 7) − (3 + 14 + 6) = <b>{gy}</b>.</p>
<p>|∇f| ≈ |{gx}| + |{gy}| = <b>{abs(gx) + abs(gy)}</b> (exact √({gx}² + {gy}²) = {math.hypot(gx, gy):.2f}).</p>
<p>Gradient angle α = tan⁻¹({gy}/{gx}) = <b>{al:.2f}°</b>; edge direction = α − 90° = <b>{al - 90:.2f}°</b>.</p>
<p>Whole magnitude image with zero padding:</p>{mats(mat(sp22, "input"), mat(GX, "G<sub>x</sub>"), mat(GY, "G<sub>y</sub>"), mat(GM, "|G<sub>x</sub>| + |G<sub>y</sub>|"))}''')}
{sim({"type": "filter", "images": ["sp22", "p25"], "filters": ["sobel", "prewitt", "sobelx", "sobely"], "pad": "zero", "start": [1, 1]}, "Sobel and Prewitt step by step on SP22 and on the SP25 bright point.")}
{paper("SP25 Final Q2(d)(i)", "2 marks", f'''<p class="q">3×3 patch [10 10 10; 10 50 10; 10 10 10]. Apply the Sobel operator in the horizontal direction; gradient value at the centre pixel?</p>
<p>G<sub>x</sub> = (10 + 2×10 + 10) − (10 + 2×10 + 10) = <b>{corr0(p25, SOB_X, 1, 1)}</b>. The left and right columns are equal, and Sobel's centre weight is 0, so the bright point is not seen by the gradient (G<sub>y</sub> = {corr0(p25, SOB_Y, 1, 1)} too). The full working is also on the deck 07 page.</p>''')}
"""))

# ================================================================ 5. LoG
S.append(sec("log", "Laplacian of Gaussian (LoG) and Marr–Hildreth", "33–37", EXAM, f"""
{idea("The Laplacian is so sensitive that a single noisy pixel looks like an edge. So blur first with a Gaussian (it removes the noise), then take the Laplacian, and mark where the result crosses zero. Blur + Laplacian can be merged into one mask: the LoG, the \"Mexican hat\".")}
<p><b>Slide 33. LoG steps:</b> (1) smoothing with a <b>Gaussian filter</b>; (2) enhance edges with the <b>Laplacian operator</b>. We usually smooth with a Gaussian before the Laplacian.</p>
<p><b>Slide 34 (glance):</b> LoG(x,y) = −1/(πσ⁴) [1 − (x² + y²)/(2σ²)] e<sup>−(x² + y²)/(2σ²)</sup>; a 5×5 approximation is [0 0 −1 0 0; 0 −1 −2 −1 0; −1 −2 16 −2 −1; 0 −1 −2 −1 0; 0 0 −1 0 0].</p>
<p><b>Slide 36. LoG properties:</b> <b>computationally cheaper</b> (the two filters combine into one); <b>no information about edge direction</b>; <b>false and missing edges can remain</b>; <b>localisation is better</b> than gradient operators.</p>
<p><b>Slide 37. Marr–Hildreth algorithm:</b> Gaussian smoothing, Laplacian, <b>zero crossings mark the edge location</b>, linear interpolation for sub-pixel location: g(x,y) = ∇²[G(x,y) ★ f(x,y)].</p>
{paper("F25 Quiz Q3D Q1", "4 + 2 marks", '''<p class="q">What are the two principal approaches to image segmentation? Why is a Laplacian filter typically combined with Gaussian smoothing (LoG) before edge detection in noisy environments?</p>
<p><b>Two approaches:</b> <b>discontinuity</b> (split where intensity changes abruptly: points, lines, edges) and <b>similarity</b> (group pixels that are alike: thresholding, region growing, split-and-merge).</p>
<p><b>Why Gaussian + Laplacian:</b> the Laplacian is a 2nd derivative, which is extremely sensitive to noise: every noisy pixel gives a strong response and false zero crossings. Gaussian smoothing first suppresses the noise, so the Laplacian's zero crossings mark real edges. Because both are linear, they combine into one LoG mask (cheaper), and the zero crossings give well-localised edges.</p>''')}
"""))

# ================================================================ 6. Canny
M23 = [[200, 40, 57], [10, 20, 101], [50, 41, 74]]
D23 = [["↓", "↓", "↙"], ["→", "↑", "←"], ["↑", "↑", "←"]]
C = canny_345(M23, D23, 100, 45)
C3 = canny_345(M23, D23, 245, 10)
G59 = [[200, 0, 57], [0, 45, 101], [50, 0, 0]]
C59 = canny_345(G59, None, 100, 45)
S.append(sec("canny", "Canny edge detector", "39–59", EXAM, f"""
{idea("Canny is the careful edge detector. Blur away noise, find how strongly and which way brightness changes, thin every thick edge to one pixel (keep only the peak), then sort pixels into sure / maybe / no with two thresholds, and keep a \"maybe\" only if it touches a sure edge.")}
<p><b>Slide 39. Three criteria:</b></p>
{tbl(["criterion", "meaning"], [["<b>good detection</b>", "find and mark all real edges (few missed, few false)"], ["<b>good localisation</b>", "minimal distance between the detected edge and the real edge"], ["<b>clear (single) response</b>", "only one response per edge"]])}
<p><b>Slide 40. Five steps:</b></p>
{flow(["f(x,y)", "1 smoothing (Gaussian): f<sub>s</sub> = G ★ f", "2 gradients: M(x,y), α(x,y)", "3 non-maximum suppression: g<sub>N</sub>", "4 double threshold: g<sub>NH</sub>, g<sub>NL</sub>", "5 hysteresis (connectivity)", "g(x,y)"])}
<ol>
<li><b>Smoothing:</b> blur the image to remove noise; G(x,y) = e<sup>−(x²+y²)/(2σ²)</sup>, f<sub>s</sub>(x,y) = G(x,y) ★ f(x,y) (slide 41).</li>
<li><b>Finding gradients:</b> edges are where the gradient magnitude is large. With Sobel or Prewitt masks on f<sub>s</sub>: M(x,y) = √(g<sub>x</sub>² + g<sub>y</sub>²), α(x,y) = tan⁻¹(g<sub>y</sub>/g<sub>x</sub>) (slide 43).</li>
<li><b>Non-maximum suppression:</b> only local maxima are marked as edges (thins wide ridges).</li>
<li><b>Double thresholding:</b> potential edges are found with a high and a low threshold.</li>
<li><b>Edge tracking by hysteresis:</b> final edges are those connected to a very certain (strong) edge; the rest are suppressed.</li>
</ol>
<h3>Step 3 in detail: non-maximum suppression (slides 45–49)</h3>
{figs(nms_dial())}
<p>Let d<sub>1</sub>…d<sub>4</sub> be the four basic directions of a 3×3 region (horizontal, −45°, vertical, +45°). (1) Find the direction d<sub>k</sub> closest to α(x,y). (2) If M(x,y) is <b>less than at least one of its two neighbours along d<sub>k</sub></b>, set g<sub>N</sub>(x,y) = 0 (suppress); otherwise g<sub>N</sub>(x,y) = M(x,y). Example (slide 47): α = 17° rounds to 0°, so compare pixel A with its left and right neighbours B and C; keep A only if it is larger.</p>
<h3>Steps 4–5: double threshold and hysteresis (slides 50–57)</h3>
{formula("g<sub>NH</sub>(x,y) = g<sub>N</sub>(x,y) ≥ T<sub>H</sub> &nbsp;&nbsp; g<sub>NL</sub>(x,y) = g<sub>N</sub>(x,y) ≥ T<sub>L</sub> &nbsp;&nbsp; then g<sub>NL</sub> = g<sub>NL</sub> − g<sub>NH</sub> &nbsp;&nbsp; (T<sub>H</sub> : T<sub>L</sub> = 2:1 or 3:1)")}
{tbl(["gradient value", "class", "fate"], [["≥ T<sub>H</sub>", "<b>strong</b> (sure edge)", "kept immediately"], ["between T<sub>L</sub> and T<sub>H</sub>", "<b>weak</b> (candidate)", "kept only if 8-connected to a strong pixel; otherwise treated as noise"], ["&lt; T<sub>L</sub>", "non-edge", "discarded"]])}
<p><b>Slide 53.</b> Threshold <b>too low</b> → false edges remain: <b>false positives</b>. Threshold <b>too high</b> → real edge points are removed: <b>false negatives</b>. <b>Slide 56:</b> a high threshold reduces false positives but increases false negatives; a low one does the opposite. <b>Canny reduces both</b>: non-maximum suppression removes extra (false-positive) pixels, and hysteresis keeps weak pixels that continue a real edge (fewer false negatives), filling gaps and giving thin, continuous contours.</p>
<p><b>Slide 57.</b> A and B are above High: sure edges. D is below Low: sure non-edge. C and E are weak; C is connected to B so it is kept; E is not, so it is discarded (edges are assumed to be long lines).</p>
{paper("Slide 59 · example", "worked", f'''<p>g<sub>N</sub> is given (after step 3); T<sub>H</sub> = 100, T<sub>L</sub> = 45.</p>
{mats(mat(G59, "g<sub>N</sub>"), mat(C59["gNH"], "g<sub>NH</sub> (≥ 100)", hi=on(C59["gNH"])), mat(C59["gNL"], "g<sub>NL</sub> (45–99)", hi=on(C59["gNL"])), mat(C59["g"], "final g", hi=on(C59["g"])))}
<p>57 touches 101 and 45 touches 200 and 101: kept. 50's neighbours are 0, 45 (weak) and 0: no <b>strong</b> neighbour, so it is dropped.</p>''')}
{trap("The slides keep a weak pixel only if it <b>directly</b> touches a strong pixel (that is why 50 is dropped on slide 59 even though it touches the weak 45). Use that rule in the exam.")}
{csim("slide 59: steps 4 and 5 only (g<sub>N</sub> given). Change the thresholds to see pixels move between strong, weak and gone.", G59, None, 100, 45)}
{paper("F23 Final Q3(a)", "5 + 2 + 3 marks", f'''<p class="q">Canny has 5 steps. The 3×3 result of the first two steps (magnitude, direction) is given. (i) Complete the remaining 3 steps with high threshold 100 and low threshold 45. (ii) Identify false positive / false negative edges. (iii) What happens with high = 245 and low = 10?</p>
{mat([[f"{M23[r][c]} {D23[r][c]}" for c in range(3)] for r in range(3)], "given: M and gradient direction")}
<p><b>Step 3 · non-maximum suppression:</b> compare each pixel with its two neighbours along its arrow; keep it only if it is not smaller than them.</p>
{tbl(["pixel", "M", "arrow", "neighbours along the arrow", "result"], C["rows"], "narrow")}
{mat(C["gN"], "g<sub>N</sub>")}
<p><b>Step 4 · double threshold</b> (T<sub>H</sub> = 100, T<sub>L</sub> = 45):</p>
{mats(mat(C["gNH"], "g<sub>NH</sub> strong", hi=on(C["gNH"])), mat(C["gNL"], "g<sub>NL</sub> weak", hi=on(C["gNL"])))}
<p><b>Step 5 · hysteresis:</b></p>
{tbl(["weak pixel", "value", "strong 8-neighbours", "decision"], C["weak"], "narrow")}
{mat(C["g"], "final edge map g", hi=on(C["g"]))}
<p><b>(ii)</b> 74 at (2,2) is weak but survives because it touches the strong 101: if it was noise it is a <b>false positive</b>. 50 at (2,0) is weak with no strong neighbour and is dropped: if it was a real edge it is a <b>false negative</b> (40 and 41 are below T<sub>L</sub> and dropped too).</p>
<p><b>(iii)</b> With T<sub>H</sub> = 245 nothing is strong, so hysteresis keeps no weak pixel: the output is <b>empty</b> (every real edge becomes a false negative). T<sub>L</sub> = 10 alone would let almost everything in as weak (false positives); 245:10 breaks the 2:1–3:1 rule.</p>''')}
{csim("F23 Q3(a): all three remaining steps, pixel by pixel. Set T<sub>H</sub> = 245, T<sub>L</sub> = 10 for part (iii).", M23, D23, 100, 45)}
{paper("SP25 Final Q2(d)(ii)", "2 marks", '''<p class="q">A pixel has gradient magnitude 80 after non-maxima suppression; low = 50, high = 100. How is it classified?</p>
<p>50 ≤ 80 &lt; 100, so it is a <b>weak edge</b> pixel. In hysteresis it is kept (becomes an edge) only if it is 8-connected to a strong pixel (≥ 100); otherwise it is discarded as noise.</p>''')}
{paper("SP22 Final Q6(a) · F21 A2(a) (another examiner)", "5 · 8 marks", '''<p class="q">How many steps are in Canny edge detection and what are they? Explain any one step (F21: explain non-maximum suppression). What are false positive and false negative edge pixels? How does Canny reduce these errors? (F21 also: what is image segmentation?)</p>
<p><b>Segmentation</b> (F21): dividing an image into meaningful regions, e.g. objects and background, as the first step of image analysis.</p>
<p><b>Five steps:</b> (1) Gaussian smoothing; (2) gradient magnitude and direction; (3) non-maximum suppression; (4) double thresholding; (5) edge tracking by hysteresis.</p>
<p><b>Non-maximum suppression:</b> the gradient magnitude forms wide ridges around edges. For each pixel, round its gradient angle to 0°, 45°, 90° or 135° and compare its magnitude with the two neighbours along that direction; keep it only if it is the largest, otherwise set it to 0. This thins edges to one pixel.</p>
<p><b>False positive:</b> a pixel marked as edge that is not a real edge (noise), caused by a threshold that is too low. <b>False negative:</b> a real edge pixel that is missed, caused by a threshold that is too high.</p>
<p><b>How Canny reduces them:</b> NMS removes non-peak pixels (fewer false positives); double thresholding with hysteresis keeps weak pixels only when they connect to strong edges, so real but faint edge parts are kept (fewer false negatives) while isolated weak noise is dropped.</p>''')}
{paper("SP24 Final Q1(e)", "1 + 2 + 2 marks", '''<p class="q">What is hysteresis thresholding in Canny? What are false positive and false negative edge pixels? How are they overcome?</p>
<p><b>Hysteresis thresholding:</b> uses two thresholds. Pixels ≥ T<sub>H</sub> are strong (sure) edges; pixels &lt; T<sub>L</sub> are discarded; pixels in between are weak and kept only if 8-connected to a strong edge. It links edge pieces and fills gaps.</p>
<p><b>False positive:</b> non-edge (noise) marked as edge (threshold too low). <b>False negative:</b> real edge missed (threshold too high).</p>
<p><b>Overcome:</b> NMS keeps only local maxima (fewer false positives); the low threshold plus the connectivity rule recovers faint parts of real edges (fewer false negatives) while isolated weak responses are removed.</p>''')}
{paper("SP23 Final Q3(e)(i)(ii)", "3 + 3 marks", f'''<p class="q">(i) Apply Canny to extract edges from f(x,y) of size m × n; draw a schematic of the whole process to g(x,y). (ii) Explain non-maxima suppression g<sub>N</sub>(x,y) OR hysteresis thresholding g<sub>NH</sub>, g<sub>NL</sub>.</p>
{flow(["f(x,y)", "Gaussian G(x,y): f<sub>s</sub> = G ★ f", "Sobel/Prewitt: g<sub>x</sub>, g<sub>y</sub>", "M = √(g<sub>x</sub>² + g<sub>y</sub>²), α = tan⁻¹(g<sub>y</sub>/g<sub>x</sub>)", "NMS → g<sub>N</sub>", "T<sub>H</sub>, T<sub>L</sub> → g<sub>NH</sub>, g<sub>NL</sub>", "connectivity → g(x,y)"])}
<p><b>(ii) Hysteresis:</b> g<sub>NH</sub> = g<sub>N</sub> ≥ T<sub>H</sub>, g<sub>NL</sub> = g<sub>N</sub> ≥ T<sub>L</sub>, then g<sub>NL</sub> = g<sub>NL</sub> − g<sub>NH</sub>. (a) locate the next unvisited edge pixel p in g<sub>NH</sub>; (b) mark as valid all weak pixels of g<sub>NL</sub> connected to p (8-connectivity); (c) repeat until all of g<sub>NH</sub> is visited; (d) set to 0 the pixels of g<sub>NL</sub> not marked; the output is g<sub>NH</sub> plus the marked g<sub>NL</sub> pixels. (Or explain NMS as in SP22 above.)</p>''')}
{paper("F23 Final Q1(e)(ii) · F22 B4(a) (another examiner)", "1 + 2 · 2 + 3 marks", '''<p class="q">How many steps are in Canny and what are they? (F22: explain the three main criteria of Canny.)</p>
<p><b>5 steps:</b> smoothing, finding gradients, non-maximum suppression, double thresholding, edge tracking by hysteresis.</p>
<p><b>Three criteria:</b> <b>good detection</b> (mark all real edges), <b>good localisation</b> (detected edge as close as possible to the true edge), <b>single (clear) response</b> (one response per edge).</p>''')}
{paper("SP25 Final Q1(e)", "4 marks", '''<p class="q">What is the primary goal of edge detection? Name two gradient-based operators. What is the role of non-maximum suppression in Canny? What is region growing?</p>
<p><b>Goal:</b> to find the pixels where intensity changes sharply, i.e. object boundaries, so the image can be segmented and its structure kept with much less data.</p>
<p><b>Two gradient operators:</b> Sobel and Prewitt (also Roberts).</p>
<p><b>NMS role:</b> thins the thick gradient ridges to one-pixel-wide edges by keeping only the local maximum along the gradient direction; this improves localisation and removes false responses.</p>
<p><b>Region growing:</b> start from seed pixel(s) and repeatedly add neighbouring pixels that are similar (e.g. |difference| ≤ T) until no more can be added (details on the deck 09 page).</p>''')}
"""))

# ================================================================ 7. Hough (not on Fall 2025 slides)
th = -45
rho = 2 * math.cos(math.radians(th)) + 1 * math.sin(math.radians(th))
S.append(sec("hough", "Hough transform (asked in SP25, not on the Fall 2025 slides)", "—", SHORT, f"""
<p>The Fall 2025 deck stops before section 10.2.7, so the Hough transform is not in the slides. SP25 still asked a 4-mark part, so here is a short answer.</p>
{paper("SP25 Final Q2(d)(iii)", "4 marks", f'''<p class="q">Find the line through (2,1), (3,2), (4,3). Are they collinear? Derive the polar representation of a line used in the Hough transform. Why is it preferred?</p>
<p>Slope (2,1)→(3,2) = (2 − 1)/(3 − 2) = 1; slope (3,2)→(4,3) = (3 − 2)/(4 − 3) = 1. Equal slopes through a common point, so the points are <b>collinear</b>: y = x − 1.</p>
<p><b>Polar form:</b> describe a line by the perpendicular from the origin: its length ρ and its angle θ. Every point (x, y) on the line satisfies <b>ρ = x cos θ + y sin θ</b>. For y = x − 1 (x − y − 1 = 0) the unit normal is (1, −1)/√2, so θ = −45° and ρ = 1/√2 ≈ {rho:.3f}. Check (2,1): 2 cos(−45°) + 1 sin(−45°) = {rho:.3f}.</p>
<p><b>Why preferred:</b> in y = ax + b the slope a goes to infinity for vertical lines, so the parameter space is unbounded. In (ρ, θ) both parameters are bounded: θ ∈ [−90°, 90°], ρ ∈ [−D, D] with D the image diagonal, so a finite accumulator array works for every line.</p>''')}
"""))

# ================================================================ 8. traps
S.append(sec("traps", "Traps and one-minute sheet", "all", None, f"""
<ul class="traps">
<li>Two approaches: <b>similarity</b> (thresholding, region growing, split/merge) and <b>discontinuity</b> (points, lines, edges).</li>
<li>Line masks: the 2s lie along the direction the mask detects; each mask sums to 0.</li>
<li>1st derivative: thick edge, max at the edge centre. 2nd derivative: double edge, zero crossing at the centre, strong at isolated points, noise-sensitive.</li>
<li>Edge direction = gradient direction − 90°.</li>
<li>LoG = Gaussian smoothing + Laplacian; no direction info; better localisation; cheaper as one mask.</li>
<li>Canny: 3 criteria, 5 steps. NMS compares along the <b>gradient</b> arrow. Double threshold ratio 2:1 or 3:1. Weak pixels survive only if 8-connected to a strong one.</li>
<li>Too low threshold → false positives; too high → false negatives.</li>
</ul>
{tbl(["what", "formula"], [["gradient", "|∇f| = √(G<sub>x</sub>² + G<sub>y</sub>²) ≈ |G<sub>x</sub>| + |G<sub>y</sub>|, α = tan⁻¹(G<sub>y</sub>/G<sub>x</sub>)"], ["2nd derivative", "f(x+1) + f(x−1) − 2f(x)"], ["LoG / Marr–Hildreth", "g = ∇²[G ★ f], edges at zero crossings"], ["double threshold", "g<sub>NH</sub> = g<sub>N</sub> ≥ T<sub>H</sub>; g<sub>NL</sub> = (g<sub>N</sub> ≥ T<sub>L</sub>) − g<sub>NH</sub>"]])}
"""))

IMAGES = {
    "hline": {"name": "horizontal line (one pixel thick)", "img": hl, "note": "At the centre: R1 = 60, the others 0."},
    "dline": {"name": "+45° line", "img": dg, "note": "At the centre: R2 = 60, the others smaller."},
    "sp22": {"name": "SP22 Q6(b) · 3×3", "img": sp22, "note": f"Centre: G<sub>x</sub> = {gx}, G<sub>y</sub> = {gy}, |G| = {abs(gx) + abs(gy)}."},
    "p25": {"name": "SP25 Q2(d) · bright point", "img": p25, "note": "Centre: both Sobel masks give 0."},
}
toc = [("seg", "Segmentation"), ("lines", "Points & lines"), ("edges", "Derivatives"), ("grad", "Gradient"), ("log", "LoG"), ("canny", "Canny"), ("hough", "Hough"), ("traps", "Traps")]
OUT.write_text(page("DIP Deck 08 Lesson", "CSE 4227 · Chapter 10 · Deck 08", "Segmentation I: edges, gradient, LoG and Canny",
                    "The two segmentation approaches, line masks, derivatives at edges, Sobel and Prewitt, LoG, and every Canny step with a pixel-by-pixel simulator. Past questions are solved the way you would write them; Fall 2024 is left out.",
                    toc, S, extra=sim_assets(images=IMAGES)), encoding="utf-8")

# ---------------------------------------------------------------- self-check (data/answers.json CAN/F23-F/3a, CAN/slide59; deck 07 SP22 values)
assert C["gN"] == [[200, 40, 57], [0, 0, 101], [50, 41, 74]]
assert C["g"] == [[200, 0, 57], [0, 0, 101], [0, 0, 74]]
assert not on(C3["g"])
assert C59["g"] == [[200, 0, 57], [0, 45, 101], [0, 0, 0]]
assert (gx, gy) == (19, -5) and d1[:6] == [0, -1, -1, -1, -1, -1] and d2[7:10] == [6, -12, 6]
assert [r[1] for r in resp] == [60, 0, 0, 0] and resp[1][2] == 60
print(OUT, OUT.stat().st_size, "alpha", round(al, 2), "rho", round(rho, 3))
