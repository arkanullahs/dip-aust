"""Builds deck09_lesson.html: segmentation part II (region growing, split & merge, thresholding). Fall 2024 questions left out on purpose."""
import sys, pathlib
from collections import deque
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from kit import *

OUT = pathlib.Path(__file__).with_name("deck09_lesson.html")


# ---------------------------------------------------------------- maths (same rules as solvers.region_grow / iterative_threshold)
def grow(img, seed, T, conn=4):
    H, W = len(img), len(img[0])
    offs = [(-1, 0), (0, -1), (0, 1), (1, 0)] if conn == 4 else [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1) if i or j]
    reg, q, log = {seed}, deque([seed]), []
    while q:
        r, c = q.popleft()
        for dr, dc in offs:
            a, b = r + dr, c + dc
            if 0 <= a < H and 0 <= b < W and (a, b) not in reg:
                d = abs(img[a][b] - img[r][c])
                if d <= T:
                    reg.add((a, b)); q.append((a, b))
                    log.append((f"({r},{c}) = {img[r][c]}", f"({a},{b}) = {img[a][b]}", f"|{img[a][b]} − {img[r][c]}| = {d} ≤ {T}"))
    return reg, log


def iter_t(vals, T=None, eps=0.5):
    T = sum(vals) / len(vals) if T is None else T
    rows = []
    while True:
        g1, g2 = [v for v in vals if v > T], [v for v in vals if v <= T]
        m1, m2 = sum(g1) / len(g1), sum(g2) / len(g2)
        Tn = (m1 + m2) / 2
        rows.append([f"{T:.3f}", f"{{{', '.join(map(str, g1))}}}", f"{m1:.3f}", f"{{{', '.join(map(str, g2))}}}", f"{m2:.3f}", f"{Tn:.3f}", f"{abs(Tn - T):.3f}"])
        if abs(Tn - T) < eps:
            return rows, Tn
        T = Tn


def split(img, T, r0=0, c0=0, n=None, out=None, log=None):
    n = n or len(img)
    out = [] if out is None else out
    log = [] if log is None else log
    vals = [img[r][c] for r in range(r0, r0 + n) for c in range(c0, c0 + n)]
    rng = max(vals) - min(vals)
    name = f"rows {r0}–{r0 + n - 1}, cols {c0}–{c0 + n - 1}"
    if rng > T and n > 1:
        log.append([name, f"{max(vals)} − {min(vals)} = {rng}", f"{rng} &gt; {T}: <b>split</b> into 4"])
        h = n // 2
        for dr, dc in ((0, 0), (0, h), (h, 0), (h, h)):
            split(img, T, r0 + dr, c0 + dc, h, out, log)
    else:
        log.append([name, f"{max(vals)} − {min(vals)} = {rng}", f"{rng} ≤ {T}: keep"])
        out.append({"cells": {(r, c) for r in range(r0, r0 + n) for c in range(c0, c0 + n)}, "mn": min(vals), "mx": max(vals), "name": name})
    return out, log


def adjacent(A, B):
    return any((r + dr, c + dc) in B for r, c in A for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0)))


def merge(regions, T):
    regs, log = [dict(x) for x in regions], []
    changed = True
    while changed:
        changed = False
        for i in range(len(regs)):
            for j in range(i + 1, len(regs)):
                A, B = regs[i], regs[j]
                if adjacent(A["cells"], B["cells"]) and A["mx"] - B["mn"] < T and B["mx"] - A["mn"] < T:
                    log.append([f"[{A['mn']}…{A['mx']}] + [{B['mn']}…{B['mx']}]", f"{A['mx']} − {B['mn']} = {A['mx'] - B['mn']}, {B['mx']} − {A['mn']} = {B['mx'] - A['mn']}", f"both &lt; {T}: <b>merge</b>"])
                    regs[i] = {"cells": A["cells"] | B["cells"], "mn": min(A["mn"], B["mn"]), "mx": max(A["mx"], B["mx"])}
                    del regs[j]
                    changed = True
                    break
            if changed:
                break
    return regs, log


S = []

# ================================================================ 1. region vs edge
E8 = [[20, 0, 0, 0, 0, 0, 10, 10], [20, 0, 0, 0, 0, 0, 10, 10], [20, 0, 143, 143, 143, 143, 10, 10], [20, 0, 143, 200, 200, 143, 10, 10],
      [20, 0, 143, 200, 200, 143, 10, 10], [20, 0, 143, 143, 143, 143, 10, 10], [20, 0, 0, 0, 0, 0, 10, 10], [20, 0, 0, 0, 0, 0, 10, 10]]
S.append(sec("start", "Region-based segmentation: the idea", "3–8", SHORT, f"""
{idea("Deck 08 found <b>borders</b> (where brightness jumps). This deck finds <b>insides</b>: groups of touching pixels that look alike. A region is just \"a blob of connected pixels with similar values\".")}
<p><b>Slide 3.</b> Segmentation is based on one of two properties of intensity: <b>similarity</b> (partition into regions similar by predefined criteria) and <b>discontinuity</b> (detect region boundaries from local changes in intensity).</p>
<p><b>Slide 4.</b> In region-based segmentation we identify the regions occupied by objects by grouping pixels that are <b>similar in some region property</b>. <b>A region is a group of connected pixels with similar properties.</b></p>
{mats(mat(E8, "slides 5–7: 8×8 crop. Edge-based looks for the jumps 20|0, 0|143, 143|200; region-based groups 20s, 0s, 143s, 200s, 10s"))}
<p><b>Slide 8.</b> Two basic region-based techniques: <b>(i) region growing</b> and <b>(ii) region splitting and merging</b>.</p>
"""))

# ================================================================ 2. region growing
RG = [[10, 10, 10, 10, 10, 10, 10], [10, 10, 10, 69, 70, 10, 10], [59, 10, 60, 64, 59, 56, 60], [10, 59, 10, 60, 70, 10, 62], [10, 60, 59, 65, 67, 10, 65], [10, 10, 10, 10, 10, 10, 10], [10, 10, 10, 10, 10, 10, 10]]
r4, l4 = grow(RG, (3, 3), 5, 4)
r8, l8 = grow(RG, (3, 3), 5, 8)
F22 = [[15] * 7, [15, 15, 15, 68, 69, 15, 15], [64, 64, 63, 67, 70, 68, 15], [15, 15, 70, 65, 61, 71, 66], [15, 15, 69, 73, 58, 15, 15], [15] * 7, [15] * 7]
rf, lf = grow(F22, (3, 3), 4, 8)
S.append(sec("grow", "Region growing", "9–17", EXAM, f"""
{idea("Drop a seed on one pixel inside the object. Look at its neighbours: any neighbour whose value is close enough (difference ≤ T) joins the region. Then look at the new members' neighbours, and so on, like a stain spreading, until nothing new can join.")}
<p><b>Slide 9.</b> Region growing groups pixels or subregions into larger regions. The simplest form is <b>pixel aggregation</b>: start with a set of <b>seed</b> points and grow regions by appending to each seed the <b>neighbouring pixels that have similar properties</b> (gray level, texture, colour, shape). It works better than edge-based methods on <b>noisy images</b>, where edges are hard to find.</p>
<p><b>Slide 10. Bottom-up approach:</b> (1) find starting points; (2) include neighbouring pixels with a similar feature; (3) continue until every pixel is associated with a starting point. <b>Problems:</b> good starting points are not trivial to find, the process is hard to automate, and it needs a good similarity criterion.</p>
<p><b>Slides 11–13.</b> Start with one pixel of a potential region and add adjacent pixels until the pixels compared are too dissimilar; the first pixel can be the first unlabelled pixel or a chosen set of seeds; usually a statistical test decides who joins. Formally, with input f(x,y), seed array S(x,y) (1 = seed) and predicate Q:</p>
<ol><li>Find all connected components in S and erode each to one pixel.</li><li>Form f<sub>Q</sub>(x,y) = 1 where f satisfies the predicate Q.</li><li>Form g(x,y) = 1 for every pixel of f<sub>Q</sub> that is 8-connected to a seed.</li><li>Label each connected component of g with a different label.</li></ol>
<p>It needs a <b>stopping rule</b>: stop when no more pixels satisfy the predicate.</p>
{paper("Slides 14–17 · worked example", "worked", f'''<p class="q">The seed is the centre of the image. (a) Grow the region in horizontal and vertical directions (4-connectivity) when the difference between two pixel values is ≤ 5. (b) What if the region is grown in horizontal, vertical and diagonal directions (8-connectivity)?</p>
{mat(RG, "input; seed (3,3) = 60 outlined", ctr=(3, 3))}
<p><b>(a) 4-connectivity.</b> Pixels that join, in the order they are added (each compared with the pixel it grows from):</p>
{tbl(["grows from", "neighbour", "test"], l4, "narrow")}
{mat(RG, f"(a) region: {len(r4)} pixels", hi=r4, ctr=(3, 3))}
<p><b>(b) 8-connectivity</b> also reaches across corners, so the 59 at (3,1), the 60 and 59 at (4,1), (4,2) and the 59 at (2,0) join too:</p>
{mat(RG, f"(b) region: {len(r8)} pixels", hi=r8, ctr=(3, 3))}
{ans(f"4-connectivity: {len(r4)} pixels; 8-connectivity: {len(r8)} pixels. The 10s never join (|10 − 60| = 50 &gt; 5).")}''')}
{sim({"type": "grow", "img": RG, "seed": [3, 3], "T": 5, "conn": 4}, "slides 14–17: watch every neighbour check. Switch “Grow in” to 8-connectivity for part (b).")}
{trap("Compare each new pixel with <b>the pixel it grows from</b> (its neighbour), as the slide answer does. Comparing with the seed value instead can give a different region; the simulator lets you switch to see the difference. Say which one you use.")}
{paper("F22 Final B5(a) (another examiner's paper)", "5 marks part", f'''<p class="q">7×7 image; region growing with the seed at the centre, 8-direction growth when |difference| ≤ 4.</p>
{mat(F22, "input; seed (3,3) = 65", ctr=(3, 3))}
{tbl(["grows from", "neighbour", "test"], lf, "narrow")}
{mat(F22, f"region: {len(rf)} pixels", hi=rf, ctr=(3, 3))}
<p>Values 64, 64, 63 on row 2 and 66 on row 3 never join: no chain of steps ≤ 4 reaches them. (The question also asks for split and merge with T ≤ 5; a 7×7 image cannot be cut into equal quadrants, so state that you pad it to 8×8 or split unevenly, then follow the method below.)</p>''')}
{sim({"type": "grow", "img": F22, "seed": [3, 3], "T": 4, "conn": 8}, "F22 B5(a): 8-direction growth with T = 4.")}
"""))

# ================================================================ 3. split and merge
SM = [[5, 6, 6, 6, 7, 7, 6, 6], [6, 7, 6, 7, 5, 5, 4, 7], [6, 6, 4, 4, 3, 2, 5, 6], [5, 4, 5, 4, 2, 3, 4, 6],
      [0, 3, 2, 3, 3, 2, 4, 7], [0, 0, 0, 0, 2, 2, 5, 6], [1, 1, 0, 1, 0, 3, 4, 4], [1, 0, 1, 0, 2, 3, 5, 4]]
blocks, slog = split(SM, 4)
final, mlog = merge(blocks, 4)
dark = next(x for x in final if x["mn"] == 0)
S.append(sec("split", "Region splitting and merging", "18–33", LIKELY, f"""
{idea("Top-down instead of bottom-up. Start with the whole image as one region. If a region is not uniform enough, cut it into 4 quarters; keep cutting until every piece is uniform. Cutting can leave neighbouring pieces that really belong together, so finally glue adjacent pieces that are similar.")}
<p><b>Slides 18–19. Splitting:</b> start with the whole image as a single region R; select a predicate P (gray values, etc.); successively divide each region into smaller <b>quadrants</b> until P(R<sub>i</sub>) = TRUE for every region. The result is a <b>quadtree</b> (R → R1, R2, R3, R4; R4 → R41…R44). <b>Problem:</b> adjacent regions could be the same. <b>Solution:</b> allow merging.</p>
<p><b>Slide 20. Merging</b> is the opposite of splitting: merge adjacent regions R<sub>i</sub> and R<sub>j</sub> for which P(R<sub>i</sub> ∪ R<sub>j</sub>) = TRUE. <b>Split/merge:</b> stop when no further split or merge is possible.</p>
<h3>Slides 21–33 example (8×8, T = 4)</h3>
<p>Rules on the slides: <b>split</b> a region into quadrants if T &lt; (max − min); <b>merge</b> adjacent regions if T &gt; (max<sub>i</sub> − min<sub>j</sub>) <b>and</b> T &gt; (max<sub>j</sub> − min<sub>i</sub>).</p>
{mat(SM, "input 8×8")}
<p><b>Splitting:</b></p>
{tbl(["region", "max − min", "decision"], slog, "narrow")}
<p>The top-left and bottom-left quadrants stay whole; the top-right and bottom-right ones are cut into 2×2 blocks (slide 24). That gives {len(blocks)} regions.</p>
<p><b>Merging</b> (adjacent pairs, one at a time):</p>
{tbl(["regions [min…max]", "cross differences", "decision"], mlog, "narrow")}
{mat(SM, f"final: {len(final)} regions. Highlighted = the dark region (values {dark['mn']}–{dark['mx']}), as in red on slide 33", hi=dark["cells"])}
{ans(f"Two regions remain: a dark one (0–3) and a bright one (4–7).")}
"""))

# ================================================================ 4. thresholding
vals = [10, 12, 15, 11, 200, 190, 205, 14, 198, 13, 201, 16]
trows, Tf = iter_t(vals)
S.append(sec("thr", "Thresholding: global, local, adaptive", "35–53", EXAM, f"""
{idea("Pick one number T. Brighter than T → object (1), otherwise background (0). If the lighting is even, one T for the whole image works (global). If one side is in shadow, use a different T for each neighbourhood (local / adaptive).")}
{formula("g(x,y) = 1 if f(x,y) &gt; T (object point); &nbsp; 0 if f(x,y) ≤ T (background point)")}
<p><b>Slides 35–38.</b> Thresholding splits the image into two classes: foreground (objects) and background. Types:</p>
{tbl(["type", "T depends on", "slide 53 form"], [["<b>global</b>", "a single constant for the whole image", "T = T[f(x,y)]"], ["<b>local / regional</b> (variable)", "properties p(x,y) of a neighbourhood of (x,y), e.g. its mean", "T = T[p(x,y), f(x,y)]"], ["<b>dynamic / adaptive</b>", "the spatial coordinates (x,y) themselves", "T = T[x, y, p(x,y), f(x,y)]"]])}
<p><b>Slides 39–41. Global thresholding:</b> one constant threshold for every pixel. It can be fixed or found automatically from the <b>intensity histogram</b>: with a bimodal histogram (object peak + background peak), the optimal T sits in the <b>valley</b> between the peaks.</p>
<h3>Iterative (automatic) global threshold, slide 42</h3>
<ol><li>Select an initial estimate for T (e.g. the mean).</li><li>Segment with T: G1 = pixels &gt; T, G2 = pixels ≤ T.</li><li>Compute the means μ1 and μ2 of G1 and G2.</li><li>New T = ½(μ1 + μ2).</li><li>Repeat 2–4 until the change in T is smaller than ΔT.</li><li>Finally g(x,y) = 1 if f(x,y) &gt; T, else 0.</li></ol>
{paper("Practice · iterative threshold", "worked", f'''<p class="q">Pixel values: {", ".join(map(str, vals))}. Find the threshold (ΔT = 0.5).</p>
{tbl(["T", "G1 (&gt; T)", "μ1", "G2 (≤ T)", "μ2", "new T", "ΔT"], trows, "narrow")}
{ans(f"T ≈ {Tf:.2f}: the 5 bright values are object (1), the 7 dark values are background (0).")}''')}
{sim({"type": "thr", "values": vals}, "the iterative threshold, one round at a time. Try another start T: it lands on the same answer.")}
<p><b>Slides 43–45 (glance). Multilevel thresholding</b> for more than two classes: g = a if f &gt; T2, b if T1 &lt; f ≤ T2, c if f ≤ T1; such problems are often better solved with region growing.</p>
<p><b>Slides 47–48. Basic adaptive thresholding:</b> subdivide the image into small areas and use a different threshold for each subimage; the threshold for a pixel depends on which subimage it lies in (fig 10.30: a shaded image fails with one global T but works per subimage).</p>
<p><b>Slide 49. Why/when local thresholding:</b> global thresholding works only with <b>uniform illumination</b>; it fails with shadows, gradients or noisy backgrounds (a document with a shadow; a medical scan with uneven contrast). Local thresholding varies across neighbourhoods: T(x,y) = f(local mean, local variance, contrast); each pixel is compared with the statistics of its own neighbourhood.</p>
<p><b>Slides 50–52.</b> Global threshold τ = f({{i ∈ I}}); local τ<sub>a</sub> = f({{i ∈ N<sub>a</sub>}}) for pixel a with neighbourhood N<sub>a</sub>. Common choices: T = <b>mean</b>, T = <b>median</b>, T = <b>(max + min)/2</b> of the neighbourhood; <b>Niblack:</b> T = m + k·s (m = local mean, s = local standard deviation, k = Niblack constant). The neighbourhood size must be chosen.</p>
{paper("SP23 Final Q1(b) · brain tumour pipeline", "2 + 2 + 3 + 2 marks", '''<p class="q">Brain tumour detection: acquisition → preprocessing → segmentation (ROI) → feature extraction… (i) Method to remove noise from the scans in preprocessing? (ii) Method to partition pixels depending on intensity values? (iii) Which transformation function highlights specific ranges of pixel values? (iv) Which segmentation method groups similar pixels?</p>
<p><b>(i)</b> Spatial smoothing: a <b>median filter</b> for salt-and-pepper (impulse) noise, keeps edges sharp; a <b>Gaussian / averaging</b> filter for random noise (deck 06).</p>
<p><b>(ii)</b> <b>Thresholding</b>: g(x,y) = 1 if f(x,y) &gt; T else 0. T can be found automatically with the iterative global method, or locally (adaptive) if the scan's contrast is uneven.</p>
<p><b>(iii)</b> <b>Intensity-level (gray-level) slicing</b>: make the range [A, B] bright and either darken or keep the other levels, so the tumour's intensity range stands out (deck 04).</p>
<p><b>(iv)</b> <b>Region growing</b> (from a seed inside the tumour, add neighbours with |difference| ≤ T); split-and-merge also groups similar pixels.</p>''')}
{paper("SP25 Final Q3(a) · case study", "4 + 3 + 3 marks", '''<p class="q">A scanned document suffers from uneven illumination, faded ink and background noise. Enhance it for readability, then segment text lines and text for OCR. (i) Two enhancement techniques. (ii) Laplacian or Sobel for sharpening, and why? (iii) Which segmentation technique to separate text and text lines?</p>
<p><b>(i) Enhancement.</b> <b>1. Noise removal with a median filter</b> (3×3): removes the background specks (impulse noise) while keeping the edges of the strokes. <b>2. Contrast enhancement for the faded ink:</b> contrast stretching or histogram equalization spreads the crowded gray levels, so faint strokes become darker against the paper (a power-law with γ &gt; 1 also darkens light ink). Because the illumination is uneven, apply it locally (per region) or first remove the slowly varying background.</p>
<p><b>(ii) Laplacian.</b> Sharpening needs to boost fine detail (thin strokes, character edges) in every direction: the Laplacian is an isotropic 2nd derivative and g = f − ∇²f (or f + ∇²f for the negative mask) sharpens all orientations. Sobel is a 1st-derivative edge <b>detector</b> that gives thick edges and responds per direction; it is used to find edges, not to sharpen. The Laplacian amplifies noise, so denoise first (step i).</p>
<p><b>(iii) Local (adaptive) thresholding.</b> A single global T fails because one part of the page is darker (slide 49). Use T(x,y) from each pixel's neighbourhood, e.g. the local mean, (max + min)/2, or Niblack T = m + k·s, to turn text into 1 and paper into 0. Then group the text pixels: connected components (or region growing) give characters and words; rows of components with empty gaps between them give the text lines.</p>''')}
"""))

# ================================================================ 5. traps
S.append(sec("traps", "Traps and one-minute sheet", "all", None, f"""
<ul class="traps">
<li>Region = group of <b>connected</b> pixels with similar properties.</li>
<li>Region growing: say the seed, the connectivity (4 or 8), the rule (|difference| ≤ T) and what you compare with (the neighbour you grow from). 8-connectivity can only give a bigger or equal region.</li>
<li>Split: range (max − min) &gt; T → cut into 4. Merge adjacent regions when both cross differences are &lt; T.</li>
<li>Iterative threshold: T = ½(μ1 + μ2), repeat until ΔT is small. Pixels equal to T go to the background (≤ T).</li>
<li>Uneven illumination → local / adaptive threshold, never a single global T.</li>
</ul>
{tbl(["what", "formula"], [["threshold", "g = 1 if f &gt; T, else 0"], ["iterative T", "T<sub>new</sub> = ½(μ<sub>G1</sub> + μ<sub>G2</sub>)"], ["local T", "mean, median, (max + min)/2 of the neighbourhood"], ["Niblack", "T = m + k·s"], ["global / local / adaptive", "T[f] / T[p, f] / T[x, y, p, f]"]])}
"""))

toc = [("start", "Idea"), ("grow", "Region growing"), ("split", "Split & merge"), ("thr", "Thresholding"), ("traps", "Traps")]
OUT.write_text(page("DIP Deck 09 Lesson", "CSE 4227 · Chapter 10 · Deck 09", "Segmentation II: region growing, split & merge, thresholding",
                    "Region growing with a pixel-by-pixel simulator, split and merge worked on the slide example, global/local/adaptive thresholding with the iterative method, and the case-study questions answered. Fall 2024 is left out.",
                    toc, S, extra=sim_assets()), encoding="utf-8")

# ---------------------------------------------------------------- self-check (data/answers.json RGN/slide14-4, RGN/slide14-8, RGN/thr)
assert len(r4) == 13 and len(r8) == 17
assert round(Tf, 1) == 105.9 and trows[0][0] == "90.417"
assert len(blocks) == 10 and len(final) == 2 and dark["mx"] == 3
print(OUT, OUT.stat().st_size, "F22 region", len(rf), "splits", len(blocks), "merges", len(mlog))
