from bisect         import bisect_left
from enum           import IntEnum
from math           import log
from typing         import List
from util.parsers   import tas_rec
from util.rec_tools import date_index
from util.sc_dt     import ts_to_ds


# for combined bids/asks:
#
#   x: tick count (trade #)
#   y: price
#   z: qty
#   t: timestamp (start, end)
#   c: color

def tick_series(recs: List):

    x           = []
    y           = []
    z           = []
    t           = []
    c           = []
    start       = recs[0][tas_rec.timestamp]
    end         = start
    prev_price  = recs[0][tas_rec.price]
    prev_side   = recs[0][tas_rec.side]
    trade_qty   = recs[0][tas_rec.qty]
    cum_qty     = trade_qty

    for i in range(1, len(recs)):

        rec     = recs[i]
        ts      = rec[tas_rec.timestamp]
        price   = rec[tas_rec.price]
        qty     = rec[tas_rec.qty]
        side    = rec[tas_rec.side]

        if price != prev_price or side != prev_side:

            x.append(cum_qty)
            y.append(prev_price)
            z.append(trade_qty)
            t.append(( start, end ))
            c.append("#0000FF" if prev_side else "#FF0000")

            start       = ts
            end         = ts
            prev_price  = price
            prev_side   = side
            trade_qty   = qty
        
        else:

            end         =  ts
            trade_qty   += qty
        
        cum_qty += qty

        # add final trade

        '''
        x.append(cum_qty)
        y.append(prev_price)
        z.append(trade_qty)
        t.append(( start, end ))
        c.append("#0000FF" if prev_side else "#FF0000")
        '''

    # add final trade

    x.append(cum_qty)
    y.append(prev_price)
    z.append(trade_qty)
    t.append(( start, end ))
    c.append("#0000FF" if prev_side else "#FF0000")  

    return ( x, y, z, t, c )


def multi_tick_series(recs: List[List], contract_ids: List):

    recs = [
        [ list(rec) for rec in recs[i] ]
        for i in range(len(recs))
    ]

    for i in range(len(recs)):

        series      = recs[i]
        contract_id = contract_ids[i]

        for j in range(len(series)):

            series[j].append(contract_id)

    recs = [
        rec
        for series in recs
        for rec in series
    ]

    init_m0 = recs[0][tas_rec.price]
    prev_m0 = init_m0

    recs = sorted(recs, key = lambda r: r[tas_rec.timestamp])

    agg_recs = []
    tick     = recs[0][tas_rec.qty]
    prev_rec = [ val for val in recs[0] ]

    prev_rec.append(tick)

    for next_rec in recs[1:]:

        if  next_rec[tas_rec.price] == prev_rec[tas_rec.price]  and \
            next_rec[tas_rec.side]  == prev_rec[tas_rec.side]   and \
            next_rec[-1]            == prev_rec[-2]:            # contract_id

            prev_rec[tas_rec.qty]   += next_rec[tas_rec.qty]
        
        else:

            agg_recs.append(prev_rec)

            prev_rec = [ val for val in next_rec ]
            
            prev_rec.append(tick)
            
        tick            += next_rec[tas_rec.qty]
        prev_rec[-1]    =  tick

    agg_recs.append(prev_rec)

    for rec in agg_recs:

        rec.append(prev_m0)

    recs = [
        [ 
            rec
            for rec in agg_recs
            if contract_id in rec
        ]
        for contract_id in contract_ids
    ]

    recs = {
        contract_ids[i]: {
            "x":        [ rec[-2] for rec in recs[i] ],
            "y":        [ rec[tas_rec.price] for rec in recs[i] ],
            "t":        [ rec[tas_rec.timestamp] for rec in recs[i] ],
            "z":        [ rec[tas_rec.qty] for rec in recs[i] ],
            "c":        [ "#0000FF" if rec[tas_rec.side] else "#FF0000" for rec in recs[i] ],
            "prev_m0":  [ rec[-1] for rec in recs[i] ]
        }
        for i in range(len(contract_ids))
    }

    return recs


# aggregates trades by rounding to the given increment

def agg_tick_series(recs: List, increment: float):

    x = []  # contract number
    y = []  # price
    a = []  # volume traded at ask
    b = []  # volume traded at bid
    v = []  # total volume
    t = []  # timestamp (start, end)
    
    prev_price  = increment * round(recs[0][tas_rec.price] / increment)
    contract    = recs[0][tas_rec.qty]
    bid_vol     = recs[0][tas_rec.qty] if not recs[0][tas_rec.side] else 0
    ask_vol     = recs[0][tas_rec.qty] if recs[0][tas_rec.side] else 0
    total_vol   = bid_vol + ask_vol
    start       = recs[0][tas_rec.timestamp]

    for rec in recs:

        price   = increment * round(rec[tas_rec.price] / increment)
        ts      = rec[tas_rec.timestamp]
        qty     = rec[tas_rec.qty]
        side    = rec[tas_rec.side]

        if price != prev_price:

            x.append(contract)
            y.append(price)
            a.append(ask_vol)
            b.append(bid_vol)
            v.append(total_vol)
            t.append(( start, ts ))

            bid_vol     = 0
            ask_vol     = 0
            total_vol   = 0
            start       = ts
            prev_price  = price
            
        contract    += qty
        bid_vol     += qty if not side else 0
        ask_vol     += qty if side else 0
        total_vol   += qty
    
    # add final trade

    x.append(contract)
    y.append(price)
    a.append(ask_vol)
    b.append(bid_vol)
    v.append(total_vol)
    t.append(( start, ts ))

    return ( x, y, a, b, v, t )


def fixed_series(recs: List, increment: float):

    x = []  # bar number
    y = []  # price
    a = []  # volume traded at ask
    b = []  # volume traded at bid
    v = []  # total volume
    t = []  # timestamp (start, end)

    prev_price  = increment * round(recs[0][tas_rec.price] / increment)
    hi_lim      = prev_price + increment
    lo_lim      = prev_price - increment
    bar         = 0
    ask_vol     = recs[0][tas_rec.qty] if recs[0][tas_rec.side] else 0
    bid_vol     = recs[0][tas_rec.qty] if not recs[0][tas_rec.side] else 0
    total_vol   = bid_vol + ask_vol
    start       = recs[0][tas_rec.timestamp]

    for rec in recs:

        price   = rec[tas_rec.price]
        ts      = rec[tas_rec.timestamp]
        qty     = rec[tas_rec.qty]
        side    = rec[tas_rec.side]

        if price > hi_lim or price < lo_lim:

            x.append(bar)
            y.append(prev_price)
            a.append(ask_vol)
            b.append(bid_vol)
            v.append(total_vol)
            t.append(( start, ts ))

            bar         += 1
            bid_vol     =  0
            ask_vol     =  0
            total_vol   =  0
            start       =  ts
            prev_price  =  hi_lim if price > hi_lim else lo_lim
            hi_lim      =  prev_price + increment
            lo_lim      =  prev_price - increment

        bid_vol     += qty if not side else 0
        ask_vol     += qty if side else 0
        total_vol   += qty

    return ( x, y, a, b, v, t )


# for bids/asks separately: x = timestamp, y = price, z = qty

def split_tick_series(recs: List):

    x           = []
    y           = []
    z           = []
    prev_price  = recs[0][tas_rec.price]
    cum_qty     = recs[0][tas_rec.qty]

    for rec in recs:

        ts      = rec[tas_rec.timestamp]
        price   = rec[tas_rec.price]
        qty     = rec[tas_rec.qty]

        if price == prev_price:

            cum_qty += qty
        
        else:

            x.append(ts)
            y.append(price)
            z.append(cum_qty)

            prev_price  = price
            cum_qty     = qty
        
    # add final trade

    x.append(ts)
    y.append(price)
    z.append(cum_qty)

    return ( x, y, z )


# groups trade records into ranges delimited by "start" and "end" timestamps,
# timestamps are %H:%M:%S.%f
# (minutes, seconds, microseconds optional)

def intraday_ranges(
        instrument_id:  str,
        recs:           List,
        start:          str, 
        end:            str
    ) -> dict:

    idx         = date_index(instrument_id, recs)
    res         = {}

    for date, rng in idx.items():

        start_ds    = f"{date}T{start}"
        end_ds      = f"{date}T{end}"
        selected    = recs[rng[0] : rng[1]]

        intraday_range_start    = rng[0] + bisect_left(selected, start_ds, key = lambda r: r[tas_rec.timestamp])
        intraday_range_end      = rng[0] + bisect_left(selected, end_ds, key = lambda r: r[tas_rec.timestamp])

        res[date] = ( intraday_range_start, intraday_range_end )

    return res


def vbp(recs: List, precision: float = None):

    hist = []

    for rec in recs:

        hist += ([ rec[tas_rec.price] ] * rec[tas_rec.qty])

    if precision:

        hist = [ round(val, precision) for val in hist ]
    
    return sorted(hist)


class ohlcv_rec(IntEnum):

    ts = 0
    o  = 1
    h  = 2
    l  = 3
    c  = 4
    v  = 5
    i  = 6
    j  = 7


def ohlcv(
    recs:       List, 
    resolution: str,
    out_fmt:    str     = None, # None  = use microsecond timestamp
    trim_empty: bool    = False # False = carry forward close for bars with no trades, True = delete bars with no trades
):

    parts       = resolution.split(":")
    step_us     = int(parts[0])
    unit        = parts[1]
    
    if unit == "U":

        step_us *= 1

    elif unit == "MS":

        step_us *= 1e3

    elif unit == "S":

        step_us *= 1e6

    elif unit == "M":

        step_us *= 6e7

    elif unit == "H":

        step_us *= 3.6e9

    elif unit == "D":

        step_us *= 8.64e10
    
    elif unit == "W":

        step_us *=  6.048e11

    step_us = int(step_us)
    i       = 0
    start   = recs[0][tas_rec.timestamp]
    end     = start + step_us
    ohlcv   = []

    while(True):

        o = None
        h = float("-inf")
        l = float("inf")
        c = None
        v = 0

        while(i < len(recs) and recs[i][tas_rec.timestamp] < end):

            price = recs[i][tas_rec.price]

            if not o:

                o = price

            h =  max(h, price)
            l =  min(l, price)
            v += recs[i][tas_rec.qty]

            i += 1

        if i >= len(recs): 
            
            break

        else:

            if i > 0:

                o   = o if o else ohlcv[-1][1]
                h   = h if h != float("-inf") else o
                l   = l if l != float("inf")  else o
                c   = recs[i - 1][tas_rec.price]
                ts  = start if not out_fmt else ts_to_ds(start, out_fmt)

                ohlcv.append(
                    ( 
                        ts,
                        o,
                        h,
                        l,
                        c,
                        v,
                        ohlcv[-1][ohlcv_rec.j] if len(ohlcv) > 0 else 0,
                        i 
                    )
                )

            start   =  end
            end     += step_us

    if trim_empty:

        ohlcv = [
            rec 
            for rec in ohlcv
            if rec[ohlcv_rec.v] != 0
        ]

    return ohlcv
