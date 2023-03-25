from json       import dumps, loads
from os         import listdir
from parsers    import bulk_parse_tas, parse_tas_header, tas_rec
from sc_dt      import ts_to_ds


CONFIG      = loads(open("./config.json", "r").read())
SC_ROOT     = CONFIG["sc_root"]
IDX_ROOT    = CONFIG["idx_root"]
INDEXES     = {}
INDEX_FNS   = listdir(IDX_ROOT)
FMT         = "%Y-%m-%d"


def get_index(instrument_id: str, day: str = None):

    res = None

    if instrument_id not in INDEXES:
        
        try:
        
            INDEXES[instrument_id] = loads(open(f"{IDX_ROOT}/{instrument_id}.json").read())

            res = INDEXES[instrument_id][day] if day else INDEXES[instrument_id]
        
        except Exception as e:

            print(e)

    return res


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
        
        print(f"created\t{index_fn}")

    else:

        # update existing index

        scid_offset = index[sorted(list(index.keys()))[-1]]
        additive    = True

    # add to index
    
    index_fd    = open(index_path, "w")
    _           = parse_tas_header(scid_fd)
    recs        = bulk_parse_tas(scid_fd, scid_offset)

    prev_day = ts_to_ds(recs[0][tas_rec.timestamp], FMT)

    for i in range(len(recs)):

        rec = recs[i]
        day = ts_to_ds(rec[tas_rec.timestamp], FMT)

        if day != prev_day:

            index[day]  = i if not additive else i + scid_offset
            prev_day    = day

    index_fd.write(dumps(index))

    print(f"updated\t{index_fn}")


if __name__ == "__main__":

    fns = [
        fn for fn in
        listdir(f"{SC_ROOT}/Data")
        if ".scid" in fn
    ]

    num_fns = len(fns)

    for i in range(num_fns):

        fn = fns[i]

        print(f"{fn:50s}\t{i + 1}/{num_fns}")

        update_index(fn[:-5])