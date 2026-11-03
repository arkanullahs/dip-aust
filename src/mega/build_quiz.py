# Fall 2025 quizzes: every question with its full answer and a simulator. Long answers are lifted from the built deck pages.
import re, sys, json, math
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))
from kit import page, paper, idea, formula, trap, tbl, mat, mats, bars, plot, fn, figs, sim, sim_assets, rhu

OUT = HERE / "f25_quiz_answers.html"


def S2(id_, title, meta, body):
    return f'<section class="sec" id="{id_}"><div class="sechead"><h2>{title}</h2><div class="meta"><span class="slides">{meta}</span></div></div>{body}</section>'


def lift(deck, tag_re):
    """Paper box whose tag matches tag_re, plus the simulators right after it, from a built deck page."""
    h = (ROOT / deck / f"deck{deck[1:]}_lesson.html").read_text(encoding="utf-8")
    for m in re.finditer(r'<section class="paper">', h):
        i, depth = m.start(), 0
        for t in re.finditer(r'<(/?)section\b', h[i:]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                j = h.index(">", i + t.end()) + 1
                break
        if not re.search(tag_re, re.search(r'class="ptag">(.*?)</span>', h[i:j]).group(1)):
            continue
        k = j
        while h[k:].lstrip().startswith('<div class="simwrap">'):
            k = len(h) - len(h[k:].lstrip())
            k = h.index("></div></div>", k) + len("></div></div>")
        return h[i:k]
    raise LookupError(f"{deck}: no paper tagged {tag_re}")


def qsim(kind, cap, **cfg):
    return f'<div class="simwrap"><p class="simcap"><b>Try it:</b> {cap}</p><div class="qsim" data-q="{kind}" data-cfg=\'{json.dumps(cfg)}\'></div></div>'


S = []

# ---------------------------------------------------------------- Quiz 1 set C
C = 255 / math.log10(256)
logv = {r: rhu(C * math.log10(1 + r)) for r in (10, 50, 100, 255)}
assert logv == {10: 110, 50: 181, 100: 212, 255: 255}
logplot = plot(255, 255, curves=[{"pts": fn(lambda r: C * math.log10(1 + r), 255), "cls": "c1", "label": "log", "at": (60, 205)},
                                 {"pts": fn(lambda r: 10 ** (r / C) - 1, 255), "cls": "c3", "label": "inverse log", "at": (200, 60)}],
              points=[(r, s, f"{r}→{s}") for r, s in logv.items() if r < 255], diag=True,
              xticks=[0, 50, 100, 150, 200, 255], yticks=[0, 128, 255], caption="s = c·log(1 + r), c = 105.89 (8-bit). Dashed: identity s = r.")
S.append(S2("q1c1", "Quiz 1 (C) Q1 · Logarithmic transformation", "6 marks · deck 04", f"""
{paper("Fall 25 Quiz 1 (set C) Q1", "6 marks", f'''
<p class="q">Discuss logarithmic transformations for image enhancement.</p>
<p><b>Definition.</b> The log transformation is a basic intensity transformation:</p>
{formula("s = c · log(1 + r)")}
<p>r = input gray level, s = output gray level, c = a constant, r ≥ 0. The 1 is added so that log 0 never occurs. To map 0…255 onto 0…255, c = 255 / log(256) = 105.89.</p>
<p><b>Shape.</b> Draw this graph in the answer script:</p>
{logplot}
<p>The curve lies above the diagonal. It is steep for small r and flat for large r.</p>
<p><b>Properties.</b></p>
<ul><li>For <b>low input values</b> the range is <b>expanded</b>: dark regions are spread out and their details become visible.</li>
<li>For <b>high input values</b> the range is <b>compressed</b>: bright regions are squeezed together.</li></ul>
<p><b>Worked values</b> (c = 105.89):</p>
{tbl(["r", "c·log(1 + r)", "s"], [[r, f"105.89 × log({1 + r}) = {C * math.log10(1 + r):.1f}", s] for r, s in logv.items()], "narrow")}
<p>The input band 0–50 (20% of the range) becomes 0–181 (71%). The band 100–255 shrinks to 212–255.</p>
<p><b>Application.</b> Use it when the input has a very large <b>dynamic range</b> that the display cannot show. The standard example is the <b>Fourier spectrum</b>, whose values run from 0 to about 1.5×10<sup>6</sup>. On a display only the bright centre shows; after the log transform the whole spectrum is visible. That is why it is called <b>dynamic-range compression</b>.</p>
<p><b>Inverse log</b>, s = 10<sup>r/c</sup> − 1, does the opposite: it expands the bright values and compresses the dark ones.</p>
''')}
{qsim("log", "move r and watch where it lands on the curve. Notice how a small step in the dark end moves s a lot, and the same step in the bright end hardly moves it.")}
"""))

S.append(S2("q1c2a", "Quiz 1 (C) Q2(a) · Gray-level slicing, X-ray bones", "11 marks · deck 04", f"""
{lift("d04", r"Fall 25 Quiz 2\(a\)")}
{qsim("slice", "type any pixel value, or change the band, and read off both approaches. The dot moves on both curves.", A=120, B=200, r=150)}
"""))

S.append(S2("q1c2b", "Quiz 1 (C) Q2(b) · 10-bit shades and intensity resolution", "3 marks · deck 02 / 04", f"""
{lift("d04", r"Fall 25 Quiz 2\(b\)")}
{idea("Every extra bit doubles the number of grays. 8 bits give 256, 10 bits give 1024, so the steps between neighbouring grays are 4 times finer. Fewer bits give visible bands (false contouring).")}
{qsim("bits", "slide k and read off L = 2<sup>k</sup> and the range. The strip shows the gray steps, which become visible bands at small k.", k=10)}
"""))

# ---------------------------------------------------------------- Quiz 1 set D
S.append(S2("q1d1", "Quiz 1 (D) Q1 · How to make a histogram, what it says", "3 + 3 marks · deck 05", f"""
{lift("d05", r"Fall 25 Quiz \(set D\) Q1")}
{qsim("types", "pick an image type. The page makes a small image of that type and counts its histogram from scratch, the same way as in steps 1–3.", t="dark")}
"""))

types = {"dark": [9, 14, 11, 6, 3, 1, 0, 0], "bright": [0, 0, 1, 3, 6, 11, 14, 9], "low": [0, 0, 4, 16, 20, 4, 0, 0], "high": [5, 6, 6, 5, 6, 6, 5, 5]}
S.append(S2("q1d2a", "Quiz 1 (D) Q2(a) · Four intensity types and their histograms", "4 marks · deck 05", f"""
{paper("Fall 25 Quiz 1 (set D) Q2(a) · also SP23 Q2(b)", "4 marks", f'''
<p class="q">Explain the four basic types of intensity characteristics of an image and their corresponding histograms.</p>
<p>The <b>histogram</b> of a digital image with gray levels 0 … L−1 is h(r<sub>k</sub>) = n<sub>k</sub>, the number of pixels with gray level r<sub>k</sub>. Its shape shows the four basic types:</p>
{figs(bars(types["dark"], caption="(1) Dark image"), bars(types["bright"], caption="(2) Bright image"))}
{figs(bars(types["low"], caption="(3) Low-contrast image"), bars(types["high"], caption="(4) High-contrast image"))}
<ol><li><b>Dark image:</b> most pixels have low values, so the histogram is crowded on the <b>left</b> (dark) side. The image looks dark and details in the shadows are hidden.</li>
<li><b>Bright image:</b> most pixels have high values, so the histogram is crowded on the <b>right</b> side. The image looks washed out.</li>
<li><b>Low-contrast image:</b> the pixels occupy a <b>narrow</b> range of gray levels in the middle, so the histogram is narrow. The image looks dull and grayish.</li>
<li><b>High-contrast image:</b> the pixels cover <b>almost the whole range</b>, and the histogram is spread fairly evenly. The image shows a lot of gray-level detail and looks sharp.</li></ol>
<p>Histogram equalization tries to turn types 1–3 into type 4.</p>
''')}
{qsim("types", "click each type: a fresh random image of that kind and its counted histogram. Compare with the four sketches.", t="low")}
"""))

S.append(S2("q1d2b", "Quiz 1 (D) Q2(b) · Histogram equalization from counts", "10 marks · deck 05", lift("d05", r"Fall 25 Quiz \(set D\) Q2\(b\)")))

# ---------------------------------------------------------------- Quiz 2 set C
S.append(S2("q2c1", "Quiz 2 (C) Q1 · Same black/white count: same histogram?", "2 + 4 marks · deck 05", f"""
{paper("Fall 25 Quiz 2 (set C) Q1", "2 + 4 marks", f'''
<p class="q">What is the histogram of an image? Two 20×20 images have equal numbers of black (0) and white (1) pixels. Are their histograms identical? Explain.</p>
<p><b>Histogram.</b> For a digital image with gray levels in [0, L−1], the histogram is the discrete function</p>
{formula("h(r<sub>k</sub>) = n<sub>k</sub>,  k = 0, 1, …, L−1")}
<p>where n<sub>k</sub> is the number of pixels with gray level r<sub>k</sub>. It is drawn as bars of n<sub>k</sub> against r<sub>k</sub>. The normalized histogram is p(r<sub>k</sub>) = n<sub>k</sub> / MN.</p>
<p><b>The two images.</b> Each has 20 × 20 = 400 pixels, and equal numbers of black and white, so 200 black and 200 white. For both images:</p>
{formula("h(0) = 200,  h(1) = 200")}
{bars([200, 200], ["0 (black)", "1 (white)"], caption="Histogram of image 1 = histogram of image 2")}
<p><b>Yes, the histograms are identical</b>, even if one image is half black and half white and the other is a checkerboard. A histogram records only <b>how many</b> pixels have each value, not <b>where</b> they are. It has no spatial information.</p>
<p>So different images can have the same histogram, and an image cannot be rebuilt from its histogram.</p>
''')}
{qsim("shuffle", "rearrange the same 200 black and 200 white pixels. The picture changes; the counted histogram never does.")}
"""))

S.append(S2("q2c2", "Quiz 2 (C) Q2 · Histogram equalization of a 4×5 image", "14 marks · deck 05", lift("d05", r"Fall 25 Quiz \(set C\) Q2")))

# ---------------------------------------------------------------- Quiz 3 set D
sig = [10, 13, 9, 12, 10, 11, 40, 38, 41, 39, 42, 40]
smo = [sig[0]] + [rhu((sig[i - 1] + 2 * sig[i] + sig[i + 1]) / 4) for i in range(1, len(sig) - 1)] + [sig[-1]]
D2 = lambda s: [s[i + 1] + s[i - 1] - 2 * s[i] for i in range(1, len(s) - 1)]
zc = lambda d: sum(1 for a, b in zip(d, d[1:]) if a * b < 0)
assert zc(D2(sig)) == 8 and zc(D2(smo)) == 3
S.append(S2("q3d1", "Quiz 3 (D) Q1 · Two approaches of segmentation, and why LoG", "4 + 2 marks · deck 08", f"""
{paper("Fall 25 Quiz 3 (set D) Q1", "4 + 2 marks", f'''
<p class="q">What are the two principal approaches to image segmentation? Why is a Laplacian filter typically combined with a Gaussian smoothing filter (LoG operator) before performing edge detection in noisy environments?</p>
<p><b>Two approaches</b> (based on two basic properties of intensity values):</p>
<ol><li><b>Discontinuity:</b> partition the image where the intensity <b>changes abruptly</b>. Methods: point, line and edge detection (gradient/Sobel, LoG, Canny).</li>
<li><b>Similarity:</b> partition the image into regions that are <b>alike</b> by a predefined rule. Methods: thresholding, region growing, region splitting and merging.</li></ol>
<p><b>Why Gaussian + Laplacian (LoG).</b></p>
<ul><li>The Laplacian is a <b>2nd derivative</b>, so it is <b>very sensitive to noise</b>: every noisy pixel gives a strong response and <b>false zero crossings</b>.</li>
<li>Gaussian smoothing first <b>removes the noise</b>, so the zero crossings of the Laplacian then mark <b>real edges</b> only.</li>
<li>Both are linear, so they combine into <b>one LoG mask</b> ∇²G (cheaper), and its zero crossings give thin, well-localised edges.</li></ul>
<p><b>Small proof</b> (a noisy step, 2nd derivative f(x+1) + f(x−1) − 2f(x)):</p>
{tbl(["", "signal", "2nd derivative", "zero crossings"], [
    ["noisy", " ".join(map(str, sig)), " ".join(map(str, D2(sig))), zc(D2(sig))],
    ["smoothed [1 2 1]/4", " ".join(map(str, smo)), " ".join(map(str, D2(smo))), zc(D2(smo))]])}
<p>Noisy: 8 sign changes, almost all false. Smoothed: the big one (7 → −7) sits at the real step, and the leftover small ones are weak, so a threshold on the jump drops them.</p>
''')}
{sim({"type": "oned", "sig": sig, "modes": ["d2"]}, "2nd derivative of the NOISY step: the signs flip again and again in the flat part.")}
{sim({"type": "oned", "sig": smo, "modes": ["d2"]}, "the same step after Gaussian-like smoothing: one strong +/− pair at the real edge.")}
"""))

S.append(S2("q3d2", "Quiz 3 (D) Q2 · Chain code: start point and rotation invariant", "7 + 7 marks · deck 10", f"""
{lift("d10", r"F25 Quiz \(Q3D\) Q2")}
{trap("Part (i) = shape number of the chain code itself (start at the smallest rotation). Part (ii) = first difference (CFD) first, then its shape number (NCFD). Use the CFD/NCFD trick from the chain-code trainer.")}
"""))

# ---------------------------------------------------------------- Quiz 4 set C
A1 = [[0] * 7 for _ in range(7)]
for r in range(1, 5):
    for c in range(1, 5):
        A1[r][c] = 1
A1[6][6] = 1
A1[2][5] = 1
SE = [[1, 1, 1]] * 3
S.append(S2("q4c1", "Quiz 4 (C) Q1 · Dilation and erosion: size and shape", "3 marks · deck 11", f"""
{lift("d11", r"Fall 25 quiz \(set C\) Q1")}
{sim({"type": "morph", "A": A1, "se": SE, "origin": [1, 1], "ops": ["erode", "dilate"], "op": "erode", "discard": False, "symmetric": True}, "a 4×4 square with a spike and a lone noise pixel. Erosion: the square shrinks to 2×2, the spike and noise vanish. Switch to dilation: everything grows by one pixel all round.")}
"""))

S.append(S2("q4c2", "Quiz 4 (C) Q2 · Edge detection with morphology", "7 marks · deck 11", lift("d11", r"Fall 25 quiz \(set C\) Q2")))

# ---------------------------------------------------------------- widgets for the questions that had no deck simulator
QJS = r"""
(() => {
const svgNS = 'http://www.w3.org/2000/svg';
const el = (t, a = {}, h = '') => { const e = document.createElement(t); for (const k in a) e.setAttribute(k, a[k]); e.innerHTML = h; return e; };
const curve = (pts, W, H, xm, ym, cls) => `<polyline class="cv ${cls}" fill="none" points="${pts.map(([x, y]) => `${(40 + x / xm * (W - 50)).toFixed(1)},${(H - 30 - y / ym * (H - 45)).toFixed(1)}`).join(' ')}"/>`;
const axes = (W, H, xl, yl, xt, yt, xm, ym) => {
  let s = `<line class="axis" x1="40" y1="${H - 30}" x2="${W - 10}" y2="${H - 30}"/><line class="axis" x1="40" y1="15" x2="40" y2="${H - 30}"/>`;
  for (const t of xt) s += `<text class="tick" x="${40 + t / xm * (W - 50)}" y="${H - 16}" text-anchor="middle">${t}</text>`;
  for (const t of yt) s += `<text class="tick" x="34" y="${H - 26 - t / ym * (H - 45)}" text-anchor="end">${t}</text>`;
  return s + `<text class="axlab" x="${W / 2}" y="${H - 2}" text-anchor="middle">${xl}</text><text class="axlab" x="10" y="${H / 2}" text-anchor="middle" transform="rotate(-90 10 ${H / 2})">${yl}</text>`;
};
const dot = (x, y, W, H, xm, ym) => `<circle class="pt acc" r="5" cx="${40 + x / xm * (W - 50)}" cy="${H - 30 - y / ym * (H - 45)}"/>`;
const range = (n) => [...Array(n).keys()];
const W = {};

W.log = (box) => {
  const c = 255 / Math.log10(256);
  box.innerHTML = `<label class="qrow">r = <input type="range" min="0" max="255" value="10"> <b class="rv"></b></label><svg viewBox="0 0 330 240" class="plot"></svg><p class="qout"></p>`;
  const inp = box.querySelector('input'), sv = box.querySelector('svg');
  const draw = () => {
    const r = +inp.value, s = c * Math.log10(1 + r);
    box.querySelector('.rv').textContent = r;
    sv.innerHTML = axes(330, 240, 'r (input)', 's (output)', [0, 100, 200, 255], [0, 128, 255], 255, 255) + curve([[0, 0], [255, 255]], 330, 240, 255, 255, 'c4') + curve(range(256).map(x => [x, c * Math.log10(1 + x)]), 330, 240, 255, 255, 'c1') + dot(r, s, 330, 240, 255, 255);
    box.querySelector('.qout').innerHTML = `s = 105.89 × log(1 + ${r}) = 105.89 × ${Math.log10(1 + r).toFixed(4)} = ${s.toFixed(2)} → <b>${Math.floor(s + 0.5)}</b>. Gain over the identity: ${(Math.floor(s + 0.5) - r) >= 0 ? '+' : ''}${Math.floor(s + 0.5) - r} levels.`;
  };
  inp.oninput = draw; draw();
};

W.slice = (box, cfg) => {
  box.innerHTML = `<div class="qrow"><label>r = <input type="number" class="r" min="0" max="255" value="${cfg.r}"></label> <label>A = <input type="number" class="a" min="0" max="255" value="${cfg.A}"></label> <label>B = <input type="number" class="b" min="0" max="255" value="${cfg.B}"></label></div><div class="figrow"><figure class="fig"><svg viewBox="0 0 300 220" class="plot s1"></svg><figcaption>Approach 1: without background</figcaption></figure><figure class="fig"><svg viewBox="0 0 300 220" class="plot s2"></svg><figcaption>Approach 2: with background</figcaption></figure></div><p class="qout"></p>`;
  const q = (s) => box.querySelector(s);
  const draw = () => {
    const r = Math.max(0, Math.min(255, +q('.r').value)), A = +q('.a').value, B = +q('.b').value, inb = r >= A && r <= B;
    const f1 = (x) => (x >= A && x <= B ? 255 : 0), f2 = (x) => (x >= A && x <= B ? 255 : x);
    const pts = (f) => range(256).flatMap(x => (x === A || x === B + 1) ? [[x - 0.001, f(x - 1)], [x, f(x)]] : [[x, f(x)]]);
    const ax = axes(300, 220, 'r', 's', [0, A, B, 255], [0, 255], 255, 255);
    q('.s1').innerHTML = ax + curve(pts(f1), 300, 220, 255, 255, 'c1') + dot(r, f1(r), 300, 220, 255, 255);
    q('.s2').innerHTML = ax + curve(pts(f2), 300, 220, 255, 255, 'c2') + dot(r, f2(r), 300, 220, 255, 255);
    q('.qout').innerHTML = `Is ${A} ≤ ${r} ≤ ${B}? <b>${inb ? 'yes' : 'no'}</b>. Approach 1: s = <b>${f1(r)}</b> (${inb ? 'highlight' : 'suppressed to 0'}). Approach 2: s = <b>${f2(r)}</b> (${inb ? 'highlight' : 'kept as r'}).`;
  };
  box.querySelectorAll('input').forEach(i => i.oninput = draw); draw();
};

W.bits = (box, cfg) => {
  box.innerHTML = `<label class="qrow">k = <input type="range" min="1" max="16" value="${cfg.k}"> <b class="kv"></b> bits</label><div class="strip"></div><p class="qout"></p>`;
  const inp = box.querySelector('input');
  const draw = () => {
    const k = +inp.value, L = 2 ** k, n = Math.min(L, 64);
    box.querySelector('.kv').textContent = k;
    box.querySelector('.strip').innerHTML = range(n).map(i => `<span style="background:hsl(0 0% ${(i / (n - 1) * 100).toFixed(1)}%)"></span>`).join('');
    box.querySelector('.qout').innerHTML = `L = 2<sup>${k}</sup> = <b>${L.toLocaleString()}</b> shades, range <b>[0, ${(L - 1).toLocaleString()}]</b>.${L > 64 ? ' (Strip shows 64 sample steps.)' : ''}`;
  };
  inp.oninput = draw; draw();
};

const grid = (vals, N, gray) => `<div class="pix" style="grid-template-columns:repeat(${N},1fr)">${vals.map(v => `<span style="background:hsl(0 0% ${gray(v)}%)"></span>`).join('')}</div>`;
const hist = (h, labels) => {
  const top = Math.max(...h, 1), Wd = 300, H = 170, bw = (Wd - 50) / h.length;
  let s = axes(Wd, H, 'gray level', 'n<tspan baseline-shift="sub">k</tspan>', [], [0, top], h.length, top);
  h.forEach((v, i) => { const bh = v / top * (H - 45), x = 40 + i * bw + bw * 0.15; s += `<rect class="bar c1" x="${x}" y="${H - 30 - bh}" width="${bw * 0.7}" height="${bh}"/><text class="bval" x="${x + bw * 0.35}" y="${H - 34 - bh}" text-anchor="middle">${v}</text><text class="tick" x="${x + bw * 0.35}" y="${H - 16}" text-anchor="middle">${labels[i]}</text>`; });
  return `<svg viewBox="0 0 ${Wd} ${H}" class="plot">${s}</svg>`;
};

W.shuffle = (box) => {
  box.innerHTML = `<div class="qrow"><button data-m="half">Half / half</button><button data-m="check">Checkerboard</button><button data-m="stripe">Stripes</button><button data-m="rand">Random shuffle</button></div><div class="figrow"><figure class="fig img"></figure><figure class="fig hst"></figure></div><p class="qout"></p>`;
  const make = (m) => {
    let v = range(400).map(i => { const r = Math.floor(i / 20), c = i % 20; return m === 'half' ? +(c >= 10) : m === 'check' ? (r + c) % 2 : m === 'stripe' ? Math.floor(c / 2) % 2 : +(i < 200); });
    if (m === 'rand') for (let i = 399; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [v[i], v[j]] = [v[j], v[i]]; }
    const h = [v.filter(x => x === 0).length, v.filter(x => x === 1).length];
    box.querySelector('.img').innerHTML = grid(v, 20, x => x * 100) + '<figcaption>the 20×20 image</figcaption>';
    box.querySelector('.hst').innerHTML = hist(h, ['0', '1']) + '<figcaption>counted from the image</figcaption>';
    box.querySelector('.qout').innerHTML = `Counted: h(0) = <b>${h[0]}</b>, h(1) = <b>${h[1]}</b>. Different picture, same histogram.`;
  };
  box.querySelectorAll('button').forEach(b => b.onclick = () => make(b.dataset.m)); make('half');
};

W.types = (box, cfg) => {
  const mu = { dark: [1.3, 1.2], bright: [5.7, 1.2], low: [3.5, 0.6], high: [3.5, 9] };
  box.innerHTML = `<div class="qrow">${Object.keys(mu).map(t => `<button data-t="${t}">${{ dark: 'Dark', bright: 'Bright', low: 'Low contrast', high: 'High contrast' }[t]}</button>`).join('')}</div><div class="figrow"><figure class="fig img"></figure><figure class="fig hst"></figure></div><p class="qout"></p>`;
  const make = (t) => {
    const [m, sd] = mu[t];
    const v = range(64).map(() => { let x; if (t === 'high') x = Math.floor(Math.random() * 8); else { const g = Math.sqrt(-2 * Math.log(Math.random() || 1e-9)) * Math.cos(2 * Math.PI * Math.random()); x = Math.round(m + g * sd); } return Math.max(0, Math.min(7, x)); });
    const h = range(8).map(k => v.filter(x => x === k).length);
    box.querySelector('.img').innerHTML = grid(v, 8, x => x / 7 * 100) + '<figcaption>8×8, 3-bit image</figcaption>';
    box.querySelector('.hst').innerHTML = hist(h, range(8)) + '<figcaption>h(r<sub>k</sub>) = n<sub>k</sub></figcaption>';
    box.querySelector('.qout').innerHTML = `Step 2 tally: ${h.map((n, k) => `h(${k}) = ${n}`).join(', ')}. Sum = ${h.reduce((a, b) => a + b, 0)} = 8 × 8 pixels.`;
  };
  box.querySelectorAll('button').forEach(b => b.onclick = () => make(b.dataset.t)); make(cfg.t);
};

document.querySelectorAll('.qsim').forEach(b => W[b.dataset.q](b, JSON.parse(b.dataset.cfg || '{}')));
})();
"""

EXTRA = """<style>
.qsim{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:6px 0 18px}
.qsim .qrow{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;margin-bottom:8px}
.qsim input[type=range]{width:min(260px,60vw)} .qsim input[type=number]{width:5.5em;font:inherit;padding:3px 6px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)}
.qsim button{font:inherit;font-size:14px;padding:5px 12px;border:1px solid var(--ink);border-radius:7px;background:var(--bg);color:var(--ink);cursor:pointer}
.qsim button:hover{background:var(--band)}
.qsim .qout{margin:8px 0 0;font-size:15.5px}
.qsim .strip{display:flex;height:38px;border:1px solid var(--line);border-radius:6px;overflow:hidden}
.qsim .strip span{flex:1}
.qsim .pix{display:grid;width:min(220px,70vw);aspect-ratio:1;border:1px solid var(--line)}
.qsim .fig.img{display:flex;flex-direction:column;align-items:center;justify-content:center}
.qsim .plot .c4{stroke:var(--c4);stroke-dasharray:4 4}
</style>"""

toc = [("q1c1", "Q1C·1 Log"), ("q1c2a", "Q1C·2a Slicing"), ("q1c2b", "Q1C·2b 10-bit"), ("q1d1", "Q1D·1 Histogram"), ("q1d2a", "Q1D·2a Four types"),
       ("q1d2b", "Q1D·2b HE counts"), ("q2c1", "Q2C·1 Same histogram?"), ("q2c2", "Q2C·2 HE 4×5"), ("q3d1", "Q3D·1 Segmentation + LoG"),
       ("q3d2", "Q3D·2 Chain code"), ("q4c1", "Q4C·1 Erosion/dilation"), ("q4c2", "Q4C·2 Morph edges")]
assert [t[0] for t in toc] == re.findall(r'<section class="sec" id="([^"]+)"', "".join(S))
OUT.write_text(page("Fall 2025 Quiz Answers", "CSE 4227 · Fall 2025 · quizzes 1–4, all sets we have", "Every Fall 2025 quiz question, answered",
                    "All 12 questions from quizzes 1–4 (sets C and D), written the way you would write them in the answer script. Every question has a simulator under it: step through it or change the numbers.",
                    toc, S, extra=EXTRA + sim_assets() + f"<script>{QJS}</script>"), encoding="utf-8")
print(OUT, OUT.stat().st_size)
