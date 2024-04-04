from csv                    import reader, writer
from sys                    import argv, path
from time                   import time

path.append(".")

from util.contract_settings import get_settings
from util.rec_tools         import get_tas, quick_tas, get_precision, tas_rec
from util.sc_dt             import ts_to_ds


# ts            unabridged %Y-%m-%dT%H:%M:%S.%f
# type          "ms" or "s"
# idx i         first record (offset from start of file)
# idx j         last record
# ticks         
# min price
# max price
# qty
# side


# python research/sweeps/gen.py ESM24_FUT_CME 5

'''
import numpy as np
import pandas as pd
from struct import calcsize, unpack_from

def parse_tas(f):
    HEADER_LENGTH = 56
    RECORD_FORMAT = "qI3f4I"
    RECORD_LENGTH = calcsize(RECORD_FORMAT)  # 40

    buffer = f.read()
    record_bytes = buffer[HEADER_LENGTH:]
    num_records = len(record_bytes) // RECORD_LENGTH
    if num_records > 0:
        records = np.array(unpack_from(num_records*RECORD_FORMAT, record_bytes)).reshape((num_records, -1))
        result = pd.DataFrame(records, \
                              columns=["timestamp", "unbundled_trade", "ask", "bid", "last", "num_trades", "total_volume", "bid_volume", "ask_volume"])
        result["timestamp"] = pd.Timestamp(1899, 12, 30) + pd.to_timedelta(result["timestamp"], unit="us")
        return result
    return None
'''

FMT     = "%Y-%m-%dT%H:%M:%S.%f"



if __name__ == "__main__":

    t0 = time()

    contract_id             = argv[1]
    min_len                 = argv[2]
    multiplier, tick_size   = get_settings(contract_id)
    precision               = get_precision(str(tick_size))
    recs                    = quick_tas(argv[1])
    
    print(f"{time() - t0:0.1f}s")
    
    pass