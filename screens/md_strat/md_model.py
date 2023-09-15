from statistics             import mean, stdev
from sys                    import argv, path
from time                   import time
from typing                 import List

path.append(".")

from util.bar_tools         import bar_rec
from util.contract_settings import get_settings
from util.opts              import get_indexed_opt_series
from util.pricing           import call, call_vertical, fly, iron_fly, put, put_vertical, straddle
from util.rec_tools         import get_precision


# python screens/md_strat/md_seq.py ZC fly FIN 2020-01-01:2024-01-01 2023-09-15T00:00:00,2023-09-22T11:20 -50:51 1 10


def model(
    symbol:             dict,
    strategy:           str,
    mode:               str,
    date_range:         List,
    expiry_ranges:      List,
    offset_range:       List,
    strike_increment:   float,
    params:             List

):

    start_date  = date_range[0]
    end_date    = date_range[1]
    rngs        = [ 
                    ( expiry_ranges[i], expiry_ranges[i + 1] ) 
                    for i in range(len(expiry_ranges) - 1)
                ]
    
    for rng in rngs:

        cur_dt  = rng[0]
        exp_dt  = rng[1]
        idx     = get_indexed_opt_series(symbol, cur_dt, exp_dt, start_date, end_date, True, True)

        pass


if __name__ == "__main__":

    t0                  = time()
    symbol              = argv[1]
    strategy            = argv[2]
    mode                = argv[3]
    date_range          = argv[4].split(":")
    expiry_ranges       = argv[5].split(",")
    offset_range        = argv[6].split(":")
    strike_increment    = float(argv[7])
    params              = argv[8:]

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