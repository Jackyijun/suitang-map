# Sui and Early Tang, 581–669

[![中文](https://img.shields.io/badge/lang-%E4%B8%AD%E6%96%87-red.svg)](README.md) [![English](https://img.shields.io/badge/lang-English-blue.svg)](README.en.md)

581–669, from Emperor Wen of Sui taking the throne from Northern Zhou to the height of Tang territory in Zongzhang 2 under Emperor Gaozong: 26 time points, with the late-Sui rebels and the Tang reunification broken down month by month. It includes the campaign route of Li Shimin, Prince of Qin, historical and modern place names side by side, a timeline and a gazetteer. Bilingual (Chinese and English), a single web page with no external dependencies.

## 1. Just look

Open `docs/index.html` in a browser. It works offline.

- Language: switch with "中 | EN" at the top right of the map (in the Timeline and Gazetteer views, at the top right of the content area). The choice is remembered in the browser; add `#en` to the end of the address to open the English version directly. In English, map labels are English only; tooltips, the index, the timeline and the gazetteer give the original Chinese characters after the English name. Search accepts Chinese or English, and English does not need diacritics.

## 2. Online

https://jackyijun.github.io/suitang-map/

## 3. Build locally

Requires Python 3.10 or later.

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py                 # full rebuild, about 1 minute, writes docs/index.html
python run.py --html          # only allegiances or text in content/ changed: reuse the computed territories, a few seconds
python run.py --draft         # build the page even if English is missing or stale (Chinese shown where missing); the default is strict and stops
python run.py --open          # open in a browser after building
python run.py --preview 669   # also write a territory sketch for that year, build/preview-669.png
```

Rebuilding from the same input gives a byte-identical `docs/index.html` (the random seed is fixed).

After building, commit `docs/index.html` along with your changes and push to `main`; the online page updates automatically.

## 4. Layout

```
suitang-map/
├── run.py              one-step build
├── requirements.txt    numpy, scipy, shapely, scikit-image, matplotlib
├── README.md           readme (Chinese, shown by default on GitHub)
├── README.en.md        readme (English)
├── docs/
│   ├── index.html      the finished page, a single file
│   └── .nojekyll
├── content/            historical content (hand-written)
│   ├── seeds.py        465 allegiance points: prefectures, commanderies and towns (shown) and helper points used only for partitioning, with modern locations and name changes
│   ├── units.py        states, protectorates, loose-rein prefectures, peoples: names, colors, notes
│   ├── snaps.py        26 time points: titles, summaries, the prefectures each unit holds, seats, alternative names
│   ├── items.py        capitals, battles, passes, events, notes on mountains and rivers, peoples, the Prince of Qin's campaign route
│   ├── frontier.py     the outer edge of the map (the northern frontier hand-drawn after the usual maps of Tang at its height)
│   └── en/             English version: translations matching the files above (JSON), zh.lock.json Chinese fingerprints, GLOSSARY.md naming conventions
├── src/
│   ├── config.py       all paths and tunable parameters
│   ├── fetch_data.py   checks geodata/, downloads pinned versions from GitHub if missing
│   ├── build.py        computes territories, writes build/*.json
│   ├── basemap.py      base map: land, lakes, rivers, canals, deserts, modern national and provincial borders
│   ├── territory.py    territory algorithm (below)
│   ├── compile_data.py allegiances per time point → territory polygons → GEO / DATA
│   ├── proj.py         Albers equal-area conic projection (same as the page)
│   ├── i18n.py         English version: lists entries needing translation, checks missing and stale English, merges translations into the data
│   ├── assemble.py     merges English and checks it, fills the template, writes docs/index.html
│   └── template.html   front end
├── geodata/            base map data, shipped with the repository so it builds offline
├── tools/
│   ├── i18n.py         English maintenance: status / todo / lock / table
│   ├── preview.py      matplotlib territory sketch
│   └── shot.js         optional: headless browser screenshots (needs Node and playwright)
└── build/              intermediate files
```

## 5. How it works

**Territory algorithm** (`src/territory.py`, parameters in `src/config.py`):

1. **Grid**: 46°–148° E, 3°–60° N, cells about 6.4 km (0.057°). Sea and lakes of 0.15 square degrees or more are impassable.
2. **Cost**: 1 on flat ground, plus ETOPO20 slope and plateau elevation; mountain ridgelines are burned in as Gaussian high-cost bands (peak +8 for main ranges, +3.5 for minor ones), with a little sideways wobble added to the hand-drawn ridgelines first; the Yangtze, Yellow River, Huai, Han, Oxus and Jaxartes add extra cost; finally everything is multiplied by ±38% multi-scale smooth noise.
3. **Partition**: one multi-source Dijkstra from all 465 allegiance points over 16 neighbors (including knight's moves); each cell goes to the point nearest in cost distance, giving each point its "cell of influence". Borders therefore follow ridges and large rivers.
4. **Outer edge**: the outer edge of the map follows the hand-drawn line in `content/frontier.py` (from the north shore of the Aral Sea, along the northern edge of the Kazakh Uplands, the Irtysh, the Altai, the middle Yenisei, round the north end of Lake Baikal, then the Shilka and the Amur to its mouth). Sea, large lakes and near-shore islets go to the nearest point and the page clips to land; islands farther offshore with no allegiance point (Taiwan, Jeju, Tsushima) are left blank.
5. **Tracing**: each class's indicator grid is Gaussian-smoothed (σ 1.2 cells) and borders are traced where two neighboring classes' smoothed values are equal, linearly interpolated along cell edges, with junctions of three or more classes placed at the mean of their crossings. The border network for the whole map is traced once and shared by both sides, then given three rounds of Laplacian smoothing to remove small kinks left by the grid interpolation.
6. **Polygons**: the border network is polygonized, faces are assigned by cell center, and stray fragments merge into a neighbor; a smooth displacement field (about 1–2 cells, at two scales) then gives borders on the plains small river-like bends; finally GEOS `coverage_simplify` simplifies the whole coverage. Neighbouring cells share the same edge, with no gaps or overlaps.
7. **Merging per time point**: `compile_data.py` merges cells into units (states, protectorates) and into states according to each time point's allegiances; labels go at the pole of inaccessibility of the largest piece; geometry unchanged between time points is stored once (`GEO.pool`).

**Page**: `template.html` is the front end of the *Tang–Song transition* map, reworked to the shared conventions for these historical maps (历史形势图统一规范), with the language switch done as in the *Song, Liao, Xia, Jin and Yuan* map; `assemble.py` first merges and checks the English with `src/i18n.py`, then replaces the four placeholders `__GEO__`, `__DATA__`, `__UCSS_LIGHT__`, `__UCSS_DARK__` with data and writes a single file.

## 6. Common changes

- **Change allegiances at a time point**: edit that time point's `own` in `content/snaps.py` (unit → list of prefectures; things like `#HB` are region shorthands), then `python run.py --html`.
- **Add a prefecture or helper point**: add a line to `content/seeds.py` (`name|modern place|longitude|latitude|type|region|name history`; type z prefecture, c town, r partitioning only), assign it in `snaps.py`, then `python run.py` (the cells must be recomputed). Add the English for a new prefecture name and modern place to `content/en/seeds.json`.
- **Change notes, battles, events**: edit `content/items.py` or `units.py`, make the same change to the English in the matching JSON in `content/en/`, run `python tools/i18n.py lock`, then `python run.py --html`.
- **Change the northern frontier**: edit the `NORTH` polyline (longitude, latitude) in `content/frontier.py`, then `python run.py`.
- **Change style or interaction**: edit `src/template.html`, then `python run.py --html`. Interface text has its English in the template (`LZ(Chinese, English)`).

## 7. The English version

Chinese is the source text. The English is written in `content/en/` under the same keys:

| File | Content | Key |
|---|---|---|
| `units.json` | states, protectorates, peoples: full name `n`, short map name `s`, note `note` | unit key (e.g. `唐`) |
| `labels.json` | names a unit went by at a given time point (`lab` in `snaps.py`) | the Chinese name |
| `seeds.json` | prefectures and towns: modern place `mod`, names in each period `n` | point ID |
| `items.json` | entries: `old` `mod` `note` `yt` `sides` `cmd`, route places `p` | `category:historical name` (e.g. `battle:虎牢之战`); entries sharing a name add `@state` or `@modern place` |
| `snaps.json` | time points: era name `era`, title `t`, summary `d` | `year-month` (e.g. `618-05`) |
| `misc.json` | modern province names `prov` | the Chinese name |

`zh.lock.json` records a fingerprint (first 10 characters of sha1) of the Chinese each English entry was written from. If the Chinese changes and the English does not, the build reports it as stale. Naming rules are in `content/en/GLOSSARY.md` (pinyin, how commanderies, counties, garrisons and protectorates are translated, foreign place names, lunar months, how battle results are written, and so on).

**After changing the Chinese**:

1. `python tools/i18n.py status` shows how many entries are missing or stale;
2. `python tools/i18n.py todo` lists the Chinese for those entries; add or revise the English in the matching JSON;
3. `python tools/i18n.py lock` records the new Chinese fingerprints;
4. `python run.py --html` reassembles (strict: missing English is an error).

`python tools/i18n.py table` exports every Chinese–English pair to `build/i18n-review.tsv` for review.

## 8. Tuning

All in `src/config.py`:

| Parameter | Effect |
| --- | --- |
| `PX` | cell size; smaller gives finer borders and slower builds |
| `RIDGE_MAJOR` / `RIDGE_MINOR` / `RIDGE_W` | height and width of the ridge bands; higher keeps borders closer to ridges |
| `BORDER_RIVERS` | border rivers and their extra cost |
| `NOISE_AMP` / `NOISE_SCALES` | cost noise; larger gives more winding borders |
| `WARP` | scale and amplitude (cells) of the displacement field |
| `SMOOTH_SIGMA` / `LAPLACE` | Gaussian smoothing before tracing and network smoothing after |
| `SIMPLIFY` | coverage simplification tolerance; larger gives smaller files and more angular borders |
| `SEED` | random seed |

## 9. Sources and reliability

Territories are inferred in outline from the *Book of Sui*, the two *Books of Tang*, the *Zizhi Tongjian* and volume 5 of Tan Qixiang's *Historical Atlas of China*, by prefecture and along mountains and rivers; they are only indicative. Loose-rein protectorates and area commands were mostly nominal, and the steppe peoples had no precise borders; the northern frontier is hand-drawn after the usual maps of Tang at its height. Modern locations are the site or the city it lies in.

English names follow `content/en/GLOSSARY.md`: places in the Chinese-character world in pinyin, places beyond it under the usual English form of their local name at the time; dates keep the lunar month and are not converted to the Western calendar.

Base map: Natural Earth 5.1.2 (land, lakes, rivers, modern national borders), ETOPO20 terrain (bundled with matplotlib/basemap 1.4.1); rivers, lakes, canals, modern provincial borders and some mountain and pass entries are carried over from the *Tang–Song transition* map.
