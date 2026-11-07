"""英文版维护工具（读 build/out_data.json，需先构建过一次）

  python tools/i18n.py status          列出缺译、过期（中文改过）和未登记指纹的条目数
  python tools/i18n.py todo [文件]      逐条列出缺译与过期的中文，便于补译
  python tools/i18n.py lock            英文改好后运行：把当前中文的指纹记入 content/en/zh.lock.json
  python tools/i18n.py table           导出中英对照表 build/i18n-review.tsv（审校用）
"""
import json, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / 'src')]
import i18n as I   # noqa: E402


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    D = json.load(open(ROOT / 'build' / 'out_data.json', encoding='utf8'))
    geo, data = D['GEO'], D['DATA']
    en, lock = I.load_en(), I.load_lock()
    missing, stale, unlocked = I.check(geo, data, en, lock)
    if cmd == 'status':
        req = I.required(geo, data)
        print(f'需要英文 {len(req)} 条：缺译 {len(missing)}，过期 {len(stale)}，未登记指纹 {len(unlocked)}')
        c = Counter(f for f, _, _ in missing)
        if c: print('缺译分布：', dict(c))
    elif cmd == 'todo':
        only = sys.argv[2] if len(sys.argv) > 2 else None
        for tag, lst in (('缺译', missing), ('过期', stale)):
            for f, path, zh in lst:
                if only and f != only: continue
                print(f"{tag}\t{f}\t{'/'.join(path)}\t{zh}")
    elif cmd == 'lock':
        new = {I.lock_key(f, path): I.fp(zh) for f, path, zh in I.required(geo, data) if I.get(en, f, path) is not None}
        I.LOCK.parent.mkdir(exist_ok=True)
        json.dump(dict(sorted(new.items())), open(I.LOCK, 'w', encoding='utf8'), ensure_ascii=False, indent=0)
        print(f'已登记 {len(new)} 条指纹')
    elif cmd == 'table':
        out = ROOT / 'build' / 'i18n-review.tsv'
        bad = {(f, p) for f, p, _ in missing} | {(f, p) for f, p, _ in stale}
        with open(out, 'w', encoding='utf8') as fh:
            fh.write('文件\t键\t中文\t英文\t状态\n')
            for f, path, zh in I.required(geo, data):
                e = I.get(en, f, path) or ''
                st = '缺译' if not e else '过期' if (f, path) in bad else ''
                fh.write('\t'.join([f, '/'.join(path), zh.replace('\n', ' ⏎ '), e.replace('\n', ' ⏎ '), st]) + '\n')
        print('wrote', out.relative_to(ROOT))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
