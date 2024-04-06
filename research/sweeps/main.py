from    enum                import  IntEnum
import  polars              as      pl
from    sys                 import  argv, path
from    time                import  time

path.append(".")

from util.contract_settings import get_settings
from util.rec_tools         import quick_tas, get_precision, tas_rec
from util.sc_dt             import ts_to_ds


COLS = [
    "timestamp",    # unabridged %Y-%m-%dT%H:%M:%S.%f
    "start_rec",    # first record (offset from start of file)
    "end_rec",      # last record
    "ticks",
    "min_price",
    "max_price",
    "qty",
    "side"
]


class sweep_rec(IntEnum):

    timestamp = 0
    start_rec = 1
    end_rec   = 2
    ticks     = 3
    min_price = 4
    max_price = 5
    qty       = 6
    side      = 7


SLICE_LEN = 1000


# python research/sweeps/main.py ESM24_FUT_CME
    

if __name__ == "__main__":

    t0                      = time()
    contract_id             = argv[1]
    multiplier, tick_size   = get_settings(contract_id)
    precision               = get_precision(contract_id)
    df                      = pl.read_csv(f"./research/sweeps/store/{contract_id}.csv")

    for row in df.iter_rows():

        recs = quick_tas(contract_id, multiplier, None, row[sweep_rec.start_rec], row[sweep_rec.end_rec] + SLICE_LEN)

        pass


    print(f"{time() - t0:0.1f}s")

    pass