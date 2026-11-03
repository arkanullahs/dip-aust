"""Builds deck06_lesson.html: smoothing spatial filtering lesson. All numbers computed here."""
import sys, pathlib, statistics
from fractions import Fraction as F
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from kit import *

OUT = pathlib.Path(__file__).with_name("deck06_lesson.html")


S = []

# ================================================================ 1. idea
S.append(sec("start", "Start here: what a filter does", "3–10", LIKELY, f"""
{idea("So far every new pixel depended only on its own old value (deck 04) or on the image's histogram (deck 05). Filtering is the third way: the new pixel depends on the pixel <b>and its neighbours</b>. Put a small grid of numbers (the kernel) on top of the image, multiply each kernel number by the pixel under it, add everything up, and write that sum as the new centre pixel. Then slide the kernel one pixel along and repeat.")}
<p><b>Slide 3.</b> Until now we used two methods: (1) transformation functions, (2) histogram processing.</p>
<p><b>Slide 4.</b> The third method is <b>convolution</b>, written two ways: g(x,y) = h(x,y) * f(x,y), the <b>mask convolved with an image</b>; or g(x,y) = f(x,y) * h(x,y), the <b>image convolved with a mask</b>.</p>
<p><b>Slide 5.</b> Convolution/correlation is a <b>neighbourhood operation</b>. The kernel is also called a <b>filter / mask / window / box</b>, and it is written as a 2-D matrix.</p>
<p><b>Slide 6.</b> Convolution/correlation is the process of <b>moving a kernel over the image</b>.</p>
<p><b>Slide 7. Steps</b> (MATLAB's im2conv()):</p>
<ol><li><b>Multiply</b> the corresponding elements (kernel value × pixel under it).</li><li><b>Add</b> them all: the <b>sum of products</b>.</li><li><b>Repeat</b> for every pixel of the image.</li></ol>
{paper("Slide 8 · correlation example", "worked", f'''
<p>Kernel [−1 0 1; 2 1 2; 1 −2 0] placed on the top-left 3×3 block of the input:</p>
{mats(mat([[5, 2, 6], [4, 3, 4], [3, 9, 2]], "pixels under the kernel"), mat([[-1, 0, 1], [2, 1, 2], [1, -2, 0]], "kernel"))}
<p>(−1×5) + (0×2) + (1×6) + (2×4) + (1×3) + (2×4) + (1×3) + (−2×9) + (0×2) = −5 + 0 + 6 + 8 + 3 + 8 + 3 − 18 + 0 = <b>5</b>.</p>
<p>5 is written in the output at the position of the centre pixel (3). Then the kernel moves one step right.</p>
''')}
{sim({"type": "filter", "images": ["s8"], "filters": ["slide8"], "pad": "discard"}, "the slide 8 kernel visiting every position of the 8×8 source.")}
<p><b>Slide 9.</b> The filtering here is called <b>correlation/convolution</b>. A spatial filter consists of (i) a <b>neighbourhood</b> and (ii) a <b>predefined operation</b> (the filter/mask/kernel).</p>
<p><b>Slide 10.</b> With neighbourhood pixels a…i around centre e and kernel r…z:</p>
{mats(mat([["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]], "3×3 neighbour pixels", ctr=(1, 1)), mat([["r", "s", "t"], ["u", "v", "w"], ["x", "y", "z"]], "kernel / filter"))}
{formula("e<sub>processed</sub> = v·e + r·a + s·b + t·c + u·d + w·f + x·g + y·h + z·i")}
<p>The process is repeated for every pixel of the original image to generate the processed image.</p>
"""))

# ================================================================ 2. equations
imp = [[0] * 5 for _ in range(5)]; imp[2][2] = 1
S.append(sec("eq", "Correlation vs convolution (the equations)", "11–14", SHORT, f"""
<p><b>Slides 11–12. Spatial correlation</b> of a filter w(s,t) of size m×n with an image f(x,y) of size M×N:</p>
{formula("w(s,t) ☆ f(x,y) = Σ<sub>s=−a</sub><sup>a</sup> Σ<sub>t=−b</sub><sup>b</sup> w(s,t) · f(x+s, y+t)")}
<p>with m = 2a+1 and n = 2b+1. For a 3×3 kernel, a = b = 1, so s and t run over −1, 0, 1: exactly "multiply the 9 pairs and add".</p>
<p><b>Slide 13. Convolution</b> is the same operation except the <b>filter is flipped both horizontally and vertically</b> (rotated 180°) before it is applied:</p>
{formula("w(s,t) ★ f(x,y) = Σ Σ w(s,t) · f(x−s, y−t)")}
<p>For symmetric kernels (mean, weighted average, Gaussian, Laplacian) flipping changes nothing, so correlation and convolution give the same answer. That's why exam questions just say "apply the filter".</p>
{paper("Slides 14, 57–63 · filtering an impulse", "worked", f'''
<p>Take an image that is all 0 except one pixel = 1 (an <b>impulse</b>) and a kernel with entries a…i.</p>
{mats(mat(imp, "impulse F", ctr=(2, 2)), mat([["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]], "kernel H"))}
{mats(mat([[0, 0, 0, 0, 0], [0, "i", "h", "g", 0], [0, "f", "e", "d", 0], [0, "c", "b", "a", 0], [0, 0, 0, 0, 0]], "correlation output: kernel flipped"),
      mat([[0, 0, 0, 0, 0], [0, "a", "b", "c", 0], [0, "d", "e", "f", 0], [0, "g", "h", "i", 0], [0, 0, 0, 0, 0]], "convolution output: kernel itself"))}
<p>Correlation with an impulse gives the kernel <b>flipped horizontally and vertically</b>. Convolution flips the kernel first, so the output <b>equals the filter kernel</b>. Slide 14 (Figure 3.30) shows the same thing with kernel 1…9: correlation gives 9 8 7 / 6 5 4 / 3 2 1, convolution gives 1 2 3 / 4 5 6 / 7 8 9.</p>
''')}
"""))

# ================================================================ 3. types + masks
S.append(sec("types", "Types of filter and the two averaging masks", "15–18", LIKELY, f"""
<p><b>Slide 15. Two types of filtering:</b></p>
<ol><li><b>Smoothing spatial filters</b> (low pass): used for <b>blurring</b> and for <b>noise reduction</b>.</li>
<li><b>Sharpening spatial filters</b> (high pass): used for <b>edge detection</b> and <b>sharpness</b>. Deck 07.</li></ol>
<p><b>Slide 16. Smoothing filters</b> include linear and nonlinear filters:</p>
{tbl(["kind", "filters", "how the output is made"], [["<b>linear</b>", "standard average (mean), weighted average", "sum of products with fixed weights"],
                                                     ["<b>nonlinear</b> (order statistics)", "median, min, max", "sort the window, pick by rank"]])}
<p><b>Slide 17. Weighted averaging formula</b> for an M×N image with an m×n filter:</p>
{formula("g(x,y) = Σ Σ w(s,t) f(x+s, y+t) / Σ Σ w(s,t), &nbsp; m = 2a+1, n = 2b+1")}
<p>Dividing by the sum of the weights keeps the brightness the same.</p>
<p><b>Slide 18. Two smoothing averaging masks:</b></p>
{mats(mat([[1, 1, 1], [1, 1, 1], [1, 1, 1]], "1/9 × · Mean filter: all elements the same"), mat([[1, 2, 1], [2, 4, 2], [1, 2, 1]], "1/16 × · Weighted average: different weights"))}
<p><b>The sum of all the elements should be 1</b> (9 × 1/9 = 1; 16/16 = 1). A flat area then stays exactly the same.</p>
<p>In the weighted mask the centre counts 4 times, the edge neighbours 2 times and the corners once. Pixels closer to the centre matter more, so there's less blurring than with the mean.</p>
"""))

# ================================================================ 4. mean
m19 = [[110, 120, 90, 130], [91, 94, 98, 200], [90, 91, 99, 100], [82, 96, 85, 90]]
w19 = win(m19, 1, 1)
wl = [[1, 2, 1], [2, 4, 2], [1, 2, 1]]
wsum = sum(wl[i][j] * w19[i][j] for i in range(3) for j in range(3))
box = [[0] * 10 for _ in range(10)]
for r in range(2, 7):
    for c in range(3, 8):
        box[r][c] = 90
box[5][4] = 0; box[8][2] = 90
box_out = [[sum(flat(win(box, r, c))) // 9 for c in range(1, 9)] for r in range(1, 9)]
assert all(sum(flat(win(box, r, c))) % 9 == 0 for r in range(1, 9) for c in range(1, 9))
S.append(sec("mean", "Mean (box) filter and weighted average", "19–35", EXAM, f"""
{idea("The mean filter replaces each pixel by the average of itself and its 8 neighbours. A lone bright speck gets averaged with 8 normal pixels, so it fades. That's noise reduction. A sharp edge also gets averaged with pixels from the other side, so it smears. That's blurring. You always get both together.")}
{paper("Slide 19 · standard averaging at the pixel 94", "worked", f'''
{show_window(m19, 1, 1, "image; shaded = 3×3 window, outlined = centre")}
<p>g = {mean_line(w19)[0]} ≈ <b>98.1</b></p>
''')}
{sim({"type": "filter", "images": ["s19"], "filters": ["mean", "weighted"], "pad": "zero", "start": [1, 1]}, "slide 19 (mean) and slide 35 (weighted) on every pixel. It opens on the 94.")}
{paper("Slide 35 · weighted average at the same pixel", "worked", f'''
<p>Mask 1/16 [1 2 1; 2 4 2; 1 2 1]. Multiply each pixel by its weight:</p>
<p>(1×110 + 2×120 + 1×90 + 2×91 + 4×94 + 2×98 + 1×90 + 2×91 + 1×99)/16</p>
<p>= (110 + 240 + 90 + 182 + 376 + 196 + 90 + 182 + 99)/16 = {wsum}/16 = <b>{wsum / 16:.2f} ≈ {rhu(wsum / 16)}</b></p>
{trap(f"The slide prints 97.25 ≈ 97 here, but the nine terms add to {wsum}, not 1556, so the correct value is {wsum / 16:.4f} ≈ {rhu(wsum / 16)}. Show your addition in the exam so the method marks are safe either way.")}
''')}
{paper("Slides 20–27 · mean filter over a whole 10×10 image", "worked", f'''
<p>The mask moves from point to point; at each point (x,y) the response is calculated. Border pixels are skipped (discard method), so the output is 8×8.</p>
{mats(mat(box, "input f (a 90-valued box with one dark hole and one stray 90)", small=True), mat(box_out, "output g (8×8)", small=True))}
<p>First few positions, as on the slides: g = 1/9 × (0+0+0+0+0+0+0+0+90) = <b>10</b>, then 20, 30, 30. At the hole: 1/9 × (0+0+0+0+90+90+90+90+90) = <b>50</b>. Fully inside the box: 1/9 × (9×90) = <b>90</b>.</p>
<p>Notice: the hard edge of the box became a ramp (0, 10, 20, 30 …), the dark hole was filled in (50 instead of 0), and the stray 90 spread into a faint 10-valued patch. That's blurring and noise reduction at the same time.</p>
''')}
{sim({"type": "filter", "images": ["box"], "filters": ["mean"], "pad": "discard"}, "the whole slides 20–27 walk-through, all 64 positions.")}
<p><b>Slide 32. What the mean (box) filter does:</b> replaces each pixel with an average of its neighbourhood; achieves a smoothing effect (<b>removes sharp features</b>); adds a "softer" look to the image.</p>
<p><b>Slide 33. Gross representation of objects:</b> a Hubble image filtered with a 15×15 averaging mask, then thresholded. Small faint objects blend into the background and disappear; only the large bright objects survive as blobs.</p>
<p><b>Slide 34. Averaging effects: blurring + reducing noise.</b> Box filters of 3×3, 5×5, 9×9, 15×15 and 35×35: the bigger the mask, the stronger the blur, and fine detail begins to disappear.</p>
"""))

# ================================================================ 5. borders
b = [[17, 24, 1, 8, 15], [23, 5, 7, 14, 16], [4, 6, 13, 20, 22], [10, 12, 19, 21, 3], [11, 18, 25, 2, 9]]
zp = [[0, 0, 0], [24, 1, 8], [5, 7, 14]]
rp = [[1, 8, 15], [1, 8, 15], [7, 14, 16]]
S.append(sec("border", "What happens at the border?", "28–31", LIKELY, f"""
<p>At the edge of the image, part of the 3×3 kernel hangs outside. Those outside cells have no values. Slide 28 gives three solutions:</p>
{show_window(b, 0, 3, "kernel centred on 8 in the top row: the top 3 cells fall outside")}
<ol>
<li><b>Zero padding</b> (slide 29): outside pixels are assumed to be 0. Easy, but the image gets a <b>black border</b> after filtering (the averages near the edge are pulled down).</li>
<li><b>Border padding / pixel replication</b> (slide 30): outside pixels copy the nearest boundary pixel.</li>
<li><b>Discard</b> (slide 31): don't compute the border pixels at all. The output is smaller: a 512×512 input gives a 510×510 output with a 3×3 mask.</li>
</ol>
{mats(mat(zp, "window with zero padding"), mat(rp, "window with replication"))}
{sim({"type": "filter", "images": ["border5"], "filters": ["mean", "median"], "pad": "zero", "start": [0, 3]}, "change the Border menu and watch the dashed cells change: zeros, copied border pixels, or not used at all.")}
{paper("Slide 31 · \"Think for mask size 5×5 or 7×7?\"", "solved", '''
<p>An m×m mask has (m − 1)/2 rows hanging over each side. Discarding removes that many rows and columns on every side, i.e. m − 1 in total.</p>
<ul><li>3×3: 1 per side → 512×512 becomes 510×510.</li><li>5×5: 2 per side → 508×508.</li><li>7×7: 3 per side → 506×506.</li></ul>
''')}
"""))

# ================================================================ 6. gaussian
g1 = lambda x, s: math.exp(-((x - 4) ** 2) / (2 * s * s)) / (s * math.sqrt(2 * math.pi))
gfig = plot(8, 0.42, curves=[{"pts": fn(lambda x: g1(x, 1), 8), "cls": "c1", "label": "σ = 1", "at": (4.4, 0.36)},
                             {"pts": fn(lambda x: g1(x, 2), 8), "cls": "c3", "label": "σ = 2", "at": (6.0, 0.13)}],
            xticks=[(0, "−4"), (2, "−2"), (4, "0"), (6, "2"), (8, "4")], yticks=[0], xlabel="distance from centre", ylabel="weight",
            caption="Gaussian weights. Small σ: tall and narrow, little smoothing. Large σ: low and wide, more smoothing.")
S.append(sec("gauss", "Gaussian filter", "36–40", SHORT, f"""
{idea("A Gaussian filter is a weighted average whose weights follow a bell curve: biggest at the centre, smaller further away. The 1/16 [1 2 1; 2 4 2; 1 2 1] mask is the 3×3 Gaussian.")}
<div class="two"><div>
<ul>
<li>Performs a weighted average of surrounding pixels based on the <b>Gaussian distribution</b> (slide 36).</li>
<li>Used to remove <b>Gaussian noise</b>.</li>
<li>Good for reducing sharpness caused by random pixels; gives <b>better performance than the average filter</b>.</li>
<li>Discrete kernels: 3×3 (÷16), 5×5 (÷273), 7×7 (÷1003).</li>
<li>Gives <b>less weight to pixels further from the centre</b> of the window (slide 37).</li>
</ul></div><div>{gfig}</div></div>
{formula("G<sub>σ</sub>(x,y) = 1/(2πσ²) · e<sup>−(x² + y²)/(2σ²)</sup>")}
<p><b>Slides 39–40.</b> σ is the "scale" / "width" / "spread" of the kernel and <b>controls the amount of smoothing</b>. "What happens if you increase σ?" The bell gets wider, far pixels get more weight, and the image gets more blurred.</p>
"""))

# ================================================================ 7. median
m42 = [[110, 120, 90, 130], [91, 94, 98, 200], [90, 95, 99, 100], [82, 96, 85, 90]]
m43 = [[10, 15, 20], [23, 90, 27], [33, 31, 30]]
sp_o = [[49, 49, 48, 48, 48, 49, 49], [47, 47, 48, 49, 49, 49, 48], [47, 48, 49, 49, 50, 50, 49], [49, 49, 49, 49, 49, 50, 50],
        [48, 48, 48, 48, 48, 49, 50], [48, 48, 49, 50, 50, 50, 49], [49, 50, 50, 51, 51, 50, 50]]
sp_n = [[49, 49, 255, 48, 48, 49, 49], [47, 0, 48, 49, 49, 49, 0], [47, 48, 49, 49, 255, 50, 49], [49, 255, 49, 49, 0, 50, 50],
        [48, 48, 48, 48, 48, 49, 255], [48, 0, 49, 50, 50, 50, 49], [255, 50, 50, 51, 51, 50, 50]]
med_in = [[sorted(flat(win(sp_n, r, c)))[4] for c in range(1, 6)] for r in range(1, 6)]
mean_in = [[rhu(sum(flat(win(sp_n, r, c))) / 9) for c in range(1, 6)] for r in range(1, 6)]
orig_in = [row[1:6] for row in sp_o[1:6]]
sig = [10, 10, 10, 10, 10, 90, 10, 10, 90, 90, 90, 90, 90]
mn = [sig[0]] + [rhu(sum(sig[i - 1:i + 2]) / 3) for i in range(1, len(sig) - 1)] + [sig[-1]]
md = [sig[0]] + [sorted(sig[i - 1:i + 2])[1] for i in range(1, len(sig) - 1)] + [sig[-1]]
x = list(range(len(sig)))
edgefig = plot(len(sig) - 1, 100, curves=[{"pts": list(zip(x, sig)), "cls": "c5", "label": "input", "at": (0.2, 22)},
                                          {"pts": list(zip(x, mn)), "cls": "c3", "label": "mean (3)", "at": (5.6, 58)},
                                          {"pts": list(zip(x, md)), "cls": "c1", "label": "median (3)", "at": (9.4, 82)}],
              points=[(i, v, "") for i, v in enumerate(md)], xticks=list(range(0, len(sig), 2)), yticks=[0, 10, 50, 90], xlabel="pixel position (one row)", ylabel="gray value",
              caption="One image row with a noise spike (position 5) and an edge (position 8). The mean smears the spike into a bump and turns the edge into a ramp. The median deletes the spike and keeps the edge a clean step.", w=360)
S.append(sec("median", "Order-statistic filters: median, min, max", "41–46", EXAM, f"""
{idea("Order-statistic filters don't multiply anything. They <b>sort</b> the 9 values in the window and pick one by its rank: the smallest (min), the largest (max) or the middle one (median, the 5th of 9). A noise spike is extreme, so it lands at an end of the sorted list and the median never picks it.")}
<p><b>Slide 41.</b> The output is based on the <b>order of gray levels</b> in the masked area; the centre pixel is replaced with the value chosen by the <b>ranking</b>.</p>
<ul><li><b>Min:</b> set the pixel to the minimum in the neighbourhood.</li><li><b>Max:</b> set it to the maximum.</li><li><b>Median:</b> the midpoint value of the set.</li></ul>
{paper("Slide 42 · median at the pixel 94", "worked", f'''
{show_window(m42, 1, 1, "image; shaded = window")}
<p>Step 1, sort ascending: 90, 90, 91, 94, 95, 98, 99, 110, 120. Step 2, replace the original value by the median: <b>95</b>.</p>
''')}
{sim({"type": "filter", "images": ["s42"], "filters": ["median", "min", "max"], "pad": "zero", "start": [1, 1]}, "sort and pick on every pixel. Switch to min or max to compare.")}
{paper("Slide 43 · median of a spike", "worked", f'''
{mat(m43, "the 90 is a spike", ctr=(1, 1))}
<p>{med_line(m43)[0]}. The 90 is replaced by 27.</p>
''')}
<p><b>Slide 43. Properties of the median filter:</b></p>
<ul><li><b>No new pixel values</b> are introduced (the output is always one of the input values).</li><li>It <b>never replaces with the largest or smallest value</b>.</li>
<li>It <b>removes spikes</b>: good for impulse and salt-and-pepper noise.</li><li>It is a <b>non-linear</b> filter.</li>
<li>Particularly effective when the noise pattern consists of strong impulse noise (salt-and-pepper).</li></ul>
<p><b>Slide 44. Median effect: blurring + reducing noise.</b> It is very effective for removing salt-and-pepper noise (pepper image).</p>
<h3>Why median keeps edges sharper than the mean</h3>
{edgefig}
{paper("Slide 45 data · median vs mean on salt-and-pepper", "worked", f'''
<p>The noisy image has random 0 (pepper) and 255 (salt) pixels. Below, both 3×3 filters are applied to the inner 5×5 pixels:</p>
{mats(mat(sp_n, "noisy image", small=True), mat(orig_in, "original (inner 5×5)", small=True), mat(mean_in, "3×3 mean", small=True), mat(med_in, "3×3 median", small=True))}
<p>The median output is within 1 of the original everywhere. The mean output carries the noise along: a 255 raises its whole neighbourhood to about 70, and a 0 pulls it down.</p>
''')}
{sim({"type": "filter", "images": ["sp"], "filters": ["median", "mean"], "pad": "discard"}, "median vs mean on the salt-and-pepper image, pixel by pixel.")}
<p><b>Slide 46. Common types of noise:</b></p>
<ul><li><b>Salt-and-pepper noise:</b> random occurrences of black and white pixels.</li><li><b>Impulse noise:</b> random occurrences of white pixels.</li>
<li><b>Gaussian noise:</b> variations in intensity drawn from a Gaussian (normal) distribution.</li></ul>
<p>Filtering is useful for noise reduction: <b>median for salt-and-pepper/impulse</b>, <b>Gaussian (or mean) for Gaussian noise</b>.</p>
"""))

# ================================================================ 8. coefficient masks
t5 = [[10, 20, 30, 40, 50], [11, 21, 31, 41, 51], [12, 22, 32, 42, 52], [13, 23, 33, 43, 53], [14, 24, 34, 44, 54]]
idm = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
shm = [[0, 0, 0], [0, 0, 1], [0, 0, 0]]
id_out = [[corr(t5, idm, r, c) for c in range(1, 4)] for r in range(1, 4)]
sh_out = [[corr(t5, shm, r, c) for c in range(1, 4)] for r in range(1, 4)]

S.append(sec("coef", "Coefficient masks: predict the output", "47–54", EXAM, f"""
<p><b>Slide 47.</b> A 3×3 mask with coefficients w<sub>1</sub> … w<sub>9</sub> covers pixels z<sub>1</sub> … z<sub>9</sub>. The response is the sum of products:</p>
{formula("z = z<sub>1</sub>w<sub>1</sub> + z<sub>2</sub>w<sub>2</sub> + … + z<sub>9</sub>w<sub>9</sub> = Σ z<sub>i</sub>w<sub>i</sub>")}
{paper("SP23 Q2(f)ii · slides 48–49", "3 marks", f'''
<p class="q">An image is convolved with the 3×3 mask [0 0 0; 0 1 0; 0 0 0]. What is the relation between the original and the modified image?</p>
<p>At every pixel, g(x,y) = 0·z<sub>1</sub> + … + 1·z<sub>5</sub> + … + 0·z<sub>9</sub> = z<sub>5</sub> = f(x,y). Only the centre coefficient is 1, and it multiplies the pixel itself.</p>
<p>So <b>g(x,y) = f(x,y)</b>: the output is identical to the original (no change). This mask is the identity, also called the unit impulse. Its coefficients add to 1, so brightness is kept, and no neighbour is mixed in, so nothing is blurred or shifted.</p>
{mats(mat(t5, "test image", small=True), mat(idm, "mask"), mat(id_out, "output (inner 3×3) = same values", small=True))}
''')}
{paper("Slides 50–51 · mask [0 0 0; 0 0 1; 0 0 0]", "worked", f'''
<p>Now the 1 sits to the right of centre, so g(x,y) = f(x, y+1): each output pixel takes the value of its <b>right-hand neighbour</b>. The picture <b>shifts left by 1 pixel</b>.</p>
{mats(mat(t5, "test image", small=True), mat(shm, "mask"), mat(sh_out, "output (inner 3×3)", small=True))}
<p>The output at the position of 21 is 31 (the value to its right): every value moved one column to the left.</p>
''')}
{sim({"type": "filter", "images": ["t5"], "filters": ["identity", "shift", "sharpen"], "pad": "zero"}, "identity, shift and the 2δ − box sharpener on the test image.")}
{paper("Slides 52–54 · [0 0 0; 0 2 0; 0 0 0] − 1/9 [all 1]", "worked", f'''
<p>2 × (identity) − (mean) gives g = 2f − f̄ = f + (f − f̄), where f̄ is the local average.</p>
<p>f − f̄ is the detail (how much a pixel differs from its neighbourhood). Adding it back makes differences bigger: a <b>sharpening filter</b> that "emphasizes differences with the local average". Its coefficients still add to 2 − 1 = 1, so flat areas keep their brightness.</p>
{mats(mat([[40, 40, 70]] * 3, "dark-side pixel 40", ctr=(1, 1)), mat([[40, 70, 70]] * 3, "bright-side pixel 70", ctr=(1, 1)))}
<p>Dark side: mean = (6×40 + 3×70)/9 = 450/9 = 50, so g = 2×40 − 50 = <b>30</b>. Bright side: mean = (3×40 + 6×70)/9 = 540/9 = 60, so g = 2×70 − 60 = <b>80</b>.</p>
<p>The edge 40 | 70 became 30 | 80: the jump is bigger, so the edge looks sharper. This is the idea behind unsharp masking in deck 07.</p>
''')}
"""))

# ================================================================ 9. applications
S.append(sec("apps", "More applications: template matching", "55–56", SHORT, """
<p><b>Slide 56.</b> Cross-correlation is useful for <b>template matching</b>, i.e. locating a given pattern in an image. Slide the template H over the image F; wherever the image patch looks like the template, the sum of products is large. The <b>highest value yields the location of the pattern</b> in the image.</p>
"""))

# ================================================================ 10. past questions
f23 = [[0, 12, 0, 0, 23], [255, 145, 200, 110, 17], [255, 160, 90, 250, 15], [0, 255, 130, 185, 15], [15, 20, 20, 21, 21]]
w23 = win(f23, 1, 1)
avg3 = [[2, 5, 8], [5, 1, 3], [4, 7, 2]]
avg_rows, avg_out = [], []
for r in range(3):
    row = []
    for c in range(3):
        w = win(avg3, r, c)
        avg_rows.append([f"({r},{c})", " + ".join(map(str, flat(w))), f"{sum(flat(w))}/9 = {sum(flat(w)) / 9:.2f}", rhu(sum(flat(w)) / 9)])
        row.append(rhu(sum(flat(w)) / 9))
    avg_out.append(row)
med4 = [[0, 2, 1, 0], [5, 2, 3, 8], [0, 1, 3, 4], [3, 0, 7, 2]]
med_rows, med_out = [], [[0] * 4 for _ in range(4)]
for r in (1, 2):
    for c in (1, 2):
        v = sorted(flat(win(med4, r, c)))
        med_rows.append([f"({r},{c})", ", ".join(map(str, v)), v[4]])
        med_out[r][c] = v[4]
f21 = [[7, 1, 0, 5], [6, 3, 6, 2], [6, 4, 4, 1], [1, 5, 7, 0]]
lap_p = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
lap_n = [[0, -1, 0], [-1, 4, -1], [0, -1, 0]]
sp25 = [[7, 7, 7, 7, 7, 7, 7], [7, 7, 7, 2, 7, 7, 7], [7, 5, 0, 0, 0, 5, 7], [5, 1, 1, 0, 1, 1, 5], [5, 5, 0, 0, 0, 5, 5], [3, 3, 3, 2, 3, 3, 3], [7, 7, 7, 7, 7, 7, 7]]
four = [[0, 1, 0], [1, 0, 1], [0, 1, 0]]

def window_answer(img, r, c, what):
    w = win(img, r, c)
    parts = [show_window(img, r, c, f"window at ({r},{c}); zero padding outside")]
    for kind in what:
        if kind == "mean":
            l, v = mean_line(w); parts.append(f"<p><b>3×3 mean:</b> {l} ≈ <b>{rhu(v)}</b></p>")
        elif kind == "median":
            l, v = med_line(w); parts.append(f"<p><b>3×3 median:</b> {l}</p>")
        elif kind == "max":
            parts.append(f"<p><b>3×3 max:</b> sorted {', '.join(map(str, sorted(flat(w))))} → largest = <b>{max(flat(w))}</b></p>")
        elif kind in ("lapP", "lapN"):
            m = lap_p if kind == "lapP" else lap_n
            parts.append(mats(mat(w, "window"), mat(m, ("positive" if kind == "lapP" else "negative") + " Laplacian")))
            parts.append(f"<p><b>Laplacian response:</b> {mask_line(w, m)[0]}</p>")
    return "".join(parts)

S.append(sec("pq", "Past questions, solved in full", "17–46", EXAM, f"""
<p>Coordinates: (row, column), counted from 0 at the top-left, as in the slides' origin. Zero padding unless the question says otherwise.</p>
{paper("F23 Q2(b) · aust.png", "6 marks", f'''
<p class="q">aust.png (5×5) has random 0 and 255 pixels; zero padding. (i) Which noise affects aust.png? (ii) Apply a 3×3 mean and a 3×3 median filter at point (1,1). (iii) Is it possible to remove the noise using only a Max or a Min filter? Justify. [1+3+2]</p>
<p><b>(i)</b> The image has random black (0) and white (255) pixels scattered among normal values: <b>salt-and-pepper (impulse) noise</b>.</p>
<p><b>(ii)</b></p>
{window_answer(f23, 1, 1, ["mean", "median"])}
<p>The mean (124) is dragged by the two 255s and the 0s; the median (145) is a real neighbouring value, and the extremes end up at the two ends of the sorted list.</p>
<p><b>(iii) No.</b> A <b>max</b> filter picks the largest value, so it removes pepper (0) but spreads salt (255) to every neighbour of a white dot. A <b>min</b> filter removes salt but spreads pepper. Salt-and-pepper noise contains both at once, so either filter alone makes half of the noise worse. The <b>median</b> filter removes both, because both extremes are pushed to the ends of the sorted list.</p>
''')}
{sim({"type": "filter", "images": ["aust"], "filters": ["mean", "median", "max", "min"], "pad": "zero", "start": [1, 1]}, "F23 aust.png. Opens at (1,1); try all four filters.")}
{paper("SP23 Q3(f) i–ii · SP22 Q1(a)ii", "3 + 3 marks", f'''
<p class="q">(i) Smooth the 3×3 image [2 5 8; 5 1 3; 4 7 2] with a 3×3 average filter, zero padding; show the calculations. (ii) Apply a 3×3 median filter to the 4×4 image; ignore the border and put zero in the output border.</p>
<p><b>(i)</b> Pad with a ring of zeros, then average every 3×3 window:</p>
{mat([[0] * 5] + [[0] + r + [0] for r in avg3] + [[0] * 5], "zero-padded input", pad={(i, j) for i in range(5) for j in range(5) if i in (0, 4) or j in (0, 4)}, small=True)}
{tbl(["pixel", "sum of the 9 values in its window", "average", "rounded"], avg_rows, "narrow")}
{mats(mat(avg3, "input"), mat(avg_out, "smoothed output (rounded)"))}
<p><b>(ii)</b> Only the 4 inner pixels have a full window:</p>
{mat(med4, "input", hi={(1, 1), (1, 2), (2, 1), (2, 2)})}
{tbl(["pixel", "sorted window", "median"], med_rows, "narrow")}
{mat(med_out, "median output (border = 0)")}
<p>(Part iii, the single-pass Laplacian, is on the deck 07 page.)</p>
''')}
{sim({"type": "filter", "images": ["avg3"], "filters": ["mean"], "pad": "zero"}, "SP23 (i): all 9 pixels with zero padding.")}
{sim({"type": "filter", "images": ["med4"], "filters": ["median"], "pad": "discard"}, "SP23 (ii): the 4 inner pixels, border ignored.")}
{paper("SP22 Q1(a) i, iii", "2 + 3 marks", f'''
<p class="q">(i) Explain with an example how a spatial filter affects an image. (iii) Why does the median filter preserve more edge sharpness than the average filter?</p>
<p><b>(i)</b> A spatial filter consists of a neighbourhood and a predefined operation. The mask is moved from pixel to pixel; at each position the response, the sum of products of mask coefficients and the pixels under them, becomes the new value of the centre pixel. Example: with the 1/9 mean mask, the pixel 94 in the slide-19 image becomes (110+120+90+91+94+98+90+91+99)/9 = 98.1. Applied everywhere, sharp features and noise are averaged out and the image looks smoother (blurred).</p>
<p><b>(iii)</b> At an edge the 3×3 window holds pixels from both sides. The <b>average</b> mixes them, so it outputs an in-between value that did not exist in the image: the step becomes a ramp and the edge blurs. The <b>median</b> outputs one of the actual pixel values: whichever side has the majority (5 or more of the 9 pixels) wins, so pixels stay on their own side and the step stays a step. It also ignores a single extreme value instead of averaging it in. <i>[Draw the 1-D step figure above.]</i></p>
''')}
{paper("F21 B4(a)", "8 marks", f'''
<p class="q">3-bit 4×4 image, Laplacian [0 1 0; 1 −4 1; 0 1 0], zero padding. (i) 3×3 mean filter at (2,2) (ii) 3×3 median at (0,0) (iii) Laplacian at (1,1) (iv) Why does the median preserve more edge sharpness than the mean?</p>
<p><b>(i)</b></p>{window_answer(f21, 2, 2, ["mean"])}
<p><b>(ii)</b></p>{window_answer(f21, 0, 0, ["median"])}
<p>Five of the nine values are padding zeros, so the median is 0 (this is why zero padding darkens corners).</p>
<p><b>(iii)</b></p>{window_answer(f21, 1, 1, ["lapP"])}
<p><b>(iv)</b> Same answer as SP22 (iii): the median picks a real value from the majority side of the edge, while the mean blends both sides into a new in-between value.</p>
''')}
{sim({"type": "filter", "images": ["f21"], "filters": ["mean", "median", "lappos"], "pad": "zero", "start": [2, 2]}, "F21: opens at (2,2) for the mean; click (0,0) for the median, (1,1) for the Laplacian.")}
{paper("SP25 Q2(b)ii · Tasks 1 and 3", "2 + 2 marks", f'''
<p class="q">At point (3,2) of the reconstructed 7×7 image: Task 1, perform a 3×3 Max filter. Task 3, design a 3×3 spatial mask that averages the 4 neighbours of a point (x,y) but excludes the point itself.</p>
<p>Original image (rebuilt from bit planes; see the deck 04 page):</p>
<p><b>Task 1</b></p>{window_answer(sp25, 3, 2, ["max"])}
<p><b>Task 2</b> (negative Laplacian, deck 07):</p>{window_answer(sp25, 3, 2, ["lapN"])}
<p><b>Task 3.</b> The 4 neighbours are up, down, left and right. Give each weight 1, the centre 0, the corners 0, and divide by 4 so the weights add to 1:</p>
{mat(four, "1/4 ×")}
{formula("g(x,y) = ¼ [ f(x−1,y) + f(x+1,y) + f(x,y−1) + f(x,y+1) ]")}
''')}
{sim({"type": "filter", "images": ["sp25"], "filters": ["max", "lapneg", "four"], "pad": "zero", "start": [3, 2]}, "SP25 at (3,2): max, negative Laplacian, and the 4-neighbour mask.")}
{paper("SP24 Q2(b)ii · same image, point (3,3)", "6 marks", f'''
<p class="q">At (3,3): Task 1, 3×3 Max filter; Task 2, 3×3 positive Laplacian; Task 3, the 4-neighbour averaging mask.</p>
<p><b>Task 1</b></p>{window_answer(sp25, 3, 3, ["max"])}
<p><b>Task 2</b></p>{window_answer(sp25, 3, 3, ["lapP"])}
<p><b>Task 3:</b> the same mask 1/4 [0 1 0; 1 0 1; 0 1 0] as above.</p>
''')}
{sim({"type": "filter", "images": ["sp25"], "filters": ["max", "lappos", "four"], "pad": "zero", "start": [3, 3]}, "SP24 at (3,3).")}
{paper("F22 A1(a)", "3 + 6 marks", '''
<p class="q">(i) Explain how you can smooth an image. If you subtract the smoothed image from the original, what happens if you add the result back to the original? (ii) Group selfies of batch "Integer 43" suffer from salt-and-pepper noise. Apply a de-noising process: which filtering is most effective, and how does it improve the photos?</p>
<p><b>(i)</b> Smooth by convolving the image with a low-pass mask whose coefficients add to 1, e.g. the 3×3 mean 1/9 [all 1] or the weighted 1/16 [1 2 1; 2 4 2; 1 2 1]. Each pixel becomes the (weighted) average of its neighbourhood, which blurs and reduces noise.</p>
<p>Original − smoothed = the <b>detail</b> (mask) image: it holds only edges and fine detail, since the smooth parts cancel out. Adding this detail back to the original, g = f + (f − f̄), <b>sharpens</b> the image: edges and fine detail are emphasized. This is <b>unsharp masking</b> (with a weight k &gt; 1 on the detail, high-boost filtering; see deck 07). It is the same as the slide 52–54 mask 2δ − box.</p>
<p><b>(ii)</b> Use a <b>3×3 median filter</b>.</p>
<ul><li>Salt-and-pepper noise is random black (0) and white (255) dots. In each 3×3 window these extremes sort to the two ends of the list, so the median, a real neighbouring value, replaces them.</li>
<li>Unlike the mean filter, the median does not smear the dots into gray blotches, and it keeps the edges of faces, eyes and hair sharp, because it never creates new in-between values.</li>
<li>It introduces no new values and is very effective for impulse noise (slides 43–44). If the noise is dense, a second pass or a 5×5 median removes what's left, at the cost of a little extra blur.</li>
<li>Result: clean skin and background, sharp facial features, and natural-looking group photos.</li></ul>
''')}
{paper("SP24 Q3(a)i", "4 marks", '''
<p class="q">An image is corrupted by salt-and-pepper noise in the object part only (not the background). Give the best way to denoise it and explain.</p>
<p>Use a <b>median filter</b> (3×3), applied to the object region. Salt-and-pepper noise consists of isolated extreme values (0 and 255). The median of each window ignores them, since they sort to the ends, and replaces each noisy pixel with a real value from its neighbourhood. It keeps the object's edges sharp, unlike the mean, which would blur the object boundary and smear the dots.</p>
<p>Because the background is clean, the filter can be restricted to the object (e.g. a mask from thresholding), so the background stays untouched and no extra blur is added there. Part (ii), morphological removal, is on the morphology page.</p>
''')}
"""))

S.append(sec("traps", "Traps and one-minute sheet", "all", None, f"""
<ul class="traps">
<li>Write the <b>whole 3×3 window</b> (with padding zeros) before computing. Most lost marks are a wrong neighbour.</li>
<li>Mean: divide by <b>9</b>; weighted: divide by <b>16</b> (the sum of the weights).</li>
<li>Median: <b>sort all 9 values</b> and take the 5th. Don't take the middle of the unsorted window.</li>
<li>At corners with zero padding, 5 of 9 values are 0, so the median there is usually 0.</li>
<li>Check your additions: even slide 35's printed sum is off.</li>
<li>Salt-and-pepper → <b>median</b>. Gaussian noise → <b>Gaussian/mean</b>. Max alone removes pepper only; min alone removes salt only.</li>
</ul>
{tbl(["filter", "mask / rule", "good for", "side effect"], [
    ["mean (box)", "1/9 [all 1]", "general noise", "blurs edges"], ["weighted average", "1/16 [1 2 1; 2 4 2; 1 2 1]", "noise, gentler", "less blur"],
    ["Gaussian", "bell-shaped weights, σ sets spread", "Gaussian noise", "blur grows with σ"], ["median", "5th of 9 sorted", "salt-and-pepper, impulse", "keeps edges, slight blur"],
    ["min / max", "smallest / largest", "salt / pepper only", "spreads the other"], ["identity", "[0 0 0; 0 1 0; 0 0 0]", "—", "no change"],
    ["shift", "[0 0 0; 0 0 1; 0 0 0]", "—", "moves image left 1 pixel"]])}
"""))

# ================================================================ step-by-step simulators (shared kit)
s8 = [[5, 2, 6, 8, 2, 0, 1, 2], [4, 3, 4, 5, 1, 9, 6, 3], [3, 9, 2, 4, 7, 7, 6, 9], [1, 3, 4, 6, 8, 2, 2, 1],
      [8, 4, 6, 2, 3, 1, 8, 8], [5, 8, 9, 0, 1, 0, 2, 3], [9, 2, 6, 6, 3, 6, 2, 1], [9, 8, 8, 2, 6, 3, 4, 5]]
IMAGES = {
    "s19": {"name": "Slides 19 & 35 · 4×4", "img": m19, "note": "The pixel 94: mean 883/9 = 98.1 (slide 19); weighted 1565/16 = 97.8 (slide 35)."},
    "s42": {"name": "Slide 42 · 4×4", "img": m42, "note": "The pixel 94: sorted 90, 90, 91, 94, 95, 98, 99, 110, 120 → median 95."},
    "box": {"name": "Slides 20–27 · 10×10 box", "img": box, "note": "Border discarded: 64 positions. Watch the box edge turn into a ramp 0, 10, 20, 30."},
    "s8": {"name": "Slide 8 · 8×8 source", "img": s8, "note": "First position: (−1×5) + (0×2) + (1×6) + (2×4) + (1×3) + (2×4) + (1×3) + (−2×9) + (0×2) = 5."},
    "border5": {"name": "Slides 28–31 · 5×5", "img": b, "note": "Starts on the 8 in the top row. Switch the Border menu to see zero padding, replication and discard."},
    "aust": {"name": "F23 Q2(b) · aust.png", "img": f23, "note": "Point (1,1): mean 1117/9 = 124.1, median 145. Try max and min to see why they fail on salt-and-pepper."},
    "avg3": {"name": "SP23 Q3(f)i · SP22 Q1(a)ii · 3×3", "img": avg3, "note": "Every pixel with zero padding: output 1 3 2 / 3 4 3 / 2 2 1."},
    "med4": {"name": "SP23 Q3(f)ii · 4×4", "img": med4, "note": "Border ignored: the 4 inner pixels give 2, 2, 3, 3."},
    "f21": {"name": "F21 B4(a) · 4×4", "img": f21, "note": "(i) mean at (2,2) = 32/9 → 4. (ii) click (0,0) with median → 0. (iii) positive Laplacian at (1,1) → 5."},
    "sp": {"name": "Slide 45 · salt-and-pepper 7×7", "img": sp_n, "note": "Median removes every 0 and 255; switch to mean to see the noise smeared instead."},
    "sp25": {"name": "SP25 / SP24 Q2(b) · 7×7", "img": sp25, "note": "SP25 at (3,2): max 5, negative Laplacian 3. SP24 at (3,3): max 1, positive Laplacian 2."},
    "t5": {"name": "Slides 48–51 · test 5×5", "img": t5, "note": "Identity copies each pixel; shift takes the right-hand neighbour; sharpen pushes pixels away from their local mean."},
}
ALL_IMG = list(IMAGES)
SMOOTH = ["mean", "weighted", "median", "min", "max", "four", "identity", "shift", "sharpen", "slide8", "lappos", "lapneg"]
S.insert(1, sec("sim", "Simulator: any image, any filter", "8–54", EXAM,
                idea("Pick an image and a filter, then press <b>Next step</b>. Each pixel takes 4 steps: <b>place</b> the window, <b>multiply</b> (or <b>sort</b>), <b>add</b> (or <b>pick</b>), <b>write</b>. Nothing is skipped. ← and → keys step too; click any input pixel to jump there; Play runs it. Smaller simulators also sit next to each method below.")
                + sim({"type": "filter", "images": ALL_IMG, "filters": SMOOTH, "pad": "zero", "start": [1, 1]})))

toc = [("start", "Start"), ("sim", "Simulator"), ("eq", "Correlation"), ("types", "Types & masks"), ("mean", "Mean"), ("border", "Borders"), ("gauss", "Gaussian"),
       ("median", "Median"), ("coef", "Coefficient masks"), ("apps", "Template"), ("pq", "Past papers"), ("traps", "Traps")]
OUT.write_text(page("DIP Deck 06 Lesson", "CSE 4227 · Chapter 3 · Deck 06", "Smoothing Spatial Filters, from zero",
                    "Every slide you need, in plain words, with each window drawn and every past-paper filtering question solved the way you write it in the answer script.",
                    toc, S, extra=sim_assets(IMAGES)), encoding="utf-8")

# ---------------------------------------------------------------- self-check against data/answers.json and the slides
assert sum(flat(w19)) == 883 and wsum == 1565
assert box_out[0][:4] == [0, 10, 20, 30] and box_out[5][3] == 50 and box_out[3][5] == 90
assert sorted(flat(win(m42, 1, 1)))[4] == 95 and sorted(flat(m43))[4] == 27
assert sum(flat(w23)) == 1117 and sorted(flat(w23))[4] == 145
assert avg_out == [[1, 3, 2], [3, 4, 3], [2, 2, 1]] and med_out == [[0, 0, 0, 0], [0, 2, 2, 0], [0, 3, 3, 0], [0, 0, 0, 0]]
assert sum(flat(win(f21, 2, 2))) == 32 and sorted(flat(win(f21, 0, 0)))[4] == 0 and corr(f21, lap_p, 1, 1) == 5
assert max(flat(win(sp25, 3, 2))) == 5 and corr(sp25, lap_n, 3, 2) == 3 and max(flat(win(sp25, 3, 3))) == 1 and corr(sp25, lap_p, 3, 3) == 2
assert all(abs(med_in[i][j] - orig_in[i][j]) <= 1 for i in range(5) for j in range(5))
print(OUT, OUT.stat().st_size, "box", box_out, "med", med_in, "mean", mean_in)
