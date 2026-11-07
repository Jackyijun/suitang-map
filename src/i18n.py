# 英文版：把 content/en/ 下的译文并入构建结果，并检查缺译与过期（做法同《宋辽夏金元形势图》）。
#
# 中文是源文本。每一条要显示的中文都有一个“键/字段”，英文按同样的键写在 content/en/*.json 里：
#
#   units.json    政权、都护府、部族       {"唐": {"n": 全称, "s": 地图短名（可省）, "note": 说明}}
#   labels.json   节点里的当年别名         {"唐公李渊": "Li Yuan, Duke of Tang"}
#   seeds.json    州郡城邑                 {"雍州": {"mod": 今地, "n": {"雍州": …, "京兆郡": …}}}
#   items.json    条目（键为 类别:古名，同名者加 @政权 或 @今地）  {"battle:浅水原之战": {"old", "mod", "note", "yt", "sides", "cmd", "p": {路线地名: …}}}
#   snaps.json    时间节点（键为 年-月）    {"618-05": {"era": 年号, "t": 标题, "d": 说明}}
#   misc.json     今省名                   {"prov": {"河南": "Henan"}}
#
# zh.lock.json 记着每条英文写成时对应中文的指纹（sha1 前 10 位）。中文改了而英文没改，就是“过期”。
# 改完英文后运行 python tools/i18n.py lock 更新指纹。
import hashlib, json
import config as C

EN = C.CONTENT / 'en'
FILES = ['units', 'labels', 'seeds', 'items', 'snaps', 'misc']
LOCK = EN / 'zh.lock.json'
ITEM_FIELDS = ('old', 'mod', 'note', 'yt', 'sides', 'cmd')


def fp(zh):
    return hashlib.sha1(zh.encode('utf8')).hexdigest()[:10]


def load_en():
    out = {}
    for f in FILES:
        p = EN / f'{f}.json'
        out[f] = json.load(open(p, encoding='utf8')) if p.exists() else {}
    return out


def load_lock():
    return json.load(open(LOCK, encoding='utf8')) if LOCK.exists() else {}


def item_key(it):
    return f"{it['c']}:{it['old']}"


def item_keys(data):
    """每个条目的键：类别:古名；同名条目（如两朝都江陵、两处柏海）再加 @所属政权 或 @今地 区分。"""
    from collections import Counter
    base = [item_key(it) for it in data['items']]
    dup = {k for k, n in Counter(base).items() if n > 1}
    keys = []
    for it, k in zip(data['items'], base):
        if k in dup:
            k += '@' + (data['units'][it['st']]['k'] if it.get('st') is not None else it.get('mod', ''))
        keys.append(k)
    seen = Counter()
    out = []
    for k in keys:
        seen[k] += 1
        out.append(k if seen[k] == 1 else f'{k}#{seen[k]}')
    return out


def snap_key(s):
    return f"{s['y']}-{s['m']:02d}" if s.get('m') else str(s['y'])


def required(geo, data):
    """列出全部需要英文的 (文件, 路径, 中文)。路径是键名组成的元组。"""
    req = []
    for u in data['units']:
        req.append(('units', (u['k'], 'n'), u['n']))
        if u.get('note'): req.append(('units', (u['k'], 'note'), u['note']))
    labs = sorted({v for s in geo['snaps'] for v in s['lab'].values()})
    for v in labs: req.append(('labels', (v,), v))
    for s in data['seeds']:
        if s['t'] == 'r': continue
        if s.get('mod'): req.append(('seeds', (s['id'], 'mod'), s['mod']))
        names = [s['n']] + [n for _, n in (s.get('nm') or [])]
        for n in dict.fromkeys(names): req.append(('seeds', (s['id'], 'n', n), n))
    IK = item_keys(data)
    for it, k in zip(data['items'], IK):
        for f in ITEM_FIELDS:
            if it.get(f): req.append(('items', (k, f), it[f]))
    R = geo.get('route')
    if R:
        k = IK[R['it']]
        for p in dict.fromkeys(p[3] for p in R['pts']): req.append(('items', (k, 'p', p), p))
    for s in geo['snaps']:
        y = snap_key(s)
        for f in ('era', 't', 'd'):
            if s.get(f): req.append(('snaps', (y, f), s[f]))
    for p in geo.get('prov', []): req.append(('misc', ('prov', p['n']), p['n']))
    return req


def get(en, f, path):
    v = en.get(f, {})
    for k in path:
        if not isinstance(v, dict) or k not in v: return None
        v = v[k]
    return v if isinstance(v, str) and v.strip() else None


def lock_key(f, path):
    return f + '/' + '/'.join(path)


def check(geo, data, en=None, lock=None):
    en = en if en is not None else load_en()
    lock = lock if lock is not None else load_lock()
    missing, stale, unlocked = [], [], []
    for f, path, zh in required(geo, data):
        if get(en, f, path) is None: missing.append((f, path, zh)); continue
        lk = lock.get(lock_key(f, path))
        if lk is None: unlocked.append((f, path, zh))
        elif lk != fp(zh): stale.append((f, path, zh))
    return missing, stale, unlocked


def attach(geo, data, en=None):
    """把英文写进 geo/data（缺译时退回中文），返回 (geo, data)。"""
    en = en if en is not None else load_en()
    g = lambda f, *path: get(en, f, path)
    for u in data['units']:
        u['ne'] = g('units', u['k'], 'n') or u['n']
        s = g('units', u['k'], 's')
        if s: u['se'] = s
        u['notee'] = g('units', u['k'], 'note') or u.get('note', '')
    for s in data['seeds']:
        if s['t'] == 'r': continue
        s['ne'] = g('seeds', s['id'], 'n', s['n']) or s['n']
        if s.get('nm'): s['nme'] = [g('seeds', s['id'], 'n', n) or n for _, n in s['nm']]
        s['mode'] = g('seeds', s['id'], 'mod') or s.get('mod', '')
    IK = item_keys(data)
    for it, k in zip(data['items'], IK):
        it['e'] = {f: (g('items', k, f) or it[f]) for f in ITEM_FIELDS if it.get(f)}
    R = geo.get('route')
    if R:
        k = IK[R['it']]
        R['pe'] = [g('items', k, 'p', p[3]) or p[3] for p in R['pts']]
    for s in geo['snaps']:
        y = snap_key(s)
        s['erae'] = g('snaps', y, 'era') or s.get('era', '')
        s['te'] = g('snaps', y, 't') or s['t']
        s['de'] = g('snaps', y, 'd') or s.get('d', '')
        s['labe'] = {u: (g('labels', v) or v) for u, v in s['lab'].items()}
    for p in geo.get('prov', []): p['ne'] = g('misc', 'prov', p['n']) or p['n']
    return geo, data
