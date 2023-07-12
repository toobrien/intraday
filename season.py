import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    statistics              import  mean, median
from    sys                     import  argv
from    util.bar_tools          import  bar_rec, get_bars, get_sessions
from    util.contract_settings  import  get_settings


# python season.py ESU23_FUT_CME 12.13 2023-07-01


# TICKS_PER_BIN = 4


if __name__ == "__main__":

    contract_id     = argv[1]
    season          = argv[2].split(".")
    start           = f"{argv[3]}T00:00:00" if len(argv) > 3 else None
    end             = f"{argv[4]}T00:00:00" if len(argv) > 4 else None
    _, tick_size    = get_settings(contract_id)
    bars            = get_bars(contract_id, start, end)
    chgs            = []

    if not bars:

        print("no bars matched")

        exit()

    idx     = get_sessions(bars, season[0], season[1])
    fig     = make_subplots(
                rows                = 2,
                cols                = 1,
                row_heights         = [ 0.85, 0.15 ],
                subplot_titles      = ( f"{contract_id} {season[0]} - {season[1]}", None ),
                vertical_spacing    = 0.05
            )

    for date, bars in idx.items():

        base = bars[0][bar_rec.open]

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    [ bar[bar_rec.time] for bar in bars ],
                    "y":    [ bar[bar_rec.last] - base for bar in bars ],
                    "name": date
                }
            ),
            row = 1,
            col = 1
        )

        chgs.append(bars[-1][bar_rec.last] - base)

    abs_chg = [ abs(x) for x in chgs ]
    
    print(f"mean:   {mean(abs_chg):0.2f}")
    print(f"median: {median(abs_chg):0.2f}")

    # n_bins = int(abs(max(chgs) - min(chgs)) / tick_size / TICKS_PER_BIN)

    n_bins = 100

    fig.add_trace(
        go.Histogram(
            x               = chgs,
            marker_color    = "#0000FF",
            nbinsx          = n_bins,
            name            = "chg"
        ),
        row = 2,
        col = 1
    )

    fig.show()