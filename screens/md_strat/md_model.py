import  numpy                   as      np
import  plotly.graph_objects    as      go
from    statistics              import  mean, stdev
from    sys                     import  argv, path
from    time                    import  time
from    typing                  import  List

path.append(".")

from util.bar_tools             import  bar_rec
from util.contract_settings     import  get_settings
from util.opts                  import  get_indexed_opt_series
from util.pricing               import  call, call_vertical, fly, iron_fly, put, put_vertical, straddle
from util.rec_tools             import  get_precision


# python screens/md_strat/md_seq.py ZC fly FIN 2020-01-01:2024-01-01 2023-09-15T00:00:00,2023-09-22T11:20 -50:51 1 10


def price_matrix(idx: dict) -> np.ndarray:

    t1      = time()
    x       = list(idx.keys())
    x_dim   = len(x)
    y_dim   = max(
                [ 
                    max(exp_data["x"])
                    for exp_data in idx.values()
                ]
            ) + 1
    A       = np.full(shape = (x_dim, y_dim), fill_value = np.nan, dtype = np.float64)

    for i in range(len(x)):

        header = x[i]
        x_      = idx[header]["x"]
        y_      = idx[header]["y"]

        for j in range(len(x_)):

            A[i, x_[j]] = y_[j]

    print(f"price_matrix: {time() - t1:0.1f}")

    return A

def sigma_index(price_m: np.ndarray) -> np.ndarray:

    t2      = time()
    settles = price_m[:, 0]
    T       = price_m.T
    log_chg = np.where(np.isnan(T), np.nan, np.log(T / settles)).T
    sigmas  = np.nanstd(log_chg, axis = 0)

    print(f"sigma_index: {time() - t2:0.1f}")

    return sigmas


def model(
    symbol:             dict,
    strategy:           str,
    mode:               str,
    date_range:         List[str],
    expiry_ranges:      List[str],
    offset_range:       List[float],
    strike_increment:   float,
    params:             List[float]

):

    start_date  = date_range[0]
    end_date    = date_range[1]
    rngs        = [ 
                    ( expiry_ranges[i], expiry_ranges[i + 1] ) 
                    for i in range(len(expiry_ranges) - 1)
                ]
    offsets     = np.arange(offset_range[0], offset_range[1], strike_increment)
    expiry_data = []
    
    for rng in rngs:

        cur_dt  = rng[0]
        exp_dt  = rng[1]
        idx     = get_indexed_opt_series(symbol, cur_dt, exp_dt, start_date, end_date, True, True)
        price_m = price_matrix(idx)
        sigmas  = sigma_index(price_m)

        pass


if __name__ == "__main__":

    t0                  = time()
    symbol              = argv[1]
    strategy            = argv[2]
    mode                = argv[3]
    date_range          = argv[4].split(":")
    expiry_ranges       = argv[5].split(",")
    offset_range        = [ float(val) for val in argv[6].split(":") ]
    strike_increment    = float(argv[7])
    params              = [ float(val) for val in argv[8:] ]

    model(
        symbol,
        strategy,
        mode,
        date_range,
        expiry_ranges,
        offset_range,
        strike_increment,
        params
    )

    print(f"md_model: {time() - t0:0.1f}")

    pass