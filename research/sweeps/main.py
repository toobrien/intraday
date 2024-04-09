# from    datetime                import  datetime, timedelta
from    bisect                  import  bisect_right
from    enum                    import  IntEnum
from    numpy                   import  mean, sum
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
import  polars                  as      pl
from    sys                     import  argv, path
from    time                    import  time
from    typing                  import  List

path.append(".")

from util.aggregations          import tick_series
from util.contract_settings     import get_settings
from util.rec_tools             import quick_tas, get_precision, tas_rec
from util.sc_dt                 import ts_to_ds


COLS = [
    "timestamp",    # unabridged %Y-%m-%dT%H:%M:%S.%f
    "start_rec",    # first record (offset from start of file)
    "end_rec",      # last record
    "ticks",
    "min_price",
    "max_price",
    "qty",
    "side"
]


class sweep_rec(IntEnum):

    timestamp = 0
    start_rec = 1
    end_rec   = 2
    ticks     = 3
    min_price = 4
    max_price = 5
    qty       = 6
    side      = 7


FMT         = "%Y-%m-%dT%H:%M:%S.%f"
SLICE_LEN   = 10000
WIN_MIN     = 2000
WIN_MAX     = 10000
MODE        = "best"


# python research/sweeps/main.py ESM24_FUT_CME 2024-03-18
    

def plot_rets(
    fig:    go.Figure,
    rets:   List, 
    side:   int
):

    recs    = [ rec for rec in rets if rec[0] == side ]
    x       = [ rec[7] for rec in recs ]
    last    = [ rec[5] for rec in recs ]
    best    = [ rec[4] for rec in recs ] if not side else [ rec[4] for rec in recs ]
    text    = [ rec[6] for rec in recs ]
    name    = "down" if not side else "up"
    color   = "#FF0000" if not side else "#0000FF"

    fig.add_trace(
        go.Scattergl(
            {
                "x":        x,
                "y":        best if MODE == "best" else last,
                "text":     text,
                "name":     name,
                "mode":     "markers",
                "marker":   { "color": color }
            }
        ),
        row = 2,
        col = 1
    )

'''
    0   side,
    1   min_price,
    2   max_price,
    3   min_win,
    4   max_win,
    5   last,
    6   name,
    7   ticks if side else -ticks
'''


def print_res(rets: List, target: int, side: int):

    if not target:

        return
    
    recs = [ 
        (
            rec[7],                     # ticks
            rec[3] if side else rec[4], # best
            rec[5]                      # last
        )
        for rec in rets if rec[0] == side 
    ]

    ticks   = sorted(list(set([ rec[0] for rec in recs])), reverse = not side)
    label   = "up" if side else "dn"

    print(f'\n{label:10}{"avg":10}{"total":10}{"%":10}{"n":10}\n')

    for tick in ticks:

        results = []

        if side: 
        
            limit   = tick - target
            results = [ rec for rec in recs if rec[0] >= tick ]
            results = [
                        target if rec[1] <= limit else tick - rec[2]
                        for rec in results
                    ]
        
        else:

            limit   = tick + target 
            results = [ rec for rec in recs if rec[0] <= tick ]
            results = [ 
                        target if rec[1] >= limit else rec[2] - tick 
                        for rec in results
                    ]

        avg         = mean(results)
        total       = sum(results)
        n           = len(results)
        pct         = len(sum([ 1 for res in results if res == limit ]) / len(results))

        print(f'{tick:<10}{avg:<10.1f}{total:<10}{pct:<10.2f}{n:<10}')


if __name__ == "__main__":

    t0                      = time()
    contract_id             = argv[1]
    target                  = int(argv[2]) if argv[2] != "-" else None
    start_date              = argv[3]  
    start_time              = argv[4] if len(argv) > 4 else None
    end_time                = argv[5] if len(argv) > 5 else None
    multiplier, tick_size   = get_settings(contract_id)
    precision               = get_precision(contract_id)
    df                      = pl.read_csv(f"./research/sweeps/store/{contract_id}.csv")
    df                      = df.filter(pl.col("timestamp") >= start_date)

    #window_days            = int(argv[2])
    #start_date             = datetime.strptime(df["timestamp"].max().split("T")[0], "%Y-%m-%d") - timedelta(days = window_days)
    #start_date             = start_date.strftime("%Y-%m-%d")
    #df                     = df.filter(pl.col("timestamp") >= start_date)
    
    df                      = df.with_columns(df["timestamp"].str.slice(11).alias("time"))
    df                      = df.filter(pl.col("time") >= start_time) if start_time else df
    df                      = df.filter(pl.col("time") <= end_time) if end_time else df
    rets                    = []
    fig                     = make_subplots(rows = 2, cols = 1)

    for row in df.iter_rows():

        recs            = quick_tas(contract_id, multiplier, None, row[sweep_rec.start_rec], row[sweep_rec.end_rec] + SLICE_LEN)
        ts              = recs[0][tas_rec.timestamp]
        name            = ts_to_ds(ts, FMT)
        side            = row[sweep_rec.side]
        ticks           = row[sweep_rec.ticks]
        x, y, z, t, _   = tick_series(recs)
        
        ds              = [ ts_to_ds(t_[0], FMT) for t_ in t ]
        t_0             = t[0][0]
        t               = [ t_[0] - t_0 for t_ in t ]
        t_0             = t[0]
        ms              = [ t_ // 1000 for t_ in t]
        color           = [ "#FF00FF" if ms_ == 0 else "#0000FF" for ms_ in ms ]
        text            = [ f"{z[i]}<br>{ms[i]} ms<br>{ds[i]}" for i in range(len(z)) ]

        x               = [ i for i in range(len(x)) ]

        y_0             = y[0]
        y               = [ (y_ - y_0) / tick_size for y_ in y ]

        j               = bisect_right(ms, 1)           # first non-sweep trade
        k               = bisect_right(ms, WIN_MIN)
        m               = bisect_right(ms, WIN_MAX)

        x               = x[:m]
        y               = y[:m]
        color           = color[:m]
        text            = text[:m]

        min_price       = min(y[j:])
        max_price       = max(y[j:])
        min_win         = min(y[k:m]) if k < m else min_price
        max_win         = max(y[k:m]) if k < m else max_price
        last            = y[-1]

        rets.append(
            [
                side,
                min_price,
                max_price,
                min_win,
                max_win,
                last,
                name,
                ticks if side else -ticks
            ]
        )

        fig.add_trace(
            go.Scattergl(
                {
                    "x":        x,
                    "y":        y,
                    "marker":   { "color": color },
                    "text":     text,
                    "mode":     "markers",
                    "name":     name
                }
            )
        )

    plot_rets(fig, rets, 0)
    plot_rets(fig, rets, 1)

    print_res(rets, target, 0)
    print_res(rets, target, 1)

    print("\n")

    fig.show()

    print(f"{len(df)} recs")
    print(f"{time() - t0:0.1f}s")