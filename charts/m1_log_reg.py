from    operator                import  itemgetter
from    math                    import  e, log
from    numpy                   import  arange, array
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


# python charts/m1_log_reg.py HO###_FUT_CME:Z23:H24:M24:U24:Z24 2023-10-25

MODE    = "CHG"
FMT     = "%Y-%m-%dT%H:%M:%S.%f"


if __name__ == "__main__":

    contract_ids            = argv[1].split(":")
    contract_ids            = [ contract_ids[0].replace("###", MYY) for MYY in contract_ids[1:] ]
    multiplier, tick_size   = get_settings(contract_ids[0])
    precision               = get_precision(str(tick_size))
    start                   = argv[2] if len(argv) > 2 else None
    end                     = argv[3] if len(argv) > 3 else None
    
    recs = [ 
            get_tas(contract_id, multiplier, None, start, end)
            for contract_id in contract_ids
        ]
    
    contract_ids    = [ get_title(contract_id) for contract_id in contract_ids ]
    recs            = multi_tick_series(recs, contract_ids)

    m1_id   = contract_ids[0]
    m1_0    = recs[m1_id]["y"][0]
    m1_logs = [ log(m1_i / m1_0) for m1_i in recs[m1_id]["y"] ]
    x_min   = min(m1_logs)
    x_max   = max(m1_logs)
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

    print("contract\tm1_0\tm_i0\tb\ta\tr^2")

    for contract_id in contract_ids[1:]:

        x, y, z, t, c, logs = itemgetter("x", "y", "z", "t", "c", "log")(recs[contract_id])
        div                 = y[0] if MODE == "CHG" else m1_0
        y_                  = array([ log(y_ / div) for y_ in y ])
        m1_y                = [ y[i] / e**logs[i] for i in range(len(logs)) ]
        x_                  = array([ log(m1_i / m1_0) for m1_i in m1_y ])
        text                = [ f"{ts_to_ds(t[i], FMT)}<br>m1: {m1_y[i]:0.{precision}f}<br>m_i: {y[i]:0.{precision}f}" for i in range(len(t)) ]

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

        model.fit(array(x_).reshape(-1, 1), y_)

        Y       = model.predict(X_)
        R2      = model.score(X_, Y)
        LAST_X  = m1_logs[-1]
        LAST_Y  = model.predict([ [ LAST_X ] ])

        
        fig.add_trace(
            go.Scattergl(
                {
                    "x":            X,
                    "y":            Y,
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
                    "marker":   { "color": "#FF0000" }
                }
            ),
            row = 1,
            col = 1
        )

        residuals = y_ - model.predict(x_.reshape(-1, 1))

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

        print(f"{contract_id}\t\t{m1_0:0.{precision}f}\t{y[0]:0.{precision}f}\t{model.coef_[0]:0.4f}\t{model.intercept_:0.4f}\t{R2:0.4f}")

    fig.show()