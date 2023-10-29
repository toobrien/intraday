from    operator                import  itemgetter
from    math                    import  e, log
import  plotly.graph_objects    as      go
from    numpy                   import  arange, array, mean, std
from    sklearn.linear_model    import  LinearRegression
from    sys                     import  argv, path

path.append(".")

from    util.aggregations       import  multi_tick_series
from    util.contract_settings  import  get_settings
from    util.plotting           import  get_title
from    util.rec_tools          import  get_tas, get_precision


# python charts/price_spread.py HO###_FUT_CME:Z23:Z24 1:2.9790,-2:2.6940 2023-10-26


FMT = "%Y-%m-%dT%H:%M:%S.%f"


if __name__ == "__main__":

    contract_ids            = argv[1].split(":")
    contract_ids            = [ contract_ids[0].replace("###", MYY) for MYY in contract_ids[1:] ]
    multiplier, tick_size   = get_settings(contract_ids[0])
    precision               = get_precision(str(tick_size))
    legs                    = argv[2].split(",")
    m1_qty, m1_entry        = ( float(part) for part in legs[0].split(":") )
    m2_qty, m2_entry        = ( float(part) for part in legs[1].split(":") )
    start                   = argv[3] if len(argv) > 3 else None
    end                     = argv[4] if len(argv) > 4 else None
    
    recs = [ 
            get_tas(contract_id, multiplier, None, start, end)
            for contract_id in contract_ids
        ]
    
    contract_ids    = [ get_title(contract_id) for contract_id in contract_ids ]
    recs            = multi_tick_series(recs, contract_ids)

    m1_0        = recs[contract_ids[0]]["y"][0]
    m1_last     = recs[contract_ids[0]]["y"][-1]
    m2_y, logs  = itemgetter("y", "log")(recs[contract_ids[1]])
    m2_0        = m2_y[0]
    m2_last     = m2_y[-1]
    m1_y        = [ m2_y[i] / e**logs[i] for i in range(len(logs)) ]
    Y           = array([ log(y / m2_0) for y in m2_y ])
    X           = array([ log(y / m1_0) for y in m1_y ])

    model = LinearRegression()

    model.fit(X.reshape(-1, 1), Y)

    Y_ = model.predict(X.reshape(-1, 1))

    residuals   = Y - Y_
    beta        = model.coef_[0]
    alpha       = model.intercept_
    mu          = mean(residuals)
    sigma       = std(residuals)  

    '''
    print(f"beta:  {beta:0.4f}")
    print(f"alpha: {alpha:0.4f}")
    print(f"mu:    {mu:0.4f}")
    print(f"sigma: {sigma:0.4f}")
    '''

    x_cur = log(m1_entry / m1_0)
    y_cur = log(m2_entry / m2_0)

    x       = [ x_cur + i for i in arange(-0.01, 0.01, 0.001) ]
    y_fair  = [ x_ * beta + alpha for x_ in x ]
    ys      = {
                "+3s": [ y_ + mu + 3 * sigma for y_ in y_fair ],
                "+2s": [ y_ + mu + 2 * sigma for y_ in y_fair ],
                "+1s": [ y_ + mu + sigma for y_ in y_fair ],
                "  0": y_fair,
                "-1s": [ y_ + mu - sigma for y_ in y_fair ],
                "-2s": [ y_ + mu - 2 * sigma for y_ in y_fair ],
                "-3s": [ y_ + mu - 3 * sigma for y_ in y_fair ]
            }
    
    '''
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            {
                "x":    X,
                "y":    Y,
                "mode": "markers",
                "name": "trades"
            }
        )
    )
    '''

    print("m1_chg\t" + "\t".join([ f"{x_:0.3f}" for x_ in arange(-0.01, 0.01, 0.001) ]) + "\n")

    for series, y in ys.items():

        m1_price = [ m1_0 * e**x for x in x ]
        m2_price = [ m2_0 * e**y_ for y_ in y ]

        position_val = [ 
                        f"{(m1_price[i] - m1_entry) * m1_qty + (m2_price[i] - m2_entry) * m2_qty:0.{precision}f}"
                        for i in range(len(m1_price))
                    ]
        
        position_str = "\t".join(position_val)
        
        print(f"{series}:\t{position_str}")

        '''
        fig.add_trace(
            go.Scatter(
                {
                    "x":        x,
                    "y":        y,
                    "mode":     "markers",
                    "name":     series,
                    "marker":   { "color": "#FF0000" },
                    "text":     [ f"{series}<br>{position_val[i]}<br>{m1_price[i]:0.{precision}f}<br>{m2_price[i]:0.{precision}f}" for i in range(len(position_val)) ]
                }
            )
        )
        '''

    #fig.show()