"""Builds deck07_lesson.html: sharpening spatial filtering lesson. All numbers computed here."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from kit import *

OUT = pathlib.Path(__file__).with_name("deck07_lesson.html")

LAP_P = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
LAP_N = [[0, -1, 0], [-1, 4, -1], [0, -1, 0]]
LAP_P8 = [[1, 1, 1], [1, -8, 1], [1, 1, 1]]
LAP_N8 = [[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]]
COMP4 = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]
COMP8 = [[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]
SOB_Y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
SOB_X = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
PRE_Y = [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]
PRE_X = [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]


def splot(series, lo, hi, ticks, caption, w=360, h=210, xlab="position x"):
    """Line plot that can go below zero: values are shifted by -lo internally."""
    n = max(len(s["v"]) for s in series) - 1
    curves = [{"pts": [(i, v - lo) for i, v in enumerate(s["v"])], "cls": s["cls"], **({"label": s["label"], "at": (s["at"][0], s["at"][1] - lo)} if "label" in s else {})} for s in series]
    pts = [(i, v - lo, "", "c3p" if s["cls"] == "c3" else "") for s in series if s.get("dots") for i, v in enumerate(s["v"])]
    return plot(n, hi - lo, curves=curves, points=pts, xticks=list(range(0, n + 1, 4)), yticks=[(t - lo, str(t)) for t in ticks],
                xlabel=xlab, ylabel="value", w=w, h=h, caption=caption)


S = []

# ================================================================ 1. idea
S.append(sec("start", "Start here: what sharpening is for", "3–6", EXAM, f"""
{idea("Smoothing (deck 06) averages neighbours, so differences between pixels shrink and the image blurs. Sharpening does the opposite: it measures <b>how fast the brightness changes</b> and boosts those changes. Edges and fine details are places where brightness changes fast, so they get stronger.")}
<p><b>Slide 3.</b> Smoothing filters remove fine details to blur the image. <b>Sharpening spatial filters seek to highlight fine details</b>:</p>
<ul><li>remove <b>blurring</b> from images;</li><li>highlight <b>edges</b>;</li><li>useful for emphasizing <b>transitions in image intensity</b>.</li></ul>
<p><b>Slide 4. Applications:</b> photo enhancement, medical image visualization, industrial defect detection, electronic printing, autonomous guidance in military systems.</p>
<p><b>Slide 5. Image derivatives</b> give information about spatial variations in an image by calculating the <b>rate of change of pixel intensity</b>. They are fundamental to image analysis, enhancement and feature extraction.</p>
<p><b>Slide 6.</b> Sharpening filters are based on <b>first- and second-order derivatives</b>. Differentiation measures the rate of change of a function, so sharpening is based on <b>spatial differentiation</b>. For a digital image, derivatives are defined in terms of <b>differences</b> between neighbouring pixels.</p>
{paper("SP23 Q2(f)i · SP25 Q1(a) first part", "2 marks", '''
<p class="q">What are the objectives of sharpening spatial filters?</p>
<p>Sharpening spatial filters highlight fine detail in an image. Their objectives are: (1) to remove blurring from images; (2) to highlight edges; (3) to emphasize transitions (sudden changes) in image intensity. They work by spatial differentiation (first- or second-order derivatives defined by differences), which responds strongly where intensity changes and gives zero in flat areas. Uses: photo enhancement, medical visualization, industrial defect detection, electronic printing, military guidance.</p>
''')}
"""))

# ================================================================ 2. derivatives
f = [5, 5, 4, 3, 2, 1, 0, 0, 0, 6, 0, 0, 0, 0, 1, 3, 1, 0, 0, 0, 0, 7, 7, 7, 7]
d1 = [None] + [f[x + 1] - f[x] for x in range(1, len(f) - 1)] + [None]
d2 = [None] + [f[x + 1] + f[x - 1] - 2 * f[x] for x in range(1, len(f) - 1)] + [None]
cell = lambda v: "" if v is None else v
strip = tbl(["x"] + list(range(len(f))), [["f(x)"] + f, ["1st: f(x+1) − f(x)"] + [cell(v) for v in d1], ["2nd: f(x+1) + f(x−1) − 2f(x)"] + [cell(v) for v in d2]], "narrow")
fplot = splot([{"v": f, "cls": "c5", "dots": True}], -1, 8, [0, 3, 6, 7], "Image strip A–B: ramp (x 0–6), isolated point (x 9), thin line (x 14–16), flat segment, step (x 21).", xlab="x")
d1p = splot([{"v": [0] + d1[1:-1] + [0], "cls": "c1", "dots": True}], -7, 8, [-6, 0, 6], "1st derivative: nonzero along the entire ramp, zero in flat areas, a single response at the step.", xlab="x")
d2p = splot([{"v": [0] + d2[1:-1] + [0], "cls": "c3", "dots": True}], -13, 8, [-12, -6, 0, 6], "2nd derivative: nonzero only at the onset and end of the ramp, a double response (+, −) at the point and the step.", xlab="x")
S.append(sec("deriv", "First and second derivatives", "7–18", EXAM, f"""
{idea("The 1st derivative asks: how much does the brightness change from this pixel to the next? The 2nd derivative asks: is that change itself changing, i.e. is the slope bending? On a constant slope (a ramp), the 1st derivative is constant and the 2nd is zero, except where the ramp starts and stops.")}
<h3>1st derivative (slide 7)</h3>
<p>The difference of two consecutive pixels:</p>
{formula("∂f/∂x = f(x+1) − f(x) &nbsp;(forward) &nbsp;·&nbsp; f(x) − f(x−1) &nbsp;(backward) &nbsp;·&nbsp; f(x+1) − f(x−1) &nbsp;(central)")}
<p>It is just the difference between subsequent values, and it measures the rate of change of the function.</p>
<p><b>Slides 10–12, as 2-D kernels</b> (horizontal one row, vertical one column):</p>
{tbl(["type", "formula (x direction)", "horizontal kernel", "formula (y direction)", "vertical kernel"],
     [["forward", "f(x+1,y) − f(x,y)", "[0 −1 1]", "f(x,y+1) − f(x,y)", "[0; −1; 1]"], ["backward", "f(x,y) − f(x−1,y)", "[−1 1 0]", "f(x,y) − f(x,y−1)", "[−1; 1; 0]"],
      ["central", "f(x+1,y) − f(x−1,y)", "[−1 0 1]", "f(x,y+1) − f(x,y−1)", "[−1; 0; 1]"]])}
<h3>2nd derivative (slide 13)</h3>
<p>It takes into account the values both before and after the current one: {{f(x+1) − f(x)}} − {{f(x) − f(x−1)}}.</p>
{formula("∂²f/∂x² = f(x+1) + f(x−1) − 2f(x) &nbsp;&nbsp; or &nbsp;&nbsp; 2f(x) − f(x−1) − f(x+1)")}
<p><b>Slides 15–16, as kernels:</b> forward (positive) [1 −2 1] (and vertically [1; −2; 1]); backward (negative) [−1 2 −1] (and [−1; 2; −1]).</p>
{paper("Slides 8–9, 14 · the image strip", "worked", f'''
<p>Gray levels along the line A–B of the slide image, with both derivatives worked out (forward 1st difference, central 2nd difference):</p>
{strip}
{fplot}
{figs(d1p, d2p)}
<p>Example cells: at x = 9 (the isolated point 6), the 1st derivative is f(10) − f(9) = 0 − 6 = −6 and the 2nd derivative is f(10) + f(8) − 2f(9) = 0 + 0 − 12 = −12.</p>
''')}
{sim({"type": "oned", "sig": f, "modes": ["d1", "d2"]}, "both derivatives along the whole strip, one position at a time. Switch the Operation menu for the 2nd derivative.")}
{paper("SP24 Q1(b)", "3 + 2 marks", '''
<p class="q">Define the first-order and second-order discrete derivatives of a 1-D digital function f(x). What relation can be obtained between first- and second-order derivatives for an edge that is a ramp of constant slope?</p>
<p><b>First-order derivative</b> (difference of consecutive pixels): ∂f/∂x = f(x+1) − f(x).</p>
<p><b>Second-order derivative</b> (difference of differences): ∂²f/∂x² = [f(x+1) − f(x)] − [f(x) − f(x−1)] = f(x+1) + f(x−1) − 2f(x).</p>
<p><b>Relation along a ramp of constant slope</b> (strip values 5 5 4 3 2 1 0 0):</p>
<ul><li>The 1st derivative is <b>nonzero along the entire ramp</b> (−1 at every step of the ramp) and zero in flat areas, so it produces <b>thick edges</b>.</li>
<li>The 2nd derivative is <b>zero along the ramp</b> and nonzero only at its <b>onset and end</b>, with <b>opposite signs</b> (−1 at the start, +1 at the end). So it produces a <b>double edge</b> one pixel thick, separated by zeros, and the sign change (zero crossing) marks the edge location.</li>
<li>The 2nd derivative also responds much more strongly to fine detail such as an isolated point (6, −12, 6 against −6 for the 1st), which is why it's preferred for sharpening.</li></ul>
<p><i>[Draw the strip and the two derivative graphs above.]</i></p>
''')}
<p><b>Slide 17.</b> Two families of sharpening filters: (1) <b>Laplacian</b>: uses the 2nd derivative; (2) <b>Sobel / Prewitt</b> (gradient operators): use the 1st derivative.</p>
<p><b>Slide 18.</b> The 2nd derivative is more useful for image enhancement than the 1st derivative: <b>stronger response to fine detail</b>. The first sharpening filter is the <b>Laplacian</b>.</p>
"""))

# ================================================================ 3. Laplacian
S.append(sec("lap", "The Laplacian: derivation and the four masks", "19–22", EXAM, f"""
{idea("The Laplacian is the 2nd derivative done in both directions at once (x and y) and added together. The result is one 3×3 mask: the centre pixel compared against its 4 (or 8) neighbours.")}
{paper("SP25 Q1(a)", "4 marks", f'''
<p class="q">What are the objectives of sharpening spatial filters? Derive the Laplacian operator using image derivatives and draw four Laplacian masks.</p>
<p><b>Objectives:</b> highlight fine detail, remove blurring, highlight edges and emphasize intensity transitions (see above).</p>
<p><b>Derivation.</b> The Laplacian of f(x,y) is the sum of the second derivatives in x and y:</p>
{formula("∇²f = ∂²f/∂x² + ∂²f/∂y²")}
<p>Using the forward 2nd differences:</p>
<p>∂²f/∂x² = f(x+1,y) + f(x−1,y) − 2f(x,y)</p>
<p>∂²f/∂y² = f(x,y+1) + f(x,y−1) − 2f(x,y)</p>
<p>Adding:</p>
{formula("∇²f = f(x+1,y) + f(x−1,y) + f(x,y+1) + f(x,y−1) − 4f(x,y)")}
<p>As masks: the horizontal [1 −2 1] plus the vertical [1; −2; 1] give</p>
{mats(mat([[0, 0, 0], [1, -2, 1], [0, 0, 0]], "x part"), mat([[0, 1, 0], [0, -2, 0], [0, 1, 0]], "y part"), mat(LAP_P, "= positive Laplacian"))}
<p>This is the <b>positive Laplacian</b>, from forward derivatives. With the backward form 2f(x) − f(x−1) − f(x+1) we get ∇²f = 4f(x,y) − f(x−1,y) − f(x+1,y) − f(x,y−1) − f(x,y+1), the <b>negative Laplacian</b>:</p>
{mat(LAP_N, "negative Laplacian")}
<p><b>Four Laplacian masks</b> (Figure 3.39): two 4-neighbour and two that include the diagonal neighbours:</p>
{mats(mat(LAP_P, "(a) 4-nbr, centre −4"), mat(LAP_P8, "(b) 8-nbr, centre −8"), mat(LAP_N, "(c) 4-nbr, centre 4"), mat(LAP_N8, "(d) 8-nbr, centre 8"))}
<p>In all cases <b>the sum of the values in the filter is zero</b>, so a flat area gives 0 and only changes produce a response.</p>
''')}
{sim({"type": "filter", "images": ["i26"], "filters": ["lappos", "lapneg", "lappos8", "lapneg8"], "pad": "zero", "start": [2, 2]}, "the four Laplacian masks on the slide 26 image. Notice the positive and negative masks give the same number with opposite sign.")}
<p><b>Slide 22.</b> Applying the Laplacian to an image gives a new image that <b>highlights edges and other discontinuities</b> (moon picture). Flat regions become 0 (gray when scaled for display).</p>
"""))

# ================================================================ 4. Laplacian enhancement
I26 = [[153, 157, 156, 153, 155], [159, 156, 158, 156, 159], [155, 158, 154, 156, 160], [154, 157, 158, 160, 160], [157, 157, 157, 156, 155]]
lap26 = corr(I26, LAP_N, 2, 2)
comp26 = corr(I26, COMP4, 2, 2)
avg3 = [[2, 5, 8], [5, 1, 3], [4, 7, 2]]
S.append(sec("lapenh", "Sharpening with the Laplacian", "23–30", EXAM, f"""
<p><b>Slide 23.</b> The result of Laplacian filtering is <b>not an enhanced image</b>; it is an edge map. To get the enhanced image, the Laplacian image is added to or subtracted from the original, depending on the sign of the mask centre w<sub>5</sub>:</p>
{cases("g(x,y)", [("f(x,y) − ∇²f", "if w<sub>5</sub> &lt; 0 (positive Laplacian, centre −4)"), ("f(x,y) + ∇²f", "if w<sub>5</sub> &gt; 0 (negative Laplacian, centre +4)")])}
<p>Rule of thumb: the sign is chosen so that the centre pixel always ends up with a <b>positive</b> weight. Edges and fine detail are then much more obvious in the final sharpened image (slide 24).</p>
{paper("Slide 26 · negative Laplacian on the pixel 154", "worked", f'''
{show_window(I26, 2, 2, "image; shaded = window, outlined = pixel 154")}
<p><b>Step 1, filter:</b> negative Laplacian [0 −1 0; −1 4 −1; 0 −1 0] at 154. Up = 158, left = 158, right = 156, down = 158.</p>
<p>∇²f = 4×154 − 158 − 158 − 156 − 158 = 616 − 630 = <b>{lap26}</b>. This is the filtered value.</p>
<p><b>Step 2, sharpen:</b> the mask centre is positive, so g = f + ∇²f = 154 + ({lap26}) = <b>{154 + lap26}</b>.</p>
<p>The pixel was darker than its neighbours (154 against about 157) and became even darker (140), so the local contrast went up.</p>
''')}
{sim({"type": "filter", "images": ["i26"], "filters": ["sharp_neg", "sharp_pos", "comp4", "comp8"], "pad": "zero", "start": [2, 2]}, "slide 26 sharpening: the two-step way (Laplacian, then add or subtract) and the one-pass masks. All give 140 at the 154.")}
<h3>One pass instead of two (slides 27–30)</h3>
<p>The two steps can be combined into a <b>single filtering operation</b>:</p>
{formula("g = f − ∇²f = f − [f(x+1,y) + f(x−1,y) + f(x,y+1) + f(x,y−1) − 4f(x,y)] = 5f(x,y) − f(x+1,y) − f(x−1,y) − f(x,y+1) − f(x,y−1)")}
{mats(mat(COMP4, "single-pass mask (4-nbr)"), mat(COMP8, "single-pass variant (8-nbr)"))}
<p>Check on slide 26: 5×154 − 158 − 158 − 156 − 158 = 770 − 630 = <b>{comp26}</b>, the same as the two-step answer.</p>
<p>The 8-neighbour variant comes the same way from [1 1 1; 1 −8 1; 1 1 1]: g = f − ∇²f gives centre 1 + 8 = 9 and −1 everywhere else.</p>
{paper("SP23 Q3(f)iii", "2 marks", f'''
<p class="q">Derive a positive Laplacian filter mask that enhances an image in a single filtering operation.</p>
<p>Positive Laplacian: ∇²f = f(x+1,y) + f(x−1,y) + f(x,y+1) + f(x,y−1) − 4f(x,y), mask [0 1 0; 1 −4 1; 0 1 0]. Its centre is negative (w<sub>5</sub> = −4), so the enhanced image is g = f − ∇²f:</p>
<p>g(x,y) = f(x,y) − [f(x+1,y) + f(x−1,y) + f(x,y+1) + f(x,y−1) − 4f(x,y)]</p>
<p>= 5f(x,y) − f(x+1,y) − f(x−1,y) − f(x,y+1) − f(x,y−1)</p>
{mat(COMP4, "single-pass enhancement mask")}
<p>Convolving the image with this one mask gives the sharpened image directly. Its coefficients add to 1, so flat areas keep their brightness.</p>
''')}
"""))

# ================================================================ 5. gradient
S.append(sec("grad", "Gradient operators: Roberts, Sobel, Prewitt", "31–37", EXAM, f"""
{idea("The gradient uses the 1st derivative in two directions: g<sub>x</sub> (change going down the rows) and g<sub>y</sub> (change going across the columns). Its size M says how strong the edge is. In practice you add the two absolute values instead of taking a square root.")}
<p><b>Slide 31.</b> The gradient of f at (x,y) is the vector</p>
{formula("∇f = grad(f) = [g<sub>x</sub>, g<sub>y</sub>] = [∂f/∂x, ∂f/∂y]")}
{formula("M(x,y) = mag(∇f) = √(g<sub>x</sub>² + g<sub>y</sub>²) ≈ |g<sub>x</sub>| + |g<sub>y</sub>|")}
<p><b>Slide 32.</b> Ways to compute it: 1-D forward differences, Roberts cross-gradient, 1-D central differences, Prewitt, Sobel.</p>
<p>Pixel names in a 3×3 window:</p>
{mat([["z1", "z2", "z3"], ["z4", "z5", "z6"], ["z7", "z8", "z9"]], "pixel arrangement", ctr=(1, 1))}
<p><b>Slide 33. 1-D forward differences:</b> M(x,y) ≈ |z<sub>8</sub> − z<sub>5</sub>| + |z<sub>6</sub> − z<sub>5</sub>|.</p>
<p><b>Slide 34. Roberts cross-gradient:</b> G<sub>x</sub> = z<sub>9</sub> − z<sub>5</sub>, G<sub>y</sub> = z<sub>8</sub> − z<sub>6</sub>; ∇f ≈ |z<sub>9</sub> − z<sub>5</sub>| + |z<sub>8</sub> − z<sub>6</sub>|. They are the simplest approximations, using 2×2 masks:</p>
{mats(mat([[-1, 0], [0, 1]], "Roberts G<sub>x</sub>"), mat([[0, -1], [1, 0]], "Roberts G<sub>y</sub>"))}
<p><b>Slide 35. Sobel:</b> provides differencing and detects vertical and horizontal edges. Two 3×3 kernels; G<sub>y</sub> is G<sub>x</sub> rotated by 90°. The centre row/column has weight 2, which also smooths a little.</p>
{mats(mat(SOB_Y, "∂f/∂y = Sobel G<sub>y</sub> (slide: extract vertical edges)"), mat(SOB_X, "∂f/∂x = Sobel G<sub>x</sub> (slide: extract horizontal edges)"))}
{formula("|G| = |G<sub>x</sub>| + |G<sub>y</sub>| ≈ |(z<sub>7</sub> + 2z<sub>8</sub> + z<sub>9</sub>) − (z<sub>1</sub> + 2z<sub>2</sub> + z<sub>3</sub>)| + |(z<sub>3</sub> + 2z<sub>6</sub> + z<sub>9</sub>) − (z<sub>1</sub> + 2z<sub>4</sub> + z<sub>7</sub>)|")}
<p><b>Slide 36. Prewitt:</b> used for detecting edges horizontally and vertically. Same as Sobel with weight 1 instead of 2.</p>
{mats(mat(PRE_Y, "∂f/∂y = Prewitt G<sub>y</sub> (vertical edges)"), mat(PRE_X, "∂f/∂x = Prewitt G<sub>x</sub> (horizontal edges)"))}
{formula("∇f ≈ |(z<sub>7</sub> + z<sub>8</sub> + z<sub>9</sub>) − (z<sub>1</sub> + z<sub>2</sub> + z<sub>3</sub>)| + |(z<sub>3</sub> + z<sub>6</sub> + z<sub>9</sub>) − (z<sub>1</sub> + z<sub>4</sub> + z<sub>7</sub>)|")}
<p>All gradient masks add up to <b>0</b>: a flat area gives no response.</p>
{sim({"type": "filter", "images": ["sp22", "cw7"], "filters": ["sobel", "prewitt", "roberts", "sobelx", "sobely"], "pad": "zero", "start": [1, 1]}, "G<sub>x</sub>, G<sub>y</sub> and |G| for Sobel, Prewitt and Roberts, step by step.")}
<p><b>Slides 37–41.</b> Examples: coins (edges along x and along y), a contact lens enhanced with Sobel so that defects become obvious ("Sobel filters are typically used for edge detection"), and Einstein: G<sub>y</sub> gives the vertical edges, G<sub>x</sub> the horizontal edges (absolute values).</p>
<p><b>Slide 42. Laplacian vs Sobel</b> on a chessboard: the Laplacian gives thin, double edges and also picks up fine texture and noise; Sobel gives thicker, stronger edges along the board lines.</p>
"""))

# ================================================================ 6. difference / unsharp
sig = [10, 10, 10, 10, 10, 30, 50, 70, 90, 90, 90, 90, 90]
pad = [sig[0]] + sig + [sig[-1]]
blur = [rhu(sum(pad[i:i + 3]) / 3) for i in range(len(sig))]
maskv = [a - b for a, b in zip(sig, blur)]
sharp = [a + m for a, m in zip(sig, maskv)]
boost = [a + 2 * m for a, m in zip(sig, maskv)]
up1 = splot([{"v": sig, "cls": "c5", "label": "original", "at": (0.3, 18)}, {"v": blur, "cls": "c1", "label": "blurred", "at": (8.6, 72)}], 0, 100, [0, 50, 90],
            "(a) original edge and (b) its blurred version (3-point average)", w=320, h=200, xlab="pixel")
up2 = splot([{"v": maskv, "cls": "c3", "dots": True}], -10, 10, [-7, 0, 7], "(c) unsharp mask = original − blurred: a dip before the edge and a bump after it", w=320, h=200, xlab="pixel")
up3 = splot([{"v": sig, "cls": "c5", "label": "original", "at": (0.3, 20)}, {"v": sharp, "cls": "c1", "label": "sharpened", "at": (7.4, 104)}], 0, 105, [0, 50, 90],
            "(d) sharpened = original + mask: undershoot before and overshoot after the edge, so the edge looks crisper", w=320, h=200, xlab="pixel")
S.append(sec("unsharp", "Difference (emboss) filters and unsharp masking", "43–48", LIKELY, f"""
<p><b>Slides 43–44. Difference filters</b>, also called <b>emboss filters</b>, enhance the details in the direction specific to the mask selected. The four primary masks, for edges in the vertical, horizontal and two diagonal directions:</p>
{mats(mat([[0, 1, 0], [0, 1, 0], [0, -1, 0]], "horizontal"), mat([[0, 0, 0], [1, 1, -1], [0, 0, 0]], "vertical"), mat([[1, 0, 0], [0, 1, 0], [0, 0, -1]], "diagonal 1"), mat([[0, 0, 1], [0, 1, 0], [-1, 0, 0]], "diagonal 2"))}
<p>The filtered image looks like a gray relief (embossed). Added back to the original, it gives a contrast-enhanced picture (Jimi Hendrix poster).</p>
{idea("Unsharp masking sounds backwards: you sharpen by using a blurred copy. Blur the image, subtract the blur from the original, and what's left is only the detail (edges). Add that detail back on top of the original and the edges stand out more.")}
<p><b>Slide 45. Unsharp masking</b> is a classic sharpening technique. It sharpens by subtracting a blurred version from the original image. <b>Steps:</b></p>
<ol><li><b>Blur the image</b> (usually with a Gaussian filter).</li><li><b>Subtract the blurred image from the original</b>: this isolates the high-frequency details (edges).</li>
<li><b>Scale the difference by a factor</b> (called the amount).</li><li><b>Add it back to the original image</b>: edges and fine details become more pronounced.</li></ol>
{formula("g<sub>mask</sub> = f − f̄ &nbsp;&nbsp;&nbsp; g = f + k · g<sub>mask</sub>")}
<p>k = 1: unsharp masking. k &gt; 1: <b>high-boost filtering</b> (Figure 3.40e, an even stronger result).</p>
<h3>Slide 46. The 1-D demo (Figure 3.39), with real numbers</h3>
{tbl(["pixel"] + list(range(len(sig))), [["(a) original"] + sig, ["(b) blurred"] + blur, ["(c) mask = a − b"] + maskv, ["(d) sharpened = a + c"] + sharp, ["high-boost, k = 2"] + boost], "narrow")}
{figs(up1, up2, up3)}
{sim({"type": "oned", "sig": sig, "modes": ["unsharp"]}, "unsharp masking on every pixel: blur, mask = original − blur, sharpened = original + mask.")}
<p><b>Slide 47. Applications of unsharp masking:</b> document scanning (enhances faint text), medical imaging (highlights subtle tissue boundaries), photography (improves clarity and detail), satellite imaging (sharpens roads and rivers).</p>
<p><b>Slide 48.</b> DIP-XE example: (a) original, (b) blurred with a Gaussian, (c) unsharp mask, (d) unsharp masking result, (e) high-boost result.</p>
"""))

# ================================================================ 7. combining
S.append(sec("combo", "Combining enhancement methods (bone scan)", "49–52", SHORT, """
<p><b>Slide 49.</b> Successful enhancement is usually not achieved with a single operation; we combine a range of techniques. The example enhances a whole-body bone scan:</p>
<ol>
<li>(a) original bone scan;</li>
<li>(b) Laplacian of (a);</li>
<li>(c) sharpened image, combining (a) and (b);</li>
<li>(d) Sobel gradient of (a);</li>
<li>(e) (d) smoothed with a 5×5 averaging filter;</li>
<li>(f) the product of (c) and (e), used as a mask: strong edges kept, noise in flat areas suppressed;</li>
<li>(g) sharpened image, the sum of (a) and (f);</li>
<li>(h) power-law (gamma) transformation applied to (g), to bring out the dark detail.</li>
</ol>
<p>Why mix them: the Laplacian brings out fine detail but also noise; the smoothed Sobel image is strong at real edges and weak at noise, so their product keeps detail only where there are edges. Gamma finally expands the dark range. Slide 52 compares the original and final images.</p>
"""))

# ================================================================ 8. past questions
cw = [[0, 2, 6, 7], [1, 1, 6, 4], [4, 5, 2, 7], [1, 2, 6, 0]]
inner = [(1, 1), (1, 2), (2, 1), (2, 2)]
def inner_grid(fn):
    g = [[0] * 4 for _ in range(4)]
    for r, c in inner:
        g[r][c] = fn(r, c)
    return g
cw_lap = inner_grid(lambda r, c: corr(cw, LAP_N, r, c))
cw_mean = inner_grid(lambda r, c: rhu(sum(flat(win(cw, r, c))) / 9))
cw_med = inner_grid(lambda r, c: sorted(flat(win(cw, r, c)))[4])
cw_sx = inner_grid(lambda r, c: corr(cw, SOB_X, r, c)); cw_sy = inner_grid(lambda r, c: corr(cw, SOB_Y, r, c))
cw_sm = inner_grid(lambda r, c: abs(cw_sx[r][c]) + abs(cw_sy[r][c]))
cw_px = inner_grid(lambda r, c: corr(cw, PRE_X, r, c)); cw_py = inner_grid(lambda r, c: corr(cw, PRE_Y, r, c))
cw_pm = inner_grid(lambda r, c: abs(cw_px[r][c]) + abs(cw_py[r][c]))
def rows_for(fn):
    return [[f"({r},{c})", *fn(r, c)] for r, c in inner]

sp22 = [[3, 7, 6], [2, 5, 8], [3, 4, 7]]
gx = [[corr(sp22, SOB_X, r, c) for c in range(3)] for r in range(3)]
gy = [[corr(sp22, SOB_Y, r, c) for c in range(3)] for r in range(3)]
gm = [[abs(gx[r][c]) + abs(gy[r][c]) for c in range(3)] for r in range(3)]
alpha = math.degrees(math.atan2(gy[1][1], gx[1][1]))
p25 = [[10, 10, 10], [10, 50, 10], [10, 10, 10]]
f21 = [[7, 1, 0, 5], [6, 3, 6, 2], [6, 4, 4, 1], [1, 5, 7, 0]]
sp25 = [[7, 7, 7, 7, 7, 7, 7], [7, 7, 7, 2, 7, 7, 7], [7, 5, 0, 0, 0, 5, 7], [5, 1, 1, 0, 1, 1, 5], [5, 5, 0, 0, 0, 5, 5], [3, 3, 3, 2, 3, 3, 3], [7, 7, 7, 7, 7, 7, 7]]

def lap_box(img, r, c, m, name):
    w = win(img, r, c)
    sgn = "negative" if m[1][1] > 0 else "positive"
    return (show_window(img, r, c, f"window at ({r},{c})") + mats(mat(w, "window"), mat(m, f"{sgn} Laplacian")) +
            f"<p>Σ w·z = {mask_line(w, m)[0]}</p><p>{name} response at ({r},{c}) = <b>{mask_line(w, m)[1]}</b>.</p>")

S.append(sec("pq", "Past questions and class work, solved in full", "19–53", EXAM, f"""
<p>Coordinates: (row, column) from 0 at the top-left. Write the window, the mask, every product, and the sum.</p>
{paper("Slide 53 · Class work", "all parts", f'''
<p class="q">3-bit 4×4 image. Find the filtered output using the negative Laplacian, a 3×3 mean, a 3×3 median, a 3×3 Sobel and a 3×3 Prewitt operator. Ignore the border pixels and put zero in the output border.</p>
{mat(cw, "input image", hi=set(inner))}
<p>Only the four inner pixels (shaded) have a full 3×3 window.</p>
<p><b>(1) Negative Laplacian</b> [0 −1 0; −1 4 −1; 0 −1 0]: 4×centre − up − down − left − right.</p>
{tbl(["pixel", "working", "value"], rows_for(lambda r, c: (f"4×{cw[r][c]} − {cw[r - 1][c]} − {cw[r + 1][c]} − {cw[r][c - 1]} − {cw[r][c + 1]}", corr(cw, LAP_N, r, c))), "narrow")}
<p><b>(2) 3×3 mean</b></p>
{tbl(["pixel", "sum of window", "÷ 9", "rounded"], rows_for(lambda r, c: (sum(flat(win(cw, r, c))), f"{sum(flat(win(cw, r, c))) / 9:.2f}", rhu(sum(flat(win(cw, r, c))) / 9))), "narrow")}
<p><b>(3) 3×3 median</b></p>
{tbl(["pixel", "sorted window", "median"], rows_for(lambda r, c: (", ".join(map(str, sorted(flat(win(cw, r, c))))), sorted(flat(win(cw, r, c)))[4])), "narrow")}
<p><b>(4) Sobel</b>: G<sub>x</sub> = (z3 + 2z6 + z9) − (z1 + 2z4 + z7), G<sub>y</sub> = (z7 + 2z8 + z9) − (z1 + 2z2 + z3), |G| = |G<sub>x</sub>| + |G<sub>y</sub>|.</p>
{tbl(["pixel", "G<sub>x</sub>", "G<sub>y</sub>", "|G|"], rows_for(lambda r, c: (cw_sx[r][c], cw_sy[r][c], cw_sm[r][c])), "narrow")}
<p><b>(5) Prewitt</b>: the same with weights 1.</p>
{tbl(["pixel", "G<sub>x</sub>", "G<sub>y</sub>", "|G|"], rows_for(lambda r, c: (cw_px[r][c], cw_py[r][c], cw_pm[r][c])), "narrow")}
<p><b>Output images</b> (border = 0):</p>
{mats(mat(cw_lap, "negative Laplacian"), mat(cw_mean, "mean"), mat(cw_med, "median"), mat(cw_sm, "Sobel |G|"), mat(cw_pm, "Prewitt |G|"))}
<p>Worked Sobel at (1,1): window [0 2 6; 1 1 6; 4 5 2]. G<sub>x</sub> = (6 + 2×6 + 2) − (0 + 2×1 + 4) = 20 − 6 = {cw_sx[1][1]}. G<sub>y</sub> = (4 + 2×5 + 2) − (0 + 2×2 + 6) = 16 − 10 = {cw_sy[1][1]}. |G| = {cw_sm[1][1]}.</p>
''')}
{sim({"type": "filter", "images": ["cw7"], "filters": ["lapneg", "mean", "median", "sobel", "prewitt"], "pad": "discard"}, "the slide 53 class work: switch filters, the border is ignored as the question says.")}
{paper("SP22 Q6(b)i", "4 marks", f'''
<p class="q">3×3 image [3 7 6; 2 5 8; 3 4 7]. Find the Sobel gradient-magnitude image and the edge direction of the central pixel.</p>
<p><b>Centre pixel:</b> z1…z9 = 3, 7, 6, 2, 5, 8, 3, 4, 7.</p>
<p>G<sub>x</sub> = (z3 + 2z6 + z9) − (z1 + 2z4 + z7) = (6 + 16 + 7) − (3 + 4 + 3) = 29 − 10 = <b>{gx[1][1]}</b></p>
<p>G<sub>y</sub> = (z7 + 2z8 + z9) − (z1 + 2z2 + z3) = (3 + 8 + 7) − (3 + 14 + 6) = 18 − 23 = <b>{gy[1][1]}</b></p>
<p>|∇f| ≈ |G<sub>x</sub>| + |G<sub>y</sub>| = {abs(gx[1][1])} + {abs(gy[1][1])} = <b>{gm[1][1]}</b></p>
<p><b>Direction</b> (deck 08 slide 23): gradient angle α = tan⁻¹(G<sub>y</sub>/G<sub>x</sub>) = tan⁻¹({gy[1][1]}/{gx[1][1]}) = <b>{alpha:.2f}°</b>. The edge runs perpendicular to the gradient: edge direction = α − 90° = <b>{alpha - 90:.2f}°</b>.</p>
<p><b>Whole magnitude image</b> with zero padding (same formulas at every pixel):</p>
{mats(mat(sp22, "input"), mat(gx, "G<sub>x</sub>"), mat(gy, "G<sub>y</sub>"), mat(gm, "|G<sub>x</sub>| + |G<sub>y</sub>|"))}
''')}
{sim({"type": "filter", "images": ["sp22"], "filters": ["sobel"], "pad": "zero", "start": [1, 1]}, "SP22: the full Sobel magnitude image with zero padding.")}
{paper("SP25 Q2(d)i", "2 marks", f'''
<p class="q">3×3 patch [10 10 10; 10 50 10; 10 10 10]. Apply the Sobel operator in the horizontal direction. What is the gradient value at the centre pixel?</p>
{mats(mat(p25, "patch", ctr=(1, 1)), mat(SOB_X, "Sobel G<sub>x</sub>"))}
<p>G<sub>x</sub> = (z3 + 2z6 + z9) − (z1 + 2z4 + z7) = (10 + 20 + 10) − (10 + 20 + 10) = 40 − 40 = <b>{corr(p25, SOB_X, 1, 1)}</b>.</p>
<p>(With the other mask, G<sub>y</sub> = (10 + 20 + 10) − (10 + 20 + 10) = {corr(p25, SOB_Y, 1, 1)} too.) The gradient is <b>0</b>: the left and right columns are equal, so there is no horizontal change across the centre. The Sobel masks have a 0 centre weight, so the bright point 50 itself is not seen. A Laplacian would respond strongly: 4×50 − 4×10 = {corr(p25, LAP_N, 1, 1)}.</p>
''')}
{sim({"type": "filter", "images": ["p25"], "filters": ["sobelx", "sobely", "sobel", "lapneg"], "pad": "zero", "start": [1, 1]}, "SP25 (d)(i): Sobel gives 0 at the centre; the Laplacian does not.")}
{paper("F21 B4(a)iii", "2 marks", lap_box(f21, 1, 1, LAP_P, "Laplacian"))}
{sim({"type": "filter", "images": ["f21"], "filters": ["lappos"], "pad": "zero", "start": [1, 1]}, "F21 (iii) at (1,1).")}
{paper("SP25 Q2(b)ii Task 2 · negative Laplacian at (3,2)", "2 marks", lap_box(sp25, 3, 2, LAP_N, "Negative Laplacian"))}
{sim({"type": "filter", "images": ["sp25"], "filters": ["lapneg"], "pad": "zero", "start": [3, 2]}, "SP25 Task 2 at (3,2).")}
{paper("SP24 Q2(b)ii Task 2 · positive Laplacian at (3,3)", "2 marks", lap_box(sp25, 3, 3, LAP_P, "Positive Laplacian"))}
{sim({"type": "filter", "images": ["sp25"], "filters": ["lappos"], "pad": "zero", "start": [3, 3]}, "SP24 Task 2 at (3,3).")}
<p>The smoothing parts of these mixed questions (max, mean, median, the 4-neighbour mask) are on the deck 06 page.</p>
"""))

S.append(sec("traps", "Traps and one-minute sheet", "all", None, f"""
<ul class="traps">
<li>Laplacian masks add to <b>0</b>. Single-pass sharpening masks add to <b>1</b>.</li>
<li>Sharpening sign: centre negative → g = f − ∇²f; centre positive → g = f + ∇²f. Either way the result is the same.</li>
<li>Gradient: write G<sub>x</sub>, G<sub>y</sub> and |G| = |G<sub>x</sub>| + |G<sub>y</sub>| separately. Take absolute values before adding.</li>
<li>Use the slide's labels: Sobel G<sub>y</sub> = [−1 −2 −1; 0 0 0; 1 2 1], G<sub>x</sub> = [−1 0 1; −2 0 2; −1 0 1].</li>
<li>1st derivative → thick edges, nonzero along ramps. 2nd derivative → double thin edges, zero on ramps, strong on points.</li>
</ul>
{tbl(["operator", "mask", "derivative", "use"], [
    ["positive Laplacian", "[0 1 0; 1 −4 1; 0 1 0]", "2nd", "edge/detail map"], ["negative Laplacian", "[0 −1 0; −1 4 −1; 0 −1 0]", "2nd", "edge/detail map"],
    ["single-pass sharpen", "[0 −1 0; −1 5 −1; 0 −1 0]", "2nd", "sharpened image in one step"], ["8-nbr single pass", "[−1 −1 −1; −1 9 −1; −1 −1 −1]", "2nd", "stronger sharpening"],
    ["Roberts", "[−1 0; 0 1], [0 −1; 1 0]", "1st", "simplest gradient"], ["Sobel", "G<sub>y</sub> [−1 −2 −1; 0 0 0; 1 2 1], G<sub>x</sub> its 90° turn", "1st", "edge detection"],
    ["Prewitt", "weights 1 instead of 2", "1st", "edge detection"], ["unsharp / high-boost", "g = f + k(f − f̄)", "—", "k = 1 unsharp, k &gt; 1 high-boost"]])}
"""))

# ================================================================ simulators
IMAGES = {
    "i26": {"name": "Slide 26 · 5×5", "img": I26, "note": "The pixel 154: negative Laplacian 616 − 630 = −14; sharpened 154 + (−14) = 140."},
    "cw7": {"name": "Slide 53 class work · 4×4", "img": cw, "note": "Inner pixels only (border ignored): Laplacian −10 11 / 11 −16; Sobel |G| at (1,1) = 20."},
    "sp22": {"name": "SP22 Q6(b) · 3×3", "img": sp22, "note": "Centre: G<sub>x</sub> = 19, G<sub>y</sub> = −5, |G| = 24."},
    "p25": {"name": "SP25 Q2(d) · bright point", "img": p25, "note": "Centre: both Sobel masks give 0; the Laplacian gives 160."},
    "f21": {"name": "F21 B4(a) · 4×4", "img": f21, "note": "Positive Laplacian at (1,1) = 5."},
    "sp25": {"name": "SP25 / SP24 Q2(b) · 7×7", "img": sp25, "note": "Negative Laplacian at (3,2) = 3; positive Laplacian at (3,3) = 2."},
}
SHARP = ["lappos", "lapneg", "lappos8", "lapneg8", "sharp_neg", "sharp_pos", "comp4", "comp8", "sobel", "prewitt", "roberts", "sobelx", "sobely", "mean", "median"]
S.insert(1, sec("sim", "Simulator: any image, any sharpening filter", "19–53", EXAM,
                idea("Pick an image and a filter, then press <b>Next step</b>. Each pixel takes 4 steps: <b>place</b> the window, <b>multiply</b>, <b>add</b> (and for sharpening, add the result back to f), <b>write</b>. Gradient filters show G<sub>x</sub> and G<sub>y</sub> side by side. ← → keys step; click a pixel to jump; Play runs it. Smaller simulators sit next to each method below.")
                + sim({"type": "filter", "images": list(IMAGES), "filters": SHARP, "pad": "zero", "start": [2, 2]})))

toc = [("start", "Start"), ("sim", "Simulator"), ("deriv", "Derivatives"), ("lap", "Laplacian"), ("lapenh", "Sharpen"), ("grad", "Gradient"), ("unsharp", "Unsharp"),
       ("combo", "Combining"), ("pq", "Past papers"), ("traps", "Traps")]
OUT.write_text(page("DIP Deck 07 Lesson", "CSE 4227 · Chapter 3 · Deck 07", "Sharpening Spatial Filters, from zero",
                    "Every slide you need, in plain words, with the derivative graphs drawn and every Laplacian and Sobel question solved the way you write it in the answer script.",
                    toc, S, extra=sim_assets(IMAGES)), encoding="utf-8")

# ---------------------------------------------------------------- self-check against the slides and data/answers.json
assert d1[1:-1] == [-1, -1, -1, -1, -1, 0, 0, 6, -6, 0, 0, 0, 1, 2, -2, -1, 0, 0, 0, 7, 0, 0, 0]
assert d2[1:-1] == [-1, 0, 0, 0, 0, 1, 0, 6, -12, 6, 0, 0, 1, 1, -4, 1, 1, 0, 0, 7, -7, 0, 0]
assert lap26 == -14 and comp26 == 140
assert [cw_lap[r][c] for r, c in inner] == [-10, 11, 11, -16] and [cw_mean[r][c] for r, c in inner] == [3, 4, 3, 4]
assert [cw_med[r][c] for r, c in inner] == [2, 5, 2, 4] and [cw_sx[r][c] for r, c in inner] == [14, 13, 6, 5] and [cw_px[r][c] for r, c in inner] == [9, 10, 8, 3]
assert gx[1][1] == 19 and gy[1][1] == -5 and gm == [[28, 32, 40], [24, 24, 22], [22, 34, 34]]
assert corr(p25, SOB_X, 1, 1) == 0 and corr(f21, LAP_P, 1, 1) == 5 and corr(sp25, LAP_N, 3, 2) == 3 and corr(sp25, LAP_P, 3, 3) == 2
print(OUT, OUT.stat().st_size, "sobel", cw_sx, cw_sy, "unsharp", blur, maskv, sharp)
