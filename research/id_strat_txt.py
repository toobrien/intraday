from    numpy                   import  percentile
import  plotly.graph_objects    as      go
from    statistics              import  mean
from    sys                     import  argv, path
from    time                    import  time

path.append(".")

from    research.id_strat       import  calc_fsigmas, get_sessions
from    util.bar_tools          import  bar_rec, get_bars
from    util.contract_settings  import  get_settings
from    util.features           import  ewma
from    util.pricing            import  fly, iron_fly
from    util.rec_tools          import  get_precision


# python research/id_strat_txt.py SPX:1m fly 15:00:00 15:59:00 15:59:00 1 2023-05-01 2023-09-01 EWMA_FIN 1 -1:1 5.0 5.0


EWMA_WIN = 5


def get_ref_strike(
    cur_price:  float, 
    offset:     int,
    strike_inc: float
):

    return strike_inc * round(cur_price / strike_inc) + offset * strike_inc


def run(args: list):

    contract_id     = args[1]
    strategy        = args[2]
    session_start   = args[3]
    session_end     = args[4]
    expiration      = args[5]
    session_inc     = int(args[6])
    date_start      = args[7] if len(args) > 7 else None
    date_end        = args[8] if len(args) > 8 else None
    mode            = args[9]
    plot            = int(args[10])
    offset_rng      = [ int(i) for i in args[11].split(":") ]
    strike_inc      = float(args[12])
    params          = [ float(i) for i in args[13:] ]
    bars            = get_bars(contract_id, f"{date_start}T0", f"{date_end}T0")
    _, tick_size    = get_settings(contract_id)
    precision       = get_precision(str(tick_size))

    if not bars:

        print("no bars matched")
        
        return None

    idx         = get_sessions(bars, session_start, session_end)
    f_sigmas    = calc_fsigmas(bars, idx, expiration)               # only need to do this once, on the longest session
    x           = set()

    for _, s_bars in idx.items():

        x = x.union(set([ bar[bar_rec.time] for bar in s_bars ]))

    offsets = range(offset_rng[0], offset_rng[1])
    x       = sorted(list(x))
    x_rng   = range(0, len(x), session_inc)
    out     = [ 
                [ None for _ in x_rng ]
                for _ in range(len(offsets))
            ]

    for i in range(len(offsets)):

        offset = offsets[i]

        for j in x_rng:

            t       = x[j]
            y       = []
            curs    = [
                        (  v[0][bar_rec.last], v[0][bar_rec.last], f_sigmas[v[0][bar_rec.time]] )
                        for _, v in get_sessions(bars, t, session_end).items()
                    ]
            fins    = [
                        (  v[-1][bar_rec.last], v[0][bar_rec.last], f_sigmas[v[-1][bar_rec.time]] )
                        for _, v in get_sessions(bars, t, session_end).items()
                    ]

            if "fly" in strategy:

                pricer  = fly if strategy == "fly" else iron_fly
                a       = [
                        pricer(cur_price = row[0], mid = get_ref_strike(row[1], offset, strike_inc), width = params[0], f_sigma = row[2])
                        for row in curs
                    ]
                b       = [
                        pricer(cur_price = row[0], mid = get_ref_strike(row[1], offset, strike_inc), width = params[0], f_sigma = row[2])
                        for row in fins
                    ]
                diff    = [ a[i] - b[i] for i in range(len(a)) ]
                y       = a if "CUR" in mode else b if "FIN" in mode else diff if "DIFF" in mode else None

            else:

                # not yet implemented
                
                print("invalid strategy")

                return None

            if not y:

                print("invalid mode")

                return None
            
            if "PCT_N" in mode:

                pct         = float(mode.split(":")[1])
                y           = sorted(y)
                out[i][j]   = percentile(y, pct)

            elif "PCT_A" in mode:

                thresh      = float(mode.split(":")[1])
                y           = [ 1 if val > thresh else 0 for val in y ]
                out[i][j]   = mean(y)

            elif "PCT_B" in mode:

                thresh      = float(mode.split(":")[1])
                y           = [ 1 if val < thresh else 0 for val in y ]
                out[i][j]   = mean(y)

            else:
                
                out[i][j] = mean(y)

    if "EWMA" in mode:
    
        out = [
            ewma(out[i], EWMA_WIN)
            for i in range(len(out))
        ]

    '''
    rows = [
        f"{x[i]:10}" + "\t".join([ f"{out[j][i]:0.{precision}f}" for j in range(len(offsets)) ])
        for i in x_rng
    ]
    '''

    if plot:

        fig = go.Figure()

        fig.update_layout(title = " ".join(argv[1:]))

        for i in range(len(out)):

            strike =  i + offset_rng[0]
            title  =  str(strike) if strike != 0 else "atm"

            fig.add_trace(
                go.Scatter(
                    {
                        "x":    x,
                        "y":    out[i],
                        "name": title
                    }
                )
            )

        fig.show()

    rows = {
        x[i] : [ round(out[j][i], precision) for j in range(len(offsets)) ]
        for i in x_rng
    }

    return rows


if __name__ == "__main__":

    t0   = time()
    rows = run(argv)

    if rows:

        for ts, vals in rows.items():

            print(f"{ts:10}" + "\t".join([ str(val) for val in vals ]))

    print(f"\nfinished in {time() - t0:0.1f}s")