from    bisect      import  bisect_left
from    databento   import  Historical
from    datetime    import  datetime, timedelta
import  numpy       as      np
import  polars      as      pl
from    sys         import  argv
from    time        import  time


pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_rows(-1)


# python test.py


if __name__ == "__main__":

    t0  = time()

    start_ts = "0000"
    end_ts   = "0000"
    data     = {}

    for symbol in [ "RTYU4", "EMDU4" ]:

        sym = symbol[:-2]
        df  = pl.read_csv(f"~/trading/databento/csvs/{symbol}_mbp-1.csv").with_columns(
                pl.col(
                    "ts_event"
                ).cast(
                    pl.Datetime
                ).dt.convert_time_zone(
                    "America/Los_Angeles"
                ).dt.strftime(
                    "%Y-%m-%dT%H:%M:%S.%f"
                ).alias(
                    "ts"
                )
            )
        
        ts          = df["ts"]
        bid         = df["bid_px_00"]
        ask         = df["ask_px_00"]
        mid         = (bid + ask) / 2

        # start ts is the latest initial timestamp, as i do not know previous state
        # end ts is the latest timestamp of all symbols, as the same period is downloaded for each

        start_ts    = start_ts if start_ts > ts[0] else ts[0]
        end_ts      = end_ts if end_ts > ts[-1] else ts[-1]

        data[sym] = {
                    "ts":   ts,
                    "bid":  bid,
                    "ask":  ask,
                    "mid":  mid
                }
        
        print()
        print(symbol)

        for i in range(100):

            print(ts[i], bid[i], ask[i], mid[i])

    start_ts    = (datetime.fromisoformat(start_ts).replace(microsecond = 0) + timedelta(seconds = 1))
    end_ts      = (datetime.fromisoformat(end_ts).replace(microsecond = 0) + timedelta(seconds = 1))
    cur_ts      = start_ts
    ts_rng      = []

    while cur_ts <= end_ts:

        ts_rng.append(cur_ts.strftime("%Y-%m-%dT%H:%M:%S"))

        cur_ts += timedelta(seconds = 1)

    print()
    print(ts_rng[0])
    print(ts_rng[-1])

    df = pl.DataFrame(
            {
                "ts": ts_rng
            }
        )

    for sym, vecs in data.items():

        ts  = vecs["ts"]
        N   = len(ts)
        idx = np.searchsorted(ts, ts_rng)
        bid = vecs["bid"]
        ask = vecs["ask"]
        mid = vecs["mid"]
    
        ts  = [ ts[int(i - 1)] if i < N else ts[-1] for i in idx ]
        bid = [ bid[int(i - 1)] if i < N else bid[-1] for i in idx ]
        ask = [ ask[int(i - 1)] if i < N else ask[-1] for i in idx ]
        mid = [ mid[int(i - 1)] if i < N else mid[-1] for i in idx ]

        df = df.with_columns(
                [
                    pl.Series(f"{sym}_bid", bid),
                    pl.Series(f"{sym}_ask", ask),
                    pl.Series(sym, mid)
                ]
            )

        pass
            

    print()
    print(df.head(n = 100))

    print()
    print(f"{time() - t0:0.1f}s")