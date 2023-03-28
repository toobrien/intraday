from json               import loads
from util.index_scid    import get_index
from util.parsers       import bulk_parse_tas, parse_tas_header, tas_rec, transform_tas
from bisect             import bisect_left, bisect_right

SC_ROOT = loads(open("./config.json", "r").read())["sc_root"]


# valid formats for "start" date:
# 
# %Y-%m-%d %H:%M:%S.%f
# %Y-%m-%dT%H:%M:%S.%f
# %Y-%m-%d
#
# any format is valid for timestamp

def get_tas(
    contract_id:    str, 
    ts_fmt:         str,
    multiplier:     float,
    start:          str = None, 
    end:            str = None
):

    idx         = None
    to_seek     = None
    recs        = None
    valid       = True

    if start:

        if " " in start:

            idx = start.split(" ")[0]
        
        elif "T" in start:

            idx = start.split("T")[0]

        else:

            idx = start

        to_seek = get_index(contract_id, idx)

        if not to_seek:

            valid = False

            print("start date not available")

    else:

        to_seek = 0

    if valid:

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
        
    return recs
    