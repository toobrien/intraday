import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    statistics              import  mean, stdev
from    sys                     import  argv, path
path.append(".")
from    util.bar_tools          import  bar_rec, get_bars
from    util.contract_settings  import  get_settings
from    util.rec_tools          import  get_precision


# python research/rank_bars.py HOU23_FUT_CME 0.999 1 2023-07-01 2023-07-20

if __name__ == "__main__":

    contract_id     = argv[1]
    thresh          = float(argv[2])
    lag             = int(argv[3])
    start           = f"{argv[4]}T0" if len(argv) > 4 else None
    end             = f"{argv[5]}T0" if len(argv) > 5 else None
    _, tick_size    = get_settings(contract_id)
    precision       = get_precision(str(tick_size))
    bars            = get_bars(contract_id, start, end)
    title           = f"{contract_id} {start} - {end} thresh: {thresh} lag: {lag}"

    if not bars:

        print("no bars matched")
        
        exit()

    rngs = [ bar[bar_rec.high] - bar[bar_rec.low] for bar in bars ]
    
    p_hi    = sorted(rngs)[int(thresh * len(rngs))]
    mu      = mean(rngs)
    sigma   = stdev(rngs)
    count   = 0

    x       = []
    y       = []
    x_hi    = []
    y_hi    = []
    txt     = []

    for i in range(1, len(rngs) - lag):

        rng     = rngs[i]
        chg_cur = bars[i][bar_rec.last] - bars[i - 1][bar_rec.last]
        chg_nxt = bars[i + lag][bar_rec.last] - bars[i][bar_rec.last]

        if rng < p_hi:

            x.append(chg_cur)
            y.append(chg_nxt)
        
        else:

            count += 1

            x_hi.append(chg_cur)
            y_hi.append(chg_nxt)
            txt.append(f"{rng:0.{precision}f}")

    print(f"mu:         {mu:0.{precision}f}")
    print(f"sigma:      {sigma:0.{precision}f}")
    print(f"p(hi):      {p_hi:0.{precision}f}")
    print(f"count(hi):  {count}")

    fig = go.Figure()

    fig.add_trace(
        go.Scattergl(
            {
                "x":        x,
                "y":        y,
                "mode":     "markers",
                "marker":   { "color": "#0000FF" },
                "name":     "lo_rng"
            }
        )
    )

    fig.add_trace(
        go.Scattergl(
            {
                "x":        x_hi,
                "y":        y_hi,
                "mode":     "markers",
                "marker":   { "color": "#FF0000" },
                "name":     "hi_rng",
                "text":     txt
            }
        )
    )

    fig.show()