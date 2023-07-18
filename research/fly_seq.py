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
    data    = {}

    for date, bars in idx.items():

        for i in range(0, len(bars), time_inc):

            selected    = bars[i:]
            time        = selected[0][bar_rec.time]
            base        = strike_inc * round(selected[0][bar_rec.open] / strike_inc) # round to nearest strike
            close       = selected[-1][bar_rec.last] - base
            val         = max(width - abs(close), 0)

            if time not in data:

                data[time] = []
            
            data[time].append(val)

    x       = sorted(list(data.keys()))
    y       = [ mean(data[time]) for time in x ]
    text    = [ f"n = {len(data[time])}" for time in x ]

    fig = go.Figure()

    fig.update_layout(title = f"{title}")

    fig.add_trace(
        go.Scatter(
            {
                "x":        x,
                "y":        y,
                "text":     text,
                "name":     "avg val",
                "marker":   { "color": "#0000FF" }
            }
        )
    )


    fig.show()