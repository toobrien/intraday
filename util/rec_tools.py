from datetime       import  datetime, timedelta
from json           import  loads
from util.parsers   import  bulk_parse_tas, depth_rec, parse_depth, parse_depth_header, \
                            parse_tas_header, tas_rec, transform_depth, transform_tas
from bisect         import  bisect_left, bisect_right
from enum           import  IntEnum
from typing         import  List
from util.sc_dt     import  ds_to_ts, ts_to_ds


CONFIG      = loads(open("./config.json", "r").read())
SC_ROOT     = CONFIG["sc_root"]
IDX_ROOT    = CONFIG["idx_root"]
INDEXES     = {}
MONTHS      = [ "F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]


def get_index(instrument_id: str, day: str = None):

    res = None

    if instrument_id not in INDEXES:
        
        try:
        
            INDEXES[instrument_id] = loads(open(f"{IDX_ROOT}/{instrument_id}.json").read())

            res = INDEXES[instrument_id][day] if day else INDEXES[instrument_id]
        
        except (FileNotFoundError, KeyError) as e:

            # print(instrument_id, repr(e))

            pass

    return res


# returns a dict of dates to slice indices (for trades that occurred that day)
#
# - use after calling get_tas to get "recs", this function 
#   will map each day to the index of its first record
# - rec timestamps should be "YYYY-MM-DDTHH:MM:SS..."
# - must run update_indexes.py before using

def date_index(instrument_id: str, recs: List) -> dict:

    start   = recs[0][tas_rec.timestamp].split("T")[0]
    end     = recs[-1][tas_rec.timestamp].split("T")[0]

    # instrument should be in INDEXES since you already called get_recs

    indexes     = []
    idx         = INDEXES[instrument_id]
    keys        = list(idx.keys())
    keys        = keys[keys.index(start) : keys.index(end) + 1]
    start_i     = idx[start]
    res         = {}

    for key in keys:

        indexes.append(idx[key] - start_i)

    for i in range(len(keys) - 1):

        res[keys[i]] = ( indexes[i], indexes[i + 1] )
    
    res[keys[-1]] = ( indexes[-1], len(recs) )
 
    return res
    

# valid formats for "start" date:
# 
# %Y-%m-%d %H:%M:%S.%f
# %Y-%m-%dT%H:%M:%S.%f
# %Y-%m-%d
#
# any format is valid for timestamp

def get_tas(
    contract_id:    str, 
    multiplier:     float,
    ts_fmt:         str = None,
    start:          str = None, 
    end:            str = None
):

    idx         = None
    to_seek     = None
    recs        = None
    to_seek     = 0

    if start:

        if " " in start:

            start.replace(" ", "T")
        
        if "T" in start:

            idx = start.split("T")[0]

        else:

            idx = start

        to_seek = get_index(contract_id, idx)

        if not to_seek:

            # either:
            #
            #   - "start" date not indexed, or bad format
            #   - timestamp given rather than index
            #
            # result:
            #
            #   - entire file will be loaded
            #   - "start" will be used with slice records later

            to_seek = 0

        if not ts_fmt:

            start = ds_to_ts(start)

    if end:

        if " " in end:

            end.replace(" ", "T")

        if not ts_fmt:

            end = ds_to_ts(end)

    try:

        with open(f"{SC_ROOT}/Data/{contract_id}.scid", "rb") as fd:

            _       = parse_tas_header(fd)
            recs    = bulk_parse_tas(fd, to_seek)
            recs    = transform_tas(recs, multiplier, ts_fmt)

            i = 0
            j = len(recs)

            if start:

                i = bisect_left(recs, start, key = lambda r: r[tas_rec.timestamp]) 

            if end:

                j = bisect_right(recs, end, key = lambda r: r[tas_rec.timestamp])

            recs = recs[i:j]
        
    except FileNotFoundError:

        pass
        
    return recs


# interleaves tas and depth records for a given day
# start/end formats must include a date:
#
#   %Y-%m-%dT%H:%M:%S.%f
#   %Y-%m-%d
#
#   note: ts_fmt must have "T"

def intraday_tas_and_depth(
    contract_id:    str, 
    multiplier:     float,
    ts_fmt:         str     = "%Y-%m-%dT%H:%M:%S.%f",
    start:          str     = None,
    end:            str     = None
):
    
    date = start if "T" not in start else start.split("T")[0]

    with open(f"{SC_ROOT}/Data/MarketDepthData/{contract_id}.{date}.depth", "rb") as fd:

        _           = parse_depth_header(fd)
        depth_recs  = parse_depth(fd, 0)
        depth_recs  = transform_depth(depth_recs, multiplier, ts_fmt)

    start_date_depth    = depth_recs[0][depth_rec.timestamp].split("T")[0]
    tas_recs            = get_tas(contract_id, multiplier, ts_fmt, start_date_depth, end)

    tas_recs.extend(depth_recs)

    combined_recs = sorted(tas_recs, key = lambda r: r[tas_rec.timestamp])

    return combined_recs


def get_term_ids(init_symbol: str, n_months: int):

    symbol      = init_symbol[:-3]
    first_month = init_symbol[-3]
    year        = int(init_symbol[-2:])
    
    results = []
    
    i = MONTHS.index(first_month)

    while n_months > 0:

        results.append(f"{symbol}{MONTHS[i]}{year}")

        year        =  year if i != 11 else year + 1
        i           =  (i + 1) % 12
        n_months    -= 1
    
    return results


def get_terms(
    init_symbol:    str,
    multiplier:     float,
    n_months:       int,
    fmt:            str = None,
    start:          str = None,
    end:            str = None
):

    term_ids    = get_term_ids(init_symbol, n_months)
    results     = {}

    for term_id in term_ids:

        try:

            recs = get_tas(f"{term_id}_FUT_CME", multiplier, fmt, start, end)

            if recs:

                results[term_id] = recs

        except Exception as e:

            # print exception and keep going on file not found
            # (for non-serial contracts)

            print(e)
    
    return results


class ohlcv_rec(IntEnum):

    ts = 0
    o  = 1
    h  = 2
    l  = 3
    c  = 4
    v  = 5


def get_ohlcv(
    recs: List, 
    resolution: str,
    start:      str,
    end:        str,
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

    step_us = int(step_us)
    i       = 0
    start   = ds_to_ts(start)
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

                ohlcv.append(( ts, o, h, l, c, v ))

            start   =  end
            end     += step_us

    if trim_empty:

        ohlcv = [
            rec 
            for rec in ohlcv
            if rec[ohlcv_rec.v] != 0
        ]

    return ohlcv


# for formatting printed prices

def get_precision(multiplier: str):

    return len(multiplier.split(".")[1]) if "." in multiplier else len(multiplier)


# for getting date ranges

def n_days_ago(n: int):

    return (datetime.today() - timedelta(days = n)).strftime("%Y-%m-%d")