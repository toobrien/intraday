from    numpy                   import  percentile
import  plotly.graph_objects    as      go
from    statistics              import  mean
from    sys                     import  argv, path
path.append(".")
from    research.id_strat       import  calc_fsigmas, get_sessions, price_strategy_by_session
from    time                    import  time
from    util.bar_tools          import  bar_rec, get_bars
from    util.contract_settings  import  get_settings
from    util.rec_tools          import  get_precision


# python research/id_strat_seq.py ESU23_FUT_CME fly 12:00:00 12:59:00 12:59:00 1 2023-05-01 2023-09-01 5.0 0 5.0


P_MAX = 90
P_MIN = 90
WIN_I = 30
WIN_J = None


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
    strike_inc      = float(argv[9])
    offset          = float(argv[10])
    params          = argv[11:]
    _, tick_size    = get_settings(contract_id)
    precision       = get_precision(str(tick_size))
    bars            = get_bars(contract_id, f"{date_start}T0", f"{date_end}T0")
    title           = f"{contract_id}\t{strategy}\t{', '.join(params)}\t{date_start} - {date_end}"

    if not bars:

        print("no bars matched")
        
        exit()

    idx         = get_sessions(bars, session_start, session_end)
    f_sigmas    = calc_fsigmas(bars, idx, expiration)               # only need to do this once, on the longest session
    x           = set()

    for _, s_bars in idx.items():

        x = x.union(set([ bar[bar_rec.time] for bar in s_bars ]))

    x       = sorted(list(x))
    x_      = []
    p_max   = []
    p_min   = []
    val_avg = []
    fin_avg = []


    for i in range(0, len(x), session_inc):

        t       = x[i]
        idx     = get_sessions(bars, t, session_end) # advance index
        res     = price_strategy_by_session(
                    strategy,
                    idx,
                    f_sigmas,
                    strike_inc,
                    offset,
                    params,
                    precision
                )

        # filter out series that aren't aligned with if clause

        y_min       = sorted([ min(ax["y"][WIN_I if WIN_I < len(ax) else 0:WIN_J]) for ax in res.values() if ax["x"][0] == t ])
        y_max       = sorted([ max(ax["y"][WIN_I if WIN_I < len(ax) else 0:WIN_J]) for ax in res.values() if ax["x"][0] == t ])
        y_fin       = [ ax["y"][-1]  for ax in res.values() if ax["x"][0] == t ]
        y_start     = [ ax["y"][0] for ax in res.values() if ax["x"][0] == t ]
        n_samples   = len(y_min)

        x_.append(t)
        p_max.append(percentile(y_max, P_MAX))
        p_min.append(percentile(y_min, P_MIN))
        val_avg.append(mean(y_start))
        fin_avg.append(mean(y_fin))

    fig = go.Figure()

    fig.update_layout(title = title)

    for trace in [
        ( p_max,    f"max_val p = {P_MAX}, w = [{WIN_I}:{WIN_J}]",  "#cccccc" ),
        ( p_min,    f"min_val p = {P_MIN}, w = [{WIN_I}:{WIN_J}]",  "#cccccc" ),
        ( val_avg,  "avg_val_at_t",                                 "#0000FF" ),
        ( fin_avg,  "avg_exp",                                      "#FF0000" ),
    ]:

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    x_,
                    "y":    trace[0],
                    "name": trace[1],
                    "line": { "color": trace[2] }
                }
            )
        )

    fig.show()

    print(f"finished in {time() - t0:0.1f}s")