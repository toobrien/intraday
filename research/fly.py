from    bisect                  import  bisect_right
from    math                    import  ceil
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    statistics              import  mean, median
from    sys                     import  argv, path
path.append(".")
from    util.bar_tools          import  bar_rec, get_bars, get_sessions
from    util.contract_settings  import  get_settings
from    util.rec_tools          import  get_precision


# python research/fly.py ESU23_FUT_CME 12:30.13 5.0 5.0 2023-03-01 2023-07-14


if __name__ == "__main__":

    contract_id     = argv[1]
    session         = argv[2].split(".")
    strike_inc      = float(argv[3])
    width           = float(argv[4])
    start           = f"{argv[5]}T0" if len(argv) > 5 else None
    end             = f"{argv[6]}T0" if len(argv) > 6 else None
    _, tick_size    = get_settings(contract_id)
    precision       = get_precision(str(tick_size))
    bars            = get_bars(contract_id, start, end)
    title           = f"{contract_id} {session[0]} - {session[1]} w: {width:0.{precision}f}"

    if not bars:

        print("no bars matched")
        
        exit()

    idx     = get_sessions(bars, session[0], session[1])
    x       = []
    o       = []
    h       = []
    l       = []
    c       = []
    vals    = []
    text    = []

    for date, bars in idx.items():

        x.append(date)

        base    = strike_inc * round(bars[0][bar_rec.open] / strike_inc) # round to nearest strike
        hi      = max([ bar[bar_rec.high] for bar in bars ]) - base
        lo      = min([ bar[bar_rec.low] for bar in bars ]) - base
        close   = bars[-1][bar_rec.last] - base

        o.append(base)
        h.append(hi)
        l.append(lo)
        c.append(close)
        vals.append(max(width - abs(close), 0))

        val_txt = f"{vals[-1]:0.2f}"
        rng_txt = f"{close + base:0.{precision}f}, {base:0.{precision}f}"
        text.append(f"{val_txt}<br>{rng_txt}")

        print(f"{date}\t{val_txt}\t{rng_txt}")

    vals    = sorted(vals)
    p_best  = bisect_right(vals, 0) / len(vals) * 100
    p90     = vals[int(len(vals) * 0.9)]

    print(f"mean val:   {mean(vals):0.{precision}f}")
    print(f"median val: {median(vals):0.{precision}f}")
    print(f"worthless:  {p_best:0.1f}%")
    print(f"p90:        {p90:0.{precision}f}")
    print(f"total:      {len(vals)}")

    fig = make_subplots(
        rows                = 2,
        cols                = 1,
        row_heights         = [ 0.85, 0.15 ],
        subplot_titles      = ( title, None ),
        vertical_spacing    = 0.05
    )

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
                "close":    c,
                "name":     "price",
                "text":     text
            }
        ),
        row = 1,
        col = 1
    )

    fig.add_hline(y = width, row = 1, col = 1)
    fig.add_hline(y = -width, row = 1, col = 1)

    fig.add_trace(
        go.Histogram(
            x               = vals,
            marker_color    = "#0000FF",
            nbinsx          = 2 * ceil(width / tick_size),
            name            = "val"
        ),
        row = 2,
        col = 1
    )

    fig.show()