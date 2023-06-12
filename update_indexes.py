from datetime       import datetime
from json           import dumps, loads
from os             import listdir, remove
from re             import search
from util.parsers   import bulk_parse_tas, parse_tas_header, tas_rec
from util.sc_dt     import ts_to_ds
from time           import time


CONFIG      = loads(open("./config.json", "r").read())
SC_ROOT     = CONFIG["sc_root"]
FMT         = "%Y-%m-%d"
IDX_ROOT    = CONFIG["idx_root"]
INDEX_FNS   = listdir(IDX_ROOT)
CALENDAR    = {
    1:  "F",
    2:  "G",
    3:  "H",
    4:  "J",
    5:  "K",
    6:  "M",
    7:  "N",
    8:  "Q",
    9:  "U",
    10: "V",
    11: "X",
    12: "Z"
}


def update_index(instrument_id: str):

    # check for existing index and update from latest day, or create new

    scid_fd     = None
    scid_fd     = open(f"{SC_ROOT}/Data/{instrument_id}.scid", "rb")
    index_fn    = f"{instrument_id}.json"
    index_path  = f"{IDX_ROOT}/{index_fn}"
    index       = None
    scid_offset = None
    index_fd    = None
    additive    = None

    if index_fn not in INDEX_FNS:

        # create new index

        index       = {}
        scid_offset = 0
        additive    = False

    else:

        # update existing index

        index       = loads(open(index_path, "r").read())
        scid_offset = index[sorted(list(index.keys()))[-1]]
        additive    = True

    # add to index
    
    _           = parse_tas_header(scid_fd)
    recs        = bulk_parse_tas(scid_fd, scid_offset)
    num_recs    = len(recs)

    if recs:

        index_fd = open(index_path, "w")
        prev_day = ts_to_ds(recs[0][tas_rec.timestamp], FMT)
    
        for i in range(num_recs):

            rec = recs[i]
            day = ts_to_ds(rec[tas_rec.timestamp], FMT)

            if day != prev_day:

                index[day]  = i if not additive else i + scid_offset
                prev_day    = day

        if index:
        
            index_fd.write(dumps(index, indent = 4))

        else:

            # < 1 index unit of data
            
            remove(index_path)

            print(f"no index for {instrument_id}")

    else:

        print(f"no records for {instrument_id}")

    return num_recs


if __name__ == "__main__":

    start = time()

    fns = [
        fn for fn in
        listdir(f"{SC_ROOT}/Data")
        if ".scid" in fn
    ]

    skipped     = 0
    today       = datetime.now()
    cur_month   = str(CALENDAR[today.month])
    cur_year    = str(today.year)[-2:]
    current_fns = []
    pattern     = "[FGHJKMNQUVXZ]\d{2}"

    # skip expired contracts
    
    for fn in fns:

        expiry = search(pattern, fn)[0]

        exp_month   = expiry[0]
        exp_year    = expiry[1:]

        if  exp_year > cur_year     or \
            exp_year == cur_year    and exp_month >= cur_month:

            current_fns.append(fn)
        
        else:

            skipped += 1

    fns     = current_fns
    num_fns = len(fns)

    for i in range(num_fns):

        fn = fns[i]

        t0 = time()

        parsed = update_index(fn[:-5])

        print(f"{fn:50s}\t{i + 1}/{num_fns}\t{parsed: 10d}\t{time() - t0:0.1f}s")

    print(f"{skipped} skipped")
    print(f"\n{time() - start:0.1f}s elapsed")