import  numpy                   as      np
from    pandas                  import  Timestamp, Timedelta, date_range as pd_date_range
from    sys                     import  argv, path
from    time                    import  time
from    typing                  import  List

path.append(".")

from util.contract_settings     import  get_settings
from util.opts                  import  get_indexed_opt_series, get_exp_time
from util.v_pricing             import  calendar, call, call_vertical, fly, iron_fly, put, put_vertical, straddle
from util.rec_tools             import  get_precision


# python screens/md_strat/md_model.py ZC fly CUR 2020-01-01 2024-01-01 now,2023-09-22 -50:51 1 10


DT_FMT          = "%Y-%m-%dT%H:%M:%S"
OHLC_RESOLUTION = "1T"   # OHLC aggregation for your data... probably should be a parameter


def price_matrix(idx: dict) -> np.array:

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

    return A


def sigma_index(price_m: np.array) -> np.array:

    settles = price_m[:, 0]
    T       = price_m.T
    log_chg = np.where(np.isnan(T), np.nan, np.log(T / settles)).T
    sigmas  = np.nanstd(log_chg, axis = 0)

    return sigmas


def value(
    price_arrs:     List[np.array],
    strike_arrs:    List[np.array], 
    sigma_arrs:     List[np.array],
    mode:           str, 
    strategy:       str,
    params:         List[float]
):

    res = []

    if "FIN" in mode:

        # final settlement values are at the 0 index
        # sigmas are 0
        # TODO: need refactor for multi-expiry strategies

        price_arrs  = [ prices[:, 0].reshape(-1, 1) for prices in price_arrs ]
        sigma_arrs  = [ np.zeros((len(price_arr))) for price_arr in price_arrs ]

    # call, call_vertical, fly, iron_fly, put, put_vertical, straddle

    if strategy == "calendar":

        res = calendar(price_arrs, strike_arrs, sigma_arrs)

    elif strategy == "call":

        res = call(price_arrs[0], strike_arrs[0], sigma_arrs[0])

    elif strategy == "call_vertical":

        res = call_vertical(price_arrs[0], strike_arrs[0], params[0], sigma_arrs[0])

    elif strategy == "fly":

        res = fly(price_arrs[0], strike_arrs[0], params[0], sigma_arrs[0])
    
    elif strategy == "iron_fly":

        res = iron_fly(price_arrs[0], strike_arrs[0], params[0], sigma_arrs[0])
    
    elif strategy == "put":

        res = put(price_arrs[0], strike_arrs[0], sigma_arrs[0])

    elif strategy == "put_vertical":

        res = put_vertical(price_arrs[0], strike_arrs[0], params[0], sigma_arrs[0])

    elif strategy == "straddle":

        res = straddle(price_arrs[0], strike_arrs[0], sigma_arrs[0])

    return res


def model(
    symbol:             str,
    strategy:           str,
    mode:               str,
    hist_start:         str,
    hist_end:           str,
    time_idx:           List[str],
    offset_range:       List[float],
    strike_increment:   float,
    params:             List[float],
    precision:          int
):

    cur_dt      = time_idx[0] if time_idx[0] != "now" else Timestamp.now().floor(OHLC_RESOLUTION).strftime(DT_FMT)
    exp_time    = get_exp_time(symbol)
    offsets     = np.arange(offset_range[0], offset_range[1], strike_increment)
    price_arrs  = []
    sigma_arrs  = []
    res         = []
    
    for exp in time_idx[1:]:

        exp_dt  = f"{exp}T{exp_time}" if "T" not in exp else exp
        idx     = get_indexed_opt_series(symbol, cur_dt, exp_dt, hist_start, hist_end, True, True)
        prices  = price_matrix(idx)
        sigmas  = sigma_index(prices)

        price_arrs.append(prices)
        sigma_arrs.append(sigmas)

    for offset in offsets:

        strike_arrs = []
        
        for prices in price_arrs:

            strikes = np.round(prices / strike_increment) * strike_increment + offset * strike_increment
            
            strike_arrs.append(strikes)

        vals    = value(price_arrs, strike_arrs, sigma_arrs, mode, strategy, params)
        avgs    = np.nanmean(vals, axis = 0)
        
        res.append(avgs)

        # exp_vals.append(avgs)

    # transpose and flip model results such that:
    #
    #   - columns are indexed by strike offset
    #   - row are indexed by minute (or other resolution)
    #   - row 0 = max time to expiration

    res = (np.array(res).T)[::-1, :]
    
    # for multi-expiry strategyies (not yet implemented), 
    # the program will build the datetime index for the model result
    # using the first expiry range supplied

    end_dt      = Timestamp(cur_dt) + Timedelta(minutes = res.shape[0] - 1)
    dt_idx      = np.array(
                    [ 
                        dt.strftime(DT_FMT)
                        for dt in pd_date_range(start = cur_dt, end = end_dt, freq = OHLC_RESOLUTION)
                    ]
                )

    # filter any rows with NaN and round to tick precision

    nan_row = np.isnan(res).any(axis = 1)
    res     = res[~nan_row]
    res     = np.around(res, decimals = precision)
    dt_idx  = dt_idx[~nan_row]

    return ( dt_idx, res )


if __name__ == "__main__":

    t0                  = time()
    symbol              = argv[1]
    strategy            = argv[2]
    mode                = argv[3]
    hist_start          = argv[4]
    hist_end            = argv[5]
    time_idx            = argv[6].split(",")
    offset_range        = [ float(val) for val in argv[7].split(":") ]
    strike_increment    = float(argv[8])
    params              = [ float(val) for val in argv[9:] ]
    precision           = get_precision(str(get_settings(symbol)[1]))

    dt_idx, vals = model(
        symbol,
        strategy,
        mode,
        hist_start,
        hist_end,
        time_idx,
        offset_range,
        strike_increment,
        params,
        precision
    )

    # debug

    for i in range(len(dt_idx)):

        print(f"{dt_idx[i]}:{''.join([ f'{val:8.2f}' for val in np.around(vals[i], 2) ])}")

    print(f"md_model: {time() - t0:0.1f}")

    pass