import  polars                  as      pl
import  plotly.graph_objects    as      go
from    re                      import  search
from    sys                     import  argv, path

path.append(".")

from    config                  import  CONFIG
from    util.dbn_util           import  strptime


# python charts/l1_tick.py RBH4-HOH4 2024-02-19


pl.Config.set_tbl_cols(18)


FMT         = "%Y-%m-%dT%H:%M:%S.%f"
TZ          = CONFIG["tz"]


def bid_ask_trace(it):

    prev = None

    x = []
    y = []
    t = []

    for row in it:

        price = row[2]

        if price != prev and price != None:

            x.append(row[0])
            t.append(row[1])
            y.append(price)

            prev = price
    
    return x, y, t


def trade_trace(it):

    x   = []
    y   = []
    z   = []
    c   = []
    t   = []

    r0          = next(it)
    prev_idx    = r0[0]
    prev_ts     = r0[1]
    prev_side   = r0[2]
    prev_price  = r0[3]
    prev_qty    = r0[4]

    for row in it:

        idx     = row[0]
        ts      = row[1]
        side    = row[2]
        price   = row[3]
        qty     = row[4]

        if price != prev_price or side != prev_side:

            x.append(prev_idx)
            y.append(prev_price)
            z.append(prev_qty)
            c.append("#FF0000" if side == "A" else "#0000FF" if side == "B" else "#cccccc")
            t.append(prev_ts)

            prev_qty = 0

        prev_idx    = idx
        prev_ts     = ts
        prev_side   = side
        prev_price  = price
        prev_qty    += qty
    
    # add last trade
        
    x.append(prev_idx)
    y.append(prev_price)
    z.append(qty)
    c.append("#FF0000" if side == "A" else "#0000FF" if side == "B" else "#cccccc")
    t.append(prev_ts)

    return x, y, z, c, t


if __name__ == "__main__":

    contract_id     = argv[1]
    df              = pl.read_csv(f"{CONFIG['dbn_root']}/csvs/{contract_id}.csv")
    df              = strptime(df, "ts_event", "ts", FMT, TZ)
    bounds          = [ arg for arg in argv if search("\d{4}-\d{2}-\d{2}", arg) ]
    start           = bounds[0] if len(bounds) > 0 else df["ts"][0]
    end             = bounds[1] if len(bounds) > 1 else df["ts"][-1]
    ts_x            = not "tick" in argv
    df              = df.filter((df['ts'] >= start) & (df['ts'] <= end)).with_row_index()
    fig             = go.Figure(layout = { "title": f"{contract_id}<br>{start}<br>{end}" })

    if df.is_empty():

        print("no records matched")

        exit()

    bids    = df.select([ "index", "ts", "bid_px_00", "bid_sz_00" ])
    asks    = df.select([ "index", "ts", "ask_px_00", "ask_sz_00" ])
    trades  = df.filter(pl.col("action") == "T").select([ "index", "ts", "side", "price", "size" ])

    bid_x, bid_y, bid_t = bid_ask_trace(bids.iter_rows())
    ask_x, ask_y, ask_t = bid_ask_trace(asks.iter_rows())
    
    trade_x, trade_y, trade_z, trade_c, trade_t = trade_trace(trades.iter_rows())

    traces = [
        ( bid_t if ts_x else bid_x, bid_y, bid_t, "bid", "lines", { "marker": { "color": "#0000FF" }, "line": { "shape": "hv" } } ),
        ( ask_t if ts_x else ask_x, ask_y, ask_t, "ask", "lines", { "marker": { "color": "#FF0000" }, "line": { "shape": "hv" } } ),
        ( trade_t if ts_x else trade_x, trade_y, trade_z, "trades", "markers", { "marker_size": trade_z, "marker": { "color": trade_c, "sizemode": "area", "sizeref": 2. * max(trade_z) / (40.**2), "sizemin": 4 } } )
    ]

    for trace in traces:

        t = {
            "x":    trace[0],
            "y":    trace[1],
            "text": trace[2],
            "name": trace[3],
            "mode": trace[4]
        }

        for key, item in trace[5].items():

            t[key] = item

        fig.add_trace(go.Scattergl(t))

    fig.show()
