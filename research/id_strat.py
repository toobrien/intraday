from    math                    import  log
from    numpy                   import  percentile
import  plotly.graph_objects    as      go
from    statistics              import  mean, stdev
from    sys                     import  argv, path
path.append(".")
from    typing                  import  List
from    util.bar_tools          import  bar_rec, get_bars, get_sessions
from    util.contract_settings  import  get_settings
from    util.pricing            import  fly, iron_fly, call_vertical, put_vertical
from    util.rec_tools          import  get_precision


# python research/id_strat.py ESU23_FUT_CME fly 12:00:00 13:00:00 13:00:00 2023-05-01 2023-08-01 5.0 5.0 0


def price_fly(
    strategy:   str,            # "fly", "iron_fly"
    mid_strike: float,
    width:      float,
    s_bars:     List[bar_rec],
    f_sigmas:   dict,
    precision:  float
):

    x       = []
    y       = []
    t       = []
    pricer  = None

    if strategy == "fly":

        pricer = fly
    
    elif strategy == "iron_fly":

        pricer = iron_fly
    
    else:

        return None, None, None

    for bar in s_bars:

        time    = bar[bar_rec.time]
        price   = bar[bar_rec.last]
        val     = pricer(
                    cur_price   = price,
                    mid         = mid_strike,
                    width       = width,
                    f_sigma     = f_sigmas[time]
                )
        
        x.append(time)
        y.append(val)
        t.append(f"mid: {mid_strike:0.{precision}f}<br>cur: {price:0.{precision}f}<br>var: {abs(mid_strike - price):0.{precision}f}")

    return x, y, t


def price_vertical(
    strategy:   str,
    width:      float, 
    offset:     float,     
    s_bars:     List[bar_rec],
    f_sigmas:   dict,
    precision:  float
):

    x       = []
    y       = []
    t       = []
    pricer  = None

    if strategy == "call_vertical":

        pricer = call_vertical
    
    elif strategy == "put_vertical":

        pricer = put_vertical
    
    else:

        return None, None, None

    # round strike to nearest atm strike (+ offset, if any)

    strike = strike_inc * round(s_bars[0][bar_rec.open] / strike_inc) + offset * strike_inc
    
    for bar in s_bars:

        time    = bar[bar_rec.time]
        price   = bar[bar_rec.last]
        val     = pricer(
                    price,
                    strike,
                    width,
                    f_sigmas[time],
                )
        
        x.append(time)
        y.append(val)
        t.append(f"str: {strike:0.{precision}f}<br>cur: {price:0.{precision}f}<br>var: {price - strike:0.{precision}f}")
    
    return x, y, t


if __name__ == "__main__":

    contract_id     = argv[1]
    strategy        = argv[2]
    session_start   = argv[3]
    session_end     = argv[4]
    expiration      = argv[5]
    date_start      = argv[6] if len(argv) > 6 else None
    date_end        = argv[7] if len(argv) > 7 else None
    strike_inc      = float(argv[8])
    params          = argv[9:]
    _, tick_size    = get_settings(contract_id)
    precision       = get_precision(str(tick_size))
    bars            = get_bars(contract_id, f"{date_start}T0", f"{date_end}T0")
    title           = f"{contract_id}\t{strategy}\t{', '.join(params)}\t{date_start} - {date_end}"

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

        if "fly" in strategy:
               
            width       = float(params[0])
            offset      = int(params[1])

            # round mid strike to nearest atm strike (+ offset, if any)

            mid_strike  = strike_inc * round(s_bars[0][bar_rec.open] / strike_inc) + offset * strike_inc

            x, y, t = price_fly(strategy, mid_strike, width, s_bars, f_sigmas, precision)
        
        elif "vertical" in strategy:

            width   = float(params[0])
            offset  = float(params[1])
            
            x, y, t = price_vertical(strategy, width, offset, s_bars, f_sigmas, precision)
    
        else: 

            # invalid strategy
    
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

    final_vals = [ y_[-1] for y_ in ys ]

    print("\n")
    print(f"final val avg:      {mean(final_vals):0.{precision}f}")
    print(f"final val stdev:    {stdev(final_vals):0.{precision}f}")
    print(f"n_samples:          {n_samples}")