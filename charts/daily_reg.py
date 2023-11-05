from    math                    import  e, log
import  numpy                   as      np
from    operator                import  itemgetter
from    plotly.subplots         import  make_subplots
import  plotly.graph_objects    as      go
from    sklearn.linear_model    import  LinearRegression
from    sys                     import  argv, path

path.append(".")

from    util.aggregations       import multi_tick_series
from    util.contract_settings  import get_settings
from    util.rec_tools          import date_index, get_tas, get_precision


# python charts/daily_reg.py HO###_FUT_CME:Z23:Z24 2023-10-01


FMT = "%Y-%m-%dT%H:%M:%S"


if __name__ == "__main__":


    contract_ids = argv[1].split(":")
    
    if "#" in contract_ids[0]:

        contract_ids = [ contract_ids[0].replace("###", MYY) for MYY in contract_ids[1:] ]

    multiplier, tick_size   = get_settings(contract_ids[0])
    precision               = get_precision(str(tick_size))
    start                   = argv[2] if len(argv) > 2 else None
    end                     = argv[3] if len(argv) > 3 else None
    title                   = f"{contract_ids[0]}    {start} - {end}"
    
    m0_id   = contract_ids[0]
    m0_recs = get_tas(m0_id, multiplier, FMT, start, end)
    m0_idx  = date_index(m0_id, m0_recs)
    m0_recs = get_tas(m0_id, multiplier, None, start, end)

    m1_id   = contract_ids[1]
    m1_recs = get_tas(m1_id, multiplier, FMT, start, end)
    m1_idx  = date_index(m1_id, m1_recs)
    m1_recs = get_tas(m1_id, multiplier, None, start, end)
    
    dates   = sorted(list(set(m0_idx.keys()).intersection(set(m1_idx.keys()))))

    model   = LinearRegression()

    fig = make_subplots(
            rows                = 1,
            cols                = 2,
            column_widths       = [ 0.8, 0.2 ],
            horizontal_spacing  = 0.025
        )
    
    fig.update_layout(title_text = title)

    for date in dates:

        i0 = m0_idx[date]
        i1 = m1_idx[date]

        recs = [ m0_recs[i0[0]:i0[1]], m1_recs[i1[0]:i1[1]]]
        recs = multi_tick_series(recs, contract_ids)

        m0_recs = recs[m0_id]
        m1_recs = recs[m1_id]

        m1_log  = m1_recs["log"]
        m1_x    = list(range(len(m1_recs["x"])))
        m1_y    = m1_recs["y"]
        m0_0    = m1_y[0]
        m0_y    = [ m1_y[i] / e**m1_log[i] for i in range(len(m1_log)) ]
        m0_log  = [ log(m0_i / m0_0) for m0_i in m0_y ]

        X       = np.array(m0_log).reshape(-1, 1)
        Y       = np.array(m1_log)

        model.fit(X, Y)

        Y_          = model.predict(X)
        residuals   = Y - Y_

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    m1_x,
                    "y":    residuals,
                    "name": date,
                    "mode": "markers"
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
                    "name":     f"{date} hist"
                }
            )
        )

        pass

    fig.show()

    pass