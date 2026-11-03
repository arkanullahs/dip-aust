"""Builds deck11_lesson.html: morphological image processing part I. All grids computed here."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from kit import *

OUT = pathlib.Path(__file__).with_name("deck11_lesson.html")


# ---------------------------------------------------------------- morphology (same rules as scripts/solvers.py and sim_kit.js)
def P(rows):
    return [[1 if ch in "#1" else 0 for ch in r] for r in rows]


def offs(se, origin):
    return [(i - origin[0], j - origin[1]) for i, row in enumerate(se) for j, v in enumerate(row) if v == 1]


def px(A, r, c):
    return A[r][c] if 0 <= r < len(A) and 0 <= c < len(A[0]) else 0


def erode(A, se, o):
    return [[1 if all(px(A, r + a, c + b) for a, b in offs(se, o)) else 0 for c in range(len(A[0]))] for r in range(len(A))]


def dilate(A, se, o):
    return [[1 if any(px(A, r - a, c - b) for a, b in offs(se, o)) else 0 for c in range(len(A[0]))] for r in range(len(A))]


def opening(A, se, o):
    return dilate(erode(A, se, o), se, o)


def closing(A, se, o):
    return erode(dilate(A, se, o), se, o)


def comp(A):
    return [[1 - v for v in r] for r in A]


def minus(X, Y):
    return [[1 if a and not b else 0 for a, b in zip(rx, ry)] for rx, ry in zip(X, Y)]


def ones(M):
    return {(r, c) for r, row in enumerate(M) for c, v in enumerate(row) if v}


def bm(M, cap="", small=True, mark=None):
    """Binary grid: 1s shaded."""
    return mat(M, cap, hi=ones(M) if mark is None else mark, small=small)


def se_grid(se, o, cap):
    return mat([["×" if v is None else v for v in row] for row in se], cap, hi={(i, j) for i, row in enumerate(se) for j, v in enumerate(row) if v == 1}, ctr=tuple(o), small=True)


def msim(A, se, o, ops, cap, op=None, discard=False, symmetric=True):
    return sim({"type": "morph", "A": A, "se": se, "origin": list(o), "ops": ops, "op": op or ops[0], "discard": discard, "symmetric": symmetric}, cap)


CROSS, SQ = [[0, 1, 0], [1, 1, 1], [0, 1, 0]], [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
C = (1, 1)
S = []

# ================================================================ 1. intro
S.append(sec("start", "Start here: what morphology is", "3–10", LIKELY, f"""
{idea("Morphology works on <b>shapes</b> in a black-and-white image. You slide a small stamp, the <b>structuring element</b> (SE), over the image and ask one yes/no question at every pixel: does the stamp <b>fit</b> inside the object here, or does it <b>touch</b> the object? The answers shrink, grow, clean or outline the shapes.")}
<p><b>Slide 3.</b> Morphological image processing is used to <b>extract image components</b> for representation and description of <b>region shape</b>, such as boundaries, skeletons and the convex hull.</p>
<p><b>Slide 4.</b> It relies only on the <b>relative ordering of pixel values</b>, not on their numerical values. We probe the image with a small shape or template called a <b>structuring element</b>. The language of mathematical morphology is <b>set theory</b>.</p>
<p><b>Slide 5.</b> Morphology applies simple rules and shapes (squares, circles, diamonds, cubes, spheres) to process images. The objective is usually to identify features of interest, as a prelude to high-level inspection or machining. Two kinds: <b>binary</b> morphology and <b>grey-level</b> morphology. Four basic operations for binary images: <b>erosion, dilation, opening and closing</b>.</p>
<p><b>Slide 6. Binary image convention:</b> each pixel is 0 or 1; foreground (object) = 1 (white), background = 0 (black).</p>
<h3>Structuring element (slides 7–10)</h3>
<p>A <b>structuring element</b> is a small image or template, a small binary array, that produces a new image from the old one. It is a shape mask used in the basic morphological operations. It can be <b>any shape and size</b> that is digitally representable (box, hexagon, disk, any shape), and each has an <b>origin</b>.</p>
<p>It works as a moving window, so non-rectangular shapes are stored as rectangular arrays (padded with 0s). For simplicity we use rectangular SEs with their origin point; the <b>origin can be at the middle or at any position</b>, and by default it is at the centre.</p>
{mats(se_grid(SQ, C, "3×3 square"), se_grid(CROSS, C, "3×3 cross (the slides' usual SE)"), se_grid([[0, 0, 1, 0, 0], [0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0], [0, 0, 1, 0, 0]], (2, 2), "5×5 diamond"), se_grid([[1, 1, 1], [1, 1, 1], [1, 1, 1]], (2, 2), "3×3 square, origin bottom-right"))}
"""))

# ================================================================ 2. fit / hit
F13 = P(["............", "...##.......", "..#####.....", ".#######....", ".#######....", "..######....", "..#######...", "..#########.", ".....######.", "............"])
boxes = {"A": (6, 3), "B": (2, 3), "C": (2, 8)}
def fit(A, se, r, c):
    return all(px(A, r + a, c + b) for a, b in offs(se, C))
def hit(A, se, r, c):
    return any(px(A, r + a, c + b) for a, b in offs(se, C))
fh = [[k] + [("yes" if fit(F13, se, r, c) else "no") for se in (SQ, CROSS)] + [("yes" if hit(F13, se, r, c) else "no") for se in (SQ, CROSS)] for k, (r, c) in boxes.items()]
S.append(sec("fithit", "Fit, hit and miss", "11–13", LIKELY, f"""
<p><b>Slide 11.</b> Put the SE on the image:</p>
<ul><li><b>Fit:</b> <b>all</b> "on" pixels of the SE cover "on" pixels of the image.</li><li><b>Hit:</b> <b>any</b> "on" pixel of the SE covers an "on" pixel of the image.</li><li><b>Miss:</b> no "on" pixel of the SE covers an "on" pixel.</li></ul>
<p>All morphological processing operations are based on these simple ideas: <b>erosion uses fit, dilation uses hit</b>.</p>
<p><b>Slide 12.</b> Fundamentally, morphological processing is very like spatial filtering: the SE is moved across every pixel and gives one pixel of the new image, whose value depends on the operation performed. The two basic operations are <b>erosion and dilation</b>.</p>
{paper("Slide 13 · fitting and hitting with s1 and s2", "solved", f'''
<p class="q">Fill in the fit/hit table for the three positions A, B, C of the binary image, with s<sub>1</sub> = 3×3 square and s<sub>2</sub> = 3×3 cross (origin at the centre).</p>
{bm(F13, "the image; A, B, C are the 3×3 windows centred at (6,3), (2,3), (2,8)")}
{mats(bm([row[2:5] for row in F13[5:8]], "window A"), bm([row[2:5] for row in F13[1:4]], "window B"), bm([row[7:10] for row in F13[1:4]], "window C"), se_grid(SQ, C, "s1"), se_grid(CROSS, C, "s2"))}
{tbl(["position", "fit s1", "fit s2", "hit s1", "hit s2"], fh, "narrow")}
<p>A is all 1s, so both fit and both hit. B has a 0 in one corner: the square does not fit (that corner), but the cross does (it ignores corners). C has a single 1 in a corner: the square hits it, the cross misses it completely.</p>
''')}
"""))

# ================================================================ 3. erosion
one = [[1, 0, 0, 0, 1, 1, 1, 0, 1, 1]]
H1 = [[1, 1, 1]]
e1d = erode(one, H1, (0, 1))[0][1:9]
d1d = dilate(one, H1, (0, 1))[0][1:9]
EX1 = P(["........", "...###..", "..####..", ".####...", ".###....", ".###....", "........", "........"])
EX1e = erode(EX1, CROSS, C)
S.append(sec("ero", "Erosion", "14–44", EXAM, f"""
{idea("Erosion keeps a pixel only if the whole SE fits inside the object when centred there. Pixels near the edge fail, so the object loses its outer layer: it <b>shrinks</b>. Tiny specks smaller than the SE vanish completely.")}
<p><b>Slides 14–15.</b> Erosion <b>shrinks the object</b>: it shrinks the foreground and enlarges the background. One of its simplest uses is eliminating <b>irrelevant details</b> from a binary image.</p>
<p><b>Slide 16. Definition 1 (does the SE fit the set?).</b> Erosion of a set A by SE B is the set of all points z such that B translated by z is contained in A:</p>
{formula("A ⊖ B = { z | (B)<sub>z</sub> ⊆ A }")}
<p><b>Slide 17. Definition 2.</b> The SE s is positioned with its origin at (x, y) and the new pixel value is</p>
{cases("g(x,y)", [("1", "if s fits f"), ("0", "otherwise")])}
<p><b>Slide 18. How to compute:</b> for each foreground pixel (the input pixel), superimpose the SE so that its origin coincides with the input pixel. If <b>every</b> SE pixel lies on a foreground pixel of the image, the input pixel stays as it is; if <b>any</b> of them lies on background, the input pixel is set to background.</p>
{paper("Slides 19–26 · 1-D erosion", "worked", f'''
<p>Input 1 0 0 0 1 1 1 0 1 1, SE [1 1 1] with the origin at the centre. At each position take the <b>minimum</b> of the three values under the SE (superimpose and multiply: all three must be 1). The two end pixels are ignored.</p>
{tbl(["position", *range(1, 9)], [["window"] + [" ".join(map(str, one[0][i - 1:i + 2])) for i in range(1, 9)], ["minimum"] + e1d], "narrow")}
<p>Output: <b>{" ".join(map(str, e1d))}</b>. Only the middle of the 1 1 1 run survives.</p>
''')}
{msim(one, H1, (0, 1), ["erode", "dilate"], "the 1-D example, position by position (switch the menu to dilation for slides 50–57).", discard=True)}
{paper("Slides 27–38 · Erosion example 1 (8×8, cross SE)", "worked", mats(bm(EX1, "original"), se_grid(CROSS, C, "SE (origin centre)"), bm(EX1e, "A ⊖ B")) +
       f"<p>Only {len(ones(EX1e))} pixels keep the whole cross inside the object. Every boundary pixel had at least one cross arm on background.</p>")}
{msim(EX1, CROSS, C, ["erode"], "erosion example 1, every one of the 64 positions (slides 27–38).")}
<p><b>Slide 39.</b> Erosion can <b>split apart joined objects</b> and <b>strip away extrusions</b>. Watch out: erosion shrinks objects.</p>
<p><b>Slide 40. Typical uses:</b> removes isolated noisy pixels; smoothes the object boundary (removes spiky edges); removes the outer layer of object pixels, so the object becomes slightly smaller (sets contour pixels to the background value).</p>
<p><b>Slide 41. Effects:</b> shrinks the size of foreground (1-valued) objects; smoothes object boundaries; removes small objects. <b>Rule:</b> in a binary image, if any pixel in the neighbourhood defined by the SE is 0, the output is 0.</p>
<p><b>Slide 42.</b> Eroding four times with an 11-pixel disk: the hole in the middle of the square grows as the border shrinks. A disk SE tends to round concave boundaries but preserves the shape of convex boundaries.</p>
{paper("Slides 43–44 · Exercise: count the coins", "solved", '''
<p class="q">Count the number of coins in the given image by performing an erosion operation.</p>
<ol><li><b>Binarize</b> the image (threshold): coins become white blobs on a black background. Many coins touch each other, so they form joined blobs.</li>
<li><b>Erode</b> with a disk SE large enough to break the narrow necks where coins touch. Each coin shrinks to a smaller, separate blob.</li>
<li>Use <b>connected-component labeling</b> to count the separate blobs: the count equals the number of coins.</li></ol>
''')}
"""))

# ================================================================ 4. dilation
EX1d = dilate(EX1, CROSS, C)
S.append(sec("dil", "Dilation", "45–63", EXAM, f"""
{idea("Dilation turns a pixel on if the SE centred there touches the object anywhere. Every object grows by a layer as thick as the SE arm: it <b>grows</b>, small holes fill up and nearby pieces join.")}
<p><b>Slides 45–46.</b> Dilation <b>grows the object</b>: it enlarges the foreground and shrinks the background. It takes two inputs: the binary image to be dilated and the SE (kernel) that decides the behaviour.</p>
<p><b>Slide 47. Definition 1 (does the SE hit the set?).</b> Dilation of A by B is the set of all z such that the reflected B̂, translated to z, overlaps A by at least one element:</p>
{formula("A ⊕ B = { z | (B̂)<sub>z</sub> ∩ A ≠ ∅ }")}
<p><b>Slide 48. Definition 2:</b></p>
{cases("g(x,y)", [("1", "if s hits f"), ("0", "otherwise")])}
<p><b>Slide 49. How to compute:</b> for each background pixel, superimpose the SE with its origin on the input pixel. If <b>at least one</b> SE pixel coincides with a foreground pixel, the input pixel becomes foreground; if all of them are background, it stays background. (B̂ = B for the symmetric square and cross, so you can skip the reflection.)</p>
{paper("Slides 50–57 · 1-D dilation", "worked", f'''
<p>Same input 1 0 0 0 1 1 1 0 1 1, SE [1 1 1]. Now take the <b>maximum</b> of the three values under the SE (border pixels ignored).</p>
{tbl(["position", *range(1, 9)], [["window"] + [" ".join(map(str, one[0][i - 1:i + 2])) for i in range(1, 9)], ["maximum"] + d1d], "narrow")}
<p>Output: <b>{" ".join(map(str, d1d))}</b>. Only position 2, whose window 0 0 0 has no 1 at all, stays 0.</p>
''')}
{paper("Slide 58 · Dilation example 1 (same image, cross SE)", "worked", mats(bm(EX1, "original"), se_grid(CROSS, C, "SE"), bm(EX1d, "A ⊕ B")) +
       f"<p>The dilated pixels (the slide's green cells) are A ⊕ B − A: {len(ones(EX1d)) - len(ones(EX1))} new pixels, one layer all round.</p>")}
{msim(EX1, CROSS, C, ["dilate", "erode"], "dilation example 1, every position.")}
<p><b>Slide 59. Bridging gaps:</b> a low-resolution text with broken characters, dilated with the 3×3 cross [0 1 0; 1 1 1; 0 1 0]: the broken segments were joined.</p>
<p><b>Slide 60.</b> Dilation can <b>repair breaks</b> and <b>repair intrusions</b>. Watch out: dilation enlarges objects.</p>
<p><b>Slide 61. Edge detection:</b> 1. dilate the input image; 2. subtract the input image from the dilated image; 3. edges remain.</p>
<p><b>Slide 62. Typical uses:</b> fills in holes; smoothes object boundaries; adds an extra outer ring of pixels onto the object boundary, so the object becomes slightly larger.</p>
<p><b>Slide 63. Effects:</b> expands the size of foreground objects; smoothes object boundaries; <b>closes holes and gaps</b>. <b>Rule:</b> if any pixel in the neighbourhood defined by the SE is 1, the output is 1.</p>
<h3>Duality (slides 64–70, formula only)</h3>
{formula("(A ⊖ B)<sup>c</sup> = A<sup>c</sup> ⊕ B̂ &nbsp;&nbsp;&nbsp; (A ⊕ B)<sup>c</sup> = A<sup>c</sup> ⊖ B̂")}
<p>Dilation and erosion are duals: one can be written in terms of the other (they are not opposites). We can obtain the erosion of A by dilating its background A<sup>c</sup> with the same SE and complementing the result.</p>
"""))

# ================================================================ 5. opening / closing
OPN = P(["....###.", "....###.", "....###.", "...##...", ".###....", ".###....", ".###....", "........"])
OPNe, OPNo = erode(OPN, CROSS, C), opening(OPN, CROSS, C)
CLS = P(["........", "....###.", "....###.", "........", ".###....", ".###....", ".###....", "........"])
CLSd, CLSc = dilate(CLS, CROSS, C), closing(CLS, CROSS, C)
S.append(sec("open", "Opening and closing", "71–117", EXAM, f"""
{idea("Opening = erode, then dilate. Erosion deletes anything too small for the SE; dilation then grows what's left back to its size. Small specks and thin bridges are gone for good. Closing = dilate, then erode: dilation fills small holes and gaps, erosion trims the object back to size. The holes stay filled.")}
<p><b>Slide 71.</b> Combinations of erosions and dilations give more interesting compound operations; the most used are <b>opening</b> and <b>closing</b>.</p>
<p><b>Slides 72–73. Opening</b> of A by B, A ∘ B, is an erosion followed by a dilation:</p>
{formula("A ∘ B = (A ⊖ B) ⊕ B")}
{paper("Slides 74–87 · Opening example (cross SE)", "worked", mats(bm(OPN, "original A"), se_grid(CROSS, C, "SE"), bm(OPNe, "step 1: A ⊖ B"), bm(OPNo, "step 2: (A ⊖ B) ⊕ B = A ∘ B")) +
       "<p>Erosion leaves only the two centres where the whole cross fits, (1,5) and (5,2). Dilation puts a cross back on each. The narrow link between the two blobs (row 3) and the blob corners are gone: they were thinner than the SE.</p>")}
{msim(OPN, CROSS, C, ["open", "close"], "the slide 74–87 opening: erosion pass, then dilation pass. Use “Next phase” to jump between them.")}
<p><b>Slides 88–92. Effect of opening:</b></p>
<ul><li>Smooths the outline by rounding off sharp points.</li><li>Removes any parts that are smaller than the shape (SE) used.</li><li>Disconnects or "opens" thin bridges.</li>
<li>Does <b>not</b> remove holes or gaps in the image.</li><li>Does not make the basic "core" size of the shape larger or smaller.</li>
<li>Repeating an opening with the same kernel has no further effect (opening is idempotent).</li></ul>
<p>Examples: the letter j with noise specks loses the tiny spots without changing its core size. Opening a lines-and-circles image with an 11-pixel disk separates the circles from the lines: the lines are almost completely removed, the circles stay.</p>
<p><b>Slides 93–94. Closing</b> of A by B, A • B, is a dilation followed by an erosion:</p>
{formula("A • B = (A ⊕ B) ⊖ B")}
{paper("Slides 95–108 · Closing example (cross SE)", "worked", mats(bm(CLS, "original A"), se_grid(CROSS, C, "SE"), bm(CLSd, "step 1: A ⊕ B"), bm(CLSc, "step 2: (A ⊕ B) ⊖ B = A • B")) +
       "<p>Dilation joins the two blobs across the gap. Erosion shrinks them back to their original outlines, but the new pixels (3,3) and (3,4) in the gap survive: closing <b>bridged</b> the gap without growing the objects.</p>")}
{msim(CLS, CROSS, C, ["close", "open"], "the slide 95–108 closing: dilation pass, then erosion pass.")}
<p><b>Slides 109–113. Effect of closing:</b></p>
<ul><li>Smooths the outline by <b>filling in</b> (closing) any holes and indentations.</li><li>Forms connecting "bridges" to other shapes that are close enough for the SE to touch both at once.</li>
<li>Does not make the basic core size larger or smaller.</li><li>Repeating a closing with the same kernel changes nothing more.</li></ul>
<p>Examples: closing with a 22-pixel disc closes the small holes in the foreground (pizza image); threshold a telephone photo, then close with a disc of size 20 to fill the reflections.</p>
{paper("Slide 114 · Exercise: which one should we apply here?", "solved", '''
<p class="q">The input map of Africa (white land) has black text "Northern Africa", "South Africa" written on it; the output is the solid white shape. Which operation was applied?</p>
<p><b>Closing.</b> The black letters are small dark holes and gaps inside the white foreground. Dilation fills them (the SE touches the white on both sides of each stroke), and the following erosion restores the coastline, so the outline and the size of the continent are unchanged. Opening would not remove holes.</p>
''')}
<p><b>Slide 115. Applications of morphology:</b> noise removal in scanned documents; medical imaging (blood vessel extraction); industrial inspection (defect detection); computer vision (object segmentation).</p>
<p><b>Slide 116.</b> Opening is the <b>dual</b> of closing: opening the foreground pixels with a particular SE is equivalent to closing the background pixels with the same element. (A ∘ B)<sup>c</sup> = A<sup>c</sup> • B̂.</p>
"""))

# ================================================================ 6. boundary
A25 = P(["......", ".####.", ".####.", ".####.", ".####.", "......"])
A25e, A25d = erode(A25, SQ, C), dilate(A25, SQ, C)
S.append(sec("bnd", "Boundary extraction and edge detection", "118–121", EXAM, f"""
<p><b>Slides 118–120.</b> Contours can be extracted by subtracting the eroded image from the original. First erode A by B, then take the set difference between A and the erosion. The thickness of the contour depends on the size of the SE.</p>
{formula("β(A) = A − (A ⊖ B)")}
<p><b>Slide 121. Edge detection by dilation:</b> (A ⊕ B) − A gives the pixels just outside the object (outer edge).</p>
{paper("Fall 25 quiz (set C) Q2", "7 marks", f'''
<p class="q">Construct a 6×6 binary image A and a 3×3 structuring element B. Using fundamental morphological operations, formulate an edge-detection algorithm for A with B, and demonstrate the procedure systematically with mathematical expressions.</p>
<p><b>Choose</b> A = a 4×4 square in a 6×6 image; B = 3×3 square, origin at the centre.</p>
{mats(bm(A25, "A"), se_grid(SQ, C, "B"))}
<p><b>Algorithm (inner boundary):</b> 1. erode: A ⊖ B = {{z | (B)<sub>z</sub> ⊆ A}}; 2. subtract: β(A) = A − (A ⊖ B) = A ∩ (A ⊖ B)<sup>c</sup>.</p>
<p>Step 1: B fits only where the pixel and all 8 neighbours are 1, i.e. the inner 2×2. Step 2: removing those from A leaves the one-pixel ring.</p>
{mats(bm(A25e, "A ⊖ B"), bm(minus(A25, A25e), "β(A) = A − (A ⊖ B)"))}
<p><b>Alternative (outer edge):</b> (A ⊕ B) − A, dilation then subtraction, gives the ring just outside the square:</p>
{mats(bm(A25d, "A ⊕ B"), bm(minus(A25d, A25), "(A ⊕ B) − A"))}
''')}
{msim(A25, SQ, C, ["boundary", "edge"], "both edge algorithms: erode then subtract, or dilate then subtract.")}
"""))

# ================================================================ 7. set basics (glance)
S.append(sec("sets", "Set basics (glance)", "123–130", SHORT, """
<ul>
<li>A binary image is a set in Z<sup>2</sup>: each element is a 2-D vector (x, y) of a foreground pixel. A grey image is a set in Z<sup>3</sup> ((x, y) and intensity).</li>
<li>a ∈ A (element of), a ∉ A, A = {(a<sub>1</sub>, a<sub>2</sub>), …}, empty set ∅.</li>
<li><b>Subset</b> A ⊆ B: every element of A is in B. <b>Union</b> A ∪ B; <b>intersection</b> A ∩ B; <b>disjoint</b> A ∩ B = ∅.</li>
<li><b>Complement</b> A<sup>c</sup> = {w | w ∉ A}. <b>Difference</b> A − B = {w | w ∈ A, w ∉ B} = A ∩ B<sup>c</sup>.</li>
<li><b>Reflection</b> B̂ = {w | w = −b, b ∈ B}: multiply both coordinates of every element by −1 (rotate 180° about the origin).</li>
<li><b>Translation</b> (A)<sub>z</sub> = {w | w = a + z, a ∈ A}: shift every element by z = (z<sub>1</sub>, z<sub>2</sub>).</li>
<li>Logic operations on binary images: NOT, AND, OR, XOR, NOT-AND (slide 128).</li>
</ul>
"""))

# ================================================================ 8. numeric past questions
FF = P([".....#", "..###.", ".####.", ".###..", "#....."])
V, Vo = [[1], [1], [1]], (1, 0)
fd, fe = dilate(FF, V, Vo), erode(FF, V, Vo)
fce = erode(comp(FF), V, Vo)
fo, fc = opening(FF, V, Vo), closing(FF, V, Vo)
X = P(["......", "...##.", "......", "......", "..#...", "...#..", "....#."])
Y = P([".####.", ".###..", "......", "#.#...", "##.#..", ".##.#.", "..##.."])
B23, o23 = [[1, 0, 1], [1, 1, 0]], (1, 2)
th = P(["...####...", "..######..", ".##....##.", ".##....##.", ".##....##.", "##......##", "##########", "##......##", ".##....##.", ".##....##.", ".##....##.", "..######..", "...####..."])
SE3, o3 = [[1], [1]], (0, 0)
the, tho = erode(th, SE3, o3), opening(th, SE3, o3)
S.append(sec("pq", "Numeric past questions, solved in full", "16–121", EXAM, f"""
<p>Convention used: outside the image counts as background (0). Write the set definition before each operation; it earns the equation marks.</p>
{paper("SP22 Q4(b) · F23 Q2(d) (same image)", "8 / 6 marks", f'''
<p class="q">F (5×6) and B = 3×1 vertical [1; 1; 1] with the origin at the centre. Compute (i) the reflection of B (ii) F ⊕ B (iii) F<sup>c</sup> ⊖ B (iv) (F ⊕ B) − F (v) the opening of F by B (vi) the closing of F by B, with equations.</p>
{mats(bm(FF, "F"), se_grid(V, Vo, "B (origin centre)"))}
<p><b>(i)</b> B̂ = {{w | w = −b, b ∈ B}}. B = {{(−1,0), (0,0), (1,0)}} → B̂ = {{(1,0), (0,0), (−1,0)}} = B. B is symmetric about its origin, so <b>B̂ = B</b>.</p>
<p><b>(ii)</b> F ⊕ B = {{z | (B̂)<sub>z</sub> ∩ F ≠ ∅}}: a pixel becomes 1 if it, the pixel above or the pixel below is 1.</p>
{mats(bm(fd, "F ⊕ B"))}
<p><b>(iii)</b> F<sup>c</sup> ⊖ B = {{z | (B)<sub>z</sub> ⊆ F<sup>c</sup>}}: complement F, then keep a pixel only if it and both vertical neighbours are 1 in F<sup>c</sup>.</p>
{mats(bm(comp(FF), "F<sup>c</sup>"), bm(fce, "F<sup>c</sup> ⊖ B"))}
<p><b>(iv)</b> (F ⊕ B) − F = the pixels added by the dilation (an outer edge above and below the object):</p>
{bm(minus(fd, FF), "(F ⊕ B) − F")}
<p><b>(v)</b> F ∘ B = (F ⊖ B) ⊕ B:</p>
{mats(bm(fe, "F ⊖ B"), bm(fo, "F ∘ B"))}
<p><b>(vi)</b> F • B = (F ⊕ B) ⊖ B:</p>
{mats(bm(fd, "F ⊕ B"), bm(fc, "F • B"))}
<p>Notice: the opening kept only the columns where the object is at least 3 pixels tall (columns 2–3), so everything thinner than B vertically is gone. The closing kept the whole object; the two isolated pixels (0,5) and (4,0) disappeared because they sit on the image border, where the erosion needs the pixel outside the image, which counts as 0.</p>
''')}
{msim(FF, V, Vo, ["dilate", "cerode", "edge", "open", "close", "erode"], "SP22 / F23: every part, switch the Operation menu.")}
{paper("SP23 Q1(a)", "3 + 2 + 2 + 2 marks", f'''
<p class="q">Images X and Y are given. (i) Design a structuring element B so that Y = X ⊕ B; mark the origin. (ii) Write the mathematical expression of the dilation. (iii) Erode Y with the same SE and show the eroded image. (iv) Explain erosion mathematically.</p>
{mats(bm(X, "X"), bm(Y, "Y"))}
<p><b>(i)</b> Take an isolated pixel of X, e.g. (6,4). In Y it has become (5,4), (6,3), (6,2), (5,2), and (6,4) itself is gone. So B holds the offsets (−1,0), (0,−1), (0,−2), (−1,−2) relative to its origin, and the origin itself is not part of B (value 0). Every other pixel of X gives the same pattern, which confirms it.</p>
{se_grid(B23, o23, "B (2×3), origin = bottom-right cell, value 0")}
<p>Check: X ⊕ B reproduces Y exactly.</p>
<p><b>(ii)</b> X ⊕ B = {{z | (B̂)<sub>z</sub> ∩ X ≠ ∅}} = {{x + b | x ∈ X, b ∈ B}}.</p>
<p><b>(iii)</b> Y ⊖ B = {{z | (B)<sub>z</sub> ⊆ Y}}: z survives only if all four offsets from z land on 1s in Y.</p>
{bm(erode(Y, B23, o23), "Y ⊖ B")}
<p>Here Y ⊖ B gives back X exactly (this image is lucky; in general (X ⊕ B) ⊖ B is the closing, which can also fill gaps).</p>
<p><b>(iv)</b> A ⊖ B = {{z | (B)<sub>z</sub> ⊆ A}}: the set of all origin positions z where the SE translated by z lies completely inside A. Equivalently, g(x,y) = 1 if B fits A at (x,y), else 0.</p>
''')}
{msim(X, B23, o23, ["dilate"], "SP23 (i): X ⊕ B gives Y. The SE is not symmetric, so watch the reflected cells.", symmetric=False)}
{msim(Y, B23, o23, ["erode"], "SP23 (iii): Y ⊖ B.", symmetric=False)}
{paper("SP24 Q3(c)", "2 + 2 + 4 marks", f'''
<p class="q">Binary image of the Greek letter θ. Which morphological operation(s) turn θ into the digit 0? Four SEs are given: SE1 horizontal 1×2, SE2 cross, SE3 vertical 2×1 (origin + below), SE4 vertical 3×1. Use any as many times as needed; explain the choice and show the outputs.</p>
{bm(th, "θ (13×10)")}
<p><b>What must go:</b> the middle bar (row 6) is only <b>1 pixel tall</b>. Every part of the ring is at least 2 pixels thick in the vertical direction. So an <b>opening with SE3</b> (vertical, 2 pixels) removes the bar and keeps the ring: θ ∘ SE3 = (θ ⊖ SE3) ⊕ SE3.</p>
<p><b>Why not the others:</b> SE1 is horizontal and the bar is long horizontally, so the bar survives. The cross (SE2) needs 3 pixels in both directions, which also deletes the thin ring corners. SE4 needs 3 pixels vertically, which deletes the 2-row top and bottom of the ring.</p>
<p><b>Step 1</b>, erosion θ ⊖ SE3 (keep a pixel only if it and the pixel below are both 1). <b>Step 2</b>, dilation by SE3 (put back the pixel below every survivor).</p>
{mats(bm(the, "θ ⊖ SE3"), bm(tho, "θ ∘ SE3 = the digit 0"))}
''')}
{msim(th, SE3, o3, ["open"], "SP24: the opening with SE3, both passes.", symmetric=False)}
"""))

# ================================================================ 9. theory + case
S.append(sec("theory", "Theory questions, answer-script form", "4–117", EXAM, f"""
{paper("SP25 Q1(f)", "4 marks", '''
<p class="q">Define dilation mathematically for a binary image. Explain the opening and closing operations. What happens when you apply closing to an image with small holes?</p>
<p><b>Dilation:</b> A ⊕ B = {z | (B̂)<sub>z</sub> ∩ A ≠ ∅}: the set of all displacements z such that the reflected SE B̂, translated to z, overlaps A in at least one pixel. It grows objects, fills small holes and bridges gaps.</p>
<p><b>Opening</b> A ∘ B = (A ⊖ B) ⊕ B, an erosion followed by a dilation: removes objects and protrusions smaller than B, breaks thin bridges and smooths the outline, without changing the size of the remaining objects.</p>
<p><b>Closing</b> A • B = (A ⊕ B) ⊖ B, a dilation followed by an erosion: fills small holes and gaps, joins nearby objects, and smooths indentations, again without changing the core size.</p>
<p><b>Closing on small holes:</b> the dilation fills every hole smaller than B (the SE reaches the object on all sides of the hole); the following erosion shrinks the object back to its original outline, but the filled holes cannot reopen because the SE now fits there. So <b>the small holes disappear</b> and the object's size and boundary stay the same (e.g. the pizza image closed with a 22-pixel disc).</p>
''')}
{paper("SP24 Q1(c) · SP22 Q4(a) · Fall 25 quiz (set C) Q1", "3–5 marks", '''
<p class="q">Give the equations of erosion and dilation; describe opening and closing. / Describe two basic morphological operations with equations, effects and applications. / Define dilation and erosion in binary images; how do they affect object size and shape?</p>
<p><b>Erosion</b> A ⊖ B = {z | (B)<sub>z</sub> ⊆ A}: a pixel stays 1 only where the SE fits inside the object. <b>Effects:</b> shrinks foreground objects (removes the outer layer), removes objects smaller than B, smooths the boundary by cutting spikes, can split touching objects, enlarges holes. <b>Uses:</b> removing isolated noise pixels, separating touching coins before counting, boundary extraction β(A) = A − (A ⊖ B).</p>
<p><b>Dilation</b> A ⊕ B = {z | (B̂)<sub>z</sub> ∩ A ≠ ∅}: a pixel becomes 1 where the SE hits the object. <b>Effects:</b> expands foreground objects (adds an outer layer), fills small holes, bridges gaps, joins nearby objects, smooths intrusions. <b>Uses:</b> repairing broken characters in low-resolution text, filling holes, edge detection (A ⊕ B) − A.</p>
<p><b>Size and shape:</b> erosion makes objects smaller and thinner (size shrinks by the SE radius); dilation makes them larger and thicker. The SE's shape decides the direction: a vertical SE acts only vertically, a disk rounds corners.</p>
<p><b>Opening</b> (A ⊖ B) ⊕ B removes small objects and thin bridges, keeps size. <b>Closing</b> (A ⊕ B) ⊖ B fills small holes and gaps, keeps size. Both are idempotent.</p>
''')}
{paper("F22 A2(c)", "5 marks", '''
<p class="q">What is a structuring element? What are the effects of erosion and dilation? Explain briefly with applications.</p>
<p>A <b>structuring element</b> is a small binary image (template) of any shape and size (square, cross, disk, line) with a defined <b>origin</b>. It is moved over the image like a filter mask, and at each position the fit or hit test between the SE and the image decides the output pixel.</p>
<p>Effects and applications of erosion and dilation: as in the answer above (erosion: shrink, remove noise, separate objects; dilation: grow, fill holes, bridge gaps, repair broken text).</p>
''')}
<h3>Case studies (CLO3)</h3>
<p>Recipe: name the operation, give its equation, say what it does to this exact problem, and why the alternative would fail.</p>
{tbl(["the problem says…", "use", "why"], [
    ["small bright spots / specks on dark background", "opening", "erosion deletes specks smaller than B, dilation restores the real objects"],
    ["small dark holes / pepper inside a white object", "closing", "dilation fills the holes, erosion restores the outline"],
    ["broken characters, gaps in roads or lines", "dilation, or closing to keep the width", "the SE bridges the gap"],
    ["touching coins / cells to count", "erosion (repeated), then connected-component labeling", "erosion breaks the thin necks between objects"],
    ["remove small particles, keep big ones", "opening with B larger than the small particles", "small ones cannot contain B and vanish"],
    ["outline / boundary of objects", "β(A) = A − (A ⊖ B), or (A ⊕ B) − A", "difference of the object and its eroded / dilated version"],
    ["find corners, end points, a given shape", "hit-or-miss transform (deck 12)", "exact match of foreground and background pattern"]])}
{paper("SP25 Q3(c)", "3 + 3 + 3 + 1 marks", '''
<p class="q">A satellite image of the AUST campus road network has noise (small bright spots), gaps in roads and overlapping structures. (i) Which morphological operation first removes the small bright spots, and why? (ii) After noise removal the roads are fragmented with small gaps: which operation connects them, and how? (iii) Develop the most suitable operation to highlight road boundaries. (iv) Can highlighting boundaries help distinguish roads from the background terrain?</p>
<p><b>(i) Opening</b>, A ∘ B = (A ⊖ B) ⊕ B, with a small disk/square SE larger than the spots. The erosion deletes every bright spot that cannot contain B; the dilation then grows the roads back to their original width, so only the noise is removed. (Dilation first would enlarge the spots instead.)</p>
<p><b>(ii) Closing</b>, A • B = (A ⊕ B) ⊖ B, with an SE a bit longer than the gaps (a line SE along the road direction works best). The dilation joins the road fragments across each gap; the erosion shrinks the roads back to their width, but the filled gaps stay filled, so the network becomes connected without fattening.</p>
<p><b>(iii) Boundary extraction</b> β(A) = A − (A ⊖ B) with a 3×3 SE: erode the cleaned road image and subtract it from itself, leaving a one-pixel outline of every road. (Or (A ⊕ B) − A for the outer edge.)</p>
<p><b>(iv) Yes.</b> The boundaries outline the road shapes sharply, separating them from the surrounding terrain; they can be used to segment, measure and map the road network.</p>
''')}
{paper("F23 Q3(b)", "5 + 5 marks", '''
<p class="q">(i) Automated coin counting: coins are circular blobs, but some touch. Which morphological operations separate touching coins for accurate counting, and why? (ii) A microscope image has small insignificant particles and larger ones: which operations remove the small ones but keep the large ones? Explain mathematically, with applications.</p>
<p><b>(i)</b> Binarize the image, then apply <b>erosion</b> A ⊖ B = {z | (B)<sub>z</sub> ⊆ A} with a disk SE (repeated if needed). Touching coins are joined only by narrow necks; the disk cannot fit in a neck, so the necks disappear first and each coin becomes a separate, smaller blob. Then count the blobs with <b>connected-component labeling</b> (slides 43–44). Counting is not affected by the coins shrinking. (A dilation afterwards, i.e. an opening, would restore size, but could rejoin coins, so count after the erosion.)</p>
<p><b>(ii) Opening</b> with an SE (disk) a little larger than the insignificant particles: A ∘ B = (A ⊖ B) ⊕ B. Erosion removes every particle that cannot contain B, i.e. all the small ones; the larger particles survive as shrunken cores, and the dilation grows them back to almost their original shape and size. Applications: cleaning cell or particle images before counting, removing dust in industrial inspection, removing noise in scanned documents.</p>
''')}
{paper("SP24 Q3(a)ii", "4 marks", '''
<p class="q">An image is corrupted by salt-and-pepper noise in the object part only. Which morphological operation would you use to remove it? Explain the process.</p>
<p>Inside a white object, the visible noise is the <b>pepper</b>: small black dots, i.e. tiny holes in the foreground. Use <b>closing</b> A • B = (A ⊕ B) ⊖ B with a small (3×3) SE: the dilation fills each black dot because the SE touches white on all sides; the erosion then restores the object's outline. Any white specks left outside the object could then be removed with an opening (open–close filtering). The background is untouched because it has no noise.</p>
''')}
{paper("F22 A3(c)i · slide 43", "4 marks", '''
<p class="q">Coins image: which morphological operation can be used to count the coins? Explain the process.</p>
<p><b>Erosion</b> followed by connected-component labeling: binarize; erode with a disk to separate the touching coins (and remove small noise); label the connected components; the number of labels = number of coins.</p>
''')}
{paper("F21 B1(a) i–ii", "3 + 3 marks", '''
<p class="q">(i) A text image has broken characters: which morphological operation joins them? (ii) Define opening and closing mathematically, with applications.</p>
<p><b>(i) Dilation</b> with a small SE such as the 3×3 cross [0 1 0; 1 1 1; 0 1 0] (slide 59): any background pixel whose SE touches a character pixel becomes foreground, so the 1–2 pixel breaks are bridged and the characters become whole. A <b>closing</b> (dilation then erosion) joins the breaks the same way but returns the strokes to their original thickness.</p>
<p><b>(ii)</b> Opening A ∘ B = (A ⊖ B) ⊕ B: removes small noise and thin bridges (cleaning scanned documents, separating objects). Closing A • B = (A ⊕ B) ⊖ B: fills small holes and gaps (repairing broken text, filling reflections in a thresholded object).</p>
''')}
"""))

S.append(sec("traps", "Traps and one-minute sheet", "all", None, f"""
<ul class="traps">
<li>Erosion = <b>fit</b> (all SE pixels on 1). Dilation = <b>hit</b> (any SE pixel on 1). Don't swap them.</li>
<li>Opening = erode <b>first</b>. Closing = dilate <b>first</b>. Opening removes specks; closing removes holes.</li>
<li>For a non-symmetric SE, dilation uses the reflection B̂. Mark the origin on every SE you draw.</li>
<li>Pixels outside the image count as 0 (background) unless the question says otherwise.</li>
<li>Show the intermediate image (A ⊖ B or A ⊕ B) in opening and closing questions; it carries marks.</li>
</ul>
{tbl(["operation", "equation", "effect"], [
    ["erosion", "A ⊖ B = {z | (B)<sub>z</sub> ⊆ A}", "shrink, remove small objects, split joins"], ["dilation", "A ⊕ B = {z | (B̂)<sub>z</sub> ∩ A ≠ ∅}", "grow, fill holes, bridge gaps"],
    ["opening", "A ∘ B = (A ⊖ B) ⊕ B", "remove specks and thin bridges, keep size"], ["closing", "A • B = (A ⊕ B) ⊖ B", "fill holes and gaps, keep size"],
    ["boundary", "β(A) = A − (A ⊖ B)", "inner outline"], ["edge (outer)", "(A ⊕ B) − A", "ring outside the object"],
    ["duality", "(A ⊖ B)<sup>c</sup> = A<sup>c</sup> ⊕ B̂", "erosion via the background"]])}
"""))

toc = [("start", "Start"), ("fithit", "Fit & hit"), ("ero", "Erosion"), ("dil", "Dilation"), ("open", "Opening & closing"), ("bnd", "Boundary"),
       ("sets", "Set basics"), ("pq", "Numeric papers"), ("theory", "Theory & cases"), ("traps", "Traps")]
OUT.write_text(page("DIP Deck 11 Lesson", "CSE 4227 · Chapter 9 · Deck 11", "Morphology I, from zero",
                    "Erosion, dilation, opening, closing and boundaries in plain words, with every slide example and past question solved in answer-script form and a pixel-by-pixel simulator next to each.",
                    toc, S, extra=sim_assets()), encoding="utf-8")

# ---------------------------------------------------------------- self-check against data/answers.json and the slides
assert fh == [["A", "yes", "yes", "yes", "yes"], ["B", "no", "yes", "yes", "yes"], ["C", "no", "no", "yes", "no"]]
assert e1d == [0, 0, 0, 0, 1, 0, 0, 0] and d1d == [1, 0, 1, 1, 1, 1, 1, 1]
assert OPNo == P([".....#..", "....###.", ".....#..", "........", "..#.....", ".###....", "..#.....", "........"])
assert CLSc == P(["........", "....###.", "....###.", "...##...", ".###....", ".###....", ".###....", "........"])
assert fd == [[0, 0, 1, 1, 1, 1], [0, 1, 1, 1, 1, 1], [0, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 0, 0]]
assert fce == [[0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0]]
assert fo == [[0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 0, 0, 0, 0]]
assert fc == [[0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 1, 0], [0, 1, 1, 1, 1, 0], [0, 1, 1, 1, 0, 0], [0, 0, 0, 0, 0, 0]]
assert dilate(X, B23, o23) == Y and erode(Y, B23, o23) == X
assert minus(A25, A25e) == P(["......", ".####.", ".#..#.", ".#..#.", ".####.", "......"])
assert tho[6] == [1, 1, 0, 0, 0, 0, 0, 0, 1, 1] and tho[0] == th[0]
print(OUT, OUT.stat().st_size, "EX1e", sorted(ones(EX1e)), "CLSd", len(ones(CLSd)))
