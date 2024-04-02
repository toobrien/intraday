import  plotly.graph_objects    as      go
from    sys                     import  argv, path
from    time                    import  time

path.append(".")

from    util.contract_settings  import  get_settings
from    util.plotting           import  get_title
from    util.rec_tools          import  get_tas, get_precision, tas_rec
from    util.sc_dt              import  ts_to_ds


# python charts/sweep.py ESM24_FUT_CME 5 2024-03-27 2024-03-28


FMT = "%Y-%m-%dT%H:%M:%S.%f"


if __name__ == "__main__":

    t0                      = time()
    contract_id             = argv[1]
    min_len                 = int(argv[2])
    multiplier, tick_size   = get_settings(contract_id)
    precision               = get_precision(str(tick_size))
    title                   = get_title(contract_id)
    start                   = argv[3] if len(argv) > 3 else None
    end                     = argv[4] if len(argv) > 4 else None
    recs                    = get_tas(contract_id, multiplier, None, start, end)
    title                   = f"{title} {start} - {end}"
    groups                  = {}

    for rec in recs:

        ts = str(rec[tas_rec.timestamp])[:-3]

        if ts not in groups:

            groups[ts] = []

        groups[ts].append(rec)

    for ts, group in groups.items():

        prices      = [ rec[tas_rec.price] for rec in group ]
        qty         = sum([ rec[tas_rec.qty] for rec in group ])
        min_price   = min(prices)
        max_price   = max(prices)
        ticks       = (max_price - min_price) / tick_size
    
        if ticks >= min_len:

            ts = ts_to_ds(group[0][tas_rec.timestamp], FMT)

            print(ts, f"{min_price:10}", f"{max_price:10}", f"{int(ticks):10}", f"{qty:10}")

    print(f"{time() - t0:0.1f}s")

    pass