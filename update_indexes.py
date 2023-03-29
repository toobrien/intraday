from json           import dumps, loads
from os             import listdir, remove
from util.parsers   import bulk_parse_tas, parse_tas_header, tas_rec
from util.sc_dt     import ts_to_ds
from time           import time


CONFIG      = loads(open("./config.json", "r").read())
SC_ROOT     = CONFIG["sc_root"]
FMT         = "%Y-%m-%d"
IDX_ROOT    = CONFIG["idx_root"]
INDEX_FNS   = listdir(IDX_ROOT)


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

    num_fns = len(fns)

    for i in range(num_fns):

        fn = fns[i]

        t0 = time()

        parsed = update_index(fn[:-5])

        print(f"{fn:50s}\t{i + 1}/{num_fns}\t{parsed: 10d}\t{time() - t0:0.1f}s")

    print(f"\n{time() - start:0.1f}s elapsed")