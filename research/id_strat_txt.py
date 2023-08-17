from    statistics              import  mean
from    sys                     import  argv, path

path.append(".")

from    research.id_strat       import  calc_fsigmas, get_sessions
from    time                    import  time
from    util.bar_tools          import  bar_rec, get_bars
from    util.contract_settings  import  get_settings
from    util.features           import  ewma
from    util.pricing            import  fly, iron_fly
from    util.rec_tools          import  get_precision


# python research/id_strat_txt.py SPX:1m fly 15:00:00 15:59:00 15:59:00 1 2023-05-01 2023-09-01 EWMA_FIN -1:1 5.0 5.0


EWMA_WIN    = 5


def get_ref_strike(cur_price: float, offset: int):

    return strike_inc * round(cur_price / strike_inc) + offset * strike_inc


if __name__ == "__main__":

    t0              = time()
    contract_id     = argv[1]
    strategy        = argv[2]
    session_start   = argv[3]
    session_end     = argv[4]
    expiration      = argv[5]
    session_inc     = int(argv[6])
    date_start      = argv[7] if len(argv) > 7 else None
    date_end        = argv[8] if len(argv) > 8 else None
    mode            = argv[9]
    offset_rng      = [ int(i) for i in argv[10].split(":") ]
    strike_inc      = float(argv[11])
    params          = [ float(i) for i in argv[12:] ]
    bars            = get_bars(contract_id, f"{date_start}T0", f"{date_end}T0")
    _, tick_size    = get_settings(contract_id)
    precision       = get_precision(str(tick_size))

    if not bars:

        print("no bars matched")
        
        exit()

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
            
            if "FIN" in mode:

                vals    =   [
                            (  v[-1][bar_rec.last], v[0][bar_rec.last], f_sigmas[v[-1][bar_rec.time]] )
                            for _, v in get_sessions(bars, t, session_end).items()
                        ]

            elif "CUR" in mode:

                vals    =   [
                            (  v[0][bar_rec.last], v[0][bar_rec.last], f_sigmas[v[0][bar_rec.time]] )
                            for _, v in get_sessions(bars, t, session_end).items()
                        ]
            
            else:

                print("invalid mode")

                exit()

            if "fly" in strategy:

                pricer = fly if strategy == "fly" else iron_fly

                y = [
                    pricer(cur_price = row[0], mid = get_ref_strike(row[1], offset), width = params[0], f_sigma = row[2])
                    for row in vals
                ]

            else:

                # not yet implemented

                pass
            
            out[i][j] = mean(y)

    if "EWMA" in mode:
    
        out = [
            ewma(out[i], EWMA_WIN)
            for i in range(len(out))
        ]

    rows = [
        f"{x[i]:10}" + "\t".join([ f"{out[j][i]:0.{precision}f}" for j in range(len(offsets)) ])
        for i in x_rng
    ]

    for row in rows:

        print(row)

    print(f"\nfinished in {time() - t0:0.1f}s")