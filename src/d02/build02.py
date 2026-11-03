"""Builds deck02_lesson.html: decks 01 (introduction) and 02 (digital image fundamentals) on one page. Fall 2024 questions left out on purpose."""
import sys, pathlib, math
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from kit import *

OUT = pathlib.Path(__file__).with_name("deck02_lesson.html")


def nn_pos(old, n):
    return [((i + 1) * old + n - 1) // n for i in range(n)]  # ceil(old/n × i), 1-indexed


def nn_zoom(img, h, w):
    rp, cp = nn_pos(len(img), h), nn_pos(len(img[0]), w)
    return rp, cp, [[img[r - 1][c - 1] for c in cp] for r in rp]


def nn_answer(img, h, w):
    rp, cp, out = nn_zoom(img, h, w)
    H, W = len(img), len(img[0])
    return (f"<p><b>Step 1 · ratios:</b> Ratio<sub>row</sub> = {H}/{h}, Ratio<sub>col</sub> = {W}/{w}.</p>"
            f"<p><b>Step 2 · positions</b> = ratio × [1 … {h}], rounded up (ceil):</p>"
            + formula(f"rows: {H}/{h} × [{' '.join(map(str, range(1, h + 1)))}] = [{' '.join(f'{H * (i + 1) / h:.3g}' for i in range(h))}] → ceil → <b>[{' '.join(map(str, rp))}]</b><br>"
                      f"cols: {W}/{w} × [{' '.join(map(str, range(1, w + 1)))}] = [{' '.join(f'{W * (j + 1) / w:.3g}' for j in range(w))}] → ceil → <b>[{' '.join(map(str, cp))}]</b>")
            + f"<p><b>Step 3 · copy:</b> output pixel (i, j) = old pixel (row position i, column position j).</p>"
            + mats(mat(img, f"original {H}×{W}"), mat(out, f"output {h}×{w}"))), out


def digitize_plot():
    strip = [7, 7, 7, 1, 2, 3, 4, 4, 5, 5, 5, 5, 5, 4, 3, 3, 2, 1, 0, 0, 7, 7, 7]
    off = [0.2, -0.1, 0.3, -0.3, 0.25, -0.2, 0.35, -0.15, 0.1, 0.4, -0.3, 0.2, -0.1, 0.3, -0.25, 0.15, 0.3, -0.35, 0.2, -0.1, 0.25, -0.2, 0.1]
    g = [s + o for s, o in zip(strip, off)]
    fine = []
    for i in range(len(g) - 1):
        for t in range(6):
            fine.append((i + t / 6, g[i] + (g[i + 1] - g[i]) * (0.5 - 0.5 * math.cos(math.pi * t / 6))))
    fine.append((len(g) - 1, g[-1]))
    pts = [(i, strip[i], "", "c3") for i in range(len(strip))]
    return plot(len(strip) - 1, 7.6, curves=[{"pts": fine, "cls": "c1", "label": "continuous intensity along A–B", "at": (6.5, 6.9)}], points=pts,
                xticks=[(0, "A"), (len(strip) - 1, "B")], yticks=list(range(8)), xlabel="sampling: one dot per sample position", ylabel="quantized level (3 bits)", w=520, h=260,
                caption="slide 15: sampling picks the positions (dots on the x-axis), quantization rounds each value to one of 2³ = 8 levels: A 7 7 7 1 2 3 4 4 5 5 5 5 5 4 3 3 2 1 0 0 7 7 7 B"), strip, g


S = []

# ================================================================ deck 01
S.append(sec("d01", "Deck 01 in five minutes: what a digital image is", "01: 3–16", SHORT, f"""
{idea("A photo, for a computer, is a grid of numbers. Each little square (pixel) holds how bright it is (or its colour). Digital image processing is doing maths on that grid.")}
<p><b>Slides 3–9.</b> An image is a two-dimensional light-intensity function <b>f(x, y)</b>: x and y are spatial coordinates, and the value (amplitude) of f at a point is its <b>intensity</b> or gray level. When x, y and the amplitude are all <b>finite, discrete quantities</b>, the image is a <b>digital image</b>. A <b>pixel</b> is the smallest element of a digital image; each pixel has an intensity (gray level in a gray image, an R, G, B vector in a colour image). Formats: JPEG, PNG, BMP, TIFF, GIF. f(x,y) for photos, f(x,y,z) for 3-D (CT), f(x,y,t) for movies.</p>
<p><b>Slides 11–13.</b> Why process images: enhance visual quality, restore degraded images, compress for storage/transmission, analyse for recognition. Elements of a DIP system: <b>acquisition, storage, processing, display</b>. Levels: <b>low</b> (image in → image out), <b>mid</b> (image in → measurements/attributes out), <b>high</b> (attributes in → description/understanding out).</p>
<p><b>Slides 15–16. Key stages of DIP</b> (start from the problem domain):</p>
{tbl(["stage", "one line"], [["image acquisition", "capture the image with a sensor (camera, scanner); may include preprocessing such as scaling"], ["image enhancement", "improve visual quality (brightness, contrast) for a specific application"],
     ["image restoration", "repair degraded images (noise, blur)"], ["morphological processing", "manipulate shapes with set operations (erosion, dilation, opening, closing)"],
     ["segmentation", "split the image into regions (objects / background)"], ["representation &amp; description", "turn regions into a form for computers (boundary or region) and describe them"],
     ["object recognition", "label objects by shape, texture and other features"], ["compression", "reduce storage and transmission size while keeping quality"], ["colour image processing", "work with colour models, conversions and corrections"]])}
"""))

# ================================================================ deck 02 digitization
dplot, strip, g = digitize_plot()
S.append(sec("dig", "Sampling and quantization", "02: 12–16", EXAM, f"""
{idea("A real scene is continuous: any position, any brightness. To store it, cut it twice. <b>Sampling</b> chooses a grid of positions (how many pixels). <b>Quantization</b> rounds each brightness to one of a few allowed levels (how many gray levels).")}
<p><b>Slide 12.</b> Computers use a discrete form of pictures; transforming the continuous analog image into a discrete approximation is <b>digitization</b>, in two steps: <b>sampling</b> and <b>quantization</b>.</p>
{tbl(["step", "digitizes", "decides"], [["<b>sampling</b>", "the coordinate values (x, y)", "the spatial resolution M × N (number of pixels)"], ["<b>quantization</b>", "the amplitude (intensity) values", "the number of gray levels L (usually a power of 2)"]])}
{figs(dplot)}
<p><b>Slides 16–19.</b> A digital image is always only an <b>approximation</b> of the scene. It is stored as an M × N matrix with the origin (0,0) at the top-left, x down the rows and y across the columns (MATLAB numbers from 1 instead).</p>
{paper("SP22 Final Q3(a)", "3 + 2 marks", '''<p class="q">(i) Mention two techniques that made the digital representation of the analog world possible. (ii) “The more intensity levels used, the finer the level of detail discernible in an image.” Explain why.</p>
<p><b>(i)</b> <b>Sampling</b>: measuring the continuous scene only at a grid of points, which digitizes the coordinates and fixes the spatial resolution M × N. <b>Quantization</b>: rounding each sampled brightness to one of L discrete levels (L = 2<sup>k</sup>), which digitizes the amplitude. Together they turn the analog picture into a matrix of integers.</p>
<p><b>(ii)</b> With more levels the step between neighbouring gray values is smaller, so small brightness differences (soft shading, fine texture) get different numbers and stay visible. With few levels, many different intensities are rounded to the same value; smooth areas turn into flat bands with visible jumps between them (<b>false contouring</b>, slides 30–34), and fine detail is lost.</p>''')}
"""))

# ================================================================ resolution
bits = [(k, 2 ** k) for k in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 16)]
S.append(sec("res", "Gray levels, bits and image size", "02: 20–25", EXAM, f"""
{formula("L = 2<sup>k</sup> (k = bit depth) &nbsp;&nbsp; gray range = [0, L − 1] &nbsp;&nbsp; image size b = M × N × k bits (square: N² k)")}
<p><b>Slide 20.</b> f(x,y) = i(x,y) · r(x,y), with illumination 0 &lt; i &lt; ∞ and reflectance 0 &lt; r &lt; 1. The gray level l = f(x,y) lies in [L<sub>min</sub>, L<sub>max</sub>] (the grayscale): a scalar measure of intensity from black through grays to white.</p>
<p><b>Slides 21–22. Intensity (gray-level) resolution</b> = the number of intensity levels L used. It is usually given as bits per pixel: k bits give L = 2<sup>k</sup> levels; 8 bits give 256 levels, range [0, 255].</p>
{tbl(["bits k", "levels L = 2<sup>k</sup>", "range"], [[k, f"{L:,}", f"0 – {L - 1:,}"] for k, L in bits], "narrow")}
<p><b>Slide 23. Spatial resolution</b> = M × N (rows × columns). A 2048 × 1536 image has 3,145,728 pixels, a 3.1-megapixel image.</p>
{paper("Slide 25 · answer the questions", "worked", '''<p><b>Q1</b> 1 bit → 2<sup>1</sup> = <b>2</b> levels (0, 1). <b>Q2</b> 2 bits → <b>4</b> levels. <b>Q3</b> p bits → <b>2<sup>p</sup></b> levels. <b>Q4</b> 256 intensities → log<sub>2</sub> 256 = <b>8</b> bits.</p>
<p><b>Q5</b> 3-bit 5×5 image: gray-level resolution L = 2³ = <b>8</b> levels (range 0–7); spatial resolution <b>5 × 5</b> = 25 pixels; size b = 5 × 5 × 3 = <b>75 bits</b>; bit depth <b>3</b>.</p>''')}
{paper("F25 Quiz Q1C Q2(b)", "3 marks", '''<p class="q">How many shades of gray are possible in a 10-bit grayscale image? Show their numeric range. Illustrate the expression of intensity resolution.</p>
<p>L = 2<sup>k</sup> = 2<sup>10</sup> = <b>1024</b> shades; range <b>[0, L − 1] = [0, 1023]</b>. Intensity resolution of a k-bit image is L = 2<sup>k</sup> levels: more bits → more levels → finer steps between grays, less false contouring.</p>''')}
{paper("F22 Final B4(b) · F21 Final A3(b) (other examiners' papers)", "5 · 6 marks", f'''<p class="q">F22: define sampling and quantization; bits for 512 intensities; spatial resolution and bit size of a 7×5 image. F21: a 256×256 image with 64 gray levels: bit depth and size in bytes; Mach band effect; index image; why more levels show finer detail.</p>
<p><b>F22:</b> sampling digitizes coordinates, quantization digitizes amplitude. 512 intensities → k = log<sub>2</sub> 512 = <b>9 bits</b>. A 7×5 image has spatial resolution 7 × 5 = 35 pixels; with 9 bits per pixel, b = 7 × 5 × 9 = <b>315 bits</b>.</p>
<p><b>F21:</b> 64 levels → k = log<sub>2</sub> 64 = <b>6 bits</b>; b = 256 × 256 × 6 = 393,216 bits = 393,216 / 8 = <b>49,152 bytes</b> (48 KB). <b>Mach band effect:</b> at the boundary between two flat bands of different brightness the eye sees a darker strip on the dark side and a brighter strip on the light side (overshoot/undershoot) that is not in the image. <b>Index image:</b> each pixel stores an index into a colour table (palette) holding the actual RGB values. The last part is the same as SP22 (ii) above.</p>''')}
"""))

# ================================================================ image types
S.append(sec("types", "Types of digital image", "02: 38–42", SHORT, f"""
{tbl(["type", "each pixel holds", "example"], [["<b>intensity / gray</b> (monochrome)", "one value: light intensity, a gray level", "[10 10 16 28; 9 6 26 37; …]"], ["<b>colour / RGB</b>", "a vector of three values (red, green, blue)", "[99, 65, 10]"],
     ["<b>binary</b> (black and white)", "one bit: 1 = white, 0 = black", "[0 0 0 0; 1 1 1 1]"], ["<b>index</b>", "an index number pointing to a colour in a colour table", "pixel 4 → table row 4 = (0.5, 0.5, 0.5)"]])}
<p><b>Slide 37.</b> Choosing size and depth: for images of the same size, a low-detail image may need more pixel depth; as image size grows, fewer gray levels may be needed.</p>
"""))

# ================================================================ zoom
rep = [[3, 2], [4, 1]]
rep_rows = [r for r in rep for _ in range(2)]
rep_out = [[v for v in r for _ in range(2)] for r in rep_rows]
A = [[10, 4, 22], [2, 18, 7], [9, 14, 25]]
a6, o6 = nn_answer(A, 6, 6)
cw = [([[1, 4], [3, 7]], 5, 5), ([[1, 4, 3], [7, 2, 3], [5, 6, 0]], 9, 9), ([[1, 4, 3, 7], [2, 3, 4, 5], [2, 6, 4, 3], [4, 7, 1, 0]], 7, 7)]
cwa = [nn_answer(m, h, w) for m, h, w in cw]
S.append(sec("zoom", "Zooming: pixel replication and nearest-neighbour interpolation", "02: 43–56", EXAM, f"""
{idea("Zooming needs more pixels than you have. Pixel replication just copies each pixel (works only for whole-number factors like ×2). Nearest-neighbour interpolation works for any size: for every new pixel, work out which old pixel it falls on, and copy that one.")}
<p><b>Slides 43–45. Pixel replication:</b> to double the size, duplicate each row, then each column (any integer factor works the same way). New pixels are exact copies of old ones.</p>
{mats(mat(rep, "original 2×2"), mat(rep_rows, "after row duplication"), mat(rep_out, "after column duplication: 4×4"))}
<p><b>Slides 46–48. Interpolation</b> uses known data to estimate unknown values (zooming, shrinking, rotating, geometric correction). Types: <b>nearest neighbour</b>, bilinear, bicubic. Nearest neighbour: <b>mapping</b> (find each target pixel's location in the source), <b>selection</b> (take the source pixel closest to it), <b>assignment</b> (copy its value): fast, but blocky “stair-step” edges.</p>
{paper("Slides 49–54 · 3×3 → 6×6", "worked", a6)}
{sim({"type": "nni", "img": A, "to": [6, 6]}, "the slide example. Change the new size (e.g. 5×5, 7×7, 9×9) to see how the positions change; the class-work matrices are solved just below.")}
<p><b>Slide 52.</b> Rounding choice matters: for 4 → 7 the positions are floor [0 1 1 2 2 3 4], ceil [1 2 2 3 3 4 4], round [1 1 2 2 3 3 4]. The slides use <b>ceil</b> (1-indexed).</p>
{paper("Slide 55 · class work", "solved", "".join(f"<p><b>{len(m)}×{len(m[0])} → {h}×{w}</b></p>" + a for (m, h, w), (a, _) in zip(cw, cwa)))}
<p><b>Slide 56. Shrinking</b> (down-scaling) works the same way, but instead of replicating, delete every second row and column (halving). <b>Slides 57–61 (skip):</b> bilinear interpolation takes a distance-weighted average of the 2×2 known neighbours (smoother than nearest neighbour); bicubic uses 4×4.</p>
"""))

# ================================================================ traps
S.append(sec("traps", "Traps and one-minute sheet", "all", None, f"""
<ul class="traps">
<li>Sampling ↔ coordinates ↔ spatial resolution. Quantization ↔ amplitude ↔ gray-level resolution.</li>
<li>L = 2<sup>k</sup>; range is [0, L − 1], not [1, L].</li>
<li>Size b = M × N × k is in <b>bits</b>; divide by 8 for bytes.</li>
<li>Nearest-neighbour positions: ratio = old / new, multiply by 1…n, round <b>up</b>, then copy.</li>
<li>Too few gray levels → false contouring; too few pixels → blocky (checkerboard) image.</li>
</ul>
"""))

toc = [("d01", "Deck 01"), ("dig", "Sampling & quantization"), ("res", "Bits & size"), ("types", "Image types"), ("zoom", "Zooming"), ("traps", "Traps")]
OUT.write_text(page("DIP Decks 01–02 Lesson", "CSE 4227 · Chapters 1–2 · Decks 01–02", "Introduction and digital image fundamentals",
                    "What a digital image is, sampling and quantization with a real graph, bits/levels/size arithmetic, image types, and nearest-neighbour zooming with a step-by-step simulator. Fall 2024 is left out.",
                    toc, S, extra=sim_assets()), encoding="utf-8")

# ---------------------------------------------------------------- self-check (data/answers.json PIX/NNI*, F25-Q1C/2b)
assert o6 == [[10, 10, 4, 4, 22, 22], [10, 10, 4, 4, 22, 22], [2, 2, 18, 18, 7, 7], [2, 2, 18, 18, 7, 7], [9, 9, 14, 14, 25, 25], [9, 9, 14, 14, 25, 25]]
assert nn_pos(2, 5) == [1, 1, 2, 2, 2] and nn_pos(4, 7) == [1, 2, 2, 3, 3, 4, 4] and nn_pos(3, 9) == [1, 1, 1, 2, 2, 2, 3, 3, 3]
assert cwa[2][1][0] == [1, 4, 4, 3, 3, 7, 7] and cwa[0][1][4] == [3, 3, 7, 7, 7]
assert all(round(x) == s for x, s in zip(g, strip)) and rep_out == [[3, 3, 2, 2], [3, 3, 2, 2], [4, 4, 1, 1], [4, 4, 1, 1]]
print(OUT, OUT.stat().st_size)
