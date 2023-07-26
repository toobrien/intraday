from    math                    import  log
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    statistics              import  mean, stdev
from    sys                     import  argv, path
path.append(".")
from    util.bar_tools          import  bar_rec, get_bars, get_sessions
from    util.contract_settings  import  get_settings
from    util.plotting           import  general_gaussian_hscatter
from    util.rec_tools          import  get_precision


# python research/ret_test.py ESU23_FUT_CME 12.13 2023-03-01 2023-08-01


if __name__ == "__main__":

    contract_id     = argv[1]
    session         = argv[2].split(".")
    start           = f"{argv[6]}T0" if len(argv) > 6 else None
    end             = f"{argv[7]}T0" if len(argv) > 7 else None
    _, tick_size    = get_settings(contract_id)
    precision       = get_precision(str(tick_size))
    bars            = get_bars(contract_id, start, end)
    
    returns = []
    idx     = get_sessions(bars, session[0], session[1])

    for date, bars in idx.items():

        o = bars[0][bar_rec.open]
        c = bars[-1][bar_rec.last]

        returns.append(log(c/o))

    mu      = mean(returns)
    sigma   = stdev(returns)

    normals = [ (ret - mu) / sigma for ret in returns ]

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            {
                "x":            normals,
                "marker_color": "#0000FF",
                "name":         "normals",
                "nbinsx":       100
            }
        )
    )

    fig.add_trace(
        general_gaussian_hscatter(0, 1, normals, "standard", stdevs = 5)
    )

    fig.show()