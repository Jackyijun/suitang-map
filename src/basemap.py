# 底图：陆地、湖泊、河流、运河、荒漠、今国界、今省界（经纬度，未编码）
# 输入 geodata/（Natural Earth 与唐宋之际形势图的底图），输出 build/geo_base.json
import json, math
from shapely.geometry import shape, box, Polygon, MultiPolygon, LineString, MultiLineString, Point, mapping
from shapely.ops import unary_union, linemerge
import config as C

OUT = C.BUILD / 'geo_base.json'
EXT = box(*C.EXT)                  # 河湖国界数据范围
LEXT = box(*C.LEXT)                # 陆地范围（大于任何视野，免出现假海岸）
G = C.GEODATA

def dec(flat):
    x = y = 0; out = []
    for i in range(0, len(flat), 2):
        x += flat[i]; y += flat[i + 1]; out.append((x / 100, y / 100))
    return out

ts = json.load(open(G / 'tangsong_geo.json', encoding='utf-8'))

# ---------- 陆地 ----------
land = unary_union([shape(f['geometry']) for f in json.load(open(G / 'ne_50m_land.geojson', encoding='utf-8'))['features']]).intersection(LEXT)
polys = []
for p in (land.geoms if hasattr(land, 'geoms') else [land]):
    if p.area < 0.02:   # 小岛舍去（济州岛约0.18，保留）
        continue
    q = p.simplify(0.018, preserve_topology=True)
    if q.is_empty: continue
    polys.append(q)
land = MultiPolygon(polys)

def rings_of(poly):
    return [list(poly.exterior.coords)] + [list(r.coords) for r in poly.interiors if Polygon(r).area > 0.02]

land_out = [[[(round(x, 2), round(y, 2)) for x, y in r] for r in rings_of(p)] for p in polys]

# ---------- 湖泊 ----------
# 沿用唐宋图湖泊，去掉现代水库与晚出湖泊
RESERVOIR = [(118.96, 29.58), (111.41, 32.71), (114.54, 23.85), (101.93, 55.68), (103.26, 54.34), (127.94, 54.42),
             (91.58, 54.69), (82.37, 54.51), (77.61, 43.84), (72.88, 41.81), (72.86, 34.19), (102.64, 18.59), (99.06, 14.7),
             (76.13, 15.2), (79.2, 16.5), (83.76, 21.65), (92.22, 22.74), (75.5, 24.44), (76.05, 32.01), (117.22, 34.61), (116.19, 35.98)]
lakes = []
ts_lake_items = {}
for lk in ts['lakes']:
    pts = dec(lk['r']); c = Polygon(pts).centroid
    if any(abs(c.x - a) < .08 and abs(c.y - b) < .08 for a, b in RESERVOIR):
        continue
    lakes.append({'r': [(round(x, 2), round(y, 2)) for x, y in pts], 'ts_it': lk.get('it')})
# 唐宋图范围外补 NE 湖泊（中亚、西伯利亚）
nel = json.load(open(G / 'ne_10m_lakes.geojson', encoding='utf-8'))['features']
for f in nel:
    pr = f['properties']
    if 'Reservoir' in (pr.get('featurecla') or ''): continue
    g = shape(f['geometry'])
    if not g.intersects(EXT): continue
    c = g.centroid
    if 71.5 <= c.x <= 136.5 and 15 <= c.y <= 55.5: continue
    for p in (g.geoms if hasattr(g, 'geoms') else [g]):
        if p.area < 0.05: continue
        if (pr.get('name') or '').startswith('Aral'): continue  # 咸海用历史湖面
        q = p.simplify(0.03)
        lakes.append({'r': [(round(x, 2), round(y, 2)) for x, y in q.exterior.coords], 'ne': pr.get('name')})
for f in json.load(open(G / 'ne_10m_lakes_historic.geojson', encoding='utf-8'))['features']:
    nm = f['properties'].get('name') or ''
    if 'Aral' in nm:
        g = shape(f['geometry'])
        for p in (g.geoms if hasattr(g, 'geoms') else [g]):
            if p.area < 0.05: continue
            q = p.simplify(0.03)
            lakes.append({'r': [(round(x, 2), round(y, 2)) for x, y in q.exterior.coords], 'ne': 'Aral historic'})

# ---------- 河流 ----------
rivers = []
for r in ts['rivers']:
    rivers.append({'p': [(round(x, 2), round(y, 2)) for x, y in dec(r['p'])], 'k': r['k'], 'ts_it': r.get('it')})
NEW_RIV = {  # NE 名称 → (等级, 键)
    'Amu  Darya': ('major', 'amu'), 'Panj': ('minor', 'amu'), 'Syr  Darya': ('major', 'syr'), 'Naryn': ('minor', 'syr'),
    'Zarafshon': ('minor', 'zer'), 'Harirud': ('faint', 'hari'), 'Helmand': ('minor', 'helm'), 'Indus': ('minor', 'indus'),
    'Sutlej': ('faint', None), 'Chenab': ('faint', None), 'Jhelum': ('faint', None), 'Ganges': ('minor', 'ganges'),
    'Yamuna': ('faint', None), 'Ghäghara': ('faint', None), 'Gandak': ('faint', None),
}
ner = json.load(open(G / 'ne_10m_rivers_lake_centerlines.geojson', encoding='utf-8'))['features']
covered = unary_union([LineString(r['p']) for r in rivers if len(r['p']) > 1]).buffer(0.15)
for f in ner:
    nm = f['properties'].get('name')
    if nm not in NEW_RIV: continue
    g = shape(f['geometry']).intersection(EXT)
    if g.is_empty: continue
    g = g.difference(covered)
    k, key = NEW_RIV[nm]
    for ln in (g.geoms if hasattr(g, 'geoms') else [g]):
        if ln.geom_type != 'LineString' or ln.length < 0.4: continue
        q = ln.simplify(0.03)
        rivers.append({'p': [(round(x, 2), round(y, 2)) for x, y in q.coords], 'k': k, 'key': key})
# 手绘：NE 缺少的几条（碎叶水、怛逻斯水、萨水、浿水、白江）
HAND = {
    'chu': ('minor', [(76.2, 42.45), (75.7, 42.75), (75.3, 42.85), (74.6, 42.95), (73.6, 43.3), (72.6, 43.9), (71.5, 44.4), (70.4, 44.8), (69.5, 45.1), (68.6, 45.3)]),
    'talas': ('minor', [(73.3, 42.3), (72.6, 42.45), (72.0, 42.6), (71.37, 42.9), (71.0, 43.3), (70.5, 43.8), (70.0, 44.3)]),
    'sa': ('minor', [(126.75, 40.25), (126.3, 40.15), (126.0, 39.85), (125.85, 39.65), (125.6, 39.62), (125.45, 39.6)]),
    'pae': ('minor', [(126.85, 39.95), (126.45, 39.75), (126.1, 39.5), (125.9, 39.3), (125.78, 39.05), (125.6, 38.85), (125.4, 38.73), (125.2, 38.7)]),
    'baek': ('minor', [(127.48, 35.75), (127.55, 36.1), (127.45, 36.4), (127.25, 36.48), (127.12, 36.46), (126.95, 36.32), (126.88, 36.2), (126.8, 36.05), (126.62, 35.99)]),
}
for key, (k, pts) in HAND.items():
    rivers.append({'p': pts, 'k': k, 'key': key})

# ---------- 运河、荒漠 ----------
canals = [{'p': [(round(x, 2), round(y, 2)) for x, y in dec(c['p'])], 'ts_it': c['it']} for c in ts['canals']]
deserts = [{'r': [(round(x, 2), round(y, 2)) for x, y in dec(d['r'])], 'ts_it': d['it']} for d in ts['deserts']]
reg = json.load(open(G / 'ne_10m_geography_regions_polys.geojson', encoding='utf-8'))['features']
for f in reg:
    nm = (f['properties'].get('NAME') or '').upper()
    if nm in ('GARAGUM DESERT', 'QIZILQUM DESERT'):
        g = shape(f['geometry']).intersection(EXT)
        for p in (g.geoms if hasattr(g, 'geoms') else [g]):
            if p.area < 1: continue
            q = p.simplify(0.15)
            deserts.append({'r': [(round(x, 2), round(y, 2)) for x, y in q.exterior.coords], 'ne': nm})

# ---------- 今国界（NE 50m 陆上国界） ----------
bl = json.load(open(G / 'ne_50m_admin_0_boundary_lines_land.geojson', encoding='utf-8'))['features']
border = []
for f in bl:
    g = shape(f['geometry']).intersection(EXT)
    for ln in (g.geoms if hasattr(g, 'geoms') else [g]):
        if ln.geom_type != 'LineString' or ln.length < 0.05: continue
        q = ln.simplify(0.03)
        border.append([(round(x, 2), round(y, 2)) for x, y in q.coords])

# ---------- 今省界（沿用） ----------
prov = [{'n': p['n'], 'c': p['c'], 'r': [[(round(x, 2), round(y, 2)) for x, y in dec(r)] for r in p['r']]} for p in ts['prov']]

def main():
    C.BUILD.mkdir(exist_ok=True)
    json.dump({'land': land_out, 'lakes': lakes, 'rivers': rivers, 'canals': canals, 'deserts': deserts, 'border': border, 'prov': prov},
              open(OUT, 'w', encoding='utf-8'), ensure_ascii=False)
    print('  [底图] land polys', len(land_out), 'pts', sum(len(r) for p in land_out for r in p))
    print('  [底图] lakes', len(lakes), 'rivers', len(rivers), 'canals', len(canals), 'deserts', [d.get('ne') for d in deserts], 'border', len(border))
    print('  [底图] new rivers', [r.get('key') for r in rivers if r.get('key')])
