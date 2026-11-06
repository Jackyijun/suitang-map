# 隋及唐初形势图

581—669 年，从隋文帝代周到唐高宗总章二年唐疆域极盛，26 个时间节点，按月细分隋末群雄与唐初统一；含秦王李世民征战路线、古今地名对照、年表与对照表。单文件网页，无外部依赖。

## 直接看

用浏览器打开 `docs/index.html` 即可，离线可用。

## 线上地址

https://jackyijun.github.io/suitang-map/

## 本地构建

需要 Python 3.10 以上。

```bash
python -m venv .venv && source .venv/bin/activate      # Windows：.venv\Scripts\activate
pip install -r requirements.txt
python run.py                 # 全部重建，约 1 分钟，输出 docs/index.html
python run.py --html          # 只改了 content/ 的归属或文字：沿用已算好的疆域，几秒钟
python run.py --open          # 构建后在浏览器打开
python run.py --preview 669   # 另出该年疆域草图 build/preview-669.png
```

同一份输入重建，`docs/index.html` 逐字节相同（随机种子固定）。

构建完成后，把 `docs/index.html` 一起提交并推送到 `main`，线上网页会自动更新。

## 目录结构

```
suitang-map/
├── run.py              一键构建
├── requirements.txt    numpy、scipy、shapely、scikit-image、matplotlib
├── docs/
│   ├── index.html      成品，单文件
│   └── .nojekyll
├── content/            史料（手写）
│   ├── seeds.py        465 个归属点：州郡城邑（显示）与仅参与分区的辅助点，含今地与名称沿革
│   ├── units.py        政权、都护府、羁縻府州、部族：名称、颜色、按语
│   ├── snaps.py        26 个时间节点：标题、概述、各单位所领州郡、治所、别名
│   ├── items.py        都城、战役、关隘、事件、山川按语、诸族、秦王征战路线
│   └── frontier.py     全图外缘（北疆按主流唐极盛图手绘）
├── src/
│   ├── config.py       全部路径与可调参数
│   ├── fetch_data.py   校验 geodata/，缺失时从 GitHub 下载固定版本
│   ├── build.py        算疆域，输出 build/*.json
│   ├── basemap.py      底图：陆地、湖泊、河流、运河、荒漠、今国界、今省界
│   ├── territory.py    疆域算法（见下）
│   ├── compile_data.py 各节点归属 → 疆域多边形 → GEO / DATA
│   ├── proj.py         Albers 等积圆锥投影（与页面一致）
│   ├── assemble.py     注入模板，输出 docs/index.html
│   └── template.html   前端
├── geodata/            底图，随仓库附带，离线可构建
├── tools/
│   ├── preview.py      matplotlib 疆域草图
│   └── shot.js         可选：无头浏览器截图（需 Node 与 playwright）
└── build/              中间产物
```

## 工作原理

**疆域算法**（`src/territory.py`，参数在 `src/config.py`）：

1. **栅格**：东经 46°—148°、北纬 3°—60°，每格约 6.4 km（0.057°）。海与面积 0.15 平方度以上的湖不可通行。
2. **代价**：平地 1，加 ETOPO20 坡度与高原海拔；山脉脊线烧出高斯形高代价带（主干峰值 +8，次要 +3.5），手绘脊线先加一点横向摆动；江、河、淮、汉与乌浒水、药杀水另加代价；最后乘 ±38% 的多尺度平滑噪声。
3. **分区**：以全部 465 个归属点为源跑一次 16 邻接（含马步）多源 Dijkstra，每格归代价距离最近的点，得到各点的「势力格」。界线因此顺山脊、大河走。
4. **外缘**：全图外缘取 `content/frontier.py` 的手绘线（北起咸海北岸，循哈萨克丘陵北缘、额尔齐斯河、阿尔泰山、叶尼塞河中游，绕贝加尔湖北端，经石勒喀河、黑龙江至入海口）。海面、大湖与近岸小岛就近延伸，页面再按陆地裁剪；台湾、济州、对马等离岸较远又无归属点的岛屿留空。
5. **描界**：每类的指示栅格作高斯平滑（σ 1.2 格），界线描在相邻两类平滑值相等处，沿格边线性插值，三类以上交汇处取交点均值。整张图的界线网络只描一次、两侧共用，再做三轮拉普拉斯平滑，抹掉格点插值留下的小折角。
6. **成面**：界线网络成面，按格心归类，零星碎块并入相邻一方；再加一层平滑位移场（约 1—2 格，两种尺度），让平原上的界线带上河曲一样的小弯；最后用 GEOS `coverage_simplify` 整体简化。相邻势力格共用同一条边，无缝无叠。
7. **按节点合并**：`compile_data.py` 按各节点的归属把势力格并成单位（政权、都护府）与政权的疆域，注记取最大陆块的不可达极点；相邻节点没变的几何只存一份（`GEO.pool`）。

**页面**：`template.html` 是唐宋之际形势图的前端，按《历史形势图统一规范》改写；`assemble.py` 把 `__GEO__`、`__DATA__`、`__UCSS_LIGHT__`、`__UCSS_DARK__` 四个占位符换成数据，输出单文件。

## 常见修改

- **改某个节点的归属**：编辑 `content/snaps.py` 里该节点的 `own`（单位 → 州郡列表，`#HB` 之类是地区简写），然后 `python run.py --html`。
- **加一个州郡或辅助点**：在 `content/seeds.py` 加一行（`名|今地|经度|纬度|类型|地区|名称沿革`，类型 z 州府、c 城邑、r 仅参与分区），再在 `snaps.py` 里分配归属，然后 `python run.py`（势力格要重算）。
- **改按语、战役、事件**：编辑 `content/items.py` 或 `units.py`，`python run.py --html`。
- **改北疆外缘**：编辑 `content/frontier.py` 的 `NORTH` 折线（经纬度），`python run.py`。
- **改样式或交互**：编辑 `src/template.html`，`python run.py --html`。

## 调参

都在 `src/config.py`：

| 参数 | 作用 |
| --- | --- |
| `PX` | 格边长；越小界线越细，构建越慢 |
| `RIDGE_MAJOR` / `RIDGE_MINOR` / `RIDGE_W` | 山脊带的高度与宽度；越高界线越贴山脊 |
| `BORDER_RIVERS` | 界河及其加价 |
| `NOISE_AMP` / `NOISE_SCALES` | 代价噪声；越大界线越曲折 |
| `WARP` | 位移场的尺度与幅度（格） |
| `SMOOTH_SIGMA` / `LAPLACE` | 描界前的高斯平滑与描界后的网络平滑 |
| `SIMPLIFY` | 覆盖简化容差；越大文件越小，界线越折 |
| `SEED` | 随机种子 |

## 资料与可靠程度

疆域据《隋书》、两《唐书》、《资治通鉴》及谭其骧《中国历史地图集》第五册大意推定，以州郡为单位、沿山川划界，仅为示意。羁縻都护、都督府多为名义统属，草原诸部并无确切界线；北疆外缘按主流唐极盛图的通行画法手绘。今地取遗址或所在城市。

底图：Natural Earth 5.1.2（陆地、湖泊、河流、今国界）、ETOPO20 地形（matplotlib/basemap 1.4.1 附带），河湖运河、今省界与部分山川关隘条目沿用《唐宋之际形势图》。
