import  plotly.graph_objects    as go
from    plotly.subplots         import make_subplots
from    sys                     import argv, path
path.append(".")
from    util.bar_tools          import bar_rec, get_bars, get_sessions
from    util.contract_settings  import get_settings


# python research/fly.py ESU23_FUT_CME 12:30.13 5 2023-03-01 2023-07-14

if __name__ == "__main__":

    contract_id     = argv[1]
    session         = argv[2].split(".")
    width           = int(argv[3])
    start           = f"{argv[4]}T0" if len(argv) > 4 else None
    end             = f"{argv[5]}T0" if len(argv) > 5 else None
    _, tick_size    = get_settings(contract_id)
    bars            = get_bars(contract_id, start, end)
    title           = f"{contract_id} {start} - {end}"

    if not bars:

        print("no bars matched")
        
        exit()

    idx = get_sessions(bars, session[0], session[1])
    x   = []
    o   = []
    h   = []
    l   = []
    c   = []

    for date, bars in idx.items():

        x.append(date)

        base    = bars[0][bar_rec.open]
        hi      = max([ bar[bar_rec.high] for bar in bars ]) - base
        lo      = min([ bar[bar_rec.low] for bar in bars ]) - base
        close   = bars[-1][bar_rec.last] - base

        o.append(base)
        h.append(hi)
        l.append(lo)
        c.append(close)

    fig = go.Figure()

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
                "open":     o,
                "high":     h,
                "low":      l,
                "close":    c
            }
        )
    )

    fig.add_hline(y = width)
    fig.add_hline(y = -width)

    fig.show()

    pass