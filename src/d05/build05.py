"""Builds deck05_lesson.html: histogram processing lesson. All numbers computed here."""
import sys, pathlib
from fractions import Fraction as F
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from kit import *

OUT = pathlib.Path(__file__).with_name("deck05_lesson.html")
rf = lambda x: math.floor(x + F(1, 2))  # exact round-half-up


def hist(img, L):
    h = [0] * L
    for r in img:
        for v in r:
            h[v] += 1
    return h


# ---------------------------------------------------------------- equalization engine
def eq(n, dp=4):
    """n: counts per level. dp=2 copies the slide-49 habit (PDF rounded to 2 places first)."""
    L, N = len(n), sum(n)
    pdf = [F(v, N) for v in n]
    if dp == 2:
        pdf = [F(round(float(p) * 100), 100) for p in pdf]
    cdf, acc = [], F(0)
    for p in pdf:
        acc += p
        cdf.append(acc)
    if dp == 2:
        cdf[-1] = F(1)
    scaled = [(L - 1) * c for c in cdf]
    s = [rf(x) for x in scaled]
    return pdf, cdf, scaled, s


def eqhist(n, s):
    out = [0] * len(n)
    for r, v in enumerate(n):
        out[s[r]] += v
    return out


def f4(x, dp=4):
    return f"{float(x):.{dp}f}"


def he_answer(n, img=None, dp=4, bits=None, show_all_levels=True):
    L, N = len(n), sum(n)
    pdf, cdf, sc, s = eq(n, dp)
    nz = [r for r in range(L) if n[r]]
    o = []
    o.append(f"<p><b>Given:</b> {bits or int(math.log2(L))}-bit image, so L = 2<sup>{int(math.log2(L))}</sup> = {L} and L − 1 = {L - 1}. Total pixels N = {N}.</p>")
    if img:
        o.append(mat(img, "input image"))
    # step 1
    o.append("<p><b>Step 1, histogram</b> h(r<sub>k</sub>) = n<sub>k</sub>: count the pixels at each gray level.</p>")
    lv = range(L) if show_all_levels else nz
    o.append(tbl(["r<sub>k</sub>"] + [str(r) for r in lv], [["n<sub>k</sub>"] + [n[r] for r in lv]], "narrow"))
    o.append(f"<p>Check: Σ n<sub>k</sub> = {' + '.join(str(n[r]) for r in nz)} = {N}.</p>")
    o.append(figs(bars(n, caption="Original histogram (n<sub>k</sub> against r<sub>k</sub>)", xlabel="r<sub>k</sub>"),
                  bars([float(p) for p in pdf], caption="Normalized histogram p(r<sub>k</sub>) = n<sub>k</sub>/N", ylabel="p(r<sub>k</sub>)", xlabel="r<sub>k</sub>", fmt=lambda v: f"{v:.2f}", cls="c2")))
    # steps 2-5
    o.append(f"<p><b>Steps 2–5.</b> PDF p(r<sub>k</sub>) = n<sub>k</sub>/N; CDF = running sum of the PDF; multiply by (L − 1) = {L - 1}; round off (.5 goes up). "
             + ("Only the intensities with non-zero occurrence are listed, as the slide says." if len(nz) < L else "") + "</p>")
    rows = [[r, n[r], f4(pdf[r], dp), f4(cdf[r], dp), f"{L - 1} × {f4(cdf[r], dp)} = {f4(sc[r], dp if dp == 2 else 4)}", f"<b>{s[r]}</b>"] for r in nz]
    o.append(tbl(["r<sub>k</sub>", "Step 1: n<sub>k</sub>", "Step 2: PDF", "Step 3: CDF", f"Step 4: (L−1)·CDF", "Step 5: s<sub>k</sub>"], rows, "narrow"))
    # mapping
    o.append("<p><b>Mapping the new gray levels into number of pixels:</b></p>")
    o.append(tbl(["gray level r<sub>k</sub>", "new gray level s<sub>k</sub>", "no. of pixels n<sub>k</sub>"], [[r, s[r], n[r]] for r in nz], "narrow"))
    eh = eqhist(n, s)
    used = [v for v in range(L) if eh[v]]
    adds = []
    for v in used:
        src = [str(n[r]) for r in nz if s[r] == v]
        adds.append([v, " + ".join(src) + (f" = {eh[v]}" if len(src) > 1 else ""), eh[v]])
    o.append("<p><b>Equalized histogram:</b> add the n<sub>k</sub> that land on the same s<sub>k</sub>. Levels not listed get 0 pixels.</p>")
    o.append(tbl(["s<sub>k</sub>", "pixels added", "n(s<sub>k</sub>)"], adds, "narrow"))
    o.append(figs(bars(eh, caption="Equalized histogram (n against new level s<sub>k</sub>)", xlabel="s<sub>k</sub>", cls="c3"),
                  stairs(s, caption="Transformation function s<sub>k</sub> = T(r<sub>k</sub>) drawn as a staircase (slide 40 style). Empty levels keep the previous step.")))
    if img:
        out = [[s[v] for v in r] for r in img]
        o.append("<p><b>Equalized output image:</b> replace every pixel r by its s.</p>")
        o.append(mats(mat(img, "input"), mat(out, "equalized output")))
    return "".join(o), s, eh


def hs_answer(n, pz, dp=2, spec_counts=None):
    L = len(n)
    _, _, scH, H = eq(n, dp)
    pdfH = eq(n, dp)[0]; cdfH = eq(n, dp)[1]
    if spec_counts:
        pz = [F(v, sum(spec_counts)) for v in spec_counts]
        if dp == 2:
            pz = [F(round(float(p) * 100), 100) for p in pz]
    else:
        pz = [F(str(p)) for p in pz]
    cz, acc = [], F(0)
    for p in pz:
        acc += p
        cz.append(acc)
    cz[-1] = F(1)
    scS = [(L - 1) * c for c in cz]
    S = [rf(x) for x in scS]
    # map each H to the z whose S is closest; tie -> higher S (slide 55); equal S -> smallest z
    def best(h):
        d = min(abs(x - h) for x in S)
        cand = sorted({x for x in S if abs(x - h) == d})
        sv = cand[-1]
        return S.index(sv)
    zmap = [best(h) for h in H]
    outn = [0] * L
    for r in range(L):
        outn[zmap[r]] += n[r]
    o = []
    o.append("<p><b>Step 1, equalize the original histogram</b> to get H<sub>k</sub>.</p>")
    o.append(tbl(["r<sub>k</sub>", "n<sub>k</sub>", "PDF", "CDF", f"(L−1)·CDF", "H<sub>k</sub>"],
                 [[r, n[r], f4(pdfH[r], dp), f4(cdfH[r], dp), f4(scH[r], 2), f"<b>{H[r]}</b>"] for r in range(L)], "narrow"))
    o.append("<p><b>Step 2, equalize the specified histogram</b> to get S<sub>k</sub>.</p>")
    o.append(tbl(["z<sub>q</sub>"] + (["specified n"] if spec_counts else []) + ["p<sub>z</sub>(z<sub>q</sub>)", "CDF", f"(L−1)·CDF", "S<sub>k</sub>"],
                 [[z] + ([spec_counts[z]] if spec_counts else []) + [f4(pz[z], 2), f4(cz[z], 2), f4(scS[z], 2), f"<b>{S[z]}</b>"] for z in range(L)], "narrow"))
    o.append("<p><b>Step 3, relate the two.</b> For each r<sub>k</sub>, take its H<sub>k</sub>, find the S value closest to it, and map r<sub>k</sub> to that z. "
             "If two S values are equally close, take the higher one (slide 55). If several z share that S value, take the first such z.</p>")
    o.append(tbl(["r<sub>k</sub>", "H<sub>k</sub>", "closest S", "map to z"], [[r, H[r], S[zmap[r]], f"<b>{zmap[r]}</b>"] for r in range(L)], "narrow"))
    adds = []
    for z in range(L):
        src = [str(n[r]) for r in range(L) if zmap[r] == z]
        adds.append([z, (" + ".join(src) + (f" = {outn[z]}" if len(src) > 1 else "")) if src else "–", outn[z]])
    o.append("<p><b>Output histogram:</b> add the pixels that land on each z.</p>")
    o.append(tbl(["z", "pixels added", "n(z)"], adds, "narrow"))
    o.append(figs(bars(n, caption="Original histogram", xlabel="r<sub>k</sub>"),
                  bars(outn, caption="Output (specified) histogram", xlabel="z<sub>q</sub>", cls="c3"),
                  stairs(zmap, caption="Transformation function r<sub>k</sub> → z<sub>q</sub>", ylabel="output z<sub>q</sub>")))
    return "".join(o), H, S, zmap, outn


S_ = []

# ================================================================ start
S_.append(sec("start", "Start here: what a histogram is", "1–5", EXAM, f"""
{idea("A histogram is a <b>head count</b> of an image. For each gray level, count how many pixels have it, then draw one bar per level. Tall bar = many pixels at that brightness. That's all a histogram is.")}
<p><b>Slide 3.</b> Image A looks foggy and gray; image B looks sharp and punchy. They show the same pollen. The difference is in how the gray levels are used, and the histogram shows that difference at a glance.</p>
<p><b>Slide 4. Definition.</b> An image histogram is a <b>graphical representation of the distribution of pixel intensity values</b> in a digital image.</p>
<p><b>Applications:</b> image enhancement, compression, segmentation. Very popular tool for real-time image processing.</p>
<p><b>Slide 5. The histogram function.</b> For gray levels in [0, L−1], the histogram is the discrete function</p>
{formula("h(r<sub>k</sub>) = n<sub>k</sub>")}
<p>where r<sub>k</sub> is the k-th gray level and n<sub>k</sub> is the number of pixels with gray level r<sub>k</sub>.</p>
"""))

# ================================================================ generate
img7 = [[5, 5, 3, 3], [4, 3, 3, 3], [0, 6, 7, 2], [1, 7, 2, 2]]
h7 = hist(img7, 8)
img8 = [[20, 21, 15, 60], [60, 15, 60, 15], [15, 60, 21, 15], [15, 20, 15, 20]]
from collections import Counter
c8 = Counter(v for r in img8 for v in r)
four = {
    "dark": [9, 14, 10, 6, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "bright": [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 6, 10, 14, 9, 4],
    "low contrast": [0, 0, 0, 0, 0, 2, 9, 15, 12, 4, 0, 0, 0, 0, 0, 0],
    "high contrast": [4, 5, 3, 6, 4, 5, 6, 4, 5, 3, 6, 5, 4, 6, 3, 4]}
fourfigs = figs(*[bars(v, labels=[""] * 16, caption=f"<b>{k}</b>", xlabel="dark → bright", ylabel="n", w=230, h=150, fmt=lambda x: "") for k, v in four.items()])
S_.append(sec("gen", "How to make a histogram, and what it tells you", "6–17", EXAM, f"""
{paper("Slides 6–7 · 3-bit 4×4 example", "worked", f'''
<p><b>Given:</b> 3-bit image, so L = 2<sup>3</sup> = 8 levels (0–7). One bin per level: h(0) … h(7).</p>
{mat(img7, "image f")}
<p><b>Count</b> each value: 0 appears once, 1 once, 2 three times, 3 five times, 4 once, 5 twice, 6 once, 7 twice.</p>
{tbl(["r<sub>k</sub>"] + list(range(8)), [["h(r<sub>k</sub>)"] + h7], "narrow")}
{bars(h7, caption="Histogram: one bar per gray level", xlabel="intensity level")}
<p>Sum of all bars = 16 = number of pixels. The slide writes this as Σ h(x) = area of the image.</p>
''')}
{sim({"type": "he", "img": img7, "L": 8, "phases": ["count"]}, "count each gray level of the slide 7 image and watch its bar grow.")}
{paper("Slide 8 · Class practice", "solved", f'''
<p class="q">sample.bmp is a 4×4 image with 6-bit gray values. Calculate its histogram and sketch it.</p>
{mat(img8, "sample.bmp (6-bit, levels 0–63)")}
<p>n = 16 pixels. Only four values occur:</p>
{tbl(["r<sub>k</sub>", "15", "20", "21", "60", "all other levels"], [["h(r<sub>k</sub>)", c8[15], c8[20], c8[21], c8[60], 0]], "narrow")}
{bars([c8[15], c8[20], c8[21], c8[60]], labels=[15, 20, 21, 60], caption="Sketch: bars at 15, 20, 21, 60; every other level 0 to 63 has height 0.", xlabel="input intensity")}
''')}
{sim({"type": "he", "img": img8, "L": 64, "phases": ["count"]}, "the 6-bit sample.bmp: only 4 levels occur, all other bins stay 0.")}
<p><b>Slide 9. What a histogram says.</b> In the example h(2) = 10: ten pixels have intensity 2. A histogram gives <b>only statistical information</b>. It gives <b>no indication of the location</b> of the pixels.</p>
<p><b>Slides 10–13. Can two images have the same histogram? Can you rebuild an image from its histogram?</b></p>
<ul><li>Two 20×20 images, one half-white/half-black, one a checkerboard: both have 400 pixels, 200 white and 200 black, so <b>their histograms are identical</b>.</li>
<li>Different images can have the <b>same</b> histogram (slide 12: half-gray block, gray circle, gray checkerboard). Same histogram means same statistics, but the arrangement can differ.</li>
<li>So <b>you cannot reconstruct an image from its histogram</b>. It doesn't say where the pixels are.</li></ul>
<p><b>Slide 14. Colour image histogram</b>, two types: (1) <b>intensity histogram</b>: convert the colour image to gray scale and show that histogram; (2) <b>individual colour channel histograms</b>: 3 histograms, one each for R, G, B.</p>
<h3>Slide 15. Four basic types of image and their histograms</h3>
{fourfigs}
<ul>
<li><b>Dark image:</b> bars crowded on the <b>left</b> (low gray levels).</li>
<li><b>Bright image:</b> bars crowded on the <b>right</b> (high gray levels).</li>
<li><b>Low-contrast image:</b> a <b>narrow</b> group of bars, usually near the middle. Few gray levels are used, so it looks dull and washed out.</li>
<li><b>High-contrast image:</b> bars <b>spread over the whole range</b>, fairly evenly. Many gray levels are used, so it shows lots of detail.</li>
</ul>
<p><b>Slide 16. Why the histogram is important.</b> Its shape gives key information on the <b>overall quality of the image</b> and the <b>possibility for enhancement</b>. Looking at it is a fast way to judge quality. Processing the histogram improves an image quickly and automatically.</p>
<p><b>Slide 17. Uses of the histogram:</b></p>
<ul><li>tells whether the image was <b>scanned properly</b> or not;</li><li>gives an idea of the <b>tonal distribution</b>;</li>
<li>histogram processing (equalization) can <b>improve the appearance</b>;</li><li>tells us about <b>objects</b> in the image;</li>
<li>objects have similar gray levels, so it helps <b>select a threshold value for object detection</b>;</li><li>it can be used for <b>image segmentation</b>.</li></ul>
"""))

# ================================================================ normalized
img19 = [[9, 8, 9, 8], [2, 7, 4, 7], [6, 4, 6, 1], [4, 0, 7, 4]]
h19 = hist(img19, 10)
img20 = [[20, 210, 150, 60], [60, 150, 60, 150], [150, 60, 210, 150], [150, 20, 150, 20]]
c20 = Counter(v for r in img20 for v in r)
S_.append(sec("norm", "Normalized histogram (PDF)", "18–20", LIKELY, f"""
{idea("A count like '4 pixels' means little unless you know the image size. Divide every count by the total number of pixels and you get a fraction: 'one quarter of the image has level 4'. Those fractions are the normalized histogram. They always add up to 1.")}
{formula("p(r<sub>k</sub>) = n<sub>k</sub> / n, &nbsp; where n = Σ n<sub>k</sub>")}
<ul><li>p(r<sub>k</sub>) estimates the <b>probability of occurrence</b> of gray level r<sub>k</sub>.</li><li>The <b>sum of all components</b> of a normalized histogram <b>equals 1</b>.</li></ul>
{paper("Slide 19 · worked", "worked", f'''
{mat(img19, "image (cropped), n = 16")}
{tbl(["bin"] + list(range(10)), [["h(r<sub>k</sub>)"] + h19, ["p(r<sub>k</sub>)"] + [f"{v}/16" if v else "0" for v in h19]], "narrow")}
{bars([v / 16 for v in h19], caption="Normalized histogram; bars add to 1", ylabel="p(r<sub>k</sub>)", fmt=lambda v: f"{v:.3g}", cls="c2")}
''')}
{sim({"type": "he", "img": img19, "L": 10, "phases": ["count", "pdf"]}, "count, then divide each count by N = 16.")}
{paper("Slide 20 · Class work", "solved", f'''
<p class="q">sample.bmp is a 4×4 image with 8-bit gray values. Calculate its normalized histogram (PDF).</p>
{mat(img20, "sample.bmp (8-bit)")}
<p>n = 16. Counts: 20 → {c20[20]}, 60 → {c20[60]}, 150 → {c20[150]}, 210 → {c20[210]}; all other levels 0.</p>
{tbl(["r<sub>k</sub>", "n<sub>k</sub>", "p(r<sub>k</sub>) = n<sub>k</sub>/16"], [[k, c20[k], f"{c20[k]}/16 = {c20[k] / 16:.4f}"] for k in (20, 60, 150, 210)] + [["sum", 16, "1.0000"]], "narrow")}
{bars([c20[k] / 16 for k in (20, 60, 150, 210)], labels=[20, 60, 150, 210], caption="PDF of sample.bmp", ylabel="p(r<sub>k</sub>)", fmt=lambda v: f"{v:.4g}", cls="c2")}
''')}
"""))

# ================================================================ sliding / stretching
toy = [6, 9, 4, 1, 0, 0, 0, 0]
slid = [0, 0, 0] + toy[:5]
toy2 = [0, 0, 5, 9, 6, 0, 0, 0]
st2 = [0] * 8
for r, v in enumerate(toy2):
    if v:
        st2[rf(F(7 * (r - 2), 2))] += v
S_.append(sec("slide", "Histogram sliding and stretching", "21–27", SHORT, f"""
<p><b>Slide 21.</b> Histogram processing is an enhancement technique: a transformation T is applied to the input f(x, y) to give the output g(x, y) = T(f(x, y)). T can be <b>(i) histogram sliding, (ii) histogram stretching, (iii) histogram equalization</b>.</p>
<p><b>Slide 22. Sliding:</b> the whole histogram is simply shifted right or left, so you see a clear change in the <b>brightness</b> of the image. Shift right = brighter, shift left = darker.</p>
{figs(bars(toy, caption="Before: 3-bit dark image"), bars(slid, caption="After adding 3 to every pixel: same shape, moved right, brighter", cls="c3"))}
<p><b>Slides 23–24. Stretching</b> increases the <b>contrast</b> (contrast = max − min pixel value). The histogram is pulled out to fill the whole range:</p>
{formula("g = 255 (f − MIN) / (MAX − MIN)")}
<p>Three steps hidden in the formula: (1) <b>slide</b> the histogram down to 0 (f − MIN); (2) <b>normalize</b> it to [0, 1] (÷ (MAX − MIN)); (3) <b>rescale</b> to [0, 255] (× 255).</p>
{paper("Mini illustration (3-bit, so 7 replaces 255)", "worked", f'''
<p>Levels used: 2 to 4. g = 7(f − 2)/(4 − 2): 2 → 0, 3 → 3.5 → 4, 4 → 7.</p>
{figs(bars(toy2, caption="Before: narrow, low contrast"), bars(st2, caption="After stretching: spread over 0–7, but the same 3 bars with gaps between", cls="c3"))}
''')}
<p><b>Slides 25–26.</b> Examples: a gray, low-contrast face becomes clearer. Stretching works better if extreme intensities are <b>clipped</b> first (city photo).</p>
<p><b>Slide 27. Limitation of stretching:</b></p>
<ul><li>Linear stretching is good but not perfect, since the <b>shape of the histogram remains the same</b> (see the gaps above).</li>
<li>Most of the time we need a <b>flat</b> histogram; stretching can't achieve that. So <b>histogram equalization</b> came into use.</li>
<li>A perfect image is one where all gray levels have an equal number of pixels. The objective is to spread the dynamic range <b>and</b> have equal pixels at all gray levels.</li></ul>
"""))

# ================================================================ HE theory
img36 = [[1, 4, 0, 4, 2], [2, 1, 3, 1, 4], [6, 2, 1, 7, 5], [7, 1, 5, 1, 3]]
he36, s36, eh36 = he_answer(hist(img36, 8))
# second pass demo
_, _, _, s2nd = eq(eh36)
S_.append(sec("he", "Histogram equalization: the idea and the algorithm", "28–35", EXAM, f"""
{idea("Equalization tries to give every gray level roughly the same number of pixels, so the histogram becomes flat. Crowded levels get pulled apart and spread over the whole range 0 to L−1. You don't choose any setting; the image's own counts decide the mapping. That's why it's called automatic.")}
<p><b>Slide 28.</b> Equalization stretches the histogram to fill the dynamic range <b>and at the same time tries to keep the histogram uniform</b>. Linear stretching only stretches; the bars keep their heights.</p>
<p><b>Slides 29–30. Case A</b> (satellite image): after equalization the result looks high-contrast with a large variety of gray tones, <b>but the histogram is not perfectly flat</b>.</p>
<p><b>Slide 31.</b> Histogram equalization is used to enhance contrast. Usually it can't perfectly equalize a digital image's histogram. That's only possible with <b>continuous</b> intensity values; real intensity values are <b>discrete</b>, so perfectly flat histograms are rare in practice.</p>
<p><b>Slide 32.</b> It <b>redistributes pixel intensities</b> so they span the full range more evenly. Original: intensities clustered in a narrow range (too dark, too bright or low contrast). After: spread out, details more visible, contrast improved. It tends to enhance contrast and can be performed <b>automatically</b>.</p>
<h3>Slide 34. The algorithm (memorize these 5 steps)</h3>
<p><b>Input:</b> a discrete image f with L intensity levels.</p>
<ol>
<li><b>Step 1:</b> compute the histogram of f: h(r<sub>k</sub>) = n<sub>k</sub>.</li>
<li><b>Step 2:</b> compute the probability distribution (PDF/PMF): p(r<sub>k</sub>) = n<sub>k</sub> / N.</li>
<li><b>Step 3:</b> compute the cumulative distribution (CDF): CDF(i) = running sum of the PDF up to i.</li>
<li><b>Step 4:</b> calculate the mapping: s<sub>i</sub> = CDF(i) × (L − 1).</li>
<li><b>Step 5:</b> round s<sub>k</sub> to get the new intensity values.</li>
</ol>
<p>Why the CDF? It counts the fraction of pixels darker than or equal to r. If 35% of pixels are at or below r, r goes to 35% of the way up the gray scale. Crowded levels make the CDF jump, which pushes neighbouring levels apart.</p>
{paper("Slides 36–40 · 3-bit 4×5 example", "worked", he36)}
{sim({"type": "he", "img": img36, "L": 8}, "the whole slide 36–40 example: count, the 5 table steps per level, the equalized histogram, then the output image pixel by pixel.")}
<p><b>Slides 41–45.</b> The four basic image types (dark, bright, low-contrast, high-contrast) all look similar after equalization, with histograms spread over the full range. Each one gets its own transformation curve (Figure 3.21).</p>
"""))

# ================================================================ HE past papers
sp25 = [[0, 0, 1, 1, 2], [0, 1, 1, 2, 4], [1, 1, 2, 4, 5], [1, 3, 4, 5, 6], [3, 3, 5, 6, 7]]
a_sp25, s_sp25, eh_sp25 = he_answer(hist(sp25, 8))
q2c = [[1, 2, 4, 7, 0], [2, 1, 3, 1, 5], [5, 2, 1, 4, 1], [7, 6, 3, 1, 4]]
a_q2c, s_q2c, _ = he_answer(hist(q2c, 8))
q1d = [2, 3, 5, 6, 9, 12, 14, 13]
a_q1d, s_q1d, eh_q1d = he_answer(q1d)
f23 = [[16, 30, 10, 18], [25, 1, 0, 12], [16, 13, 9, 5], [19, 14, 28, 0]]
a_f23, s_f23, _ = he_answer(hist(f23, 32), img=f23)
sp22 = [[11, 10, 12, 7], [6, 8, 7, 7], [5, 6, 11, 11], [9, 9, 7, 7]]
a_sp22, s_sp22, _ = he_answer(hist(sp22, 32), img=sp22)
f21 = [[16, 30, 8, 10], [25, 1, 12, 0], [6, 13, 9, 5], [19, 14, 29, 4]]
a_f21, s_f21, _ = he_answer(hist(f21, 32), img=f21)
n49 = [790, 1023, 850, 656, 329, 245, 122, 81]
a_f22, s_f22, eh_f22 = he_answer(n49, dp=2)

def he_paper_intro(text):
    return f'<p class="q">{text}</p>'

S_.append(sec("hepq", "Equalization past questions, solved in full", "33–40", EXAM, f"""
<p>Every equalization question has the same skeleton: <b>histogram → PDF → CDF → (L−1)·CDF → round → mapping table → equalized histogram → staircase curve → output image</b>. Learn it once; the solutions below repeat it with different numbers.</p>
{paper("SP25 Q2(a) · SP24 Q2(a)", "8–9 marks", he_paper_intro("For the 5×5, 3-bit input image, find a transformation function that will approximately equalize its histogram. (i) Illustrate in detail (ii) give the equalized output image (iii) sketch the transformation curve (iv) draw the input and output histograms.") + he_answer(hist(sp25, 8), img=sp25)[0])}
{sim({"type": "he", "img": sp25, "L": 8}, "SP25 / SP24, every step.")}
{paper("Fall 25 Quiz (set C) Q2", "14 marks", he_paper_intro("A 4×5, 3-bit image [1,2,4,7,0; 2,1,3,1,5; 5,2,1,4,1; 7,6,3,1,4]. (i) Draw the histogram (ii) sketch the normalized histogram (iii) compute and sketch the equalized histogram (iv) sketch the transformation function curve (v) show the equalized output image.") + he_answer(hist(q2c, 8), img=q2c)[0])}
{sim({"type": "he", "img": q2c, "L": 8}, "Fall 25 quiz set C, every step.")}
{paper("Fall 25 Quiz (set D) Q2(b)", "10 marks", he_paper_intro("A 3-bit 8×8 image has histogram counts {{0:2, 1:3, 2:5, 3:6, 4:9, 5:12, 6:14, 7:13}}. (i) Sketch the normalized histogram (ii) compute and sketch the equalized histogram (iii) sketch the transformation function curve.") + a_q1d)}
{sim({"type": "he", "counts": q1d, "L": 8, "phases": ["table", "eqhist"]}, "Fall 25 quiz set D: counts are given, so it starts at the table.")}
{paper("F22 A3(b) · same counts as slide 49", "8 marks", he_paper_intro("Histogram r = 0..7, n = [790, 1023, 850, 656, 329, 245, 122, 81]. (i) normalized histogram (ii) equalized histogram (iii) mapping of new gray levels into number of pixels (iv) transformation curve.") + "<p>Here, as on slide 49, the PDF is rounded to 2 decimal places before the CDF.</p>" + a_f22)}
{sim({"type": "he", "counts": n49, "L": 8, "dp": 2, "phases": ["table", "eqhist"]}, "F22 with the PDF rounded to 2 places, as on slide 49.")}
{paper("F23 Q2(a) · Qubits.png", "6 marks", he_paper_intro("4×4, 5-bit image. (i) histogram (ii) compute and sketch the normalized histogram (iii) compute and sketch the equalized histogram (iv) sketch the transformation curve.") + a_f23)}
{sim({"type": "he", "img": f23, "L": 32}, "F23 (5-bit): only the levels that occur get a table row.")}
{paper("SP22 Q2(b)", "8 marks", he_paper_intro("4×4, 5-bit image. (i) histogram (ii) normalized histogram (iii) equalized histogram (iv) transformation curve.") + a_sp22)}
{sim({"type": "he", "img": sp22, "L": 32}, "SP22 (5-bit), every step.")}
{paper("F21 B3(a) · Enigma.png", "8 marks", he_paper_intro("(i) What is a histogram? Calculate it. (ii) normalized histogram (iii) equalized histogram (iv) transformation curve. 4×4, 5-bit image.") + "<p><b>Histogram:</b> a graphical representation of the distribution of pixel intensity values, h(r<sub>k</sub>) = n<sub>k</sub>.</p>" + a_f21)}
{sim({"type": "he", "img": f21, "L": 32}, "F21 (5-bit), every step.")}
{trap("For 5-bit images most of the 32 levels are empty. Put only the non-zero intensities in the table (the slide says so), but draw the axes from 0 to 31. Use L − 1 = 31, not 7.")}
"""))

# ================================================================ second pass + classwork
cw = [100, 90, 50, 20, 0, 0, 0, 0]
a_cw, s_cw, eh_cw = he_answer(cw)
S_.append(sec("pass2", "Homework and class work", "59–61", LIKELY, f"""
{paper("Slide 59 · Home work", "proof", f'''
<p class="q">An image is histogram-equalized. Show that a second pass of histogram equalization produces exactly the same result as the first pass.</p>
<p>After the first pass, every input level r<sub>k</sub> has been moved to s<sub>k</sub> = round((L−1)·CDF(r<sub>k</sub>)). The order of levels is kept, since the CDF never decreases.</p>
<p>In the equalized image, the number of pixels at or below level s<sub>k</sub> is exactly the number of original pixels at or below r<sub>k</sub> (for the last r<sub>k</sub> that maps to s<sub>k</sub>). So the CDF of the new image at s<sub>k</sub> equals the old CDF at r<sub>k</sub>.</p>
<p>The second pass therefore computes round((L−1)·CDF) from the same CDF values and gets the same s<sub>k</sub> again. Each level maps to itself: the second mapping is the identity, and the image does not change.</p>
<p><b>Numeric check</b> with the slide 36 result: equalized counts at s = 0, 2, 4, 5, 6, 7 are {", ".join(str(eh36[v]) for v in range(8) if eh36[v])}. A second equalization gives new levels {", ".join(f"{v}→{s2nd[v]}" for v in range(8) if eh36[v])}, every level unchanged.</p>
''')}
{paper("Slides 60–61 · Class work", "solved", "<p class=\"q\">Equalize the given histogram: r = 0..7, n = [100, 90, 50, 20, 0, 0, 0, 0].</p>" + a_cw)}
{sim({"type": "he", "counts": cw, "L": 8, "phases": ["table", "eqhist"]}, "the slide 60 class work.")}
"""))

# ================================================================ HS
a49, H49, S49, z49, o49 = hs_answer(n49, [0, 0, 0, .15, .20, .30, .20, .15])
n55 = [8, 10, 10, 2, 12, 16, 4, 2]
a55, H55, S55, z55, o55 = hs_answer(n55, None, spec_counts=[0, 0, 0, 0, 20, 20, 16, 8])
S_.append(sec("hs", "Histogram specification (matching)", "46–58", LIKELY, f"""
<p><b>Slide 46. Why another method?</b> Histogram equalization has a disadvantage: it can produce <b>only one type of output</b> image. With <b>histogram specification</b> we can specify the shape of the histogram we want the output to have. It doesn't have to be uniform. Specification is a <b>trial-and-error</b> process: there are no rules for choosing the target histogram, and each enhancement task needs case-by-case analysis.</p>
<p><b>Slide 47. Example:</b> you have a dull image and want it to look like a bright, high-contrast photo. Use the bright photo's histogram as the reference, and the result inherits its tonal style.</p>
{idea("Equalization always aims at a flat histogram. Matching aims at a histogram you pick. The trick: equalize both your image and the target. Both now sit on the same flat scale, so you can line them up and see which input level should become which target level.")}
<p><b>Slide 48. Definition:</b> generate a processed image that has a specified histogram, i.e. convert the input image so that its histogram matches one that was arbitrarily specified. The mapping is found in <b>three steps</b>:</p>
<ol><li><b>Equalize</b> the histogram of the input image, giving H<sub>k</sub>.</li><li><b>Equalize</b> the specified histogram, giving S<sub>k</sub>.</li><li><b>Relate</b> the two equalized histograms: map each r<sub>k</sub> to the z whose S is closest to its H<sub>k</sub>.</li></ol>
{paper("Slides 49–53 · 3-bit, 64×64 (MN = 4096)", "worked", "<p class=\"q\">Get the histogram transformation function and make the output image follow the specified histogram p<sub>z</sub> = [0, 0, 0, 0.15, 0.20, 0.30, 0.20, 0.15].</p>" + a49 +
       f"<p>Compare with the slide: the actual output histogram has p(z) = {', '.join(f'{v / 4096:.2f}' for v in o49)}, close to the specified one, though not exact, because levels are discrete.</p>")}
{sim({"type": "hs", "counts": n49, "spec": [0, 0, 0, 15, 20, 30, 20, 15], "dp": 2}, "all three matching steps for slide 49: equalize the input, equalize the target, then relate them level by level.")}
{paper("Slides 55–58 · second example (N = 64)", "worked", "<p class=\"q\">Original histogram n = [8, 10, 10, 2, 12, 16, 4, 2]. Desired histogram n = [0, 0, 0, 0, 20, 20, 16, 8]. Find the mapping and the output histogram.</p>" + a55)}
{sim({"type": "hs", "counts": n55, "spec": [0, 0, 0, 0, 20, 20, 16, 8], "specCounts": True, "dp": 2}, "slide 55, including the ties that go to the higher S.")}
{trap("In Step 3 you compare H with S values, then write down the z position of that S, not the S value itself. Example: on slide 49, H = 1 is closest to S = 1, which sits at z = 3, so r = 0 → 3.")}
"""))

# ================================================================ theory answers
S_.append(sec("theory", "Theory questions, answer-script form", "4–17, 31–34, 62", EXAM, f"""
{paper("F23 Q1(a)", "4 marks", f'''
<p class="q">What is the histogram of an image? Can you reconstruct the image from the histogram? How does the histogram differ for a dark, bright, low-contrast or high-contrast image? [1+1+2]</p>
<p><b>Histogram:</b> a graphical representation of the distribution of pixel intensity values in an image. For gray levels in [0, L−1] it is the discrete function h(r<sub>k</sub>) = n<sub>k</sub>, where n<sub>k</sub> is the number of pixels with gray level r<sub>k</sub>.</p>
<p><b>Reconstruction:</b> No. A histogram holds only statistical information (how many pixels have each value), not the location of the pixels. Different images can have the same histogram, e.g. a half-black/half-white image and a checkerboard with the same numbers of black and white pixels.</p>
<p><b>Four types</b> <i>[draw the four small histograms]</i>:</p>
{fourfigs}
<ul><li>Dark: components concentrated on the low (left) side of the gray scale.</li><li>Bright: concentrated on the high (right) side.</li>
<li>Low contrast: a narrow band, usually in the middle of the scale.</li><li>High contrast: spread over a broad range, fairly uniformly.</li></ul>
''')}
{paper("SP23 Q2(b) · Fall 25 Quiz (D) Q2(a)", "4–5 marks", '''
<p class="q">What is the histogram of an image? Explain the four basic intensity characteristics of an image and their corresponding histograms.</p>
<p>Write the definition and h(r<sub>k</sub>) = n<sub>k</sub> as above, then the four types with their four sketches. Add the meaning of each:</p>
<ul><li><b>Dark image</b>: most pixels have low values, so the histogram sits on the left; the image looks dark and details in shadows are hidden.</li>
<li><b>Bright image</b>: most pixels have high values, so the histogram sits on the right; the image looks washed out.</li>
<li><b>Low-contrast image</b>: pixels occupy a narrow range of gray levels, so the histogram is narrow; the image looks dull and gray.</li>
<li><b>High-contrast image</b>: pixels cover almost the whole range and the histogram is spread fairly evenly; the image shows a lot of gray-level detail.</li></ul>
''')}
{paper("F22 A2(b)", "5 marks", '''
<p class="q">What is the histogram of an image? How does the histogram differ for dark, bright, low-contrast and high-contrast images of the same scene? Write the steps of the histogram equalization algorithm. [1+2+2]</p>
<p>Definition and four types as above. <b>Algorithm</b> (input: image f with L levels):</p>
<ol><li>Compute the histogram h(r<sub>k</sub>) = n<sub>k</sub>.</li><li>Compute the PDF p(r<sub>k</sub>) = n<sub>k</sub>/N.</li><li>Compute the CDF, the cumulative sum of the PDF.</li><li>Compute s<sub>k</sub> = (L − 1) × CDF(r<sub>k</sub>).</li><li>Round s<sub>k</sub> to get the new intensity values, and replace every r<sub>k</sub> by s<sub>k</sub>.</li></ol>
''')}
{paper("Fall 25 Quiz (set D) Q1", "6 marks", f'''
<p class="q">How do you generate an image histogram? What does an image histogram say? [3+3]</p>
<p><b>Generate:</b> (1) find the number of gray levels L = 2<sup>k</sup> and make one bin per level 0 … L−1; (2) scan the image and, for each pixel with value r<sub>k</sub>, add 1 to bin h(r<sub>k</sub>); (3) plot n<sub>k</sub> against r<sub>k</sub> as bars. Σ h = total number of pixels.</p>
<p>Example (slide 7, 3-bit 4×4): h = [{", ".join(map(str, h7))}].</p>
{bars(h7, caption="h(r<sub>k</sub>) for the slide 7 image", xlabel="r<sub>k</sub>")}
<p><b>What it says:</b> how many pixels have each intensity, i.e. the tonal distribution. From its shape we can tell whether the image is dark, bright, low- or high-contrast; judge the overall quality and the possibility of enhancement; check whether the image was scanned properly; and choose a threshold for object detection and segmentation. It gives only statistical information and no indication of pixel locations.</p>
''')}
{paper("Fall 25 Quiz (set C) Q1", "6 marks", f'''
<p class="q">What is the histogram of an image? Two 20×20 images have equal numbers of black (0) and white (1) pixels. Are their histograms identical? Explain. [2+4]</p>
<p>Definition: as above, h(r<sub>k</sub>) = n<sub>k</sub>.</p>
<p>Each image has 20 × 20 = 400 pixels: 200 black and 200 white. So for both images h(0) = 200 and h(1) = 200.</p>
{bars([200, 200], labels=["0 (black)", "1 (white)"], caption="Histogram of either image: identical", xlabel="gray level", w=240)}
<p><b>Yes, the histograms are identical</b>, even if one image is half black / half white and the other is a checkerboard. A histogram records only how many pixels have each value, not where they are. So the same histogram can come from different images, and an image cannot be reconstructed from its histogram.</p>
''')}
{paper("Short note · continuous CDF (slide 62)", "theory", '''
<p>For continuous intensities the equalizing transformation is s = T(r) = (L − 1) ∫<sub>0</sub><sup>r</sup> p<sub>r</sub>(w) dw. In the discrete case it becomes s = T(r) = (L − 1) Σ p(r<sub>j</sub>) for j = 0 … k, i.e. (L − 1) times the CDF. This is why the algorithm multiplies the CDF by L − 1.</p>
''')}
"""))

S_.append(sec("traps", "Traps and one-minute sheet", "all", None, f"""
<ul class="traps">
<li>Use <b>L − 1</b>: 7 for 3-bit, 31 for 5-bit, 255 for 8-bit.</li>
<li>Round <b>.5 up</b> (3.5 → 4, 15.5 → 16), as on slide 37.</li>
<li>Always draw <b>both histograms</b> (original and equalized) and the <b>staircase</b> curve. Each is a separate mark.</li>
<li>The equalized histogram is built by <b>adding</b> the counts of levels that land on the same s. Its total must still equal N.</li>
<li>Matching, Step 3: compare H with S values, then write the <b>z position</b>. Ties go to the higher S.</li>
<li>"Not perfectly flat" is the expected comment on any equalized histogram, because levels are discrete.</li>
</ul>
{tbl(["thing", "formula / rule"], [
    ["histogram", "h(r<sub>k</sub>) = n<sub>k</sub>"], ["normalized", "p(r<sub>k</sub>) = n<sub>k</sub>/N, Σ = 1"],
    ["sliding", "add a constant: brighter or darker, same shape"], ["stretching", "g = 255(f − MIN)/(MAX − MIN), same shape"],
    ["equalization", "s<sub>k</sub> = round((L−1)·CDF(r<sub>k</sub>))"], ["matching", "equalize input → H, equalize target → S, map H to closest S"]])}
"""))

toc = [("start", "Start"), ("gen", "Make & read"), ("norm", "Normalized"), ("slide", "Slide & stretch"), ("he", "Equalization"),
       ("hepq", "HE past papers"), ("pass2", "Homework"), ("hs", "Matching"), ("theory", "Theory answers"), ("traps", "Traps")]
OUT.write_text(page("DIP Deck 05 Lesson", "CSE 4227 · Chapter 3 · Deck 05", "Histogram Processing, from zero",
                    "Every slide you need, in plain words, with every histogram and curve drawn, and the past-paper questions solved the way you write them in the answer script.",
                    toc, S_, extra=sim_assets()), encoding="utf-8")

# ---------------------------------------------------------------- self-check against data/answers.json and the slides
assert s36 == [0, 2, 4, 4, 5, 6, 6, 7] and eh36 == [1, 0, 6, 0, 5, 3, 3, 2]
assert s_sp25 == [1, 3, 4, 4, 5, 6, 7, 7] and eh_sp25 == [0, 3, 0, 7, 6, 3, 3, 3]
assert s_f22 == [1, 3, 5, 6, 6, 7, 7, 7]
assert H49 == [1, 3, 5, 6, 6, 7, 7, 7] and S49 == [0, 0, 0, 1, 2, 5, 6, 7] and z49 == [3, 4, 5, 6, 6, 7, 7, 7] and o49 == [0, 0, 0, 790, 1023, 850, 985, 448]
assert H55 == [1, 2, 3, 3, 5, 6, 7, 7] and S55 == [0, 0, 0, 0, 2, 4, 6, 7] and z55 == [4, 4, 5, 5, 6, 6, 7, 7] and o55 == [0, 0, 0, 0, 18, 12, 28, 6]
assert eh_cw == [0, 0, 0, 100, 0, 90, 50, 20]
assert s_f23 == [4, 6, 6, 6, 6, 8, 8, 8, 8, 10, 12, 12, 14, 16, 17, 17, 21, 21, 23, 25, 25, 25, 25, 25, 25, 27, 27, 27, 29, 29, 31, 31]
assert s_sp22 == [0, 0, 0, 0, 0, 2, 6, 16, 17, 21, 23, 29] + [31] * 20
assert s_f21 == [2, 4, 4, 4, 6, 8, 10, 10, 12, 14, 16, 16, 17, 19, 21, 21, 23, 23, 23, 25, 25, 25, 25, 25, 25, 27, 27, 27, 27, 29, 31, 31]
assert s_q2c == [0, 2, 4, 4, 5, 6, 6, 7] and s_q1d == [0, 1, 1, 2, 3, 4, 6, 7] and eh_q1d == [2, 8, 6, 9, 12, 0, 14, 13]
assert s2nd[0] == 0 and all(s2nd[v] == v for v in range(8) if eh36[v])
print(OUT, OUT.stat().st_size, "s_q2c", s_q2c, "s_q1d", s_q1d, eh_q1d)
