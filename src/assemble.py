# 把 build/out_data.json 注入 src/template.html，输出 docs/index.html（成品，单文件）
# 另出 build/artifact.html：去掉文档外壳的同一页面，用于更新 claude.ai 上的地图
import json
import config as C

SHELL_END = '</body></html>'


def main():
    D = json.load(open(C.BUILD / 'out_data.json', encoding='utf-8'))
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
    main()
