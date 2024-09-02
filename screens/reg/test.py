from    bisect      import  bisect_left
from    databento   import  Historical
from    json        import  loads
import  numpy       as      np
from    os.path     import  join
import  polars      as      pl
from    sys         import  argv
from    time        import  time


pl.Config.set_tbl_cols(-1)


# python test.py


if __name__ == "__main__":

    t0  = time()
    emd = pl.read_csv("~/trading/databento/csvs/EMDU4_mbp-1.csv")
    rty = pl.read_csv("~/trading/databento/csvs/RTYU4_mbp-1.csv")
    
    ts  = np.concatenate((rty["ts_event"], emd["ts_event"]))
    sym = np.concatenate((rty["symbol"], emd["symbol"]))
    bid = np.concatenate((rty["bid_px_00"], emd["bid_px_00"]))
    ask = np.concatenate((rty["ask_px_00"], emd["ask_px_00"]))
    
    idx = np.argsort(ts)

    ts  = ts[idx]
    sym = sym[idx]
    bid = bid[idx]
    ask = ask[idx]

    i   = bisect_left(ts, "2024-08-29T15")

    for i in range(i, i + 50):

        print(ts[i], sym[i], bid[i], ask[i])
    
    print(f"{time() - t0:0.1f}s")

    pass