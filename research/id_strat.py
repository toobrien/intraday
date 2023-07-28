from    math                    import  log
from    numpy                   import  percentile
import  plotly.graph_objects    as      go
from    statistics              import  stdev
from    sys                     import  argv, path
path.append(".")
from    typing                  import  List
from    util.bar_tools          import  bar_rec, get_bars, get_sessions
from    util.contract_settings  import  get_settings
from    util.pricing            import  fly, iron_fly
from    util.rec_tools          import  get_precision


# python research/id_strat.py ESU23_FUT_CME fly 12:00:00 13:00:00 13:00:00 2023-05-01 2023-08-01 5.0 5.0


def price_fly(
    kind:       str,            # "fly", "iron_fly"
    mid_strike: float,
    width:      float,
    bars:       List[bar_rec],
    f_sigmas:   dict
):

    x       = []
    y       = []
    pricer  = None

    if kind == "fly":

        pricer = fly
    
    elif kind == "iron_fly":

        pricer = iron_fly
    
    else:

        return None, None

    for bar in bars:

        time    = bar[bar_rec.time]
        f_sigma = f_sigmas[time]

        if f_sigma == 0:

            # last bar, no fwd return

            continue

        val = pricer(
                cur_price   = bar[bar_rec.last],
                mid         = mid_strike,
                width       = width,
                f_sigma     = f_sigmas[time]
            )
        
        x.append(time)
        y.append(val)

    t = [ str(mid_strike) for i in range(len(x)) ]

    return x, y, t


if __name__ == "__main__":

    contract_id     = argv[1]
    strategy        = argv[2]
    session_start   = argv[3]
    session_end     = argv[4]
    expiration      = argv[5]
    date_start      = f"{argv[6]}T0" if len(argv) > 6 else None
    date_end        = f"{argv[7]}T0" if len(argv) > 7 else None
    params          = argv[8:]
    _, tick_size    = get_settings(contract_id)
    precision       = get_precision(str(tick_size))
    bars            = get_bars(contract_id, date_start, date_end)
    title           = f"{contract_id}\t{strategy}\t{', '.join(params)}"

    if not bars:

        print("no bars matched")
        
        exit()

    idx             = get_sessions(bars, session_start, session_end)
    dt_idx          = { (bars[i][bar_rec.date], bars[i][bar_rec.time]) : i for i in range(len(bars)) }
    forward_returns = {}

    for date, s_bars in idx.items():

        try:
        
            settlement = bars[dt_idx[(date, expiration)]][bar_rec.last]
        
        except KeyError:

            # incomplete session

            continue

        for bar in s_bars:

            time = bar[bar_rec.time]

            if time not in forward_returns:

                forward_returns[time] = []

            forward_returns[time].append(log(settlement / bar[bar_rec.last]))
    
    f_sigmas = {
                time: stdev(forward_returns[time])
                for time in forward_returns.keys()
            }

    fig = go.Figure()

    fig.update_layout(title = title)

    ys          = []
    n_samples   = 0

    for date, s_bars in idx.items():

        if strategy in [ "fly", "iron_fly" ]:
               
                strike_inc  = float(params[0])
                width       = float(params[1])
                mid_strike  = strike_inc * round(s_bars[0][bar_rec.open] / strike_inc) # round to nearest strike 

                x, y, t = price_fly(strategy, mid_strike, width, s_bars, f_sigmas)
        
        else: 
            
            pass

        n_samples += 1

        ys.append(y)

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    x,
                    "y":    y,
                    "name": date,
                    "text": t
                }
            )
        )
        
    fig.show()

    # f_sigma debug

    '''
    for time in sorted(f_sigmas.keys()):

        print(f"{time}\t{f_sigmas[time]:0.6f}")

    fig2 = go.Figure()

    x_ = sorted(list(f_sigmas.keys()))
    y_ = [ f_sigmas[x] for x in x_ ]

    fig2.add_trace(
        go.Bar(
            x = x_,
            y = y_
        )
    )

    fig2.show()
    '''

    mins = sorted([ min(y) for y in ys ])
    maxs = sorted([ max(y) for y in ys ])

    print(f"{'lo'.rjust(15)}{'hi'.rjust(15)}")

    for p in [ 5, 15, 50, 85, 95 ]:

        pct = f"{str(p).rjust(2)}%:"
        lo  = f"{percentile(mins, p):0.{precision}f}".rjust(11)
        hi  = f"{percentile(maxs, p):0.{precision}f}".rjust(15)

        print(f"{pct}{lo}{hi}")

    print(f"\nn_samples: {n_samples}")

