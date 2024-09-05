from    bisect      import  bisect_left
from    databento   import  Historical
from    datetime    import  datetime, timedelta
import  numpy       as      np
import  polars      as      pl
from    sys         import  argv
from    time        import  time


CLIENT      = Historical()
DATE_FMT    = "%Y-%m-%d"
FMT         = "%Y-%m-%dT%H:%M:%S.%f+0000"

pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_rows(-1)


# python screens/reg/get_historical.py rty_emd 2024-06-18 - RTYU4 EMDU4 


def get_df(
    symbol: str, 
    start:  str, 
    end:    str
):
    
    args = {
            "dataset":  "GLBX.MDP3",
            "schema":   "mbp-1",
            "stype_in": "raw_symbol",
            "symbols":  [ symbol ],
            "start":    start,
            "end":      end 
    }

    cost = CLIENT.metadata.get_cost(**args)
    size = CLIENT.metadata.get_billable_size(**args)

    print(f"{symbol + ' cost':<15}{cost:0.4f}")
    print(f"{symbol + ' size':<15}{size} ({size / 1073741824:0.2f} GB)")

    try:

        df  = pl.from_pandas(
                CLIENT.timeseries.get_range(**args).to_df(),
                include_index = False
            ).with_columns(
                pl.col(
                    "ts_event"
                ).dt.convert_time_zone(
                    "America/Los_Angeles"
                ).dt.strftime(
                    FMT
                ).alias(
                    "ts"
                )
            )
    
    except Exception as e:

        print(e)

        df = pl.DataFrame()

    return df



if __name__ == "__main__":

    t0  = time()

    folder      = argv[1]
    start_date  = datetime.strptime(argv[2], DATE_FMT)
    end_date    = datetime.strptime(argv[3], DATE_FMT) if argv[3] != "-" else datetime.today()
    date_range  = [ 
                    date.strftime(DATE_FMT) 
                    for date in 
                    pl.date_range(start_date, end_date, interval = "1d", eager = True) 
                ]
    symbols     = argv[4:]

    for i in range(len(date_range) - 1):

        t_i         = time()
        start_date  = date_range[i]
        end_date    = date_range[i + 1]
        start_ts    = "0000"
        end_ts      = "0000"
        data        = {}
        skip_date   = False

        for symbol in symbols:

            in_df = get_df(symbol, start_date, end_date)

            if in_df.is_empty() or skip_date:

                skip_date = True

                continue

            sym         = symbol[:-2]
            ts          = in_df["ts"]
            bid         = in_df["bid_px_00"]
            ask         = in_df["ask_px_00"]
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
            
        if skip_date:

            continue

        start_ts    = (datetime.fromisoformat(start_ts).replace(microsecond = 0) + timedelta(seconds = 1))
        end_ts      = (datetime.fromisoformat(end_ts).replace(microsecond = 0) + timedelta(seconds = 1))
        cur_ts      = start_ts
        ts_rng      = []

        while cur_ts <= end_ts:

            ts_rng.append(cur_ts.strftime("%Y-%m-%dT%H:%M:%S"))

            cur_ts += timedelta(seconds = 1)

        out_df = pl.DataFrame(
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

            out_df = out_df.with_columns(
                    [
                        pl.Series(f"{sym}_bid", bid),
                        pl.Series(f"{sym}_ask", ask),
                        pl.Series(sym, mid)
                    ]
                )
        
        out_df.write_csv(f"./screens/reg/historical/{folder}/{start_date}.csv")

        print(f"{start_date:<15}{time() - t_i:0.1f}s\n")

    print(f"{time() - t0:0.1f}s\n")