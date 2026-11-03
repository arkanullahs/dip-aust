"""Builds deck12_lesson.html: morphology part II (hit-or-miss, thinning, thickening). All grids computed here."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from kit import *

OUT = pathlib.Path(__file__).with_name("deck12_lesson.html")
X_ = None


def P(rows):
    return [[1 if ch in "#1" else 0 for ch in r] for r in rows]


def px(A, r, c):
    return A[r][c] if 0 <= r < len(A) and 0 <= c < len(A[0]) else 0


def hmt(A, se):
    """3×3 SE, centre origin: 1 must be object, 0 must be background, None don't care; outside = background."""
    return [[1 if all(se[i][j] is None or px(A, r + i - 1, c + j - 1) == se[i][j] for i in range(3) for j in range(3)) else 0
             for c in range(len(A[0]))] for r in range(len(A))]


def union(*Ms):
    return [[1 if any(M[r][c] for M in Ms) else 0 for c in range(len(Ms[0][0]))] for r in range(len(Ms[0]))]


def ones(M):
    return sorted((r, c) for r, row in enumerate(M) for c, v in enumerate(row) if v)


def bm(M, cap="", mark=None):
    return mat(M, cap, hi=set(ones(M)) if mark is None else mark, small=True)


def se_grid(se, cap):
    return mat([["×" if v is None else v for v in row] for row in se], cap, hi={(i, j) for i in range(3) for j in range(3) if se[i][j] == 1}, ctr=(1, 1), small=True)


def js(se):
    return [[v for v in row] for row in se]


def hsim(A, ses, cap):
    return sim({"type": "morph", "A": A, "ops": ["hmt"], "ses": [{"name": n, "se": js(s), "origin": [1, 1]} for n, s in ses]}, cap)


def hmt_answer(A, ses, what):
    o, res = [], []
    for name, se in ses:
        R = hmt(A, se)
        res.append(R)
        o.append(mats(se_grid(se, name), bm(R, f"A ⊛ {name.split(' ')[0]}: {len(ones(R))} found {', '.join(map(str, ones(R)))}")))
    fin = union(*res)
    o.append(f"<p><b>Combine</b> with OR: a pixel is a {what} if any SE marked it.</p>")
    o.append(mats(bm(A, "input A"), bm(fin, f"final: {len(ones(fin))} {what}s")))
    return "".join(o), fin, res


S = []

# ================================================================ 1. review + HMT idea
S.append(sec("start", "Start here: review and the hit-or-miss idea", "3–9", EXAM, f"""
<p><b>Slide 3. Review of part I:</b></p>
{tbl(["operation", "equation"], [["erosion", "A ⊖ B = {z | (B)<sub>z</sub> ⊆ A}"], ["dilation", "A ⊕ B = {z | (B̂)<sub>z</sub> ∩ A ≠ ∅}"],
     ["duality", "(A ⊖ B)<sup>c</sup> = A<sup>c</sup> ⊕ B̂, (A ⊕ B)<sup>c</sup> = A<sup>c</sup> ⊖ B̂"], ["opening", "A ∘ B = (A ⊖ B) ⊕ B"], ["closing", "A • B = (A ⊕ B) ⊖ B"]])}
{idea("Erosion only asks \"are these pixels white?\". The hit-or-miss transform asks a stricter question: \"are <b>these</b> pixels white <b>and those</b> pixels black?\". That lets it find an exact pattern, such as a corner or the end of a line.")}
<p><b>Slides 4–5.</b> The <b>hit-or-miss transform (HMT)</b> is a powerful tool used to <b>detect exact shapes or patterns in binary images</b>: a pattern-matching morphological operator and very simple object recognition. It is used to look for particular patterns of <b>foreground and background</b> pixels.</p>
<p>A hit-or-miss (composite) SE contains three kinds of cells: <b>1</b> means foreground, <b>0</b> means background, and <b>× (NaN)</b> means "I don't care" / any pixel.</p>
<p><b>Slide 6.</b> If the foreground and background pixels of the SE <b>exactly match</b> the foreground and background pixels of the image, the pixel under the origin of the SE is set to the foreground colour; otherwise to background.</p>
{formula("A ⊛ B: g(x,y) = 1 if every 1 of B lies on a 1 of A and every 0 of B lies on a 0 of A (× ignored); else 0")}
<p><b>Slide 7.</b> Watch out: we actually look for <b>fits</b>, but call them <b>hits</b> when talking about the hit-or-miss transform. Whenever there is a "hit", we mark where the centre of shape B was on image A.</p>
<p><b>Slides 8–9.</b> So far the 0s of an SE were treated as don't cares (we focused on the 1s only). The <b>extended / composite SE</b> distinguishes 0s from don't cares: for a fit, the 0s of the SE must also match 0s of the underlying image.</p>
{mats(se_grid([[None, 1, None], [1, 1, 1], [None, 1, None]], "ordinary SE: only 1s matter"), se_grid([[1, 1, 1], [None, 0, None], [None, 0, None]], "composite SE: 1s, 0s and ×"))}
"""))

# ================================================================ 2. procedure example
I11 = P([".........", "..###....", "....####.", ".#..#####", ".######.#", "..#####.#"])
T = [[1, 1, 1], [None, 0, None], [None, 0, None]]
I11h = hmt(I11, T)
pat = [[0, 0, 0], [0, 1, 0], [None, 0, None]]
S.append(sec("proc", "Hit-or-miss procedure, step by step", "10–14", EXAM, f"""
<p><b>Slide 10.</b> The SE has pixels with three values: 0, the corresponding pixel must be 0; 1, it must be 1; don't care. An input neighbourhood matches only if every 0 and every 1 agree; one wrong pixel (a 1 where the SE wants 0) makes it false.</p>
{paper("Slides 11–14 · procedure with an extended SE", "worked", f'''
<p>Slide the SE [1 1 1; × 0 ×; × 0 ×] over the image like an erosion and look for exact fits: three 1s in the row above, a 0 at the centre, a 0 below.</p>
{mats(bm(I11, "input image"), se_grid(T, "SE (origin = centre)"), bm(I11h, f"output: {len(ones(I11h))} fits at {', '.join(map(str, ones(I11h)))}"))}
<p>At (2,3): the row above is 1 1 1, the centre is 0 and the pixel below is 0, so it is a fit. Same at (4,7). Every other position fails somewhere.</p>
<p><b>Slide 14. What we actually did:</b> we searched for the pattern, i.e. we actually performed an <b>erosion</b>, but with both the foreground and the background part of the SE: A ⊛ B = (A ⊖ B<sub>1</sub>) ∩ (A<sup>c</sup> ⊖ B<sub>2</sub>), where B<sub>1</sub> is the set of 1s and B<sub>2</sub> the set of 0s.</p>
''')}
{hsim(I11, [("SE", T)], "the slide 11–14 search, every position: each 1 and 0 of the SE is compared with the image.")}
"""))

# ================================================================ 3. corners
CORN = [("B1 (up + right: bottom-left corner)", [[None, 1, None], [0, 1, 1], [0, 0, None]]),
        ("B2 (up + left: bottom-right corner)", [[None, 1, None], [1, 1, 0], [None, 0, 0]]),
        ("B3 (down + left: top-right corner)", [[None, 0, 0], [1, 1, 0], [None, 1, None]]),
        ("B4 (down + right: top-left corner)", [[0, 0, None], [0, 1, 1], [None, 1, None]])]
CS = P([".............", ".#####.#####.", ".#...#.#...#.", ".#.....#.....", ".#.....#####.", ".#.........#.", ".#...#.#...#.", ".#####.#####."])
csA, csF, csR = hmt_answer(CS, CORN, "corner")
S.append(sec("corner", "Corner detection with hit-or-miss", "15–17", EXAM, f"""
<p><b>Slides 15–16.</b> Use <b>structuring elements representing the four corners</b>. Apply each SE, then use the <b>OR</b> operation to combine the four results.</p>
<p>How to design a corner SE: the centre is 1 (the corner pixel itself). The two arms of the corner are 1 (e.g. the pixel above and the pixel to the right). The two opposite sides and the diagonal between them are 0 (background). The other cells are × (don't care). Rotating it by 90° gives the other three corners.</p>
{mats(*[se_grid(se, n) for n, se in CORN])}
<p><b>Slide 17. More applications:</b> any shape detection ("T", "L", …); corner detection (rotated SEs); endpoint detection (line terminals); skeletonization and thinning; pattern recognition of predefined shapes.</p>
{paper("F23 Q2(e)", "3 + 3 marks", f'''
<p class="q">Apply the hit-and-miss transform to detect the corners of the binary image A ("CS"). (i) Design four SEs for detecting the four different corners and explain them. (ii) Using your SEs, extract all corners of A; show the output for each SE and the combined final output.</p>
<p><b>(i)</b> Each SE is 3×3 with the origin at the centre: 1 = must be object, 0 = must be background, × = don't care. The centre and the two arm pixels are 1; the two opposite neighbours and the cell between them are 0; the rest are ×. B1 finds bottom-left corners (arms going up and right), B2 bottom-right, B3 top-right, B4 top-left. Outside the image counts as background.</p>
<p><b>(ii)</b></p>{csA}
''')}
{hsim(CS, CORN, "F23 CS image: each corner SE in turn, then the OR. Use “Next phase” to move to the next SE.")}
{paper("F21 B1(a)iii", "2 marks", f'''
<p class="q">Design four hit-or-miss SEs for locating the four corners of an object.</p>
{mats(*[se_grid(se, n) for n, se in CORN])}
<p>1 = object, 0 = background, × = don't care, origin at the centre. Apply each one with A ⊛ B<sub>i</sub> and OR the four results.</p>
''')}
"""))

# ================================================================ 4. endpoints
END = [("E1 (arm below / open above)", [[None, None, None], [0, 1, 0], [None, 0, None]]),
       ("E2 (open below)", [[None, 0, None], [0, 1, 0], [None, None, None]]),
       ("E3 (open left)", [[None, 0, None], [None, 1, 0], [None, 0, None]]),
       ("E4 (open right)", [[None, 0, None], [0, 1, None], [None, 0, None]])]
END = [("E1 (open above)", [[None, None, None], [0, 1, 0], [None, 0, None]])] + END[1:]
F22 = P(["...#..#..#...", "...#...#####.", "...#.#...#...", ".#.###...#...", ".........###.", ".#######.....", "............."])
f22A, f22F, f22R = hmt_answer(F22, END, "4-connected endpoint")
CSE = P(["........................", "####.####.####...#.#.#.#", "#..#.#....#......#.#.#.#", "#....####.###..#.###.###", "#..#....#.#........#...#", "####.####.####.....#...#", "........................"])
cseA, cseF, cseR = hmt_answer(CSE, END, "end point")
S.append(sec("end", "End points with hit-or-miss", "18–19, 30–32", EXAM, f"""
<p><b>Slides 30–32.</b> Find the <b>4-connected endpoints</b> of a binary image: the pixels where a line ends. An endpoint has exactly one object neighbour among its 4 neighbours. So each SE has the centre 1, three of the 4-neighbours 0, and the fourth (the direction the line continues) × don't care; the diagonals are ×. Four rotations cover lines ending in the four directions.</p>
{mats(*[se_grid(se, n) for n, se in END])}
<p>An isolated single pixel fits all four SEs, so it is also counted as an endpoint.</p>
{paper("Slides 30–32 · F22 A3(c) ii–iii", "2 + 2 marks", f'''
<p class="q">(ii) Design hit-or-miss SEs for locating the 4-connected endpoints of an image. (iii) Locate all 4-connected endpoints of the given binary image with them; draw each result and the combined one.</p>
<p><b>(ii)</b> The four SEs above: centre 1, three 4-neighbours 0, one 4-neighbour × (the arm), diagonals ×.</p>
<p><b>(iii)</b></p>{f22A}
''')}
{hsim(F22, END, "slide 30–32 / F22 image, each endpoint SE then the OR.")}
{paper("SP23 Q3(c)", "1 + 4 + 2 + 1 marks", f'''
<p class="q">Binary image "CSE-44". (i) Which morphological technique locates all end points? (ii) Design four SEs for four different end points. (iii) Extract all end points with your SEs and explain. (iv) How many end points are in the final output?</p>
<p><b>(i)</b> The <b>hit-or-miss transform</b> A ⊛ B, with one SE per end direction, combined by OR.</p>
<p><b>(ii)</b> The four endpoint SEs above (centre 1, three 4-neighbours 0, the arm ×).</p>
<p><b>(iii)</b></p>{cseA}
<p><b>(iv)</b> <b>{len(ones(cseF))}</b> end points in the final output.</p>
''')}
{hsim(CSE, END, "SP23 CSE-44, each SE then the OR.")}
"""))

# ================================================================ 5. algorithms, thinning, thickening
bA = P(["........", ".######.", ".######.", ".######.", "........"])
S.append(sec("thin", "Boundary, thinning and thickening", "18–29", LIKELY, f"""
<p><b>Slide 18. Some basic morphological algorithms:</b> boundary extraction, region filling; also extraction of connected components, thinning/thickening, skeletons.</p>
<p><b>Slide 19. Boundary extraction:</b> extracting the boundary (outline) of an object is often extremely useful: <b>β(A) = A − (A ⊖ B)</b> (worked and simulated on the deck 11 page).</p>
<h3>Thinning (slides 20–26)</h3>
<p>Used to <b>remove selected foreground pixels</b> from binary images. After edge detection, lines are often thicker than one pixel; thinning makes them one pixel wide.</p>
{formula("A ⊗ B = A − (A ⊛ B) = A ∩ (A ⊛ B)<sup>c</sup>")}
<p>Symmetric thinning uses a sequence of SEs {{B}} = {{B<sup>1</sup>, B<sup>2</sup>, …, B<sup>n</sup>}}, where B<sup>i</sup> is a rotated version of B<sup>i−1</sup>: A ⊗ {{B}} = ((…((A ⊗ B<sup>1</sup>) ⊗ B<sup>2</sup>)…) ⊗ B<sup>n</sup>). If the foreground and background fit the SE exactly, the pixel at the origin is <b>set to 0</b>. The SE value at the origin is 1 or don't care.</p>
<p>Figure 9.21: the set A is thinned with B<sup>1</sup>, then B<sup>2</sup> … B<sup>8</sup>, and the whole sequence is repeated until no more changes occur (convergence); finally the result is converted to m-connectivity.</p>
<h3>Thickening (slides 27–29)</h3>
<p>Used to <b>grow selected regions of foreground pixels</b>, e.g. to approximate the convex hull. It is the morphological dual of thinning:</p>
{formula("A ⊙ B = A ∪ (A ⊛ B), &nbsp;&nbsp; A ⊙ {{B}} = ((…((A ⊙ B<sup>1</sup>) ⊙ B<sup>2</sup>)…) ⊙ B<sup>n</sup>)")}
<p>If the foreground and background match the SE exactly, the pixel at the origin is <b>set to 1</b>. The SE value at the origin is 0 or don't care.</p>
<p><b>Slide 29. A separate thickening algorithm:</b> thin the <b>background</b> instead (thin A<sup>c</sup>), then <b>complement</b> the result; remove any disconnected points.</p>
{tbl(["", "thinning ⊗", "thickening ⊙"], [["equation", "A − (A ⊛ B)", "A ∪ (A ⊛ B)"], ["on a match, the origin pixel becomes", "0 (removed)", "1 (added)"],
     ["SE value at origin", "1 or ×", "0 or ×"], ["use", "make lines 1 pixel wide, skeletons", "grow regions, convex hull"]])}
"""))

S.append(sec("traps", "Traps and one-minute sheet", "all", None, f"""
<ul class="traps">
<li>Hit-or-miss needs <b>both</b> parts to match: 1s on object and 0s on background. × cells are ignored.</li>
<li>Draw each SE with its origin, label each cell 1 / 0 / ×, and show one output grid per SE plus the OR. That's where the marks are.</li>
<li>Pixels outside the image count as background, so an object touching the border can still give a corner or endpoint there.</li>
<li>An isolated single pixel is an endpoint for every endpoint SE.</li>
<li>Thinning subtracts the HMT result; thickening adds it.</li>
</ul>
{tbl(["what", "formula"], [["hit-or-miss", "A ⊛ B = (A ⊖ B<sub>1</sub>) ∩ (A<sup>c</sup> ⊖ B<sub>2</sub>)"], ["thinning", "A ⊗ B = A − (A ⊛ B)"], ["thickening", "A ⊙ B = A ∪ (A ⊛ B)"], ["boundary", "β(A) = A − (A ⊖ B)"]])}
"""))

toc = [("start", "Start"), ("proc", "HMT procedure"), ("corner", "Corners"), ("end", "End points"), ("thin", "Thinning & thickening"), ("traps", "Traps")]
OUT.write_text(page("DIP Deck 12 Lesson", "CSE 4227 · Chapter 9 · Deck 12", "Morphology II: hit-or-miss, thinning, thickening",
                    "The hit-or-miss transform in plain words, every corner and end-point past question solved in answer-script form, and a pixel-by-pixel simulator for each SE.",
                    toc, S, extra=sim_assets()), encoding="utf-8")

# ---------------------------------------------------------------- self-check against data/answers.json and the slides
assert ones(I11h) == [(2, 3), (4, 7)]
assert [len(ones(R)) for R in csR] == [3, 2, 3, 2] and ones(csR[0]) == [(4, 7), (7, 1), (7, 7)]
assert [len(ones(R)) for R in f22R] == [2, 5, 5, 4] and ones(f22R[1]) == [(0, 3), (0, 6), (0, 9), (2, 5), (3, 1)]
assert len(ones(cseR[0])) == 4 and len(ones(cseR[1])) == 6
print(OUT, OUT.stat().st_size, "CS corners", len(ones(csF)), "F22 endpoints", len(ones(f22F)), ones(f22F), "CSE endpoints", len(ones(cseF)), [len(ones(R)) for R in cseR])
