// Checks the simulator maths against slide and past-paper answers (all verified earlier in Python).
const K = require('./sim_kit.js');
let bad = 0;
const eq = (a, b, msg) => { if (JSON.stringify(a) !== JSON.stringify(b)) { console.error('FAIL', msg, JSON.stringify(a), JSON.stringify(b)); bad++; } };
const hist = (img, L) => { const h = Array(L).fill(0); img.flat().forEach(v => h[v]++); return h; };
const F = { mean: { k: Array(9).fill(1), n: 9 }, med: { rank: 4 }, max: { rank: 8 },
  lapP: { k: [0, 1, 0, 1, -4, 1, 0, 1, 0], n: 1 }, lapN: { k: [0, -1, 0, -1, 4, -1, 0, -1, 0], n: 1 },
  sharpN: { k: [0, -1, 0, -1, 4, -1, 0, -1, 0], n: 1, post: 1 }, sharpP: { k: [0, 1, 0, 1, -4, 1, 0, 1, 0], n: 1, post: -1 },
  sobel: { kx: [-1, 0, 1, -2, 0, 2, -1, 0, 1], ky: [-1, -2, -1, 0, 0, 0, 1, 2, 1] },
  prewitt: { kx: [-1, 0, 1, -1, 0, 1, -1, 0, 1], ky: [-1, -1, -1, 0, 0, 0, 1, 1, 1] } };
const res = (img, r, c, f, pad = 'zero') => K.filter(img, r, c, F[f], pad).result;

// ---- equalization
const s36 = [[1, 4, 0, 4, 2], [2, 1, 3, 1, 4], [6, 2, 1, 7, 5], [7, 1, 5, 1, 3]];
const E36 = K.equalize(hist(s36, 8), 4);
eq(E36.s, [0, 2, 4, 4, 5, 6, 6, 7], 'slide 36 s'); eq(K.eqHist(hist(s36, 8), E36.s), [1, 0, 6, 0, 5, 3, 3, 2], 'slide 36 eq hist');
const sp25 = [[0, 0, 1, 1, 2], [0, 1, 1, 2, 4], [1, 1, 2, 4, 5], [1, 3, 4, 5, 6], [3, 3, 5, 6, 7]];
eq(K.equalize(hist(sp25, 8), 4).s, [1, 3, 4, 4, 5, 6, 7, 7], 'SP25');
eq(K.equalize([2, 3, 5, 6, 9, 12, 14, 13], 4).s, [0, 1, 1, 2, 3, 4, 6, 7], 'F25 Q1D');
const n49 = [790, 1023, 850, 656, 329, 245, 122, 81];
eq(K.equalize(n49, 2).s, [1, 3, 5, 6, 6, 7, 7, 7], 'F22 / slide 49 H');
const f23 = [[16, 30, 10, 18], [25, 1, 0, 12], [16, 13, 9, 5], [19, 14, 28, 0]];
eq(K.equalize(hist(f23, 32), 4).s, [4, 6, 6, 6, 6, 8, 8, 8, 8, 10, 12, 12, 14, 16, 17, 17, 21, 21, 23, 25, 25, 25, 25, 25, 25, 27, 27, 27, 29, 29, 31, 31], 'F23 5-bit');
const sp22 = [[11, 10, 12, 7], [6, 8, 7, 7], [5, 6, 11, 11], [9, 9, 7, 7]];
eq(K.equalize(hist(sp22, 32), 4).s, [0, 0, 0, 0, 0, 2, 6, 16, 17, 21, 23, 29, ...Array(20).fill(31)], 'SP22 5-bit');
const cw = [100, 90, 50, 20, 0, 0, 0, 0];
eq(K.eqHist(cw, K.equalize(cw, 4).s), [0, 0, 0, 100, 0, 90, 50, 20], 'slide 60 classwork');
// ---- specification
const S49 = K.specEqualize([0, 0, 0, 15, 20, 30, 20, 15], 8, 2, false).s;
eq(S49, [0, 0, 0, 1, 2, 5, 6, 7], 'slide 49 S'); eq(K.matchMap(K.equalize(n49, 2).s, S49), [3, 4, 5, 6, 6, 7, 7, 7], 'slide 49 map');
const n55 = [8, 10, 10, 2, 12, 16, 4, 2], S55 = K.specEqualize([0, 0, 0, 0, 20, 20, 16, 8], 8, 2, true).s;
eq(K.equalize(n55, 2).s, [1, 2, 3, 3, 5, 6, 7, 7], 'slide 55 H'); eq(S55, [0, 0, 0, 0, 2, 4, 6, 7], 'slide 55 S');
eq(K.matchMap(K.equalize(n55, 2).s, S55), [4, 4, 5, 5, 6, 6, 7, 7], 'slide 55 map');
const n24 = [120, 240, 160, 50, 100, 100, 210, 44], S24 = K.specEqualize([0, 0, 15, 20, 25, 20, 10, 10], 8, 4, false).s;
eq(K.equalize(n24, 4).s, [1, 2, 4, 4, 5, 5, 7, 7], 'F24 H'); eq(S24, [0, 0, 1, 2, 4, 6, 6, 7], 'F24 S');
eq(K.matchMap(K.equalize(n24, 4).s, S24), [2, 3, 4, 4, 5, 5, 7, 7], 'F24 map');
// ---- 1-D
const strip = [5, 5, 4, 3, 2, 1, 0, 0, 0, 6, 0, 0, 0, 0, 1, 3, 1, 0, 0, 0, 0, 7, 7, 7, 7];
eq(K.oneDPositions(strip, 'd1').map(x => K.oneD(strip, x, 'd1').result), [-1, -1, -1, -1, -1, 0, 0, 6, -6, 0, 0, 0, 1, 2, -2, -1, 0, 0, 0, 7, 0, 0, 0], 'strip 1st');
eq(K.oneDPositions(strip, 'd2').map(x => K.oneD(strip, x, 'd2').result), [-1, 0, 0, 0, 0, 1, 0, 6, -12, 6, 0, 0, 1, 1, -4, 1, 1, 0, 0, 7, -7, 0, 0], 'strip 2nd');
const sig = [10, 10, 10, 10, 10, 30, 50, 70, 90, 90, 90, 90, 90];
eq(K.oneDPositions(sig, 'unsharp').map(x => K.oneD(sig, x, 'unsharp').result), [10, 10, 10, 10, 3, 30, 50, 70, 97, 90, 90, 90, 90], 'unsharp');
// ---- 2-D (deck 07)
const I26 = [[153, 157, 156, 153, 155], [159, 156, 158, 156, 159], [155, 158, 154, 156, 160], [154, 157, 158, 160, 160], [157, 157, 157, 156, 155]];
eq(res(I26, 2, 2, 'lapN'), -14, 'slide 26 lap'); eq(res(I26, 2, 2, 'sharpN'), 140, 'slide 26 sharpened'); eq(res(I26, 2, 2, 'sharpP'), 140, 'positive two-step');
const c7 = [[0, 2, 6, 7], [1, 1, 6, 4], [4, 5, 2, 7], [1, 2, 6, 0]];
eq([[1, 1], [1, 2], [2, 1], [2, 2]].map(([r, c]) => res(c7, r, c, 'lapN', 'discard')), [-10, 11, 11, -16], 'classwork lap');
eq([[1, 1], [1, 2], [2, 1], [2, 2]].map(([r, c]) => K.filter(c7, r, c, F.sobel, 'discard').gx), [14, 13, 6, 5], 'classwork sobel gx');
eq([[1, 1], [1, 2], [2, 1], [2, 2]].map(([r, c]) => K.filter(c7, r, c, F.prewitt, 'discard').gx), [9, 10, 8, 3], 'classwork prewitt gx');
const s22 = [[3, 7, 6], [2, 5, 8], [3, 4, 7]];
eq([0, 1, 2].map(r => [0, 1, 2].map(c => res(s22, r, c, 'sobel'))), [[28, 32, 40], [24, 24, 22], [22, 34, 34]], 'SP22 sobel image');
eq(res([[10, 10, 10], [10, 50, 10], [10, 10, 10]], 1, 1, 'sobel'), 0, 'SP25 2d');
// ---- 2-D (deck 06)
eq(res([[110, 120, 90, 130], [91, 94, 98, 200], [90, 91, 99, 100], [82, 96, 85, 90]], 1, 1, 'mean'), 98, 'slide 19');
eq(res([[0, 12, 0, 0, 23], [255, 145, 200, 110, 17], [255, 160, 90, 250, 15], [0, 255, 130, 185, 15], [15, 20, 20, 21, 21]], 1, 1, 'med'), 145, 'F23 median');
console.log(bad ? `${bad} failures` : 'all simulator maths checks pass');
process.exitCode = bad ? 1 : 0;

// ---- compression (deck 13), expected values from scripts/solvers.py answers
const hc = (syms, w) => K.huffman(syms, w).code;
eq(hc(['a2', 'a6', 'a1', 'a4', 'a3', 'a5'], [40, 30, 10, 10, 6, 4]), { a2: '1', a6: '00', a1: '011', a4: '0100', a3: '01010', a5: '01011' }, 'slide 35 huffman');
eq(hc(['A', 'B', 'C', 'D'], [4, 3, 2, 1]), { A: '1', B: '00', C: '010', D: '011' }, 'SP25 2c huffman');
eq(hc(['P1', 'P2', 'P3', 'P4', 'P5', 'P6'], [2, 2, 3, 1, 1, 1]), { P1: '10', P2: '11', P3: '00', P4: '011', P5: '0100', P6: '0101' }, 'F24 QSB huffman');
eq(hc([160, 120, 110, 140, 170, 180].map(String), [4, 7, 5, 5, 3, 1].map(Number)) && true, true, 'smoke');
const sp24 = [180, 160, 160, 140, 120, 110, 110, 120, 140, 120, 110, 140, 120, 120, 140, 120, 160, 160, 170, 170, 170, 120, 110, 140, 110];
const cnt = a => { const m = new Map(); a.forEach(v => m.set(v, (m.get(v) || 0) + 1)); return [...m].sort((x, y) => y[1] - x[1] || x[0] - y[0]); };
const c24 = cnt(sp24);
eq(hc(c24.map(x => x[0]), c24.map(x => x[1])), { 120: '01', 110: '10', 140: '11', 160: '000', 170: '0010', 180: '0011' }, 'SP24 2c huffman');
eq(K.huffman(c24.map(x => x[0]), c24.map(x => x[1])).lavg, 2.48, 'SP24 Lavg');
const f21 = [18, 16, 16, 14, 12, 11, 11, 12, 14, 12, 11, 14, 12, 12, 14, 12, 16, 16, 17, 17, 17, 12, 11, 14, 11], c21 = cnt(f21);
eq(K.huffman(c21.map(x => x[0]), c21.map(x => x[1])).lavg, 2.48, 'F21 Lavg');
eq(K.lzw([7, 8, 40, 100, 7, 8, 40, 100, 7, 8, 40, 100, 7, 8, 40, 100]).out, [7, 8, 40, 100, 256, 258, 260, 259, 257, 100], 'SP25 LZW');
eq(K.lzw([5, 8, 8, 40, 120, 5, 8, 8, 40, 120, 5, 8, 8, 40, 120, 5, 8, 8, 40, 120]).out, [5, 8, 8, 40, 120, 256, 258, 260, 257, 259, 261, 259], 'F24 LZW');
eq(K.lzw([3, 4, 7, 3, 4, 7, 3, 4, 7]).out, [3, 4, 7, 256, 258, 257], 'SP22 LZW');
eq(K.lzw([39, 39, 126, 126, 39, 39, 126, 126, 39, 39, 126, 126, 39, 39, 126, 126]).out, [39, 39, 126, 126, 256, 258, 260, 259, 257, 126], 'slide LZW');
const A1 = K.arith(['0.1', '0.4', '0.3', '0.2'], [1, 1, 0, 3, 2]);
eq([K.dec(A1.L, A1.scale), K.dec(A1.Hh, A1.scale), K.dec(A1.q, A1.scale)], ['0.1544', '0.15536', '0.155'], 'F24 arithmetic');
const A2 = K.arith(['0.2', '0.2', '0.4', '0.2'], [0, 1, 2, 2, 3]);
eq([K.dec(A2.L, A2.scale), K.dec(A2.Hh, A2.scale), K.dec(A2.q, A2.scale)], ['0.06752', '0.0688', '0.068'], 'slide arithmetic');
eq(K.golomb(9, 4).code, '11001', 'G4(9)'); eq(K.golomb(7, 1).code, '11111110', 'G1(7)'); eq(K.golomb(7, 2).code, '11101', 'G2(7)'); eq(K.golomb(7, 4).code, '1011', 'G4(7)');
eq(K.rle([..."AAAAABBBCCDAA"]).map(r => r.v + r.n).join(' '), 'A5 B3 C2 D1 A2', 'SP25 RLE');
console.log(bad ? `${bad} failures` : 'all compression checks pass');
process.exitCode = bad ? 1 : 0;

// ---- morphology (decks 11-12), expected values from scripts/solvers.py answers
const P = rows => rows.map(r => [...r].map(ch => (ch === '#' ? 1 : 0)));
const cross = [[0, 1, 0], [1, 1, 1], [0, 1, 0]];
const FF = P(['.....#', '..###.', '.####.', '.###..', '#.....']), V = [[1], [1], [1]];
const z = M => M.map(r => r.map(v => v ?? 0));
eq(K.morphImage(FF, V, [1, 0], 'dilate'), [[0, 0, 1, 1, 1, 1], [0, 1, 1, 1, 1, 1], [0, 1, 1, 1, 1, 0], [1, 1, 1, 1, 1, 0], [1, 1, 1, 1, 0, 0]], 'SP22 dilate');
eq(K.morphImage(K.morphImage(FF, V, [1, 0], 'erode'), V, [1, 0], 'dilate'), [[0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 1, 1, 0, 0], [0, 0, 0, 0, 0, 0]], 'SP22 open');
eq(K.morphImage(K.morphImage(FF, V, [1, 0], 'dilate'), V, [1, 0], 'erode'), [[0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 1, 0], [0, 1, 1, 1, 1, 0], [0, 1, 1, 1, 0, 0], [0, 0, 0, 0, 0, 0]], 'SP22 close');
eq(K.morphImage(FF.map(r => r.map(v => 1 - v)), V, [1, 0], 'erode'), [[0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 0], [1, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0]], 'SP22 complement erode');
const X = P(['......', '...##.', '......', '......', '..#...', '...#..', '....#.']), Y = P(['.####.', '.###..', '......', '#.#...', '##.#..', '.##.#.', '..##..']);
const B23 = [[1, 0, 1], [1, 1, 0]];
eq(K.morphImage(X, B23, [1, 2], 'dilate'), Y, 'SP23 X dilate = Y'); eq(K.morphImage(Y, B23, [1, 2], 'erode'), X, 'SP23 Y erode = X');
const sq = [[1, 1, 1], [1, 1, 1], [1, 1, 1]], A25 = P(['......', '.####.', '.####.', '.####.', '.####.', '......']);
eq(K.minus(A25, K.morphImage(A25, sq, [1, 1], 'erode')), P(['......', '.####.', '.#..#.', '.#..#.', '.####.', '......']), 'F25 boundary');
const op1 = P(['....###.', '....###.', '....###.', '...##...', '.###....', '.###....', '.###....', '........']);
eq(K.morphImage(K.morphImage(op1, cross, [1, 1], 'erode'), cross, [1, 1], 'dilate'), P(['.....#..', '....###.', '.....#..', '........', '..#.....', '.###....', '..#.....', '........']), 'slide 87 opening');
const corner = [[null, 1, null], [0, 1, 1], [0, 0, null]];
const CS = P(['.............', '.#####.#####.', '.#...#.#...#.', '.#.....#.....', '.#.....#####.', '.#.........#.', '.#...#.#...#.', '.#####.#####.']);
eq(K.morphImage(CS, corner, [1, 1], 'hmt').flat().filter(Boolean).length, 3, 'F23 HMT B1 count');
const e1 = [[null, null, null], [0, 1, 0], [null, 0, null]];
const A22 = P(['...#..#..#...', '...#...#####.', '...#.#...#...', '.#.###...#...', '.........###.', '.#######.....', '.............']);
eq(K.morphImage(A22, e1, [1, 1], 'hmt').flat().filter(Boolean).length, 2, 'F22 HMT E1 count');
eq(z(K.morphImage([[1, 0, 0, 0, 1, 1, 1, 0, 1, 1]], [[1, 1, 1]], [0, 1], 'erode', true)).flat().slice(1, 9), [0, 0, 0, 0, 1, 0, 0, 0], '1-D erosion slide 26');
eq(z(K.morphImage([[1, 0, 0, 0, 1, 1, 1, 0, 1, 1]], [[1, 1, 1]], [0, 1], 'dilate', true)).flat().slice(1, 9), [1, 0, 1, 1, 1, 1, 1, 1], '1-D dilation slide 57');

// chain code (deck 10): paths are (row, col), answers from data/answers.json
const D = s => [...s].map(Number), J = a => a.join('');
const chainAll = (path, n = 8, rule = 'next') => { const cc = K.chainCode(K.unitPath(path), n), d = K.firstDiff(cc, n, rule); return { cc: J(cc), cfd: J(d), ncfd: J(K.minRot(d).best), sn: J(K.minRot(cc).best) }; };
const F25 = chainAll([[1, 2], [2, 1], [3, 0], [4, 1], [5, 1], [6, 2], [5, 3], [4, 4], [3, 4], [2, 3]]);
eq([F25.cc, F25.cfd, F25.ncfd, F25.sn], ['5576711233', '0271201102', '0110202712', '1123355767'], 'F25 quiz chain');
const SP24 = chainAll([[0, 2], [0, 3], [0, 4], [1, 5], [2, 6], [3, 5], [4, 5], [5, 4], [6, 3], [6, 2], [5, 1], [4, 1], [3, 1], [2, 1], [1, 2]]);
eq([SP24.cc, SP24.cfd, SP24.ncfd], ['007756554322212', '070617077700716', '007160706170777'], 'SP24 / slide 12 chain');
const SP22 = chainAll([[3, 5], [4, 6], [5, 5], [6, 4], [5, 3], [4, 2], [3, 1], [2, 2], [1, 3], [0, 4], [1, 5], [2, 6]].map(([x, y]) => [-y, x]));
eq([SP22.cc, SP22.cfd, SP22.ncfd, SP22.sn], ['177555333117', '606006006062', '006006062606', '117177555333'], 'SP22 chain (x,y axes)');
const F21 = chainAll([[8, 3], [7, 4], [6, 5], [6, 6], [6, 7], [5, 7], [4, 8], [4, 9], [4, 10], [3, 10], [2, 9], [1, 8], [0, 7], [0, 6], [0, 5], [0, 4], [1, 3], [2, 3], [3, 2], [4, 1], [5, 1], [6, 1], [7, 2]]);
eq([F21.cc, F21.ncfd], ['11002100233344456556677', '00100117010102070277021'], 'F21 chain');
const V24 = [[1, 1], [1, 3], [3, 3], [3, 5], [1, 5], [1, 7], [4, 7], [4, 5], [5, 5], [5, 4], [6, 4], [6, 3], [7, 3], [7, 1]], U24 = K.unitPath(V24);
[[[1, 1], '0066002200666446464644222222', '0602020606006026262606000006'], [[3, 3], '0022006664464646442222220066', '0206060060262626060000060602'], [[7, 1], '2222220066002200666446464644', '0000060602020606006026262606']].forEach(([st, cc, cfd]) => {
  const j = U24.findIndex(p => p[0] === st[0] && p[1] === st[1]), path = U24.slice(j).concat(U24.slice(0, j)), c = K.chainCode(path), d = K.firstDiff(c);
  eq([J(c), J(d), J(K.minRot(d).best)], [cc, cfd, '0000060602020606006026262606'], `F24 start ${st}`);
});
const c23 = D('1100223344557766');
eq(K.chainCode(K.pathFromCode(c23)), c23, 'SP23 code -> path -> code');
eq([J(K.minRot(c23).best), J(K.minRot(K.firstDiff(c23)).best)], ['0022334455776611', '0101010207030702'], 'SP23 shape number / NCFD');
eq(J(K.chainCode(K.unitPath([[4, 1], [4, 3], [3, 4], [2, 4], [1, 3], [0, 3], [0, 1], [1, 1], [2, 0], [3, 0]]))), '001232446567', 'slide 13 hexagon');
['444201066', '066444201', '067644222'].forEach((c, k) => eq(J(K.minRot(K.firstDiff(D(c), 8, 'prev')).best), '002271202', `slide 23 shape ${k + 1} (this - next rule)`));
eq(J(K.firstDiff(D('444201066'), 8, 'prev')), '002271202', 'slide 23 normalised curvature');
['03032211', '03221103', '01033221', '10033212'].forEach(c => { const d = K.firstDiff(D(c), 4); eq(J(K.minRot(d).best), '03033133', `slide 22 ${c} NCFD`); eq(J(K.chainCode(K.pathFromCode(D(c), 4), 4)), c, `slide 22 ${c} path`); });
eq(J(K.firstDiff(D('03032211'), 4)), '31330303', 'slide 22 CFD');
eq(J(K.chainCode(K.unitPath([[0, 3], [0, 4], [1, 5], [5, 5], [7, 3], [5, 1], [4, 1], [3, 2], [2, 2], [1, 3]]))), '076666553321212', 'slide 29 class work');
eq(K.minRot(D('202002271')).idx, 3, 'minRot index');

// colour (deck 14): slide 20 CMY and the practice HSI from data/answers.json
const r4 = x => Math.round(x * 10000) / 10000;
eq(K.cmy(98, 35, 146).map(x => Math.round(x * 1000) / 1000), [0.616, 0.863, 0.427], 'slide 20 RGB(98,35,146) -> CMY');
const HX = K.hsi(200, 100, 50);
eq([Math.round(HX.theta * 100) / 100, Math.round(HX.H * 100) / 100, r4(HX.S), r4(HX.I)], [19.11, 19.11, 0.5714, 0.4575], 'practice RGB(200,100,50) -> HSI');
const Bl = K.hsi(0, 0, 255); eq([Math.round(Bl.H), r4(Bl.S), r4(Bl.I)], [240, 1, 0.3333], 'pure blue H = 240');
const Gy = K.hsi(128, 128, 128); eq([Gy.H, r4(Gy.S)], [null, 0], 'gray: hue undefined, S = 0');

// Canny steps 3-5 (deck 08): F23 Q3(a) from data/answers.json, slide 59 (gN given)
const M23 = [[200, 40, 57], [10, 20, 101], [50, 41, 74]], D23 = [['↓', '↓', '↙'], ['→', '↑', '←'], ['↑', '↑', '←']];
const C23 = K.canny(M23, D23, 100, 45);
eq(C23.gN, [[200, 40, 57], [0, 0, 101], [50, 41, 74]], 'F23 NMS');
eq(C23.g, [[200, 0, 57], [0, 0, 101], [0, 0, 74]], 'F23 final');
eq(K.canny(M23, D23, 245, 10).g.flat().filter(Boolean).length, 0, 'F23 (iii) TH 245: empty');
eq(K.canny([[200, 0, 57], [0, 45, 101], [50, 0, 0]], null, 100, 45).g, [[200, 0, 57], [0, 45, 101], [0, 0, 0]], 'slide 59');

// region growing + iterative threshold (deck 09, data/answers.json RGN/*)
const RG = [[10, 10, 10, 10, 10, 10, 10], [10, 10, 10, 69, 70, 10, 10], [59, 10, 60, 64, 59, 56, 60], [10, 59, 10, 60, 70, 10, 62], [10, 60, 59, 65, 67, 10, 65], [10, 10, 10, 10, 10, 10, 10], [10, 10, 10, 10, 10, 10, 10]];
eq(K.grow(RG, [3, 3], 5, 4).region.length, 13, 'slide 15 region growing, 4-connectivity');
eq(K.grow(RG, [3, 3], 5, 8).region.length, 17, 'slide 17 region growing, 8-connectivity');
const TR = K.iterT([10, 12, 15, 11, 200, 190, 205, 14, 198, 13, 201, 16]);
eq([Math.round(TR[0].T * 1000) / 1000, Math.round(TR[TR.length - 1].Tn * 10) / 10, TR.length], [90.417, 105.9, 2], 'iterative threshold practice');

// paths (deck 03, data/answers.json PIX/*)
const S22 = [[1, 4, 3, 4], [2, 3, 4, 7], [0, 5, 1, 6], [3, 4, 7, 1]];
eq(K.findPath(S22, [0, 1, 2, 4], [0, 0], [3, 3], 4).path, null, 'SP22 4-path absent');
eq(K.findPath(S22, [0, 1, 2, 4], [0, 0], [3, 3], 'm').path, [[0, 0], [0, 1], [1, 2], [2, 2], [3, 3]], 'SP22 m-path');
const F21i = [[0, 0, 0, 3, 2, 2, 1, 2, 1, 2], [0, 1, 0, 2, 1, 1, 1, 2, 2, 0], [0, 0, 0, 1, 1, 1, 0, 2, 3, 2], [0, 0, 1, 0, 0, 2, 2, 3, 2, 2], [0, 0, 1, 1, 1, 0, 0, 1, 1, 1]];
eq(K.findPath(F21i, [1, 2], [3, 2], [0, 6], 4).path, null, 'F21 V={1,2} no 4-path');
eq(K.findPath(F21i, [0, 1], [3, 2], [0, 6], 4).path, [[3, 2], [2, 2], [2, 3], [2, 4], [1, 4], [1, 5], [1, 6], [0, 6]], 'F21 V={0,1} 4-path');
const S23e = [[9, 34, 20, 0], [16, 21, 50, 5], [5, 6, 11, 15], [7, 8, 10, 2], [8, 7, 9, 0]];
eq(K.findPath(S23e, [10, 20, 9, 7, 0, 5, 1, 3], [2, 0], [4, 2], 8).path, [[2, 0], [3, 0], [4, 1], [4, 2]], 'SP23 8-path');

// nearest-neighbour zoom (deck 02, data/answers.json PIX/NNI*)
eq(K.nnZoom([[10, 4, 22], [2, 18, 7], [9, 14, 25]], 6, 6).out, [[10, 10, 4, 4, 22, 22], [10, 10, 4, 4, 22, 22], [2, 2, 18, 18, 7, 7], [2, 2, 18, 18, 7, 7], [9, 9, 14, 14, 25, 25], [9, 9, 14, 14, 25, 25]], 'slides 49-54 3x3 -> 6x6');
eq(K.nnZoom([[1, 4], [3, 7]], 5, 5).rp, [1, 1, 2, 2, 2], 'class work 2x2 -> 5x5 positions');
eq(K.nnZoom([[1, 4, 3, 7], [2, 3, 4, 5], [2, 6, 4, 3], [4, 7, 1, 0]], 7, 7).rp, [1, 2, 2, 3, 3, 4, 4], 'class work 4x4 -> 7x7 positions');
eq(K.nnZoom([[1, 4, 3], [7, 2, 3], [5, 6, 0]], 9, 9).out[3], [7, 7, 7, 2, 2, 2, 3, 3, 3], 'class work 3x3 -> 9x9 row 4');
console.log(bad ? `${bad} failures` : 'all morphology + chain code + colour + Canny + region + path + zoom checks pass');
process.exitCode = bad ? 1 : 0;
