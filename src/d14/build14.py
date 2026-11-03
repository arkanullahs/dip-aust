"""Builds deck14_lesson.html: colour image processing (RGB, CMY/CMYK, HSI). Fall 2024 questions left out on purpose."""
import sys, pathlib, math
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from kit import *

OUT = pathlib.Path(__file__).with_name("deck14_lesson.html")


# ---------------------------------------------------------------- maths (slides 20 and 29)
def norm(rgb):
    return [v / 255 for v in rgb]


def cmy(rgb):
    return [1 - v for v in norm(rgb)]


def hsi(rgb):
    R, G, B = norm(rgb)
    num = 0.5 * ((R - G) + (R - B))
    den = math.sqrt((R - G) ** 2 + (R - B) * (G - B))
    th = math.degrees(math.acos(max(-1, min(1, num / den))))
    H = th if B <= G else 360 - th
    S = 1 - 3 * min(R, G, B) / (R + G + B)
    return dict(R=R, G=G, B=B, num=num, den=den, th=th, H=H, S=S, I=(R + G + B) / 3)


def f4(x):
    return f"{x:.4f}"


def hsi_answer(rgb):
    X = hsi(rgb)
    r, g, b = rgb
    side = f"B = {f4(X['B'])} ≤ G = {f4(X['G'])}, so H = θ" if X["B"] <= X["G"] else f"B = {f4(X['B'])} > G = {f4(X['G'])}, so H = 360° − θ"
    body = (f"<p><b>Step 1 · normalise</b> (divide by 255): R = {r}/255 = {f4(X['R'])}, G = {g}/255 = {f4(X['G'])}, B = {b}/255 = {f4(X['B'])}.</p>"
            f"<p><b>Step 2 · θ</b></p>"
            + formula(f"numerator = ½[(R − G) + (R − B)] = ½[({f4(X['R'] - X['G'])}) + ({f4(X['R'] - X['B'])})] = {f4(X['num'])}<br>"
                      f"denominator = √[(R − G)² + (R − B)(G − B)] = √[{f4((X['R'] - X['G']) ** 2)} + ({f4(X['R'] - X['B'])})({f4(X['G'] - X['B'])})] = {f4(X['den'])}<br>"
                      f"θ = cos⁻¹({f4(X['num'])} / {f4(X['den'])}) = cos⁻¹({f4(X['num'] / X['den'])}) = {X['th']:.2f}°")
            + f"<p><b>Step 3 · hue:</b> {side} = <b>{X['H']:.2f}°</b>.</p>"
            + formula(f"S = 1 − 3·min(R,G,B)/(R + G + B) = 1 − 3 × {f4(min(X['R'], X['G'], X['B']))} / {f4(X['R'] + X['G'] + X['B'])} = {f4(X['S'])}<br>"
                      f"I = (R + G + B)/3 = {f4(X['R'] + X['G'] + X['B'])}/3 = {f4(X['I'])}")
            + ans(f"RGB({r}, {g}, {b}) → H = {X['H']:.2f}°, S = {f4(X['S'])}, I = {f4(X['I'])}"))
    return body, X


# ---------------------------------------------------------------- drawings
def spectrum():
    stops = [(380, "#4b0082"), (440, "#3b3bff"), (490, "#00a6ff"), (520, "#18c018"), (570, "#e6e600"), (600, "#ff9a00"), (650, "#ff2a00"), (750, "#7a0000")]
    W, x = 520, lambda nm: 20 + (nm - 380) / 370 * (W - 40)
    g = "".join(f'<stop offset="{(nm - 380) / 370:.3f}" stop-color="{c}"/>' for nm, c in stops)
    o = [f'<svg viewBox="0 0 {W} 92" width="{W}" role="img" class="plot"><defs><linearGradient id="spec">{g}</linearGradient></defs>',
         f'<rect x="20" y="22" width="{W - 40}" height="30" fill="url(#spec)" rx="3"/>']
    for nm, name in [(410, "violet"), (465, "blue"), (530, "green"), (577, "yellow"), (605, "orange"), (680, "red")]:
        o.append(f'<text x="{x(nm):.0f}" y="16" text-anchor="middle" font-size="11" fill="var(--fg)">{name}</text>')
    for nm in (400, 500, 600, 700):
        o.append(f'<line x1="{x(nm):.0f}" y1="52" x2="{x(nm):.0f}" y2="58" stroke="var(--fg2)"/><text x="{x(nm):.0f}" y="70" text-anchor="middle" font-size="10" fill="var(--fg2)">{nm} nm</text>')
    o.append(f'<text x="20" y="86" font-size="10" fill="var(--fg2)">← ultraviolet</text><text x="{W - 20}" y="86" text-anchor="end" font-size="10" fill="var(--fg2)">infrared →</text></svg>')
    return f'<figure class="fig">{"".join(o)}<figcaption>visible light ≈ 400–700 nm; the six regions blend smoothly (slides 4–6)</figcaption></figure>'


def venn(kind):
    add = kind == "add"
    bg, blend = ("#000", "screen") if add else ("#fff", "multiply")
    cols = [("#ff0000", 80, 70, "Red"), ("#00ff00", 120, 70, "Green"), ("#0000ff", 100, 105, "Blue")] if add else \
           [("#00ffff", 80, 70, "Cyan"), ("#ff00ff", 120, 70, "Magenta"), ("#ffff00", 100, 105, "Yellow")]
    c = "".join(f'<circle cx="{x}" cy="{y}" r="42" fill="{col}" style="mix-blend-mode:{blend}"/>' for col, x, y, _ in cols)
    lab = "".join(f'<text x="{x + (x - 100) * .9}" y="{y + (y - 82) * 1.1 + 4}" text-anchor="middle" font-size="11" font-weight="700" fill="{"#fff" if add else "#222"}">{n}</text>' for _, x, y, n in cols)
    mid = "white" if add else "black"
    cap = "additive (light): R + G + B = white; R + G = yellow, G + B = cyan, B + R = magenta" if add else "subtractive (pigment): C + M + Y = black; C + M = blue, M + Y = red, Y + C = green"
    return (f'<figure class="fig"><svg viewBox="0 0 200 165" width="200" role="img" class="plot"><rect width="200" height="165" rx="6" fill="{bg}"/>'
            f'<g style="isolation:isolate">{c}</g>{lab}<text x="100" y="86" text-anchor="middle" font-size="10" fill="{"#000" if add else "#fff"}">{mid}</text></svg><figcaption>{cap}</figcaption></figure>')


def cube():
    P = lambda x, y, z: (90 + y * 170 - x * 70, 230 - z * 170 + x * 52)
    C = [((0, 0, 0), "#000", "Black (0,0,0)"), ((1, 0, 0), "#f00", "Red (1,0,0)"), ((0, 1, 0), "#0c0", "Green (0,1,0)"), ((0, 0, 1), "#00f", "Blue (0,0,1)"),
         ((1, 1, 0), "#ff0", "Yellow"), ((0, 1, 1), "#0ff", "Cyan"), ((1, 0, 1), "#f0f", "Magenta"), ((1, 1, 1), "#fff", "White (1,1,1)")]
    E = [(0, 1), (0, 2), (0, 3), (1, 4), (1, 6), (2, 4), (2, 5), (3, 5), (3, 6), (4, 7), (5, 7), (6, 7)]
    o = ['<svg viewBox="0 0 330 320" width="330" role="img" class="plot">']
    for a, b in E:
        p, q = P(*C[a][0]), P(*C[b][0])
        o.append(f'<line x1="{p[0]}" y1="{p[1]}" x2="{q[0]}" y2="{q[1]}" stroke="var(--fg2)" stroke-width="1.2"/>')
    k, w = P(0, 0, 0), P(1, 1, 1)
    o.append(f'<line x1="{k[0]}" y1="{k[1]}" x2="{w[0]}" y2="{w[1]}" stroke="var(--mark)" stroke-width="2" stroke-dasharray="6 4"/>')
    g = P(.5, .5, .5)
    o.append(f'<text x="{g[0] + 8}" y="{g[1] + 4}" font-size="11" fill="var(--mark)">gray scale (R = G = B)</text>')
    for ax, (x, y, z) in (("R", (1.35, 0, 0)), ("G", (0, 1.25, 0)), ("B", (0, 0, 1.22))):
        p = P(x, y, z)
        o.append(f'<line x1="{k[0]}" y1="{k[1]}" x2="{p[0]}" y2="{p[1]}" stroke="var(--fg)" stroke-width="1.2"/><text x="{p[0] + 4}" y="{p[1] + 4}" font-size="13" font-weight="700" fill="var(--fg)">{ax}</text>')
    for (x, y, z), col, name in C:
        p = P(x, y, z)
        dx = 9 if y else -9
        o.append(f'<circle cx="{p[0]}" cy="{p[1]}" r="6.5" fill="{col}" stroke="var(--fg)"/><text x="{p[0] + dx}" y="{p[1] + (-9 if z else 16)}" text-anchor="{"start" if y else "end"}" font-size="11" fill="var(--fg)">{name}</text>')
    o.append("</svg>")
    return f'<figure class="fig">{"".join(o)}<figcaption>RGB colour cube (slide 14), values normalised to [0, 1]; for 8-bit images multiply by 255</figcaption></figure>'


def hexagon():
    c, R = 130, 90
    pt = lambda d, r=R: (c + r * math.cos(math.radians(d)), c - r * math.sin(math.radians(d)))
    V = [(0, "Red", "#f00"), (60, "Yellow", "#ff0"), (120, "Green", "#0c0"), (180, "Cyan", "#0ff"), (240, "Blue", "#00f"), (300, "Magenta", "#f0f")]
    o = ['<svg viewBox="0 0 260 260" width="260" role="img" class="plot">',
         f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(d) for d, _, _ in V))}" fill="none" stroke="var(--fg2)"/>',
         f'<line x1="{c}" y1="{c}" x2="{c + R}" y2="{c}" stroke="var(--fg2)" stroke-dasharray="3 3"/>']
    for d, n, col in V:
        x, y = pt(d)
        lx, ly = pt(d, R + 22)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{col}" stroke="var(--fg)"/><text x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="middle" font-size="11" fill="var(--fg)">{n} {d}°</text>')
    H, S = 50, .7
    e = pt(H, R * S)
    a = pt(H, 30)
    o.append(f'<path d="M {c + 30} {c} A 30 30 0 0 0 {a[0]:.1f} {a[1]:.1f}" fill="none" stroke="var(--mark)" stroke-width="2"/>'
             f'<line x1="{c}" y1="{c}" x2="{e[0]:.1f}" y2="{e[1]:.1f}" stroke="var(--mark)" stroke-width="2.5"/><circle cx="{e[0]:.1f}" cy="{e[1]:.1f}" r="5" fill="var(--mark)"/>'
             f'<text x="{c + 34}" y="{c - 10}" font-size="12" fill="var(--mark)">H</text><text x="{(c + e[0]) / 2 - 12:.1f}" y="{(c + e[1]) / 2 - 2:.1f}" font-size="12" fill="var(--mark)">S</text>'
             f'<circle cx="{c}" cy="{c}" r="3.5" fill="var(--fg)"/><text x="{c - 6}" y="{c + 16}" font-size="10" text-anchor="end" fill="var(--fg2)">white/gray axis (I)</text></svg>')
    return f'<figure class="fig">{"".join(o)}<figcaption>looking down the gray axis of the RGB cube: primaries 120° apart, secondaries 60° from them (slides 24–25)</figcaption></figure>'


def csim(cap, rgb, parts, dp=4):
    return sim({"type": "color", "rgb": list(rgb), "parts": parts, "dp": dp}, cap)


ADD_SUB = tbl(["", "additive (RGB)", "subtractive (CMY/CMYK)"], [
    ["works with", "<b>light</b> (emitted)", "<b>pigments / inks</b> (reflected)"],
    ["primaries", "red, green, blue", "cyan, magenta, yellow"],
    ["start from", "black (no light), then add light", "white paper, then inks absorb (subtract) light"],
    ["all three together", "<b>white</b>", "<b>black</b> (in practice dark brown, so K is added)"],
    ["secondaries", "R+G = yellow, G+B = cyan, B+R = magenta", "C+M = blue, M+Y = red, Y+C = green"],
    ["used in", "monitors, TVs, cameras, projectors", "printers, presses, packaging"]])

S = []

# ================================================================ 1. fundamentals
S.append(sec("start", "Colour fundamentals in two minutes", "3–8", SHORT, f"""
{idea("Colour is just which wavelengths of light reach your eye. Your eye has three kinds of colour sensors (cones), roughly for red, green and blue, so every colour can be described with three numbers. That is why colour images store three values per pixel.")}
<p><b>Slide 3.</b> Colour image processing is about how mathematical models represent and manipulate colour. The key ideas are the <b>physics of light</b>, <b>human vision</b> and <b>colour models</b>, each serving different applications.</p>
<p><b>Slides 4–6.</b> In 1666 Newton passed sunlight through a prism and got a continuous spectrum of six regions: <b>violet, blue, green, yellow, orange, red</b>. No colour ends abruptly; each blends into the next. Visible light is a narrow band of the electromagnetic spectrum, about <b>400–700 nm</b>.</p>
{figs(spectrum())}
<p><b>Slide 6.</b> The eye has three types of cones, sensitive to red, green and blue. About 6–7 million cones per eye: roughly <b>65% red-sensitive, 33% green, 2% blue</b> (the blue cones are the most sensitive). This <b>trichromatic</b> system is the basis of most digital colour models.</p>
<p><b>Slide 7.</b> Colour perception depends on the wavelength composition. CIE (1931) primaries: <b>red = 700 nm, green = 546.1 nm, blue = 435.8 nm</b>. Attributes of colour:</p>
{tbl(["attribute", "meaning"], [["<b>hue</b>", "the dominant wavelength: which colour it is (red, green…)"], ["<b>saturation</b>", "purity: how much it is diluted with white (high = vivid)"], ["<b>brightness / intensity</b>", "the amount of light energy perceived"]])}
<p><b>Slide 8. Colour vision.</b> We see the colour of an object by the light it <b>reflects</b>. White light holds all wavelengths; a red object reflects red and absorbs the rest.</p>
"""))

# ================================================================ 2. additive / subtractive
S.append(sec("mix", "Additive vs subtractive colour", "9–11", EXAM, f"""
{idea("Screens make colour by <b>adding</b> light onto black: more light, brighter, until R + G + B = white. Printers make colour by <b>removing</b> light from white paper: each ink soaks up one colour, until C + M + Y absorbs everything = black.")}
{figs(venn("add"), venn("sub"))}
<p><b>Slide 9. Colour addition (mixtures of light):</b> primary colours of light (red, green, blue) are <b>additive</b>; red + green + blue gives white.</p>
<p><b>Slide 10. Colour subtraction (mixtures of pigments):</b> primary colours of pigment (cyan, magenta, yellow) are <b>subtractive</b>; cyan + magenta + yellow gives black. When white light shines on a surface, the pigment absorbs some wavelengths and we see what is not absorbed:</p>
{tbl(["pigment", "absorbs", "reflects", "so it equals"], [["cyan", "red", "green + blue", "white − red"], ["magenta", "green", "red + blue", "white − green"], ["yellow", "blue", "red + green", "white − blue"]])}
<p><b>Slide 11. Primary and secondary colours:</b></p>
{ADD_SUB}
{paper("SP22 Final Q7(b)(i)", "4 marks", f'''<p class="q">Why is RGB called “additive” whereas CMYK is “subtractive”?</p>
<p>RGB builds a colour by <b>adding light</b> of the three primaries on a black (no light) background, as a monitor does: each primary adds energy, and R + G + B at full strength gives <b>white</b>. CMY(K) builds a colour with <b>pigments</b> on white paper: each ink <b>absorbs (subtracts)</b> one primary from the white light, e.g. cyan = white − red, magenta = white − green, yellow = white − blue. Adding more ink removes more light, so C + M + Y gives <b>black</b> (in practice dark brown, so black ink K is added for depth and contrast).</p>
{ans("RGB adds light (all three = white); CMY(K) subtracts light from white (all three = black).")}''')}
"""))

# ================================================================ 3. models table
S.append(sec("models", "Major colour models and when to use which", "12", EXAM, f"""
{idea("A colour model is just a coordinate system for colours. Pick the one that matches the job: light devices use RGB, ink uses CMYK, and when you want to talk about colour the way people do (\"which hue?\", \"how vivid?\") use HSI.")}
{tbl(["model", "type", "components", "applications"], [
    ["<b>RGB</b>", "additive", "3 channels", "displays, cameras, image editing"],
    ["<b>CMY / CMYK</b>", "subtractive", "4 channels (with K)", "printing, publishing"],
    ["<b>HSV / HSI</b>", "perceptual", "cylindrical coordinates", "image segmentation, computer vision"],
    ["YIQ / YUV", "luminance + chrominance", "Y = brightness, I/Q or U/V = colour", "television, video compression"],
    ["CIELAB", "perceptually uniform", "L* (lightness), a*, b* (colour axes)", "colour correction, medical / satellite imaging"]])}
{paper("SP24 Final Q1(d)", "2 + 3 marks", '''<p class="q">Which colour model (RGB, CMY, CMYK, HSI) is appropriate for (i) colour printing, (ii) computer displaying? Explain.</p>
<p><b>(i) Colour printing: CMYK.</b> A printer puts inks on white paper. Inks work by absorbing light, so a subtractive model is needed: cyan, magenta and yellow each remove one primary. Mixing C + M + Y gives only a muddy dark brown, so a separate black (K) ink is added for true black, better contrast and less ink use.</p>
<p><b>(ii) Computer display: RGB.</b> A monitor emits light. Each pixel has red, green and blue sub-pixels whose light adds up (additive model): (255, 0, 0) is red, (255, 255, 255) is white, (0, 0, 0) is black. RGB also matches the eye's three cone types.</p>''')}
{paper("SP25 Final Q1(c)", "4 marks", f'''<p class="q">Define a colour image. What is the difference between additive and subtractive colour mixing? What is the purpose of colour models in image processing? Which model is appropriate for colour printing and for segmentation?</p>
<p><b>Colour image:</b> an image whose every pixel holds a colour vector, usually three components (R, G, B), each 8 bits, i.e. 24 bits per pixel.</p>
<p><b>Additive vs subtractive:</b> additive mixing adds <b>light</b> (R, G, B; all three = white; screens). Subtractive mixing uses <b>pigments</b> that absorb light (C, M, Y; all three = black; printing).</p>
<p><b>Purpose of colour models:</b> to specify colours in a standard way, as points in a coordinate system, so that hardware (RGB for displays, CMYK for printers) and processing (HSI for describing and analysing colour) can use them.</p>
<p><b>Printing:</b> CMY/CMYK. <b>Segmentation:</b> HSI/HSV, because hue is kept apart from intensity, so an object can be picked out by its hue even when lighting changes.</p>''')}
"""))

# ================================================================ 4. RGB
S.append(sec("rgb", "RGB model and the colour cube", "13–17", EXAM, f"""
{idea("Think of a box. One corner is black (no light). Walk along one edge and red light turns on; along another, green; up, blue. Every colour is one point inside the box, given by how much R, G and B it has. The corner opposite black is white, and the straight line from black to white is every shade of gray.")}
<p><b>Slide 13.</b> RGB: type <b>additive</b>; primary components red, green, blue; colours are formed by combining light of the three primaries; each channel ranges <b>0–255</b> in 8-bit images.</p>
{figs(cube())}
<p><b>Slide 14. The RGB model is based on a Cartesian coordinate system:</b></p>
<ul>
<li>R, G, B are at three corners of the cube: (1,0,0), (0,1,0), (0,0,1).</li>
<li>Cyan, magenta and yellow are at three other corners.</li>
<li><b>Black is at the origin</b>; <b>white is the corner furthest from the origin</b>.</li>
<li>Different colours are points on or inside the cube, represented by <b>RGB vectors</b>.</li>
</ul>
<p><b>Slide 15. How it works.</b> Additive mixing: R + G = yellow, G + B = cyan, B + R = magenta, R + G + B = white, no light = black. Each pixel is defined by three values (R, G, B): (255,0,0) pure red, (0,255,0) pure green, (0,0,255) pure blue, (255,255,0) yellow, (0,255,255) cyan, (255,0,255) magenta, (255,255,255) white, (0,0,0) black.</p>
{formula("total colours in a 24-bit RGB image = (2<sup>8</sup>)<sup>3</sup> = 2<sup>24</sup> = <b>16,777,216</b>")}
<p><b>Slide 16. How grayscale is formed:</b> equal intensity in all three channels gives gray: dark gray (50,50,50), medium (128,128,128), light (200,200,200), white (255,255,255), black (0,0,0). These points form the <b>gray axis</b>, the diagonal from black to white.</p>
<p><b>Slide 17.</b> Applications: displays (monitors, TVs, projectors), cameras (sensors capture R, G, B), image processing (editing and enhancement start in RGB before conversion to HSV, CIELAB…). Limitations: <b>device dependence</b> (colours look different on different screens), <b>not perceptually uniform</b> (equal number changes ≠ equal visible changes), <b>printing issues</b> (printers use CMYK, so RGB must be converted).</p>
{csim("move the colour around the cube: type any R, G, B and watch where it sits.", (255, 255, 0), ["cmy"])}
{paper("SP23 Final Q3(d)", "3 + 3 + 2 marks", '''<p class="q">(i) Draw the schematic of the RGB colour cube (Cartesian). (ii) How are colours and gray scale formed in RGB? (iii) How many colours in a standard RGB image?</p>
<p><b>(i)</b> Draw the cube above: axes R, G, B from the origin; black at (0,0,0); red (1,0,0), green (0,1,0), blue (0,0,1); yellow (1,1,0), cyan (0,1,1), magenta (1,0,1); white (1,1,1); dashed gray-scale diagonal.</p>
<p><b>(ii)</b> Every colour is a point (R, G, B) on or inside the cube: the three primaries of light are added in those amounts (e.g. (1,1,0) = red + green = yellow). When R = G = B the point lies on the diagonal from black to white, so equal amounts of the three give a <b>shade of gray</b>; (0.5, 0.5, 0.5) is mid-gray.</p>
<p><b>(iii)</b> 8 bits per channel × 3 channels = 24 bits per pixel, so (2<sup>8</sup>)<sup>3</sup> = 2<sup>24</sup> = <b>16,777,216</b> colours.</p>''')}
{paper("F23 Final Q1(c) · SP22 Q7(a) · F22 B4(c)", "4 · 5 · 1 + 4 marks", '''<p class="q">Draw the RGB colour cube using the Cartesian coordinate system. How are different colours and gray scales formed in the RGB colour model? (SP22: describe the RGB model with a schematic of the cube.)</p>
<p>Same answer as SP23 (i) and (ii). For the 5-mark SP22 version add: RGB is <b>additive</b>; primaries red, green, blue; each channel 0–255 in an 8-bit image; used in monitors, cameras and image editing; 24-bit RGB gives 16,777,216 colours. (F22 Section B is from another examiner's paper.)</p>''')}
"""))

# ================================================================ 5. CMY / CMYK
s20 = cmy((98, 35, 146))
S.append(sec("cmy", "CMY and CMYK", "18–22", LIKELY, f"""
{idea("Cyan ink is \"white minus red\". So the amount of cyan you need is just how much red is missing: C = 1 − R. Same for the other two. That is the whole conversion.")}
<p><b>Slide 18.</b> CMY: <b>subtractive</b>; primaries cyan, magenta, yellow; colours are formed by overlapping transparent inks that absorb certain wavelengths. Used in printing presses, magazines, packaging and any physical media.</p>
<p><b>Slide 19. How colours are formed:</b> cyan + magenta = blue; magenta + yellow = red; yellow + cyan = green; cyan + magenta + yellow = dark brown/black (not perfect), so <b>black (K)</b> is added in the CMYK model to improve depth and contrast and to reduce ink usage.</p>
{formula("[C M Y]<sup>T</sup> = [1 1 1]<sup>T</sup> − [R G B]<sup>T</sup> &nbsp;&nbsp; (R, G, B normalised to [0, 1] first)")}
{paper("Slide 20 · worked example", "worked", f'''<p class="q">Convert RGB (98, 35, 146) to CMY.</p>
<p><b>Step 1 · normalise:</b> R = 98/255 = 0.384, G = 35/255 = 0.137, B = 146/255 = 0.573.</p>
<p><b>Step 2 · subtract from 1:</b> C = 1 − 0.384 = <b>0.616</b>, M = 1 − 0.137 = <b>0.863</b>, Y = 1 − 0.573 = <b>0.427</b>.</p>
{ans(f"CMY = ({s20[0]:.3f}, {s20[1]:.3f}, {s20[2]:.3f}); in 8-bit form (255 − R, 255 − G, 255 − B) = (157, 220, 109)")}''')}
{trap("Slide 20 prints B = 0.572 and Y = 0.428. 146/255 = 0.5725…, which rounds to 0.573, so Y = 0.427. Either is accepted if you show the working; just keep the same decimals all the way.")}
{csim("RGB → CMY, one channel at a time (slide 20's numbers loaded; change them freely).", (98, 35, 146), ["cmy"], 3)}
<p><b>Slide 20. Applications:</b> printing industry (offset and digital), graphic design (designers convert RGB screen colours to CMYK for accurate print), packaging and branding (consistent colour on physical products).</p>
<p><b>Slide 21. Challenges:</b> <b>colour shift</b> (screen RGB looks different printed), <b>ink absorption</b> (paper type changes how inks mix), <b>limited gamut</b> (CMYK cannot reproduce all RGB colours, especially bright neon tones). Key insight: RGB is for light-based devices, CMYK for ink-based printing; convert RGB files to CMYK before printing.</p>
<p><b>Slide 22. Key conversions:</b> RGB ↔ CMYK for digital-to-print workflows; RGB ↔ HSV for isolating hue in object detection; CIELAB ↔ RGB for perceptual uniformity in colour correction.</p>
"""))

# ================================================================ 6. HSI
hpA, hX = hsi_answer((200, 100, 50))
hpB, hY = hsi_answer((98, 35, 146))
S.append(sec("hsi", "HSI model and RGB → HSI", "23–30", EXAM, f"""
{idea("RGB is how machines <i>make</i> colour; HSI is how people <i>describe</i> it. Hue = which colour (an angle round a colour wheel, red at 0°). Saturation = how vivid (0 = gray, 1 = pure). Intensity = how bright (0 = black, 1 = white). Because brightness is kept separate, HSI is great for picking objects by colour.")}
<p><b>Slide 23.</b> RGB is useful for hardware and fits how the eye senses colour; <b>RGB is great for colour generation, HSI is great for colour description</b>. HSI uses three measures:</p>
{tbl(["component", "meaning", "range"], [["<b>Hue (H)</b>", "the pure colour (pure yellow, orange or red), an angle from red", "0°–360°"], ["<b>Saturation (S)</b>", "how much the pure colour is diluted with white", "0–1"], ["<b>Intensity (I)</b>", "achromatic brightness, as in a gray-level image", "0 (black) – 1 (white)"]])}
{figs(hexagon())}
<p><b>Slides 24–25.</b> Look straight down the RGB cube along its gray diagonal and you see a <b>hexagon</b>: each primary is 120° apart (<b>red 0°, green 120°, blue 240°</b>); the secondaries sit 60° from the primaries (yellow 60°, cyan 180°, magenta 300°). The HSI space has a vertical <b>intensity axis</b>; colour points lie on planes perpendicular to it. At an arbitrary colour point: the <b>hue</b> is the angle from a reference point (red); the <b>saturation</b> is the distance from the axis (origin) to the point; the <b>intensity</b> is how far up the axis the plane sits. The plane is often drawn as a circle or a triangle (slides 25–28: slices at I = 0.75 and I = 0.5 of a double cone from black to white).</p>
<h3>Conversion from RGB to HSI (slide 29)</h3>
{formula("Normalise R, G, B to [0, 1] first.<br>θ = cos⁻¹ { ½[(R − G) + (R − B)] / [(R − G)² + (R − B)(G − B)]<sup>½</sup> }<br>H = θ if B ≤ G; &nbsp; H = 360° − θ if B &gt; G<br>S = 1 − 3·min(R, G, B) / (R + G + B)<br>I = (R + G + B) / 3")}
{paper("Worked · RGB(200, 100, 50) → HSI", "worked", hpA)}
{csim("RGB → HSI, one quantity at a time (θ top, θ bottom, θ, H, S, I).", (200, 100, 50), ["hsi"])}
{paper("Worked · slide 20 colour RGB(98, 35, 146) → HSI", "practice", hpB + "<p>Here B &gt; G, so the hue is measured the long way round: 360° − θ. That puts it between blue (240°) and magenta (300°), which matches a purple colour.</p>")}
{trap("Use the <b>normalised</b> values (÷255) everywhere, including θ. Check B against G before writing H. A gray (R = G = B) has no hue (the bottom of θ is 0) and S = 0.")}
<h3>Conversion from HSI to RGB (slide 30, glance)</h3>
{tbl(["sector", "formulas"], [
    ["RG: 0° ≤ H &lt; 120°", "B = I(1 − S); &nbsp;R = I[1 + S cos H / cos(60° − H)]; &nbsp;G = 3I − (R + B)"],
    ["GB: 120° ≤ H &lt; 240°", "H = H − 120°; &nbsp;R = I(1 − S); &nbsp;G = I[1 + S cos H / cos(60° − H)]; &nbsp;B = 3I − (R + G)"],
    ["BR: 240° ≤ H &lt; 360°", "H = H − 240°; &nbsp;G = I(1 − S); &nbsp;B = I[1 + S cos H / cos(60° − H)]; &nbsp;R = 3I − (G + B)"]])}
{trap("Slide 30 writes the last line as G = 1 − (R + B). That only holds for chromaticity values that add to 1. With I = (R + G + B)/3 the correct line is G = 3I − (R + B) (Gonzalez &amp; Woods). Check: for RGB(200,100,50) it gives back G = 0.392.")}
{paper("F22 Final B5(c) (another examiner's paper)", "3 + 2 + 3 marks", '''<p class="q">Explain the HSI colour model with an example. Differences between additive and subtractive colour? How does the combination of cyan, magenta and yellow pigments create different colours?</p>
<p><b>HSI:</b> describes colour as Hue (angle from red: red 0°, green 120°, blue 240°), Saturation (purity, 0–1) and Intensity (brightness, 0–1). Example: RGB(200, 100, 50) gives H ≈ 19.1° (an orange-red), S ≈ 0.57, I ≈ 0.46.</p>
<p><b>Additive vs subtractive:</b> see the table in the additive/subtractive section (light vs pigment; all three = white vs black; screens vs printers).</p>
<p><b>CMY combinations:</b> each pigment removes one primary from white light: cyan + magenta removes red and green, leaving <b>blue</b>; magenta + yellow leaves <b>red</b>; yellow + cyan leaves <b>green</b>; all three remove everything: <b>black</b>.</p>''')}
"""))

# ================================================================ 7. other theory questions
S.append(sec("other", "Other colour theory questions", "—", SHORT, f"""
{paper("SP22 Final Q7(b)(ii)", "4 marks", '''<p class="q">Basic differences between an RGB image and an indexed colour image? Which is preferred for storage and transmission?</p>
<p>(Not on the Fall 2025 slides; a short answer is enough.)</p>
<p><b>RGB (true-colour) image:</b> every pixel stores its own three values R, G, B, usually 24 bits per pixel, so it can show any of 16.7 million colours.</p>
<p><b>Indexed image:</b> every pixel stores only an <b>index</b> (e.g. 8 bits) into a small <b>colour map (palette)</b> that lists the actual RGB colours, e.g. 256 entries.</p>
<p><b>Storage/transmission:</b> the indexed image is preferred: about 8 bits/pixel plus a small table instead of 24 bits/pixel (GIF uses this). The cost is a limited number of colours.</p>''')}
{paper("F21 Final A3(a) (another examiner's paper)", "8 marks", '''<p class="q">Inkjet printer and computer: describe the colour model used in a monitor and in a printer. Among red, green and blue, which appears brightest, followed by the others? Justify. Discuss the two major areas of colour image processing.</p>
<p><b>Monitor: RGB</b> (additive, emits light). <b>Printer: CMYK</b> (subtractive inks on white paper, K added for true black).</p>
<p><b>Brightest:</b> <b>green</b>, then <b>red</b>, then <b>blue</b>. The eye's overall brightness sensitivity peaks near 555 nm (green), where the red- and green-sensitive cones overlap; very few cones (about 2%) respond to blue, so equal-energy blue looks darkest. (The luminance formula agrees: Y = 0.299R + 0.587G + 0.114B.)</p>
<p><b>Two major areas</b> (Gonzalez, chapter 6): <b>full-colour processing</b> (images from a full-colour sensor, e.g. a colour camera; process the colour vectors) and <b>pseudo-colour processing</b> (assign colours to gray levels or ranges of intensity to make features easier to see).</p>''')}
"""))

# ================================================================ 8. traps
S.append(sec("traps", "Traps and one-minute sheet", "all", None, f"""
<ul class="traps">
<li>Additive = light, R + G + B = <b>white</b>. Subtractive = pigment, C + M + Y = <b>black</b>. Do not swap the secondaries: light R + G = yellow; pigment M + Y = red.</li>
<li>In the cube, black is the origin, white the far corner, gray the diagonal (R = G = B).</li>
<li>Colours in 24-bit RGB: 2<sup>24</sup> = 16,777,216.</li>
<li>Always normalise (÷255) before CMY or HSI formulas.</li>
<li>H = θ when B ≤ G, otherwise 360° − θ. Red 0°, green 120°, blue 240°.</li>
<li>Printing → CMYK; displays → RGB; segmentation / describing colour → HSI.</li>
</ul>
{tbl(["what", "formula"], [["RGB → CMY", "C = 1 − R, M = 1 − G, Y = 1 − B"], ["θ", "cos⁻¹{½[(R−G)+(R−B)] / √[(R−G)² + (R−B)(G−B)]}"], ["H", "θ if B ≤ G, else 360° − θ"], ["S", "1 − 3·min(R,G,B)/(R+G+B)"], ["I", "(R+G+B)/3"]])}
"""))

toc = [("start", "Start"), ("mix", "Additive vs subtractive"), ("models", "Which model"), ("rgb", "RGB cube"), ("cmy", "CMY/CMYK"), ("hsi", "HSI"), ("other", "Other questions"), ("traps", "Traps")]
OUT.write_text(page("DIP Deck 14 Lesson", "CSE 4227 · Chapter 6 · Deck 14", "Colour image processing: RGB, CMY(K), HSI",
                    "Every colour model in plain words, the RGB cube drawn properly, step-by-step RGB → CMY and RGB → HSI simulators, and each past theory question answered the way you would write it. Fall 2024 questions are left out.",
                    toc, S, extra=sim_assets()), encoding="utf-8")

# ---------------------------------------------------------------- self-check (data/answers.json COL/cmy, COL/hsi)
assert [round(v, 3) for v in s20] == [0.616, 0.863, 0.427]
assert round(hX["th"], 2) == 19.11 and round(hX["H"], 2) == 19.11 and round(hX["S"], 4) == 0.5714 and round(hX["I"], 4) == 0.4575
# HSI -> RGB with the Gonzalez line gives the colour back
I_, S_, H_ = hX["I"], hX["S"], math.radians(hX["H"])
Bk = I_ * (1 - S_); Rk = I_ * (1 + S_ * math.cos(H_) / math.cos(math.radians(60) - H_)); Gk = 3 * I_ - (Rk + Bk)
assert abs(Rk - 200 / 255) < 1e-9 and abs(Gk - 100 / 255) < 1e-9 and abs(Bk - 50 / 255) < 1e-9
print(OUT, OUT.stat().st_size, "slide-20 HSI", round(hY["H"], 2), round(hY["S"], 4), round(hY["I"], 4))
