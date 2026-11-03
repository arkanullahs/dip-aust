// Step-by-step simulators for the DIP lesson pages (decks 05–07).
// Every <div class="sim" data-sim='{...}'> on the page becomes one simulator.
// The maths (SIMK.*) is pure and is tested by sim_kit_test.js.
const SIMK = (() => {
  const rhu = x => Math.floor(x + 0.5 + 1e-9); // slide rule: .5 rounds up

  /* ------------------------------------------------ 2-D filters */
  function at(img, i, j, pad) {
    const H = img.length, W = img[0].length;
    if (i >= 0 && i < H && j >= 0 && j < W) return { v: img[i][j], out: false };
    if (pad === 'zero') return { v: 0, out: true };
    if (pad === 'replicate') return { v: img[Math.min(Math.max(i, 0), H - 1)][Math.min(Math.max(j, 0), W - 1)], out: true };
    return { v: null, out: true };
  }
  function positions(img, pad) {
    const H = img.length, W = img[0].length, lo = pad === 'discard' ? 1 : 0, p = [];
    for (let r = lo; r < H - lo; r++) for (let c = lo; c < W - lo; c++) p.push([r, c]);
    return p;
  }
  const dot = (k, z) => z.map((v, i) => k[i] * v);
  const sum = a => a.reduce((x, y) => x + y, 0);
  function filter(img, r, c, f, pad) {
    const win = [];
    for (let dr = -1; dr <= 1; dr++) for (let dc = -1; dc <= 1; dc++) win.push(at(img, r + dr, c + dc, pad));
    const z = win.map(o => o.v);
    if (f.rank !== undefined) {
      const sorted = [...z].sort((a, b) => a - b);
      return { win, z, sorted, result: sorted[f.rank] };
    }
    if (f.kx) {
      const px = dot(f.kx, z), py = dot(f.ky, z), gx = sum(px), gy = sum(py);
      return { win, z, px, py, gx, gy, result: Math.abs(gx) + Math.abs(gy) };
    }
    const prods = dot(f.k, z), s = sum(prods);
    if (f.post) return { win, z, prods, sum: s, result: z[4] + f.post * s };
    return { win, z, prods, sum: s, exact: s / f.n, result: f.n === 1 ? s : rhu(s / f.n) };
  }

  /* ------------------------------------------------ 1-D signals */
  function oneD(sig, x, mode) {
    const g = i => sig[Math.min(Math.max(i, 0), sig.length - 1)]; // replicate ends
    const a = g(x - 1), b = sig[x], c = g(x + 1);
    if (mode === 'd1') return { a, b, c, result: c - b };
    if (mode === 'd2') return { a, b, c, result: c + a - 2 * b };
    const blur = rhu((a + b + c) / 3), mask = b - blur;
    return { a, b, c, blur, mask, result: b + mask };
  }
  const oneDPositions = (sig, mode) => (mode === 'unsharp' ? sig.map((_, i) => i) : sig.slice(1, -1).map((_, i) => i + 1));

  /* ------------------------------------------------ histogram equalization (exact integer maths) */
  // dp = 4: exact fractions. dp = 2: PDF rounded to 2 places first, as on slide 49.
  function equalize(n, dp) {
    const L = n.length, N = sum(n), D = dp === 2 ? 100 : N;
    const unit = dp === 2 ? n.map(v => Math.round((v * 100) / N)) : n.slice();
    const cum = [];
    unit.reduce((acc, v, i) => (cum[i] = acc + v), 0);
    if (dp === 2) cum[L - 1] = 100;
    const s = cum.map(cv => Math.floor((2 * (L - 1) * cv + D) / (2 * D)));
    return { L, N, D, unit, cum, s };
  }
  function eqHist(n, s) {
    const out = n.map(() => 0);
    n.forEach((v, r) => (out[s[r]] += v));
    return out;
  }
  // Specified histogram given as counts or as probabilities in hundredths.
  function specEqualize(spec, L, dp, isCounts) {
    if (isCounts) return equalize(spec, dp);
    const cum = [];
    spec.reduce((acc, v, i) => (cum[i] = acc + v), 0);
    cum[L - 1] = 100;
    return { L, N: 100, D: 100, unit: spec.slice(), cum, s: cum.map(cv => Math.floor((2 * (L - 1) * cv + 100) / 200)) };
  }
  function matchMap(H, S) {
    return H.map(h => {
      const d = Math.min(...S.map(x => Math.abs(x - h)));
      const sv = Math.max(...S.filter(x => Math.abs(x - h) === d)); // tie -> higher S (slide 55)
      return S.indexOf(sv); // several z share it -> first z
    });
  }
  /* ------------------------------------------------ compression (deck 13) */
  // Huffman as on slides 29-35: sort descending (ties keep the given order), merge the two smallest,
  // the sum goes ABOVE the first strictly smaller value (so below equal ones); upper branch 0, lower 1.
  // w = integer weights (counts, or probabilities × 100).
  function huffman(syms, w) {
    let id = 0;
    const leaves = syms.map((s, i) => ({ id: id++, sym: s, w: w[i] }));
    const start = leaves.map((n, i) => [n, i]).sort((a, b) => b[0].w - a[0].w || a[1] - b[1]).map(x => x[0]);
    const lists = [start], merges = [];
    let cur = start.slice();
    while (cur.length > 2) {
      const a = cur[cur.length - 2], b = cur[cur.length - 1];
      const node = { id: id++, w: a.w + b.w, kids: [a, b] };
      cur = cur.slice(0, -2);
      let pos = cur.findIndex(n => n.w < node.w);
      if (pos < 0) pos = cur.length;
      cur.splice(pos, 0, node);
      merges.push({ a, b, node, pos, col: lists.length - 1 });
      lists.push(cur.slice());
    }
    const code = {};
    cur[0].code = '0'; cur[1].code = '1';
    for (let k = merges.length - 1; k >= 0; k--) {
      const m = merges[k];
      m.a.code = m.node.code + '0'; m.b.code = m.node.code + '1';
    }
    leaves.forEach(n => (code[n.sym] = n.code));
    const W = sum(w);
    const lavgNum = leaves.reduce((t, n) => t + n.w * n.code.length, 0);
    const H = -leaves.reduce((t, n) => (n.w ? t + (n.w / W) * Math.log2(n.w / W) : t), 0);
    return { leaves, lists, merges, code, W, lavg: lavgNum / W, lavgNum, H };
  }

  // LZW as on slides 77-95: dictionary 0..255 holds single gray levels, new entries from 256.
  function lzw(seq, start = 256) {
    const dic = new Map(), rows = [], out = [];
    let nxt = start, crs = '';
    const has = s => s.split('-').length === 1 ? Number(s) < start : dic.has(s);
    const codeOf = s => (s.split('-').length === 1 ? Number(s) : dic.get(s));
    seq.forEach((px, i) => {
      const cand = crs === '' ? String(px) : crs + '-' + px;
      if (has(cand)) { rows.push({ i, crs, px, cand, hit: true }); crs = cand; }
      else {
        const code = codeOf(crs);
        out.push(code); dic.set(cand, nxt);
        rows.push({ i, crs, px, cand, hit: false, code, loc: nxt });
        nxt++; crs = String(px);
      }
    });
    out.push(codeOf(crs));
    rows.push({ i: seq.length, crs, px: null, final: true, code: codeOf(crs) });
    return { rows, out, dic };
  }

  // Arithmetic coding, slides 56-63. Exact decimals with BigInt: probabilities as strings like "0.45".
  function arith(probs, msgIdx) {
    const dp = Math.max(...probs.map(p => (p.split('.')[1] || '').length));
    const one = 10n ** BigInt(dp);
    const P = probs.map(p => BigInt(Math.round(Number(p) * Number(one))));
    const lo = [], hi = [];
    P.reduce((acc, p, i) => { lo[i] = acc; hi[i] = acc + p; return acc + p; }, 0n);
    let scale = 1n, L = 0n, Hh = 1n; // interval = [L/scale, Hh/scale)
    const steps = [];
    msgIdx.forEach(s => {
      const w = Hh - L;           // in units of 1/scale
      const nL = L * one + w * lo[s], nH = L * one + w * hi[s];
      steps.push({ s, L, Hh, scale, w, nL, nH, nscale: scale * one });
      L = nL; Hh = nH; scale *= one;
    });
    // shortest decimal q with L/scale <= q < Hh/scale
    const digits = String(scale).length - 1;
    let q = null, qd = 0;
    for (let d = 1; d <= digits; d++) {
      const unit = 10n ** BigInt(digits - d);
      const c = ((L + unit - 1n) / unit) * unit;
      if (c < Hh) { q = c; qd = d; break; }
    }
    return { dp, one, lo, hi, steps, L, Hh, scale, q, qd, digits };
  }
  const dec = (num, scale) => { // BigInt fraction num/scale (scale = 10^k) as a trimmed decimal string
    const k = String(scale).length - 1;
    if (k === 0) return String(num);
    const s = String(num).padStart(k + 1, '0');
    const t = (s.slice(0, -k) + '.' + s.slice(-k)).replace(/0+$/, '').replace(/\.$/, '');
    return t;
  };

  function rle(row) {
    const runs = [];
    row.forEach((v, c) => {
      if (runs.length && runs[runs.length - 1].v === v) runs[runs.length - 1].n++;
      else runs.push({ v, n: 1, c });
    });
    return runs;
  }

  function golomb(n, m) {
    const q = Math.floor(n / m), k = Math.ceil(Math.log2(m)), c = 2 ** k - m, r = n % m;
    const unary = '1'.repeat(q) + '0';
    let rb, trunc = r < c;
    if (trunc) rb = k > 1 ? r.toString(2).padStart(k - 1, '0') : '';
    else rb = k > 0 ? (r + c).toString(2).padStart(k, '0') : '';
    return { q, k, c, r, unary, rb, trunc, code: unary + rb };
  }
  /* ------------------------------------------------ binary morphology (decks 11-12) */
  // se cells: 1 = part of B (for HMT: must be foreground), 0 = not part (HMT: must be background), null = don't care.
  // Outside the image counts as background (0).
  const px = (A, r, c) => (r >= 0 && r < A.length && c >= 0 && c < A[0].length ? A[r][c] : 0);
  const inside = (A, r, c) => r >= 0 && r < A.length && c >= 0 && c < A[0].length;
  function seCells(se, origin, want = 1) {
    const out = [];
    se.forEach((row, i) => row.forEach((v, j) => { if (v === want) out.push([i - origin[0], j - origin[1]]); }));
    return out;
  }
  // erosion: (B)z ⊆ A, cells z + b.  dilation: (B̂)z ∩ A ≠ ∅, cells z − b.  hmt: exact match of 1s and 0s around z.
  function morphAt(A, r, c, se, origin, kind) {
    if (kind === 'hmt') {
      const cells = [];
      se.forEach((row, i) => row.forEach((v, j) => { if (v !== null) cells.push({ r: r + i - origin[0], c: c + j - origin[1], want: v }); }));
      cells.forEach(x => (x.have = px(A, x.r, x.c)));
      const bad = cells.find(x => x.have !== x.want);
      return { cells, result: bad ? 0 : 1, bad };
    }
    const sign = kind === 'dilate' ? -1 : 1;
    const cells = seCells(se, origin).map(([dr, dc]) => ({ r: r + sign * dr, c: c + sign * dc }));
    cells.forEach(x => (x.have = px(A, x.r, x.c)));
    if (kind === 'erode') { const bad = cells.find(x => !x.have); return { cells, result: bad ? 0 : 1, bad }; }
    const hit = cells.find(x => x.have); return { cells, result: hit ? 1 : 0, hit };
  }
  function morphImage(A, se, origin, kind, discard) {
    return A.map((row, r) => row.map((_, c) => {
      const R = morphAt(A, r, c, se, origin, kind);
      return discard && R.cells.some(x => !inside(A, x.r, x.c)) ? null : R.result;
    }));
  }
  const minus = (X, Y) => X.map((row, r) => row.map((v, c) => (v && !Y[r][c] ? 1 : 0)));
  const orAll = Ms => Ms[0].map((row, r) => row.map((_, c) => (Ms.some(M => M[r][c]) ? 1 : 0)));

  /* ------------------------------------------------ chain code (row 0 at the top, so "up" = row − 1) */
  const DIRS = { 8: [[0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1], [1, 0], [1, 1]], 4: [[0, 1], [-1, 0], [0, -1], [1, 0]] };
  // closed list of corner vertices -> every pixel on the way (each move to a neighbour)
  function unitPath(path) {
    const out = [];
    path.forEach((a, k) => {
      const b = path[(k + 1) % path.length], dr = Math.sign(b[0] - a[0]), dc = Math.sign(b[1] - a[1]);
      for (let s = 0; s < Math.max(Math.abs(b[0] - a[0]), Math.abs(b[1] - a[1])); s++) out.push([a[0] + s * dr, a[1] + s * dc]);
    });
    return out;
  }
  function chainCode(path, n = 8) {
    return path.map((a, k) => {
      const b = path[(k + 1) % path.length], d = DIRS[n].findIndex(([dr, dc]) => dr === b[0] - a[0] && dc === b[1] - a[1]);
      if (d < 0) throw new Error(`(${a}) -> (${b}) is not a ${n}-neighbour move`);
      return d;
    });
  }
  function pathFromCode(code, n = 8) {
    const p = [[0, 0]];
    code.slice(0, -1).forEach(c => { const [r, q] = p[p.length - 1]; p.push([r + DIRS[n][c][0], q + DIRS[n][c][1]]); });
    const r0 = Math.min(...p.map(x => x[0])), c0 = Math.min(...p.map(x => x[1]));
    return p.map(([r, c]) => [r - r0, c - c0]);
  }
  // slide 22: (next − this) mod n; slide 23: (this − next) mod n. The last digit wraps to the first.
  const firstDiff = (code, n = 8, rule = 'next') => code.map((c, i) => {
    const b = code[(i + 1) % code.length];
    return (((rule === 'next' ? b - c : c - b) % n) + n) % n;
  });
  // smallest circular shift, with the comparison made at every shift
  function minRot(seq) {
    const m = seq.length, log = [];
    let best = 0;
    for (let k = 0; k < m; k++) {
      const s = seq.slice(k).concat(seq.slice(0, k)), prev = log.length ? log[best].seq : null;
      const pos = prev ? s.findIndex((v, j) => v !== prev[j]) : -1, better = !!prev && pos >= 0 && s[pos] < prev[pos];
      if (better) best = k;
      log.push({ seq: s, prev, pos, better, best });
    }
    return { best: log[best].seq, idx: best, log };
  }
  /* ------------------------------------------------ colour (deck 14 slides 20, 29): values normalised to [0,1] first */
  const cmy = (r, g, b) => [1 - r / 255, 1 - g / 255, 1 - b / 255];
  function hsi(r8, g8, b8) {
    const R = r8 / 255, G = g8 / 255, B = b8 / 255, sum = R + G + B;
    const num = 0.5 * ((R - G) + (R - B)), den = Math.sqrt((R - G) ** 2 + (R - B) * (G - B));
    const theta = den ? (Math.acos(Math.max(-1, Math.min(1, num / den))) * 180) / Math.PI : null;
    const H = theta === null ? null : B <= G ? theta : 360 - theta;
    const S = sum ? 1 - (3 * Math.min(R, G, B)) / sum : null;
    return { R, G, B, num, den, theta, H, S, I: sum / 3 };
  }
  /* ------------------------------------------------ Canny steps 3–5 (deck 08 slides 45–59, same rules as solvers.canny_345) */
  const ARROW = { '→': [0, 1], '←': [0, -1], '↑': [-1, 0], '↓': [1, 0], '↗': [-1, 1], '↙': [1, -1], '↖': [-1, -1], '↘': [1, 1] };
  function canny(M, D, TH, TL) {
    const H = M.length, W = M[0].length, ins = (r, c) => r >= 0 && r < H && c >= 0 && c < W;
    const nms = [], gN = M.map(row => row.slice());
    if (D) M.forEach((row, r) => row.forEach((v, c) => {
      const [dr, dc] = ARROW[D[r][c]], nb = [1, -1].map(s => ({ r: r + s * dr, c: c + s * dc })).map(p => ({ ...p, v: ins(p.r, p.c) ? M[p.r][p.c] : null }));
      const keep = nb.every(p => p.v === null || v >= p.v);
      gN[r][c] = keep ? v : 0;
      nms.push({ r, c, v, d: D[r][c], nb, keep });
    }));
    const gNH = gN.map(row => row.map(v => (v >= TH ? v : 0))), gNL = gN.map(row => row.map(v => (v >= TL && v < TH ? v : 0)));
    const g = gNH.map(row => row.slice()), weak = [];
    gNL.forEach((row, r) => row.forEach((v, c) => {
      if (!v) return;
      const strong = [];
      for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) if ((i || j) && ins(r + i, c + j) && gNH[r + i][c + j]) strong.push({ r: r + i, c: c + j, v: gNH[r + i][c + j] });
      if (strong.length) g[r][c] = v;
      weak.push({ r, c, v, strong });
    }));
    return { nms, gN, gNH, gNL, weak, g };
  }
  /* ------------------------------------------------ region growing and iterative threshold (deck 09 slides 14–17, 42) */
  // breadth-first from the seed; a neighbour joins if |its value − the value it is compared with| ≤ T
  function grow(img, seed, T, conn = 4, compare = 'nbr') {
    const H = img.length, W = img[0].length, key = (r, c) => r * W + c, inReg = new Set([key(...seed)]), queue = [seed], log = [];
    const offs = conn === 4 ? [[-1, 0], [0, -1], [0, 1], [1, 0]] : [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]];
    while (queue.length) {
      const [r, c] = queue.shift(), base = compare === 'seed' ? img[seed[0]][seed[1]] : img[r][c];
      for (const [dr, dc] of offs) {
        const a = r + dr, b = c + dc;
        if (a < 0 || a >= H || b < 0 || b >= W) continue;
        const already = inReg.has(key(a, b)), d = Math.abs(img[a][b] - base), ok = !already && d <= T;
        if (ok) { inReg.add(key(a, b)); queue.push([a, b]); }
        log.push({ from: [r, c], base, to: [a, b], v: img[a][b], d, ok, already });
      }
    }
    return { log, region: [...inReg].map(k => [Math.floor(k / W), k % W]) };
  }
  function iterT(values, T0, eps = 0.5) {
    let T = T0 ?? values.reduce((s, v) => s + v, 0) / values.length;
    const rows = [];
    for (let it = 0; it < 50; it++) {
      const g1 = values.filter(v => v > T), g2 = values.filter(v => v <= T);
      const m1 = g1.length ? g1.reduce((s, v) => s + v, 0) / g1.length : 0, m2 = g2.length ? g2.reduce((s, v) => s + v, 0) / g2.length : 0, Tn = (m1 + m2) / 2;
      rows.push({ T, g1, g2, m1, m2, Tn, dT: Math.abs(Tn - T) });
      if (Math.abs(Tn - T) < eps) break;
      T = Tn;
    }
    return rows;
  }
  /* ------------------------------------------------ 4-, 8-, m-paths (deck 03, same search order as solvers.find_path) */
  function findPath(img, V, p, q, kind) {
    const H = img.length, W = img[0].length, inside = (r, c) => r >= 0 && r < H && c >= 0 && c < W, inV = (r, c) => inside(r, c) && V.includes(img[r][c]);
    const N4 = [[1, 0], [-1, 0], [0, 1], [0, -1]], ND = [[1, 1], [1, -1], [-1, 1], [-1, -1]];
    const key = (r, c) => r + ',' + c, prev = new Map([[key(...p), null]]), queue = [p], log = [];
    if (!inV(...p) || !inV(...q)) return { log, path: null, bad: !inV(...p) ? p : q };
    while (queue.length) {
      const [r, c] = queue.shift(), checks = [];
      if (r === q[0] && c === q[1]) {
        const path = [];
        for (let k = key(r, c); k; k = prev.get(k)) path.unshift(k.split(',').map(Number));
        log.push({ at: [r, c], checks, reached: true });
        return { log, path };
      }
      const consider = (b, diag) => {
        const [a2, b2] = b;
        if (!inside(a2, b2)) return;
        const ck = { to: b, v: img[a2][b2], diag, inV: V.includes(img[a2][b2]), seen: prev.has(key(a2, b2)) };
        if (diag && kind === 'm' && ck.inV) {
          ck.shared = [[r, b2], [a2, c]].map(([x, y]) => ({ at: [x, y], v: img[x][y], inV: V.includes(img[x][y]) }));
          ck.blocked = ck.shared.some(s => s.inV);
        }
        ck.ok = ck.inV && !ck.seen && !ck.blocked;
        if (ck.ok) { prev.set(key(a2, b2), key(r, c)); queue.push(b); }
        checks.push(ck);
      };
      N4.forEach(([dr, dc]) => consider([r + dr, c + dc], false));
      if (kind !== 4) ND.forEach(([dr, dc]) => consider([r + dr, c + dc], true));
      log.push({ at: [r, c], checks });
    }
    return { log, path: null };
  }
  /* ------------------------------------------------ nearest-neighbour zoom (deck 02 slides 46–55): position = ceil(ratio × i), 1-indexed */
  const nnPos = (old, n) => Array.from({ length: n }, (_, i) => Math.floor(((i + 1) * old + n - 1) / n));
  function nnZoom(img, h, w) {
    const rp = nnPos(img.length, h), cp = nnPos(img[0].length, w);
    return { rp, cp, out: rp.map(r => cp.map(c => img[r - 1][c - 1])) };
  }
  return { rhu, at, positions, filter, oneD, oneDPositions, equalize, eqHist, specEqualize, matchMap, sum, huffman, lzw, arith, dec, rle, golomb, morphAt, morphImage, minus, orAll, inside, unitPath, chainCode, pathFromCode, firstDiff, minRot, cmy, hsi, canny, grow, iterT, findPath, nnZoom };
})();
if (typeof module !== 'undefined') module.exports = SIMK;

/* ================================================================ UI (browser only) */
if (typeof document !== 'undefined') (() => {
  const K = SIMK, DATA = window.SIM_DATA || { images: {}, filters: {} };
  const fmt = (x, d = 2) => (Number.isInteger(x) ? String(x) : x.toFixed(d));
  const signed = a => a.map((x, k) => (k === 0 ? String(x) : x < 0 ? '− ' + -x : '+ ' + x)).join(' ');
  const tbl = rows => `<table>${rows.map(r => `<tr>${r.map(c => (typeof c === 'object' && c !== null ? `<td class="${c.cls || ''}"${c.attr || ''}>${c.v}</td>` : `<td>${c}</td>`)).join('')}</tr>`).join('')}</table>`;
  const fig = (inner, cap, cls = 'mat sm') => `<figure class="${cls}">${inner}${cap ? `<figcaption>${cap}</figcaption>` : ''}</figure>`;

  // bar chart; vals may contain null (not filled yet)
  function bars(vals, { labels, hi = -1, cap = '', fmtv = v => v, color = 'c1', w = 300, h = 170 } = {}) {
    const n = vals.length, Lp = 34, R = 8, T = 16, B = 28, pw = w - Lp - R, ph = h - T - B;
    const top = Math.max(1e-9, ...vals.map(v => v || 0)), step = pw / n, bw = Math.max(2, step * 0.62), dense = n > 12;
    let o = `<svg viewBox="0 0 ${w} ${h}" class="plot" role="img"><line x1="${Lp}" y1="${T + ph}" x2="${Lp + pw}" y2="${T + ph}" class="axis"/><line x1="${Lp}" y1="${T}" x2="${Lp}" y2="${T + ph}" class="axis"/>`;
    vals.forEach((v, i) => {
      const x = Lp + i * step + (step - bw) / 2;
      if (v) {
        const bh = (v / top) * ph;
        o += `<rect x="${x.toFixed(1)}" y="${(T + ph - bh).toFixed(1)}" width="${bw.toFixed(1)}" height="${bh.toFixed(1)}" class="${i === hi ? 'barhi' : 'bar ' + color}"/>`;
        o += `<text x="${(x + bw / 2).toFixed(1)}" y="${(T + ph - bh - 3).toFixed(1)}" class="bval" text-anchor="middle">${fmtv(v)}</text>`;
      }
      if (!dense || v || i === hi || i === 0 || i === n - 1)
        o += `<text x="${(x + bw / 2).toFixed(1)}" y="${T + ph + 12}" class="tick" text-anchor="middle">${labels ? labels[i] : i}</text>`;
    });
    return fig(o + '</svg>', cap, 'fig');
  }
  // staircase s = T(r); s[r] may be null (not known yet)
  function stairs(s, { hi = -1, cap = '' } = {}) {
    const Lm = s.length - 1, w = 280, h = 220, Lp = 34, R = 10, T = 12, B = 28, pw = w - Lp - R, ph = h - T - B;
    const X = x => Lp + (x / (Lm + 0.7)) * pw, Y = y => T + ph - (y / Lm) * ph;
    let o = `<svg viewBox="0 0 ${w} ${h}" class="plot" role="img"><line x1="${Lp}" y1="${T + ph}" x2="${Lp + pw}" y2="${T + ph}" class="axis"/><line x1="${Lp}" y1="${T}" x2="${Lp}" y2="${T + ph}" class="axis"/>`;
    const tk = Lm > 10 ? [0, 8, 16, 24, Lm] : [...Array(Lm + 1).keys()];
    tk.forEach(t => {
      o += `<text x="${X(t).toFixed(1)}" y="${T + ph + 13}" class="tick" text-anchor="middle">${t}</text><text x="${Lp - 5}" y="${(Y(t) + 4).toFixed(1)}" class="tick" text-anchor="end">${t}</text>`;
    });
    let pts = [], prev = null;
    s.forEach((v, r) => {
      if (v === null) return;
      if (prev !== null) pts.push([r, prev]);
      pts.push([r, v], [r < Lm ? r + 1 : r + 0.7, v]);
      prev = v;
    });
    if (pts.length) o += `<polyline points="${pts.map(([x, y]) => `${X(x).toFixed(1)},${Y(y).toFixed(1)}`).join(' ')}" class="cv c1" fill="none"/>`;
    s.forEach((v, r) => { if (v !== null) o += `<circle cx="${X(r).toFixed(1)}" cy="${Y(v).toFixed(1)}" r="${r === hi ? 5 : 3.2}" class="pt ${r === hi ? 'acc' : ''}"/>`; });
    o += `<text x="${Lp + pw / 2}" y="${h - 3}" class="axlab" text-anchor="middle">r<tspan dy="3" font-size="9">k</tspan></text></svg>`;
    return fig(o, cap, 'fig');
  }
  // signed line plot for 1-D signals; series = [{v:[...], cls}], values may be null
  function lines1(series, { lo, hi, cap = '', cur = -1 } = {}) {
    const n = Math.max(...series.map(s => s.v.length)) - 1, w = 340, h = 190, Lp = 30, R = 8, T = 10, B = 22, pw = w - Lp - R, ph = h - T - B;
    const X = x => Lp + (x / n) * pw, Y = y => T + ph - ((y - lo) / (hi - lo)) * ph;
    let o = `<svg viewBox="0 0 ${w} ${h}" class="plot" role="img"><line x1="${Lp}" y1="${Y(0).toFixed(1)}" x2="${Lp + pw}" y2="${Y(0).toFixed(1)}" class="grid"/><line x1="${Lp}" y1="${T}" x2="${Lp}" y2="${T + ph}" class="axis"/>`;
    [lo, 0, hi].forEach(t => (o += `<text x="${Lp - 4}" y="${(Y(t) + 4).toFixed(1)}" class="tick" text-anchor="end">${t}</text>`));
    if (cur >= 0) o += `<rect x="${(X(cur) - 5).toFixed(1)}" y="${T}" width="10" height="${ph}" class="band2"/>`;
    series.forEach(s => {
      const p = s.v.map((v, i) => (v === null ? null : `${X(i).toFixed(1)},${Y(v).toFixed(1)}`)).filter(Boolean);
      if (p.length > 1) o += `<polyline points="${p.join(' ')}" class="cv ${s.cls}" fill="none"/>`;
      s.v.forEach((v, i) => { if (v !== null) o += `<circle cx="${X(i).toFixed(1)}" cy="${Y(v).toFixed(1)}" r="2.6" class="pt ${s.cls === 'c3' ? 'c3p' : ''}"/>`; });
    });
    return fig(o + '</svg>', cap, 'fig');
  }

  /* ------------------------------------------------ the player shared by every simulator */
  function player(el, opt) {
    el.innerHTML = `<div class="ctl">${opt.controls || ''}</div><p class="simnote"></p>
<div class="btns"><button data-a="reset">Restart</button><button data-a="prev">◀ Back</button><button data-a="next" class="main">Next step ▶</button><button data-a="skip">${opt.skipLabel || 'Skip ⏭'}</button>${opt.phaseKey ? '<button data-a="phase">Next phase ⏭⏭</button>' : ''}<button data-a="play">Play</button>
<select data-a="speed" aria-label="Play speed"><option value="1600">slow</option><option value="900" selected>medium</option><option value="350">fast</option></select></div>
<div class="prog"></div><div class="stage"></div><ol class="work"></ol>`;
    const q = s => el.querySelector(s);
    let steps = [], i = 0, timer = null;
    const stop = () => { if (timer) clearInterval(timer); timer = null; q('[data-a=play]').textContent = 'Play'; };
    const go = t => { i = Math.max(0, Math.min(steps.length - 1, t)); draw(); if (i === steps.length - 1) stop(); };
    function draw() {
      const st = steps[i];
      const v = opt.render(st, steps, i);
      q('.stage').innerHTML = v.stage;
      q('.work').innerHTML = st.lines.slice(0, st.sub + 1).map((t, k) => `<li class="${k === st.sub ? 'now' : ''}">${t}</li>`).join('');
      q('.prog').textContent = `${st.g} · step ${st.sub + 1} of ${st.lines.length} · (${i + 1}/${steps.length} overall)`;
      q('.simnote').innerHTML = v.note || '';
      q('[data-a=prev]').disabled = i === 0;
      q('[data-a=next]').disabled = q('[data-a=skip]').disabled = i === steps.length - 1;
      if (opt.phaseKey) q('[data-a=phase]').disabled = i === steps.length - 1;
    }
    el.addEventListener('click', e => {
      const a = e.target.closest('[data-a]')?.dataset.a;
      if (a === 'play') { if (timer) stop(); else { timer = setInterval(() => go(i + 1), Number(q('[data-a=speed]').value)); q('[data-a=play]').textContent = 'Pause'; } return; }
      if (['reset', 'prev', 'next', 'skip', 'phase'].includes(a)) stop();
      if (a === 'reset') go(0);
      if (a === 'prev') go(i - 1);
      if (a === 'next') go(i + 1);
      if (a === 'phase') { let t = i + 1; while (t < steps.length - 1 && steps[t][opt.phaseKey] === steps[i][opt.phaseKey]) t++; go(t); }
      if (a === 'skip') { let t = i + 1; while (t < steps.length - 1 && steps[t].g === steps[i].g) t++; go(t); }
      const td = e.target.closest('td[data-jump]');
      if (td && opt.jump) { stop(); const t = opt.jump(td.dataset.jump, steps, i); if (t >= 0) go(t); }
    });
    el.addEventListener('keydown', e => {
      if (e.target.tagName === 'SELECT' || e.target.tagName === 'INPUT') return;
      if (e.key === 'ArrowRight') { stop(); go(i + 1); e.preventDefault(); }
      if (e.key === 'ArrowLeft') { stop(); go(i - 1); e.preventDefault(); }
    });
    el.addEventListener('change', e => { if (e.target.dataset.opt) { stop(); rebuild(); } if (e.target.dataset.a === 'speed' && timer) { stop(); } });
    function rebuild(start = 0) { steps = opt.build(); i = Math.min(start, steps.length - 1); draw(); }
    return { rebuild, q };
  }
  const sel = (name, opts, value, label) => (opts.length < 2 ? '' :
    `<label>${label}<select data-opt="${name}">${opts.map(([v, t]) => `<option value="${v}"${v === value ? ' selected' : ''}>${t}</option>`).join('')}</select></label>`);

  /* ------------------------------------------------ 2-D filter simulator */
  function filterSim(el, cfg) {
    const imgs = cfg.images, fils = cfg.filters;
    const controls = sel('img', imgs.map(k => [k, DATA.images[k].name]), cfg.image || imgs[0], 'Image') +
      sel('fil', fils.map(k => [k, DATA.filters[k].name]), cfg.filter || fils[0], 'Filter') +
      `<label>Border<select data-opt="pad">${[['zero', 'zero padding'], ['replicate', 'replicate border'], ['discard', 'discard border']].map(([v, t]) => `<option value="${v}"${v === (cfg.pad || 'zero') ? ' selected' : ''}>${t}</option>`).join('')}</select></label>`;
    const P = player(el, {
      controls, skipLabel: 'Next pixel ⏭',
      build() {
        const ik = P.q('[data-opt=img]')?.value || imgs[0];
        const fk = P.q('[data-opt=fil]')?.value || fils[0];
        const pad = P.q('[data-opt=pad]').value;
        const img = DATA.images[ik].img, f = DATA.filters[fk], pos = K.positions(img, pad);
        const res = pos.map(([r, c]) => K.filter(img, r, c, f, pad));
        const steps = [];
        pos.forEach(([r, c], p) => {
          const R = res[p], lines = textFilter(img, r, c, f, pad, R, pos[p + 1]);
          lines.forEach((_, sub) => steps.push({ g: `Pixel (${r},${c})`, sub, lines, p, r, c, R, ctx: { img, f, pad, pos, res, ik } }));
        });
        return steps;
      },
      render: st => renderFilter(st),
      jump(key, steps) { const [r, c] = key.split(',').map(Number); return steps.findIndex(s => s.r === r && s.c === c && s.sub === 0); },
    });
    P.rebuild();
    if (cfg.start) el.querySelector(`td[data-jump="${cfg.start[0]},${cfg.start[1]}"]`)?.click(); // open on the pixel the slide uses
  }
  function textFilter(img, r, c, f, pad, R, nxt) {
    const rows3 = [0, 1, 2].map(a => R.z.slice(a * 3, a * 3 + 3).map(v => (v === null ? '·' : v)).join('  ')).join(' / ');
    const outside = R.win.filter(o => o.out).length;
    const padNote = outside === 0 ? 'All 9 are inside the image.'
      : pad === 'zero' ? `${outside} of them fall outside the image, so they count as 0 (zero padding).`
      : `${outside} of them fall outside the image, so they copy the nearest border pixel (replication).`;
    const L = [`<b>Place the window</b> with its centre on pixel (${r},${c}) = <b>${img[r][c]}</b>. The 9 values under it, row by row: <code>${rows3}</code>. ${padNote}`];
    const plist = (k, p) => `<div class="prodlist">${R.z.map((v, i) => `<span>${k[i]} × ${v} = <b>${p[i]}</b></span>`).join('')}</div>`;
    if (f.rank !== undefined) {
      L.push(`<b>Sort</b> the 9 values from smallest to largest: <code>${R.sorted.join(', ')}</code>.`);
      L.push(`<b>Pick</b> the ${f.rankName}: <code>${R.sorted.map((v, k) => (k === f.rank ? `<mark>${v}</mark>` : v)).join(', ')}</code> → <b>${R.result}</b>.`);
    } else if (f.kx) {
      L.push(`<b>Multiply</b> by both masks. With G<sub>x</sub>:${plist(f.kx, R.px)}With G<sub>y</sub>:${plist(f.ky, R.py)}`);
      L.push(`<b>Add</b> each set: G<sub>x</sub> = ${signed(R.px)} = <b>${R.gx}</b>; G<sub>y</sub> = ${signed(R.py)} = <b>${R.gy}</b>. Magnitude |G| = |G<sub>x</sub>| + |G<sub>y</sub>| = ${Math.abs(R.gx)} + ${Math.abs(R.gy)} = <b>${R.result}</b>.`);
    } else {
      L.push(`<b>Multiply</b> each value by the kernel weight on top of it:${plist(f.k, R.prods)}`);
      if (f.post) {
        L.push(`<b>Add</b> the 9 products: ${signed(R.prods)} = <b>${R.sum}</b> = ∇²f. The mask centre is ${f.post > 0 ? 'positive, so g = f + ∇²f' : 'negative, so g = f − ∇²f'} = ${R.z[4]} ${f.post > 0 ? '+' : '−'} (${R.sum}) = <b>${R.result}</b>.`);
      } else {
        L.push(`<b>Add</b> the 9 products: ${signed(R.prods)} = <b>${R.sum}</b>.` + (f.n === 1 ? ` No division (the weights are already the mask), so the result is <b>${R.result}</b>.` : ` Divide by ${f.n}: ${R.sum}/${f.n} = ${fmt(R.exact)} → rounded <b>${R.result}</b>.`));
      }
    }
    L.push(`<b>Write</b> ${R.result} into the output at (${r},${c}).` + (nxt ? ` Next, the window slides to (${nxt[0]},${nxt[1]}).` : ' That was the last pixel: the output image is complete.'));
    return L;
  }
  function renderFilter(st) {
    const { img, f, pad, pos, res, ik } = st.ctx, H = img.length, W = img[0].length, { r, c, R, sub, p } = st;
    const inRows = [];
    for (let i = -1; i <= H; i++) {
      const row = [];
      for (let j = -1; j <= W; j++) {
        const o = K.at(img, i, j, pad), win = Math.abs(i - r) <= 1 && Math.abs(j - c) <= 1;
        row.push({ v: o.v === null ? '·' : o.v, cls: `${o.out ? 'pad' : ''} ${win ? 'hi' : ''} ${i === r && j === c ? 'ctr' : ''}`, attr: o.out ? '' : ` data-jump="${i},${j}" title="Jump to (${i},${j})"` });
      }
      inRows.push(row);
    }
    let stage = fig(tbl(inRows), `input · dashed = ${pad === 'zero' ? 'zero padding' : pad === 'replicate' ? 'replicated border' : 'outside (not used)'} · click a pixel to jump`);
    const g3 = (k, cls) => tbl([0, 1, 2].map(a => [0, 1, 2].map(b => ({ v: k[a * 3 + b], cls }))));
    if (f.rank !== undefined) stage += `<div class="rule">${f.rule}</div>`;
    else if (f.kx) {
      stage += fig(g3(f.kx, sub === 1 ? 'hi' : ''), 'G<sub>x</sub> mask') + fig(g3(f.ky, sub === 1 ? 'hi' : ''), 'G<sub>y</sub> mask');
      if (sub >= 1) stage += fig(g3(R.px, 'hi'), 'G<sub>x</sub> products') + fig(g3(R.py, 'hi'), 'G<sub>y</sub> products');
    } else {
      stage += fig(g3(f.k, sub === 1 ? 'hi' : ''), f.n && f.n !== 1 ? `1/${f.n} × kernel` : 'kernel');
      if (sub >= 1) stage += fig(g3(R.prods, 'hi'), 'products');
    }
    const done = sub === 3 ? p : p - 1, out = Array.from({ length: H }, () => Array(W).fill(''));
    for (let k = 0; k <= done; k++) out[pos[k][0]][pos[k][1]] = res[k].result;
    const visited = new Set(pos.map(([a, b]) => a + ',' + b));
    stage += fig(tbl(out.map((row, a) => row.map((v, b) => (visited.has(a + ',' + b) ? { v, cls: a === r && b === c ? (sub === 3 ? 'ctr new' : 'ctr') : '' } : { v: '·', cls: 'pad' })))),
      'output' + (pad === 'discard' ? ' · dotted = not computed (write 0 if the question says so)' : ''));
    return { stage, note: DATA.images[ik].note || '' };
  }

  /* ------------------------------------------------ 1-D simulator (derivatives, unsharp masking) */
  function oneDSim(el, cfg) {
    const modes = cfg.modes, names = { d1: '1st derivative f(x+1) − f(x)', d2: '2nd derivative f(x+1) + f(x−1) − 2f(x)', unsharp: 'Unsharp masking' };
    const P = player(el, {
      controls: sel('mode', modes.map(m => [m, names[m]]), modes[0], 'Operation'), skipLabel: 'Next position ⏭',
      build() {
        const mode = P ? (P.q('[data-opt=mode]')?.value || modes[0]) : modes[0], sig = cfg.sig, xs = K.oneDPositions(sig, mode);
        const res = xs.map(x => K.oneD(sig, x, mode)), steps = [];
        xs.forEach((x, p) => {
          const R = res[p], nx = xs[p + 1];
          let L;
          if (mode === 'unsharp') L = [
            `<b>Place</b> the 3-pixel window on x = ${x}: f(x−1) = ${R.a}, f(x) = <b>${R.b}</b>, f(x+1) = ${R.c}${x === 0 || x === sig.length - 1 ? ' (the end pixel is repeated outside the signal)' : ''}.`,
            `<b>Blur</b>: average of the 3 values = (${R.a} + ${R.b} + ${R.c})/3 = ${fmt((R.a + R.b + R.c) / 3)} → <b>${R.blur}</b>.`,
            `<b>Unsharp mask</b> = original − blurred = ${R.b} − ${R.blur} = <b>${R.mask}</b>.`,
            `<b>Sharpened</b> g = original + mask = ${R.b} + (${R.mask}) = <b>${R.result}</b>. Write it.` + (nx !== undefined ? ` Next x = ${nx}.` : ' Done.')];
          else if (mode === 'd1') L = [
            `<b>Place</b> at x = ${x}: f(x) = <b>${R.b}</b>, f(x+1) = ${R.c}.`,
            `<b>Multiply</b> by the forward kernel [0 −1 1]: 0×${R.a} + (−1)×${R.b} + 1×${R.c}.`,
            `<b>Add</b>: ${R.c} − ${R.b} = <b>${R.result}</b>.`,
            `<b>Write</b> ${R.result} under x = ${x}.` + (nx !== undefined ? ` Next x = ${nx}.` : ' Done.')];
          else L = [
            `<b>Place</b> at x = ${x}: f(x−1) = ${R.a}, f(x) = <b>${R.b}</b>, f(x+1) = ${R.c}.`,
            `<b>Multiply</b> by the kernel [1 −2 1]: 1×${R.a} + (−2)×${R.b} + 1×${R.c}.`,
            `<b>Add</b>: ${R.a} − ${2 * R.b} + ${R.c} = <b>${R.result}</b>.`,
            `<b>Write</b> ${R.result} under x = ${x}.` + (nx !== undefined ? ` Next x = ${nx}.` : ' Done.')];
          L.forEach((_, sub) => steps.push({ g: `x = ${x}`, sub, lines: L, p, x, ctx: { mode, sig, xs, res } }));
        });
        return steps;
      },
      render(st) {
        const { mode, sig, xs, res } = st.ctx, done = st.sub === 3 ? st.p : st.p - 1;
        const row = key => sig.map((_, i) => { const p = xs.indexOf(i); return p >= 0 && p <= done ? res[p][key] : null; });
        const cell = (v, i) => ({ v: v === null ? '' : v, cls: i === st.x ? 'ctr' : Math.abs(i - st.x) <= 1 ? 'hi' : '' });
        let rows = [['x', ...sig.map((_, i) => i)], ['f(x)', ...sig.map((v, i) => cell(v, i))]];
        let series = [{ v: sig, cls: 'c5' }];
        if (mode === 'unsharp') {
          const bl = row('blur'), mk = row('mask'), g = row('result');
          rows.push(['blurred', ...bl.map(cell)], ['mask', ...mk.map(cell)], ['sharpened', ...g.map(cell)]);
          series.push({ v: bl, cls: 'c1' }, { v: g, cls: 'c3' });
          return { stage: fig(tbl(rows), 'f = original; rows fill in as the window moves', 'mat sm wide1') + lines1(series, { lo: -10, hi: 110, cur: st.x, cap: 'gray: original · blue: blurred · orange: sharpened' }) };
        }
        const d = row('result');
        rows.push([mode === 'd1' ? '1st' : '2nd', ...d.map(cell)]);
        return { stage: fig(tbl(rows), 'image strip and its derivative', 'mat sm wide1') + lines1([{ v: sig, cls: 'c5' }, { v: d, cls: mode === 'd1' ? 'c1' : 'c3' }], { lo: mode === 'd1' ? -7 : -13, hi: 8, cur: st.x, cap: 'gray: strip f(x) · colour: derivative so far' }) };
      },
    });
    P.rebuild();
  }

  /* ------------------------------------------------ histogram equalization simulator */
  function heSim(el, cfg) {
    const img = cfg.img, L = cfg.L, dp = cfg.dp || 4, phases = cfg.phases || ['count', 'table', 'eqhist', 'output'];
    const n = cfg.counts || (() => { const h = Array(L).fill(0); img.flat().forEach(v => h[v]++); return h; })();
    const E = K.equalize(n, dp), eh = K.eqHist(n, E.s), N = E.N, nz = n.map((v, r) => (v ? r : -1)).filter(r => r >= 0);
    const pdfS = r => (dp === 2 ? (E.unit[r] / 100).toFixed(2) : (n[r] / N).toFixed(4));
    const cdfS = r => (dp === 2 ? (E.cum[r] / 100).toFixed(2) : (E.cum[r] / N).toFixed(4));
    const scS = r => (dp === 2 ? (((L - 1) * E.cum[r]) / 100).toFixed(2) : (((L - 1) * E.cum[r]) / N).toFixed(4));
    const steps = [];
    const push = (g, lines, extra) => lines.forEach((_, sub) => steps.push({ g, sub, lines, ...extra }));
    if (phases.includes('count')) {
      const lv = L <= 16 ? [...Array(L).keys()] : nz;
      lv.forEach(r => push(`Histogram: level ${r}`, [`<b>Count</b> the pixels whose value is ${r} (highlighted): h(${r}) = n<sub>${r}</sub> = <b>${n[r]}</b>.` + (n[r] === 0 ? ' None, so its bar is 0.' : '')], { ph: 'count', r }));
      if (L > 16) push('Histogram: other levels', [`Every other level from 0 to ${L - 1} has <b>0</b> pixels. Check: ${nz.map(r => n[r]).join(' + ')} = ${N} = N.`], { ph: 'count', r: L });
    }
    if (phases.includes('pdf')) {
      (L <= 16 ? [...Array(L).keys()] : nz).forEach(r => push(`Normalized: level ${r}`, [`<b>Divide</b> by the total: p(${r}) = n<sub>${r}</sub>/N = ${n[r]}/${N} = <b>${(n[r] / N).toFixed(4)}</b>.`], { ph: 'pdf', r }));
    }
    if (phases.includes('table')) {
      nz.forEach((r, k) => {
        const prev = k ? cdfS(nz[k - 1]) : '0';
        push(`Table row r = ${r}`, [
          `<b>Step 2, PDF:</b> p(${r}) = n/N = ${n[r]}/${N} = <b>${pdfS(r)}</b>${dp === 2 ? ' (rounded to 2 places, as on slide 49)' : ''}.`,
          `<b>Step 3, CDF:</b> add it to the running total: ${prev} + ${pdfS(r)} = <b>${cdfS(r)}</b>${dp === 2 && r === L - 1 ? ' (the last CDF is 1 by definition)' : ''}.`,
          `<b>Step 4:</b> (L − 1) × CDF = ${L - 1} × ${cdfS(r)} = <b>${scS(r)}</b>.`,
          `<b>Step 5, round</b> (.5 goes up): ${scS(r)} → <b>s = ${E.s[r]}</b>. So every pixel with value ${r} will become ${E.s[r]}.`], { ph: 'table', r, k });
      });
    }
    if (phases.includes('eqhist')) {
      const acc = Array(L).fill(0);
      nz.forEach(r => {
        acc[E.s[r]] += n[r];
        push(`Equalized histogram: r = ${r}`, [`<b>Move</b> the ${n[r]} pixel${n[r] > 1 ? 's' : ''} of level ${r} to the new level ${E.s[r]}: bin ${E.s[r]} now holds <b>${acc[E.s[r]]}</b>${acc[E.s[r]] > n[r] ? ` (it already had ${acc[E.s[r]] - n[r]})` : ''}.`], { ph: 'eqhist', r, acc: acc.slice() });
      });
    }
    if (phases.includes('output') && img) {
      img.forEach((row, a) => row.forEach((v, b) => push(`Output pixel (${a},${b})`, [`<b>Replace</b> pixel (${a},${b}): r = ${v} → s = <b>${E.s[v]}</b> (from the table).`], { ph: 'out', a, b })));
    }
    steps.forEach((s, i) => (s.i = i));
    player(el, {
      skipLabel: 'Next stage ⏭',
      build: () => steps,
      render(st) {
        const ph = st.ph, order = ['count', 'pdf', 'table', 'eqhist', 'out'], at = order.indexOf(ph);
        let stage = '';
        if (img) {
          const outDone = ph === 'out' ? st.a * img[0].length + st.b : -1;
          stage += fig(tbl(img.map((row, a) => row.map((v, b) => ({ v, cls: (ph === 'count' && v === st.r) || (ph === 'out' && a === st.a && b === st.b) ? 'hi ctr' : '' })))), `input image (N = ${N})`);
          if (ph === 'out') stage += fig(tbl(img.map((row, a) => row.map((v, b) => ({ v: a * row.length + b <= outDone ? E.s[v] : '', cls: a === st.a && b === st.b ? 'new' : '' })))), 'equalized output image');
        }
        const shown = ph === 'count' ? n.map((v, r) => (r <= st.r ? v : null)) : n;
        stage += bars(shown, { hi: ph === 'count' ? st.r : -1, cap: 'original histogram n<sub>k</sub>' });
        if (ph === 'pdf') stage += bars(n.map((v, r) => (r <= st.r ? v / N : null)), { hi: st.r, color: 'c2', fmtv: v => v.toFixed(2), cap: 'normalized histogram p(r<sub>k</sub>)' });
        if (at >= 2 && phases.includes('table')) {
          const doneRow = ph === 'table' ? st.k : nz.length - 1;
          const head = ['r<sub>k</sub>', 'n<sub>k</sub>', 'PDF', 'CDF', `${L - 1}×CDF`, 's<sub>k</sub>'];
          const body = nz.map((r, k) => {
            if (k > doneRow) return [r, n[r], '', '', '', ''];
            const upto = k < doneRow ? 3 : ph === 'table' ? st.sub : 3, cell = (v, j) => ({ v: j <= upto ? v : '', cls: ph === 'table' && k === doneRow && j === upto ? 'hi ctr' : '' });
            return [r, n[r], cell(pdfS(r), 0), cell(cdfS(r), 1), cell(scS(r), 2), cell(E.s[r], 3)];
          });
          stage += fig(`<table><tr>${head.map(h => `<td class="pad"><b>${h}</b></td>`).join('')}</tr>${body.map(r => `<tr>${r.map(c => (typeof c === 'object' ? `<td class="${c.cls}">${c.v}</td>` : `<td>${c}</td>`)).join('')}</tr>`).join('')}</table>`, 'equalization table (non-zero levels)');
          const known = ph === 'table' ? (st.sub === 3 ? st.k : st.k - 1) : nz.length - 1;
          const sk = n.map(() => null);
          for (let r = 0; r < L; r++) { const lastNz = nz.filter(x => x <= r).pop(); const kk = nz.indexOf(lastNz); if (lastNz === undefined) { if (known >= 0) sk[r] = 0; } else if (kk <= known) sk[r] = E.s[r]; }
          stage += stairs(sk, { hi: ph === 'table' ? st.r : -1, cap: 'transformation function (staircase)' });
        }
        if (ph === 'eqhist' || ph === 'out') stage += bars(ph === 'eqhist' ? st.acc.map(v => v || null) : eh, { hi: ph === 'eqhist' ? E.s[st.r] : -1, color: 'c3', cap: 'equalized histogram' });
        return { stage };
      },
    }).rebuild();
  }

  /* ------------------------------------------------ histogram specification simulator */
  function hsSim(el, cfg) {
    const n = cfg.counts, L = n.length, dp = cfg.dp || 2;
    const E = K.equalize(n, dp), SP = K.specEqualize(cfg.spec, L, dp, !!cfg.specCounts), H = E.s, S = SP.s, zmap = K.matchMap(H, S);
    const steps = [], push = (g, lines, extra) => lines.forEach((_, sub) => steps.push({ g, sub, lines, ...extra }));
    const f = (num, den, d) => (num / den).toFixed(d);
    for (let r = 0; r < L; r++) {
      const p = dp === 2 ? f(E.unit[r], 100, 2) : f(n[r], E.N, 4), c = dp === 2 ? f(E.cum[r], 100, 2) : f(E.cum[r], E.N, 4);
      const sc = dp === 2 ? f((L - 1) * E.cum[r], 100, 2) : f((L - 1) * E.cum[r], E.N, 4);
      push(`Step 1 (equalize input): r = ${r}`, [`PDF = ${n[r]}/${E.N} = <b>${p}</b>.`, `CDF = <b>${c}</b>.`, `(L−1)·CDF = ${L - 1} × ${c} = <b>${sc}</b>.`, `Round → <b>H<sub>${r}</sub> = ${H[r]}</b>.`], { ph: 1, r });
    }
    for (let z = 0; z < L; z++) {
      const p = f(SP.unit[z], SP.D, 2), c = f(SP.cum[z], SP.D, 2), sc = f((L - 1) * SP.cum[z], SP.D, 2);
      push(`Step 2 (equalize target): z = ${z}`, [`p<sub>z</sub>(${z}) = <b>${p}</b>${cfg.specCounts ? ` (${cfg.spec[z]}/${SP.N})` : ''}.`, `CDF = <b>${c}</b>.`, `(L−1)·CDF = <b>${sc}</b>.`, `Round → <b>S<sub>${z}</sub> = ${S[z]}</b>.`], { ph: 2, z });
    }
    const acc = Array(L).fill(0);
    for (let r = 0; r < L; r++) {
      const d = S.map(x => Math.abs(x - H[r])), m = Math.min(...d), ties = [...new Set(S.filter(x => Math.abs(x - H[r]) === m))];
      acc[zmap[r]] += n[r];
      push(`Step 3 (relate): r = ${r}`, [
        `H<sub>${r}</sub> = <b>${H[r]}</b>. Distance to every S: ${S.map((x, z) => `z${z}: |${x} − ${H[r]}| = ${d[z]}`).join(', ')}.`,
        `Smallest distance ${m}${ties.length > 1 ? ` is shared by S = ${ties.join(' and ')}; take the higher, ${S[zmap[r]]}` : ` at S = ${S[zmap[r]]}`}. The first z with S = ${S[zmap[r]]} is <b>z = ${zmap[r]}</b>, so r = ${r} → <b>${zmap[r]}</b>.`,
        `<b>Move</b> its ${n[r]} pixels to z = ${zmap[r]}: bin ${zmap[r]} now holds <b>${acc[zmap[r]]}</b>.`], { ph: 3, r, acc: acc.slice() });
    }
    player(el, {
      skipLabel: 'Next level ⏭',
      build: () => steps,
      render(st) {
        const rowIn = (r) => st.ph > 1 || (st.ph === 1 && r < st.r) ? 3 : st.ph === 1 && r === st.r ? st.sub : -1;
        const vIn = r => [dp === 2 ? f(E.unit[r], 100, 2) : f(n[r], E.N, 4), dp === 2 ? f(E.cum[r], 100, 2) : f(E.cum[r], E.N, 4), dp === 2 ? f((L - 1) * E.cum[r], 100, 2) : f((L - 1) * E.cum[r], E.N, 4), H[r]];
        const t1 = `<table><tr>${['r', 'n', 'PDF', 'CDF', '(L−1)CDF', 'H'].map(h => `<td class="pad"><b>${h}</b></td>`).join('')}</tr>${n.map((v, r) => `<tr><td>${r}</td><td>${v}</td>${vIn(r).map((x, j) => `<td class="${st.ph === 1 && r === st.r && j === st.sub ? 'hi ctr' : st.ph === 3 && r === st.r && j === 3 ? 'hi' : ''}">${j <= rowIn(r) ? x : ''}</td>`).join('')}</tr>`).join('')}</table>`;
        const rowS = z => st.ph > 2 || (st.ph === 2 && z < st.z) ? 3 : st.ph === 2 && z === st.z ? st.sub : -1;
        const vS = z => [f(SP.unit[z], SP.D, 2), f(SP.cum[z], SP.D, 2), f((L - 1) * SP.cum[z], SP.D, 2), S[z]];
        const t2 = `<table><tr>${['z', 'p<sub>z</sub>', 'CDF', '(L−1)CDF', 'S'].map(h => `<td class="pad"><b>${h}</b></td>`).join('')}</tr>${S.map((_, z) => `<tr><td>${z}</td>${vS(z).map((x, j) => `<td class="${st.ph === 2 && z === st.z && j === st.sub ? 'hi ctr' : st.ph === 3 && z === zmap[st.r] && j === 3 && st.sub >= 1 ? 'hi ctr' : ''}">${j <= rowS(z) ? x : ''}</td>`).join('')}</tr>`).join('')}</table>`;
        let stage = fig(t1, 'Step 1: equalize the original') + fig(t2, 'Step 2: equalize the specified');
        if (st.ph === 3) {
          const t3 = `<table><tr>${['r', 'H', '→ z'].map(h => `<td class="pad"><b>${h}</b></td>`).join('')}</tr>${n.map((_, r) => `<tr><td>${r}</td><td>${r <= st.r ? H[r] : ''}</td><td class="${r === st.r ? 'hi ctr' : ''}">${r < st.r || (r === st.r && st.sub >= 1) ? zmap[r] : ''}</td></tr>`).join('')}</table>`;
          const shown = st.sub === 2 ? st.acc : st.acc.map((v, z) => (z === zmap[st.r] ? v - n[st.r] : v));
          stage += fig(t3, 'Step 3: mapping') + bars(n, { cap: 'original histogram' }) + bars(shown.map(v => v || null), { hi: st.sub === 2 ? zmap[st.r] : -1, color: 'c3', cap: 'output histogram (filling)' });
        }
        return { stage };
      },
    }).rebuild();
  }

  /* ------------------------------------------------ Huffman simulator */
  const trim = (x, d = 4) => String(Number(x.toFixed(d)));
  function huffSim(el, cfg) {
    const R = K.huffman(cfg.syms, cfg.w), D = cfg.D || R.W, merges = R.merges, last = R.lists[R.lists.length - 1];
    const p = n => (cfg.asCount ? `${n.w}/${D}` : trim(n.w / D));
    const col = j => (j === 0 ? 'the original column' : `reduction ${j}`);
    // when each node's code becomes known: final pair at assign step 0, kids of merge k at step merges.length − k
    const known = new Map();
    last.forEach(n => known.set(n.id, 0));
    merges.forEach((m, k) => { known.set(m.a.id, merges.length - k); known.set(m.b.id, merges.length - k); });
    const steps = [], push = (g, lines, x) => lines.forEach((_, sub) => steps.push({ g, sub, lines, ...x }));
    push('Sort', [`List every symbol with its probability and <b>sort</b> them largest first: ${R.lists[0].map(n => `${n.sym} = ${p(n)}`).join(', ')}.`], { ph: 'sort' });
    merges.forEach((m, k) => {
      const ties = R.lists[k + 1].filter(n => n !== m.node && n.w === m.node.w);
      push(`Reduction ${k + 1}`, [
        `Take the <b>two smallest</b> at the bottom of ${col(k)}: ${p(m.a)} and ${p(m.b)}.`,
        `<b>Add</b> them: ${p(m.a)} + ${p(m.b)} = <b>${p(m.node)}</b>.`,
        `<b>Re-sort</b> into ${col(k + 1)}: ${p(m.node)} goes in position ${m.pos + 1}` + (ties.length ? `. It ties with ${ties.map(p).join(', ')}, so it goes <b>below</b> the equal value (slide rule)` : '') + '. The other values are copied across unchanged.'], { ph: 'red', k });
    });
    push('Codes: last column', [`The last column has two values, ${p(last[0])} and ${p(last[1])}. Give the upper one <b>0</b> and the lower one <b>1</b>.`], { ph: 'asg', t: 0 });
    for (let k = merges.length - 1; k >= 0; k--) {
      const m = merges[k];
      push(`Codes: back to ${col(k)}`, [
        `In ${col(k + 1)}, ${p(m.node)} has code <b>${m.node.code}</b>. It was made by adding ${p(m.a)} + ${p(m.b)} in ${col(k)}.`,
        `Pass the code back and add one bit: upper ${p(m.a)} gets ${m.node.code}<b>0</b> = <b>${m.a.code}</b>, lower ${p(m.b)} gets ${m.node.code}<b>1</b> = <b>${m.b.code}</b>. Every other value keeps the code it had in the column to its right.`], { ph: 'asg', t: merges.length - k, k });
    }
    const terms = R.leaves.map(n => `(${p(n)})(${n.code.length})`).join(' + ');
    const res = [`<b>Average code length</b> L<sub>avg</sub> = Σ p·l = ${terms} = <b>${trim(R.lavg)}</b> bits/symbol.`,
      `<b>Entropy</b> H = −Σ p log<sub>2</sub> p = ${R.leaves.filter(n => n.w).map(n => `−(${p(n)})log<sub>2</sub>(${p(n)})`).join(' + ')} = <b>${trim(R.H)}</b> bits/symbol. Efficiency = H / L<sub>avg</sub> = ${trim(R.H)} / ${trim(R.lavg)} = <b>${trim((100 * R.H) / R.lavg, 2)}%</b>.`];
    if (cfg.bits) {
      const C = cfg.bits / R.lavg;
      res.push(`<b>Compression ratio</b> C = n<sub>1</sub>/n<sub>2</sub> = ${cfg.bits} / ${trim(R.lavg)} = <b>${trim(C)}</b>. <b>Relative redundancy</b> R<sub>D</sub> = 1 − 1/C = <b>${trim(1 - 1 / C)}</b>, so ${trim(100 * (1 - 1 / C), 2)}% of the data was redundant.`);
    }
    push('Results', res, { ph: 'res' });
    player(el, {
      skipLabel: 'Next stage ⏭', build: () => steps,
      render(st) {
        const nCols = st.ph === 'sort' ? 1 : st.ph === 'red' ? st.k + 1 + (st.sub === 2 ? 1 : 0) : R.lists.length;
        const t = st.ph === 'asg' ? st.t + (st.t === 0 || st.sub === 1 ? 0 : -1) : st.ph === 'res' ? 1e9 : -1;
        const showCode = n => known.has(n.id) && known.get(n.id) <= t;
        const hi = new Set();
        if (st.ph === 'red') { const m = merges[st.k]; hi.add(`${st.k}:${m.a.id}`); hi.add(`${st.k}:${m.b.id}`); if (st.sub >= 1) hi.add(`${st.k + 1}:${m.node.id}`); }
        if (st.ph === 'asg') {
          if (st.t === 0) last.forEach(n => hi.add(`${R.lists.length - 1}:${n.id}`));
          else { const m = merges[st.k]; hi.add(`${st.k + 1}:${m.node.id}`); if (st.sub === 1) { hi.add(`${st.k}:${m.a.id}`); hi.add(`${st.k}:${m.b.id}`); } }
        }
        let h = '<table><tr><td class="pad"><b>Symbol</b></td><td class="pad"><b>Prob.</b></td><td class="pad"><b>Code</b></td>';
        for (let j = 1; j < R.lists.length; j++) h += `<td class="pad"><b>${j}</b></td>`;
        h += '</tr>';
        R.lists[0].forEach((_, i) => {
          h += '<tr>';
          const n0 = R.lists[0][i], c0 = hi.has(`0:${n0.id}`) ? 'hi ctr' : '';
          h += `<td>${n0.sym}</td><td class="${c0}">${p(n0)}</td><td class="${c0}">${showCode(n0) ? n0.code : ''}</td>`;
          for (let j = 1; j < R.lists.length; j++) {
            const n = R.lists[j][i];
            if (!n || j >= nCols) { h += '<td></td>'; continue; }
            h += `<td class="${hi.has(`${j}:${n.id}`) ? 'hi ctr' : ''}">${p(n)}${showCode(n) ? ` <b>${n.code}</b>` : ''}</td>`;
          }
          h += '</tr>';
        });
        let stage = fig(h + '</table>', 'source reduction (columns 1, 2, … are the reductions); codes fill in from the right');
        if (st.ph === 'res') stage += fig(tbl([[{ v: '<b>Symbol</b>', cls: 'pad' }, { v: '<b>p</b>', cls: 'pad' }, { v: '<b>Code</b>', cls: 'pad' }, { v: '<b>Length</b>', cls: 'pad' }],
          ...R.leaves.map(n => [n.sym, p(n), n.code, n.code.length])]), 'final Huffman code');
        return { stage };
      },
    }).rebuild();
  }

  /* ------------------------------------------------ LZW simulator */
  function lzwSim(el, cfg) {
    const img = cfg.img, W = img[0].length, seq = img.flat(), Z = K.lzw(seq), bits = cfg.bits || 9;
    const steps = [], push = (g, lines, x) => lines.forEach((_, sub) => steps.push({ g, sub, lines, ...x }));
    Z.rows.forEach((r, k) => {
      if (r.final) {
        push('End', [`No pixels are left. Output the code of the currently recognized sequence ${r.crs}: <b>${r.code}</b>.`,
          `Encoded output: <b>${Z.out.join(' ')}</b> (${Z.out.length} codes). Original = ${seq.length} pixels × 8 bits = <b>${seq.length * 8}</b> bits. Encoded = ${Z.out.length} codes × ${bits} bits = <b>${Z.out.length * bits}</b> bits. C<sub>R</sub> = ${seq.length * 8}/${Z.out.length * bits} = <b>${trim((seq.length * 8) / (Z.out.length * bits))}</b>.`], { k, r });
        return;
      }
      const single = !r.cand.includes('-');
      push(`Pixel ${r.i + 1} = ${r.px}`, [
        `<b>Read</b> the next pixel: <b>${r.px}</b>. The currently recognized sequence is ${r.crs || '(empty)'}, so test <b>${r.cand}</b>.`,
        r.hit ? `${r.cand} <b>is</b> in the dictionary (${single ? 'locations 0–255 already hold every single gray level' : 'location ' + Z.dic.get(r.cand)}). It becomes the currently recognized sequence. Nothing is output.`
          : `${r.cand} is <b>not</b> in the dictionary. Output the code of ${r.crs}: <b>${r.code}</b>. Add ${r.cand} to the dictionary at location <b>${r.loc}</b>. The currently recognized sequence restarts as ${r.px}.`], { k, r });
    });
    player(el, {
      skipLabel: 'Next pixel ⏭', build: () => steps,
      render(st) {
        const cur = st.r.final ? seq.length : st.r.i;
        let stage = fig(tbl(img.map((row, a) => row.map((v, b) => { const i = a * W + b; return { v, cls: i === cur ? 'hi ctr' : i > cur ? 'pad' : '' }; }))), 'image, read left to right, top to bottom');
        const shown = Z.rows.slice(0, st.k + 1);
        const body = shown.map((r, j) => {
          const full = j < st.k || st.sub === 1;
          return [r.crs, r.final ? '' : r.px, full && r.code !== undefined ? r.code : '', full && r.loc ? r.loc : '', full && r.loc ? r.cand : ''].map((v, c) => ({ v, cls: j === st.k && (c < 2 || st.sub === 1) ? 'hi' : '' }));
        });
        stage += fig(tbl([['Currently recognized sequence', 'Pixel being processed', 'Encoded output', 'Dictionary location', 'Dictionary entry'].map(v => ({ v: `<b>${v}</b>`, cls: 'pad' })), ...body]), 'LZW encoding table (as on the slides)');
        return { stage };
      },
    }).rebuild();
  }

  /* ------------------------------------------------ arithmetic coding simulator */
  function arithSim(el, cfg) {
    const A = K.arith(cfg.probs, cfg.msg), S = cfg.syms, dec = K.dec;
    const steps = [], push = (g, lines, x) => lines.forEach((_, sub) => steps.push({ g, sub, lines, ...x }));
    push('Sub-intervals', [`Divide [0, 1) in the given symbol order, each symbol getting a width equal to its probability: ${S.map((s, i) => `${s} [${dec(A.lo[i], A.one)}, ${dec(A.hi[i], A.one)})`).join(', ')}.`], { k: -1 });
    A.steps.forEach((x, k) => {
      const L = dec(x.L, x.scale), H = dec(x.Hh, x.scale), w = dec(x.Hh - x.L, x.scale), a = dec(A.lo[x.s], A.one), b = dec(A.hi[x.s], A.one);
      push(`Symbol ${k + 1}: ${S[x.s]}`, [
        `Current interval [${L}, ${H}). Its width is ${H} − ${L} = <b>${w}</b>.`,
        `${S[x.s]} owns [${a}, ${b}) of any interval. New low = ${L} + ${w} × ${a} = <b>${dec(x.nL, x.nscale)}</b>. New high = ${L} + ${w} × ${b} = <b>${dec(x.nH, x.nscale)}</b>.`], { k });
    });
    push('Code word', [`After the last symbol the interval is [<b>${dec(A.L, A.scale)}</b>, <b>${dec(A.Hh, A.scale)}</b>). Any number inside it encodes the whole message.`,
      `Shortest decimal inside the interval: <b>${dec(A.q, A.scale)}</b>. That single number is the arithmetic code for ${cfg.msg.map(i => S[i]).join('')}.`], { k: A.steps.length });
    player(el, {
      skipLabel: 'Next symbol ⏭', build: () => steps,
      render(st) {
        const w = 340, rowH = 46, rows = st.k < 0 ? 1 : st.k >= A.steps.length ? A.steps.length + 1 : st.k + 1 + (st.sub === 1 ? 1 : 0), Hs = rows * rowH + 14, x0 = 14, x1 = w - 14;
        let o = `<svg viewBox="0 0 ${w} ${Hs}" class="plot" role="img">`;
        for (let r = 0; r < rows; r++) {
          const y = 8 + r * rowH, x = r === 0 ? { L: 0n, Hh: 1n, scale: 1n } : A.steps[r - 1], nx = A.steps[r];
          const L = r === 0 ? '0' : dec(A.steps[r - 1].nL, A.steps[r - 1].nscale), H = r === 0 ? '1' : dec(A.steps[r - 1].nH, A.steps[r - 1].nscale);
          let acc = 0;
          cfg.probs.forEach((pp, i) => {
            const a = x0 + (x1 - x0) * acc; acc += Number(pp); const b = x0 + (x1 - x0) * acc;
            const on = nx && nx.s === i && (r < st.k || (r === st.k && st.sub === 1) || st.k >= A.steps.length);
            o += `<rect x="${a.toFixed(1)}" y="${y}" width="${(b - a).toFixed(1)}" height="18" class="${on ? 'barhi' : 'bar c1'}" opacity="${on ? 1 : 0.35}"/><text x="${((a + b) / 2).toFixed(1)}" y="${y + 13}" class="bval" text-anchor="middle">${S[i]}</text>`;
          });
          o += `<text x="${x0}" y="${y + 32}" class="tick">${L}</text><text x="${x1}" y="${y + 32}" class="tick" text-anchor="end">${H}</text>`;
        }
        o += '</svg>';
        let stage = fig(tbl([[{ v: '<b>Symbol</b>', cls: 'pad' }, { v: '<b>Prob.</b>', cls: 'pad' }, { v: '<b>Sub-interval</b>', cls: 'pad' }], ...S.map((s, i) => [s, cfg.probs[i], `[${dec(A.lo[i], A.one)}, ${dec(A.hi[i], A.one)})`])]), 'initial sub-intervals');
        stage += fig(o, 'each bar is the current interval stretched to full width; orange = the part the next symbol keeps', 'fig');
        return { stage };
      },
    }).rebuild();
  }

  /* ------------------------------------------------ run-length simulator */
  function rleSim(el, cfg) {
    const img = cfg.img, bits = cfg.bits, runs = img.map(K.rle), steps = [], push = (g, lines, x) => lines.forEach((_, sub) => steps.push({ g, sub, lines, ...x }));
    runs.forEach((rr, r) => rr.forEach((run, k) => push(`Row ${r + 1}, run ${k + 1}`, [
      `Start at column ${run.c} of row ${r + 1}: the value is <b>${run.v}</b>. Count how many equal values sit next to each other: <b>${run.n}</b>.`,
      `Write the pair (<b>${run.v}, ${run.n}</b>).` + (k === rr.length - 1 ? ` Row ${r + 1} is finished.` : '')], { r, k })));
    const pairs = runs.reduce((t, rr) => t + rr.length, 0), N = img.length * img[0].length;
    const fin = [`Count the pairs: ${runs.map(rr => rr.length).join(' + ')} = <b>${pairs}</b> pairs = ${2 * pairs} numbers.`];
    if (bits) fin.push(`Original = ${img.length}×${img[0].length}×${bits} = <b>${N * bits}</b> bits. RLE = ${2 * pairs} numbers × ${bits} bits = <b>${2 * pairs * bits}</b> bits. C<sub>R</sub> = ${N * bits}/${2 * pairs * bits} = <b>${trim((N * bits) / (2 * pairs * bits))}</b>${N < 2 * pairs ? ' (below 1: the file got bigger)' : ''}.`);
    push('Total', fin, { r: img.length });
    player(el, {
      skipLabel: 'Next run ⏭', build: () => steps,
      render(st) {
        let stage = fig(tbl(img.map((row, a) => row.map((v, b) => {
          const run = a === st.r ? runs[a][st.k] : null, inRun = run && b >= run.c && b < run.c + (st.sub >= 0 ? run.n : 0);
          const done = a < st.r || (a === st.r && run && b < run.c);
          return { v, cls: inRun ? 'hi ctr' : done ? '' : 'pad' };
        }))), 'image, scanned row by row');
        stage += fig(tbl(runs.map((rr, a) => [{ v: `<b>Row ${a + 1}</b>`, cls: 'pad' }, rr.filter((_, k) => a < st.r || (a === st.r && (k < st.k || (k === st.k && st.sub === 1)))).map(x => `(${x.v},${x.n})`).join(' ')])), 'run-length pairs (value, run)');
        return { stage };
      },
    }).rebuild();
  }

  /* ------------------------------------------------ Golomb simulator */
  function golSim(el, cfg) {
    const opts = (a, b) => Array.from({ length: b - a + 1 }, (_, i) => [String(a + i), String(a + i)]);
    const P = player(el, {
      controls: sel('n', opts(0, 20), String(cfg.n), 'n') + sel('m', opts(1, 8), String(cfg.m), 'm'), skipLabel: 'Skip ⏭',
      build() {
        const n = Number(P.q('[data-opt=n]').value), m = Number(P.q('[data-opt=m]').value), G = K.golomb(n, m);
        const lines = [
          `<b>Step 1, quotient.</b> q = ⌊n/m⌋ = ⌊${n}/${m}⌋ = ${G.q}. Unary code of q = q ones then a 0 = <b>${G.unary}</b>.`,
          `<b>Step 2, setup.</b> k = ⌈log<sub>2</sub> m⌉ = ⌈log<sub>2</sub> ${m}⌉ = ${G.k}; c = 2<sup>k</sup> − m = ${2 ** G.k} − ${m} = ${G.c}; r = n mod m = ${n} mod ${m} = ${G.r}.`,
          G.k === 0 ? `<b>Truncated remainder.</b> k = 0, so the remainder part is empty (m = 1 always gives r = 0).`
            : G.trunc ? `<b>Truncated remainder.</b> r = ${G.r} &lt; c = ${G.c}, so write r in k − 1 = ${G.k - 1} bit${G.k - 1 === 1 ? '' : 's'}: <b>${G.rb || '(empty)'}</b>.`
            : `<b>Truncated remainder.</b> r = ${G.r} ≥ c = ${G.c}, so write r + c = ${G.r + G.c} in k = ${G.k} bit${G.k === 1 ? '' : 's'}: <b>${G.rb}</b>.`,
          `<b>Step 3, concatenate</b> unary + remainder: ${G.unary} + ${G.rb || '(nothing)'} = <b>G<sub>${m}</sub>(${n}) = ${G.code}</b>.`];
        return lines.map((_, sub) => ({ g: `G${m}(${n})`, sub, lines, G, n, m }));
      },
      render(st) {
        const G = st.G, cells = [['q', G.q], ['unary', G.unary], ['k', G.k], ['c', G.c], ['r', G.r], ["r'", G.rb || '—'], ['code', G.code]];
        const upto = [2, 5, 6, 7][st.sub];
        return { stage: fig(tbl([cells.map(c => ({ v: `<b>${c[0]}</b>`, cls: 'pad' })), cells.map((c, i) => ({ v: i < upto ? c[1] : '', cls: i < upto && i >= [0, 2, 5, 6][st.sub] ? 'hi ctr' : '' }))]), `Golomb code of n = ${st.n} with m = ${st.m}`) };
      },
    });
    P.rebuild();
  }

  /* ------------------------------------------------ RMSE simulator */
  function rmseSim(el, cfg) {
    const f = cfg.f.flat(), d = cfg.fd.flat(), W = cfg.f[0].length, MN = f.length, e = d.map((v, i) => v - f[i]);
    const se = e.reduce((t, x) => t + x * x, 0), sd = d.reduce((t, x) => t + x * x, 0);
    const steps = [];
    f.forEach((v, i) => { const lines = [`Pixel (${Math.floor(i / W)},${i % W}): error e = f̂ − f = ${d[i]} − ${v} = <b>${e[i]}</b>.`, `Square it: (${e[i]})² = <b>${e[i] * e[i]}</b>.`]; lines.forEach((_, sub) => steps.push({ g: `Pixel ${i + 1}`, sub, lines, i })); });
    const fin = [`<b>Add</b> the squared errors: ${e.map(x => x * x).join(' + ')} = <b>${se}</b>.`,
      `<b>Divide</b> by MN = ${MN}: ${se}/${MN} = <b>${trim(se / MN)}</b> (the mean squared error).`,
      `<b>Square root:</b> e<sub>rms</sub> = √${trim(se / MN)} = <b>${trim(Math.sqrt(se / MN))}</b>.`,
      se ? `<b>SNR<sub>ms</sub></b> = Σ f̂² / Σ (f̂ − f)² = ${sd} / ${se} = <b>${trim(sd / se)}</b>.` : 'No error at all, so SNR is infinite.'];
    fin.forEach((_, sub) => steps.push({ g: 'Result', sub, lines: fin, i: MN }));
    player(el, {
      skipLabel: 'Skip ⏭', build: () => steps,
      render(st) {
        const g = (vals, show) => tbl(cfg.f.map((row, a) => row.map((_, b) => { const i = a * W + b; return { v: show(i) ? vals[i] : '', cls: i === st.i ? 'hi ctr' : '' }; })));
        return { stage: fig(g(f, () => true), 'original f') + fig(g(d, () => true), 'decompressed f̂') + fig(g(e, i => i < st.i || (i === st.i)), 'error e = f̂ − f') + fig(g(e.map(x => x * x), i => i < st.i || (i === st.i && st.sub === 1)), 'squared error') };
      },
    }).rebuild();
  }

  /* ------------------------------------------------ morphology simulator */
  const OPS = {
    erode: { name: 'Erosion A ⊖ B', phases: ['erode'] }, dilate: { name: 'Dilation A ⊕ B', phases: ['dilate'] },
    open: { name: 'Opening A ∘ B = (A ⊖ B) ⊕ B', phases: ['erode', 'dilate'] }, close: { name: 'Closing A • B = (A ⊕ B) ⊖ B', phases: ['dilate', 'erode'] },
    boundary: { name: 'Boundary β(A) = A − (A ⊖ B)', phases: ['erode', 'minusAE'] }, edge: { name: 'Outer edge (A ⊕ B) − A', phases: ['dilate', 'minusDA'] },
    cerode: { name: 'Aᶜ ⊖ B (erode the complement)', phases: ['comp', 'erode'] }, hmt: { name: 'Hit-or-miss A ⊛ B', phases: ['hmt'] },
  };
  function morphSim(el, cfg) {
    const ops = cfg.ops || ['erode'];
    const P = player(el, {
      controls: sel('op', ops.map(o => [o, OPS[o].name]), cfg.op || ops[0], 'Operation'), skipLabel: 'Next pixel ⏭', phaseKey: 'ph',
      build() {
        const op = P.q('[data-opt=op]')?.value || ops[0];
        const ses = op === 'hmt' ? cfg.ses : [{ name: 'B', se: cfg.se, origin: cfg.origin }];
        const steps = [];
        let cur = cfg.A, results = [];
        const push = (g, lines, x) => lines.forEach((_, sub) => steps.push({ g, sub, lines, ...x }));
        const phases = op === 'hmt' ? ses.map((_, k) => 'hmt' + k) : OPS[op].phases;
        phases.forEach((ph, pi) => {
          const label = op === 'hmt' ? `${ses[pi].name}` : ph === 'erode' ? 'erosion' : ph === 'dilate' ? 'dilation' : ph === 'comp' ? 'complement' : 'subtraction';
          const S = op === 'hmt' ? ses[pi] : ses[0], kind = op === 'hmt' ? 'hmt' : ph;
          const pre = `Phase ${pi + 1} of ${phases.length}: ${label}. `;
          if (ph === 'comp' || ph === 'minusAE' || ph === 'minusDA') {
            const out = ph === 'comp' ? cur.map(r => r.map(v => 1 - v)) : ph === 'minusAE' ? K.minus(cfg.A, cur) : K.minus(cur, cfg.A);
            const txt = ph === 'comp' ? 'Complement: flip every pixel, 1 ↔ 0. This gives Aᶜ, the background as an object.'
              : ph === 'minusAE' ? 'Subtract: keep the pixels that are 1 in A but 0 in A ⊖ B. What is left is the one-pixel-thick boundary β(A).'
              : 'Subtract: keep the pixels that are 1 in A ⊕ B but 0 in A. What is left is the outer edge the dilation added.';
            push(pre + 'whole image', [txt], { ph: pi, phase: ph, input: cur, out, all: true, S });
            results.push({ label, img: out }); cur = out; return;
          }
          const out = K.morphImage(cur, S.se, S.origin, kind, cfg.discard);
          const posList = [];
          cur.forEach((row, r) => row.forEach((_, c) => { if (out[r][c] !== null) posList.push([r, c]); }));
          posList.forEach(([r, c], k) => {
            const R = K.morphAt(cur, r, c, S.se, S.origin, kind), nxt = posList[k + 1];
            const list = R.cells.map(x => `(${x.r},${x.c})=${x.have}${K.inside(cur, x.r, x.c) ? '' : ' (outside)'}`).join(', ');
            let l1, l2;
            if (kind === 'erode') {
              l1 = `Put the origin of B on pixel (${r},${c}). B covers ${R.cells.length} pixel${R.cells.length > 1 ? 's' : ''}: ${list}.`;
              l2 = R.bad ? `(${R.bad.r},${R.bad.c}) is 0, so B does <b>not fit</b> inside A. Write <b>0</b>.` : `Every covered pixel is 1, so B <b>fits</b>. Write <b>1</b>.`;
            } else if (kind === 'dilate') {
              l1 = `Put the origin of the reflected element B̂ on pixel (${r},${c})${cfg.symmetric ? ' (B is symmetric, so B̂ = B)' : ''}. It covers: ${list}.`;
              l2 = R.hit ? `(${R.hit.r},${R.hit.c}) is 1, so B̂ <b>hits</b> A. Write <b>1</b>.` : `No covered pixel is 1, so B̂ misses A. Write <b>0</b>.`;
            } else {
              l1 = `Put the centre of ${S.name} on pixel (${r},${c}). Compare every 1 and 0 of the SE with the image (× cells are ignored): ${R.cells.map(x => `(${x.r},${x.c}) wants ${x.want}, has ${x.have}`).join('; ')}.`;
              l2 = R.bad ? `Mismatch at (${R.bad.r},${R.bad.c}): the SE wants ${R.bad.want}, the image has ${R.bad.have}. Write <b>0</b>.` : `Every 1 and every 0 matches: <b>hit</b>. Write <b>1</b>.`;
            }
            l2 += nxt ? '' : ` That was the last pixel of this phase.`;
            push(pre + `pixel (${r},${c})`, [l1, l2], { ph: pi, phase: ph, input: cur, out, posList, k, r, c, R, S });
          });
          results.push({ label, img: out.map(row => row.map(v => v ?? 0)) });
          if (op !== 'hmt') cur = results[results.length - 1].img; // every hit-or-miss SE scans the original image
        });
        if (op === 'hmt' && ses.length > 1) {
          const fin = K.orAll(results.map(x => x.img)), n = fin.flat().filter(Boolean).length;
          push('Combine', [`<b>OR</b> the ${ses.length} results: a pixel is marked if any SE found it. Total marked: <b>${n}</b>.`], { ph: phases.length, phase: 'or', input: cfg.A, out: fin, all: true, results });
        }
        steps.forEach(s => (s.results = results));
        return steps;
      },
      jump(key, steps, i) { const [r, c] = key.split(',').map(Number); return steps.findIndex(s => s.ph === steps[i].ph && s.r === r && s.c === c && s.sub === 0); },
      render(st) {
        const A = st.input, H = A.length, W = A[0].length, cov = new Map();
        (st.R?.cells || []).forEach(x => cov.set(x.r + ',' + x.c, x));
        const rows = [];
        for (let i = -1; i <= H; i++) {
          const row = [];
          for (let j = -1; j <= W; j++) {
            const ins = K.inside(A, i, j), v = ins ? A[i][j] : 0, x = cov.get(i + ',' + j);
            if (!ins && !x) { if (i === -1 || i === H || j === -1 || j === W) row.push({ v: '', cls: 'pad off' }); continue; }
            const bad = x && ((st.R.bad && st.R.bad.r === i && st.R.bad.c === j) || (st.R.hit && st.R.hit.r === i && st.R.hit.c === j));
            row.push({ v, cls: `${ins ? (v ? 'on' : '') : 'pad'} ${x ? 'cov' : ''} ${bad && st.sub === 1 ? 'key' : ''} ${i === st.r && j === st.c ? 'ctr' : ''}`, attr: ins && st.posList ? ` data-jump="${i},${j}"` : '' });
          }
          rows.push(row);
        }
        let stage = fig(tbl(rows), st.phase === 'or' ? 'original image' : 'image being processed · outlined = covered by the SE · dashed = outside (counts as 0)');
        const se = st.S?.se;
        if (se && !st.all) stage += fig(tbl(se.map((row, i) => row.map((v, j) => ({ v: v === null ? '×' : v, cls: `${v === 1 ? 'on' : ''} ${i === st.S.origin[0] && j === st.S.origin[1] ? 'ctr' : ''}` })))), `${st.S.name} · outlined = origin`);
        const shown = st.all ? st.out : A.map((row, r) => row.map((_, c) => { const k = st.posList.findIndex(([a, b]) => a === r && b === c); if (k < 0) return null; return k < st.k || (k === st.k && st.sub === 1) ? st.out[r][c] : ''; }));
        stage += fig(tbl(shown.map((row, r) => row.map((v, c) => ({ v: v === null ? '·' : v, cls: `${v === null ? 'pad' : v === 1 ? 'on' : ''} ${r === st.r && c === st.c && st.sub === 1 ? 'new' : ''}` })))), st.phase === 'or' ? 'final result (OR of all)' : 'output of this phase');
        (st.results || []).forEach((x, k) => { if (k < st.ph) stage += fig(tbl(x.img.map(row => row.map(v => ({ v, cls: v ? 'on' : '' })))), `done: ${x.label}`); });
        return { stage };
      },
    });
    P.rebuild();
  }

  /* ------------------------------------------------ chain code simulator */
  const DNAME = { 8: ['right →', 'up-right ↗', 'up ↑', 'up-left ↖', 'left ←', 'down-left ↙', 'down ↓', 'down-right ↘'], 4: ['right →', 'up ↑', 'left ←', 'down ↓'] };
  function arrow(x1, y1, x2, y2, color, wd, cut) {
    const L = Math.hypot(x2 - x1, y2 - y1), ux = (x2 - x1) / L, uy = (y2 - y1) / L;
    const ax = x1 + ux * cut, ay = y1 + uy * cut, bx = x2 - ux * cut, by = y2 - uy * cut, h = 4 + wd * 1.6, w = 2 + wd;
    const p = [[bx, by], [bx - ux * h - uy * w, by - uy * h + ux * w], [bx - ux * h + uy * w, by - uy * h - ux * w]].map(q => q.map(v => v.toFixed(1)).join(',')).join(' ');
    return `<line x1="${ax.toFixed(1)}" y1="${ay.toFixed(1)}" x2="${(bx - ux * h * 0.6).toFixed(1)}" y2="${(by - uy * h * 0.6).toFixed(1)}" stroke="${color}" stroke-width="${wd}"/><polygon points="${p}" fill="${color}"/>`;
  }
  function compass(n, hi) {
    let o = '<svg viewBox="0 0 124 124" width="124" style="max-width:124px" class="plot">';
    for (let k = 0; k < n; k++) {
      const t = (2 * Math.PI * k) / n, c = hi[k] || 'var(--fg2)';
      o += arrow(62, 62, 62 + 40 * Math.cos(t), 62 - 40 * Math.sin(t), c, hi[k] ? 3 : 1.5, 0);
      o += `<text x="${(62 + 53 * Math.cos(t)).toFixed(1)}" y="${(66 - 53 * Math.sin(t)).toFixed(1)}" text-anchor="middle" font-size="12" font-weight="${hi[k] ? 700 : 400}" fill="${c}">${k}</text>`;
    }
    return fig(o + '<circle cx="62" cy="62" r="4" fill="var(--fg)"/></svg>', `${n}-direction compass`, 'fig');
  }
  function chainSim(el, cfg) {
    const n = cfg.n || 8, names = DNAME[n], deg = 360 / n, starts = cfg.starts || [];
    const base = cfg.path ? K.unitPath(cfg.path) : K.pathFromCode(cfg.code, n), grid = cfg.grid || [];
    const H = Math.max(cfg.H || 0, grid.length, ...base.map(p => p[0] + 1)), W = Math.max(cfg.H || 0, grid[0]?.length || 0, ...base.map(p => p[1] + 1)), off = cfg.off || 0;
    const lab = p => (cfg.xy ? `(${p[1]},${H - 1 - p[0]})` : `(${p[0] + off},${p[1] + off})`);
    const S = s => s.join('');
    const P = player(el, {
      controls: sel('start', starts.map((s, k) => [String(k), s[0]]), '0', 'Start point')
        + sel('rule', [['next', '(next − this) mod n · slide 22'], ['prev', '(this − next) mod n · slide 23']], cfg.rule || 'next', 'Difference rule')
        + sel('target', [['cfd', 'CFD → NCFD (start + rotation)'], ['cc', 'CC → smallest shift (start only)']], cfg.target || 'cfd', 'Normalise'),
      skipLabel: 'Skip ⏭', phaseKey: 'ph',
      build() {
        const sk = Number(P.q('[data-opt=start]')?.value || 0), rule = P.q('[data-opt=rule]').value, target = P.q('[data-opt=target]').value;
        let path = base;
        if (starts.length) { const [r, c] = starts[sk][1], j = base.findIndex(p => p[0] === r && p[1] === c); path = base.slice(j).concat(base.slice(0, j)); }
        const code = K.chainCode(path, n), m = code.length, d = K.firstDiff(code, n, rule), R = K.minRot(target === 'cfd' ? d : code);
        const steps = [], push = (g, ph, lines, x) => lines.forEach((_, sub) => steps.push({ g, ph, sub, lines, path, code, d, R, m, target, ...x }));
        const who = starts.length ? ` (start point ${starts[sk][0]})` : cfg.startLabel ? ` (${cfg.startLabel})` : '';
        push('Start', 0, [`Put your finger on the start pixel <b>${lab(path[0])}</b>${who}. Walk ${cfg.dir || 'round the boundary'} until you are back. Each move to a neighbour gets one number: ${names.map((t, k) => `${k} = ${t}`).join(', ')}. The numbers go round <b>counterclockwise</b>, ${deg}° apart.`], { k: -1 });
        code.forEach((c, k) => {
          const a = path[k], b = path[(k + 1) % m], dr = b[0] - a[0], dc = b[1] - a[1];
          const dx = dc, dy = -dr, sg = v => (v > 0 ? '+' + v : String(v));
          push(`Move ${k + 1} of ${m}`, 0, [
            `You are on ${lab(a)}. The next boundary pixel is ${lab(b)}. Step: ${dx ? (dx > 0 ? 'right' : 'left') : ''}${dx && dy ? ' and ' : ''}${dy ? (dy > 0 ? 'up' : 'down') : ''} (${cfg.xy ? `Δx = ${sg(dx)}, Δy = ${sg(dy)}` : `Δrow = ${sg(dr)}, Δcol = ${sg(dc)}; row numbers grow downwards`}).`,
            `That direction is ${names[c]}, so write <b>${c}</b>. Chain so far: <code>${S(code.slice(0, k + 1))}</code>${k === m - 1 ? '. You are back on the start pixel, so the boundary is closed.' : ''}`], { k });
        });
        push('Chain code', 0, [`<b>CC = ${S(code)}</b> (${m} moves). It already ignores where the shape sits in the image (translation). It still changes if you start somewhere else or rotate the shape.`], { k: m });
        const rt = rule === 'next' ? 'next − this' : 'this − next';
        push('Difference rule', 1, [`<b>First difference.</b> For each digit work out (${rt}) mod ${n}. The last digit wraps round to the first one, because the boundary is a closed loop. ` + (rule === 'next'
          ? `The answer counts how many ${deg}° steps you turn left (counterclockwise): 0 = straight on, 1 = slight left, ${n - 1} = slight right, ${n / 2} = U-turn.`
          : `Slide 23 subtracts the other way round, so every digit is ${n} − (the slide-22 digit), mod ${n}. Name the rule you use in the paper.`)], { k: m, i: -1 });
        d.forEach((v, i) => {
          const a = code[i], b = code[(i + 1) % m], raw = rule === 'next' ? b - a : a - b;
          push(`Difference ${i + 1} of ${m}`, 1, [`${i === m - 1 ? '<b>Wrap-around:</b> ' : ''}this = c<sub>${i + 1}</sub> = ${a}, next = c<sub>${((i + 1) % m) + 1}</sub> = ${b}. ${rule === 'next' ? `${b} − ${a}` : `${a} − ${b}`} = ${raw}${raw < 0 ? `, negative, so add ${n}: ${raw + n}` : ''}. Digit = <b>${v}</b>${rule === 'next' ? ` (turn ${v ? `${v * deg}° left` : 'none'})` : ''}.`], { k: m, i });
        });
        push('CFD', 1, [`<b>CFD = ${S(d)}</b>. Rotating the shape by a multiple of ${deg}° adds the same number to every chain digit, and a difference cancels it out. So the CFD is rotation invariant. It still depends on the start pixel.`], { k: m, i: m });
        const nm = target === 'cfd' ? 'CFD' : 'CC';
        push('Normalise', 2, [`<b>Minimum-magnitude normalisation.</b> Think of the ${nm} as a ring of ${m} digits. Read it starting from each digit in turn (${m} circular shifts). Keep the shift that reads as the smallest number.`], { k: m, i: m, r: -1 });
        R.log.forEach((x, r) => push(`Shift ${r + 1} of ${m}`, 2, [r === 0
          ? `Start at digit 1: <code>${S(x.seq)}</code>. Nothing to compare yet, so this is the best so far.`
          : x.pos < 0 ? `Start at digit ${r + 1}: <code>${S(x.seq)}</code>. Same digits as the best so far (a tie), so keep the earlier one.`
          : `Start at digit ${r + 1}: <code>${S(x.seq)}</code>. Compare with the best so far <code>${S(x.prev)}</code>. They first differ at place ${x.pos + 1}: ${x.seq[x.pos]} vs ${x.prev[x.pos]}, so this one is ${x.better ? '<b>smaller: new best</b>' : 'bigger: keep the old best'}.`], { k: m, i: m, r }));
        push('Answer', 2, [target === 'cfd'
          ? `The smallest shift starts at digit ${R.idx + 1}: <b>NCFD = shape number = ${S(R.best)}</b>. You get the same number from any start pixel and after any rotation by ${deg}° steps.`
          : `The smallest shift starts at digit ${R.idx + 1}: <b>${S(R.best)}</b>. This is the CC normalised for start point only (slides 18 and 24 call it the shape number). A rotation still changes it; normalise the CFD to remove rotation as well.`], { k: m, i: m, r: m });
        return steps;
      },
      render(st) {
        const { path, code, d, R, m, ph } = st, s = Math.max(18, Math.min(34, Math.floor(300 / Math.max(W, H)))), L = 20, T = 16;
        const cx = p => L + p[1] * s + s / 2, cy = p => T + p[0] * s + s / 2;
        let o = `<svg viewBox="0 0 ${L + W * s + 4} ${T + H * s + 4}" width="${L + W * s + 4}" style="max-width:${L + W * s + 4}px" class="plot">`;
        for (let c = 0; c < W; c++) o += `<text x="${L + c * s + s / 2}" y="${T - 4}" text-anchor="middle" font-size="10" fill="var(--fg2)">${c + off}</text>`;
        for (let r = 0; r < H; r++) o += `<text x="${L - 4}" y="${T + r * s + s / 2 + 3}" text-anchor="end" font-size="10" fill="var(--fg2)">${cfg.xy ? H - 1 - r : r + off}</text>`;
        for (let r = 0; r < H; r++) for (let c = 0; c < W; c++) o += `<rect x="${L + c * s}" y="${T + r * s}" width="${s}" height="${s}" fill="${'#1'.includes(grid[r]?.[c] ?? '.') ? 'var(--line)' : 'none'}" stroke="var(--line)"/>`;
        path.forEach(p => (o += `<circle cx="${cx(p)}" cy="${cy(p)}" r="${(s * 0.17).toFixed(1)}" fill="var(--fg)"/>`));
        o += `<circle cx="${cx(path[0])}" cy="${cy(path[0])}" r="${(s * 0.36).toFixed(1)}" fill="none" stroke="var(--c2)" stroke-width="2.5"/>`;
        path.forEach((a, k) => {
          const b = path[(k + 1) % m];
          const now = (ph === 0 && k === st.k) || (ph === 1 && (k === st.i || k === (st.i + 1) % m) && st.i >= 0 && st.i < m);
          if (ph === 0 && k > st.k) return;
          o += arrow(cx(a), cy(a), cx(b), cy(b), now ? 'var(--mark)' : 'var(--c1)', now ? 3 : 1.6, s * 0.2);
        });
        let stage = fig(o + '</svg>', `boundary · ringed = start${cfg.xy ? ' · axes are x →, y ↑' : ` · (row, col), row ${off} at the top`}`, 'fig');
        const hi = {};
        if (ph === 0 && st.k >= 0 && st.k < m && st.sub === 1) hi[code[st.k]] = 'var(--mark)';
        if (ph === 1 && st.i >= 0 && st.i < m) { hi[code[st.i]] = 'var(--c2)'; hi[code[(st.i + 1) % m]] = 'var(--mark)'; }
        if (ph < 2) stage += compass(n, hi);
        const lbl = t => ({ v: `<b>${t}</b>`, cls: 'pad' });
        const rows = [[lbl('#'), ...code.map((_, j) => ({ v: j + 1, cls: 'pad' }))],
          [lbl('CC'), ...code.map((c, j) => ({ v: ph > 0 || j < st.k || (j === st.k && st.sub === 1) ? c : '', cls: (ph === 0 && j === st.k && st.sub === 1) ? 'new' : (ph === 1 && st.i >= 0 && st.i < m && (j === st.i || j === (st.i + 1) % m)) ? 'cov' : '' }))]];
        if (ph > 0) rows.push([lbl('CFD'), ...d.map((v, j) => ({ v: ph > 1 || j <= st.i ? v : '', cls: ph === 1 && j === st.i ? 'new' : '' }))]);
        stage += fig(tbl(rows), ph === 1 ? 'outlined = the two codes being subtracted' : 'the digits so far');
        if (ph === 2 && st.r >= 0) {
          const upto = Math.min(st.r, m - 1), best = R.log[upto].best;
          stage += fig(tbl(R.log.slice(0, upto + 1).map((x, k) => [{ v: `from ${k + 1}`, cls: 'pad' }, ...x.seq.map((v, j) => ({ v, cls: k === best ? 'key' : k === st.r ? (j === x.pos ? 'new' : 'cov') : '' }))])),
            `circular shifts of the ${st.target === 'cfd' ? 'CFD' : 'CC'} · filled = smallest so far`);
        }
        return { stage };
      },
    });
    P.rebuild();
  }

  /* ------------------------------------------------ colour conversion simulator (RGB → CMY, RGB → HSI) */
  function cubeSvg(r, g, b, hl) {
    // R axis toward the viewer (down-left), G to the right, B up, as on slide 14
    const P = (x, y, z) => [70 + y * 130 - x * 55, 175 - z * 130 + x * 40];
    const C = [[0, 0, 0, '#000', 'Black'], [1, 0, 0, '#f00', 'Red'], [0, 1, 0, '#0c0', 'Green'], [0, 0, 1, '#00f', 'Blue'], [1, 1, 0, '#ff0', 'Yellow'], [0, 1, 1, '#0ff', 'Cyan'], [1, 0, 1, '#f0f', 'Magenta'], [1, 1, 1, '#fff', 'White']];
    const E = [[0, 1], [0, 2], [0, 3], [1, 4], [1, 6], [2, 4], [2, 5], [3, 5], [3, 6], [4, 7], [5, 7], [6, 7]];
    let o = '<svg viewBox="0 0 230 230" width="230" style="max-width:230px" class="plot">';
    E.forEach(([a, b2]) => { const p = P(...C[a]), q = P(...C[b2]); o += `<line x1="${p[0]}" y1="${p[1]}" x2="${q[0]}" y2="${q[1]}" stroke="var(--fg2)" stroke-width="1"/>`; });
    const k = P(0, 0, 0), w = P(1, 1, 1);
    o += `<line x1="${k[0]}" y1="${k[1]}" x2="${w[0]}" y2="${w[1]}" stroke="var(--fg2)" stroke-dasharray="4 3"/>`;
    C.forEach(([x, y, z, col, name]) => { const p = P(x, y, z); o += `<circle cx="${p[0]}" cy="${p[1]}" r="5" fill="${col}" stroke="var(--fg)"/><text x="${p[0] + (y ? 7 : -7)}" y="${p[1] + (z ? -6 : 13)}" text-anchor="${y ? 'start' : 'end'}" font-size="10" fill="var(--fg)">${name}</text>`; });
    const p = P(r, g, b), base = P(r, g, 0);
    o += `<line x1="${p[0]}" y1="${p[1]}" x2="${base[0]}" y2="${base[1]}" stroke="var(--mark)" stroke-dasharray="3 3"/><circle cx="${p[0]}" cy="${p[1]}" r="${hl ? 8 : 6}" fill="rgb(${Math.round(r * 255)},${Math.round(g * 255)},${Math.round(b * 255)})" stroke="var(--mark)" stroke-width="2.5"/>`;
    return fig(o + '</svg>', 'RGB cube (normalised) · dashed diagonal = gray scale', 'fig');
  }
  function hexSvg(H, S) {
    const c = 110, R = 80, pt = d => [c + R * Math.cos((d * Math.PI) / 180), c - R * Math.sin((d * Math.PI) / 180)];
    const V = [[0, 'Red', '#f00'], [60, 'Yellow', '#ff0'], [120, 'Green', '#0c0'], [180, 'Cyan', '#0ff'], [240, 'Blue', '#00f'], [300, 'Magenta', '#f0f']];
    let o = '<svg viewBox="0 0 220 220" width="220" style="max-width:220px" class="plot">';
    o += `<polygon points="${V.map(([d]) => pt(d).map(v => v.toFixed(1)).join(',')).join(' ')}" fill="none" stroke="var(--fg2)"/>`;
    V.forEach(([d, n, col]) => { const p = pt(d), q = [c + (R + 16) * Math.cos((d * Math.PI) / 180), c - (R + 16) * Math.sin((d * Math.PI) / 180)]; o += `<circle cx="${p[0]}" cy="${p[1]}" r="5" fill="${col}" stroke="var(--fg)"/><text x="${q[0]}" y="${q[1] + 4}" text-anchor="middle" font-size="10" fill="var(--fg)">${n} ${d}°</text>`; });
    o += `<line x1="${c}" y1="${c}" x2="${c + R}" y2="${c}" stroke="var(--fg2)" stroke-dasharray="3 3"/>`;
    if (H !== null && H !== undefined) {
      const r = R * (S ?? 1), e = [c + r * Math.cos((H * Math.PI) / 180), c - r * Math.sin((H * Math.PI) / 180)], big = H > 180 ? 1 : 0, a = [c + 26 * Math.cos((H * Math.PI) / 180), c - 26 * Math.sin((H * Math.PI) / 180)];
      o += `<path d="M ${c + 26} ${c} A 26 26 0 ${big} 0 ${a[0].toFixed(1)} ${a[1].toFixed(1)}" fill="none" stroke="var(--mark)" stroke-width="2"/>`;
      o += `<line x1="${c}" y1="${c}" x2="${e[0].toFixed(1)}" y2="${e[1].toFixed(1)}" stroke="var(--mark)" stroke-width="2.5"/><circle cx="${e[0].toFixed(1)}" cy="${e[1].toFixed(1)}" r="5" fill="var(--mark)"/>`;
      o += `<text x="${c + 30}" y="${c - 8}" font-size="11" fill="var(--mark)">H</text>`;
    }
    return fig(o + `<circle cx="${c}" cy="${c}" r="3" fill="var(--fg)"/></svg>`, 'hue = angle from red · saturation = distance from the centre', 'fig');
  }
  function colorSim(el, cfg) {
    const parts = cfg.parts || ['cmy', 'hsi'], dp = cfg.dp || 4, f = x => x.toFixed(dp);
    const num = (name, v, label) => `<label>${label}<input type="number" min="0" max="255" step="1" data-opt="${name}" value="${v}" style="width:6em;font:15px var(--f-mono);padding:5px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)"></label>`;
    const P = player(el, {
      controls: num('r', cfg.rgb[0], 'R (0–255)') + num('g', cfg.rgb[1], 'G (0–255)') + num('b', cfg.rgb[2], 'B (0–255)'), skipLabel: 'Skip ⏭', phaseKey: 'ph',
      build() {
        const v = ['r', 'g', 'b'].map((k, i) => { const x = Math.round(Number(P.q(`[data-opt=${k}]`).value)); return Number.isFinite(x) ? Math.max(0, Math.min(255, x)) : cfg.rgb[i]; });
        const [r, g, b] = v, X = K.hsi(r, g, b), Cm = K.cmy(r, g, b), steps = [];
        const push = (g2, ph, lines, x) => lines.forEach((_, sub) => steps.push({ g: g2, ph, sub, lines, v, X, Cm, ...x }));
        push('Normalise', 0, [`Divide each value by 255 so it lies in [0, 1]: R = ${r}/255 = <b>${f(X.R)}</b>.`, `G = ${g}/255 = <b>${f(X.G)}</b>.`, `B = ${b}/255 = <b>${f(X.B)}</b>.`], { k: 'n' });
        if (parts.includes('cmy')) push('RGB → CMY', 1, [`[C M Y] = [1 1 1] − [R G B]. C = 1 − ${f(X.R)} = <b>${f(Cm[0])}</b> (cyan ink absorbs red).`, `M = 1 − ${f(X.G)} = <b>${f(Cm[1])}</b>.`, `Y = 1 − ${f(X.B)} = <b>${f(Cm[2])}</b>. In 0–255 form: (${255 - r}, ${255 - g}, ${255 - b}).`], { k: 'c' });
        if (parts.includes('hsi')) {
          const lines = [
            `Top of θ: ½[(R − G) + (R − B)] = ½[(${f(X.R)} − ${f(X.G)}) + (${f(X.R)} − ${f(X.B)})] = <b>${f(X.num)}</b>.`,
            `Bottom of θ: √[(R − G)² + (R − B)(G − B)] = √[(${f(X.R - X.G)})² + (${f(X.R - X.B)})(${f(X.G - X.B)})] = <b>${f(X.den)}</b>.`,
            X.theta === null ? 'The bottom is 0 because R = G = B: this is a gray, so the hue is <b>undefined</b> (take H = 0).' : `θ = cos⁻¹(${f(X.num)} / ${f(X.den)}) = cos⁻¹(${f(X.num / X.den)}) = <b>${X.theta.toFixed(2)}°</b>.`,
            X.theta === null ? 'No hue for a gray.' : X.B <= X.G ? `B = ${f(X.B)} ≤ G = ${f(X.G)}, so <b>H = θ = ${X.H.toFixed(2)}°</b>.` : `B = ${f(X.B)} > G = ${f(X.G)}, so <b>H = 360 − θ = ${X.H.toFixed(2)}°</b>.`,
            X.S === null ? 'R + G + B = 0 (black), so S is undefined (take S = 0).' : `S = 1 − 3·min(R,G,B)/(R + G + B) = 1 − 3 × ${f(Math.min(X.R, X.G, X.B))} / ${f(X.R + X.G + X.B)} = <b>${f(X.S)}</b>.`,
            `I = (R + G + B)/3 = ${f(X.R + X.G + X.B)} / 3 = <b>${f(X.I)}</b>.`];
          push('RGB → HSI', 2, lines, { k: 'h' });
        }
        return steps;
      },
      render(st) {
        const [r, g, b] = st.v, X = st.X, done = (ph, sub) => st.ph > ph || (st.ph === ph && st.sub >= sub);
        let stage = fig(`<div style="width:120px;height:90px;border-radius:8px;border:1px solid var(--line);background:rgb(${r},${g},${b})"></div>`, `the colour (${r}, ${g}, ${b})`, 'fig');
        stage += cubeSvg(X.R, X.G, X.B, st.ph === 0);
        if (parts.includes('hsi') && st.k === 'h') stage += hexSvg(done(2, 3) ? X.H : null, done(2, 4) ? X.S : 1);
        const cell = (t, ok) => ({ v: ok ? t : '', cls: ok ? '' : 'pad' });
        const rows = [[{ v: '<b>R, G, B</b>', cls: 'pad' }, cell(f(X.R), done(0, 0)), cell(f(X.G), done(0, 1)), cell(f(X.B), done(0, 2))]];
        if (parts.includes('cmy')) rows.push([{ v: '<b>C, M, Y</b>', cls: 'pad' }, cell(f(st.Cm[0]), done(1, 0)), cell(f(st.Cm[1]), done(1, 1)), cell(f(st.Cm[2]), done(1, 2))]);
        if (parts.includes('hsi')) rows.push([{ v: '<b>H, S, I</b>', cls: 'pad' }, cell(X.H === null ? 'undef.' : X.H.toFixed(2) + '°', done(2, 3)), cell(X.S === null ? 'undef.' : f(X.S), done(2, 4)), cell(f(X.I), done(2, 5))]);
        stage += fig(tbl(rows), 'results so far');
        return { stage };
      },
    });
    P.rebuild();
  }

  /* ------------------------------------------------ Canny steps 3–5 simulator */
  function cannySim(el, cfg) {
    const num = (name, v, label) => `<label>${label}<input type="number" min="0" max="999" step="1" data-opt="${name}" value="${v}" style="width:6em;font:15px var(--f-mono);padding:5px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)"></label>`;
    const P = player(el, {
      controls: num('th', cfg.TH, 'High threshold T<sub>H</sub>') + num('tl', cfg.TL, 'Low threshold T<sub>L</sub>'), skipLabel: 'Next pixel ⏭', phaseKey: 'ph',
      build() {
        const TH = Number(P.q('[data-opt=th]').value), TL = Number(P.q('[data-opt=tl]').value), R = K.canny(cfg.M, cfg.D, TH, TL), steps = [];
        const push = (g, ph, lines, x) => lines.forEach((_, sub) => steps.push({ g, ph, sub, lines, R, TH, TL, ...x }));
        const at = p => `(${p.r},${p.c})`;
        if (cfg.D) {
          push('Step 3 · non-maximum suppression', 0, [`<b>Step 3, non-maximum suppression.</b> For each pixel look along its gradient arrow, one pixel each way. Keep the pixel only if it is not smaller than those neighbours; otherwise write 0. Outside the image there is no neighbour.`], { k: -1 });
          R.nms.forEach((x, k) => push(`Step 3 · pixel ${at(x)}`, 0, [
            `Pixel ${at(x)}: M = <b>${x.v}</b>, arrow ${x.d}. Neighbours along it: ${x.nb.map(p => (p.v === null ? `${at(p)} outside` : `${at(p)} = ${p.v}`)).join(', ')}.`,
            x.keep ? `${x.v} is not smaller than ${x.nb.filter(p => p.v !== null).map(p => p.v).join(' or ') || 'anything (no neighbours)'}: it is a local maximum, <b>keep ${x.v}</b>.` : `${x.v} is smaller than ${x.nb.filter(p => p.v !== null && p.v > x.v).map(p => p.v).join(' and ')}: not a maximum, <b>suppress → 0</b>.`], { k, cur: x }));
        }
        const cells = [];
        R.gN.forEach((row, r) => row.forEach((v, c) => cells.push({ r, c, v })));
        push('Step 4 · double threshold', 1, [`<b>Step 4, double thresholding</b> with T<sub>H</sub> = ${TH}, T<sub>L</sub> = ${TL}: g<sub>N</sub> ≥ ${TH} is <b>strong</b> (g<sub>NH</sub>); ${TL} ≤ g<sub>N</sub> &lt; ${TH} is <b>weak</b> (g<sub>NL</sub>); below ${TL} becomes 0.${TH < 2 * TL || TH > 3 * TL ? ` (Slide 52 suggests T<sub>H</sub> : T<sub>L</sub> = 2:1 or 3:1; here it is ${(TH / Math.max(1, TL)).toFixed(1)}:1.)` : ''}`], { k: -1 });
        cells.forEach((x, k) => push(`Step 4 · pixel ${at(x)}`, 1, [x.v >= TH ? `g<sub>N</sub>${at(x)} = ${x.v} ≥ ${TH}: <b>strong</b> (sure edge).` : x.v >= TL ? `g<sub>N</sub>${at(x)} = ${x.v} is between ${TL} and ${TH}: <b>weak</b> (decided in step 5).` : `g<sub>N</sub>${at(x)} = ${x.v} &lt; ${TL}: <b>not an edge</b>, 0.`], { k, cur: x }));
        push('Step 5 · hysteresis', 2, [`<b>Step 5, hysteresis.</b> Every strong pixel stays. A weak pixel stays only if one of its 8 neighbours is strong; otherwise it is treated as noise and removed.${R.weak.length ? '' : ' There are no weak pixels, so nothing changes.'}`], { k: -1 });
        R.weak.forEach((x, k) => push(`Step 5 · weak ${at(x)}`, 2, [x.strong.length ? `Weak ${x.v} at ${at(x)} touches strong ${x.strong.map(p => `${p.v} ${at(p)}`).join(', ')}: <b>keep it</b>.` : `Weak ${x.v} at ${at(x)} has no strong 8-neighbour: <b>discard</b> (set to 0).`], { k, cur: x }));
        push('Result', 3, [`Final edge map: ${R.g.flat().filter(Boolean).length} edge pixel${R.g.flat().filter(Boolean).length === 1 ? '' : 's'}.`], { k: -1 });
        return steps;
      },
      render(st) {
        const R = st.R, x = st.cur, nb = new Set((x?.nb || []).map(p => p.r + ',' + p.c)), st5 = new Set((x?.strong || []).map(p => p.r + ',' + p.c));
        const grid = (G, cap, fmt, cls) => fig(tbl(G.map((row, r) => row.map((v, c) => ({ v: fmt(v, r, c), cls: cls(r, c, v) })))), cap);
        const here = (r, c) => x && x.r === r && x.c === c;
        let stage = '';
        if (cfg.D) stage += grid(cfg.M, 'M and gradient direction (steps 1–2 given)', (v, r, c) => `${v} ${cfg.D[r][c]}`, (r, c) => `${here(r, c) && st.ph === 0 ? 'ctr' : ''} ${st.ph === 0 && nb.has(r + ',' + c) ? 'cov' : ''}`);
        const kN = st.ph === 0 ? st.k : 99;
        stage += grid(R.gN, 'g<sub>N</sub> after non-max suppression', (v, r, c) => (!cfg.D || r * cfg.M[0].length + c <= kN - (st.sub === 0 && st.ph === 0 ? 1 : 0) || st.ph > 0 ? v : ''), (r, c) => `${here(r, c) && st.ph <= 1 ? 'ctr' : ''}`);
        if (st.ph >= 1) {
          const shown = (r, c) => st.ph > 1 || r * R.gN[0].length + c <= st.k;
          stage += grid(R.gNH, `g<sub>NH</sub> strong (≥ ${st.TH})`, (v, r, c) => (shown(r, c) ? v : ''), (r, c, v) => (shown(r, c) && v ? 'on' : ''));
          stage += grid(R.gNL, `g<sub>NL</sub> weak (${st.TL} to ${st.TH - 1})`, (v, r, c) => (shown(r, c) ? v : ''), (r, c, v) => `${shown(r, c) && v ? 'key' : ''} ${st.ph === 2 && here(r, c) ? 'ctr' : ''} ${st.ph === 2 && st5.has(r + ',' + c) ? 'cov' : ''}`);
        }
        if (st.ph >= 2) {
          const doneW = new Set(R.weak.filter((w, k) => st.ph > 2 || k <= st.k).map(w => w.r + ',' + w.c));
          stage += grid(R.g, 'final edge map g', (v, r, c) => (R.gNH[r][c] || doneW.has(r + ',' + c) ? v : R.gNL[r][c] ? '?' : 0), (r, c, v) => (v && (R.gNH[r][c] || doneW.has(r + ',' + c)) ? 'on' : ''));
        }
        return { stage };
      },
    });
    P.rebuild();
  }

  /* ------------------------------------------------ region growing simulator */
  const numIn = (name, v, label, w = '5em') => `<label>${label}<input type="number" min="0" step="1" data-opt="${name}" value="${v}" style="width:${w};font:15px var(--f-mono);padding:5px 8px;border:1px solid var(--line);border-radius:6px;background:var(--bg);color:var(--fg)"></label>`;
  function growSim(el, cfg) {
    const P = player(el, {
      controls: sel('conn', [['4', '4-connectivity (up, down, left, right)'], ['8', '8-connectivity (+ diagonals)']], String(cfg.conn || 4), 'Grow in')
        + sel('cmp', [['nbr', 'the pixel it grows from'], ['seed', 'the seed value']], cfg.compare || 'nbr', 'Compare with') + numIn('t', cfg.T, 'T (|difference| ≤ T)'),
      skipLabel: 'Next pixel ⏭',
      build() {
        const conn = Number(P.q('[data-opt=conn]').value), cmp = P.q('[data-opt=cmp]').value, T = Number(P.q('[data-opt=t]').value);
        const R = K.grow(cfg.img, cfg.seed, T, conn, cmp), steps = [], at = p => `(${p[0]},${p[1]})`;
        const s0 = cfg.img[cfg.seed[0]][cfg.seed[1]];
        steps.push({ g: 'Seed', sub: 0, lines: [`Start the region with the seed ${at(cfg.seed)} = <b>${s0}</b>. Put it in the queue. Rule: a ${conn}-neighbour joins when |its value − ${cmp === 'seed' ? `the seed (${s0})` : 'the pixel it grows from'}| ≤ ${T}.`], k: -1, R, conn });
        let grp = null, lines = [], first = 0;
        R.log.forEach((x, k) => {
          const g = `Grow from ${at(x.from)}`;
          if (g !== grp) { grp = g; lines = []; first = k; }
          lines.push(x.already ? `${at(x.to)} = ${x.v} is already in the region.` : `${at(x.to)} = ${x.v}: |${x.v} − ${x.base}| = ${x.d} ${x.ok ? `≤ ${T} → <b>joins</b>` : `&gt; ${T} → no`}.`);
          steps.push({ g, sub: lines.length - 1, lines, k, R, conn });
        });
        steps.push({ g: 'Done', sub: 0, lines: [`The queue is empty: no more pixels can join. Region size = <b>${R.region.length}</b> pixels.`], k: R.log.length, R, conn });
        return steps;
      },
      render(st) {
        const R = st.R, x = R.log[st.k], inRegionByNow = new Set([cfg.seed[0] + ',' + cfg.seed[1]]);
        R.log.forEach((y, k) => { if (k <= st.k && y.ok) inRegionByNow.add(y.to.join(',')); });
        const rows = cfg.img.map((row, r) => row.map((v, c) => ({ v, cls: `${inRegionByNow.has(r + ',' + c) ? 'on' : ''} ${x && x.from[0] === r && x.from[1] === c ? 'ctr' : ''} ${x && x.to[0] === r && x.to[1] === c ? (x.ok ? 'new' : 'cov') : ''}` })));
        return { stage: fig(tbl(rows), `filled = region so far (${inRegionByNow.size} px) · thick ring = growing from · outlined/orange = neighbour being checked`) };
      },
    });
    P.rebuild();
  }

  /* ------------------------------------------------ iterative global threshold simulator */
  function thrSim(el, cfg) {
    const vals = cfg.values, f = x => (Number.isInteger(x) ? String(x) : x.toFixed(3));
    const P = player(el, {
      controls: numIn('t0', cfg.T0 ?? '', 'Start T (blank = mean)', '7em') + numIn('eps', cfg.eps ?? 0.5, 'Stop when ΔT &lt;', '5em'), skipLabel: 'Next iteration ⏭',
      build() {
        const t0 = P.q('[data-opt=t0]').value, eps = Number(P.q('[data-opt=eps]').value) || 0.5;
        const rows = K.iterT(vals, t0 === '' ? undefined : Number(t0), eps), steps = [];
        rows.forEach((x, it) => {
          const lines = [
            it === 0 ? (t0 === '' ? `Start with T = mean of all ${vals.length} values = ${vals.reduce((s, v) => s + v, 0)}/${vals.length} = <b>${f(x.T)}</b>.` : `Start with T = <b>${f(x.T)}</b>.`) : `New round with T = <b>${f(x.T)}</b>.`,
            `Split: G1 = values &gt; ${f(x.T)}: {${x.g1.join(', ')}} (${x.g1.length}); G2 = values ≤ ${f(x.T)}: {${x.g2.join(', ')}} (${x.g2.length}).`,
            `Means: μ1 = ${x.g1.length ? `${x.g1.reduce((s, v) => s + v, 0)}/${x.g1.length}` : '—'} = <b>${f(x.m1)}</b>; μ2 = ${x.g2.length ? `${x.g2.reduce((s, v) => s + v, 0)}/${x.g2.length}` : '—'} = <b>${f(x.m2)}</b>.`,
            `New T = ½(μ1 + μ2) = ½(${f(x.m1)} + ${f(x.m2)}) = <b>${f(x.Tn)}</b>. ΔT = |${f(x.Tn)} − ${f(x.T)}| = ${f(x.dT)} ${x.dT < eps ? `&lt; ${eps}: <b>stop</b>. Final T ≈ ${f(x.Tn)}.` : `≥ ${eps}: repeat.`}`];
          lines.forEach((_, sub) => steps.push({ g: `Iteration ${it + 1}`, sub, lines, x }));
        });
        return steps;
      },
      render(st) {
        const x = st.x, show = st.sub >= 1;
        return { stage: fig(tbl([vals.map(v => ({ v, cls: show ? (v > x.T ? 'on' : 'key') : '' }))]), show ? `filled = G1 (&gt; T), orange = G2 (≤ T)` : 'the values') };
      },
    });
    P.rebuild();
  }

  /* ------------------------------------------------ path simulator (4 / 8 / m) */
  function pathSim(el, cfg) {
    const kinds = cfg.kinds || ['4', '8', 'm'];
    const P = player(el, {
      controls: sel('kind', kinds.map(k => [k, k === 'm' ? 'm-path (mixed)' : `${k}-path`]), String(cfg.kind || kinds[0]), 'Path type'), skipLabel: 'Next pixel ⏭',
      build() {
        const kv = P.q('[data-opt=kind]')?.value || kinds[0], kind = kv === 'm' ? 'm' : Number(kv), R = K.findPath(cfg.img, cfg.V, cfg.p, cfg.q, kind), steps = [];
        const at = p => `(${p[0]},${p[1]})`, V = `{${cfg.V.join(', ')}}`, val = p => cfg.img[p[0]][p[1]];
        const intro = `Find a ${kv === 'm' ? 'm' : kv}-path from p ${at(cfg.p)} = ${val(cfg.p)} to q ${at(cfg.q)} = ${val(cfg.q)} with V = ${V}. Every pixel on the path must have a value in V, and each step must go to a ${kv === '4' ? '4-neighbour (up, down, left, right)' : kv === '8' ? '8-neighbour (including diagonals)' : '4-neighbour, or to a diagonal neighbour only when the two pixels share no 4-neighbour whose value is in V'}.`;
        steps.push({ g: 'Start', sub: 0, lines: [R.bad ? `${intro} But ${at(R.bad)} = ${val(R.bad)} is not in V, so <b>no path can exist</b>.` : intro], k: -1, R, kv });
        R.log.forEach((x, k) => {
          const lines = [];
          if (x.reached) lines.push(`Reached q ${at(x.at)}. <b>Path found.</b>`);
          x.checks.forEach(ck => {
            let t = `${ck.diag ? 'diagonal' : '4-neighbour'} ${at(ck.to)} = ${ck.v}: `;
            if (!ck.inV) t += `${ck.v} ∉ V, skip.`;
            else if (ck.seen) t += 'already reached, skip.';
            else if (ck.blocked) t += `in V, but the shared 4-neighbours ${ck.shared.map(s => `${at(s.at)} = ${s.v}`).join(', ')} include a value in V, so this diagonal step is <b>not m-adjacent</b> (go round instead).`;
            else t += ck.shared ? `in V, and the shared 4-neighbours ${ck.shared.map(s => `${at(s.at)} = ${s.v}`).join(', ')} are not in V: <b>m-adjacent, add</b>.` : '<b>in V, add</b>.';
            lines.push(t);
          });
          if (!lines.length) lines.push('No neighbours to check.');
          lines.forEach((_, sub) => steps.push({ g: `From ${at(x.at)}`, sub, lines, k, R, kv }));
        });
        if (!R.bad) steps.push({ g: 'Result', sub: 0, lines: [R.path ? `${kv}-path: ${R.path.map(p => `${at(p)}=${val(p)}`).join(' → ')} (length ${R.path.length - 1}).` : `Every reachable pixel has been tried and q was never reached: <b>no ${kv}-path exists</b>.`], k: R.log.length, R, kv });
        return steps;
      },
      render(st) {
        const R = st.R, x = R.log[st.k], reached = new Set([cfg.p.join(',')]);
        R.log.forEach((y, k) => { if (k <= st.k) y.checks.forEach(ck => { if (ck.ok) reached.add(ck.to.join(',')); }); });
        const onPath = new Set(st.k >= R.log.length && R.path ? R.path.map(p => p.join(',')) : []);
        const ck = x?.checks?.[st.sub - (x.reached ? 1 : 0)], shared = new Set((ck?.shared || []).map(s => s.at.join(',')));
        const rows = cfg.img.map((row, r) => row.map((v, c) => {
          const k2 = r + ',' + c, isP = k2 === cfg.p.join(','), isQ = k2 === cfg.q.join(',');
          return { v: `${v}${isP ? '<sup>p</sup>' : isQ ? '<sup>q</sup>' : ''}`, cls: `${onPath.has(k2) ? 'key' : reached.has(k2) ? 'on' : cfg.V.includes(v) ? '' : 'pad'} ${x && x.at[0] === r && x.at[1] === c ? 'ctr' : ''} ${ck && ck.to[0] === r && ck.to[1] === c ? 'cov' : ''} ${shared.has(k2) ? 'cov' : ''}` };
        }));
        return { stage: fig(tbl(rows), 'grey = value not in V · filled = reached · ring = current pixel · outlined = being checked (and its shared 4-neighbours) · orange = final path') };
      },
    });
    P.rebuild();
  }

  /* ------------------------------------------------ nearest-neighbour zoom simulator */
  function nniSim(el, cfg) {
    const H = cfg.img.length, W = cfg.img[0].length, f3 = x => (Number.isInteger(x) ? String(x) : x.toFixed(3).replace(/0+$/, ''));
    const P = player(el, {
      controls: numIn('h', cfg.to[0], 'New rows', '4.5em') + numIn('w', cfg.to[1], 'New columns', '4.5em'), skipLabel: 'Next part ⏭',
      build() {
        const h = Math.max(1, Math.min(16, Number(P.q('[data-opt=h]').value) || cfg.to[0])), w = Math.max(1, Math.min(16, Number(P.q('[data-opt=w]').value) || cfg.to[1]));
        const Z = K.nnZoom(cfg.img, h, w), steps = [];
        const push = (g, lines, x) => lines.forEach((_, sub) => steps.push({ g, sub, lines, Z, h, w, ...x }));
        push('Ratios', [`Ratio<sub>row</sub> = old rows / new rows = ${H}/${h} = ${f3(H / h)}; Ratio<sub>col</sub> = old columns / new columns = ${W}/${w} = ${f3(W / w)}.`], { ph: 'r' });
        push('Row positions', Z.rp.map((p, i) => `New row ${i + 1}: ${f3(H / h)} × ${i + 1} = ${f3((H * (i + 1)) / h)} → ceil = <b>${p}</b> (take old row ${p}).`), { ph: 'rp' });
        push('Column positions', Z.cp.map((p, j) => `New column ${j + 1}: ${f3(W / w)} × ${j + 1} = ${f3((W * (j + 1)) / w)} → ceil = <b>${p}</b> (take old column ${p}).`), { ph: 'cp' });
        push('Fill the output', Z.rp.map((p, i) => `Output row ${i + 1} = old row ${p} [${cfg.img[p - 1].join(' ')}] read at columns [${Z.cp.join(' ')}] = <b>[${Z.out[i].join(' ')}]</b>.`), { ph: 'out' });
        return steps;
      },
      render(st) {
        const Z = st.Z, i = st.sub;
        const src = cfg.img.map((row, r) => row.map((v, c) => ({ v, cls: `${(st.ph === 'rp' || st.ph === 'out') && r === Z.rp[i] - 1 ? 'on' : ''} ${st.ph === 'cp' && c === Z.cp[i] - 1 ? 'on' : ''}` })));
        let stage = fig(tbl(src), `original ${H}×${W}`);
        stage += fig(tbl([Z.rp.map((p, k) => ({ v: st.ph === 'rp' && k > i ? '' : st.ph === 'r' ? '' : p, cls: st.ph === 'rp' && k === i ? 'new' : '' }))]), 'row positions');
        stage += fig(tbl([Z.cp.map((p, k) => ({ v: (st.ph === 'cp' && k > i) || st.ph === 'r' || st.ph === 'rp' ? '' : p, cls: st.ph === 'cp' && k === i ? 'new' : '' }))]), 'column positions');
        if (st.ph === 'out') stage += fig(tbl(Z.out.map((row, r) => row.map(v => ({ v: r <= i ? v : '', cls: r === i ? 'new' : '' })))), `output ${st.h}×${st.w}`);
        return { stage };
      },
    });
    P.rebuild();
  }

  document.querySelectorAll('.sim[data-sim]').forEach(el => {
    const cfg = JSON.parse(el.dataset.sim);
    el.tabIndex = -1;
    ({ filter: filterSim, oned: oneDSim, he: heSim, hs: hsSim, huff: huffSim, lzw: lzwSim, arith: arithSim, rle: rleSim, golomb: golSim, rmse: rmseSim, morph: morphSim, chain: chainSim, color: colorSim, canny: cannySim, grow: growSim, thr: thrSim, path: pathSim, nni: nniSim })[cfg.type](el, cfg);
  });
})();
