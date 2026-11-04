# 检查 geodata/ 底图；缺失的从 GitHub 下载固定版本并校验 sha256
# 仓库已附带全部底图，离线即可构建；此脚本只在文件被删或损坏时用到。
import hashlib, sys, urllib.request
import config as C

NE = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/v5.1.2/geojson/'
BM = 'https://raw.githubusercontent.com/matplotlib/basemap/v1.4.1/examples/'
FILES = {
    'ne_50m_land.geojson': (NE, 'e874b27a51d146452be360cafb3cc50c86001074a67d534113e6534682f9826b'),
    'ne_10m_lakes.geojson': (NE, '2d036f53dedec578001c5c30c2959ee7d4eebc1306900fa4367c49929ec8f2d9'),
    'ne_10m_lakes_historic.geojson': (NE, '43913ce0f5c18fe4d551d628b836af0da59ba193631767b5012a7f97b6a5b615'),
    'ne_10m_rivers_lake_centerlines.geojson': (NE, 'bb854a900ecbd3b408df46d5e16e3e0f974ba55993f9d8b5c26e855273c0905a'),
    'ne_10m_geography_regions_polys.geojson': (NE, 'b7b26e50ea917d3696aec87f932def2bf5f890f5770e441d59c162c6f4c92a77'),
    'ne_50m_admin_0_boundary_lines_land.geojson': (NE, '2faac4f6b34386f3d21b6e018cf151f241f00e5c936d44dd17d7d9bfb147fa48'),
    'etopo20data.gz': (BM, 'bd6549bb0a675d2978d1dee1609fc4cec7e4d74b98d4fe49c0e8a2e8c8f3b8ce'),
    'etopo20lats.gz': (BM, '3201109f72a8371d1fee6396292618c9b05cae0a55abf8b2117bb2ef1f7e97ce'),
    'etopo20lons.gz': (BM, '95109988351bed186a886c6dd2a607455939013dfc49f7b7c61997d3389802b7'),
    # 以下两件取自《唐宋之际形势图》（河湖、运河、荒漠、今省界与山川关隘条目），随仓库附带，无处下载
    'tangsong_geo.json': (None, '52e4159b932279e4719c0c1c64263e5457736ffcb386c4e7e490163c2ba1a6f0'),
    'tangsong_data.json': (None, '9b20ad5195125adf9fd6220481e1432a5c872470daa3ea957cc2a0c243c4194f'),
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    C.GEODATA.mkdir(exist_ok=True)
    bad = []
    for name, (base, digest) in FILES.items():
        p = C.GEODATA / name
        if p.exists() and sha(p) == digest: continue
        if base is None:
            bad.append(name); continue
        print(f'  [底图] 下载 {name}')
        with urllib.request.urlopen(base + name, timeout=120) as r: p.write_bytes(r.read())
        if sha(p) != digest: bad.append(name)
    if bad:
        sys.exit('geodata 缺失或校验不符：' + '、'.join(bad))


if __name__ == '__main__':
    main()
