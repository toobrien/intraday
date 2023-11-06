from    bisect                  import  bisect_left, bisect_right
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


# python charts/daily_reg.py HO###_FUT_CME:Z23:Z24 1,00:00:00,23:59:59 2023-10-01

# argv[2] defines the in-sample window: lag (days) , first day cutoff, last day cutoff
# the remainder of the last day is out-of-sample


FMT = "%Y-%m-%dT%H:%M:%S"


if __name__ == "__main__":


    contract_ids = argv[1].split(":")
    
    if "#" in contract_ids[0]:

        contract_ids = [ contract_ids[0].replace("###", MYY) for MYY in contract_ids[1:] ]

    multiplier, tick_size       = get_settings(contract_ids[0])
    precision                   = get_precision(str(tick_size))
    day_offset, start_t, end_t  = argv[2].split(",")
    day_offset                  = int(day_offset)
    start                       = argv[3] if len(argv) > 3 else None
    end                         = argv[4] if len(argv) > 4 else None
    title                       = f"{contract_ids[0]}    {start} - {end}"
    
    m0_id       = contract_ids[0]
    m0_recs_dt  = get_tas(m0_id, multiplier, FMT, start, end)
    m0_idx      = date_index(m0_id, m0_recs_dt)
    m0_recs_ts  = get_tas(m0_id, multiplier, None, start, end)

    m1_id       = contract_ids[1]
    m1_recs_dt  = get_tas(m1_id, multiplier, FMT, start, end)
    m1_idx      = date_index(m1_id, m1_recs_dt)
    m1_recs_ts  = get_tas(m1_id, multiplier, None, start, end)
    
    dates   = sorted(list(set(m0_idx.keys()).intersection(set(m1_idx.keys()))))

    model   = LinearRegression()

    fig = make_subplots(
            rows                = 1,
            cols                = 2,
            column_widths       = [ 0.8, 0.2 ],
            horizontal_spacing  = 0.025
        )
    
    fig.update_layout(title_text = title)

    for i in range(day_offset, len(dates)) in dates:

        start_date  = dates[i - day_offset]
        end_date    = dates[i]

        m0_i = m0_recs_dt[m0_idx[start_date][0]:bisect_left(m0_recs_dt, f"{start_date}T{start_t}", key = lambda r: r[0])]
        m0_k = m0_recs_dt[m0_idx[end_date][1]]
        m0_j = m0_recs_dt[bisect_right(m0_recs_dt, f"{end_date}T{end_t}", key = lambda r: r[0])] - m0_i
        
        m1_i = m1_idx[start_date[0]:bisect_left(m1_recs_dt, f"{start_date}T{start_t}", key = lambda r: r[0])]
        m1_k = m1_idx[end_date][1]
        m1_j = m1_recs_dt[bisect_right(m1_recs_dt, f"{end_date}T{end_t}", key = lambda r: r[0])] - m1_i

        recs = multi_tick_series([ m0_recs_ts[m0_i:m0_k], m1_recs_ts[m1_i:m1_k] ] , contract_ids)

        m0_recs = recs[m0_id]
        m1_recs = recs[m1_id]

        m1_log  = m1_recs["log"]
        m1_y    = m1_recs["y"]
        m0_0    = m1_y[0]
        m0_y    = [ m1_y[i] / e**m1_log[i] for i in range(len(m1_log)) ]
        m0_log  = [ log(m0_i / m0_0) for m0_i in m0_y ]

        X_in    = np.array(m0_log[:m0_j]).reshape(-1, 1)
        X_out   = np.array(m0_log[m0_j:]).reshape(-1, 1)
        Y_in    = np.array(m1_log[:m1_j])
        Y_out   = np.array(m1_log[m1_j:])

        m1_x    = list(range(len(X_out)))

        model.fit(X_in, Y_in)

        pred        = model.predict(X_out)
        residuals   = pred - Y_out

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    m1_x,
                    "y":    residuals,
                    "name": dates[i],
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
                    "name":     f"{dates[i]} hist"
                }
            ),
            row = 1,
            col = 2
        )

    fig.add_hline(
        y               = 0,
        line_color      = "#FF0000",
        opacity         = 0.5,
        row             = 1,
        col             = 1
    )

    fig.show()

    pass