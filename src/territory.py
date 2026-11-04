# 疆域算法（规范第十三节）：归属点 + 通行代价栅格 + 多源最短路
# 每个州郡归属点（seeds）分得一块「势力格」，只算一次；各时间节点按归属把势力格合并成疆域。
# 1 栅格  2 代价  3 16 邻接多源 Dijkstra  4 外缘（手绘）  5 高斯平滑 + 等值界线 → 覆盖图  6 位移场 + 覆盖简化
import json, math, pickle, time
import numpy as np
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from skimage.draw import polygon as draw_polygon
import shapely
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import unary_union
import config as C
from proj import proj, inv
from seeds import SEEDS
from frontier import outer_proj
import items as IT

OUT = C.BUILD / 'cells.pkl'


def log(*a):
    print('  [疆域]', *a, flush=True)


# ---------------- 1 栅格 ----------------
def grid():
    W, E, S, N = C.GRID_BOX
    lons = np.r_[np.linspace(W, E, 200), np.full(200, E), np.linspace(E, W, 200), np.full(200, W)]
    lats = np.r_[np.full(200, N), np.linspace(N, S, 200), np.full(200, S), np.linspace(S, N, 200)]
    bx, by = proj(lons, lats)
    X0, Y0 = math.floor(bx.min()), math.floor(by.min())
    NX, NY = int((bx.max() - X0) / C.PX) + 1, int((by.max() - Y0) / C.PX) + 1
    return X0, Y0, NX, NY, Polygon(list(zip(bx, by)))


class G:
    pass


def to_rc(x, y):
    """投影坐标 → 栅格行列（格心为整数）"""
    return (np.asarray(y) - G.Y0) / C.PX - .5, (np.asarray(x) - G.X0) / C.PX - .5


def to_xy(c, r):
    return G.X0 + (np.asarray(c) + .5) * C.PX, G.Y0 + (np.asarray(r) + .5) * C.PX


def fill(geom):
    """多边形（投影坐标）→ 布尔栅格，按格心是否在内"""
    m = np.zeros((G.NY, G.NX), bool)
    polys = geom.geoms if hasattr(geom, 'geoms') else [geom]
    for p in polys:
        if p.is_empty or p.geom_type != 'Polygon': continue
        r, c = to_rc(*np.array(p.exterior.coords).T)
        rr, cc = draw_polygon(r, c, m.shape); m[rr, cc] = True
        for h in p.interiors:
            r, c = to_rc(*np.array(h.coords).T)
            rr, cc = draw_polygon(r, c, m.shape); m[rr, cc] = False
    return m


def burn(lines_ll, step=0.25):
    """经纬度折线 → 布尔栅格（沿线每 step 格取样）"""
    m = np.zeros((G.NY, G.NX), bool)
    for pts in lines_ll:
        a = np.array(pts, float)
        if len(a) < 2: continue
        x, y = proj(a[:, 0], a[:, 1])
        r, c = to_rc(x, y)
        for i in range(len(a) - 1):
            n = max(2, int(math.hypot(r[i + 1] - r[i], c[i + 1] - c[i]) / step) + 1)
            rr = np.rint(np.linspace(r[i], r[i + 1], n)).astype(int)
            cc = np.rint(np.linspace(c[i], c[i + 1], n)).astype(int)
            ok = (rr >= 0) & (rr < G.NY) & (cc >= 0) & (cc < G.NX)
            m[rr[ok], cc[ok]] = True
    return m


def smooth_noise(rng, sigma):
    n = ndimage.gaussian_filter(rng.standard_normal((G.NY, G.NX)), sigma, mode='wrap')
    return n / n.std()


def pgeom(rings_ll):
    rings = []
    for r in rings_ll:
        a = np.array(r); x, y = proj(a[:, 0], a[:, 1]); rings.append(list(zip(x, y)))
    return Polygon(rings[0], rings[1:]).buffer(0)


def wiggle(pts, rng, amp):
    """手绘脊线加一点横向摆动：每 0.05° 插值，沿法向平移一条平滑随机曲线"""
    a = np.array(pts, float)
    seg = np.hypot(*np.diff(a, axis=0).T)
    s = np.r_[0, np.cumsum(seg)]
    if s[-1] <= 0: return a
    t = np.linspace(0, s[-1], max(3, int(s[-1] / .05)))
    p = np.c_[np.interp(t, s, a[:, 0]), np.interp(t, s, a[:, 1])]
    d = np.gradient(p, axis=0); d /= np.maximum(np.hypot(d[:, 0], d[:, 1]), 1e-9)[:, None]
    nrm = np.c_[-d[:, 1], d[:, 0]]
    off = ndimage.gaussian_filter1d(rng.standard_normal(len(t)), 6, mode='nearest')
    off = off / max(np.abs(off).max(), 1e-9) * amp
    off *= np.sin(np.linspace(0, math.pi, len(t))) ** .5     # 两端不动
    return p + nrm * off[:, None]


def main():
    t0 = time.time()
    rng = np.random.default_rng(C.SEED)
    G.X0, G.Y0, G.NX, G.NY, box = grid()
    log('栅格', G.NX, '×', G.NY, f'（{C.PX} 单位 ≈ {C.PX * 6.371:.1f} km）')
    BASE = json.load(open(C.BUILD / 'geo_base.json', encoding='utf-8'))

    # 陆地、大湖、外缘
    land_p = unary_union([pgeom(p) for p in BASE['land']])
    big = [lk for lk in BASE['lakes'] if Polygon(lk['r']).area > C.BIG_LAKE]
    lakes_p = unary_union([pgeom([lk['r']]) for lk in big])
    land = fill(land_p) & fill(box)
    lake = fill(lakes_p) & land
    land &= ~lake
    OUTER = outer_proj(proj)
    inner = fill(OUTER.buffer(C.PX * 3))

    # ---------------- 2 代价 ----------------
    ez = np.loadtxt(C.GEODATA / 'etopo20data.gz'); elo = np.loadtxt(C.GEODATA / 'etopo20lons.gz'); ela = np.loadtxt(C.GEODATA / 'etopo20lats.gz')
    CX, CY = np.meshgrid(*to_xy(np.arange(G.NX), np.arange(G.NY)))
    glon, glat = inv(CX, CY)
    fi = (glon - elo[0]) / (elo[1] - elo[0]); fj = (glat - ela[0]) / (ela[1] - ela[0])
    elev = ndimage.map_coordinates(ez, [fj, fi], order=1, mode='nearest')
    elev = np.where(land, np.maximum(elev, 0), 0)
    gy, gx = np.gradient(ndimage.gaussian_filter(elev, 1.2))
    slope = np.hypot(gx, gy) / (C.PX * 6.371)                 # 米/公里
    lo, hi, add = C.PLATEAU
    cost = 1 + C.SLOPE_K * np.clip(slope, 0, C.SLOPE_MAX) + add * np.clip((elev - lo) / (hi - lo), 0, 1)

    # 山脊带：主干 / 次要分别烧线，按距离加高斯形代价
    major, minor = [], []
    ranges = [(it['geo'], bool(it.get('major'))) for it in IT.TS if it['c'] == 'range' and it.get('geo')]
    ranges += [(geo, bool(mj)) for o, m, note, geo, anc, mj in IT.NEWRANGE]
    for geo, mj in ranges:
        a = np.array(geo, float)
        if np.hypot(*np.diff(a, axis=0).T).sum() < C.RIDGE_MIN_LEN: continue
        (major if mj else minor).append(wiggle(a, rng, C.RIDGE_WIGGLE))
    gauss = lambda m, w: np.exp(-ndimage.distance_transform_edt(~m) ** 2 / (2 * w * w)) if m.any() else 0
    ridge = np.maximum(C.RIDGE_MAJOR * gauss(burn(major), C.RIDGE_W), C.RIDGE_MINOR * gauss(burn(minor), C.RIDGE_W))
    log('山脊', len(major), '主干', len(minor), '次要')

    # 界河
    river = np.zeros_like(cost)
    for key, v in C.BORDER_RIVERS.items():
        lines = [r['p'] for r in BASE['rivers'] if (r.get('ts_it') == key or r.get('key') == key) and len(r['p']) > 1]
        if lines: river = np.maximum(river, v * gauss(burn(lines), C.RIVER_W))
    cost = cost + ridge + river

    # 多尺度平滑噪声
    noise = sum(w * smooth_noise(rng, s) for s, w in C.NOISE_SCALES)
    noise = np.clip(noise / noise.std(), -2.2, 2.2) / 2.2
    cost *= 1 + C.NOISE_AMP * noise
    log('代价', f'{cost[land].min():.2f}—{cost[land].max():.2f}', f'{time.time() - t0:.0f}s')

    # ---------------- 3 多源 Dijkstra（16 邻接，含马步） ----------------
    node = land & inner
    nid = np.full((G.NY, G.NX), -1, np.int64)
    NN = int(node.sum()); nid[node] = np.arange(NN)
    rows, cols, wts = [], [], []
    for dr, dc in ((0, 1), (1, -1), (1, 0), (1, 1), (1, -2), (1, 2), (2, -1), (2, 1)):
        L = math.hypot(dr, dc)
        sa = (slice(0, G.NY - dr), slice(0, G.NX - dc) if dc >= 0 else slice(-dc, G.NX))
        sb = (slice(dr, G.NY), slice(dc, G.NX) if dc >= 0 else slice(0, G.NX + dc))
        a, b, ca, cb = nid[sa], nid[sb], cost[sa], cost[sb]
        ok = (a >= 0) & (b >= 0)
        rows.append(a[ok]); cols.append(b[ok]); wts.append(L * (ca[ok] + cb[ok]) / 2)
    graph = coo_matrix((np.concatenate(wts), (np.concatenate(rows), np.concatenate(cols))), shape=(NN, NN)).tocsr()
    log('图', NN, '点', graph.nnz, '边')

    starts, owner = [], []
    for i, s in enumerate(SEEDS):
        x, y = proj(s['lon'], s['lat'])
        r, c = (int(round(float(v))) for v in to_rc(x, y))
        if not (0 <= r < G.NY and 0 <= c < G.NX): log('归属点在范围外', s['id']); continue
        if not node[r, c]:
            k = C.SEED_SNAP
            sub = node[max(0, r - k):r + k + 1, max(0, c - k):c + k + 1]
            ys, xs = np.nonzero(sub)
            if len(ys) == 0: log('归属点在海中', s['id']); continue
            j = np.argmin((ys - min(r, k)) ** 2 + (xs - min(c, k)) ** 2)
            r, c = max(0, r - k) + ys[j], max(0, c - k) + xs[j]
        if nid[r, c] in starts:
            # 两点落在同一格：挪到旁边一格
            for dr, dc in ((0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1)):
                if node[r + dr, c + dc] and nid[r + dr, c + dc] not in starts: r, c = r + dr, c + dc; break
        starts.append(int(nid[r, c])); owner.append(i)
    dist, _, src = dijkstra(graph, directed=False, indices=starts, min_only=True, return_predecessors=True)
    seed_of = np.full(NN, -1, np.int32)
    seed_of[np.array(starts)] = np.array(owner)
    lab_n = np.where(src >= 0, seed_of[np.maximum(src, 0)], -1)
    lab = np.full((G.NY, G.NX), -1, np.int32)
    lab[node] = lab_n
    log('最短路', f'{time.time() - t0:.0f}s', '未达', int((lab_n < 0).sum()))

    # ---------------- 4 外缘以外不属任何政权；海面、大湖、近岸无归属点的小岛就近延伸 ----------------
    # （台湾、济州、对马等离岸较远又无归属点的岛屿留空）
    d, (ir, ic) = ndimage.distance_transform_edt(lab < 0, return_indices=True)
    ext = lab[ir, ic]
    lab = np.where((lab < 0) & inner & (lake | (d <= C.FILL_SEA)), ext, lab)

    # ---------------- 5 平滑 → 等值界线 → 覆盖图 ----------------
    # 每类（归属点，以及 -1 = 界外）的指示栅格作高斯平滑，每格归平滑值最大的一类。
    # 界线描在相邻两类平滑值相等处（两类时即各自的 0.5 等值线）：沿格边线性插值求交点，
    # 每个对偶方格内两点连线，三类以上相交处连到交点均值。界线全图只描一次、两侧共用，
    # 因此相邻疆域之间既无白缝也无叠色，交汇处不留小缝。
    sig = C.SMOOTH_SIGMA
    pad = int(4 * sig) + 3
    classes = [-1] + sorted(set(int(v) for v in np.unique(lab)) - {-1})
    objs = ndimage.find_objects(lab + 1)

    def field(k):
        if k == -1:
            return 0, G.NY, 0, G.NX, ndimage.gaussian_filter((lab == -1).astype(float), sig, mode='nearest')
        sl = objs[k]
        r0, r1 = max(0, sl[0].start - pad), min(G.NY, sl[0].stop + pad)
        c0, c1 = max(0, sl[1].start - pad), min(G.NX, sl[1].stop + pad)
        return r0, r1, c0, c1, ndimage.gaussian_filter((lab[r0:r1, c0:c1] == k).astype(float), sig, mode='constant')

    best = np.full((G.NY, G.NX), -1.0); arg = np.full((G.NY, G.NX), -1, np.int32)
    for k in classes:
        r0, r1, c0, c1, f = field(k)
        sub = best[r0:r1, c0:c1]; up = f > sub
        sub[up] = f[up]; arg[r0:r1, c0:c1][up] = k
    # 平滑后整块消失的小州：保留其原格
    gone = [k for k in classes[1:] if not (arg == k).any()]
    for k in gone: arg[lab == k] = k
    if gone: log('小州保留原格', [SEEDS[k]['id'] for k in gone])

    # 格边交点：水平边 (r,c)-(r,c+1)，竖直边 (r,c)-(r+1,c)
    hr, hc = np.nonzero(arg[:, :-1] != arg[:, 1:])
    vr, vc = np.nonzero(arg[:-1, :] != arg[1:, :])
    er = np.r_[hr, vr]; ec = np.r_[hc, vc]
    qr = np.r_[hr, vr + 1]; qc = np.r_[hc + 1, vc]
    A = arg[er, ec]; B = arg[qr, qc]
    fAp, fAq, fBp, fBq = (np.zeros(len(er)) for _ in range(4))
    for k in classes:
        r0, r1, c0, c1, f = field(k)
        for m, (o1, o2) in ((A == k, (fAp, fAq)), (B == k, (fBp, fBq))):
            idx = np.nonzero(m)[0]
            if len(idx) == 0: continue
            o1[idx] = f[er[idx] - r0, ec[idx] - c0]; o2[idx] = f[qr[idx] - r0, qc[idx] - c0]
    dp, dq = fAp - fBp, fAq - fBq
    den = dp - dq
    t = np.clip(np.where(np.abs(den) > 1e-12, dp / np.where(np.abs(den) > 1e-12, den, 1), .5), 1e-3, 1 - 1e-3)
    nh = len(hr)
    px = np.r_[hc + t[:nh], vc.astype(float)]
    py = np.r_[hr.astype(float), vr + t[nh:]]
    hid = np.full((G.NY, G.NX), -1, np.int64); vid = np.full((G.NY, G.NX), -1, np.int64)
    hid[hr, hc] = np.arange(nh); vid[vr, vc] = nh + np.arange(len(vr))
    # 对偶方格 (r,c)：上 hid[r,c]、右 vid[r,c+1]、下 hid[r+1,c]、左 vid[r,c]
    sq = np.stack([hid[:-1, :-1], vid[:-1, 1:], hid[1:, :-1], vid[:-1, :-1]], -1).reshape(-1, 4)
    n = (sq >= 0).sum(1)
    # 顶点：格边交点 0..E-1，三类以上交汇的对偶方格另加一个交点
    E = len(px)
    edges = []
    two = sq[n == 2]
    if len(two): edges.append(np.sort(two, 1)[:, 2:])        # 两个非 -1
    many = sq[n >= 3]
    jx, jy = np.zeros(0), np.zeros(0)
    if len(many):
        ok = many >= 0
        jx = np.where(ok, px[np.maximum(many, 0)], 0).sum(1) / ok.sum(1)
        jy = np.where(ok, py[np.maximum(many, 0)], 0).sum(1) / ok.sum(1)
        jid = E + np.arange(len(many))
        for j in range(4):
            m = ok[:, j]
            edges.append(np.c_[many[m, j], jid[m]])
    edges = np.concatenate(edges)
    P = np.c_[np.r_[px, jx], np.r_[py, jy]]
    faces = list(shapely.get_parts(shapely.polygonize(shapely.linestrings(P[edges]))))
    log('界线', len(edges), '段', '面', len(faces), f'{time.time() - t0:.0f}s')

    # 每个面内至少含一个格心，取其类别
    fa = shapely.area(np.array(faces, dtype=object))
    reps = shapely.point_on_surface(np.array(faces, dtype=object))
    cls = []
    for fc, p in zip(faces, reps):
        r, c = int(round(p.y)), int(round(p.x))
        k = None
        for dr, dc in ((0, 0), (0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < G.NY and 0 <= cc < G.NX and fc.contains(shapely.Point(cc, rr)):
                k = int(arg[rr, cc]); break
        cls.append(int(arg[min(G.NY - 1, max(0, r)), min(G.NX - 1, max(0, c))]) if k is None else k)
    # 小于 C.MIN_FACE 格的零星碎块（不是该类最大的一块）并入共边最长的相邻面
    small = fa < C.MIN_FACE
    for k in sorted(set(cls)):
        small[max((i for i, c in enumerate(cls) if c == k), key=lambda i: fa[i])] = False
    tree = shapely.STRtree(faces)
    nm = 0
    for i in np.argsort(fa, kind='stable'):
        if not small[i]: continue
        best_c, best_l = cls[i], 0.0
        for j in sorted(tree.query(faces[i], predicate='intersects')):
            if j == i: continue
            L = faces[i].boundary.intersection(faces[j].boundary).length
            if L > best_l + 1e-9: best_c, best_l = cls[j], L
        nm += best_c != cls[i]; cls[i] = best_c
    # 界线网络整体做几轮拉普拉斯平滑（每个顶点挪向相邻顶点的均值），抹掉格点插值留下的小折角和细刺；
    # 顶点两侧共用，平滑后相邻疆域仍是同一条线。平滑后重新成面，按与原面重叠最多者归类。
    V = len(P)
    adj = coo_matrix((np.ones(2 * len(edges)), (np.r_[edges[:, 0], edges[:, 1]], np.r_[edges[:, 1], edges[:, 0]])), shape=(V, V)).tocsr()
    deg = np.asarray(adj.sum(1)).ravel()
    lam = np.where(deg == 2, C.LAPLACE[0], np.where(deg >= 3, C.LAPLACE[0] * .5, 0))[:, None]
    Q = P.copy()
    for _ in range(C.LAPLACE[1]):
        Q = Q + lam * (adj @ Q / np.maximum(deg, 1)[:, None] - Q)
    new = list(shapely.get_parts(shapely.polygonize(shapely.linestrings(Q[edges]))))
    if len(new) == len(faces):
        tree = shapely.STRtree(faces)
        ncls = []
        for g in new:
            js = tree.query(g, predicate='intersects')
            ncls.append(cls[max(js, key=lambda j: g.intersection(faces[j]).area)])
        faces, cls = new, ncls
    else:
        log('平滑后面数不符，沿用未平滑界线', len(new), len(faces))
    by = {}
    for fc, k in zip(faces, cls): by.setdefault(k, []).append(fc)
    keys = sorted(by)
    log('碎块并入', nm)
    cov = [unary_union(by[k]) for k in keys]

    # ---------------- 6 位移场：界线带上河曲一样的小弯（两种尺度），再整体覆盖简化 ----------------
    wr = np.zeros((G.NY, G.NX)); wc = np.zeros((G.NY, G.NX))
    for s_, amp in C.WARP:
        for w in (wr, wc):
            n = ndimage.gaussian_filter(rng.standard_normal((G.NY, G.NX)), s_, mode='wrap')
            w += n * (amp / n.std())

    def warp_to_xy(a):
        c, r = a[:, 0], a[:, 1]
        dr = ndimage.map_coordinates(wr, [r, c], order=1, mode='nearest')
        dc = ndimage.map_coordinates(wc, [r, c], order=1, mode='nearest')
        x, y = to_xy(c + dc, r + dr)
        return np.c_[x, y]

    cov = [shapely.transform(g, warp_to_xy) for g in cov]
    cov = shapely.coverage_simplify(np.array(cov, dtype=object), tolerance=C.SIMPLIFY * C.PX)

    cells = {}
    for k, g in zip(keys, cov):
        if k < 0: continue
        g = g.buffer(0).intersection(OUTER)
        ps = [p for p in (g.geoms if hasattr(g, 'geoms') else [g]) if p.geom_type == 'Polygon' and p.area > C.MIN_PART]
        if ps: cells[k] = MultiPolygon(ps)
    pickle.dump({'cells': cells, 'outer': OUTER, 'land_p': land_p.difference(lakes_p)}, open(OUT, 'wb'))
    missing = [SEEDS[i]['id'] for i in range(len(SEEDS)) if i not in cells]
    log('势力格', len(cells), '缺', missing, f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
