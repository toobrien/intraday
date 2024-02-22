import  polars                  as      pl
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv, path

path.append(".")

from    config                  import  CONFIG
from    util.parsers            import  depth_cmd, depth_rec, tas_rec
from    util.rec_tools          import  intraday_tas_and_depth


# python charts/l1_tick.py RBH4-HOH4 2024-02-19


FMT = "%Y-%m-%dT%H:%M:%S.%f"


'''
publisher_id 	uint16_t 	The publisher ID assigned by Databento, which denotes the dataset and venue.
instrument_id 	uint32_t 	The numeric instrument ID.
ts_event 	    uint64_t 	The matching-engine-received timestamp expressed as the number of nanoseconds since the UNIX epoch.
price 	        int64_t 	The order price where every 1 unit corresponds to 1e-9, i.e. 1/1,000,000,000 or 0.000000001.
size 	        uint32_t 	The order quantity.
action 	        char 	    The event action. Can be Add, Cancel, Modify, cleaR book, or Trade.
side 	        char 	    The order side. Can be Ask, Bid, or None.
flags 	        uint8_t 	A bit field indicating packet end, message characteristics, and data quality.
depth 	        uint8_t 	The book level where the update event occurred.
ts_recv 	    uint64_t 	The capture-server-received timestamp expressed as the number of nanoseconds since the UNIX epoch.
ts_in_delta 	int32_t 	The matching-engine-sending timestamp expressed as the number of nanoseconds before ts_recv.
sequence 	    uint32_t 	The message sequence number assigned at the venue.
bid_px_N 	    int64_t 	The bid price at level N (top level if N = 00).
ask_px_N 	    int64_t 	The ask price at level N (top level if N = 00).
bid_sz_N 	    uint32_t 	The bid size at level N (top level if N = 00).
ask_sz_N 	    uint32_t 	The ask size at level N (top level if N = 00).
bid_ct_N 	    uint32_t 	The number of bid orders at level N (top level if N = 00).
ask_ct_N 	    uint32_t 	The number of ask orders at level N (top level if N = 00).
'''


if __name__ == "__main__":

    contract_id     = argv[1]
    df              = pl.read_csv(f"{CONFIG['dbn_root']}/csvs/{contract_id}.csv")
    start           = argv[2] if len(argv) > 2 else df["ts_event"][0]
    end             = argv[3] if len(argv) > 3 else df["ts_event"][-1]
    df              = df.filter((df['ts_event'] >= start) & (df['ts_event'] <= end))

    if df.is_empty():

        print("no records matched")

        exit()

    print(df)

    pass