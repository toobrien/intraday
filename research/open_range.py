import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    statistics              import  mean
from    sys                     import  argv, path
path.append(".")
from    util.bar_tools          import  bar_rec, get_bars, get_sessions
from    util.contract_settings  import  get_settings
from    util.rec_tools          import  get_precision


# python research/open_range.py ZCU23_FUT_CME 11:15.11:21 17:00.17:16 2023-03-01 2023-07-23


if __name__ == "__main__":

    contract_id     = argv[1]
    close_range     = argv[2].split(".")
    open_range      = argv[3].split(".")
    start           = f"{argv[4]}T0" if len(argv) > 4 else None
    end             = f"{argv[5]}T0" if len(argv) > 5 else None
    _, tick_size    = get_settings(contract_id)
    precision       = get_precision(str(tick_size))
    bars            = get_bars(contract_id, start, end)
    title           = f"{contract_id} {open_range[0]} - {open_range[1]}"

    if not bars:

        print("no bars matched")
        
        exit()

    close_idx   = get_sessions(bars, close_range[0], close_range[1])
    open_idx    = get_sessions(bars, open_range[0], open_range[1])
    date_idx    = sorted(list(set(close_idx.keys()).intersection(set(open_idx.keys()))))
    dt_key      = lambda b: ( b[bar_rec.date], b[bar_rec.time] )
    x           = []
    o_          = []
    h_          = []
    l_          = []
    c_          = []


    for date in date_idx:

        close_bars  = close_idx[date]
        open_bars   = open_idx[date]

        if len(open_bars) < 2 or not close_bars:

            continue

        prev_close  = close_bars[-1][bar_rec.last]
        o           = open_bars[0][bar_rec.open]
        h           = float("-inf")
        l           = float("inf")
        c           = open_bars[-1][bar_rec.last]

        for bar in open_bars:

            h = max(bar[bar_rec.high], h)
            l = min(bar[bar_rec.low], l)

        x.append(date)
        o_.append(o - prev_close)
        h_.append(h - prev_close)
        l_.append(l - prev_close)
        c_.append(c - prev_close)

    fig = make_subplots(rows = 1, cols = 1)

    fig.update_layout(
        { 
            'xaxis': {
                'rangeslider': { 'visible': False } 
            }
        }
    )

    fig.add_trace(
        go.Ohlc(
            {
                "x":        x,
                "open":     o_,
                "high":     h_,
                "low":      l_,
                "close":    c_,
                "name":     "price"
            }
        ),
        row = 1,
        col = 1
    )

    fig.show()