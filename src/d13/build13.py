"""Builds deck13_lesson.html: image compression lesson. All numbers computed here."""
import sys, pathlib
from collections import Counter
from fractions import Fraction as F
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from kit import *

OUT = pathlib.Path(__file__).with_name("deck13_lesson.html")
log2 = math.log2


def tr(x, d=4):
    s = f"{float(x):.{d}f}".rstrip("0").rstrip(".")
    return s if s else "0"


# ---------------------------------------------------------------- Huffman (slides 29-35 rules, same as sim_kit.js)
def huff(syms, w):
    leaves = [{"sym": s, "w": x} for s, x in zip(syms, w)]
    start = sorted(leaves, key=lambda n: -n["w"])  # stable: ties keep the given order
    lists, merges, cur = [start], [], start[:]
    while len(cur) > 2:
        a, b = cur[-2], cur[-1]
        node = {"w": a["w"] + b["w"], "kids": (a, b)}
        cur = cur[:-2]
        pos = next((i for i, n in enumerate(cur) if n["w"] < node["w"]), len(cur))
        cur.insert(pos, node)
        merges.append(node)
        lists.append(cur[:])
    cur[0]["code"], cur[1]["code"] = "0", "1"
    for m in reversed(merges):
        m["kids"][0]["code"], m["kids"][1]["code"] = m["code"] + "0", m["code"] + "1"
    return {"lists": lists, "leaves": leaves, "code": {n["sym"]: n["code"] for n in leaves}}


def huff_block(syms, w, D, bits=None, label=lambda s: s):
    """Paper-style Huffman answer: source reduction table, code table, Lavg, H, efficiency, (CR, RD)."""
    R = huff(syms, w)
    p = lambda n: tr(F(n["w"], D))
    head = ["Symbol", "Probability", "Code"] + [f"Reduction {j}" for j in range(1, len(R["lists"]))]
    rows = []
    for i, n0 in enumerate(R["lists"][0]):
        row = [label(n0["sym"]), p(n0), f"<b>{n0['code']}</b>"]
        for L in R["lists"][1:]:
            row.append(f"{p(L[i])} &nbsp;<code>{L[i]['code']}</code>" if i < len(L) else "")
        rows.append(row)
    leaves = R["leaves"]
    W = sum(w)
    lavg = F(sum(n["w"] * len(n["code"]) for n in leaves), W)
    H = -sum((n["w"] / W) * log2(n["w"] / W) for n in leaves if n["w"])
    terms = " + ".join(f"({p(n)})({len(n['code'])})" for n in leaves)
    o = ["<p><b>Step 1</b>, sort the probabilities largest first. <b>Steps 2–4</b>, add the two smallest and re-sort, until two values are left "
         "(a sum that ties with an existing value goes below it). <b>Step 5</b>, walk back from the last column: upper branch 0, lower branch 1.</p>",
         tbl(head, rows, "narrow"),
         tbl(["Symbol", "Probability p", "Code", "Length l", "p × l"], [[label(n["sym"]), p(n), n["code"], len(n["code"]), tr(F(n["w"], D) * len(n["code"]))] for n in leaves], "narrow"),
         f"<p><b>Average length</b> L<sub>avg</sub> = Σ l·p = {terms} = <b>{tr(lavg)}</b> bits/symbol.</p>",
         f"<p><b>Entropy</b> H = −Σ p log<sub>2</sub> p = {' + '.join(f'−({p(n)})log<sub>2</sub>({p(n)})' for n in leaves if n['w'])} = <b>{H:.4f}</b> bits/symbol.</p>",
         f"<p><b>Coding efficiency</b> η = H / L<sub>avg</sub> = {H:.4f} / {tr(lavg)} = <b>{100 * H / float(lavg):.2f}%</b>.</p>"]
    info = {"code": R["code"], "lavg": lavg, "H": H}
    if bits:
        C = bits / float(lavg)
        o.append(f"<p><b>Compression ratio</b> C<sub>R</sub> = n<sub>1</sub>/n<sub>2</sub> = {bits} / {tr(lavg)} = <b>{C:.4f}</b>. "
                 f"<b>Relative redundancy</b> R<sub>D</sub> = 1 − 1/C<sub>R</sub> = 1 − 1/{C:.4f} = <b>{1 - 1 / C:.4f}</b> → {100 * (1 - 1 / C):.2f}% of the data was redundant.</p>")
        info.update(C=C, RD=1 - 1 / C)
    return "".join(o), info


def image_counts(img):
    flat = [v for r in img for v in r]
    c = Counter(flat)
    syms = sorted(c, key=lambda s: (-c[s], s))
    return flat, c, syms


def freq_table(img):
    flat, c, syms = image_counts(img)
    N = len(flat)
    return tbl(["Symbol (gray level)", "Count", "Probability = count/N"], [[s, c[s], f"{c[s]}/{N} = {tr(F(c[s], N))}"] for s in syms], "narrow"), syms, [c[s] for s in syms], N


def huff_sim(syms, w, D=None, bits=None, as_count=False, cap=""):
    return sim({"type": "huff", "syms": [str(s) for s in syms], "w": list(w), "D": D, "bits": bits, "asCount": as_count}, cap)


# ---------------------------------------------------------------- LZW (slides 77-95)
def lzw(seq):
    dic, nxt, rows, out, crs = {}, 256, [], [], ""
    has = lambda s: ("-" not in s and int(s) < 256) or s in dic
    code_of = lambda s: int(s) if "-" not in s else dic[s]
    for px in seq:
        cand = str(px) if crs == "" else f"{crs}-{px}"
        if has(cand):
            rows.append([crs, px, "", "", ""]); crs = cand
        else:
            c = code_of(crs); out.append(c); dic[cand] = nxt
            rows.append([crs, px, c, nxt, cand]); nxt += 1; crs = str(px)
    out.append(code_of(crs)); rows.append([crs, "", code_of(crs), "", ""])
    return rows, out


def lzw_block(img):
    seq = [v for r in img for v in r]
    rows, out = lzw(seq)
    n, k = len(seq), len(out)
    return ("<p>Dictionary locations 0–255 already hold the 256 single gray levels; new sequences go from location 256. Read the pixels left to right, top to bottom. "
            "For each pixel: if <i>currently recognized sequence + pixel</i> is in the dictionary, keep growing it; otherwise output the code of the recognized sequence, "
            "add the longer sequence to the dictionary, and restart from the pixel.</p>"
            + tbl(["Currently recognized sequence", "Pixel being processed", "Encoded output", "Dictionary location (code word)", "Dictionary entry"], rows, "narrow")
            + f"<p><b>Encoded output:</b> {' '.join(map(str, out))} ({k} code words).</p>"
            + f"<p>Original = {n} pixels × 8 bits = <b>{8 * n}</b> bits. Compressed = {k} codes × 9 bits = <b>{9 * k}</b> bits. "
              f"C<sub>R</sub> = {8 * n}/{9 * k} = <b>{8 * n / (9 * k):.4f}</b>{' (compression achieved)' if 8 * n > 9 * k else ' (no compression)'}.</p>"), out


# ---------------------------------------------------------------- arithmetic (slides 56-63)
def arith_block(syms, probs, msg):
    P = [F(p) for p in probs]
    lo, acc = [], F(0)
    for p in P:
        lo.append(acc); acc += p
    L, H = F(0), F(1)
    rows = []
    for s in msg:
        i = syms.index(s); w = H - L
        nL, nH = L + w * lo[i], L + w * (lo[i] + P[i])
        rows.append([s, f"[{tr(L, 8)}, {tr(H, 8)})", tr(w, 8), f"{tr(L, 8)} + {tr(w, 8)}×{tr(lo[i])} = <b>{tr(nL, 8)}</b>", f"{tr(L, 8)} + {tr(w, 8)}×{tr(lo[i] + P[i])} = <b>{tr(nH, 8)}</b>"])
        L, H = nL, nH
    d = 1
    while True:
        q = F(math.ceil(L * 10 ** d), 10 ** d)
        if q < H:
            break
        d += 1
    out = (tbl(["Symbol", "Probability", "Initial sub-interval"], [[s, tr(p), f"[{tr(a)}, {tr(a + p)})"] for s, p, a in zip(syms, P, lo)], "narrow")
           + "<p>For each symbol: width = high − low; new low = low + width × (symbol's low end); new high = low + width × (symbol's high end).</p>"
           + tbl(["Symbol", "Current interval", "Width", "New low", "New high"], rows, "narrow")
           + f"<p><b>Final interval:</b> [{tr(L, 8)}, {tr(H, 8)}). Any number in it encodes the message. Shortest decimal: <b>{tr(q, 8)}</b>.</p>")
    return out, (L, H, q)


def arith_sim(syms, probs, msg, cap):
    return sim({"type": "arith", "syms": syms, "probs": probs, "msg": [syms.index(s) for s in msg]}, cap)


# ---------------------------------------------------------------- RLE
def runs(row):
    out = []
    for v in row:
        if out and out[-1][0] == v:
            out[-1][1] += 1
        else:
            out.append([v, 1])
    return out


def rle_block(img, bits):
    R = [runs(r) for r in img]
    npairs = sum(len(r) for r in R)
    N = len(img) * len(img[0])
    return (tbl(["Row", "(gray level, run length) pairs"], [[f"Row {i + 1}", "  ".join(f"({a},{b})" for a, b in r)] for i, r in enumerate(R)], "narrow")
            + f"<p>{npairs} pairs = {2 * npairs} numbers, each stored in {bits} bits. Original = {len(img)}×{len(img[0])}×{bits} = <b>{N * bits}</b> bits. "
              f"RLE = {2 * npairs}×{bits} = <b>{2 * npairs * bits}</b> bits. C<sub>R</sub> = {N * bits}/{2 * npairs * bits} = <b>{N / (2 * npairs):.4f}</b>.</p>"), N / (2 * npairs)


def golomb(n, m):
    q, k = n // m, math.ceil(log2(m)) if m > 1 else 0
    c, r = 2 ** k - m, n % m
    if r < c:
        rb = format(r, f"0{k - 1}b") if k > 1 else ""
        why = f"r = {r} &lt; c = {c} → r in k − 1 = {k - 1} bits = {rb}"
    else:
        rb = format(r + c, f"0{k}b") if k > 0 else ""
        why = f"r = {r} ≥ c = {c} → r + c = {r + c} in k = {k} bits = {rb if rb else '(nothing)'}"
    return "1" * q + "0" + rb, q, k, c, r, why


S = []

# ================================================================ 1. why
S.append(sec("start", "Start here: why compress, and data vs information", "3–7", EXAM, f"""
{idea("A picture holds some <b>information</b>, but a file stores <b>data</b> (bits). The same information can be stored with many or few bits. Compression finds the bits that are repeated or not needed and drops them, so the picture takes less space or downloads faster.")}
<p><b>Slide 3.</b> <b>Data compression</b> is the process of reducing the amount of <b>data</b> required to represent a given quantity of <b>information</b>. Data and information are not the same thing: various amounts of data can represent the same information. Data that is <b>irrelevant or repeated</b> is called <b>data redundancy</b>.</p>
<p><b>Slide 4.</b> The goal of image compression is to reduce the amount of data required to represent a digital image. It is very important for <b>image storage</b> and <b>image transmission</b>. Compression is achieved by <b>encoding data</b> with an appropriate encoding scheme.</p>
<p><b>Slide 5. Applications:</b> internet, businesses, multimedia, satellite imaging, medical imaging.</p>
{paper("Slides 6–7 · why images must be compressed", "worked", '''
<p><b>SD TV</b>, 2 hours, 720×480 colour frames at 30 frames/s, 3 bytes per pixel:</p>
<p>One second = 30 × (720 × 480) × 3 = 31,104,000 bytes ≈ <b>31 MB</b>.</p>
<p>Two hours = 31,104,000 × 60² × 2 ≈ 2.24 × 10<sup>11</sup> bytes = <b>224 GB</b>. That needs twenty-seven 8.5 GB dual-layer DVDs, so the video must be compressed by a factor of about <b>26.3</b> to fit on one DVD.</p>
<p><b>HD TV</b> (1920×1080) needs even higher compression. <b>Web images</b> of 128×128 colour take 7.0 to 0.03 s to download over 56 kbps to 12 Mbps links. A <b>1 GB flash memory</b> holds only about 41 uncompressed 8-megapixel photos.</p>
''')}
{paper("F23 Q1(d) first part · F22 A2(a) · SP22 Q5(a)i", "1–2 marks", '''
<p class="q">What is image compression? Why do we need it?</p>
<p>Image compression is the process of reducing the amount of data required to represent a digital image, by removing redundant (repeated or irrelevant) data while keeping the information.</p>
<p>We need it because raw images and videos are huge: for example a 2-hour SD video needs about 224 GB uncompressed, which is too big to store or send. Compression saves <b>storage space</b> and <b>transmission time/bandwidth</b> (internet, multimedia, satellite and medical imaging).</p>
''')}
"""))

# ================================================================ 2. CR, RD
S.append(sec("cr", "Compression ratio and relative data redundancy", "8–9", EXAM, f"""
<p><b>Slide 8.</b> Data redundancy is unnecessary or repetitive data in an image file; removing it reduces the file size without losing essential information. It is a <b>mathematically quantifiable</b> entity. If n<sub>1</sub> and n<sub>2</sub> are the numbers of information-carrying units (e.g. bits) in the original and compressed data sets:</p>
{formula("C<sub>R</sub> = n<sub>1</sub> / n<sub>2</sub> &nbsp;&nbsp;&nbsp;&nbsp; R<sub>D</sub> = 1 − 1/C<sub>R</sub>")}
{tbl(["case", "C<sub>R</sub>", "R<sub>D</sub>", "meaning"], [["n<sub>1</sub> = n<sub>2</sub>", "1", "0", "the original contains no redundant data"],
     ["n<sub>1</sub> ≫ n<sub>2</sub>", "→ ∞", "→ 1", "highly compressed, highly redundant data"], ["n<sub>1</sub> ≪ n<sub>2</sub>", "→ 0", "→ −∞", "undesirable: the 'compressed' file is bigger"]])}
<p><b>Slide 9.</b> A practical ratio such as C<sub>R</sub> = 10 (10:1) means the original has 10 bits for every 1 bit of the compressed data. Then R<sub>D</sub> = 1 − 1/10 = <b>0.9</b>: 90% of the data in the original was redundant.</p>
{paper("SP25 Q2(c)i", "1 mark", '''
<p class="q">An uncompressed grayscale image is 512×512 with 8 bits/pixel. After compression the file is 64 KB. Compute the compression ratio.</p>
<p>n<sub>1</sub> = 512 × 512 × 8 = 2,097,152 bits.</p>
<p>n<sub>2</sub> = 64 KB = 64 × 1024 bytes × 8 = 524,288 bits.</p>
<p>C<sub>R</sub> = n<sub>1</sub>/n<sub>2</sub> = 2,097,152 / 524,288 = <b>4</b>, i.e. <b>4:1</b>. (R<sub>D</sub> = 1 − 1/4 = 0.75: 75% of the original data was redundant.)</p>
''')}
{paper("SP22 Q5(a)iii · SP23 Q3(a)iii", "2 marks", '''
<p class="q">A 512×512, 8-bit image with entropy 5.3 bits/pixel is Huffman coded. What is the maximum compression that can be expected?</p>
<p>Entropy is the lower limit of the average code length: no lossless code can use fewer than H = 5.3 bits/pixel on average (slide 40). So the best possible L<sub>avg</sub> is 5.3 bits/pixel.</p>
<p>C<sub>max</sub> = 8 / 5.3 = <b>1.509</b> (about 1.51:1). In bits: 512 × 512 × 8 = 2,097,152 bits against at least 512 × 512 × 5.3 ≈ 1,389,363 bits.</p>
''')}
"""))

# ================================================================ 3. redundancies
S.append(sec("red", "The three data redundancies", "10–23", EXAM, f"""
{idea("There are three ways an image wastes bits. <b>Coding</b>: every gray level gets the same 8 bits, even the very common ones. <b>Spatial</b>: neighbouring pixels are nearly the same, so writing each one again repeats information. <b>Irrelevant</b>: some detail the eye can't see anyway. Each type has its own cure.")}
<p><b>Slide 10.</b> Three basic redundancies can be identified and exploited. Compression is achieved when one or more of them are reduced or eliminated:</p>
<ol><li><b>Coding redundancy</b> (inefficient bit usage): intensity arrays contain more bits than are needed.</li>
<li><b>Spatial / inter-pixel redundancy</b> (correlated neighbouring pixels): intensity arrays are correlated spatially.</li>
<li><b>Psychovisual redundancy</b> (irrelevant information): the array holds information that is ignored by the human visual system.</li></ol>
<h3>Coding redundancy (slides 11–16)</h3>
<p><b>Slide 11. Elements of an encoding scheme:</b> <b>code</b>, a list of symbols (letters, numbers, bits); <b>code word</b>, a sequence of symbols that represents one piece of information or gray level; <b>word length</b>, the number of symbols in each code word. Example: 3-bit binary code 0 = 000, 1 = 001, …, 7 = 111.</p>
<p>If an image uses fixed-length codes for every pixel value although some values occur far more often than others, storage is wasted.</p>
<p><b>Slide 12. Idea: variable-length coding.</b> Assign <b>shorter code words to the most probable</b> pixel values and <b>longer code words to less probable</b> ones. The process is reversible (lossless). The histogram gives the frequency of each gray level.</p>
<p><b>Slide 14.</b> With p(r<sub>k</sub>) = n<sub>k</sub>/n and l(r<sub>k</sub>) bits for r<sub>k</sub>:</p>
{formula("L<sub>avg</sub> = Σ<sub>k=0</sub><sup>L−1</sup> l(r<sub>k</sub>) p(r<sub>k</sub>) &nbsp;&nbsp;&nbsp; total bits = M N L<sub>avg</sub>")}
{paper("Slides 13–15 · fixed vs variable length", "worked", f'''
<p>A computer-generated 256×256, 8-bit image uses only four gray levels:</p>
{tbl(["r<sub>k</sub>", "p<sub>r</sub>(r<sub>k</sub>)", "Code 1", "l<sub>1</sub>", "Code 2", "l<sub>2</sub>"], [["87", "0.25", "01010111", 8, "01", 2], ["128", "0.47", "10000000", 8, "1", 1], ["186", "0.25", "11000100", 8, "000", 3], ["255", "0.03", "11111111", 8, "001", 3], ["others", "0", "—", 8, "—", 0]], "narrow")}
<p>Code 1 (fixed): 8 bits/pixel, total 256 × 256 × 8 bits.</p>
<p>Code 2 (variable): L<sub>avg</sub> = 0.25×2 + 0.47×1 + 0.25×3 + 0.03×3 = <b>1.81</b> bits; total 256 × 256 × 1.81 bits.</p>
<p>C = 8/1.81 ≈ <b>4.42</b>; R<sub>D</sub> = 1 − 1/4.42 = <b>0.774</b>: 77.4% of the data in the first image was redundant.</p>
''')}
{paper("Slide 16 · second example", "worked", f'''
{tbl(["r<sub>k</sub>", "p<sub>r</sub>(r<sub>k</sub>)", "Code 1", "l<sub>1</sub>", "Code 2", "l<sub>2</sub>"], [[f"r<sub>{k}</sub> = {k}/7" if k else "r<sub>0</sub> = 0", p, format(k, "03b"), 3, c2, len(c2)] for k, (p, c2) in enumerate(zip(["0.19", "0.25", "0.21", "0.16", "0.08", "0.06", "0.03", "0.02"], ["11", "01", "10", "001", "0001", "00001", "000001", "000000"]))], "narrow")}
<p>L<sub>avg</sub> = 2(0.19) + 2(0.25) + 2(0.21) + 3(0.16) + 4(0.08) + 5(0.06) + 6(0.03) + 6(0.02) = <b>2.7</b> bits.</p>
<p>C<sub>R</sub> = 3/2.7 = <b>1.11</b>; R<sub>D</sub> = 1 − 1/1.11 = <b>0.099</b>: 9.9% of the data was redundant.</p>
''')}
<h3>Spatial / inter-pixel redundancy (slides 17–19)</h3>
<p>When the value of a pixel can be obtained from its neighbouring pixels, the redundancy is called <b>inter-pixel or spatial redundancy</b>. Intensities of each pixel may correlate to their neighbours, so much information is unnecessarily replicated.</p>
<p><b>Slide 18.</b> A computer-generated 256×256×8 image of horizontal lines: each line has one random gray level, so the histogram is uniform (all 256 levels equally likely). Pixels are maximally correlated horizontally but independent vertically. This image <b>cannot be compressed with variable-length coding</b>.</p>
<p><b>Slide 19.</b> It can be represented as <b>run-length pairs</b> (intensity value, number of pixels with that intensity). Each of the 256 lines becomes one pair (value, 256):</p>
{formula("C = (256 × 256 × 8) / ((256 + 256) × 8) = 128 : 1")}
<h3>Psychovisual redundancy / irrelevant information (slides 20–21)</h3>
<p>Many images hold information that is ignored by the human visual system (HVS); try to remove this extraneous data. Slide 20: a 256×256×8 image that looks like one flat gray. Its histogram is a narrow spike, and it can be represented by a <b>single average gray level</b>:</p>
{formula("C = (256 × 256 × 8) / 8 = 65536 : 1")}
<p><b>Slide 21.</b> However, this coarse quantization may remove useful "invisible" information: after histogram equalization the "flat" image shows a hidden pattern.</p>
<p><b>Slide 22. Summary:</b> coding redundancy, the image does not need all 8 bits; spatial redundancy, information is unnecessarily replicated; irrelevant information, information that is not useful.</p>
<h3>Compression types (slide 23)</h3>
{tbl(["type", "removes", "methods"], [["<b>Error-free (lossless)</b>", "coding redundancy", "variable-length coding: Huffman, Golomb, arithmetic"],
     ["<b>Error-free (lossless)</b>", "spatial / inter-pixel redundancy", "LZW coding, run-length coding"], ["<b>Lossy</b>", "irrelevant (psychovisual) information", "information is lost; quality judged by fidelity criteria"]])}
{paper("SP25 Q1(d)", "4 marks", '''
<p class="q">What is data redundancy in images? Name its three main types. Discuss the redundancy type that can be overcome using variable-length code words. How do you calculate relative data redundancy?</p>
<p><b>Data redundancy</b> is unnecessary or repeated data in an image file which, when removed, reduces the file size without losing essential information. It is a mathematically quantifiable entity.</p>
<p><b>Three types:</b> (1) coding redundancy, (2) spatial / inter-pixel redundancy, (3) psychovisual redundancy (irrelevant information).</p>
<p><b>Coding redundancy</b> is overcome with variable-length codes. A fixed-length code gives every gray level the same number of bits (e.g. 8), although some levels occur much more often. Variable-length coding (e.g. Huffman) gives <b>shorter code words to more probable gray levels</b> and longer ones to rare levels, so the average length L<sub>avg</sub> = Σ l(r<sub>k</sub>) p(r<sub>k</sub>) drops below 8. Example (slide 15): L<sub>avg</sub> = 1.81 bits instead of 8. This is reversible, so lossless.</p>
<p><b>Relative data redundancy:</b> with n<sub>1</sub> and n<sub>2</sub> the bits in the original and compressed data, C<sub>R</sub> = n<sub>1</sub>/n<sub>2</sub> and <b>R<sub>D</sub> = 1 − 1/C<sub>R</sub></b>. Example: C<sub>R</sub> = 8/1.81 = 4.42 gives R<sub>D</sub> = 0.774, so 77.4% of the data was redundant.</p>
''')}
{paper("F23 Q1(d) · SP23 Q2(a) · SP22 Q5(a)ii · F22 A2(a)", "3–5 marks", '''
<p class="q">How many types of data redundancy are there in an image? Describe each briefly. How can compression be implemented? How do you calculate the percentage of redundant data after compression?</p>
<p>There are <b>three</b> types of data redundancy:</p>
<ol><li><b>Coding redundancy:</b> the code used for the gray levels has more bits than needed, e.g. every pixel stored in 8 bits although a few values dominate. Removed by variable-length coding (Huffman, Golomb, arithmetic): short codes for frequent values.</li>
<li><b>Spatial (inter-pixel) redundancy:</b> neighbouring pixels are correlated, so a pixel's value can be predicted from its neighbours and the same information is replicated. Removed by run-length coding or LZW. Example: an image of constant horizontal lines compresses 128:1 with run-length pairs.</li>
<li><b>Psychovisual (irrelevant) redundancy:</b> information the human visual system ignores. Removed by quantization (lossy). Example: a near-flat gray image stored as one average gray level, 65536:1.</li></ol>
<p><b>Implementation:</b> compression is achieved when one or more of these redundancies are reduced or eliminated, by encoding the data with a suitable scheme (compress → store/transmit → decompress).</p>
<p><b>Percentage redundant:</b> C<sub>R</sub> = n<sub>1</sub>/n<sub>2</sub>, R<sub>D</sub> = 1 − 1/C<sub>R</sub>, and the percentage of redundant data = R<sub>D</sub> × 100%. Example: C<sub>R</sub> = 10 → R<sub>D</sub> = 0.9 → 90% redundant.</p>
''')}
"""))

# ================================================================ 4. Huffman
hs = ["a2", "a6", "a1", "a4", "a3", "a5"]
hw = [40, 30, 10, 10, 6, 4]
blk35, i35 = huff_block(hs, hw, 100, bits=3)
cw_s, cw_w = ["A", "B", "C", "D", "E", "F"], [45, 13, 12, 16, 9, 5]
blkcw, icw = huff_block(cw_s, cw_w, 100, bits=3)
S.append(sec("huff", "Huffman coding", "24–38", EXAM, f"""
{idea("Huffman coding builds the best variable-length code by repeatedly merging the two rarest symbols. Rare symbols get merged many times, so they end up deep in the tree with long codes. Common symbols are merged late and get short codes.")}
<p><b>Slide 24.</b> Huffman coding is a <b>lossless</b> compression algorithm, the most popular technique for removing <b>coding redundancy</b>. It is variable-length: most frequent symbols get shorter codes, rare symbols longer codes. Widely used in JPEG. The resulting code is <b>optimal</b>.</p>
<p><b>Slide 25. Steps:</b></p>
<ol><li>Find the gray-level probabilities from the image histogram.</li><li>Order the input probabilities from largest to smallest.</li>
<li>Combine the smallest two probabilities by addition.</li><li>Go to step 2 until only two probabilities are left.</li>
<li>Working backward along the tree, generate the code by alternating assignment of 0 and 1.</li></ol>
{paper("Slides 26–34 · 3-bit image, six gray levels", "worked", "<p class=\"q\">Probabilities: a1 = 0.1, a2 = 0.4, a3 = 0.06, a4 = 0.1, a5 = 0.04, a6 = 0.3. Find the Huffman code.</p>" + blk35 +
       "<p>As on slide 34: n<sub>1</sub> = 3, n<sub>2</sub> = 2.2, C = 3/2.2 = 1.364, R<sub>D</sub> = 0.267. <b>26.7% fewer bits: coding redundancy eliminated.</b> Yes, it reduces the total bit count.</p>")}
{huff_sim(hs, hw, 100, 3, cap="every sort, merge and re-sort, then the codes passed back column by column (slides 26–33).")}
<p><b>Slide 35. Short-cut:</b> draw the tree directly: join the two smallest, label the branches 0 (upper) and 1 (lower), keep joining, then read each code from the root down.</p>
{paper("Slide 36 · Class work", "solved", "<p class=\"q\">A 3-bit grayscale image has A (dark gray) 0.45, B (medium gray) 0.13, C (light gray) 0.12, D (white) 0.16, E (black) 0.09, F (very light gray) 0.05. Find the Huffman code.</p>" + blkcw)}
{huff_sim(cw_s, cw_w, 100, 3, cap="the slide 36 class work.")}
<p><b>Slide 37. Applications:</b> file compression (ZIP, GZIP), image compression (PNG), multimedia (part of MP3 and JPEG), data transmission (efficient coding for bandwidth-limited channels).</p>
<p><b>Slide 38. Is Huffman lossless?</b> Yes. Every code word is unique and no code word is the prefix of another (prefix code), so the decoder reads the bits and recovers every symbol exactly. Nothing is thrown away; only the coding redundancy is removed.</p>
{trap("Tie rule: when the new sum equals an existing value, put the sum <b>below</b> the equal value (it is what the slide 26–33 table does). A different tie order can give different codes with the same L<sub>avg</sub>; the examiner accepts either if your table is consistent, but follow the slide to be safe.")}
"""))

# ================================================================ 5. entropy
S.append(sec("ent", "Entropy: the minimum number of bits", "39–45", EXAM, f"""
{idea("Entropy measures how unpredictable the gray levels are. If every pixel is the same, there is nothing to learn: 0 bits. If all 8 levels are equally likely, you need the full 3 bits. Entropy is the lowest average number of bits per pixel any lossless code can reach.")}
<p><b>Slide 39. Information theory.</b> A random event E with probability P(E) carries</p>
{formula("I(E) = log 1/P(E) = −log P(E)")}
<p>units of information. Higher uncertainty means higher information content. For a source of events a<sub>1</sub> … a<sub>J</sub> with probabilities P(a<sub>j</sub>), the average information per event is the <b>entropy</b>:</p>
{formula("H = −Σ<sub>j=1</sub><sup>J</sup> P(a<sub>j</sub>) log P(a<sub>j</sub>)")}
<p><b>Slide 40.</b> Treating pixel intensities as random events, the normalized histogram approximates the probabilities, and the image entropy is H̃ = −Σ P<sub>r</sub>(r<sub>k</sub>) log<sub>2</sub> P<sub>r</sub>(r<sub>k</sub>) bits/pixel. Entropy is the measure of the average information in an image, and <b>it is not possible to encode any image with fewer than H bits/pixel</b> (losslessly).</p>
{paper("Slide 41 · entropy of the 4-level image", "worked", '''
<p>H = −[0.25 log<sub>2</sub> 0.25 + 0.47 log<sub>2</sub> 0.47 + 0.25 log<sub>2</sub> 0.25 + 0.03 log<sub>2</sub> 0.03]</p>
<p>≈ −[0.25(−2) + 0.47(−1.09) + 0.25(−2) + 0.03(−5.06)] ≈ <b>1.6614 bits/pixel</b>.</p>
<p>Compare: the variable-length code used 1.81 bits, close to this limit.</p>
''')}
<p><b>Slides 42–43.</b> The star image has H = 1.6614, the random-lines image H = 8, the flat-looking image H = 1.566. Entropy (information) and visual impression are far from intuitive.</p>
{paper("Slides 44–45 · two extreme cases", "worked", '''
<p><b>Uniform distribution</b>, 3-bit image (L = 8), every level has p = 1/8: H = −Σ (1/8) log<sub>2</sub>(1/8) = <b>3</b> bits/pixel. The natural 3-bit code is already optimal; a uniform distribution has the highest entropy.</p>
<p><b>Certain event</b>, every pixel is 2: p(2) = 1, so H = −(1) log<sub>2</sub>(1) = <b>0</b> bits/pixel. The gray level is known in advance, so one value codes the whole image.</p>
''')}
"""))

# ================================================================ 6. Huffman past papers
sp25 = (["A", "B", "C", "D"], [4, 3, 2, 1])
b_sp25, i_sp25 = huff_block(*sp25, 10)
sp24 = [[180, 160, 160, 140, 120], [110, 110, 120, 140, 120], [110, 140, 120, 120, 140], [120, 160, 160, 170, 170], [170, 120, 110, 140, 110]]
ft24, s24, w24, N24 = freq_table(sp24)
b_sp24, i_sp24 = huff_block(s24, w24, N24, bits=8)
H24 = -sum((x / N24) * log2(x / N24) for x in w24)
sp23 = [[3, 10, 3, 21, 34]] * 4
ft23, s23, w23, N23 = freq_table(sp23)
b_sp23, i_sp23 = huff_block(s23, w23, N23, bits=6)
f22 = [[3, 10, 3, 24, 35], [3, 10, 10, 24, 3], [3, 10, 10, 24, 35], [3, 10, 10, 24, 35]]
ft22, s22, w22, N22 = freq_table(f22)
b_f22, i_f22 = huff_block(s22, w22, N22, bits=6)
rle22, c_rle22 = rle_block(f22, 6)
sp22 = [[18, 16, 16], [11, 11, 14], [11, 14, 16]]
ft2b, s2b, w2b, N2b = freq_table(sp22)
b_sp22, i_sp22 = huff_block(s2b, w2b, N2b, bits=8)
f21 = [[18, 16, 16, 14, 12], [11, 11, 12, 14, 12], [11, 14, 12, 12, 14], [12, 16, 16, 17, 17], [17, 12, 11, 14, 11]]
ft21, s21, w21, N21 = freq_table(f21)
b_f21, i_f21 = huff_block(s21, w21, N21, bits=8)

def img_sim(syms, w, N, bits, cap):
    return huff_sim(syms, w, N, bits, as_count=False, cap=cap)

S.append(sec("huffpq", "Huffman past questions, solved in full", "24–45", EXAM, f"""
<p>Recipe for every image question: <b>count</b> each gray level → <b>probability</b> = count/N → Huffman table → code table → L<sub>avg</sub> → entropy → C<sub>R</sub> = (original bits)/L<sub>avg</sub> → R<sub>D</sub>. Lossless? Always yes for Huffman.</p>
{paper("SP25 Q2(c) ii–iv", "1 + 2 + 4 marks", f'''
<p class="q">(ii) Encode the 1-D run AAAAABBBCCDAA with RLE (symbol, count). (iii) A row of 100 pixels alternates ABAB… (50 A, 50 B). Explain how RLE performs and compute the encoded length, the count stored as one byte. (iv) Symbols A: 0.4, B: 0.3, C: 0.2, D: 0.1. Build a Huffman code, compute the average code length and compare it with the entropy.</p>
<p><b>(ii)</b> Group equal neighbours: AAAAA | BBB | CC | D | AA → <b>(A,5) (B,3) (C,2) (D,1) (A,2)</b>. 13 symbols become 5 pairs.</p>
<p><b>(iii)</b> Every run has length 1, so the row becomes 100 pairs (A,1)(B,1)(A,1)… With 1 byte for the symbol and 1 byte for the count, encoded length = 100 × 2 = <b>200 bytes</b> against 100 bytes originally (one byte per pixel). C<sub>R</sub> = 100/200 = <b>0.5</b>: the data <b>doubles</b>. RLE performs badly here: it only helps when there are long runs; small runs result in expansion instead of compression (slide 109).</p>
<p><b>(iv)</b></p>{b_sp25}
<p>L<sub>avg</sub> = {tr(i_sp25["lavg"])} is just above H = {i_sp25["H"]:.4f}: Huffman is within {float(i_sp25["lavg"]) - i_sp25["H"]:.4f} bits of the theoretical minimum (efficiency {100 * i_sp25["H"] / float(i_sp25["lavg"]):.2f}%). A fixed-length code would need 2 bits.</p>
''')}
{huff_sim(*sp25, 10, cap="SP25 (iv).")}
{sim({"type": "rle", "img": [list("AAAAABBBCCDAA")]}, "SP25 (ii): the runs found one by one.")}
{paper("SP24 Q2(c)", "1 + 3 + 2 + 3 marks", f'''
<p class="q">5×5, 8-bit image. (i) Table of frequencies and histogram (ii) minimum number of bits per symbol (iii) Huffman code for each symbol (iv) average number of bits per symbol.</p>
{mat(sp24, "image")}
<p><b>(i)</b> N = 25.</p>{ft24}
{bars([w24[s24.index(v)] for v in sorted(s24)], labels=sorted(s24), caption="Histogram (count per gray level)", xlabel="gray level")}
<p><b>(ii)</b> 6 different gray levels appear, so a fixed-length code needs ⌈log<sub>2</sub> 6⌉ = <b>3 bits</b> per symbol. The theoretical minimum average (entropy) is H = −Σ p log<sub>2</sub> p = <b>{H24:.4f}</b> bits/symbol; no lossless code can do better.</p>
<p><b>(iii)–(iv)</b></p>{b_sp24}
''')}
{img_sim(s24, w24, N24, 8, "SP24, built from the counts (probabilities shown as count/25).")}
{paper("SP23 Q3(a)", "3 + 3 + 2 marks", f'''
<p class="q">4×5, 6-bit image, every row [3, 10, 3, 21, 34]. (i) Compress with Huffman coding and calculate the compression ratio. (ii) How much data was redundant? Was any data lost? (iii) A 512×512 8-bit image with entropy 5.3 bits/pixel is Huffman coded: maximum compression expected?</p>
<p><b>(i)</b> N = 20.</p>{ft23}{b_sp23}
<p>Original = 20 × 6 = 120 bits; Huffman = 20 × {tr(i_sp23["lavg"])} = {20 * float(i_sp23["lavg"]):.0f} bits; C<sub>R</sub> = {i_sp23["C"]:.4f}.</p>
<p><b>(ii)</b> R<sub>D</sub> = 1 − 1/{i_sp23["C"]:.0f} = {i_sp23["RD"]:.4f}: <b>{100 * i_sp23["RD"]:.1f}%</b> of the data was redundant. <b>No data was lost</b>: Huffman coding is lossless (a prefix code, decoded exactly).</p>
<p><b>(iii)</b> C<sub>max</sub> = 8/5.3 = <b>1.509</b> (see above).</p>
''')}
{img_sim(s23, w23, N23, 6, "SP23 (i).")}
{paper("F22 A3(a)", "3 + 3 + 2 marks", f'''
<p class="q">4×5, 6-bit image. (i) Compress using Huffman coding (ii) compress using run-length coding (iii) compression ratio of (i) and (ii).</p>
{mat(f22, "image")}
<p><b>(i)</b></p>{ft22}{b_f22}
<p><b>(ii)</b> Row by row (gray level, run length), each number stored in 6 bits:</p>{rle22}
<p><b>(iii)</b> Huffman: C<sub>R</sub> = 6/{tr(i_f22["lavg"])} = <b>{i_f22["C"]:.4f}</b>. RLE: C<sub>R</sub> = <b>{c_rle22:.4f}</b>, less than 1, so RLE <b>expands</b> this image (the runs are too short). Huffman is far better here.</p>
''')}
{img_sim(s22, w22, N22, 6, "F22 (i).")}
{sim({"type": "rle", "img": f22, "bits": 6}, "F22 (ii): every run, row by row.")}
{paper("SP22 Q5(b)", "3 + 2 + 1 + 2 marks", f'''
<p class="q">3×3, 8-bit image [18 16 16; 11 11 14; 11 14 16]. (i) Illustrate Huffman encoding (ii) entropy (iii) which redundancy is reduced; is it lossless? (iv) Is compression achieved? Prove it.</p>
<p><b>(i)–(ii)</b> N = 9.</p>{ft2b}{b_sp22}
<p><b>(iii)</b> Huffman reduces <b>coding redundancy</b>. It is <b>lossless</b>: each code word is unique and prefix-free, so the image is recovered exactly.</p>
<p><b>(iv)</b> Original = 9 × 8 = 72 bits. Huffman = Σ count × length = {sum(w2b[i] * len(i_sp22["code"][s]) for i, s in enumerate(s2b))} bits. C<sub>R</sub> = 72/{sum(w2b[i] * len(i_sp22["code"][s]) for i, s in enumerate(s2b))} = <b>{i_sp22["C"]:.2f}</b> &gt; 1, so yes, compression is achieved.</p>
''')}
{img_sim(s2b, w2b, N2b, 8, "SP22 Q5(b).")}
{paper("F21 B2(a)", "2 + 1 + 2 + 2 + 1 marks", f'''
<p class="q">5×5, 8-bit image. (i) Derive the entropy equation from information theory (ii) entropy (iii) Huffman codes (iv) compression ratio against 8-bit fixed length (v) relative data redundancy.</p>
<p><b>(i)</b> An event E with probability P(E) carries I(E) = log<sub>2</sub>(1/P(E)) = −log<sub>2</sub>P(E) bits of information: the rarer the event, the more information. For a source with symbols a<sub>1</sub> … a<sub>J</sub>, symbol a<sub>j</sub> occurs with probability P(a<sub>j</sub>) and carries −log<sub>2</sub>P(a<sub>j</sub>) bits, so the average information per symbol is the weighted sum</p>
{formula("H = Σ P(a<sub>j</sub>) I(a<sub>j</sub>) = −Σ<sub>j=1</sub><sup>J</sup> P(a<sub>j</sub>) log<sub>2</sub> P(a<sub>j</sub>) &nbsp; bits/symbol")}
<p>For an image, P(a<sub>j</sub>) is the normalized histogram p(r<sub>k</sub>) = n<sub>k</sub>/N.</p>
<p><b>(ii)–(v)</b> N = 25.</p>{ft21}{b_f21}
<p>Total bits: Huffman = {sum(w21[i] * len(i_f21["code"][s]) for i, s in enumerate(s21))} bits; fixed = 25 × 8 = 200 bits.</p>
''')}
{img_sim(s21, w21, N21, 8, "F21 (iii)–(v).")}
"""))

# ================================================================ 7. Golomb
g49 = golomb(9, 4)
g512 = golomb(12, 5)
g47 = golomb(7, 4)
chart = [[n] + [golomb(n, m)[0] for m in (1, 2, 4)] for n in range(8)]
S.append(sec("gol", "Golomb coding", "46–51", EXAM, f"""
{idea("Golomb coding is a quick code for non-negative integers where small numbers are the most common. Split n by a chosen divisor m into a quotient and a remainder. Write the quotient in unary (that many 1s, then a 0) and the remainder in a short binary form.")}
<p><b>Slide 46.</b> A lossless method, particularly effective <b>when small values occur much more frequently than large ones</b>. It can only represent <b>non-negative integers</b>, is computationally simpler than Huffman, and depends on a tunable parameter m that decides how numbers are split into quotient and remainder.</p>
<p><b>Slides 47–48.</b> The Golomb code of n with respect to m, G<sub>m</sub>(n), combines the unary code of the quotient ⌊n/m⌋ and the binary representation of the remainder n mod m:</p>
<ol><li><b>Step 1.</b> Form the unary code of the quotient q = ⌊n/m⌋ (q ones followed by a 0; e.g. q = 3 → 1110).</li>
<li><b>Step 2.</b> Let k = ⌈log<sub>2</sub> m⌉, c = 2<sup>k</sup> − m, r = n mod m, and compute the truncated remainder r′: r truncated to k − 1 bits if 0 ≤ r &lt; c; otherwise r + c truncated to k bits.</li>
<li><b>Step 3.</b> Concatenate the results of steps 1 and 2.</li></ol>
{paper("SP24 Q3(b)ii · F23 Q2(c)ii · F21 B2(b)ii · slide 49", "3–4 marks", f'''
<p class="q">Compute the Golomb code G<sub>4</sub>(9).</p>
<p><b>Step 1:</b> q = ⌊9/4⌋ = {g49[1]} → unary code <b>110</b>.</p>
<p><b>Step 2:</b> k = ⌈log<sub>2</sub> 4⌉ = {g49[2]}; c = 2<sup>2</sup> − 4 = {g49[3]}; r = 9 mod 4 = {g49[4]}. {g49[5]}.</p>
<p><b>Step 3:</b> concatenate: 110 + 01 = <b>G<sub>4</sub>(9) = {g49[0]}</b>.</p>
''')}
{sim({"type": "golomb", "n": 9, "m": 4}, "any n and m. Pick n and m from the menus; it opens on G4(9).")}
{paper("Slide 50 · G4(7) and G5(12)", "worked", f'''
<p><b>G<sub>4</sub>(7):</b> q = 1 → 10; k = 2, c = 0, r = 3 ≥ 0 → r + c = 3 in 2 bits = 11 → <b>{g47[0]}</b>.</p>
<p><b>G<sub>5</sub>(12):</b> q = ⌊12/5⌋ = 2 → 110; k = ⌈log<sub>2</sub> 5⌉ = 3, c = 8 − 5 = 3, r = 12 mod 5 = 2. {g512[5]}. So G<sub>5</sub>(12) = 110 + 10 = <b>{g512[0]}</b>.</p>
''')}
{trap(f"Slide 50 prints G<sub>5</sub>(12) = 110010, which writes r = 2 in 3 bits (010) without truncating. Its own step 2 says r &lt; c, so r goes in k − 1 = 2 bits: 10, giving {g512[0]}. The textbook rule gives {g512[0]}. If this comes up, show the step-2 working and write {g512[0]}; mention 110010 only as the slide's value.")}
{paper("Slide 51 · \"Fill the chart at home\"", "solved", tbl(["n", "G<sub>1</sub>(n)", "G<sub>2</sub>(n)", "G<sub>4</sub>(n)"], chart, "narrow") +
       "<p>m = 1: k = 0, so the code is just the unary code of n. m = 2: k = 1, c = 0, the remainder is 1 bit. m = 4: k = 2, c = 0, the remainder is 2 bits. Row 7 matches the slide (11111110, 11101, 1011).</p>")}
"""))

# ================================================================ 8. arithmetic
a53, r53 = arith_block(["a1", "a2", "a3", "a4"], ["0.2", "0.2", "0.4", "0.2"], ["a1", "a2", "a3", "a3", "a4"])
acw, rcw = arith_block(list("ABCDEF"), ["0.45", "0.13", "0.12", "0.16", "0.09", "0.05"], list("ACEF"))
S.append(sec("ari", "Arithmetic coding", "52–74", LIKELY, f"""
{idea("Arithmetic coding turns a whole message into <b>one number</b> between 0 and 1. Start with the interval [0, 1). Each symbol zooms into its own slice of the current interval, sized by its probability. After the last symbol, any number inside the final tiny interval stands for the whole message.")}
<p><b>Slide 52.</b> Variable-length, error-free (lossless), <b>non-block</b> code: there is no one-to-one correspondence between symbols and code words. An entire sequence of source symbols is mapped to a <b>single arithmetic number (code word)</b>, which defines an interval of real numbers between 0 and 1. It can achieve theoretically higher compression than Huffman.</p>
<p><b>Slide 53.</b> It maintains an interval within [0, 1) based on the symbol probabilities.</p>
{paper("Slides 53–64 · encode a1 a2 a3 a3 a4", "worked", "<p class=\"q\">Four-symbol source a1 = 0.2, a2 = 0.2, a3 = 0.4, a4 = 0.2. Encode the message a1 a2 a3 a3 a4.</p>" + a53 +
       "<p>The slide picks <b>0.068</b>: the arithmetic code for a1a2a3a3a4.</p>")}
{arith_sim(["a1", "a2", "a3", "a4"], ["0.2", "0.2", "0.4", "0.2"], ["a1", "a2", "a3", "a3", "a4"], "slides 55–63: watch each symbol zoom into its slice.")}
<h3>Decoding (slides 65–73)</h3>
<p>The decoder knows the same sub-intervals. Take the code 0.068: it lies in [0, 0.2), so the first symbol is a1. Inside [0, 0.2) the slices are a1 [0, 0.04), a2 [0.04, 0.08), a3 [0.08, 0.16), a4 [0.16, 0.2): 0.068 lies in a2. Keep zooming: [0.04, 0.08) → a3 slice [0.056, 0.072); then a3 again [0.0624, 0.0688); then a4. Decoded: <b>a1 a2 a3 a3 a4</b>. (The decoder also needs the message length or an end symbol to know when to stop.)</p>
{paper("Slide 74 · Class work", "solved", "<p class=\"q\">Six-symbol source A 0.45, B 0.13, C 0.12, D 0.16, E 0.09, F 0.05 with sub-intervals A [0, 0.45), B [0.45, 0.58), C [0.58, 0.70), D [0.70, 0.86), E [0.86, 0.95), F [0.95, 1.00). Encode the message \"ACEF\". (The Huffman code of the same source is the slide 36 class work above.)</p>" + acw)}
{arith_sim(list("ABCDEF"), ["0.45", "0.13", "0.12", "0.16", "0.09", "0.05"], list("ACEF"), "the slide 74 class work 'ACEF'.")}
{trap("Use the sub-intervals in the order the question lists the symbols, not sorted by probability. Keep every decimal (no rounding) until the final interval, then pick the shortest decimal that lies inside it.")}
"""))

# ================================================================ 9. LZW
lzw_slide = [[39, 39, 126, 126]] * 4
b_ls, o_ls = lzw_block(lzw_slide)
b_l25, o_l25 = lzw_block([[7, 8, 40, 100]] * 4)
b_l23, o_l23 = lzw_block([[5, 8, 40, 120]] * 4)
b_l22, o_l22 = lzw_block([[3, 4, 7]] * 3)
dec_rows = []
dic = {i: str(i) for i in range(256)}
prev, nxt = None, 256
for c in o_ls:
    entry = dic[c] if c in dic else dic[prev] + "-" + dic[prev].split("-")[0]
    if prev is not None:
        dic[nxt] = dic[prev] + "-" + entry.split("-")[0]; added = f"{nxt}: {dic[nxt]}"; nxt += 1
    else:
        added = "—"
    dec_rows.append([c, entry.replace("-", " "), added]); prev = c
S.append(sec("lzw", "LZW coding", "75–106", EXAM, f"""
{idea("LZW builds a dictionary while it reads. The first time it meets a pattern such as 39-39, it adds it to the dictionary. The next time 39-39 appears, one dictionary code replaces both pixels. Repeated patterns therefore shrink, without needing any probabilities.")}
<p><b>Slide 75. Key features:</b> <b>lossless</b> (no data lost); <b>dictionary-based</b> (builds a dictionary of sequences met in the input); a <b>universal</b> algorithm (text, images, other data); efficient: it removes <b>spatial / inter-pixel redundancy</b>, is simple to implement with high throughput, and needs <b>no knowledge of the probability of occurrence</b>. Used in <b>GIF, TIFF and PDF</b>.</p>
<p><b>Slide 76. Encoding:</b> images are scanned left to right and top to bottom. The codebook (dictionary) is extended with new sequences met in the input, each assigned a <b>fixed-length code word</b>. For 8-bit monochrome images the first 256 words are the intensities 0, 1, …, 255; new gray-level sequences get entries from #256. With a 9-bit, 512-word dictionary, two pixels (16 bits) can be represented by 9 bits only.</p>
<p><b>Slide 77.</b> Read input symbols and form longer sequences. If a sequence is already in the dictionary, continue extending it. If not, add the new sequence to the dictionary and output the code for the longest existing sequence.</p>
{paper("Slides 77–95 · 4×4, 8-bit image of 39 39 126 126 rows", "worked", mat(lzw_slide, "image") + b_ls)}
{sim({"type": "lzw", "img": lzw_slide}, "the slide example, one pixel at a time (slides 78–95).")}
<p><b>Slide 106. Compression ratio:</b> the sequence 39-39-126 is replaced by code 260, i.e. 3 × 8 = 24 bits by 9 bits. Original 16 × 8 = 128 bits, compressed 10 × 9 = 90 bits, C<sub>R</sub> = 128 : 90 = <b>1.42 : 1</b>.</p>
<h3>Decoding (slides 96–105)</h3>
<p>The decoder rebuilds the <b>same dictionary</b> while it reads the codes. Each code is translated back into its sequence; after each code (from the second on) the entry previous-sequence + first pixel of the current sequence is added.</p>
{tbl(["code read", "output pixels", "dictionary entry added"], dec_rows, "narrow")}
<p>Output: 39 39 126 126 / 39 39 126 126 / 39 39 126 126 / 39 39 126 126, the original image.</p>
{paper("SP25 Q3(b)i", "6 marks", "<p class=\"q\">A collection of bitmap images with many repeating colours and patterns must be compressed with a lossless fixed-length coding algorithm. Name it and explain step-by-step encoding of the 4×4 8-bit image with every row [7 8 40 100].</p><p>Use <b>LZW coding</b>: lossless, fixed-length (9-bit) code words, and it removes the repeated patterns (spatial redundancy) without needing probabilities.</p>" + b_l25)}
{sim({"type": "lzw", "img": [[7, 8, 40, 100]] * 4}, "SP25.")}
{paper("F23 Q3(c)", "10 marks", "<p class=\"q\">Encode the 4×4 8-bit image with every row [5 8 40 120] using LZW, step by step; the codebook uses 9 bits.</p>" + b_l23)}
{sim({"type": "lzw", "img": [[5, 8, 40, 120]] * 4}, "F23.")}
{paper("SP22 Q1(b)", "5 + 2 + 2 marks", "<p class=\"q\">3×3 8-bit image with every row [3 4 7]. (i) Generate a 9-bit codebook and LZW-encode it step by step. (ii) Which redundancy does it reduce? (iii) Is any compression achieved? Prove it.</p><p><b>(i)</b></p>" + b_l22 +
       "<p><b>(ii)</b> LZW reduces <b>spatial / inter-pixel redundancy</b>: repeated pixel patterns (3-4, 4-7, 7-3 …) are replaced by single dictionary codes.</p>"
       f"<p><b>(iii)</b> Yes: 72 bits are coded with {len(o_l22)} × 9 = {9 * len(o_l22)} bits, C<sub>R</sub> = 72/{9 * len(o_l22)} = {72 / (9 * len(o_l22)):.2f} &gt; 1.</p>")}
{sim({"type": "lzw", "img": [[3, 4, 7]] * 3}, "SP22.")}
"""))

# ================================================================ 10. RLE
r109 = [[10] * 8, [10] * 5 + [12] * 3, [10] * 5 + [12] * 3, [0] * 3 + [10] * 3 + [0] * 2, [5] * 3 + [0] * 5, [5] * 3 + [10, 10, 9, 9, 10], [5] * 3 + [4] * 3 + [0] * 2, [0] * 8]
b109, c109 = rle_block(r109, 4)
bin8 = [[0] * 8, [1, 1, 1, 1, 0, 0, 0, 0], [0, 1, 1, 0, 0, 0, 0, 0], [0, 1, 1, 1, 1, 1, 0, 0], [0, 1, 1, 1, 0, 0, 1, 0], [0, 0, 1, 0, 0, 1, 1, 0], [1, 1, 1, 1, 0, 1, 0, 0], [0] * 8]
def bin_runs(row):
    rr = runs(row)
    nums = ([0] if rr[0][0] == 1 else []) + [n for _, n in rr]
    return ", ".join(map(str, nums))
S.append(sec("rle", "Run-length encoding", "107–118", EXAM, f"""
{idea("Run-length encoding writes \"what value, how many times\" instead of every pixel. Ten 10s in a row become the pair (10, 10). It is great for images with long flat runs and bad for busy ones, where every run is short.")}
<p><b>Slides 107–108.</b> Image features: in the line image all 256 gray levels are equally probable (uniform histogram), so variable-length coding cannot be applied. But the gray level of each line is chosen at random, so pixels are independent vertically and identical (completely dependent) horizontally: <b>spatial redundancy</b>.</p>
<p>The spatial redundancy is eliminated with <b>run-length pairs</b> (a mapping scheme). A run-length pair has two parts: the <b>start of a new intensity</b> and the <b>number of consecutive pixels</b> having that intensity. Each 256-pixel line is replaced by a single 8-bit intensity and the run length 256: C<sub>R</sub> = (256 × 256 × 8)/((256 + 256) × 8) = <b>128</b>.</p>
<p><b>Slide 109.</b> RLE uses run-length pairs, e.g. (0, 1), (1, 2), (0, 1), (1, 3), …. It eliminates small spatial redundancies. However, <b>small runs result in expansion instead of compression</b>.</p>
{paper("Slides 110–112 · Example 10.2.9, 8×8 4-bit image", "worked", mat(r109, "image") + b109 + "<p>As on slide 112: original 64 × 4 = 256 bits, compressed 36 × 4 = 144 bits, compression ratio 64:36 = <b>16:9</b>.</p>")}
{sim({"type": "rle", "img": r109, "bits": 4}, "Example 10.2.9, every run.")}
<h3>RLE in binary images (slides 113–117)</h3>
<p>In binary images adjacent pixels are even more likely to be identical, so the image can be written as a <b>sequence of run lengths only</b> (e.g. 1b 2w 1b 3w 4b 1w → 121341). Scan each row left to right and code each contiguous run of 0s or 1s by its length. A convention fixes the value of the runs:</p>
<ul><li><b>specify the value of the first run</b> of each row, or</li><li><b>assume each row begins with a white run</b> (bit 1), whose length may be zero.</li></ul>
<p>Example (slide 115): the 30-bit row 000001100000100000000101100000 has runs of 5, 2, 5, 1, 8, 1, 1, 2, 5. With the first convention it is written <b>0</b> 5 2 5 1 8 1 1 2 5, where the leading 0 says "the first run is black (0)". With the second convention it is also 0 5 2 5 1 8 1 1 2 5, but now the leading 0 means "the first white run has length 0".</p>
{paper("Slides 116–117 · Example 10.2.7, 8×8 binary image", "worked", mat(bin8, "binary image (1 = white, 0 = black)", small=True) +
       "<p>Convention: the first number of each row is the number of zeros (black) in the first run, so a row that starts with 1 begins with 0.</p>" +
       tbl(["Row", "RLC numbers"], [[f"Row {i + 1}", bin_runs(r)] for i, r in enumerate(bin8)], "narrow") +
       "<p>Rows 2 and 7 begin with 0 because they start with a white run.</p>")}
<p><b>Slide 118. RLE in BMP</b> combines an <b>encoded mode</b> (2-byte RLE: the first byte is the run length, the second the gray/colour index) and an <b>absolute mode</b> (first byte 0, the second byte is 0 end of line, 1 end of image, 2 move to a new position, 3–255 specify pixels individually). Either mode can appear anywhere in the image.</p>
"""))

# ================================================================ 11. fidelity
f0 = [[1, 4, 3], [2, 3, 4], [2, 4, 5]]
fd = [[v + 2 for v in r] for r in f0]
flat0, flatd = [v for r in f0 for v in r], [v for r in fd for v in r]
se = sum((b - a) ** 2 for a, b in zip(flat0, flatd)); sd = sum(b * b for b in flatd)
cw132 = [[1, 4, 3], [5, 2, 3], [4, 2, 1]]
cw132d = [[3, 6, 5], [7, 4, 5], [6, 4, 3]]
S.append(sec("fid", "Fidelity criteria (how much quality was lost)", "119–132", EXAM, f"""
<p><b>Slide 119.</b> Removing irrelevant information also removes useful "invisible" information. Information is lost in many other <b>lossy</b> compression techniques. How do we assess the loss? With <b>image fidelity</b> criteria.</p>
<p><b>Slide 120.</b> The goal of image compression is to reduce file size while keeping acceptable quality. Fidelity criteria define how closely the reconstructed image matches the original, i.e. the degree of exactness (measuring the quality). Two classes: (i) <b>objective</b> fidelity criteria (quantifiable, mathematically defined); (ii) <b>subjective</b> fidelity criteria (person dependent, based on human observers).</p>
<p><b>Slides 121–122.</b> f(x,y) is compressed to g(x,y) and decompressed to f̂(x,y) = f(x,y) + e(x,y). The error is e(x,y) = f̂(x,y) − f(x,y), and the total error between the two images is ΣΣ [f̂(x,y) − f(x,y)].</p>
<p><b>Slide 123. Objective criteria:</b> RMSE, signal-to-noise ratio (SNR), structural similarity index (SSIM), normalized cross-correlation (NCC).</p>
{formula("e<sub>rms</sub> = [ (1/MN) Σ<sub>x</sub> Σ<sub>y</sub> ( f̂(x,y) − f(x,y) )² ]<sup>1/2</sup>")}
<p><b>Slide 124.</b> RMSE measures the average squared difference between pixel values of the original and decompressed image: compute the squared differences pixel by pixel, average them and take the square root. <b>The smaller the RMSE, the better</b> the compressed image represents the original.</p>
{paper("Slide 125 · 2×2 example", "worked", '''
<p>Original [100 150; 200 250], reconstructed [102 148; 198 255].</p>
<p>Step 1, differences: [−2 2; 2 −5]. Step 2, squares: [4 4; 4 25]. Step 3, mean: (4 + 4 + 4 + 25)/4 = 37/4 = 9.25. Step 4, root: RMSE = √9.25 ≈ <b>3.04</b>.</p>
''')}
<p><b>Slide 126.</b> Three approximations of one image have RMSE 5.17, 15.67 and 14.17: the first is closest to the original.</p>
{formula("SNR<sub>ms</sub> = Σ<sub>x</sub> Σ<sub>y</sub> f̂(x,y)² / Σ<sub>x</sub> Σ<sub>y</sub> ( f̂(x,y) − f(x,y) )²")}
<p><b>Slide 127. SNR</b> expresses the ratio between the signal and the noise introduced by compression. <b>The higher the SNR</b>, the better the quality.</p>
<p><b>Slides 128–129 (short).</b> <b>SSIM</b> evaluates similarity based on luminance, contrast and structure; it is often closer to human perception than MSE/PSNR; values from −1 to 1, where 1 is perfect similarity. <b>NCC</b> compares the correlation between original and compressed images and is invariant to linear changes in brightness and contrast; −1 (perfect negative) to 1 (perfect positive correlation).</p>
<p><b>Slides 130–131. Subjective criteria</b> rely on human judgement: visual losslessness (indistinguishable to the eye), quality ratings (excellent, good, fair, poor), artifact evaluation (blockiness, blurring, colour banding). The Television Allocations Study Organization scale: 1 Excellent, 2 Fine, 3 Passable, 4 Marginal, 5 Inferior, 6 Unusable.</p>
{paper("SP24 Q3(b)i · F23 Q2(c)i · F21 B2(b)i · SP25 Q3(b)ii", "2–5 marks", f'''
<p class="q">A 3×3, 3-bit image f(x,y) = [1 4 3; 2 3 4; 2 4 5] is compressed with a lossy technique; after decompression every pixel value increased by 2. Give the decompressed image f̂ and evaluate it with a suitable fidelity criterion (RMSE).</p>
{mats(mat(f0, "original f"), mat(fd, "decompressed f̂ = f + 2"), mat([[2] * 3] * 3, "error e = f̂ − f"), mat([[4] * 3] * 3, "e²"))}
<p>e<sub>rms</sub> = [ (1/9) × (9 × 2²) ]<sup>1/2</sup> = [ 36/9 ]<sup>1/2</sup> = √4 = <b>2</b>.</p>
<p>SNR<sub>ms</sub> = Σ f̂² / Σ e² = {sd} / {se} = <b>{sd / se:.4f}</b>.</p>
<p>Every pixel is off by exactly 2 gray levels (out of 0–7), so the decompressed image is a brighter copy; the RMSE of 2 is large for a 3-bit image.</p>
''')}
{sim({"type": "rmse", "f": f0, "fd": fd}, "the RMSE, pixel by pixel.")}
{paper("Slide 132 · Class work", "solved", f'''
<p class="q">A 3×3, 3-bit image [1,4,3,5,2,3,4,2,1] is lossy compressed; after decompression it becomes [3,6,5,7,4,5,6,4,3]. Calculate the RMSE.</p>
<p>Every pixel increased by 2, so e = 2 everywhere: e<sub>rms</sub> = √((9 × 4)/9) = √4 = <b>2</b>.</p>
''')}
{sim({"type": "rmse", "f": cw132, "fd": cw132d}, "slide 132 class work.")}
"""))

S.append(sec("traps", "Traps and one-minute sheet", "all", None, f"""
<ul class="traps">
<li>C<sub>R</sub> = <b>original / compressed</b>, never the other way. R<sub>D</sub> = 1 − 1/C<sub>R</sub>.</li>
<li>1 KB = 1024 bytes = 8192 bits. Keep units the same on top and bottom.</li>
<li>Huffman ties: the sum goes <b>below</b> an equal value. Upper branch 0, lower branch 1. Check: the codes form a prefix code and L<sub>avg</sub> ≥ H.</li>
<li>Write the full reduction table: the examiner marks the table, not just the codes.</li>
<li>Arithmetic: keep all decimals; use the listed symbol order for the sub-intervals.</li>
<li>LZW: the first pixel is always in the dictionary (locations 0–255). Don't forget to output the last recognized sequence at the end. Count code words × 9 bits.</li>
<li>RLE on short runs makes the file bigger (C<sub>R</sub> &lt; 1); say so.</li>
<li>Golomb: unary of q is q ones and then a 0. Truncated remainder: r &lt; c → k − 1 bits; else r + c in k bits.</li>
</ul>
{tbl(["method", "removes", "lossless?", "key formula / rule"], [
    ["Huffman", "coding redundancy", "yes", "merge two smallest; L<sub>avg</sub> = Σ l p"], ["Golomb", "coding redundancy", "yes", "unary(⌊n/m⌋) + truncated(n mod m)"],
    ["Arithmetic", "coding redundancy", "yes", "one number in the final interval"], ["LZW", "spatial / inter-pixel", "yes", "dictionary from 256, 9-bit codes"],
    ["RLE", "spatial / inter-pixel", "yes", "(value, run length) pairs"], ["quantization", "irrelevant information", "no (lossy)", "judge with RMSE, SNR"],
    ["entropy", "—", "—", "H = −Σ p log<sub>2</sub> p, lower bound on L<sub>avg</sub>"]])}
"""))

toc = [("start", "Start"), ("cr", "C<sub>R</sub>, R<sub>D</sub>"), ("red", "Redundancies"), ("huff", "Huffman"), ("ent", "Entropy"), ("huffpq", "Huffman past papers"),
       ("gol", "Golomb"), ("ari", "Arithmetic"), ("lzw", "LZW"), ("rle", "RLE"), ("fid", "Fidelity"), ("traps", "Traps")]
OUT.write_text(page("DIP Deck 13 Lesson", "CSE 4227 · Chapter 8 · Deck 13", "Image Compression, from zero",
                    "Every slide you need, in plain words, with every Huffman, arithmetic, LZW, RLE, Golomb and RMSE past question solved the way you write it in the answer script, and a step-by-step simulator next to each method.",
                    toc, S, extra=sim_assets()), encoding="utf-8")

# ---------------------------------------------------------------- self-check against data/answers.json and the slides
assert i35["code"] == {"a2": "1", "a6": "00", "a1": "011", "a4": "0100", "a3": "01010", "a5": "01011"} and i35["lavg"] == F(22, 10)
assert i_sp25["code"] == {"A": "1", "B": "00", "C": "010", "D": "011"} and abs(i_sp25["H"] - 1.8464) < 1e-4
assert i_sp24["code"] == {160: "000", 170: "0010", 180: "0011", 120: "01", 110: "10", 140: "11"} and i_sp24["lavg"] == F(248, 100)
assert i_sp23["lavg"] == 2 and abs(i_sp23["C"] - 3) < 1e-9 and abs(i_f22["C"] - 3) < 1e-9 and abs(c_rle22 - 0.5882) < 1e-4
assert i_sp22["lavg"] == 2 and abs(i_sp22["H"] - 1.8911) < 1e-4
assert i_f21["lavg"] == F(248, 100) and abs(i_f21["H"] - 2.4188) < 1e-4 and abs(i_f21["C"] - 3.2258) < 1e-4
assert o_l25 == [7, 8, 40, 100, 256, 258, 260, 259, 257, 100]
assert o_l23 == [5, 8, 40, 120, 256, 258, 260, 259, 257, 120] and o_l22 == [3, 4, 7, 256, 258, 257] and o_ls == [39, 39, 126, 126, 256, 258, 260, 259, 257, 126]
assert (r53[0], r53[1], r53[2]) == (F("0.06752"), F("0.0688"), F("0.068"))
assert g49[0] == "11001" and chart[7] == [7, "11111110", "11101", "1011"] and abs(c109 - 64 / 36) < 1e-9
assert [bin_runs(r) for r in bin8] == ["8", "0, 4, 4", "1, 2, 5", "1, 5, 2", "1, 3, 2, 1, 1", "2, 1, 2, 2, 1", "0, 4, 1, 1, 2", "8"]
assert se == 36 and math.sqrt(se / 9) == 2
print(OUT, OUT.stat().st_size, "cw huffman", icw["code"], "ACEF", rcw, "G5(12)", g512[0])
