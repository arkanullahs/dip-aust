"""Builds deck03_lesson.html: pixel relationships (neighbours, adjacency, paths, components, distances). Fall 2024 questions left out on purpose."""
import sys, pathlib, math
from collections import deque
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from kit import *

OUT = pathlib.Path(__file__).with_name("deck03_lesson.html")


# ---------------------------------------------------------------- same rules as scripts/solvers.py find_path / components
def find_path(img, V, p, q, kind):
    H, W = len(img), len(img[0])
    inV = lambda a: 0 <= a[0] < H and 0 <= a[1] < W and img[a[0]][a[1]] in V
    N4 = lambda a: [(a[0] + d[0], a[1] + d[1]) for d in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    ND = lambda a: [(a[0] + d[0], a[1] + d[1]) for d in ((1, 1), (1, -1), (-1, 1), (-1, -1))]

    def nbrs(a):
        out = [b for b in N4(a) if inV(b)]
        if kind == 8:
            out += [b for b in ND(a) if inV(b)]
        if kind == "m":
            out += [b for b in ND(a) if inV(b) and not any(inV(x) for x in set(N4(a)) & set(N4(b)))]
        return out
    if not (inV(p) and inV(q)):
        return None
    prev, dq = {p: None}, deque([p])
    while dq:
        a = dq.popleft()
        if a == q:
            path = []
            while a is not None:
                path.append(a); a = prev[a]
            return path[::-1]
        for b in nbrs(a):
            if b not in prev:
                prev[b] = a; dq.append(b)
    return None


def components(img, V, kind):
    H, W = len(img), len(img[0])
    seen, comps = set(), []
    for r in range(H):
        for c in range(W):
            if img[r][c] in V and (r, c) not in seen:
                comp, st = [], [(r, c)]
                seen.add((r, c))
                while st:
                    a = st.pop(); comp.append(a)
                    for b in [(a[0] + i, a[1] + j) for i in (-1, 0, 1) for j in (-1, 0, 1) if (i, j) != (0, 0)]:
                        if not (0 <= b[0] < H and 0 <= b[1] < W) or b in seen or img[b[0]][b[1]] not in V:
                            continue
                        diag = a[0] != b[0] and a[1] != b[1]
                        if kind == 4 and diag:
                            continue
                        if kind == "m" and diag and any(img[x][y] in V for x, y in ((a[0], b[1]), (b[0], a[1]))):
                            continue
                        seen.add(b); st.append(b)
                comps.append(sorted(comp))
    return comps


def d4(p, q): return abs(p[0] - q[0]) + abs(p[1] - q[1])
def d8(p, q): return max(abs(p[0] - q[0]), abs(p[1] - q[1]))
def de(p, q): return math.hypot(p[0] - q[0], p[1] - q[1])


def dist_lines(p, q, lp="p", lq="q"):
    return formula(f"D<sub>4</sub>({lp},{lq}) = |{p[0]} − {q[0]}| + |{p[1]} − {q[1]}| = <b>{d4(p, q)}</b> (city block)<br>"
                   f"D<sub>8</sub>({lp},{lq}) = max(|{p[0]} − {q[0]}|, |{p[1]} − {q[1]}|) = max({abs(p[0] - q[0])}, {abs(p[1] - q[1])}) = <b>{d8(p, q)}</b> (chessboard)<br>"
                   f"D<sub>e</sub>({lp},{lq}) = √[({p[0]} − {q[0]})² + ({p[1]} − {q[1]})²] = √{(p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2} = <b>{de(p, q):.4f}</b> (Euclidean)")


def nb(img, p, kind, base=0):
    """neighbours inside the image, labelled in the question's own numbering (base 0 or 1)"""
    offs = {"4": [(-1, 0), (1, 0), (0, -1), (0, 1)], "D": [(-1, -1), (-1, 1), (1, -1), (1, 1)]}
    offs["8"] = offs["4"] + offs["D"]
    H, W = len(img), len(img[0])
    out = []
    for dr, dc in offs[kind]:
        r, c = p[0] + dr, p[1] + dc
        if 0 <= r < H and 0 <= c < W:
            out.append(f"({r + base},{c + base}) = {img[r][c]}")
    return "{" + ", ".join(out) + "}"


def ptxt(path, img, base=0):
    return " → ".join(f"({r + base},{c + base})={img[r][c]}" for r, c in path)


def psim(cap, img, V, p, q, kinds=("4", "8", "m"), kind=None):
    return sim({"type": "path", "img": img, "V": list(V), "p": list(p), "q": list(q), "kinds": list(kinds), "kind": kind or kinds[0]}, cap)


def rings(kind):
    n, c = 7, 3
    f = d4 if kind == 4 else d8
    M = [[f((r, cc), (c, c)) for cc in range(n)] for r in range(n)]
    return mat(M, f"D<sub>{kind}</sub> from the centre: ≤ 2 forms a {'diamond' if kind == 4 else 'square'}", hi={(r, cc) for r in range(n) for cc in range(n) if M[r][cc] <= 2}, ctr=(c, c), small=True)


S = []

# ================================================================ 1. indexing and neighbours
P11 = [[49, 47, 48, 45, 46, 43, 42], [47, 41, 43, 44, 45, 49, 48], [48, 47, 49, 45, 50, 43, 49], [49, 49, 49, 49, 49, 50, 50],
       [48, 48, 48, 48, 48, 49, 50], [48, 48, 49, 50, 50, 50, 49], [49, 50, 50, 51, 51, 50, 50]]
def one(r, c): return (r - 1, c - 1)
S.append(sec("nbr", "Indexing and neighbours", "4–11", EXAM, f"""
{idea("Every pixel has 8 pixels touching it. The 4 that share a side (up, down, left, right) are its 4-neighbours N<sub>4</sub>. The 4 that touch only at a corner are the diagonal neighbours N<sub>D</sub>. All 8 together are N<sub>8</sub>.")}
<p><b>Slide 4. Conventional indexing:</b> the origin (0,0) is the <b>top-left</b> pixel; <b>x runs down the rows</b>, <b>y runs across the columns</b>. So p(x,y) means row x, column y. Around p:</p>
{mat([["(x−1, y−1)", "(x−1, y)", "(x−1, y+1)"], ["(x, y−1)", "<b>p (x, y)</b>", "(x, y+1)"], ["(x+1, y−1)", "(x+1, y)", "(x+1, y+1)"]], "the 3×3 neighbourhood of p", ctr=(1, 1))}
{tbl(["set", "pixels", "distance from p"], [["<b>N<sub>4</sub>(p)</b> (4-neighbours)", "(x+1, y), (x−1, y), (x, y+1), (x, y−1): vertical and horizontal", "1 (unit distance)"],
     ["<b>N<sub>D</sub>(p)</b> (diagonal)", "(x+1, y+1), (x+1, y−1), (x−1, y+1), (x−1, y−1)", "√2 = 1.414 (Euclidean)"], ["<b>N<sub>8</sub>(p)</b>", "N<sub>4</sub>(p) ∪ N<sub>D</sub>(p): all eight", "1 or 1.414"]])}
<p>The relation is symmetric: q ∈ N<sub>4</sub>(p) implies p ∈ N<sub>4</sub>(q) (same for N<sub>D</sub>, N<sub>8</sub>).</p>
<p><b>Slide 10. Missing neighbours:</b> when p lies on the image border some neighbours fall outside. Handle them by <b>discarding</b> them, <b>zero padding</b> or <b>pixel replication</b>.</p>
{paper("Slide 11 · practice", "worked", f'''<p class="q">For the 7×7 image (rows and columns numbered from 1, as on the slide) find N<sub>4</sub>(3,4), N<sub>D</sub>(3,4), N<sub>8</sub>(3,4), N<sub>4</sub>(1,1), N<sub>4</sub>(4,1), N<sub>8</sub>(7,7).</p>
{mat(P11, "rows/columns 1–7; (3,4) = 45 outlined", ctr=(2, 3))}
<ul>
<li>N<sub>4</sub>(3,4) = {nb(P11, one(3, 4), "4", 1)}</li>
<li>N<sub>D</sub>(3,4) = {nb(P11, one(3, 4), "D", 1)}</li>
<li>N<sub>8</sub>(3,4) = {nb(P11, one(3, 4), "8", 1)}</li>
<li>N<sub>4</sub>(1,1) = {nb(P11, one(1, 1), "4", 1)}: a corner, only 2 neighbours inside</li>
<li>N<sub>4</sub>(4,1) = {nb(P11, one(4, 1), "4", 1)}: on the left border, 3 inside</li>
<li>N<sub>8</sub>(7,7) = {nb(P11, one(7, 7), "8", 1)}: a corner, 3 inside</li>
</ul>''')}
"""))

# ================================================================ 2. adjacency
Q21 = [[4, 2, 3, 2], [3, 3, 1, 3], [2, 3, 5, 2], [2, 1, 2, 5]]
Q22 = [[4, 2, 3, 2], [3, 3, 1, 3], [2, 3, 5, 4], [2, 1, 6, 0]]
S.append(sec("adj", "Adjacency: 4, 8 and m", "12–17, 21–22", EXAM, f"""
{idea("\"Adjacent\" needs two things: the pixels must be <b>neighbours</b>, and <b>both values must be in the set V</b> (the values we care about, e.g. V = {{1}} in a binary image). m-adjacency is 8-adjacency with one extra rule that stops double connections.")}
<p><b>Slides 12–13.</b> Adjacency depends on both the neighbourhood and the gray values. Two pixels are connected if they are neighbours and their gray levels satisfy a similarity criterion. In a binary image V = {{1}}; in a gray image V can be any subset of the 256 values.</p>
{tbl(["type", "p and q (values in V) are adjacent if…"], [["<b>4-adjacency</b>", "q ∈ N<sub>4</sub>(p)"], ["<b>8-adjacency</b>", "q ∈ N<sub>8</sub>(p)"],
     ["<b>m-adjacency</b> (mixed)", "(i) q ∈ N<sub>4</sub>(p), <b>or</b> (ii) q ∈ N<sub>D</sub>(p) <b>and</b> N<sub>4</sub>(p) ∩ N<sub>4</sub>(q) has no pixel whose value is in V"]])}
{idea("Why m? With 8-adjacency a diagonal pair and a corner pixel can both link p to q, giving two different paths (ambiguity). The m rule says: if you can already go round through a shared 4-neighbour, the diagonal shortcut does not count. So every connection is unique.")}
{paper("Slide 21 · 4- and 8-adjacency", "worked", f'''<p class="q">V = {{0, 1, 2, 3, 5}}. A = (0,0), B = (0,1), E = (1,1), C = (2,2), D = (3,3). Which pairs are 4-adjacent / 8-adjacent?</p>
{mat(Q21, "A=4 at (0,0), B=2, E=3, C=5, D=5")}
{tbl(["pair", "neighbours?", "values in V?", "4-adjacent", "8-adjacent"], [
    ["A, B", "yes (4-neighbours)", "A = 4 ∉ V", "no", "no"], ["A, C", "no", "A = 4 ∉ V", "no", "no"], ["B, C", "no: (0,1) and (2,2) are 2 rows apart", "yes", "no", "no"],
    ["C, D", "diagonal", "yes", "no", "<b>yes</b>"], ["C, E", "diagonal", "yes", "no", "<b>yes</b>"]])}''')}
{paper("Slide 22 · m-adjacency", "worked", f'''<p class="q">V = {{0, 1, 2, 3, 5}}. A = (0,0) = 4, B = (0,1) = 2, C = (2,2) = 5, D = (3,3) = 0. Which pairs are m-adjacent?</p>
{mat(Q22, "C = 5 at (2,2), D = 0 at (3,3)")}
<p><b>A, B / A, C:</b> no, A = 4 ∉ V. <b>B, C:</b> not neighbours. <b>C, D:</b> D ∈ N<sub>D</sub>(C); N<sub>4</sub>(C) ∩ N<sub>4</sub>(D) = {{(2,3) = 4, (3,2) = 6}}, and neither 4 nor 6 is in V, so <b>C and D are m-adjacent</b>.</p>''')}
"""))

# ================================================================ 3. paths and components
P20 = [[0, 1, 1], [0, 2, 0], [0, 0, 1]]
V12 = {1, 2}
p20, q20 = (0, 2), (2, 2)
P23 = [[4, 2, 3, 2], [3, 3, 1, 3], [2, 3, 2, 2], [2, 1, 2, 3]]
m23 = find_path(P23, V12, (3, 0), (0, 3), "m")
C25 = [[1, 0, 1, 1], [1, 0, 1, 0], [0, 0, 0, 1]]
c25_4, c25_m = components(C25, {1}, 4), components(C25, {1}, "m")
S.append(sec("path", "Paths, connectivity, components, regions", "18–28", EXAM, f"""
<p><b>Slide 18.</b> A <b>digital path</b> from p = (x<sub>0</sub>, y<sub>0</sub>) to q = (x<sub>n</sub>, y<sub>n</sub>) is a sequence of <b>distinct</b> pixels (x<sub>0</sub>, y<sub>0</sub>), (x<sub>1</sub>, y<sub>1</sub>), …, (x<sub>n</sub>, y<sub>n</sub>) where each pixel is adjacent to the next. <b>n is the length</b> of the path. If (x<sub>0</sub>, y<sub>0</sub>) = (x<sub>n</sub>, y<sub>n</sub>) the path is <b>closed</b>. 4-, 8- and m-paths use the matching adjacency.</p>
<p><b>Slide 19.</b> p and q are <b>connected in S</b> if there is a path between them made only of pixels in S.</p>
{paper("Slide 20 · 4-, 8- and m-paths", "worked", f'''<p class="q">V = {{1, 2}}; p = (1,3), q = (3,3) in the slide's numbering (top-right and bottom-right).</p>
{mat(P20, "rows/cols 1–3 on the slide; here (0,2) = p and (2,2) = q")}
<p><b>8-path:</b> two exist: (1,3) → (1,2) → (2,2) → (3,3) and (1,3) → (2,2) → (3,3). That ambiguity is what m-adjacency removes.</p>
<p><b>m-path:</b> only (1,3) → (1,2) → (2,2) → (3,3). The diagonal step (1,3) → (2,2) is not allowed because they share the 4-neighbour (1,2) = 1 ∈ V. The step (2,2) → (3,3) is allowed: their shared 4-neighbours (2,3) and (3,2) are both 0.</p>
<p><b>4-path:</b> absent: from (2,2) the only way down is through 0s.</p>''')}
{psim("slide 20: switch between 4-, 8- and m-paths and watch which steps are allowed.", P20, V12, p20, q20, kind="m")}
{paper("Slide 23 · m-connected path", "worked", f'''<p class="q">V = {{1, 2}}. Find the m-connected path between p (bottom-left) and q (top-right). Is a 4-connected path possible?</p>
{mat(P23, "p = (3,0), q = (0,3)", hi=set(m23))}
<p><b>4-path:</b> {"none" if find_path(P23, V12, (3, 0), (0, 3), 4) is None else "exists"}. <b>m-path:</b> {ptxt(m23, P23)}, i.e. 2(p) → 1 → 2 → 2 → 1 → 2(q) as on the slide.</p>''')}
{psim("slide 23: the m-path, step by step. Try 4-path too: it fails.", P23, V12, (3, 0), (0, 3), kind="m")}
<p><b>Slide 24.</b> Two subsets S1 and S2 are <b>adjacent</b> if some pixel of S1 is adjacent to some pixel of S2.</p>
<p><b>Slide 25. Connected component:</b> for any pixel p in S, the set of pixels connected to it in S is a connected component of S. Example (V = {{1}}): 4-connectivity gives {len(c25_4)} components, m-connectivity {len(c25_m)}: the lone 1 at the bottom right joins the top-right group through a diagonal whose shared 4-neighbours are 0.</p>
{mats(mat(C25, f"{len(c25_4)} 4-connected components", hi={x for comp in c25_4 for x in comp}), mat(C25, f"{len(c25_m)} m-connected components"))}
<p><b>Slides 26–28.</b> If S has only one connected component, S is a <b>connected set</b>; a <b>region</b> is a connected set. Regions that are not adjacent are <b>disjoint</b>; two regions may be adjacent only under 8-adjacency (no 4-path between them, so their union is not 4-connected). The <b>boundary</b> (border, contour) of a region R is the set of its pixels that have at least one neighbour not in R; for a whole image, the first and last rows and columns.</p>
"""))

# ================================================================ 4. distances
S.append(sec("dist", "Distance measures", "29–33", EXAM, f"""
{idea("Three rulers. City block D<sub>4</sub>: walk only along streets (up/down + left/right), so add the two differences. Chessboard D<sub>8</sub>: a king may move diagonally, so only the bigger difference counts. Euclidean D<sub>e</sub>: the straight line, Pythagoras.")}
<p><b>Slide 29.</b> For pixels p (x,y), q (s,t), z (v,w), a distance function D has three properties:</p>
{formula("1. D(p,q) ≥ 0, and D(p,q) = 0 if and only if p = q<br>2. D(p,q) = D(q,p) (symmetry)<br>3. D(p,z) ≤ D(p,q) + D(q,z) (triangle inequality)")}
{formula("D<sub>4</sub>(p,q) = |x − s| + |y − t| &nbsp;&nbsp; D<sub>8</sub>(p,q) = max(|x − s|, |y − t|) &nbsp;&nbsp; D<sub>e</sub>(p,q) = √[(x − s)² + (y − t)²]")}
{mats(rings(4), rings(8))}
<p>The pixels with D<sub>4</sub> = 1 are exactly N<sub>4</sub>(p); the pixels with D<sub>8</sub> = 1 are N<sub>8</sub>(p).</p>
{paper("Slide 32 · practice", "worked", f'<p class="q">p = (3,4), q = (6,7). Find D<sub>4</sub>, D<sub>8</sub>, D<sub>e</sub>.</p>{dist_lines((3, 4), (6, 7))}')}
{paper("SP24 Final Q1(a)", "2 + 3 marks", f'''<p class="q">What are the properties of the distance function for 3 pixels a, b and c? How are the city-block, chessboard and Euclidean distances between a and b calculated?</p>
<p><b>Properties:</b> D(a,b) ≥ 0 with D(a,b) = 0 iff a = b; D(a,b) = D(b,a); D(a,c) ≤ D(a,b) + D(b,c).</p>
<p>For a = (x, y), b = (s, t): city block D<sub>4</sub> = |x − s| + |y − t|; chessboard D<sub>8</sub> = max(|x − s|, |y − t|); Euclidean D<sub>e</sub> = √[(x − s)² + (y − t)²]. Example a = (0,0), b = (3,4):</p>{dist_lines((0, 0), (3, 4), "a", "b")}''')}
<p><b>Slide 33 · Problem 2.11 (glance):</b> S1 and S2 are not 4-connected (q is not in N<sub>4</sub>(p)); they are 8-connected (q ∈ N<sub>8</sub>(p)); they are m-connected because q ∈ N<sub>D</sub>(p) and N<sub>4</sub>(p) ∩ N<sub>4</sub>(q) is empty of V-values.</p>
"""))

# ================================================================ 5. past papers
S22 = [[1, 4, 3, 4], [2, 3, 4, 7], [0, 5, 1, 6], [3, 4, 7, 1]]
V22 = {0, 1, 2, 4}
p22, r22, q22 = (0, 0), (0, 3), (3, 3)
m22 = find_path(S22, V22, p22, q22, "m")
S23 = [[9, 34, 20, 0], [16, 21, 50, 5], [5, 6, 11, 15], [7, 8, 10, 2], [8, 7, 9, 0]]
V23 = {10, 20, 9, 7, 0, 5, 1, 3}
p23, q23 = (2, 0), (4, 2)
e23 = find_path(S23, V23, p23, q23, 8)
F21 = [[0, 0, 0, 3, 2, 2, 1, 2, 1, 2], [0, 1, 0, 2, 1, 1, 1, 2, 2, 0], [0, 0, 0, 1, 1, 1, 0, 2, 3, 2], [0, 0, 1, 0, 0, 2, 2, 3, 2, 2], [0, 0, 1, 1, 1, 0, 0, 1, 1, 1]]
x21, y21 = (3, 2), (0, 6)
f4a, f4b, fmb = find_path(F21, {1, 2}, x21, y21, 4), find_path(F21, {0, 1}, x21, y21, 4), find_path(F21, {0, 1}, x21, y21, "m")
CB = [[1, 0, 1, 0], [0, 1, 0, 1], [1, 0, 1, 0], [0, 1, 0, 1]]
cb = {k: len(components(CB, {1}, k)) for k in (4, 8, "m")}
S.append(sec("papers", "Past questions solved like the answer script", "all", EXAM, f"""
<p>Coordinates are (row, column) from 0 at the top-left unless the paper numbers from 1.</p>
{paper("SP22 Final Q3(b)", "2 + 2 + 1.5 + 1 + 1.5 marks", f'''<p class="q">4×4 image, V = {{0, 1, 2, 4}}; p = (0,0) top-left, r = (0,3) top-right, q = (3,3) bottom-right. (i) Properties of the distance function for p, q, r. (ii) D<sub>4</sub>(p,q), D<sub>4</sub>(p,r), D<sub>8</sub>(p,q), D<sub>e</sub>(p,q). (iii) N<sub>4</sub>(p), N<sub>D</sub>(p), N<sub>8</sub>(p). (iv) Is there a 4-path between p and q? (v) An m-path between p and q?</p>
{mat(S22, "image; grey cells are not in V", pad={(r, c) for r in range(4) for c in range(4) if S22[r][c] not in V22})}
<p><b>(i)</b> D(p,q) ≥ 0 and = 0 only if p = q; D(p,q) = D(q,p); D(p,r) ≤ D(p,q) + D(q,r).</p>
<p><b>(ii)</b> D<sub>4</sub>(p,q) = |0 − 3| + |0 − 3| = <b>{d4(p22, q22)}</b>; D<sub>4</sub>(p,r) = |0 − 0| + |0 − 3| = <b>{d4(p22, r22)}</b>; D<sub>8</sub>(p,q) = max(3, 3) = <b>{d8(p22, q22)}</b>; D<sub>e</sub>(p,q) = √(9 + 9) = <b>{de(p22, q22):.4f}</b>.</p>
<p><b>(iii)</b> p is a corner, so the other neighbours fall outside: N<sub>4</sub>(p) = {nb(S22, p22, "4")}; N<sub>D</sub>(p) = {nb(S22, p22, "D")}; N<sub>8</sub>(p) = {nb(S22, p22, "8")}.</p>
<p><b>(iv)</b> 4-path: <b>{"none" if find_path(S22, V22, p22, q22, 4) is None else "exists"}</b>. From p, the 4-neighbours in V are (0,1) = 4 and (1,0) = 2; from them every 4-step leads to 3, 5 or 7 (not in V), so q cannot be reached.</p>
<p><b>(v)</b> m-path: <b>{ptxt(m22, S22)}</b>. Check the diagonal (0,1) → (1,2): shared 4-neighbours (0,2) = 3 and (1,1) = 3 are not in V, so the step is m-adjacent; likewise (2,2) → (3,3) with (2,3) = 6, (3,2) = 7.</p>''')}
{psim("SP22 Q3(b): the 4-path fails; the m-path goes round through the diagonals.", S22, V22, p22, q22, kind="4")}
{paper("SP23 Final Q2(e)", "2 + 3 marks", f'''<p class="q">5×4 image [9, 34, 20, 0, 16, 21, 50, 5, 5, 6, 11, 15, 7, 8, 10, 2, 8, 7, 9, 0], V = {{10, 20, 9, 7, 0, 5, 1, 3}}. (i) Does an 8-path exist between the 9th and the 19th pixels? (ii) Their city-block, chessboard and Euclidean distances.</p>
<p>5×4 = 5 rows × 4 columns. Counting row by row from 1: the 9th pixel is (2,0) = 5 and the 19th is (4,2) = 9.</p>
{mat(S23, "grey = not in V", pad={(r, c) for r in range(5) for c in range(4) if S23[r][c] not in V23}, hi=set(e23))}
<p><b>(i)</b> Yes: <b>{ptxt(e23, S23)}</b>. All values are in V and each step goes to an 8-neighbour (the step (3,0) → (4,1) is diagonal).</p>
<p><b>(ii)</b></p>{dist_lines(p23, q23)}''')}
{psim("SP23 Q2(e): the 8-path from the 9th to the 19th pixel.", S23, V23, p23, q23, kinds=("8", "4", "m"))}
{paper("F21 Final B4(b)", "2 + 1 + 2 + 1 marks", f'''<p class="q">S1 (columns 0–4) and S2 (columns 5–9) side by side; x = (3,2) in S1, y = (0,6) in S2. (i) Define a digital path. (ii) Is there a 4-path between x and y for V = {{1, 2}}? (iii) 4-path and m-path for V = {{0, 1}}. (iv) Are S1 and S2 4-adjacent for V = {{1, 2}}?</p>
{mat(F21, "x = (3,2), y = (0,6)", ctr=x21)}
<p><b>(i)</b> A sequence of distinct pixels from x to y, each adjacent (4, 8 or m) to the next, all with values in V; the number of steps is its length.</p>
<p><b>(ii)</b> V = {{1, 2}}: <b>{"no 4-path" if f4a is None else ptxt(f4a, F21)}</b>. x's 4-neighbours are 0, 0, 1 and 0; the 1 below leads only to more 1s at the bottom that never reach the top-right through 1s and 2s.</p>
<p><b>(iii)</b> V = {{0, 1}}: 4-path <b>{ptxt(f4b, F21)}</b>; m-path <b>{ptxt(fmb, F21)}</b> (the same here: a 4-path is also an m-path).</p>
<p><b>(iv)</b> Yes: column 4 of S1 and column 5 of S2 touch with values in {{1, 2}}: row 0: 2 | 2, row 1: 1 | 1, row 2: 1 | 1.</p>''')}
{psim("F21 B4(b): change nothing for V = {0, 1}: watch the 4-path being found.", F21, {0, 1}, x21, y21, kinds=("4", "m"))}
{paper("SP25 Final Q1(b)", "4 marks", f'''<p class="q">State the difference between 4-neighbour, 8-neighbour and m-connectivity. For the 4×4 binary image [1010; 0101; 1010; 0101], find the number of connected components under each connectivity and discuss the effect of diagonal adjacency.</p>
<p><b>4-connectivity:</b> only the up/down/left/right neighbours link pixels. <b>8-connectivity:</b> the four diagonal neighbours link too. <b>m-connectivity:</b> 4-neighbours always link; a diagonal neighbour links only if the two pixels have no common 4-neighbour with a value in V (removes the double paths of 8-connectivity).</p>
{mat(CB, "V = {1}")}
<p>Every 1 has only 0s as 4-neighbours, so with 4-connectivity each 1 is alone: <b>{cb[4]} components</b>. Every 1 touches other 1s diagonally, so 8-connectivity joins all of them: <b>{cb[8]} component</b>. For each diagonal pair the two shared 4-neighbours are 0 (not in V), so every diagonal link is m-adjacent as well: <b>{cb["m"]} component</b>.</p>
<p><b>Effect of diagonal adjacency:</b> it merges pixels that touch only at corners, dropping the count from {cb[4]} to {cb[8]}. m-connectivity keeps those joins here and only removes redundant (ambiguous) diagonal links where a 4-connection already exists.</p>''')}
"""))

# ================================================================ 6. traps
S.append(sec("traps", "Traps and one-minute sheet", "all", None, f"""
<ul class="traps">
<li>(x, y) = (row, column), origin top-left. If the paper counts from 1, keep its numbering in the answer.</li>
<li>Adjacent = neighbour <b>and</b> both values in V. A pixel whose value is not in V is never on a path.</li>
<li>m-adjacency for a diagonal pair: check the two shared 4-neighbours. If either is in V, the diagonal does not count.</li>
<li>A path ends at q only if q itself is in V.</li>
<li>Count pixels row by row when the paper gives a flat list (5×4 = 5 rows, 4 columns).</li>
<li>D<sub>4</sub> ≥ D<sub>e</sub> ≥ D<sub>8</sub> always.</li>
</ul>
{tbl(["what", "formula"], [["N<sub>4</sub>(p)", "(x±1, y), (x, y±1)"], ["N<sub>D</sub>(p)", "(x±1, y±1)"], ["D<sub>4</sub>", "|x − s| + |y − t|"], ["D<sub>8</sub>", "max(|x − s|, |y − t|)"], ["D<sub>e</sub>", "√[(x − s)² + (y − t)²]"]])}
"""))

toc = [("nbr", "Neighbours"), ("adj", "Adjacency"), ("path", "Paths & components"), ("dist", "Distances"), ("papers", "Past papers"), ("traps", "Traps")]
OUT.write_text(page("DIP Deck 03 Lesson", "CSE 4227 · Chapter 2 · Deck 03", "Pixel relationships: neighbours, adjacency, paths, distances",
                    "N4, ND, N8, the three adjacencies (with m-adjacency explained), paths and components with a step-by-step path finder, and D4/D8/De, with every past question solved. Fall 2024 is left out.",
                    toc, S, extra=sim_assets()), encoding="utf-8")

# ---------------------------------------------------------------- self-check (data/answers.json PIX/*)
assert find_path(S22, V22, p22, q22, 4) is None and m22 == [(0, 0), (0, 1), (1, 2), (2, 2), (3, 3)]
assert (d4(p22, q22), d4(p22, r22), d8(p22, q22), round(de(p22, q22), 4)) == (6, 3, 3, 4.2426)
assert e23 == [(2, 0), (3, 0), (4, 1), (4, 2)] and (d4(p23, q23), d8(p23, q23)) == (4, 2)
assert f4a is None and f4b == [(3, 2), (2, 2), (2, 3), (2, 4), (1, 4), (1, 5), (1, 6), (0, 6)] and fmb == f4b
assert cb == {4: 8, 8: 1, "m": 1}
assert (len(c25_4), len(c25_m)) == (3, 2)
assert find_path(P20, V12, p20, q20, "m") == [(0, 2), (0, 1), (1, 1), (2, 2)] and find_path(P20, V12, p20, q20, 4) is None
print(OUT, OUT.stat().st_size, "slide23 m-path", ptxt(m23, P23))
