from    sys                     import  argv
from    util.parsers            import  tas_rec
from    util.tas_tools          import  get_tas
from    util.sc_dt              import  ts_to_ds

if __name__ == "__main__":

    contract_id = argv[1]
    multiplier  = float(argv[2])
    start       = argv[3]
    end         = argv[4]

    recs = get_tas(contract_id, multiplier, None, start, end)

    for rec in recs[:10]:

        ts = rec[tas_rec.timestamp]
        ds = ts_to_ds(ts, "%Y-%m-%dT%H:%M:%S.%f")
        
        print(ds)