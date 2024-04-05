from csv                    import reader, writer
from os.path                import exists
from random                 import randint
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


# python research/sweeps/gen.py ESM24_FUT_CME 5


FMT = "%Y-%m-%dT%H:%M:%S.%f"

if __name__ == "__main__":

    t0 = time()

    contract_id             = argv[1]
    min_len                 = argv[2]
    multiplier, tick_size   = get_settings(contract_id)
    precision               = get_precision(str(tick_size))
    fn                      = f"./research/sweeps/store/{contract_id}.csv"
    rows                    = []
    i                       = 0

    if exists(fn):

        rows    = [ row for row in reader(fn) ]
        i       = rows[-1][1]

    recs = quick_tas(contract_id, multiplier, None, i, 0)
        
    print(f"{len(recs)} recs\t{time() - t0:0.1f}s")
    
    pass