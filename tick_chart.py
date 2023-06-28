import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    util.contract_settings  import  get_settings
from    util.features           import  delta
from    util.plotting           import  gaussian_vscatter, get_title
from    util.aggregations       import  tick_series, vbp
from    util.modelling          import  gaussian_estimates, vbp_gmm, vbp_kde
from    util.rec_tools          import  get_tas, get_precision
from    util.sc_dt              import  ts_to_ds


# usage: python tick_chart.py CLN23_FUT_CME 2023-05-21 2023-05-22


BANDWIDTH   = 0.15
FMT         = "%Y-%m-%dT%H:%M:%S.%f"
STDEVS      = 4
KDE         = False
HVN         = True
LVN         = True
GAUSSIAN    = False
GMM         = True
GMM_MAX     = 5


if __name__ == "__main__":

    contract_id             = argv[1]
    title                   = get_title(contract_id)
    multiplier, tick_size   = get_settings(contract_id)
    precision               = get_precision(str(tick_size))
    start                   = argv[2] if len(argv) > 2 else None
    end                     = argv[3] if len(argv) > 3 else None
    title                   = f"{title} {start} - {end}"
    recs                    = get_tas(contract_id, multiplier, None, start, end)

    if not recs:

        print("no records matched")

        exit()

    x, y, z, t, c                               = tick_series(recs)
    vbp_hist                                    = vbp(recs, precision)
    vbp_y, vbp_x, scale_factor, maxima, minima  = vbp_kde(vbp_hist, BANDWIDTH)
    gaussians                                   = gaussian_estimates(maxima, minima, vbp_hist)
    deltas                                      = delta(recs)
    text                                        = []

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
                "nbinsy":       int((max(vbp_hist) - min(vbp_hist)) / tick_size) + 1, 
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

    if KDE:

        fig.add_trace(
            go.Scatter(
                {
                    "x":        [ val * scale_factor for val in vbp_x ],
                    "y":        vbp_y,
                    "name":     "vbp_kde",
                    "marker":   { "color": "#FF0000" }
                }
            ),
            row = 1,
            col = 1
        )

        if HVN:

            for hvn in maxima:

                fig.add_hline(
                    y               = hvn,
                    line_dash       = "dash", 
                    line_color      = "#0000FF", 
                    opacity         = 0.3,
                    annotation_text = str(hvn),
                    row             = 1
                )

        if LVN:

            for lvn in minima:

                fig.add_hline(
                    y               = lvn,
                    line_dash       = "dash",
                    line_color      = "#FF0000",
                    opacity         = 0.5,
                    annotation_text = str(lvn),
                    row             = 1
                )

    if GAUSSIAN:

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
                ),
                row = 1,
                col = 1
            )

            fig.add_hline(
                y                   = mu,
                line_dash           = "dash",
                line_color          = "#ff66ff",
                opacity             = 0.5,
                annotation_text     = f"{mu:0.2f}",
                row                 = 1
            )

    if GMM:

        mus, sigmas, _ = vbp_gmm(y, vbp_hist, max_components = GMM_MAX)

        for i in range(len(mus)):

            mu      = round(float(mus[i]), precision)
            sigma   = round(float(sigmas[i]), precision)

            fig.add_trace(
                gaussian_vscatter(
                    mu,
                    sigma,
                    vbp_hist,
                    tick_size,
                    f"c-{i} [{mu:0.{precision}f}, {sigma:0.{precision}f}]"
                ),
                row = 1,
                col = 1
            )

            fig.add_hline(
                y                   = mu,
                line_dash           = "dash",
                line_color          = "#ff66ff",
                opacity             = 0.5,
                annotation_text     = f"{mu:0.2f}",
                row                 = 1
            )

    fig.show()