from    bisect  import  bisect_left, bisect_right
from    os      import  listdir
from    os.path import  expanduser
import  polars  as      pl
from    sys     import  path
from    time    import  time

path.append(".")

from    config  import CONFIG


CFG = CONFIG["futs_db_v3"] # https://github.com/toobrien/futures_db_v3


def cat_df(
    type:   str,
    symbol: str,
    start:  str, 
    end:    str
):

    path    = expanduser(CFG[type][0]) if "~" in CFG[type][0] else CFG[type][0]
    key     = CFG[type][1]
    fns     = sorted(listdir(path))[1:] 
    fns     = fns[bisect_left(fns, start) : bisect_right(fns, end)][1:] # skip .gitignore

    if fns:

        dfs = [ 
                pl.read_parquet(f"{path}/{fn}").filter(pl.col(key) == symbol)
                for fn in fns
            ]
        df  = pl.concat(dfs, how = "vertical")

    else:
        
        df = None

    return df