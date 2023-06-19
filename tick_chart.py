import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    util.features           import  delta, vbp, vbp_kde
from    util.rec_tools          import  get_tas, tick_series
from    util.sc_dt              import  ts_to_ds


# usage: python tick_chart.py CLN23_FUT_CME 0.01 2023-05-21 2023-05-22


BANDWIDTH   = 0.15
FMT         = "%Y-%m-%dT%H:%M:%S.%f"


if __name__ == "__main__":

    contract_id = argv[1]
    title       = argv[1].split(".")[0] if "." in argv[1] else argv[1].split("_")[0]
    multiplier  = float(argv[2])
    start       = argv[3] if len(argv) > 3 else None
    end         = argv[4] if len(argv) > 4 else None

    recs = get_tas(contract_id, multiplier, None, start, end)

    if not recs:

        print("no records matched")

        exit()

    x, y, z, t, c                           = tick_series(recs)
    vbp_hist                                = vbp(recs)
    vbp_y, vbp_x, max_vol, maxima, minima   = vbp_kde(vbp_hist, BANDWIDTH)
    deltas                                  = delta(recs)
    text                                    = []

    for i in range(len(z)):

        size        = z[i]
        start, end  = t[i]
        start_parts = ts_to_ds(start, FMT).split("T")
        end_parts   = ts_to_ds(end, FMT).split("T")
        date        = start_parts[0]
        
        text.append(
            f"{start_parts[0]} {start_parts[1]}<br>{end_parts[0]} {end_parts[1]}<br>{size}"
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

    fig.update_yaxes(showgrid = False)

    fig.add_trace(
        go.Scattergl(
            {
                "name":         title,
                "x":            x,
                "y":            y,
                "text":         text,
                "mode":         "markers",
                "marker_size":  z,
                "marker":       {
                                    "color":    c,
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
                "name":         "vbp",
                "y":            vbp_hist,
                "nbinsy":       len(set(vbp_hist)),
                "opacity":      0.5,
                "marker_color": "#0000FF"
            }
        ),
        row = 1,
        col = 1
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":        [ val * max_vol for val in vbp_x ],
                "y":        vbp_y,
                "name":     "vbp_kde",
                "marker":   { "color": "#FF0000" }
            }
        ),
        row = 1,
        col = 1
    )

    for m in maxima:

        fig.add_hline(
            y               = m,
            line_dash       = "dash", 
            line_color      = "#0000FF", 
            opacity         = 0.3,
            annotation_text = str(m)
        )

    for m in minima:

        fig.add_hline(
            y               = m,
            line_dash       = "dash",
            line_color      = "#FF0000",
            opacity         = 0.5,
            annotation_text = str(m)
        )

    fig.add_trace(
        go.Scatter(
            {
                "name": "delta",
                "x":    x,
                "y":    deltas,
                "text": [ f"{deltas[i] / x[i] * 100:0.1f}%" for i in range(len(x)) ],
                "line": { "color": "#0000FF" }
            }
        ),
        row = 2,
        col = 2
    )

    fig.show()