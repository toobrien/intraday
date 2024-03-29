import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv, path

path.append(".")

from    util.aggregations       import  split_tick_series, vbp
from    util.contract_settings  import  get_settings
from    util.plotting           import  get_title
from    util.features           import  delta
from    util.rec_tools          import  get_tas
from    util.sc_dt              import  ts_to_ds


# usage: python charts/tick_chart.py CLN23_FUT_CME 2023-05-21 2023-05-22


FMT = "%Y-%m-%dT%H:%M:%S.%f"


if __name__ == "__main__":

    contract_id     = argv[1]
    title           = get_title(contract_id)
    multiplier, _   = get_settings(contract_id)
    start           = argv[2] if len(argv) > 2 else None
    end             = argv[3] if len(argv) > 3 else None
    recs            = get_tas(contract_id, multiplier, None, start, end)

    if not recs:

        print("no records matched")

        exit()

    x, y, z     = split_tick_series(recs)
    cum_qty     = [ z[0] ] * len(z)
    vbp_hist    = vbp(recs)
    deltas      = delta(recs)
    text        = []

    for i in range(1, len(z)):

        cum_qty[i] = z[i] + cum_qty[i - 1]

    for i in range(len(z)):

        size    = z[i]
        end     = ts_to_ds(x[i], FMT)
        
        text.append(
            f"{end}<br>{size}"
        )

    fig = make_subplots(
        rows                = 2,
        cols                = 2,
        column_widths       = [ 0.1, 0.9 ],
        row_heights         = [ 0.8, 0.2 ],
        shared_yaxes        = True,
        shared_xaxes        = True,
        horizontal_spacing  = 0.025,
        vertical_spacing    = 0.025,
        subplot_titles      = ( title, "" )
    )

    fig.add_trace(
        go.Scattergl(
            {
                "name":         title,
                "x":            cum_qty,
                "y":            y,
                "text":         text,
                "mode":         "markers",
                "marker_size":  z,
                "marker":       {
                                    "color":    "#CCCCCC",
                                    "sizemode": "area",
                                    "sizeref":  2. * max(z) / (40.**2),
                                    "sizemin":  4
                                }
            }
        ),
        row = 1,
        col = 2
    )

    fig.add_trace(
        go.Histogram(
            {
                "name":     "vbp",
                "y":        vbp_hist,
                "nbinsy":   len(set(vbp_hist)),
                "opacity":  0.3
            }
        ),
        row = 1,
        col = 1
    )


    fig.add_trace(
        go.Scatter(
            {
                "name": "delta",
                "x":    cum_qty,
                "y":    deltas,
                "text": [ f"{deltas[i] / x[i] * 100:0.1f}%" for i in range(len(x)) ],
                "line": { "color": "#0000FF" }
            }
        ),
        row = 2,
        col = 2
    )

    fig.show()