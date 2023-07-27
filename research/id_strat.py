from    math                    import  log
import  plotly.graph_objects    as      go
from    statistics              import  stdev
from    sys                     import  argv, path
path.append(".")
from    typing                  import  List
from    util.bar_tools          import  bar_rec, get_bars, get_sessions
from    util.contract_settings  import  get_settings
from    util.pricing            import  fly, iron_fly
from    util.rec_tools          import  get_precision


# python research/id_strat.py ESU23_FUT_CME fly 12:00:00 13:00:00 2023-03-01 2023-08-01 5.0 5.0


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

    return x, y


if __name__ == "__main__":

    contract_id     = argv[1]
    strategy        = argv[2]
    session_start   = argv[3]
    session_end     = argv[4]
    date_start      = f"{argv[5]}T0" if len(argv) > 5 else None
    date_end        = f"{argv[6]}T0" if len(argv) > 6 else None
    params          = argv[7:]
    _, tick_size    = get_settings(contract_id)
    precision       = get_precision(str(tick_size))
    bars            = get_bars(contract_id, date_start, date_end)
    title           = f"{contract_id}\t{strategy}\t{', '.join(params)}"

    if not bars:

        print("no bars matched")
        
        exit()

    idx             = get_sessions(bars, session_start, session_end)
    closes          = {
                        date: idx[date][-1][bar_rec.last]
                        for date in idx.keys()
                    }
    forward_returns = {}

    for date, bars in idx.items():

        close = closes[date]

        for bar in bars:

            time = bar[bar_rec.time]

            if time not in forward_returns:

                forward_returns[time] = []

            forward_returns[time].append(log(close / bar[bar_rec.last]))
    
    f_sigmas = {
                time: stdev(forward_returns[time])
                for time in forward_returns.keys()
            }

    fig = go.Figure()

    fig.update_layout(title = title)

    for date, bars in idx.items():

        if strategy in [ "fly", "iron_fly" ]:
               
                strike_inc  = float(params[0])
                width       = float(params[1])
                mid_strike  = strike_inc * round(bars[0][bar_rec.open] / strike_inc) # round to nearest strike 

                x, y = price_fly(strategy, mid_strike, width, bars, f_sigmas)
        
        else: 
            
            pass

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    x,
                    "y":    y,
                    "name": date
                }
            )
        )

    '''
    for time in sorted(f_sigmas.keys()):

        print(f"{time}\t{f_sigmas[time]:0.6f}")
    '''
        
    fig.show()
