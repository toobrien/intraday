import  plotly.graph_objects    as      go
from    sys                     import  argv
from    util.bar_tools          import  bar_rec, get_bars, get_sessions
from    util.rec_tools          import  n_days_ago


# python season.py ESU23_FUT_CME 30 12.13


if __name__ == "__main__":

    contract_id     = argv[1]
    days_ago        = int(argv[2])
    season          = argv[3].split(".")
    start           = f"{n_days_ago(days_ago)}T00:00:00"
    bars            = get_bars(contract_id, start)

    if not bars:

        print("no bars matched")

        exit()

    idx     = get_sessions(bars, season[0], season[1])
    fig     = go.Figure()

    for date, bars in idx.items():

        base = bars[0][bar_rec.open]

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    [ bar[bar_rec.time] for bar in bars ],
                    "y":    [ bar[bar_rec.last] - base for bar in bars ],
                    "name": date
                }
            )
        )

    fig.show()