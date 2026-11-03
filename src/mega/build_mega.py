# DIP final mega sheet: cues, formulas with one or two worked iterations, theory skeletons, Q3 case answers.
# Every number on the page is computed here and checked with asserts.
import math, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from kit import page, formula, idea, trap, ans, tbl, mat, mats, paper, cases, bars, stairs

OUT = HERE / "dip_mega_sheet.html"
rhu = lambda x: math.floor(x + 0.5)  # her rounding: .5 goes up
log2 = math.log2


def S2(id_, title, meta, body):
    return f'<section class="sec" id="{id_}"><div class="sechead"><h2>{title}</h2><div class="meta"><span class="slides">{meta}</span></div></div>{body}</section>'


def cue(rows):  # rows: (you read, it means, you write)
    return tbl(["you read", "it means", "you write / use"], rows, "cue")


# ================================================================ worked numbers
# Ch 2
bits_1024 = 1024 * 768 * 12
nn = [math.ceil(3 / 5 * i) for i in range(1, 6)]
p, q = (1, 2), (4, 6)
D4, D8, De = abs(p[0] - q[0]) + abs(p[1] - q[1]), max(abs(p[0] - q[0]), abs(p[1] - q[1])), math.dist(p, q)
assert bits_1024 == 9437184 and nn == [1, 2, 2, 3, 3] and (D4, D8, De) == (7, 4, 5.0)

# Ch 3 point operations
c_log = 255 / math.log10(256)
s_log50 = rhu(c_log * math.log10(51))
s_g05 = rhu(7 * (3 / 7) ** 0.5)
s_g20 = rhu(7 * (3 / 7) ** 2.0)
s_st = rhu((100 - 50) * 255 / (150 - 50))
assert s_log50 == 181 and s_g05 == 5 and s_g20 == 1 and s_st == 128

# histogram equalization (slide 55 counts)
nk = [8, 10, 10, 2, 12, 16, 4, 2]
N = sum(nk)
cdf, run = [], 0
for v in nk:
    run += v; cdf.append(run / N)
sk = [rhu(7 * c) for c in cdf]
eqh = [sum(n for n, s in zip(nk, sk) if s == lvl) for lvl in range(8)]
assert sk == [1, 2, 3, 3, 5, 6, 7, 7] and sum(eqh) == N
he_rows = [[r, n, f"{n / N:.4f}", f"{c:.4f}", f"{7 * c:.3f}", f"<b>{s}</b>"] for r, (n, c, s) in enumerate(zip(nk, cdf, sk))]

# filters on one noisy window
W = [[10, 20, 30], [40, 200, 60], [70, 80, 90]]
flat = [v for r in W for v in r]
mean = sum(flat) / 9
wts = [[1, 2, 1], [2, 4, 2], [1, 2, 1]]
wavg = sum(W[i][j] * wts[i][j] for i in range(3) for j in range(3)) / 16
med = sorted(flat)[4]
assert sum(flat) == 600 and med == 60 and wavg == 87.5

# Laplacian and Sobel
Wl = [[10, 10, 10], [10, 50, 10], [10, 10, 10]]
lap = Wl[0][1] + Wl[1][0] + Wl[1][2] + Wl[2][1] - 4 * Wl[1][1]
g_lap = Wl[1][1] - lap
Ws = [[10, 10, 10], [10, 10, 10], [90, 90, 90]]
Gx = (Ws[0][2] + 2 * Ws[1][2] + Ws[2][2]) - (Ws[0][0] + 2 * Ws[1][0] + Ws[2][0])
Gy = (Ws[2][0] + 2 * Ws[2][1] + Ws[2][2]) - (Ws[0][0] + 2 * Ws[0][1] + Ws[0][2])
assert lap == -160 and g_lap == 210 and Gx == 0 and Gy == 320

# iterative threshold
vals = [10, 20, 30, 200, 210, 220]
T0 = sum(vals) / len(vals)
g1, g2 = [v for v in vals if v > T0], [v for v in vals if v <= T0]
T1 = (sum(g1) / len(g1) + sum(g2) / len(g2)) / 2
assert T0 == 115 and T1 == 115

# chain code (slide 12 / SP24) and the teacher's tricks
cc = [int(c) for c in "007756554322212"]
cfd = [(cc[(i + 1) % len(cc)] - c) % 8 for i, c in enumerate(cc)]
rots = lambda s: [s[k:] + s[:k] for k in range(len(s))]
ncfd = min(rots(cfd))
assert "".join(map(str, cfd)) == "070617077700716" and "".join(map(str, ncfd)) == "007160706170777"

# Huffman (SP25 A–D probabilities)
P = {"A": 0.4, "B": 0.3, "C": 0.2, "D": 0.1}
code = {"A": "1", "B": "00", "C": "010", "D": "011"}
Lavg = sum(P[s] * len(code[s]) for s in P)
H = -sum(p_ * log2(p_) for p_ in P.values())
assert abs(Lavg - 1.9) < 1e-9 and abs(H - 1.8464) < 1e-4


def golomb(n, m):
    q_, r_ = divmod(n, m)
    k = math.ceil(log2(m)); c = 2 ** k - m
    rb = format(r_, f"0{k - 1}b") if r_ < c else format(r_ + c, f"0{k}b")
    return "1" * q_ + "0" + (rb if k > 0 else ""), q_, r_, k, c


g49, g512 = golomb(9, 4), golomb(12, 5)
assert g49[0] == "11001" and g512[0] == "11010"

# arithmetic coding, slide 53 example
sub = {"a1": (0.0, 0.2), "a2": (0.2, 0.4), "a3": (0.4, 0.8), "a4": (0.8, 1.0)}
lo, hi, ari_rows = 0.0, 1.0, []
for s in ["a1", "a2", "a3", "a3", "a4"]:
    rng = hi - lo
    lo, hi = lo + rng * sub[s][0], lo + rng * sub[s][1]
    ari_rows.append([s, f"{rng:.5g}", f"{lo:.5g}", f"{hi:.5g}"])
assert abs(lo - 0.06752) < 1e-12 and abs(hi - 0.0688) < 1e-12


def lzw(pix):
    d, nxt, cur, out, rows = {(i,): i for i in range(256)}, 256, (), [], []
    for x in pix:
        t = cur + (x,)
        if t in d:
            rows.append(["-".join(map(str, cur)) or "", x, "", "", ""]); cur = t
        else:
            out.append(d[cur]); d[t] = nxt
            rows.append(["-".join(map(str, cur)), x, d[cur], nxt, "-".join(map(str, t))]); nxt += 1; cur = (x,)
    out.append(d[cur]); rows.append(["-".join(map(str, cur)), "", d[cur], "", ""])
    return out, rows


lz_out, lz_rows = lzw([39, 39, 126, 126] * 4)
assert lz_out == [39, 39, 126, 126, 256, 258, 260, 259, 257, 126]

# fidelity (SP25 Q3(b)ii)
f0 = [[1, 4, 3], [2, 3, 4], [2, 4, 5]]
fd = [[v + 2 for v in r] for r in f0]
se = sum((b - a) ** 2 for r0, r1 in zip(f0, fd) for a, b in zip(r0, r1))
sd = sum(b * b for r in fd for b in r)
rmse = math.sqrt(se / 9)
assert se == 36 and rmse == 2 and sd == 248

# colour
R, G, B = 0.8, 0.4, 0.2
num = 0.5 * ((R - G) + (R - B)); den = math.sqrt((R - G) ** 2 + (R - B) * (G - B))
theta = math.degrees(math.acos(num / den))
Hh = theta if B <= G else 360 - theta
Sat = 1 - 3 * min(R, G, B) / (R + G + B)
Ii = (R + G + B) / 3
assert abs(Hh - 19.1066) < 1e-3 and abs(Sat - 0.5714) < 1e-4 and abs(Ii - 0.4667) < 1e-4

# morphology 1-D
row = [1, 0, 0, 0, 1, 1, 1, 0, 1, 1]
ero = [min(row[i - 1:i + 2]) for i in range(1, 9)]
dil = [max(row[i - 1:i + 2]) for i in range(1, 9)]
assert ero == [0, 0, 0, 0, 1, 0, 0, 0] and dil == [1, 0, 1, 1, 1, 1, 1, 1]

J = lambda s: " ".join(map(str, s))

# ================================================================ sections
S = []

S.append(S2("paper", "The paper in one look", "70 marks · 3 hours", f"""
{idea("Three questions. Q1 asks you to <b>explain</b>, Q2 asks you to <b>calculate</b>, Q3 gives a <b>story</b> (a hospital, a satellite, a scanner) and asks which method fits. The same 12 methods answer all three; only the way you write changes.")}
{tbl(["question", "what it wants", "choice", "how you write it"], [
    ["<b>Q1</b> theory · 25", "define, compare, list effects", "any 5 of 6 (one per chapter)", "definition → formula → 2–3 points → small sketch"],
    ["<b>Q2</b> math · 24", "numbers: histogram, filter, compression, chain code / morphology", "about 3 of 4", "formula → table of every step → final grid / code → one-line comment"],
    ["<b>Q3</b> case · 21", "a real problem; pick and justify methods", "any 3 of 4", "problem → method → why → steps (with equation) → result"]])}
<p><b>Time:</b> about 2.5 minutes per mark. A 7-mark case = 17 minutes. Never spend more than 20 minutes on one part.</p>
<p><b>Where marks hide:</b> the formula line, the working table and the final labelled answer each carry marks on their own. A right answer with no table loses about half.</p>
"""))

S.append(S2("map", "How everything connects", "all 14 decks", f"""
{idea("Every topic is one stop on the same road: take a picture, make it look better, find the object, describe its shape, store it small. Once you see the road, you know which chapter a question comes from.")}
<div class="road">
<div class="stop"><b>1 · Capture</b><span>decks 01–03</span><p>sampling, quantization, bits, pixels, neighbours, distance</p></div>
<div class="stop"><b>2 · Enhance</b><span>decks 04–07</span><p>point ops (negative, log, gamma, stretch, slice, bit-plane) → histogram → smooth → sharpen</p></div>
<div class="stop"><b>3 · Find objects</b><span>decks 08–09</span><p>edges (gradient, Laplacian, Canny) or regions (threshold, region growing)</p></div>
<div class="stop"><b>4 · Clean shape</b><span>decks 11–12</span><p>erosion, dilation, opening, closing, boundary, hit-or-miss</p></div>
<div class="stop"><b>5 · Describe shape</b><span>deck 10</span><p>chain code → CFD → shape number</p></div>
<div class="stop"><b>6 · Store / colour</b><span>decks 13–14</span><p>Huffman, Golomb, LZW, RLE, RMSE · RGB, CMY, HSI</p></div>
</div>
<h3>The same idea shows up twice (connect these dots)</h3>
{tbl(["first meeting", "second meeting", "the link"], [
    ["thresholding s = 1 if r &gt; k (deck 04)", "global / iterative threshold (deck 09), binary input for morphology (deck 11)", "one cut turns gray into object vs background"],
    ["contrast stretching (deck 04)", "histogram equalization (deck 05)", "both spread values over 0…L−1; HE does it automatically from the CDF"],
    ["mean / Gaussian smoothing (deck 06)", "Canny step 1, LoG (deck 08)", "smooth first so noise doesn't make fake edges"],
    ["Laplacian ∇²f (deck 07)", "LoG / zero crossings (deck 08)", "2nd derivative: thin double edges, sensitive to noise"],
    ["Sobel / Prewitt gradient (deck 07)", "Canny step 2 (deck 08)", "1st derivative: edge strength and direction"],
    ["median filter (deck 06)", "salt-and-pepper case questions (Q3)", "median ignores extreme 0/255 values and keeps edges"],
    ["boundary β(A) = A − (A ⊖ B) (deck 11)", "chain code walks that boundary (deck 10)", "first find the outline, then code it"],
    ["erosion (deck 11)", "hit-or-miss = two erosions (deck 12)", "HMT erodes the object with B1 and the background with B2"],
    ["entropy H (deck 13)", "Huffman L<sub>avg</sub> (deck 13)", "H is the floor: L<sub>avg</sub> ≥ H, efficiency = H / L<sub>avg</sub>"],
    ["histogram p(r<sub>k</sub>) = n<sub>k</sub>/N (deck 05)", "probabilities for Huffman and entropy (deck 13)", "same counting table, different use"],
    ["intensity I in HSI (deck 14)", "gray-level methods (decks 04–06)", "enhance I only, keep H and S, colours stay true"]], "")}
"""))

S.append(S2("cues", "Cue words: what the question really asks", "Q3 and Q1 triggers", f"""
{idea("Case questions hide the method inside a story. Spot the <b>problem word</b>, map it to the <b>method</b>, then justify with one line of how the method works. Learn this table and Q3 becomes matching.")}
<h3>Enhancement stories</h3>
{cue([
    ["too <b>dark</b>, underexposed X-ray / MRI, details hidden in shadows", "dark values squashed together", "<b>log</b> or <b>gamma γ &lt; 1</b>; or histogram equalization"],
    ["<b>washed out</b>, too bright, aerial photo, faded", "bright values squashed together", "<b>gamma γ &gt; 1</b> (3.0–4.0 on the slides)"],
    ["<b>low contrast</b>, dull, narrow histogram", "values use only part of 0…L−1", "<b>contrast stretching</b> or <b>histogram equalization</b>"],
    ["<b>highlight a range</b>: tumor, bone [120, 200], water in satellite", "one band of gray levels matters", "<b>gray-level slicing</b>: give both approaches (background 0, or keep r)"],
    ["huge dynamic range, Fourier spectrum", "values 0 to 10⁶ won't fit 0–255", "<b>log transform</b>"],
    ["negative film, white lesions in dark mammogram", "dark ↔ light swap helps viewing", "<b>negative</b> s = L−1−r"],
    ["hidden watermark, which bits matter, compress by bits", "image = stack of bit planes", "<b>bit-plane slicing</b>: top planes carry the shape"],
    ["want the look of another image", "target histogram given", "<b>histogram matching</b> (specification)"]])}
<h3>Noise and sharpness stories</h3>
{cue([
    ["<b>salt-and-pepper</b>, impulse noise, black and white dots", "isolated extreme 0 / 255 pixels", "<b>median filter</b> 3×3 (keeps edges)"],
    ["Gaussian noise, grainy, random noise", "every pixel slightly off", "<b>mean</b> / <b>weighted average</b> / Gaussian filter (blurs a bit)"],
    ["only pepper (black dots) / only salt (white dots)", "one-sided impulses", "<b>max</b> filter removes pepper, <b>min</b> filter removes salt"],
    ["<b>blurred</b>, fine detail, sharpen, faded ink edges", "edges too soft", "<b>Laplacian</b> g = f − ∇²f, or <b>unsharp masking / high-boost</b>"],
    ["find edges / outline of an organ, crack, road edge", "big change in intensity", "<b>Sobel / Prewitt</b> gradient, best: <b>Canny</b>"],
    ["noisy image but need thin, clean, connected edges", "edge detector that resists noise", "<b>Canny</b> (smooth, gradient, NMS, double threshold, hysteresis)"],
    ["straight lines: roads, lanes, fracture lines", "pixels lying on a line", "line masks (−1 −1 −1 / 2 2 2) or Hough transform (one line: votes in (ρ, θ))"]])}
<h3>Segmentation stories</h3>
{cue([
    ["separate object from background, text from paper", "two intensity groups", "<b>thresholding</b>; iterative T = ½(μ₁ + μ₂)"],
    ["<b>uneven illumination</b>, shadow on the document", "one T can't fit everywhere", "<b>local / adaptive threshold</b> (T from each neighbourhood)"],
    ["group similar pixels from a seed point, tumor region", "grow from a known pixel", "<b>region growing</b>: |neighbour − pixel it grows from| ≤ T"],
    ["\"partition pixels depending on intensity\"", "the words for thresholding", "<b>thresholding</b> (SP23 Q1(b)ii)"],
    ["\"groups similar pixels\"", "the words for region-based", "<b>region growing</b> or split & merge (SP23 Q1(b)iv)"]])}
<h3>Shape stories (binary images)</h3>
{cue([
    ["<b>broken characters</b>, gaps in roads, cracks to join", "small breaks in the object", "<b>dilation</b> (or <b>closing</b> to keep thickness)"],
    ["small bright spots, specks, small particles to remove", "objects smaller than the SE", "<b>opening</b> (erode, then dilate)"],
    ["small holes inside objects, reflections to fill", "background specks inside the object", "<b>closing</b> (dilate, then erode)"],
    ["touching coins, count objects", "thin necks join the objects", "<b>erosion</b> to split, then count connected components"],
    ["outline / boundary of roads, organ edge (binary)", "the object's border pixels", "<b>boundary β(A) = A − (A ⊖ B)</b>"],
    ["find corners, end points, a fixed pattern", "match object AND background", "<b>hit-or-miss</b> A ⊛ B = (A ⊖ B₁) ∩ (Aᶜ ⊖ B₂)"],
    ["recognise a shape whatever its rotation / start", "describe the boundary by numbers", "<b>chain code → CFD → NCFD</b> (shape number)"]])}
<h3>Storage and colour stories</h3>
{cue([
    ["medical, legal, must not lose any detail", "lossless only", "<b>Huffman</b>, <b>LZW</b>, <b>RLE</b>, Golomb, arithmetic"],
    ["many <b>repeating patterns / colours</b>, bitmap, fixed-length codes", "the same sequences come back", "<b>LZW</b> (dictionary, 9-bit codes)"],
    ["long runs of the same value, fax, binary documents", "consecutive equal pixels", "<b>RLE</b> (value, run length)"],
    ["some gray levels far more common than others", "unequal probabilities", "<b>Huffman</b> (short codes for frequent values)"],
    ["small integers / prediction errors, geometric spread", "small values common", "<b>Golomb</b> G<sub>m</sub>(n)"],
    ["whole message as one number", "non-block code", "<b>arithmetic</b> coding"],
    ["how good is the decompressed image?", "fidelity criterion", "<b>RMSE</b> (objective) or rating scale (subjective)"],
    ["printing, ink, printer", "subtractive colour", "<b>CMY / CMYK</b>"],
    ["monitor, camera, display", "additive colour", "<b>RGB</b>"],
    ["segment by colour, lighting changes, describe colour like humans", "separate colour from brightness", "<b>HSI</b> (use Hue)"]])}
{trap("When a case lists four methods (SP25 Q3(d): chain code, histogram, Hough, power-law), give each one line of <b>what it does</b>, one line of <b>how it helps here</b>, and one <b>limitation</b>. That is the 3-part pattern she marks.")}
"""))

S.append(S2("q3", "Q3 case answers: the template and six solved stories", "SP23 · F23 · SP24 · SP25 · F21 · F25 quiz", f"""
{formula("Problem (cue word) → Method → Why it works → Steps / equation → Result + one limitation")}
<p>Write each case as 4–6 short lines in that order. Name the method in bold in the first line; the examiner looks for it.</p>
{paper("SP23 Q1(b) · brain tumor pipeline", "2 + 2 + 3 + 2", '''
<p><b>(i) Remove noise:</b> median filter (scan noise is impulse-like; median keeps tumor edges) or Gaussian/mean for random noise.</p>
<p><b>(ii) Partition by intensity:</b> thresholding, g = 1 if f &gt; T else 0; T found iteratively.</p>
<p><b>(iii) Highlight a range of values:</b> gray-level slicing, [A, B] → L−1, others 0 (or unchanged).</p>
<p><b>(iv) Group similar pixels:</b> region growing from a seed inside the tumor, add 8-neighbours with |difference| ≤ T.</p>''')}
{paper("SP25 Q3(a) · faded, unevenly lit document for OCR", "4 + 3 + 3", '''
<p><b>(i) Enhance:</b> contrast stretching or histogram equalization (faded ink = low contrast) and median filter (background specks).</p>
<p><b>(ii) Laplacian</b> over Sobel: text is thin strokes and fine detail; the 2nd derivative gives thin, sharp response and g = f − ∇²f sharpens in one mask. Sobel gives thick edges and needs two masks.</p>
<p><b>(iii) Segment:</b> local (adaptive) thresholding, because illumination is uneven; then horizontal projection to split text lines.</p>''')}
{paper("SP25 Q3(c) · satellite roads with spots and gaps", "3 + 3 + 3", '''
<p><b>(i) Opening</b> A ∘ B = (A ⊖ B) ⊕ B: erosion deletes spots smaller than B, dilation restores the roads' size.</p>
<p><b>(ii) Closing</b> A • B = (A ⊕ B) ⊖ B: dilation bridges small gaps, erosion returns the road width. Use a line-shaped SE along the road.</p>
<p><b>(iii) Boundary</b> β(A) = A − (A ⊖ B): subtract the eroded road from the road; one-pixel outline remains.</p>''')}
{paper("F23 Q3(b) · touching coins, small particles", "5 + 5", '''
<p><b>(i) Erosion</b> with a disk SE larger than the necks: touching coins split into separate blobs; count with connected-component labeling. (Follow with dilation if size matters = opening.)</p>
<p><b>(ii) Opening</b> with an SE just larger than the small particles: they cannot contain the SE, so erosion removes them; dilation restores the large particles to their size.</p>''')}
{paper("SP24 Q3(a) · salt-and-pepper only on the object", "4 + 4", '''
<p><b>(i) Median filter</b> 3×3 on the object region (mask from thresholding), background untouched: impulses sort to the ends, the median ignores them, edges stay sharp.</p>
<p><b>(ii) Morphology:</b> opening removes white (salt) specks, closing fills black (pepper) dots inside the object.</p>''')}
{paper("SP25 Q3(d) · bone fracture, four methods", "7", '''
<p><b>Power-law:</b> γ &lt; 1 brightens a dark X-ray so thin cracks show; limitation: also brightens noise.</p>
<p><b>Histogram analysis / equalization:</b> spreads bone gray levels for contrast; limitation: may over-enhance soft tissue.</p>
<p><b>Hough transform:</b> finds straight fracture lines by voting in (ρ, θ); limitation: curved cracks are missed.</p>
<p><b>Chain code:</b> codes the bone outline; a break shows as an irregular CFD (sudden turns); limitation: noise-sensitive, needs a clean boundary.</p>''')}
"""))

# ---------------------------------------------------------------- formulas
pw_rows = [("(s₁ / r₁) · r", "0 ≤ r &lt; r₁"), ("s₁ + (s₂ − s₁)(r − r₁) / (r₂ − r₁)", "r₁ ≤ r ≤ r₂"), ("s₂ + (L−1 − s₂)(r − r₂) / (L−1 − r₂)", "r &gt; r₂")]
S.append(S2("f-ch2", "Formulas 1 · capture and pixels", "decks 01–03", f"""
{tbl(["what", "formula", "one worked line"], [
    ["gray levels", "L = 2<sup>k</sup>, range 0 … L−1", "k = 12 → L = 4096, range 0–4095"],
    ["image size", "b = M × N × k bits (÷ 8 = bytes)", f"1024 × 768 × 12 = {bits_1024:,} bits = {bits_1024 // 8:,} bytes"],
    ["nearest-neighbour zoom", "position = ⌈i × old / new⌉, i = 1…new", f"3×3 → 5×5: ⌈0.6 i⌉ = {J(nn)} (copy those rows / columns)"],
    ["city-block D<sub>4</sub>", "|x − s| + |y − t|", f"p(1,2), q(4,6): 3 + 4 = <b>{D4}</b>"],
    ["chessboard D<sub>8</sub>", "max(|x − s|, |y − t|)", f"max(3, 4) = <b>{D8}</b>"],
    ["Euclidean D<sub>e</sub>", "√[(x − s)² + (y − t)²]", f"√(9 + 16) = <b>{De:g}</b>"]])}
<ul>
<li><b>Sampling</b> = digitise coordinates (spatial resolution, blocky if too few). <b>Quantization</b> = digitise amplitude (gray-level resolution, false contouring if too few).</li>
<li><b>4-adjacent:</b> q in N<sub>4</sub>(p). <b>8-adjacent:</b> q in N<sub>8</sub>(p). <b>m-adjacent:</b> q in N<sub>4</sub>(p), <i>or</i> q in N<sub>D</sub>(p) and N<sub>4</sub>(p) ∩ N<sub>4</sub>(q) has no pixel in V. m removes the double paths of 8-adjacency.</li>
<li>Distance properties: D ≥ 0 (= 0 only if p = q), D(p,q) = D(q,p), D(p,z) ≤ D(p,q) + D(q,z). Always D<sub>4</sub> ≥ D<sub>e</sub> ≥ D<sub>8</sub>.</li>
</ul>
"""))

S.append(S2("f-ch3", "Formulas 2 · point transformations", "deck 04", f"""
{tbl(["method", "formula", "worked line", "use"], [
    ["negative", "s = (L−1) − r", "8-bit, r = 100 → 155", "white detail in dark areas"],
    ["log", "s = c · log(1 + r), c = (L−1)/log(L)", f"c = 255/log 256 = {c_log:.2f}; r = 50 → {c_log:.2f} × log 51 = <b>{s_log50}</b>", "expand dark, compress bright"],
    ["gamma", "s = (L−1) · (r / (L−1))<sup>γ</sup>", f"3-bit, r = 3: γ = 0.5 → 7 × 0.6547 = <b>{s_g05}</b>; γ = 2 → 7 × 0.1837 = <b>{s_g20}</b>", "γ &lt; 1 brighter, γ &gt; 1 darker"],
    ["min–max stretch", "s = (r − r<sub>min</sub>)(L−1) / (r<sub>max</sub> − r<sub>min</sub>)", f"[50, 150] → [0, 255]: r = 100 → 50 × 255/100 = 127.5 → <b>{s_st}</b>", "fill the whole range"],
    ["threshold", "s = L−1 if r &gt; k, else 0", "k = 127: 90 → 0, 200 → 255", "binary object vs background"],
    ["bit plane n", "bit<sub>n</sub> = ⌊r / 2<sup>n−1</sup>⌋ mod 2 (weight 2<sup>n−1</sup>)", "13 = 1101: planes 4,3,2,1 = 1,1,0,1", "top planes = shape, bottom = noise"]])}
<h3>Piecewise contrast stretching with (r₁, s₁), (r₂, s₂)</h3>
{cases("s", pw_rows)}
<p><b>Three special settings:</b> r₁ = s₁ and r₂ = s₂ → identity (no change). r₁ = r₂, s₁ = 0, s₂ = L−1 → thresholding. r₁ ≤ r₂ and s₁ &lt; s₂ in between → contrast stretching. Draw all three graphs.</p>
<h3>Gray-level slicing, range [A, B] (F25 quiz: bone [120, 200])</h3>
<div class="two"><div>{cases("approach 1", [("L−1", "A ≤ r ≤ B"), ("0", "otherwise")])}</div><div>{cases("approach 2", [("L−1", "A ≤ r ≤ B"), ("r", "otherwise")])}</div></div>
<p>r = 100 → 0 / 100 · r = 150 → 255 / 255 · r = 220 → 0 / 220. Approach 1 = binary, background gone; approach 2 = background kept.</p>
{trap("Find L first. A 3-bit image means L − 1 = 7, so gamma and log use 7, not 255. Round .5 up.")}
"""))

S.append(S2("f-he", "Formulas 3 · histogram equalization", "deck 05 · in almost every final", f"""
{formula("p(r<sub>k</sub>) = n<sub>k</sub> / N &nbsp;→&nbsp; CDF = Σ p &nbsp;→&nbsp; s<sub>k</sub> = round( (L−1) × CDF<sub>k</sub> )")}
<p>Worked (3-bit, N = {N}, n<sub>k</sub> = [{', '.join(map(str, nk))}]). Do every row like the first two:</p>
<p>r = 0: p = 8/64 = 0.125, CDF = 0.125, 7 × 0.125 = 0.875 → <b>1</b>. &nbsp; r = 1: p = 10/64 = 0.15625, CDF = 0.28125, 7 × 0.28125 = 1.969 → <b>2</b>.</p>
{tbl(["r", "n<sub>k</sub>", "p", "CDF", "7 × CDF", "s"], he_rows, "narrow")}
<p><b>New histogram:</b> add the counts that land on the same s: s = 3 gets 10 + 2 = 12; s = 7 gets 4 + 2 = 6. Total stays {N}.</p>
{bars(eqh, caption="Equalized histogram: spread out, not perfectly flat, because levels are discrete. Write that sentence.")}
<p><b>Matching</b> (if asked): equalize the input → H, equalize the target → S, map each r to the z whose S is closest to its H (ties → higher S).</p>
{trap("Draw three things: the original histogram, the equalized histogram and the transformation (staircase). Each is a separate mark.")}
"""))

S.append(S2("f-filt", "Formulas 4 · smoothing and sharpening", "decks 06–07", f"""
<p>One window, every filter. Centre pixel = 200 (a noise spike):</p>
{mats(mat(W, "window f", ctr=(1, 1)), mat(wts, "weights / 16"))}
{tbl(["filter", "rule", "result at the centre"], [
    ["mean (box)", "Σ / 9", f"600 / 9 = {mean:.2f} → <b>67</b>"],
    ["weighted average", "Σ w·f / 16", f"1400 / 16 = <b>{wavg}</b>"],
    ["median", "sort 9, take the 5th", f"{J(sorted(flat))} → <b>{med}</b> (spike gone)"],
    ["min / max", "smallest / largest", "10 / 200"]], "narrow")}
<h3>Laplacian sharpening (2nd derivative)</h3>
{formula("∇²f = f(x+1,y) + f(x−1,y) + f(x,y+1) + f(x,y−1) − 4f(x,y)")}
{mats(mat(Wl, "f", ctr=(1, 1)), mat([[0, 1, 0], [1, -4, 1], [0, 1, 0]], "mask (centre −4)"))}
<p>∇²f = 10 + 10 + 10 + 10 − 4×50 = <b>{lap}</b>. Centre negative, so g = f − ∇²f = 50 + 160 = <b>{g_lap}</b>: the bright dot gets brighter, detail stands out. One-pass mask: [0 −1 0; −1 5 −1; 0 −1 0].</p>
<h3>Sobel gradient (1st derivative)</h3>
{mats(mat(Ws, "f"), mat([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], "Gx"), mat([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], "Gy"))}
<p>Gx = (10 + 20 + 90) − (10 + 20 + 90) = <b>{Gx}</b>. Gy = (90 + 180 + 90) − (10 + 20 + 10) = <b>{Gy}</b>. |∇f| ≈ |Gx| + |Gy| = <b>{abs(Gx) + abs(Gy)}</b>: a strong horizontal edge. Direction α = tan⁻¹(Gy / Gx).</p>
<p><b>Unsharp masking:</b> mask = f − blurred f; g = f + k · mask. k = 1 unsharp, k &gt; 1 high-boost.</p>
{tbl(["1st derivative (gradient)", "2nd derivative (Laplacian)"], [
    ["thick edges, non-zero along ramps", "thin double edges, zero on ramps, zero crossing at the edge"],
    ["less noise-sensitive", "very noise-sensitive, strong on isolated points"],
    ["gives direction", "no direction, one mask"]])}
"""))

S.append(S2("f-seg", "Formulas 5 · edges and segmentation", "decks 08–09", f"""
<h3>Canny: 3 criteria, 5 steps</h3>
<p><b>Criteria:</b> low error rate (find real edges only), good localisation (on the true edge), single response (one pixel per edge).</p>
<ol><li><b>Smooth</b> with a Gaussian.</li><li><b>Gradient</b> magnitude and angle (Sobel).</li><li><b>Non-maximum suppression:</b> keep a pixel only if it beats its two neighbours along the gradient direction (thin edges).</li>
<li><b>Double threshold</b> T<sub>H</sub> and T<sub>L</sub> (ratio 2:1 or 3:1): strong ≥ T<sub>H</sub>, weak between.</li><li><b>Hysteresis:</b> keep a weak pixel only if it is 8-adjacent to a strong one.</li></ol>
<h3>Thresholding</h3>
{formula("g(x,y) = 1 if f(x,y) &gt; T, else 0 &nbsp;&nbsp; T<sub>new</sub> = ½(μ₁ + μ₂)")}
<p>Iterative T, values {J(vals)}: start T₀ = mean = {T0:g}. Group above: mean {sum(g1) / len(g1):g}; group at or below: mean {sum(g2) / len(g2):g}. T₁ = ½(210 + 20) = {T1:g} = T₀, so stop.</p>
<p><b>Region growing:</b> start at a seed, add a 4- or 8-neighbour when |neighbour − the pixel it grows from| ≤ T, repeat until nothing joins. <b>Split &amp; merge:</b> split a block into 4 while (max − min) &gt; T, merge neighbours that are similar.</p>
<p><b>Line masks</b> (sum 0, the 2s lie along the line): horizontal [−1 −1 −1; 2 2 2; −1 −1 −1], vertical [−1 2 −1; −1 2 −1; −1 2 −1], ±45° with the 2s on a diagonal.</p>
"""))

S.append(S2("f-cc", "Formulas 6 · chain code (the teacher's tricks)", "deck 10", f"""
<p><b>Compass:</b> 0 = right, counting <b>anticlockwise</b>: 1 ↗, 2 ↑, 3 ↖, 4 ←, 5 ↙, 6 ↓, 7 ↘ (4-direction: 0 →, 1 ↑, 2 ←, 3 ↓).</p>
<ol><li><b>CC:</b> walk the boundary in the direction asked; write the arrow number of each move until you are back at the start.</li>
<li><b>CFD trick:</b> from each digit to the next, count anticlockwise steps on the compass. Same arrow = 0. The last digit goes to the first.</li>
<li><b>NCFD trick:</b> underline the 0s. Start at the longest run of 0s (the end joins the start), read to the end, wrap round. Two runs tie? Compare the digits right after them. No 0? Use the smallest digit.</li></ol>
<p>Worked (slide 12 / SP24): CC = <b>{J(cc)}</b></p>
<p>CFD: 0→0 = 0 steps, 0→7 = 7 steps, 7→7 = 0, 7→5 = 6, … last 2→0 = 6. CFD = <b>{''.join(map(str, cfd))}</b></p>
<p>0s at places 1, 3, 7, 11, 12. Longest run = places 11–12 (two 0s). Start there: 0 0 7 1 6 | 0 7 0 6 1 7 0 7 7 7 → NCFD = <b>{''.join(map(str, ncfd))}</b></p>
{tbl(["what", "invariant to"], [["CC", "translation"], ["smallest shift of CC", "+ start point"], ["CFD", "+ rotation (45° steps)"], ["NCFD = shape number", "start point + rotation"]])}
"""))

S.append(S2("f-mor", "Formulas 7 · morphology and hit-or-miss", "decks 11–12", f"""
{tbl(["operation", "equation", "plain rule", "effect"], [
    ["erosion", "A ⊖ B = {z | (B)<sub>z</sub> ⊆ A}", "SE must <b>fit</b> (all 1s on object)", "shrink, delete specks, split joins"],
    ["dilation", "A ⊕ B = {z | (B̂)<sub>z</sub> ∩ A ≠ ∅}", "SE must <b>hit</b> (any 1 on object)", "grow, fill holes, join gaps"],
    ["opening", "A ∘ B = (A ⊖ B) ⊕ B", "erode, then dilate", "remove small objects and thin bridges, size kept"],
    ["closing", "A • B = (A ⊕ B) ⊖ B", "dilate, then erode", "fill small holes and gaps, size kept"],
    ["boundary", "β(A) = A − (A ⊖ B)", "object minus its eroded self", "1-pixel inner outline"],
    ["hit-or-miss", "A ⊛ B = (A ⊖ B₁) ∩ (Aᶜ ⊖ B₂)", "1s match object AND 0s match background; × ignored", "corners, end points, patterns"],
    ["thinning / thickening", "A − (A ⊛ B) / A ∪ (A ⊛ B)", "subtract / add the matches", "skeleton / grow outline"]])}
<p>1-D worked, row {J(row)}, SE [1 1 1] (ends ignored):</p>
<p>Erosion takes the <b>minimum</b> under the SE: windows 100, 000, 001, 011, 111, 110, 101, 011 → <b>{J(ero)}</b>.</p>
<p>Dilation takes the <b>maximum</b>: → <b>{J(dil)}</b> (only the 000 window stays 0).</p>
<p><b>Memory hook:</b> Erosion <b>E</b>ats, Dilation <b>D</b>eposits. Opening = <b>E</b> then <b>D</b> (opens gaps between things, removes specks). Closing = <b>D</b> then <b>E</b> (closes holes).</p>
{trap("Show the middle image (A ⊖ B or A ⊕ B) in every opening / closing answer. For hit-or-miss draw each SE with 1 / 0 / ×, one output grid per SE, then the OR.")}
"""))

S.append(S2("f-cmp", "Formulas 8 · compression", "deck 13 · biggest marks block", f"""
{tbl(["what", "formula", "worked line"], [
    ["compression ratio", "C<sub>R</sub> = n₁ / n₂ (original / compressed)", "512×512×8 = 2,097,152 bits; 64 KB = 524,288 bits → C<sub>R</sub> = 4"],
    ["relative redundancy", "R<sub>D</sub> = 1 − 1/C<sub>R</sub>", "1 − 1/4 = 0.75 → 75% redundant"],
    ["average length", "L<sub>avg</sub> = Σ l(r<sub>k</sub>) p(r<sub>k</sub>)", f"Huffman below: {Lavg:g} bits/symbol"],
    ["entropy", "H = −Σ p log₂ p", f"0.4·1.322 + 0.3·1.737 + 0.2·2.322 + 0.1·3.322 = <b>{H:.4f}</b>"],
    ["efficiency", "η = H / L<sub>avg</sub>", f"{H:.4f} / {Lavg:g} = <b>{H / Lavg:.1%}</b>"],
    ["RMSE", "e<sub>rms</sub> = √[ (1/MN) Σ (f̂ − f)² ]", f"every pixel +2: √(36/9) = <b>{rmse:g}</b>"],
    ["SNR (ms)", "Σ f̂² / Σ (f̂ − f)²", f"{sd} / {se} = <b>{sd / se:.3f}</b>"]])}
<h3>Huffman (SP25: A 0.4, B 0.3, C 0.2, D 0.1)</h3>
<p><b>Reduce:</b> sort, merge the two smallest: C + D = 0.3 → list 0.4, 0.3, 0.3 (the sum goes below the equal value) → merge 0.3 + 0.3 = 0.6 → list 0.6, 0.4.</p>
<p><b>Code back:</b> upper branch 0, lower 1: 0.6 = 0, 0.4 = 1 → A = 1; B = 00, (CD) = 01 → C = 010, D = 011.</p>
<p>L<sub>avg</sub> = 0.4·1 + 0.3·2 + 0.2·3 + 0.1·3 = <b>{Lavg:g}</b> ≥ H = {H:.4f}. Fixed 2-bit code → C<sub>R</sub> = 2 / {Lavg:g} = {2 / Lavg:.3f}.</p>
<h3>Golomb G<sub>m</sub>(n)</h3>
{formula("q = ⌊n/m⌋ → q ones + 0 &nbsp;|&nbsp; r = n mod m, k = ⌈log₂m⌉, c = 2<sup>k</sup> − m: r &lt; c → r in k−1 bits, else r + c in k bits")}
<p>G₄(9): q = 2 → 110; r = 1, k = 2, c = 0 → r ≥ c → 1 + 0 = 1 in 2 bits = 01 → <b>{g49[0]}</b>.</p>
<p>G₅(12): q = 2 → 110; r = 2, k = 3, c = 3 → r &lt; c → 2 in 2 bits = 10 → <b>{g512[0]}</b>.</p>
<h3>Arithmetic (slide 53: a1 0.2, a2 0.2, a3 0.4, a4 0.2; message a1 a2 a3 a3 a4)</h3>
{formula("new low = low + range × (slice start) &nbsp;&nbsp; new high = low + range × (slice end)")}
{tbl(["symbol", "range before", "low", "high"], ari_rows, "narrow")}
<p>Any number in [0.06752, 0.0688) codes the message: the slide picks <b>0.068</b>.</p>
<h3>LZW (slide 77: 4×4 image, every row 39 39 126 126)</h3>
<p>Dictionary starts with 0–255. Read a pixel: if (current + pixel) is in the dictionary, keep extending; if not, output the code of current, add (current + pixel) at the next location (256, 257, …), restart from the pixel.</p>
{tbl(["recognized", "pixel", "output", "location", "entry"], lz_rows[:8], "narrow")}
<p>Full output: {J(lz_out)} → 10 codes × 9 bits = 90 bits vs 128 → C<sub>R</sub> = 1.42.</p>
<p><b>RLE:</b> write (value, run length). Row 10 10 10 10 12 12 → (10, 4)(12, 2). Short runs make the file bigger (C<sub>R</sub> &lt; 1): say so.</p>
<h3>Which redundancy each method removes</h3>
{tbl(["redundancy", "what it is", "removed by"], [
    ["coding", "codes longer than needed", "Huffman, Golomb, arithmetic"],
    ["spatial / inter-pixel", "neighbours repeat or predict each other", "LZW, RLE, predictive coding"],
    ["irrelevant (psychovisual)", "detail the eye ignores", "quantization (lossy)"],
    ["temporal", "frames in a video repeat", "frame differencing"]])}
"""))

S.append(S2("f-col", "Formulas 9 · colour", "deck 14", f"""
{tbl(["what", "formula / fact"], [
    ["RGB → CMY", "C = 1 − R, M = 1 − G, Y = 1 − B (normalise to 0–1 first)"],
    ["θ", "cos⁻¹ { ½[(R − G) + (R − B)] / √[(R − G)² + (R − B)(G − B)] }"],
    ["H", "θ if B ≤ G, else 360° − θ (red 0°, green 120°, blue 240°)"],
    ["S", "1 − 3·min(R, G, B) / (R + G + B)"],
    ["I", "(R + G + B) / 3"],
    ["24-bit colours", "2²⁴ = 16,777,216"]])}
<p>Worked (R, G, B) = (0.8, 0.4, 0.2): numerator ½(0.4 + 0.6) = 0.5; denominator √(0.16 + 0.6 × 0.2) = √0.28 = 0.5292; θ = cos⁻¹(0.9449) = {theta:.1f}°. B ≤ G, so <b>H = {Hh:.1f}°</b>. <b>S</b> = 1 − 3 × 0.2 / 1.4 = <b>{Sat:.4f}</b>. <b>I</b> = 1.4 / 3 = <b>{Ii:.4f}</b>.</p>
<ul><li><b>Additive</b> (light, RGB): R + G + B = white. <b>Subtractive</b> (pigment, CMY): C + M + Y = black (K added because CMY black is muddy).</li>
<li>RGB cube: black at the origin, white at the far corner, grays on the diagonal R = G = B.</li>
<li>HSI separates colour (H, S) from brightness (I): good for segmentation and for enhancing I without changing hues.</li></ul>
"""))

S.append(S2("q1", "Q1 theory: question → what to write", "5 marks each · any 5 of 6", f"""
{idea("Each Q1 answer is a definition, a formula or sketch, and three short points. Below are the questions she repeats, with the points to write.")}
{tbl(["if asked", "write"], [
    ["sampling vs quantization; why more levels look finer", "coordinates vs amplitude; few pixels → blocky, few levels → false contours; bits = M·N·k"],
    ["4-, 8-, m-connectivity; distance properties", "the three adjacency rules; m removes double paths; D ≥ 0, symmetric, triangle inequality"],
    ["image enhancement; spatial vs frequency domain", "make an image more useful for a task; spatial works on pixels directly (point, neighbourhood), frequency on the Fourier transform"],
    ["piecewise linear: identity, threshold, stretch", "the 3-piece formula with (r₁,s₁),(r₂,s₂) and the 3 settings, each with a graph"],
    ["histogram; 4 types; can you rebuild the image?", "h(r<sub>k</sub>) = n<sub>k</sub>; dark / bright / low / high contrast sketches; no, it holds no positions"],
    ["why is the equalized histogram not flat?", "discrete levels: several r map to one s, some s stay empty"],
    ["smoothing vs sharpening", "averaging (integration) blurs, removes noise; derivatives (differentiation) bring out edges"],
    ["1st vs 2nd derivative", "thick vs thin double edge; ramp non-zero vs zero; 2nd strong on points, noise-sensitive"],
    ["edge detection steps; Canny", "smooth → gradient → threshold; Canny's 3 criteria and 5 steps"],
    ["segmentation approaches", "discontinuity (points, lines, edges) and similarity (threshold, region growing, split &amp; merge)"],
    ["structuring element; erosion vs dilation", "small shape with an origin; fit vs hit; shrink vs grow; one application each"],
    ["opening vs closing", "equations, order of operations, specks vs holes, idempotent"],
    ["chain code; why CFD and NCFD", "boundary as direction numbers; CFD removes rotation, smallest shift removes start point"],
    ["data vs information; three redundancies", "data = what is stored, information = what it tells; coding, spatial, irrelevant (+ temporal)"],
    ["lossless vs lossy", "exact rebuild (Huffman, LZW, RLE) vs some loss for higher C<sub>R</sub> (quantization); judge lossy with RMSE"],
    ["why is Huffman optimal / entropy", "shortest codes for most likely symbols, prefix-free; H is the lower bound on L<sub>avg</sub>"],
    ["additive vs subtractive; which model for printing, display, segmentation", "light vs pigment; CMYK, RGB, HSI"],
    ["RGB cube; how gray is formed", "axes R, G, B 0–1; black origin, white (1,1,1); gray on the diagonal"]])}
"""))

S.append(S2("traps", "Last-hour traps", "read this on the bus", """
<ul class="traps">
<li>Find L from the bits first: 3-bit → 0…7. Using 255 on a 3-bit image ruins every number after it.</li>
<li>Round .5 up (3.5 → 4). HE: s = round(7 × CDF), not floor.</li>
<li>Median: sort all nine values, take the 5th. Zero padding at corners means five 0s.</li>
<li>Laplacian sign: centre negative → g = f − ∇²f; centre positive → g = f + ∇²f.</li>
<li>Gradient: |Gx| + |Gy|, take absolute values before adding.</li>
<li>Erosion = fit, dilation = hit. Opening = erode first. Closing = dilate first.</li>
<li>Non-symmetric SE: dilation uses the reflected SE B̂. Mark the origin.</li>
<li>Chain code: walk the direction the question says. The CFD's last digit wraps to the first code.</li>
<li>C<sub>R</sub> = original / compressed. 1 KB = 1024 bytes = 8192 bits.</li>
<li>Huffman: sum goes below an equal value; upper 0, lower 1; show the full reduction table.</li>
<li>LZW: output the last recognized sequence at the end; count codes × 9 bits.</li>
<li>Golomb: unary = q ones then a 0.</li>
<li>HSI: normalise to 0–1 first; H = 360° − θ when B &gt; G.</li>
<li>Q3: name the method in bold in the first line; give one limitation.</li>
</ul>
"""))

S.append(S2("links", "Practise each method step by step", "deck pages with simulators", """
<p>Every formula above has a full lesson page with past questions solved and a step-by-step simulator:</p>
<ul class="links">
<li><a href="https://claude.ai/artifact/6JjedKPgBz7cwxVaQrzobW">Decks 01–02 · fundamentals</a> · <a href="https://claude.ai/artifact/U5XjXXih4nAAcmAaKeVwx8">03 · pixels</a> · <a href="https://claude.ai/artifact/2qjwACXWKTzu8p5Aayccr5">04 · intensity</a> · <a href="https://claude.ai/artifact/Qt4kTFXCiVGnU2vgy6Y9NK">05 · histogram</a></li>
<li><a href="https://claude.ai/artifact/E4eeC6pkMmhGX66dheSjMj">06 · smoothing</a> · <a href="https://claude.ai/artifact/K14i96mZprNmn92k8y7YtF">07 · sharpening</a> · <a href="https://claude.ai/artifact/BoW6fySYaxW8oKx7Abem1U">08 · edges</a> · <a href="https://claude.ai/artifact/TiabWz7aSGKZZ2RdgbusT4">09 · regions</a></li>
<li><a href="https://claude.ai/artifact/64f8ExYNkonuEM17no7D6o">10 · chain code</a> · <a href="https://claude.ai/artifact/PnjH4weLv1WAgnFRmdLHre">11 · morphology I</a> · <a href="https://claude.ai/artifact/N1ZWaqJAJ2MZaW7DqRLZdZ">12 · hit-or-miss</a> · <a href="https://claude.ai/artifact/G4ZKL2xjzZJazc12gdypDP">13 · compression</a> · <a href="https://claude.ai/artifact/7hVft4bZ8ZytybJ4hR9bZ8">14 · colour</a></li>
<li>Trainers: <a href="https://claude.ai/artifact/Qw67rrRo2rNngbz9G4x552">chain code</a> · <a href="https://claude.ai/artifact/KAWJzbW2T9dUJ6bfjc9w28">LZW</a></li>
</ul>
"""))

EXTRA = """<style>
.road{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr));gap:10px;margin:14px 0;counter-reset:none}
.stop{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:10px 14px;min-width:0}
.stop b{font-family:var(--f-display);font-size:17px;display:block}
.stop span{font-family:var(--f-mono);font-size:12px;color:var(--fg2)}
.stop p{margin:4px 0 0;font-size:14.5px}
table.cue td:first-child{width:38%} table.cue td:last-child{color:var(--fg)} table.cue td:nth-child(2){color:var(--fg2);font-size:14px}
table.cue b{color:var(--ink)}
ul.links li{margin:8px 0}
</style>"""

toc = [("paper", "Paper"), ("map", "Big picture"), ("cues", "Cue words"), ("q3", "Q3 cases"), ("f-ch2", "Pixels"), ("f-ch3", "Point ops"),
       ("f-he", "Histogram"), ("f-filt", "Filters"), ("f-seg", "Edges & segments"), ("f-cc", "Chain code"), ("f-mor", "Morphology"),
       ("f-cmp", "Compression"), ("f-col", "Colour"), ("q1", "Q1 theory"), ("traps", "Traps"), ("links", "Decks")]
OUT.write_text(page("DIP Final Mega Sheet", "CSE 4227 · Prof. Kalpoma · AUST", "DIP on one page",
                    "What each question type wants, which method each story word points to, every formula with a worked line, and the theory points to write. Fall 2024 papers are left out.",
                    toc, S, extra=EXTRA), encoding="utf-8")
print(OUT, OUT.stat().st_size)
