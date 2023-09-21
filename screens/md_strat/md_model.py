import  numpy                   as      np
from    pandas                  import  Timestamp, Timedelta, date_range as pd_date_range
from    sys                     import  argv, path
from    time                    import  time
from    typing                  import  List

path.append(".")

from util.contract_settings     import  get_settings
from util.opts                  import  get_indexed_opt_series
from util.v_pricing             import  call, call_vertical, fly, iron_fly, put, put_vertical, straddle
from util.rec_tools             import  get_precision


# python screens/md_strat/md_seq.py ZC fly FIN 2020-01-01:2024-01-01 2023-09-15T00:00:00,2023-09-22T11:20 -50:51 1 10


DT_FMT      = "%Y-%m-%dT%H:%M:%S"
FREQUENCY   = "1T"   # OHLC aggregation for your data... probably should be a parameter


def price_matrix(idx: dict) -> np.array:

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


def sigma_index(price_m: np.array) -> np.array:

    t2      = time()
    settles = price_m[:, 0]
    T       = price_m.T
    log_chg = np.where(np.isnan(T), np.nan, np.log(T / settles)).T
    sigmas  = np.nanstd(log_chg, axis = 0)

    print(f"sigma_index: {time() - t2:0.1f}")

    return sigmas


def value(
    prices:     np.array,
    strikes:    np.array, 
    sigmas:     np.array,
    mode:       str, 
    strategy:   str,
    params:     List[float]
):

    res = []

    if "FIN" in mode:

        # final settlement values are at the 0 index
        # sigmas are 0

        prices  = prices[:, 0].reshape(-1, 1)
        sigmas  = np.zeros((len(prices)))

    # call, call_vertical, fly, iron_fly, put, put_vertical, straddle

    if strategy == "call":

        res = call(prices, strikes, sigmas)

    elif strategy == "call_vertical":

        res = call_vertical(prices, strikes, params[0], sigmas)

    elif strategy == "fly":

        res = fly(prices, strikes, params[0], sigmas)
    
    elif strategy == "iron_fly":

        res = iron_fly(prices, strikes, params[0], sigmas)
    
    elif strategy == "put":

        res = put(prices, strikes, sigmas)

    elif strategy == "put_vertical":

        res = put_vertical(prices, strikes, params[0], sigmas)

    elif strategy == "straddle":

        res = straddle(prices, strikes, sigmas)

    return res


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

    start_date      = date_range[0]
    end_date        = date_range[1]
    exp_rngs        = [ 
                        ( expiry_ranges[i], expiry_ranges[i + 1] ) 
                        for i in range(len(expiry_ranges) - 1)
                    ]
    offsets         = np.arange(offset_range[0], offset_range[1], strike_increment)
    expiry_data     = [] # for multi-expiry strategies... not yet implemented
    res             = []
    
    for exp_rng in exp_rngs:

        cur_dt  = exp_rng[0]
        exp_dt  = exp_rng[1]
        idx     = get_indexed_opt_series(symbol, cur_dt, exp_dt, start_date, end_date, True, True)
        prices  = price_matrix(idx)
        sigmas  = sigma_index(prices)

        for offset in offsets:

            strikes = np.round(prices / strike_increment) * strike_increment + offset * strike_increment
            vals    = value(prices, strikes, sigmas, mode, strategy, params)
            avgs    = np.nanmean(vals, axis = 0)
            
            res.append(avgs)

            pass

    # transpose and flip model results such that:
    #
    #   - columns are indexed by strike offset
    #   - row are indexed by minute (or other resolution)
    #   - row 0 = max time to expiration

    res = (np.array(res).T)[::-1, :]
    
    # for multi-expiry strategyies (not yet implemented), 
    # the program will build the datetime index for the model result
    # using the first expiry range supplied

    start_dt    = Timestamp(exp_rngs[0][0])
    end_dt      = start_dt + Timedelta(minutes = res.shape[0] - 1)
    dt_idx      = np.array(
                    [ 
                        dt.strftime(DT_FMT)
                        for dt in pd_date_range(start = start_dt, end = end_dt, freq = FREQUENCY)
                    ]
                )

    # filter any rows with NaN

    nan_row = np.isnan(res).any(axis = 1)
    res     = res[~nan_row]
    #res     = np.around(res, decimals = precision)
    dt_idx  = dt_idx[~nan_row]

    return ( dt_idx, res )


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

    res = model(
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