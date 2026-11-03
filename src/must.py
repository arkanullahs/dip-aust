# Marks the must-study sections on every built deck page (run after any dNN/buildNN.py).
# Evidence: her finals SP22–SP25, F21–F23 and the Fall 2025 quizzes; Fall 2024 excluded.
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
MUST = {
    "d02/deck02_lesson.html": {
        "dig": "sampling vs quantization theory, asked in 3 finals",
        "res": "L = 2^k and M×N×k bits: Fall 25 quiz and 2 finals"},
    "d03/deck03_lesson.html": {
        "adj": "4 / 8 / m-adjacency: part of the distance question in 5 finals",
        "path": "m-path and connected components: same 5 finals",
        "dist": "D4, D8, De with numbers: asked in 5 of her finals",
        "papers": "the exact past questions, solved"},
    "d04/deck04_lesson.html": {
        "piece": "(r1,s1),(r2,s2) identity / threshold / stretch: asked in 4 finals",
        "cs": "contrast stretching with numbers: F23, SP24",
        "gls": "gray-level slicing: Fall 25 quiz, tumor cases in F22 and SP23",
        "bit": "bit-plane slicing: SP24, SP25",
        "case": "which transformation for which problem: case marks in 4 finals"},
    "d05/deck05_lesson.html": {
        "gen": "histogram + 4 types with sketches: theory in 3 finals and 2 quizzes",
        "he": "histogram equalization: in almost every final (8–9 marks)",
        "hepq": "the equalization questions she set, solved",
        "theory": "the histogram theory answers she repeats"},
    "d06/deck06_lesson.html": {
        "mean": "mean / weighted average numbers: filter questions in 6 finals",
        "median": "median for salt-and-pepper: numbers and case questions",
        "pq": "the filter questions she set, solved"},
    "d07/deck07_lesson.html": {
        "deriv": "1st vs 2nd derivative: the theory she asks",
        "lapenh": "Laplacian sharpening, g = f − ∇²f: SP25 case (Laplacian vs Sobel)",
        "grad": "Sobel / Prewitt masks and |Gx| + |Gy|"},
    "d08/deck08_lesson.html": {
        "seg": "two approaches of segmentation: theory in 7 finals",
        "edges": "1st vs 2nd derivative edges",
        "canny": "Canny steps: SP25, F23"},
    "d09/deck09_lesson.html": {
        "grow": "region growing: SP23 tumor case",
        "thr": "global / adaptive threshold: SP23 and SP25 cases"},
    "d10/deck10_lesson.html": {
        "cc": "write the chain code: in 5 finals and the Fall 25 quiz",
        "norm": "CC → CFD → NCFD: the part that carries the marks",
        "papers": "the exact past questions, solved"},
    "d11/deck11_lesson.html": {
        "ero": "erosion: numbers and theory in 6 finals",
        "dil": "dilation: same questions",
        "open": "opening / closing: case questions in 5 finals",
        "bnd": "boundary extraction: SP25 roads case, Fall 25 quiz",
        "pq": "the numeric questions she set, solved",
        "theory": "the morphology theory and case answers she repeats"},
    "d12/deck12_lesson.html": {
        "proc": "hit-or-miss procedure: asked in 4 finals",
        "corner": "corner detection SEs: F21, F23",
        "end": "end points: F22, SP23"},
    "d13/deck13_lesson.html": {
        "cr": "C_R and R_D: in 5 finals",
        "red": "the three redundancies: theory in 5 finals",
        "huff": "Huffman: in 7 finals",
        "ent": "entropy and efficiency: with every Huffman question",
        "huffpq": "the Huffman questions she set, solved",
        "gol": "Golomb: SP24, F23, F21",
        "lzw": "LZW step table: SP25, F23, SP22 (10 marks)",
        "fid": "RMSE / SNR: in 4 finals"},
    "d14/deck14_lesson.html": {
        "mix": "additive vs subtractive: SP22, F22, SP25",
        "models": "which model for printing / display: F21, SP24, SP25",
        "rgb": "RGB cube and how gray forms: in 5 finals"},
}

CSS = """
.sec.must{box-shadow:inset 4px 0 0 var(--mark);padding-left:14px;margin-left:-14px}
.tag.must{background:var(--mark);color:var(--bg);font-size:12.5px}
.tag.must::before{content:"★ "}
.mustbox{border:2px solid var(--mark);border-radius:8px;padding:10px 16px;margin:14px 0;background:var(--surface)}
.mustbox .k{color:var(--mark)} .mustbox ul{margin:6px 0 0} .mustbox li{margin:4px 0}
nav.toc a.must{border-color:var(--mark);color:var(--mark);font-weight:700}
@media (max-width:720px){.sec.must{margin-left:0;padding-left:10px}}
"""


def mark(path, must):
    s = path.read_text(encoding="utf-8")
    if 'class="mustbox"' in s:
        return "already marked"
    titles = {}
    for sid in must:
        old = f'<section class="sec" id="{sid}"><div class="sechead"><h2>'
        assert s.count(old) == 1, (path, sid)
        titles[sid] = re.search(re.escape(old) + r"(.*?)</h2>", s).group(1)
        s = s.replace(old, old.replace('class="sec"', 'class="sec must"'))
        i = s.index(f'id="{sid}"'); j = s.index('<div class="meta">', i) + len('<div class="meta">')
        s = s[:j] + '<span class="tag must">Must study</span>' + s[j:]
        a = f'<a href="#{sid}">'
        assert s.count(a) == 1, (path, "toc", sid)
        s = s.replace(a, f'<a class="must" href="#{sid}">★ ')
    box = ('<div class="mustbox"><span class="k">★ Must study on this page</span><ul>'
           + "".join(f'<li><a href="#{k}"><b>{titles[k]}</b></a>: {why}</li>' for k, why in must.items()) + "</ul></div>")
    k = s.index("</nav>") + len("</nav>")
    s = s[:k] + box + s[k:]
    k = s.index("</style>")
    s = s[:k] + CSS + s[k:]
    path.write_text(s, encoding="utf-8")
    return f"{len(must)} marked"


for rel, must in MUST.items():
    print(rel, mark(HERE / rel, must))
