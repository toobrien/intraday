    
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    util.aggregations       import  tick_series, vbp
from    util.contract_settings  import  get_settings
from    util.modelling          import  vbp_gmm
from    util.plotting           import  gaussian_vscatter, get_title
from    util.rec_tools          import  get_precision, get_tas


# python gmm_chart.py CLQ23_FUT_CME 2023-06-22


MAX_COMPONENTS = 10


if __name__ == "__main__":

    contract_id             = argv[1]
    title                   = get_title(contract_id)
    multiplier, tick_size   = get_settings(contract_id)
    start                   = argv[2] if len(argv) > 2 else None
    end                     = argv[3] if len(argv) > 3 else None
    precision               = get_precision(str(multiplier))
    recs                    = get_tas(contract_id, multiplier, None, start, end)
    hist                    = vbp(recs)
    x, y, _, _, _           = tick_series(recs)
    fig                     = make_subplots(
        rows                = 1, 
        cols                = 2,
        column_widths       = [ 0.1, 0.9 ],
        horizontal_spacing  = 0.0,
        shared_yaxes        = True,
        subplot_titles      = [ "", f"{title} [ {start} - {end} ]" ]
    )

    means, sigmas, labels = vbp_gmm(y, hist, max_components = MAX_COMPONENTS)

    fig.add_trace(
        go.Scatter(
            {
                "x":        x,
                "y":        y,
                "mode":     "markers",
                "marker":   { "color": labels },
                "name":     contract_id
            }
        ),
        row = 1,
        col = 2
    )

    fig.add_trace(
        go.Histogram(
            {
                "y":            hist,
                "nbinsy":       len(set(hist)),
                "opacity":      0.5,
                "marker_color": "#0000FF",
                "name":         "vbp"
            }
        ),
        row = 1,
        col = 1
    )

    for i in range(len(means)):

        mu      = round(float(means[i]), precision)
        sigma   = round(float(sigmas[i]), precision)

        fig.add_trace(
            gaussian_vscatter(
                mu,
                sigma,
                hist,
                tick_size,
                f"c-{i} [{mu:0.{precision}f}, {sigma:0.{precision}f}]"
            ),
            row = 1,
            col = 1
        )
        

    fig.show()