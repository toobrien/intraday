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


FMT     = "%Y-%m-%dT%H:%M:%S.%f"
R_MIN   = -0.005
R_MAX   = 0.005
R_STEP  = 0.001
X_MIN   = -0.02
X_MAX   = 0.02
X_STEP  = 0.001


if __name__ == "__main__":

    contract_ids = argv[1].split(":")
    
    if "#" in contract_ids[0]:

        contract_ids = [ contract_ids[0].replace("###", MYY) for MYY in contract_ids[1:] ]
    
    multiplier, tick_size   = get_settings(contract_ids[0])
    precision               = get_precision(str(tick_size))
    legs                    = argv[2].split(",")
    m0_qty, m0_entry        = ( float(part) for part in legs[0].split(":") )
    mi_qty, mi_entry        = ( float(part) for part in legs[1].split(":") )
    start                   = argv[3] if len(argv) > 3 else None
    end                     = argv[4] if len(argv) > 4 else None
    
    recs = [ 
            get_tas(contract_id, multiplier, None, start, end)
            for contract_id in contract_ids
        ]
    
    contract_ids    = [ get_title(contract_id) for contract_id in contract_ids ]
    recs            = multi_tick_series(recs, contract_ids)

    m0_0        = recs[contract_ids[0]]["y"][0]
    m0_last     = recs[contract_ids[0]]["y"][-1]
    mi_y, m0_y  = itemgetter("y", "prev_m0")(recs[contract_ids[1]])
    mi_0        = mi_y[0]
    mi_last     = mi_y[-1]
    Y           = array([ log(y / mi_0) for y in mi_y ])
    X           = array([ log(y / m0_0) for y in m0_y ])

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

    x_cur = log(m0_entry / m0_0)
    y_cur = log(mi_entry / mi_0)
    x_rng = arange(X_MIN, X_MAX, X_STEP)

    x       = [ x_cur + i for i in x_rng ]
    y_fair  = [ x_ * beta + alpha for x_ in x ]
    r_rng   = arange(R_MAX, R_MIN, -R_STEP)
    ys      = {
                f"{r_:0.3f}": [ y_ + r_ for y_ in y_fair ]
                for r_ in r_rng
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

    print("m0_chg\t" + "\t".join([ f"{x_:0.3f}" for x_ in x_rng ]) + "\n")

    for series, y in ys.items():

        m0_price = [ m0_0 * e**x for x in x ]
        mi_price = [ mi_0 * e**y_ for y_ in y ]

        position_val = [ 
                        f"{(m0_price[i] - m0_entry) * m0_qty + (mi_price[i] - mi_entry) * mi_qty:0.{precision}f}"
                        for i in range(len(m0_price))
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
                    "text":     [ f"{series}<br>{position_val[i]}<br>{m0_price[i]:0.{precision}f}<br>{mi_price[i]:0.{precision}f}" for i in range(len(position_val)) ]
                }
            )
        )
        '''

    #fig.show()