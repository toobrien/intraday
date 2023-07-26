from    math                    import  log
import  plotly.graph_objects    as      go
from    statistics              import  stdev
from    sys                     import  argv, path
path.append(".")
from    util.bar_tools          import  bar_rec, get_bars, get_sessions
from    util.contract_settings  import  get_settings
from    util.pricing            import  fly
from    util.rec_tools          import  get_precision


# python research/fly_price.py ESU23_FUT_CME 12:00.13:00 5.0 5.0 2023-03-01 2023-08-01


if __name__ == "__main__":

    contract_id     = argv[1]
    session         = argv[2].split(".")
    strike_inc      = float(argv[3])
    width           = float(argv[4])
    start           = f"{argv[6]}T0" if len(argv) > 6 else None
    end             = f"{argv[7]}T0" if len(argv) > 7 else None
    _, tick_size    = get_settings(contract_id)
    precision       = get_precision(str(tick_size))
    bars            = get_bars(contract_id, start, end)
    title           = f"{contract_id} {session[0]} - {session[1]} w: {width:0.{precision}f}"

    if not bars:

        print("no bars matched")
        
        exit()

    idx             = get_sessions(bars, session[0], session[1])
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

    for date, bars in idx.items():

        x           = []
        y           = []
        mid_strike  = strike_inc * round(bars[0][bar_rec.open] / strike_inc) # round to nearest strike 

        for bar in bars:

            time    = bar[bar_rec.time]
            f_sigma = f_sigmas[time]

            if f_sigma == 0:

                # last bar, no fwd return

                continue

            val     = fly(
                        cur_price   = bar[bar_rec.last],
                        mid         = mid_strike,
                        width       = width,
                        f_sigma     = f_sigmas[time],
                        step        = 0.01
                    )
            
            x.append(time)
            y.append(val)
        
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
