# 算疆域，输出 build/*.json：底图 geo_base.json → 势力格 cells.pkl → 汇编 out_data.json
import sys, time
import config as C

sys.path[:0] = [str(C.CONTENT)]


def main(territory=True):
    t0 = time.time()
    C.BUILD.mkdir(exist_ok=True)
    import fetch_data
    fetch_data.main()
    if territory or not ((C.BUILD / 'cells.pkl').exists() and (C.BUILD / 'geo_base.json').exists()):
        import basemap
        basemap.main()
        import territory as T
        T.main()
    import compile_data
    compile_data.main()
    print(f'  [构建] {time.time() - t0:.0f}s')


if __name__ == '__main__':
    main()
