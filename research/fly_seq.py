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

    idx     = get_sessions(bars, session[0], session[1])
    x       = []
    val_mu  = []
    p90s    = []
    max_len = max([ len(series) for series in idx.values() ])
    idx     = { key: val for key, val in idx.items() if len(val) == max_len }   # prune incomplete series
    times   = [ bar[bar_rec.time] for bar in list(idx.values())[0] ]            # all series times should be aligned

    for i in range(0, max_len, time_inc):

        x.append(times[i])

        vals = []

        for date, bars in idx.items():

            selected    = bars[i:]
            base        = strike_inc * round(selected[0][bar_rec.open] / strike_inc) # round to nearest strike
            close       = selected[-1][bar_rec.last] - base

            vals.append(max(width - abs(close), 0))

        vals    = sorted(vals)
        p90     = vals[int(len(vals) * 0.9)]

        val_mu.append(mean(vals))
        p90s.append(p90)

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            {
                "x":    x,
                "y":    val_mu,
                "name": "vals",
                "marker": { "color": "#0000FF" }
            }
        )
    )

    '''
    fig.add_trace(
        go.Scatter(
            {
                "x":    x,
                "y":    p90s,
                "name": "p90",
                "marker": { "color": "#FF0000" }
            }
        )
    )
    '''

    fig.show()