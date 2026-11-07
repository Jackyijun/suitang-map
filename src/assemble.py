# 并入英文、检查缺译，把 build/out_data.json 注入 src/template.html，输出 docs/index.html（成品，单文件）
# 另出 build/artifact.html：去掉文档外壳的同一页面，用于更新 claude.ai 上的地图
#   python src/assemble.py           严格：有缺译或过期的英文就报错退出
#   python src/assemble.py --draft   草稿：缺译、过期处临时显示中文，只给警告
import json, sys
from collections import Counter
import config as C
import i18n

SHELL_END = '</body></html>'


def check_english(geo, data, draft):
    missing, stale, unlocked = i18n.check(geo, data)
    bad = missing + stale
    if unlocked:
        print(f'  [英文] 提醒：{len(unlocked)} 条英文未登记指纹（改完英文后运行 python tools/i18n.py lock）')
    if not bad:
        print('  [英文] 齐全')
        return
    msg = (f'英文缺译 {len(missing)} 条、过期 {len(stale)} 条：'
           + '、'.join(f'{f} {n}' for f, n in Counter(f for f, _, _ in bad).items())
           + '。运行 python tools/i18n.py todo 查看清单。')
    if not draft:
        sys.exit('  [英文] ' + msg + '\n  如只想先看效果，用 python run.py --html --draft（缺译处显示中文）。')
    print('  [英文] 草稿模式，' + msg)


def main(draft=False):
    D = json.load(open(C.BUILD / 'out_data.json', encoding='utf-8'))
    check_english(D['GEO'], D['DATA'], draft)
    D['GEO'], D['DATA'] = i18n.attach(D['GEO'], D['DATA'])
    tpl = (C.SRC / 'template.html').read_text(encoding='utf-8')
    js = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':'))
    out = tpl
    for k, v in (('__UCSS_LIGHT__', D['css_l']), ('__UCSS_DARK__', D['css_d']), ('__GEO__', js(D['GEO'])), ('__DATA__', js(D['DATA']))):
        assert k in out, k
        out = out.replace(k, v)
    C.DOCS.mkdir(exist_ok=True)
    (C.DOCS / 'index.html').write_text(out, encoding='utf-8', newline='\n')
    (C.DOCS / '.nojekyll').write_text('', encoding='utf-8')
    shell, body = out.split('\n', 1)
    assert shell.startswith('<!doctype html>') and body.rstrip().endswith(SHELL_END)
    (C.BUILD / 'artifact.html').write_text(body.rstrip()[:-len(SHELL_END)].rstrip() + '\n', encoding='utf-8', newline='\n')
    print(f'  [页面] docs/index.html {len(out.encode()) // 1024} KB')


if __name__ == '__main__':
    main(draft='--draft' in sys.argv[1:])
