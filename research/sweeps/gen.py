from csv                    import reader, writer
from os.path                import exists
from sys                    import argv, path
from time                   import time

path.append(".")

from util.contract_settings import get_settings
from util.rec_tools         import quick_tas, get_precision, tas_rec
from util.sc_dt             import ts_to_ds


# 0 ts            unabridged %Y-%m-%dT%H:%M:%S.%f
# 1 idx i         first record (offset from start of file)
# 2 idx j         last record
# 3 ticks         
# 4 min price
# 5 max price
# 6 qty
# 7 side

COLS = [
    "timestamp",
    "start_rec",
    "end_rec",
    "ticks",
    "min_price",
    "max_price",
    "qty",
    "side"
]

# python research/sweeps/gen.py ESM24_FUT_CME 5


FMT = "%Y-%m-%dT%H:%M:%S.%f"

if __name__ == "__main__":

    t0 = time()

    contract_id             = argv[1]
    min_len                 = int(argv[2])
    multiplier, tick_size   = get_settings(contract_id)
    precision               = get_precision(str(tick_size))
    fn                      = f"./research/sweeps/store/{contract_id}.csv"
    rows                    = []
    mode                    = "w"
    i                       = 0

    if exists(fn):

        mode = "a"

        with open(fn, "r") as fd:

            rows    = [ row for row in reader(fd) ]
            i       = rows[-1][2]

    recs = quick_tas(contract_id, multiplier, None, i)

    groups  = {}
    out     = []

    for j in range(len(recs)):

        rec     = recs[i]
        ts      = str(rec[tas_rec.timestamp])[:-3]
        price   = rec[tas_rec.price]
        side    = rec[tas_rec.side]

        if ts not in groups:

            groups[ts] = []

        groups[ts].append((i + j, *rec))

    for ts, group in groups.items():

        prices      = [ rec[tas_rec.price] for rec in group ]
        min_price   = min(prices)
        max_price   = max(prices)
        ticks       = int((max_price - min_price) / tick_size)

        if ticks >= min_len:

            side    = 0 if prices[0] > prices[-1] else 1
            qty     = sum([ rec[tas_rec.qty] for rec in group ])
            ts_full = ts_to_ds(group[0][tas_rec.timestamp], FMT)
            i       = group[0][0]
            j       = group[-1][0]

            out.append(
                [
                    ts_full,
                    i,
                    j,
                    ticks,
                    min_price,
                    max_price,
                    qty,
                    side
                ]
            )

    with open(fn, mode) as fd:

        writer_ = writer(fd)

        if mode == "w":

            writer_.writerow(COLS)

        for row in out:

            writer_.writerow(row)
        
    print(f"{len(recs)} recs\t{time() - t0:0.1f}s")
    
    pass