import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv, path

path.append(".")

from    util.aggregations       import  fixed_series, vbp
from    util.contract_settings  import  get_settings
from    util.modelling          import  gaussian_estimates, vbp_kde
from    util.plotting           import  gaussian_vscatter, get_title
from    util.rec_tools          import  get_precision, get_tas
from    util.sc_dt              import  ts_to_ds


# usage: python charts/fixed_chart.py CLQ23_FUT_CME 0.10 2023-07-01 2023-07-12


BANDWIDTH   = 0.15
FMT         = "%Y-%m-%dT%H:%M:%S.%f"
STDEVS      = 4
CLR_THRESH  = 0.7
MODE        = "LINE"


if __name__ == "__main__":

    contract_id             = argv[1]
    title                   = get_title(contract_id)
    multiplier, tick_size   = get_settings(contract_id)
    increment               = float(argv[2])
    start                   = argv[3] if len(argv) > 3 else None
    end                     = argv[4] if len(argv) > 4 else None
    precision               = get_precision(str(multiplier))
    recs                    = get_tas(contract_id, multiplier, None, start, end)

    if not recs:

        print("no records matched")

        exit()

    hist                                        = vbp(recs)
    x, y, a, b, v, t                            = fixed_series(recs, increment)
    vbp_hist                                    = vbp(recs)
    vbp_x, vbp_y, scale_factor, maxima, minima  = vbp_kde(hist, BANDWIDTH)
    gaussians                                   = gaussian_estimates(maxima, minima, vbp_hist)
    c                                           = []

    for i in range(len(v)):

        bid_vol     = b[i]
        ask_vol     = a[i]
        total_vol   = v[i]

        if bid_vol / total_vol > CLR_THRESH:

            c.append("#FF0000")
        
        elif ask_vol / total_vol > CLR_THRESH:

            c.append("#0000FF")
        
        else:

            c.append("#CCCCCC")

    fig = make_subplots(
        rows                = 1,
        cols                = 2,
        column_widths       = [ 0.1, 0.9 ],
        shared_yaxes        = True,
        shared_xaxes        = True,
        horizontal_spacing  = 0.025,
        vertical_spacing    = 0.025,
        subplot_titles      = ( title, "" )
    )

    if MODE == "SCATTER":

        fig.add_trace(
            go.Scattergl(
                {
                    "name":         title,
                    "x":            x,
                    "y":            y,
                    "mode":         "markers",
                    "marker_size":  v,
                    "marker":       {
                                        "color":    c,
                                        "sizemode": "area",
                                        "sizeref":  2. * max(v) / (40.**2),
                                        "sizemin":  4
                                    },
                    "text":         [
                                        f"{v[i]}<br>{ts_to_ds(t[i][0], FMT)}<br>{ts_to_ds(t[i][1], FMT)}"
                                        for i in range(len(t))
                                    ]
                }
            ),
            row = 1,
            col = 2
        )
    
    elif MODE == "LINE":

        fig.add_trace(
            go.Scattergl(
                {
                    "name": title,
                    "x":    x,
                    "y":    y,
                    "text": [
                                f"{v[i]}<br>{ts_to_ds(t[i][0], FMT)}<br>{ts_to_ds(t[i][1], FMT)}"
                                for i in range(len(t))
                            ]
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
                "marker_color": "#0000FF",
                "opacity":      0.3
            }
        ),
        row = 1,
        col = 1
    )

    for title, data in gaussians.items():

        mu      = data["mu"]
        sigma   = data["sigma"]

        fig.add_trace(
            gaussian_vscatter(
                mu,
                sigma,
                vbp_hist,
                tick_size,
                f"hvn [{mu:0.2f}, {sigma:0.2f}]"
            )
        )

        fig.add_hline(
            y               = mu,
            line_dash       = "dash",
            line_color      = "#ff66ff",
            opacity         = 0.5,
            annotation_text = f"{mu:0.2f}",
            row             = 1
        )

    fig.show()