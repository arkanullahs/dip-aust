# Builds the whole site into _site/: runs every lesson and revision generator in src/,
# then wraps each page as a full HTML document, rewrites links between pages and writes the home page.
# Usage: python build.py          (stdlib only, Python 3.10+)
import html, json, re, shutil, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
SRC, OUT = REPO / "src", REPO / "_site"
sys.path.insert(0, str(SRC))

# ---------------------------------------------------------------- the catalog
# One entry per page. To add a page: write its generator (or drop a static HTML file in src/),
# then add a line here. "made" is the file the generator writes; "art" is the old claude.ai id,
# kept so links inside older pages still resolve.
LESSONS = [  # deck, chapter, slug, title, what it covers, artifact id
    ("01–02", "Ch 1–2", "01-02-fundamentals", "Introduction and digital image fundamentals",
     "Human eye, image formation, sampling and quantization, resolution, L = 2^k, M×N×k bits, zooming by nearest neighbour.", "6JjedKPgBz7cwxVaQrzobW"),
    ("03", "Ch 2", "03-pixels", "Pixel relationships",
     "4-, 8- and m-neighbours, adjacency, paths, connected components, D4 / D8 / Euclidean distance.", "U5XjXXih4nAAcmAaKeVwx8"),
    ("04", "Ch 3", "04-intensity", "Intensity transformations",
     "Negative, log, power-law (gamma), piecewise linear, contrast stretching, gray-level slicing, bit-plane slicing.", "2qjwACXWKTzu8p5Aayccr5"),
    ("05", "Ch 3", "05-histogram", "Histogram processing",
     "Histograms and the 4 image types, sliding, stretching, equalization step by step, histogram matching.", "Qt4kTFXCiVGnU2vgy6Y9NK"),
    ("06", "Ch 3", "06-smoothing", "Smoothing spatial filters",
     "Correlation vs convolution, mean and weighted average, borders, median, min and max filters, noise.", "E4eeC6pkMmhGX66dheSjMj"),
    ("07", "Ch 3", "07-sharpening", "Sharpening spatial filters",
     "1st and 2nd derivatives, Laplacian derivation and masks, sharpening g = f ± ∇²f, Sobel and Prewitt gradients.", "K14i96mZprNmn92k8y7YtF"),
    ("08", "Ch 10", "08-edges", "Segmentation I: points, lines, edges, Canny",
     "Point and line masks, gradient magnitude and angle, LoG and zero crossings, Canny NMS and hysteresis.", "BoW6fySYaxW8oKx7Abem1U"),
    ("09", "Ch 10", "09-regions", "Segmentation II: thresholding and regions",
     "Global and iterative thresholding, region growing, split and merge.", "TiabWz7aSGKZZ2RdgbusT4"),
    ("10", "Ch 11", "10-chain-code", "Chain code",
     "4- and 8-direction chain codes, first difference, normalising for start point and rotation, shape number.", "64f8ExYNkonuEM17no7D6o"),
    ("11", "Ch 9", "11-morphology-1", "Morphology I",
     "Structuring elements, erosion, dilation, opening, closing, boundary extraction, region filling, counting coins.", "PnjH4weLv1WAgnFRmdLHre"),
    ("12", "Ch 9", "12-morphology-2", "Morphology II",
     "Hit-or-miss transform, corners and end points, thinning, thickening.", "N1ZWaqJAJ2MZaW7DqRLZdZ"),
    ("13", "Ch 8", "13-compression", "Image compression",
     "Redundancy, compression ratio, entropy, Huffman, Golomb, arithmetic, LZW, run-length coding, RMSE.", "G4ZKL2xjzZJazc12gdypDP"),
    ("14", "Ch 6", "14-colour", "Colour image processing",
     "Colour fundamentals, RGB cube, CMY(K), HSI and the conversions.", "7hVft4bZ8ZytybJ4hR9bZ8"),
]
REVISION = [  # slug, title, blurb, generated file, artifact id
    ("ultimate", "Ultimate revision: every past question", "Each past final and quiz question as the paper image, with its worked answer and simulator, grouped by chapter, with the pattern and formula wall.", "mega/ultimate/dip_ultimate.html", "AjLxeuxw8oBvd6Ty8EZvCr"),
    ("mega-sheet", "Mega sheet", "Cue words, every formula with a worked line, Q1 theory points, Q3 case answers and traps on one page.", "mega/dip_mega_sheet.html", "QpFPAaWU9x11nFxhsmYA5G"),
    ("segmentation-fast-track", "Segmentation fast track", "The minimum of decks 08–09 for the exam, with numerics.", "mega/seg_fast_track.html", "QkuyxffpQT9TdvpFkQSsbv"),
    ("f25-quiz", "Fall 2025 quiz answers", "All 12 Fall 2025 quiz questions, answered in full with simulators.", "mega/f25_quiz_answers.html", "F5G1hnSxE8uXTAwfq9N3wZ"),
    ("past-questions", "Past questions only", "Every past question as the paper image, without answers, for self-testing.", "static/past_questions.html", "PTKz3h82tpExAwC34BQnuL"),
]
TRAINERS = [  # slug, title, blurb, source, artifact id
    ("region-growing", "Region growing trainer", "Circle the pixels that join, check yourself, and get the exam write-up table.", "trainers/rg_trainer.html", "UbjFCUUhp7JyJgzkFthvLS"),
    ("lzw", "LZW trainer", "Fill the LZW dictionary table the way it is done on paper.", "trainers/lzw_trainer.html", "KAWJzbW2T9dUJ6bfjc9w28"),
    ("chain-code", "Chain code trainer", "Walk a boundary, write the chain code, first difference and shape number.", "trainers/cc_trainer.html", "Qw67rrRo2rNngbz9G4x552"),
]
PAGES = [(f"lessons/{s}.html", f"d{d[-2:]}/deck{d[-2:]}_lesson.html", a) for d, _, s, _, _, a in LESSONS] + \
        [(f"revision/{s}.html", f, a) for s, _, _, f, a in REVISION] + [(f"trainers/{s}.html", f, a) for s, _, _, f, a in TRAINERS]


# ---------------------------------------------------------------- generators
def run(script):
    print("build", script.relative_to(REPO))
    subprocess.run([sys.executable, "-I", "-X", "utf8", script.name], check=True, cwd=script.parent)


def generate():
    for b in sorted(SRC.glob("d[0-9][0-9]/build*.py")):
        run(b)
    run(SRC / "must.py")                       # must-study marks on the deck pages
    for name in ("build_mega.py", "build_seg.py", "build_quiz.py", "build_ultimate.py"):  # these lift from the decks
        run(SRC / "mega" / name)


# ---------------------------------------------------------------- assembling
BAR = """<nav class="sitebar"><style>.sitebar{{font:14px/1.4 system-ui,-apple-system,"Segoe UI",sans-serif;padding:8px 16px;border-bottom:1px solid rgba(127,127,127,.35)}}.sitebar a{{color:inherit;text-decoration:none;font-weight:600}}.sitebar a:hover{{text-decoration:underline}}</style><a href="{rel}index.html">← DIP for AUST · all pages</a></nav>"""


def wrap(h, rel, links):
    for art, path in links.items():
        h = h.replace(f"https://claude.ai/artifact/{art}", rel + path)
    if "viewport" not in h[:3000]:
        h = h.replace("<meta charset=\"utf-8\">", '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">', 1)
    h = re.sub(r'<meta name="claude:[^"]*" content="[^"]*">', "", h)
    m = re.search(r"<body[^>]*>", h) or re.search(r"<(div|main|header|section)\b", h)
    i = m.end() if m.group(0).startswith("<body") else m.start()
    h = h[:i] + BAR.format(rel=rel) + h[i:]
    if not h.lstrip().lower().startswith("<!doctype"):
        h = '<!doctype html><html lang="en">' + h
    return h


def home():
    from kit import page, tbl
    card = lambda href, title, blurb, tag="": f'<a class="card" href="{href}"><span class="tag">{tag}</span><b>{html.escape(title)}</b><span>{html.escape(blurb)}</span></a>'
    lessons = "".join(card(f"lessons/{s}.html", t, b, f"Deck {d} · {c}") for d, c, s, t, b, _ in LESSONS)
    rev = "".join(card(f"revision/{s}.html", t, b, "Revision") for s, t, b, _, _ in REVISION)
    tr = "".join(card(f"trainers/{s}.html", t, b, "Trainer") for s, t, b, _, _ in TRAINERS)
    S = [
        f'''<section class="sec" id="start"><div class="sechead"><h2>How to use this site</h2></div>
<ol><li><b>Learn:</b> go through the <a href="#lessons">lessons</a> in order. Each one explains its slide deck in plain words, with real graphs, every past question solved in answer-script form, and step-by-step simulators wherever a method appears.</li>
<li><b>Practise:</b> use the <a href="#trainers">trainers</a> for the methods that are easiest to get wrong on paper.</li>
<li><b>Revise:</b> before the final, use the <a href="#revision">revision pages</a>. The ultimate page puts every past question next to its answer.</li></ol>
<p>The course is CSE 4227 Digital Image Processing at AUST. The final paper has 3 sections: Q1 is theory (CLO1), Q2 is maths in the spatial domain (CLO2) and Q3 is case studies (CLO3). Questions marked ★ in the lessons are the ones that keep coming back.</p></section>''',
        f'<section class="sec" id="lessons"><div class="sechead"><h2>Lessons, one per slide deck</h2></div><div class="cards">{lessons}</div></section>',
        f'<section class="sec" id="revision"><div class="sechead"><h2>Revision</h2></div><div class="cards">{rev}</div></section>',
        f'<section class="sec" id="trainers"><div class="sechead"><h2>Trainers</h2></div><div class="cards">{tr}</div></section>',
        '''<section class="sec" id="contribute"><div class="sechead"><h2>Fix or add something</h2></div>
<p>Every page is generated from Python in the <a href="https://github.com/arkanullahs/dip-aust">GitHub repository</a>, and every number on a page is computed there. To fix a mistake or add a lesson, edit the generator in <code>src/</code>, run <code>python build.py</code>, and open a pull request. The site rebuilds itself when a change lands on <code>main</code>. The README explains the layout.</p></section>''',
    ]
    extra = """<style>
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,260px),1fr));gap:12px;margin:12px 0}
.card{display:flex;flex-direction:column;gap:4px;padding:12px 14px;border:1px solid var(--line);border-radius:10px;background:var(--surface);color:var(--fg);text-decoration:none}
.card:hover,.card:focus-visible{border-color:var(--ink);outline:none}
.card .tag{font:600 11.5px var(--f-mono);text-transform:uppercase;letter-spacing:.05em;color:var(--fg2)}
.card b{font-family:var(--f-display);font-size:17px}
.card span:last-child{font-size:14.5px;color:var(--fg2)}
</style>"""
    return page("DIP for AUST", "CSE 4227 · Digital Image Processing · AUST", "Digital Image Processing, from zero",
                "Plain-words lessons for every slide deck, past questions solved the way the exam wants them, and simulators you can step through.",
                [("start", "Start"), ("lessons", "Lessons"), ("revision", "Revision"), ("trainers", "Trainers"), ("contribute", "Contribute")],
                S, extra=extra)


def assemble():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    links = {a: p for p, _, a in PAGES}
    for path, src, _ in PAGES:
        dst = OUT / path
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(wrap((SRC / src).read_text(encoding="utf-8"), "../", links), encoding="utf-8")
    crops = json.loads((SRC / "mega" / "ultimate" / "files.json").read_text(encoding="utf-8"))
    (OUT / "revision" / "c").mkdir()
    for c in crops:
        shutil.copy(REPO / "crops" / c, OUT / "revision" / "c" / c)
    (OUT / "index.html").write_text(wrap(home(), "", links).replace(BAR.format(rel=""), "", 1), encoding="utf-8")
    (OUT / ".nojekyll").write_text("")
    left = [p for p in OUT.rglob("*.html") if "claude.ai/artifact" in p.read_text(encoding="utf-8")]
    print("site:", OUT, sum(1 for _ in OUT.rglob("*.html")), "pages;", "pages still linking to claude.ai:", [str(p.relative_to(OUT)) for p in left])


if __name__ == "__main__":
    if "--no-generate" not in sys.argv:
        generate()
    assemble()
