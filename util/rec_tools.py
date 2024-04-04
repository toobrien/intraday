from datetime       import  datetime, timedelta
from json           import  loads
from bisect         import  bisect_left, bisect_right
from sys            import  path
from typing         import  List

path.append(".")

from config         import  CONFIG
from util.parsers   import  bulk_parse_tas, depth_rec, parse_depth, parse_depth_header, \
                            parse_tas_header, tas_rec, raw_tas_slice, transform_depth, transform_tas
from util.sc_dt     import  ds_to_ts


SC_ROOT     = CONFIG["sc_root"]
IDX_ROOT    = CONFIG["idx_root"]
INDEXES     = {}


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


# returns a slice of time and sales records without loading the entire file
#
# - start_rec and end_rec should be record, not byte, indices

def quick_tas(
    contract_id:    str,
    start_rec:      int = 0,
    end_rec:        int = None
):

    with open(f"{SC_ROOT}/Data/{contract_id}.scid", "rb") as fd:

        tas_recs = raw_tas_slice(fd, start_rec, end_rec)

    return tas_recs


# returns a dict of dates to slice indices (for trades or quotes that occurred that day)
#
# - use after calling get_tas to get "recs", this function 
#   will map each day to the index of its first record
# - rec timestamps should be "YYYY-MM-DDTHH:MM:SS..."
# - must run update_indexes.py before using

def date_index(instrument_id: str, recs: List) -> dict:

    start   = recs[0][tas_rec.timestamp].split("T")[0]
    end     = recs[-1][tas_rec.timestamp].split("T")[0]

    # instrument should be in INDEXES since you already called get_tas

    indexes     = []
    idx         = INDEXES[instrument_id]
    keys        = list(idx.keys())
    start       = max(start, keys[0])
    end         = min(end, keys[-1])
    keys        = keys[keys.index(start) : keys.index(end) + 1]
    start_i     = idx[start]
    res         = {}

    for key in keys:

        indexes.append(idx[key] - start_i)

    for i in range(len(keys) - 1):

        res[keys[i]] = ( indexes[i], indexes[i + 1] )
    
    res[keys[-1]] = ( indexes[-1], len(recs) )
 
    return res


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


# for formatting printed prices

def get_precision(multiplier: str):

    return len(multiplier.split(".")[1]) if "." in multiplier else len(multiplier)


# for getting date ranges

def n_days_ago(n: int):

    return (datetime.today() - timedelta(days = n)).strftime("%Y-%m-%d")