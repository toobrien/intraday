import  polars                  as      pl
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv, path

path.append(".")

from    config                  import  CONFIG


# python charts/l1_tick.py RBH4-HOH4 2024-02-19


pl.Config.set_tbl_cols(18)


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

def bid_ask_trace(it):

    prev = None

    x = []
    y = []
    t = []

    for row in it:

        if row[3] != prev:

            x.append(row[0])
            t.append(row[1])
            y.append(row[3])

            prev = row[3]
    
    return x, y, t


def trade_trace(it):

    for row in it:

        pass


if __name__ == "__main__":

    contract_id     = argv[1]
    df              = pl.read_csv(f"{CONFIG['dbn_root']}/csvs/{contract_id}.csv")
    bounds          = [ arg for arg in argv if "-" in argv ]
    start           = bounds[0] if len(bounds) > 0 else df["ts_event"][0]
    end             = bounds[1] if len(bounds) > 1 else df["ts_event"][-1]
    x_type          = "ts" if "ts" in argv else "tick"
    df              = df.filter((df['ts_event'] >= start) & (df['ts_event'] <= end)).with_row_index()

    if df.is_empty():

        print("no records matched")

        exit()

    #print(df)

    bids    = df.select([ "index", "ts_event", "bid_px_00", "bid_sz_00" ])
    asks    = df.select([ "index", "ts_event", "ask_px_00", "ask_sz_00" ])
    trades  = df.filter(pl.col("action") == "T").select([ "index", "ts_event", "side", "price", "size" ])

    #print(bids)
    #print(asks)
    #print(trades)

    bid_x, bid_y, bid_t = bid_ask_trace(bids.iter_rows())
    ask_x, ask_y, ask_t = bid_ask_trace(asks.iter_rows())
    
    trade_x, trade_y, trade_z, trade_c, trade_t = trade_trace(trades.iter_rows())

    pass