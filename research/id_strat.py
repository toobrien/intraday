from    math                    import  log
from    numpy                   import  percentile
import  plotly.graph_objects    as      go
from    statistics              import  mean, stdev
from    sys                     import  argv, path
path.append(".")
from    typing                  import  List, Callable
from    util.bar_tools          import  bar_rec, get_bars, get_sessions
from    util.contract_settings  import  get_settings
from    util.pricing            import  fly, iron_fly, call_vertical, put_vertical
from    util.rec_tools          import  get_precision


# python research/id_strat.py ESU23_FUT_CME fly 12:00:00 13:00:00 13:00:00 2023-05-01 2023-08-01 5.0 0 5.0


PRICERS = {
    "fly":              fly,
    "iron_fly":         iron_fly,
    "call_vertical":    call_vertical,
    "put_vertical":     put_vertical
}


def price_strategy(
    ref_strike:     float,
    pricer:         Callable,
    price_params:   dict,
    s_bars:         List[bar_rec],
    f_sigmas:       dict[str, List],
    precision:      float
):

    x   = []
    y   = []
    t   = []

    for bar in s_bars:

        time                        = bar[bar_rec.time]
        price                       = bar[bar_rec.last]
        price_params["cur_price"]   = price
        price_params["f_sigma"]     = f_sigmas[time]
        val                         = pricer(**price_params)

        x.append(time)
        y.append(val)
        t.append(f"str: {ref_strike:0.{precision}f}<br>cur: {price:0.{precision}f}<br>var: {price - ref_strike:0.{precision}f}")

    return x, y, t


def price_strategy_by_session(
    strategy:       str,
    bars:           List,       
    session_start:  str,
    session_end:    str,
    expiration:     str,
    strike_inc:     float,
    offset:         int,
    params:         dict,
    precision:      float
):

    res             = {}
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
    
    f_sigmas    = {
                    time: stdev(forward_returns[time])
                    for time in forward_returns.keys()
                }
    pricer      = PRICERS[strategy]

    for date, s_bars in idx.items():

        # round reference strike to nearest atm strike (+ offset, if any)

        ref_strike  = strike_inc * round(s_bars[0][bar_rec.open] / strike_inc) + offset * strike_inc

        if "fly" in strategy:
               
            width           = float(params[0])
            price_params    = {
                                "mid":          ref_strike,
                                "width":        width,
                            }

        elif "vertical" in strategy:

            width           = float(params[0])
            price_params    = { "width": width }

            if strategy == "call_vertical":

                 price_params["lo_strike"] = ref_strike
                
            elif strategy == "put_vertical":

                price_params["hi_strike"] = ref_strike
    
        else:

            print("invalid strategy")
    
            exit()

        x, y, t = price_strategy(ref_strike, pricer, price_params, s_bars, f_sigmas, precision)

        res[date] = {
            "x": x,
            "y": y,
            "t": t
        }

    return res


if __name__ == "__main__":

    contract_id     = argv[1]
    strategy        = argv[2]
    session_start   = argv[3]
    session_end     = argv[4]
    expiration      = argv[5]
    date_start      = argv[6] if len(argv) > 6 else None
    date_end        = argv[7] if len(argv) > 7 else None
    strike_inc      = float(argv[8])
    offset          = float(argv[9])
    params          = argv[10:]
    _, tick_size    = get_settings(contract_id)
    precision       = get_precision(str(tick_size))
    bars            = get_bars(contract_id, f"{date_start}T0", f"{date_end}T0")
    title           = f"{contract_id}\t{strategy}\t{', '.join(params)}\t{date_start} - {date_end}"

    if not bars:

        print("no bars matched")
        
        exit()

    res = price_strategy_by_session(
            strategy,
            bars,
            session_start,
            session_end,
            expiration,
            strike_inc,
            offset,
            params,
            precision
        )

    fig         = go.Figure()
    y_min       = []
    y_max       = []
    y_fin       = []
    n_samples   = 0

    fig.update_layout(title = title)

    for date, ax in res.items():

        x = ax["x"]
        y = ax["y"]
        t = ax["t"]

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

        y_min.append(min(y))
        y_max.append(max(y))
        y_fin.append(y[-1])

        n_samples += 1

    fig.show()

    y_min = sorted(y_min)
    y_max = sorted(y_max)
    y_fin = sorted(y_fin)

    print(f"{'lo'.rjust(15)}{'hi'.rjust(15)}{'fin'.rjust(15)}")

    for p in [ 10, 20, 30, 40, 50, 60, 70, 80, 90, 100 ]:

        pct = f"{str(p).rjust(3)}%:"
        lo  = f"{percentile(y_min, p):0.{precision}f}".rjust(10)
        hi  = f"{percentile(y_max, p):0.{precision}f}".rjust(15)
        fin = f"{percentile(y_fin, p):0.{precision}f}".rjust(15)

        print(f"{pct}{lo}{hi}{fin}")

    print("\n")
    print(f"fin avg:    {mean(y_fin):0.{precision}f}")
    print(f"n_samples:  {n_samples}")