# DIP ultimate night-before page: every past question (crop) next to its worked answer + sims,
# grouped by chapter, with the pattern, the formula wall and the CLO1/CLO2/CLO3 map.
# Content is lifted from the built deck pages, the F25 quiz page and the mega sheet, so rebuild those first.
import ast, html, json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from kit import page, tbl, sim_assets

REPO = ROOT.parent
OUT = HERE / "ultimate" / "dip_ultimate.html"
CROPS = REPO / "crops"
OUT.parent.mkdir(exist_ok=True)

tags = json.load(open(REPO / "data" / "tags.json", encoding="utf-8"))
types = json.load(open(REPO / "data" / "types.json", encoding="utf-8"))
qtext = {}
for f in (REPO / "data").glob("finals_*.json"):
    d = json.load(open(f, encoding="utf-8"))
    for q in d["questions"]:
        qtext[f'{d["paper"]}/{q["q"]}'] = q["text"]
for f in (REPO / "data").glob("quiz_f25.json"):
    d = json.load(open(f, encoding="utf-8"))
    for q in d.get("questions", []):
        qtext.setdefault(f'{q.get("paper", "")}/{q.get("q", "")}', q.get("text", ""))


def owner(qid):
    paper, num = qid.split("/")
    for key in (f"{paper}-{num[0]}", paper):
        if key in tags["papers"]:
            return tags["papers"][key]["owner"]
    return "ours"


OURS = {q: v for q, v in tags["q"].items() if not q.startswith("F24") and owner(q) == "ours"}
ORDER = ["SP25-F", "SP24-F", "F23-F", "SP23-F", "F22-F", "SP22-F", "F21-F", "F25-Q1C", "F25-Q1D", "F25-Q2C", "F25-Q3D", "F25-Q4C"]
qkey = lambda q: (ORDER.index(q.split("/")[0]), q.split("/")[1])
short = lambda q: q.replace("-F/", " ").replace("F25-", "F25 quiz ").replace("/", " ")


def crop(qid):
    return qid.replace("/", "_") + ".jpg"


# ---------------------------------------------------------------- lifting
def boxes(h):
    """Every paper box (+ the sims right after it) in a built page, in order: (ptag, html)."""
    out = []
    for m in re.finditer(r'<section class="paper">', h):
        i, depth = m.start(), 0
        for t in re.finditer(r'<(/?)section\b', h[i:]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                j = h.index(">", i + t.end()) + 1
                break
        k = j
        while h[k:].lstrip().startswith('<div class="simwrap">'):
            k = len(h) - len(h[k:].lstrip())
            k = h.index("></div></div>", k) + len("></div></div>")
        out.append((html.unescape(re.search(r'class="ptag">(.*?)</span>', h[i:j]).group(1)), h[i:k]))
    return out


def section(h, sid):
    i = h.index(f'<section class="sec" id="{sid}"')
    depth = 0
    for t in re.finditer(r'<(/?)section\b', h[i:]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return h[i:h.index(">", i + t.end()) + 1]


CODE = {"SP25": "SP25-F", "SP24": "SP24-F", "F23": "F23-F", "SP23": "SP23-F", "F22": "F22-F", "SP22": "SP22-F", "F21": "F21-F"}
SPECIAL = {"SP25 Final (CLO3 case study)": ["SP25-F/3d"]}


def qids(tag):
    if tag in SPECIAL:
        return SPECIAL[tag]
    out = []
    for m in re.finditer(r'\b(SP2[2-5]|F2[1-3])\b(?:\s+Final)?\s+Q?([AB]?\d)(?:\(([a-f])\))?', tag):
        q = f"{CODE[m.group(1)]}/{m.group(2)}{m.group(3) or ''}"
        if q in tags["q"] and q not in out:
            out.append(q)
    return out


SIM_IMAGES = {}


def prefix_images(deck, h):
    """Deck-local image keys can collide (f21, sp25 …), so prefix them with the deck and rewrite the sims."""
    m = re.search(r'window\.SIM_DATA = (.*?);</script>', h, re.S)
    imgs = json.loads(m.group(1))["images"] if m else {}
    for k, v in imgs.items():
        SIM_IMAGES[f"{deck}_{k}"] = v

    def fix(mm):
        cfg = json.loads(html.unescape(mm.group(1)))
        if "images" in cfg:
            cfg["images"] = [f"{deck}_{k}" for k in cfg["images"]]
        return f'data-sim="{html.escape(json.dumps(cfg), quote=True)}"'
    return re.sub(r'data-sim="([^"]*)"', fix, h)


DECKS = {"d02": "01–02", "d03": "03", "d04": "04", "d05": "05", "d06": "06", "d07": "07", "d08": "08", "d09": "09",
         "d10": "10", "d11": "11", "d12": "12", "d13": "13", "d14": "14"}
by_q, extra = {}, {}          # qid -> [(deck, tag, html)], deck -> [(tag, html)] slide examples / other examiners
for d in DECKS:
    h = prefix_images(d, (ROOT / d / f"deck{d[1:]}_lesson.html").read_text(encoding="utf-8"))
    for tag, b in boxes(h):
        q = [x for x in qids(tag) if x in OURS]
        if q:
            by_q.setdefault(q[0], []).append((d, tag, b))
            for x in q[1:]:
                by_q.setdefault(x, []).append((d, tag, f'<p class="same">Same answer as <a href="#q-{q[0].replace("/", "-")}">{short(q[0])}</a> ({html.escape(tag)}).</p>'))
        elif re.search(r"quiz", tag, re.I) and not qids(tag):
            continue                     # the quiz page below has the full answer
        else:
            extra.setdefault(d, []).append((tag, b))

# F25 quiz: whole sections of the quiz page
qh = (HERE / "f25_quiz_answers.html").read_text(encoding="utf-8")
QZ = {"q1c1": "F25-Q1C/1", "q1c2a": "F25-Q1C/2a", "q1c2b": "F25-Q1C/2b", "q1d1": "F25-Q1D/1", "q1d2a": "F25-Q1D/2a", "q1d2b": "F25-Q1D/2b",
      "q2c1": "F25-Q2C/1", "q2c2": "F25-Q2C/2", "q3d1": "F25-Q3D/1", "q3d2": "F25-Q3D/2", "q4c1": "F25-Q4C/1", "q4c2": "F25-Q4C/2"}
for sid, q in QZ.items():
    s = section(qh, sid)
    body = s[s.index("</div></div>", s.index('class="sechead"')) + len("</div></div>"):s.rindex("</section>")]
    by_q[q] = [("quiz", "Fall 25 quiz", body)]


# SP23 Q3(b) has no deck box: 4×4, 4-bit, 16 values (the last 4 as the student wrote them)
import math
from kit import paper, bars, sim
img23 = [[1, 2, 4, 7], [2, 1, 3, 1], [5, 2, 1, 4], [7, 6, 3, 1]]
v23 = [v for r in img23 for v in r]
n23 = [v23.count(k) for k in range(16)]
run, rows23, s23 = 0, [], []
for k in range(16):
    run += n23[k]
    s = math.floor(15 * run / 16 + 0.5)
    s23.append(s)
    if n23[k]:
        rows23.append([k, n23[k], f"{n23[k]}/16 = {n23[k] / 16:.4f}", f"{run}/16 = {run / 16:.4f}", f"15 × {run / 16:.4f} = {15 * run / 16:.4f}", f"<b>{s}</b>"])
eq23 = [sum(n for n, s in zip(n23, s23) if s == j) for j in range(16)]
assert sum(n23) == 16 and [s23[k] for k in (1, 2, 3, 4, 5, 6, 7)] == [5, 8, 9, 11, 12, 13, 15]
by_q["SP23-F/3b"] = [("new", "SP23 Q3(b)", paper("SP23 Q3(b)", "8 marks", f"""
<p>4-bit image, so L = 16 and the levels are 0 to 15. MN = 16. The last row (7 6 3 1) is how the student copy reads.</p>
<p><b>i) Histogram and normalized histogram</b>: count each level, p(r<sub>k</sub>) = n<sub>k</sub>/16.</p>
{bars(n23[:9], list(range(9)), "histogram h(r<sub>k</sub>) = n<sub>k</sub> (levels 9–15 are 0)")}
<p><b>iii) Transformation</b> s<sub>k</sub> = round(15 · CDF), .5 rounds up:</p>
{tbl(["r<sub>k</sub>", "n<sub>k</sub>", "p(r<sub>k</sub>)", "CDF", "15 · CDF", "s<sub>k</sub>"], rows23)}
<p><b>ii) Equalized histogram</b>: move each count to its new level s<sub>k</sub>.</p>
{bars(eq23, list(range(16)), "equalized histogram: the counts now spread from 5 to 15")}
<p>Mapping: 1→5, 2→8, 3→9, 4→11, 5→12, 6→13, 7→15. The levels spread over the whole 0–15 range, so contrast goes up.</p>""")
                      + sim({"type": "he", "img": img23, "L": 16}, "the same 4-bit image, step by step."))]


def src_const(path, name):
    for n in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == name:
            return ast.literal_eval(n.value)


QJS = src_const(HERE / "build_quiz.py", "QJS")
QCSS = src_const(HERE / "build_quiz.py", "EXTRA")
MCSS = src_const(HERE / "build_mega.py", "EXTRA")
mh = (HERE / "dip_mega_sheet.html").read_text(encoding="utf-8")
mega = lambda sid: re.sub(r'<section class="sec" id="[^"]+"><div class="sechead"><h2>.*?</h2>.*?</div></div>', "", section(mh, sid), count=1, flags=re.S)[:-len("</section>")]

# ---------------------------------------------------------------- chapters
TYPE_CH = {"tFUN": "c2", "RES": "c2", "NNI": "c2", "tPIX": "c2", "DST": "c2",
           "tENH": "c3", "tPW": "c3", "GAM": "c3", "CS": "c3", "GLS": "c3", "BIT": "c3",
           "tHIS": "he", "tHE": "he", "HE": "he", "HS": "he",
           "tSMO": "fil", "tSHP": "fil", "FIL": "fil",
           "tSEG": "seg", "CAN": "seg", "RGN": "seg", "THR": "seg", "cENH": "seg", "HOU": "seg",
           "tCC": "cc", "CC": "cc", "cMIX": "cc",
           "tMOR": "mor", "MOR": "mor", "HMT": "mor", "cMOR": "mor",
           "tCMP": "cmp", "CR": "cmp", "HUF": "cmp", "RLE": "cmp", "LZW": "cmp", "ARI": "cmp", "GOL": "cmp", "RMS": "cmp",
           "tCOL": "col", "HSI": "col"}
FORCE = {"F25-Q1C/2b": "c3", "SP24-F/3a": "seg", "SP25-F/2d": "seg", "SP22-F/6b": "seg", "SP24-F/2b": "fil", "SP25-F/2b": "fil"}

CH = [  # id, title, decks, formula section, deck pages used for slide examples, pattern bullets, connections
    ("c2", "Pixels, resolution, neighbours and distance", "decks 01–03", "f-ch2", ["d02", "d03"], [
        "<b>Q1 (4 marks):</b> 4- vs 8- vs m-connectivity, then count the connected components of a small 0/1 grid (SP25 1b). Sampling vs quantization and image types also come here.",
        "<b>Q2 small part:</b> D4 / D8 / De between two pixels, or the shortest 4-, 8- or m-path through a set V (SP23 2e, SP22 3b, SP24 1a).",
        "<b>Arithmetic:</b> bits = M × N × k, levels L = 2<sup>k</sup>; zoom by pixel replication / nearest neighbour.",
    ], "m-adjacency comes back in chain code (the boundary is a path) and in morphology (connected components, coin counting)."),
    ("c3", "Point operations: negative, log, gamma, stretching, slicing, bit planes", "deck 04", "f-ch3", ["d04"], [
        "<b>Q1:</b> short notes on negative / log / power-law; the piecewise (r1,s1), (r2,s2) cases: identity, threshold, stretch (SP23 2d, SP22 2a, F21 B3b).",
        "<b>Q2:</b> bit-plane slicing of a small grid (SP25 2b i, SP24 2b i); gray-level slicing map (F25 quiz).",
        "<b>Q3 case:</b> dark or washed-out X-ray, so power-law with γ &lt; 1 or &gt; 1, plus contrast stretching numbers (F23 3d, SP24 3e).",
    ], "Stretching and HE do the same job (spread the gray levels). Gamma/log are the first step in almost every Q3 enhancement pipeline."),
    ("he", "Histogram: types, equalization, matching", "deck 05", "f-he", ["d05"], [
        "<b>Q2(a), 8 marks, nearly every paper:</b> a 3-bit 5×5 grid or a table of counts. Write PDF, CDF, s = round(7·CDF), then the new histogram, and draw both.",
        "<b>Q1:</b> the 4 histogram types (dark, bright, low, high contrast), whether two images can have the same histogram, the definition and steps of HE.",
        "<b>Rare:</b> histogram matching (F22 A3b uses the slide 49 counts).",
    ], "HE is the automatic version of contrast stretching (ch 3). Its output flattens the histogram, which helps the thresholding and segmentation steps later."),
    ("fil", "Spatial filters: smoothing and sharpening", "decks 06–07", "f-filt", ["d06", "d07"], [
        "<b>Q2(b):</b> one image, several tasks at a point: mean, weighted, median, Laplacian, then sharpen (SP25 2b, SP24 2b, F23 2b).",
        "<b>Q1:</b> objectives of sharpening, derive the Laplacian from 2nd derivatives, draw 4 masks (SP25 1a, SP24 1b).",
        "<b>Q3 / short:</b> salt-and-pepper means median; Gaussian noise means mean or weighted; median vs mean (F22 A1a, SP22 1a).",
    ], "Smoothing = average = blur, and it removes noise. Sharpening = derivative, which picks up edges. The same derivative masks become Sobel and Prewitt in segmentation."),
    ("seg", "Segmentation: edges, Canny, threshold, region growing", "decks 08–09", "f-seg", ["d08", "d09"], [
        "<b>Q1:</b> goal of edge detection, 2 gradient operators, the role of NMS in Canny, what region growing is (SP25 1e, SP24 1e, F23 1e).",
        "<b>Q2:</b> Sobel Gx, Gy, |G|, α at a pixel (SP25 2d, SP22 6b); full Canny numeric with NMS and hysteresis (F23 3a, 10 marks).",
        "<b>Q3 case:</b> pipeline for a medical image: enhance, smooth, edges or threshold, region growing, morphology (SP25 3a, SP23 1b).",
    ], "Edges use the ch 7 derivatives. Thresholding needs a two-peak histogram (ch 5). The masks it produces are then cleaned with morphology (ch 9)."),
    ("cc", "Chain code (boundary representation)", "deck 10", "f-cc", ["d10"], [
        "<b>Q2:</b> walk the boundary and write the 4- or 8-direction chain code, then the first difference (CFD) and its smallest rotation, the shape number (SP24 3d, SP23 2c, F25 quiz 3D).",
        "<b>Q1:</b> definition, and the two problems: depends on the start point (normalise by smallest rotation) and on rotation (use the difference).",
        "<b>Q3 mix:</b> fracture X-ray with chain code + histogram + gamma (SP25 3d).",
    ], "The boundary it walks is the one morphology extracts (A − (A ⊖ B)), and it follows 8- or 4-adjacency from ch 2."),
    ("mor", "Morphology: erosion, dilation, opening, closing, hit-or-miss", "decks 11–12", "f-mor", ["d11", "d12"], [
        "<b>Q2 / Q3:</b> erode or dilate a grid with a given SE, then open or close it (SP24 3c, SP22 4b, F23 2d, SP23 1a).",
        "<b>Q1:</b> define dilation as a set, explain opening and closing, and what closing does to small holes (SP25 1f, SP24 1c).",
        "<b>Q3 case:</b> which operation and why: noise specks mean opening, gaps or holes mean closing, touching coins mean erosion then count, boundary = A − erosion (SP25 3c, F23 3b). Hit-or-miss finds corners and end points (F23 2e, SP23 3c).",
    ], "It works on binary masks, the output of thresholding (ch 8). Boundary extraction feeds the chain code."),
    ("cmp", "Compression: redundancy, Huffman, RLE, LZW, Golomb, arithmetic, RMSE", "deck 13", "f-cmp", ["d13"], [
        "<b>Q2(c) / Q3(b), every paper:</b> Huffman + L<sub>avg</sub> + entropy + CR (SP25 2c, SP24 2c, SP23 3a, SP22 5b); LZW table (SP25 3b, F23 3c, SP22 1b); RLE; Golomb G<sub>m</sub>(n); RMSE.",
        "<b>Q1:</b> data redundancy, the 3 types (coding, spatial/inter-pixel, psychovisual), C = n1/n2, R = 1 − 1/C (SP25 1d, F23 1d).",
    ], "Coding redundancy is what Huffman and Golomb remove, spatial redundancy is what RLE and LZW remove, and RMSE measures what lossy coding loses."),
    ("col", "Colour: RGB, CMY(K), HSI", "deck 14", "f-col", ["d14"], [
        "<b>Q1 / Q3 theory:</b> define a colour image, additive vs subtractive mixing, why colour models exist, which model is used for printing (CMYK) and for segmentation (HSI) (SP25 1c, SP24 1d, F23 1c).",
        "<b>Numeric:</b> RGB → CMY (1 − RGB), RGB → HSI (θ, S, I) (SP22 7b).",
    ], "HSI separates intensity from colour, so the gray-level methods (HE, filters) run on I alone."),
]
CHN = {c[0]: i for i, c in enumerate(CH)}


def chapter_of(q):
    if q in FORCE:
        return FORCE[q]
    return TYPE_CH.get(OURS[q][0][0], "c2")


per_ch = {c[0]: [] for c in CH}
for q in sorted(OURS, key=qkey):
    per_ch[chapter_of(q)].append(q)
missing = [q for q in OURS if not (CROPS / crop(q)).exists()]
assert not missing, missing

CLO = {"T": ("CLO1", "theory"), "M": ("CLO2", "math"), "C": ("CLO3", "case")}


def qcard(q):
    kinds = []
    for t, mk in OURS[q]:
        k = types.get(t, {}).get("kind", "M")
        kinds.append(f'<span class="clo {k}">{CLO[k][0]} · {types.get(t, {"name": t})["name"].split("(")[0].strip()} · {mk:g}</span>')
    ans = by_q.get(q)
    body = "".join(b for _, _, b in ans) if ans else '<p class="noans">No worked box for this one in the deck pages: use the pattern and formula above.</p>'
    src = "" if not ans else " · ".join(sorted({f"deck {DECKS[d]}" if d in DECKS else "F25 quiz page" for d, _, _ in ans}))
    alt = html.escape(qtext.get(q, short(q)))
    return f'''<article class="qc" id="q-{q.replace("/", "-")}">
<div class="qhead"><b>{short(q)}</b>{"".join(kinds)}</div>
<img class="crop" loading="lazy" src="c/{crop(q)}" alt="{alt}">
<details class="ans"><summary>Worked answer{f" <span>({src})</span>" if src else ""}</summary>{body}</details>
</article>'''


S = []
# ---- top: night plan, paper format, dot map
dot_rows = []
for cid, title, decks_, *_ in CH:
    qs = per_ch[cid]
    col = {k: [x for x in qs if any(types.get(t, {}).get("kind") == k for t, _ in OURS[x])] for k in "TMC"}
    link = lambda xs: " ".join(f'<a href="#q-{x.replace("/", "-")}">{short(x)}</a>' for x in xs) or "–"
    dot_rows.append([f'<a href="#{cid}"><b>{title.split(":")[0]}</b></a><br><span class="mut">{decks_}</span>', link(col["T"]), link(col["M"]), link(col["C"])])

S.append(f'''<section class="sec" id="tonight"><div class="sechead"><h2>Night-before revision plan</h2></div>
<ol class="plan">
<li><b>15 min:</b> the <a href="#dots">dot map</a> and the <a href="#cues">cue words</a>. Say out loud which method each story word points to.</li>
<li><b>2 hours:</b> chapter by chapter. For each one, read the <i>pattern</i> box, then the <i>formula wall</i>. Look at each question image, say the first two lines of the answer, then open <i>Worked answer</i> to check. Don't redo the sums you already know. Run one simulator only if a step feels foggy.</li>
<li><b>30 min:</b> <a href="#q1">Q1 theory points</a> and <a href="#q3">Q3 case bank</a>. Keywords matter more than wording.</li>
<li><b>10 min:</b> <a href="#traps">traps</a> and the <a href="#check">final checklist</a>. Then sleep.</li>
</ol>
<div class="tools"><button type="button" id="openall">Open every answer</button><button type="button" id="closeall">Close every answer</button><span class="mut">Click any question image to zoom.</span></div>
</section>''')

S.append(f'<section class="sec" id="paper"><div class="sechead"><h2>The paper</h2></div>{mega("paper")}</section>')
S.append(f'''<section class="sec" id="dots"><div class="sechead"><h2>Dot map: every past question by chapter and CLO</h2></div>
<p>Each row is a chapter. Each column is a section of the paper: Q1 is CLO1 theory, Q2 is CLO2 math, Q3 is CLO3 case. Click a question to jump to its image and answer. Fall 2024 and the other examiners' sections are left out.</p>
<div class="tw">{tbl(["chapter", "CLO1 · Q1 theory", "CLO2 · Q2 math", "CLO3 · Q3 case"], dot_rows, "dots")}</div>
{mega("map")}</section>''')
S.append(f'<section class="sec" id="cues"><div class="sechead"><h2>Cue words: story word, then method</h2></div>{mega("cues")}</section>')

for cid, title, decks_, fsec, ex_decks, pat, conn in CH:
    qs = per_ch[cid]
    freq = {}
    for q in qs:
        for t, _ in OURS[q]:
            freq.setdefault(t, []).append(q)
    ftab = tbl(["type", "CLO", "times", "where"], [[types[t]["name"].split("(")[0].strip(), CLO[types[t]["kind"]][0], len(v), ", ".join(short(x) for x in v)]
                                                  for t, v in sorted(freq.items(), key=lambda kv: -len(kv[1])) if t in types], "freq")
    exs = [(d, tag, b) for d in ex_decks for tag, b in extra.get(d, [])]
    exhtml = "".join(f'<details class="ex"><summary>{html.escape(tag)} <span>(deck {DECKS[d]})</span></summary>{b}</details>' for d, tag, b in exs)
    S.append(f'''<section class="sec chap" id="{cid}"><div class="sechead"><h2>{CHN[cid] + 1}. {title}</h2><div class="meta"><span class="slides">{decks_} · {len(qs)} past questions</span></div></div>
<div class="pattern"><span class="k">The pattern: how she asks it</span><ul>{"".join(f"<li>{p}</li>" for p in pat)}</ul><p class="conn"><b>Connects to:</b> {conn}</p></div>
<div class="tw">{ftab}</div>
<details class="fw" open><summary>Formula wall: every formula with a worked line</summary>{mega(fsec)}</details>
<h3 class="qs">Past questions: look, recall, then open the answer</h3>
{"".join(qcard(q) for q in qs)}
{f'<details class="exs"><summary>More worked examples: slides and other examiners ({len(exs)})</summary>{exhtml}</details>' if exs else ""}
</section>''')

S.append(f'<section class="sec" id="q1"><div class="sechead"><h2>Q1 theory points (CLO1)</h2></div>{mega("q1")}</section>')
S.append(f'<section class="sec" id="q3"><div class="sechead"><h2>Q3 case bank (CLO3)</h2></div>{mega("q3")}</section>')
S.append(f'<section class="sec" id="traps"><div class="sechead"><h2>Traps</h2></div>{mega("traps")}</section>')
S.append('''<section class="sec" id="check"><div class="sechead"><h2>Final checklist</h2></div><ul class="chk">
<li>HE: PDF → CDF → s = round((L−1)·CDF), .5 rounds up, then the new histogram (add the counts that land on the same s) and both bar graphs.</li>
<li>Filters: write the 3×3 window, then the sum line, then the answer. Median: sorted list, 5th value. Say whether you pad with zeros or skip the border.</li>
<li>Laplacian: g = f − ∇²f when the centre is negative (−4), g = f + ∇²f when it is positive (+4). Clip to [0, L−1].</li>
<li>Sobel: Gx, Gy, |G| = |Gx| + |Gy| (or √), α = tan⁻¹(Gy/Gx). The edge runs perpendicular to α.</li>
<li>Huffman: sort, merge the two smallest, keep the tie order; then L<sub>avg</sub>, H, efficiency, C = fixed bits / L<sub>avg</sub>.</li>
<li>LZW: 256 is the first new code. Output the code for the current string when current + next is not in the dictionary.</li>
<li>Chain code: number the directions counter-clockwise from →. CFD: (next − current) mod 8, wrapping around. Shape number: the smallest rotation.</li>
<li>Morphology: erosion keeps a pixel only if the whole SE fits; dilation sets it if the SE hits anything. Opening = erode then dilate (removes specks), closing = dilate then erode (fills holes and gaps).</li>
<li>Q3: name the technique, say why for this image, give the steps, then an advantage and a limitation. 10 marks = about 4 techniques × 2–3 lines.</li>
</ul></section>''')

toc = [("tonight", "Plan"), ("paper", "Paper"), ("dots", "Dot map"), ("cues", "Cues")] + [(c[0], c[1].split(":")[0].split(",")[0]) for c in CH] + \
      [("q1", "Q1 theory"), ("q3", "Q3 cases"), ("traps", "Traps"), ("check", "Checklist")]

CSS = """<style>
.plan li{margin:6px 0}
.tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:10px}
.tools button{font:600 14px var(--f-body);color:var(--fg);background:var(--surface);border:1px solid var(--fg2);border-radius:6px;padding:7px 12px;cursor:pointer}
.mut{color:var(--fg2);font-size:13.5px}
.tw{overflow-x:auto}
table.dots td{vertical-align:top} table.dots td a{white-space:nowrap;margin-right:6px;font-size:14px}
table.freq td:nth-child(3){text-align:center;font-family:var(--f-mono)} table.freq td:last-child{font-size:13.5px;color:var(--fg2)}
.pattern{background:var(--surface);border:1.5px solid var(--ink);border-radius:8px;padding:10px 14px;margin:12px 0}
.pattern .k{display:block;font-family:var(--f-mono);font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--fg2);margin-bottom:4px}
.pattern ul{margin:0;padding-left:1.2em} .pattern li{margin:4px 0} .pattern .conn{margin:8px 0 0;font-size:14.5px}
details.fw,details.exs{border:1px solid var(--line);border-radius:8px;padding:2px 12px;margin:12px 0;background:var(--surface)}
details.fw>summary,details.exs>summary,details.ex>summary{cursor:pointer;font-weight:700;padding:8px 0}
details.ex{border-top:1px dashed var(--line);padding:0 4px} details.ex>summary{font-weight:600} details.ex>summary span,details.ans>summary span{color:var(--fg2);font-weight:400;font-size:13.5px}
h3.qs{margin:22px 0 6px}
.qc{border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin:14px 0;background:var(--bg)}
.qhead{display:flex;flex-wrap:wrap;gap:6px 8px;align-items:center;margin-bottom:8px}
.qhead b{font-family:var(--f-display);font-size:18px;margin-right:4px}
.clo{font:600 11.5px var(--f-mono);border-radius:999px;padding:2px 8px;border:1px solid var(--line)}
.clo.T{background:color-mix(in srgb,var(--c1) 18%,transparent)} .clo.M{background:color-mix(in srgb,var(--c2) 18%,transparent)} .clo.C{background:color-mix(in srgb,var(--c3) 22%,transparent)}
img.crop{display:block;max-width:100%;height:auto;border:1px solid var(--line);border-radius:6px;background:#fff;cursor:zoom-in}
details.ans{margin-top:8px} details.ans>summary{cursor:pointer;font-weight:700;color:var(--ink);padding:6px 0}
.same,.noans{color:var(--fg2);font-size:14.5px}
.chk li{margin:6px 0}
#zoom{position:fixed;inset:0;background:rgba(0,0,0,.85);display:none;align-items:center;justify-content:center;z-index:50;cursor:zoom-out;padding:10px}
#zoom.on{display:flex} #zoom img{max-width:100%;max-height:100%;background:#fff;border-radius:4px}
</style>"""
JS = """<div id="zoom"><img alt=""></div><script>
(() => {
  const z = document.getElementById('zoom'), zi = z.querySelector('img');
  document.addEventListener('click', e => {
    if (e.target.matches('img.crop')) { zi.src = e.target.src; zi.alt = e.target.alt; z.classList.add('on'); }
    else if (z.contains(e.target)) z.classList.remove('on');
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') z.classList.remove('on'); });
  const all = o => document.querySelectorAll('details.ans').forEach(d => d.open = o);
  document.getElementById('openall').onclick = () => all(true);
  document.getElementById('closeall').onclick = () => all(false);
})();
</script>"""

htmlout = page("DIP Ultimate", "CSE 4227 · Prof. Kalpoma · AUST · CLO1 + CLO2 + CLO3",
               "DIP, every dot connected",
               "Every past question of hers (Spring 2022 to Spring 2025, plus the Fall 2025 quizzes) as the real paper image, next to the worked answer and simulator from your lesson pages. Grouped by chapter, each with the pattern she asks in and the formula wall. Fall 2024 and the other examiners' sections are left out.",
               toc, S, extra=MCSS + QCSS + CSS + sim_assets(images=SIM_IMAGES) + f"<script>{QJS}</script>" + JS)
htmlout = htmlout.replace("<title>", '<meta name="viewport" content="width=device-width, initial-scale=1"><title>', 1)
OUT.write_text(htmlout, encoding="utf-8")
used = sorted({crop(q) for q in OURS})
(OUT.parent / "files.json").write_text(json.dumps(used), encoding="utf-8")
print(OUT, OUT.stat().st_size, "questions", len(OURS), "with answers", sum(1 for q in OURS if q in by_q),
      "no answer", [q for q in sorted(OURS, key=qkey) if q not in by_q], "extras", sum(len(v) for v in extra.values()))
