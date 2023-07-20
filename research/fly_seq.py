import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    statistics              import  mean, median
from    sys                     import  argv, path
path.append(".")
from    util.bar_tools          import  bar_rec, get_bars, get_sessions
from    util.contract_settings  import  get_settings
from    util.rec_tools          import  get_precision


# python research/fly_seq.py ESU23_FUT_CME 06:30.13 5.0 5.0 5 2023-03-01 2023-07-14


if __name__ == "__main__":

    contract_id     = argv[1]
    session         = argv[2].split(".")
    strike_inc      = float(argv[3])
    width           = float(argv[4])
    time_inc        = int(argv[5])
    start           = f"{argv[6]}T0" if len(argv) > 6 else None
    end             = f"{argv[7]}T0" if len(argv) > 7 else None
    _, tick_size    = get_settings(contract_id)
    precision       = get_precision(str(tick_size))
    bars            = get_bars(contract_id, start, end)
    title           = f"{contract_id} {session[0]} - {session[1]} w: {width:0.{precision}f}"

    if not bars:

        print("no bars matched")
        
        exit()

    idx         = get_sessions(bars, session[0], session[1])
    vals        = {}
    rngs        = {}
    touches     = {}
    zeroes      = {}

    for date, bars in idx.items():

        for i in range(0, len(bars), time_inc):

            time        = bars[i][bar_rec.time]
            base        = strike_inc * round(bars[i][bar_rec.open] / strike_inc)                    # round to nearest strike
            close       = bars[-1][bar_rec.last] - base
            val         = max(width - abs(close), 0)
            rng         = bars[i][bar_rec.high] - bars[i][bar_rec.low]
            hi          = abs(max(bars[i:], key = lambda b: b[bar_rec.high])[bar_rec.high] - base)
            lo          = abs(min(bars[i:], key = lambda b: b[bar_rec.low])[bar_rec.low] - base)
            touch       = 1 if max(hi, lo) >= width else 0
            zero        = 1 if val == 0 else 0

            for t in [
                (vals, val),
                (rngs, rng),
                (touches, touch),
                (zeroes, zero)
            ]:

                data = t[0]

                if time not in data:

                    data[time] = []
            
                data[time].append(t[1])

    x       = sorted(list(vals.keys()))
    val_avg = [ mean(vals[time]) for time in x ]
    rng_avg = [ mean(rngs[time]) for time in x ]
    p_touch = [ mean(touches[time]) for time in x ]
    p_zero  = [ mean(zeroes[time]) for time in x ]
    text    = [ f"n = {len(vals[time])}" for time in x ]

    fig = make_subplots(
        rows                = 4,
        cols                = 1,
        row_heights         = [ 0.70, 0.10, 0.10, 0.10 ],
        subplot_titles      = (title, None),
        vertical_spacing    = 0.1
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":        x,
                "y":        val_avg,
                "text":     text,
                "name":     "avg val",
                "marker":   { "color": "#0000FF" }
            }
        ),
        row = 1,
        col = 1
    )

    fig.add_trace(
        go.Bar(
            {
                "x":        x,
                "y":        rng_avg,
                "name":     "avg rng",
                "marker":   { "color": "#0000FF" }
            }
        ),
        row = 2,
        col = 1
    )

    fig.add_trace(
        go.Bar(
            {
                "x":        x,
                "y":        p_touch,
                "name":     "p(touch)",
                "marker":   { "color": "#FF0000" }
            }
        ),
        row = 3,
        col = 1
    )

    fig.add_trace(
        go.Bar(
            {
                "x":        x,
                "y":        p_zero,
                "name":     "p(worthless)",
                "marker":   { "color": "#FF00FF" }
            }
        ),
        row = 4,
        col = 1
    )

    fig.show()