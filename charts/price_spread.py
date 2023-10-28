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
    front_leg               = ( float(part) for part in legs[0].split(":") )
    back_leg                = ( float(part) for part in legs[1].split(":") )
    start                   = argv[3] if len(argv) > 3 else None
    end                     = argv[4] if len(argv) > 4 else None
    
    recs = [ 
            get_tas(contract_id, multiplier, None, start, end)
            for contract_id in contract_ids
        ]
    
    contract_ids    = [ get_title(contract_id) for contract_id in contract_ids ]
    recs            = multi_tick_series(recs, contract_ids)

    m1_0        = recs[contract_ids[0]]["y"][0]
    m2_y, logs  = itemgetter("y", "log")(recs[contract_ids[1]])
    m1_y        = [ m2_y[i] / e**logs[i] for i in range(len(logs)) ]
    Y           = array([ log(y / m2_y[0]) for y in m2_y ])
    X           = array([ log(y / m1_0) for y in m1_y ])

    model = LinearRegression()

    model.fit(X.reshape(-1, 1), Y)

    Y_ = model.predict(X.reshape(-1, 1))

    residuals   = Y - Y_
    mu          = mean(residuals)
    sigma       = std(residuals)  

    print(f"beta:  {model.coef_[0]:0.4f}")
    print(f"alpha: {model.intercept_:0.4f}")
    print(f"mu:    {mu:0.4f}")
    print(f"sigma: {sigma:0.4f}")

    fig = go.Figure()

    fig.add_trace(
        go.Histogram(
            {
                "x":        residuals,
                "opacity":  0.5
            }
        )
    )

    fig.show()