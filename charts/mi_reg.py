from    operator                import  itemgetter
from    math                    import  e, log
from    numpy                   import  arange, array, std
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sklearn.linear_model    import  LinearRegression
from    sys                     import  argv, path

path.append(".")

from    util.aggregations       import  multi_tick_series
from    util.contract_settings  import  get_settings
from    util.plotting           import  get_title
from    util.rec_tools          import  get_tas, get_precision
from    util.sc_dt              import  ts_to_ds


# python charts/m0_log_reg.py HO###_FUT_CME:Z23:H24:M24:U24:Z24 1 2023-10-25

MODE    = "CHG"
FMT     = "%Y-%m-%dT%H:%M:%S.%f"


if __name__ == "__main__":

    contract_ids = argv[1].split(":")
    
    if "#" in contract_ids[0]:

        contract_ids = [ contract_ids[0].replace("###", MYY) for MYY in contract_ids[1:] ]
    
    multiplier, tick_size   = get_settings(contract_ids[0])
    precision               = get_precision(str(tick_size))
    show_chart              = int(argv[2])
    start                   = argv[3] if len(argv) > 3 else None
    end                     = argv[4] if len(argv) > 4 else None
    
    recs = [ 
            get_tas(contract_id, multiplier, None, start, end)
            for contract_id in contract_ids
        ]
    
    contract_ids    = [ get_title(contract_id) for contract_id in contract_ids ]
    recs            = multi_tick_series(recs, contract_ids)

    m0_id   = contract_ids[0]
    m0_0    = recs[m0_id]["y"][0]
    m0_logs = [ log(m0_i / m0_0) for m0_i in recs[m0_id]["y"] ]
    x_min   = min(m0_logs)
    x_max   = max(m0_logs)
    X       = arange(x_min, x_max, step = 0.001)
    X_      = X.reshape(-1, 1)

    fig = make_subplots(
            rows                = 2,
            cols                = 2,
            column_widths       = [ 0.8, 0.2 ],
            row_heights         = [ 0.8, 0.2 ],
            vertical_spacing    = 0.025,
            horizontal_spacing  = 0.025 
        )

    size_norm   = 2. * max(recs[contract_ids[0]]["z"]) / (40.**2)
    title       = f"{contract_ids[0]}    {start} - {end}"

    fig.update_layout(title_text = title)

    model = LinearRegression()

    print("contract\tm0_0\tm_i0\tb\ta\tr^2\tsigma\tten_bp_t")

    for contract_id in contract_ids[1:]:

        x, y, z, t, c, m0_y = itemgetter("x", "y", "z", "t", "c", "prev_m0")(recs[contract_id])
        div                 = y[0] if MODE == "CHG" else m0_0
        y_                  = array([ log(y_ / div) for y_ in y ])
        x_                  = array([ log(m0_i / m0_0) for m0_i in m0_y ])

        model.fit(array(x_).reshape(-1, 1), y_)

        Y                   = model.predict(X_)
        R2                  = model.score(X_, Y)
        LAST_X              = m0_logs[-1]
        LAST_Y              = model.predict([ [ LAST_X ] ])
        residuals           = y_ - model.predict(x_.reshape(-1, 1))
        sigma               = std(residuals)
        ten_bp_t            = y[0] * e**(0.001) - y[0]
        text                = [ 
                                f"{ts_to_ds(t[i], FMT)}<br>m0: {m0_y[i]:0.{precision}f}<br>m_i: {y[i]:0.{precision}f}<br>{residuals[i]:0.4f}"
                                for i in range(len(t)) 
                            ]

        fig.add_trace(
            go.Scattergl(
                {
                    "x":            x_,
                    "y":            y_,
                    "text":         text,
                    "mode":         "markers",
                    "marker_size":  z,
                    "marker":       {
                                        "sizemode": "area",
                                        "sizeref":  size_norm,
                                        "sizemin":  4
                                    },
                    "name":         contract_id
                }
            ),
            row = 1,
            col = 1
        )

        fig.add_trace(
            go.Scattergl(
                {
                    "x":            X,
                    "y":            Y,
                    "text":         [   
                                        f"{m0_0 * e**X[i]:0.{precision}f}<br>{div * e**Y[i]:0.{precision}f}" 
                                        for i in range(len(X)) 
                                    ],
                    "name":         f"{contract_id} model",
                    "mode":         "lines",
                    "line":         { "width": 0.5 },
                    "line_color":   "#FF00FF",
                    "opacity":      0.75
                }
            ),
            row = 1,
            col = 1
        )

        fig.add_trace(
            go.Scattergl(
                {
                    "x":        [ LAST_X ],
                    "y":        LAST_Y,
                    "name":     f"{contract_id} m_last",
                    "text":     [ f"{m0_0 * e**LAST_X:0.{precision}f}<br>{y[0] * e**LAST_Y[0]:0.{precision}f}" ],
                    "marker":   { "color": "#FF0000" }
                }
            ),
            row = 1,
            col = 1
        )

        fig.add_trace(
            go.Histogram(
                {
                    "x":        residuals,
                    "opacity":  0.5,
                    "name":     f"{contract_id} res hist",
                }
            ),
            row = 1,
            col = 2
        )

        fig.add_trace(
            go.Scattergl(
                {
                    "x":        x,
                    "y":        residuals,
                    "text":     text,
                    "mode":     "markers",
                    "marker":   {
                                    "sizemode": "area",
                                    "sizeref":  size_norm,
                                    "sizemin":  4
                                },
                    "name":     f"{contract_id} res plot",
                }
            ),
            row = 2,
            col = 1
        )

        print(f"{contract_id}\t\t{m0_0:0.{precision}f}\t{y[0]:0.{precision}f}\t{model.coef_[0]:0.4f}\t{model.intercept_:0.4f}\t{R2:0.4f}\t{sigma:0.4f}\t{ten_bp_t:0.04f}")

    if show_chart:
    
        fig.show()