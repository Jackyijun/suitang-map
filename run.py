# 一键构建《隋及唐初形势图》
#   python run.py               全部重建：底图 → 疆域 → 汇编 → docs/index.html（约 1 分钟）
#   python run.py --html        沿用 build/ 里已算好的疆域，只重新汇编条目并生成页面（改了 content/ 的归属或文字时用）
#   python run.py --open        构建后在浏览器打开 docs/index.html
#   python run.py --preview 669 另出该年疆域草图 build/preview-669.png
import argparse, sys, webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'content')]


def main():
    ap = argparse.ArgumentParser(description='隋及唐初形势图 构建')
    ap.add_argument('--html', action='store_true', help='跳过疆域计算，只汇编并生成页面')
    ap.add_argument('--open', action='store_true', help='构建后在浏览器打开')
    ap.add_argument('--preview', type=int, metavar='年份', help='另出该年疆域草图')
    a = ap.parse_args()
    import build, assemble
    build.main(territory=not a.html)
    assemble.main()
    if a.preview:
        sys.path[:0] = [str(ROOT / 'tools')]
        import preview
        preview.main(a.preview)
    if a.open:
        webbrowser.open((ROOT / 'docs' / 'index.html').as_uri())


if __name__ == '__main__':
    main()
