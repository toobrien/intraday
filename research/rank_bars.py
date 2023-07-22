import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    statistics              import  mean, stdev
from    sys                     import  argv, path
path.append(".")
from    util.bar_tools          import  bar_rec, get_bars
from    util.contract_settings  import  get_settings
from    util.rec_tools          import  get_precision


# python research/rank_bars.py HOU23_FUT_CME 0.999 2023-07-01 2023-08-01

if __name__ == "__main__":

    contract_id     = argv[1]
    thresh          = float(argv[2])
    start           = f"{argv[3]}T0" if len(argv) > 3 else None
    end             = f"{argv[4]}T0" if len(argv) > 4 else None
    _, tick_size    = get_settings(contract_id)
    precision       = get_precision(str(tick_size))
    bars            = get_bars(contract_id, start, end)
    title           = f"{contract_id} {start} - {end} thresh: {thresh}"

    if not bars:

        print("no bars matched")
        
        exit()

    rngs = [ bar[bar_rec.high] - bar[bar_rec.low] for bar in bars ]
    
    p_hi    = sorted(rngs)[int(thresh * len(rngs))]
    mu      = mean(rngs)
    sigma   = stdev(rngs)
    count   = 0

    for i in range(len(rngs)):

        if rngs[i] >= p_hi:

            count += 1

            print(f"{bars[i][bar_rec.date]} {bars[i][bar_rec.time]} {rngs[i]:0.{precision}f}")

    print(f"mu:         {mu:0.{precision}f}")
    print(f"sigma:      {sigma:0.{precision}f}")
    print(f"p(hi):      {p_hi:0.{precision}f}")
    print(f"count(hi):  {count}")

    fig = make_subplots(cols = 2)

    fig.add_trace(
        go.Histogram(
            {
                "x":            rngs,
                "name":         "count",
                "marker_color": "#0000FF"
            }
        ),
        row = 1,
        col = 1
    )

    fig.add_trace(
        go.Histogram(
            {
                "x":                    rngs,
                "cumulative_enabled":   True,
                "name":                 "cdf",
                "histnorm":             "probability density",
                "marker_color":         "#0000FF"
            }
        ),
        row = 1,
        col = 2
    )

    fig.show()