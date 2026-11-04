# 疆域草图：python tools/preview.py 669 → build/preview-669.png（取该年及以前最近的节点）
import json, re, sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'src')]
from proj import proj   # noqa: E402

CJK = [f for f in ('Noto Sans CJK SC', 'Source Han Sans SC', 'PingFang SC', 'Microsoft YaHei', 'SimHei')
       if any(f == x.name for x in font_manager.fontManager.ttflist)]
if CJK: plt.rcParams['font.family'] = CJK[:1]


def dec(f):
    x = y = 0; out = []
    for i in range(0, len(f), 2):
        x += f[i]; y += f[i + 1]; out.append((x / 100, y / 100))
    return out


def rings_path(rings):
    verts, codes = [], []
    for r in rings:
        pts = dec(r); x, y = proj([p[0] for p in pts], [p[1] for p in pts])
        verts += list(zip(x, -y)); codes += [MPath.MOVETO] + [MPath.LINETO] * (len(pts) - 1)
    return MPath(verts, codes)


def main(year):
    D = json.load(open(ROOT / 'build' / 'out_data.json', encoding='utf-8'))
    G, U = D['GEO'], D['DATA']['units']
    cols = dict(re.findall(r'--u-(\d+):(#[0-9A-Fa-f]{6})', D['css_l']))
    j = max([i for i, s in enumerate(G['snaps']) if s['y'] <= year] or [0])
    sn = G['snaps'][j]
    fig, ax = plt.subplots(figsize=(14, 9), dpi=110)
    for poly in G['land']: ax.add_patch(PathPatch(rings_path(poly), fc='#ECEBE3', ec='#A9AFAE', lw=.4))
    for u, pi in sn['z'].items():
        ax.add_patch(PathPatch(rings_path(G['pool'][pi]), fc=cols.get(u, '#999'), ec='#333', lw=.5, alpha=.75))
    for u, L in sn['lz'].items():
        x, y = proj(L[0], L[1])
        if L[2] > 1: ax.text(x, -y, U[int(u)]['n'], ha='center', va='center', fontsize=7)
    W, E, S, N = G['ext'][0], G['ext'][1], G['ext'][2], G['ext'][3]
    xs, ys = proj([W, E, W, E, (W + E) / 2, (W + E) / 2], [S, S, N, N, N, S])
    ax.set_xlim(min(xs), max(xs)); ax.set_ylim(-max(ys), -min(ys)); ax.set_aspect(1); ax.axis('off')
    ax.set_title(f"{sn['y']} · {sn['t']}")
    out = ROOT / 'build' / f'preview-{year}.png'
    fig.savefig(out, bbox_inches='tight'); print('  [草图]', out.relative_to(ROOT))


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 669)
