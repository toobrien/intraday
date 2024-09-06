from    datetime    import  datetime
from    os          import  listdir
import  polars      as      pl
from    typing      import  List


def get_dfs(
    folder:         str,
    limit:          int, 
    skip_weekend:   bool = True
) -> List[pl.DataFrame]:

    dates   = sorted(
                datetime.strptime(date[:-4], "%Y-%m-%d")
                for date in 
                listdir(f"./screens/reg/csvs/{folder}")
            )
    
    if skip_weekend:

        dates = [ date for date in dates if date.weekday() < 5 ]

    fns     = [ 
                f"./screens/reg/csvs/{folder}/{date.strftime('%Y-%m-%d')}.csv" 
                for date in dates 
            ][limit:]

    dfs     = { fn[-14:-4]: pl.read_csv(fn) for fn in fns }

    return dfs
