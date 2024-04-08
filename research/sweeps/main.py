# from    datetime                import  datetime, timedelta
from    bisect                  import  bisect_right
from    enum                    import  IntEnum
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
import  polars                  as      pl
from    sys                     import  argv, path
from    time                    import  time

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
    

if __name__ == "__main__":

    t0                      = time()
    contract_id             = argv[1]
    start_date              = argv[2]  
    start_time              = argv[3] if len(argv) > 3 else None
    end_time                = argv[4] if len(argv) > 4 else None
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

        sweep_j         = y[j]
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
                sweep_j
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

    down    = [ rec for rec in rets if not rec[0] ]
    x       = [ rec[7] for rec in down ]
    lowest  = [ rec[1] for rec in down ]
    last    = [ rec[5] for rec in down ]
    best    = [ rec[4] for rec in down ]
    text    = [ rec[6] for rec in down ]
    name    = "down"
    color   = "#FF0000"

    fig.add_trace(
        go.Scattergl(
            {
                "x":        x,
                "y":        best if MODE == "best" else last,
                "text":     text,
                "name":     "down",
                "mode":     "markers",
                "marker":   { "color": "#FF0000" }
            }
        ),
        row = 2,
        col = 1
    )

    up      = [ rec for rec in rets if rec[0] ]
    x       = [ rec[7] for rec in up ]
    highest = [ rec[2] for rec in up ]
    last    = [ rec[5] for rec in up ]
    best    = [ rec[3] for rec in up ]
    text    = [ rec[6] for rec in up ]
    name    = "up"
    color   = "#0000FF"

    fig.add_trace(
        go.Scattergl(
            {
                "x":        x,
                "y":        best if MODE == "best" else last,
                "text":     text,
                "name":     "up",
                "mode":     "markers",
                "marker":   { "color": "#0000FF" }
            }
        ),
        row = 2,
        col = 1
    )

    fig.show()

    print(f"{len(df)} recs")
    print(f"{time() - t0:0.1f}s")

    pass