    
from    numpy                   import  array
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv, path

path.append(".")

from    util.aggregations       import  agg_tick_series, tick_series, vbp
from    util.contract_settings  import  get_settings
from    util.modelling          import  vbp_gmm
from    util.plotting           import  gaussian_vscatter, get_title
from    util.rec_tools          import  get_precision, get_tas
from    util.sc_dt              import  ts_to_ds


# python charts/gmm_chart.py CLQ23_FUT_CME 5:10 0.1 2023-06-01


FMT = "%Y-%m-%dT%H:%M:%S.%f"


if __name__ == "__main__":

    contract_id             = argv[1]
    title                   = get_title(contract_id)
    multiplier, tick_size   = get_settings(contract_id)
    components              = argv[2].split(":")
    min_components          = int(components[0])
    max_components          = int(components[1])
    price_increment         = float(argv[3])
    start                   = argv[4] if len(argv) > 4 else None
    end                     = argv[5] if len(argv) > 5 else None
    precision               = get_precision(str(multiplier))
    recs                    = get_tas(contract_id, multiplier, None, start, end)
    hist                    = vbp(recs, precision)
    x, y, _, _, _           = tick_series(recs)
    x_, y_, _, _, v, t      = agg_tick_series(recs, price_increment)
    fig                     = make_subplots(
        rows                = 1, 
        cols                = 2,
        column_widths       = [ 0.1, 0.9 ],
        horizontal_spacing  = 0.0,
        shared_yaxes        = True,
        subplot_titles      = [ "", f"{title} [ {start} - {end} ]" ]
    )
    m, means, sigmas, _     = vbp_gmm(
                                y, 
                                hist, 
                                min_components = min_components, 
                                max_components = max_components
                            )
    labels                  = m.predict(array(y_).reshape(-1, 1))

    fig.add_trace(
        go.Scattergl(
            {
                "x":            x_,
                "y":            y_,
                "mode":         "markers",
                "marker":       {
                                    "color":    labels,
                                    "sizemode": "area",
                                    "sizeref":  2. * max(v) / (40.**2),
                                    "sizemin":  4
                                },
                "marker_size":  v,
                "name":         contract_id,
                "text":         [ 
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
                "y":            hist,
                "nbinsy":       int((max(hist) - min(hist)) / tick_size) + 1,
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

        fig.add_hline(
            y                   = mu,
            line_dash           = "dash",
            line_color          = "#ff66ff",
            opacity             = 0.5,
            annotation_text     = f"{mu:0.2f}",
            row                 = 1
        )
        

    fig.show()