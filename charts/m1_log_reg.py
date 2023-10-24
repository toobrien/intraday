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


# python charts/m1_log_reg.py HOZ23_FUT_CME:HOH24_FUT_CME:HOM24_FUT_CME:HOU24_FUT_CME:HOZ24_FUT_CME 2023-10-23


FMT = "%Y-%m-%dT%H:%M:%S.%f"


if __name__ == "__main__":

    contract_ids            = argv[1].split(":")
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
            rows            = 1,
            cols            = 2,
            column_widths   = [ 0.8, 0.2 ]
        )

    size_norm   = 2. * max(recs[contract_ids[0]]["z"]) / (40.**2)
    title       = f"{contract_ids[0]}    {start} - {end}"

    fig.update_layout(title_text = title)

    model = LinearRegression()

    print("contract_id\t\ta\tb\tr^2")

    for contract_id in contract_ids[1:]:

        y, z, t, c, logs    = itemgetter("y", "z", "t", "c", "log")(recs[contract_id])
        y_                  = array([ log(y_ / y[0]) for y_ in y ])
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

        residuals = y_ - model.predict(x_.reshape(-1, 1))

        fig.add_trace(
            go.Histogram(
                {
                    "x":        residuals,
                    "name":     f"{contract_id} residuals",
                    "opacity":  0.5
                }
            ),
            row = 1,
            col = 2
        )

        print(f"{contract_id}\t{model.coef_[0]:0.4f}\t{model.intercept_:0.4f}\t{R2:0.4f}")

    fig.show()