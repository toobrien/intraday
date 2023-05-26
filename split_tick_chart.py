from    polars                  import  Series
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    statistics              import  mean
from    sys                     import  argv
from    typing                  import  List
from    util.parsers            import  tas_rec
from    util.rec_tools          import  get_tas
from    util.sc_dt              import  ts_to_ds


# usage: python split_tick_chart.py CLN23_FUT_CME 0.01 2023-05-21 2023-05-22


EWMA_LEN    = 50
FMT         = "%Y-%m-%dT%H:%M:%S.%f"


def get_vbp(recs: List):

    prices = []

    for rec in recs:

        prices += ([ rec[tas_rec.price] ] * rec[tas_rec.qty])
    
    return prices


def get_liq_by_price(
        bid_prices: List, 
        bid_trades: List, 
        ask_prices: List, 
        ask_trades: List
    ):

    prices  = set(bid_prices + ask_prices)
    liq     = { price: [] for price in prices }

    for pair in [ 
        ( bid_prices, bid_trades ),
        ( ask_prices, ask_trades )
    ]:
        
        prices = pair[0]
        trades = pair[1]

        for i in range(len(prices)):

            price   = prices[i]
            qty     = trades[i]

            liq[price].append(qty)
        
    for price, qtys in liq.items():

        liq[price] = mean(qtys)

    liq_x = sorted(list(liq.keys()))
    liq_y = [ liq[price] for price in liq_x ]

    return liq_x, liq_y


def get_twap(recs: List):

    x           = []
    y           = []
    prev_price  = recs[0][tas_rec.price]
    prev_ts     = recs[0][tas_rec.timestamp]
    dur         = 0
    cum_dur     = 0
    twap        = 0

    for rec in recs[1:]:

        ts      =   rec[tas_rec.timestamp]
        price   =   rec[tas_rec.price]
        dur     +=  ts - prev_ts

        if price == prev_price:

            prev_ts = ts

            continue

        if cum_dur:

            twap *= cum_dur / (cum_dur + dur)
        
        cum_dur = cum_dur + dur

        twap += (dur * prev_price) / cum_dur

        x.append(ts)
        y.append(twap)

        dur         = 0
        prev_ts     = ts
        prev_price  = price

    return x, y


def get_tick_time(recs: List):

    up_x = []
    up_y = []
    dn_x = []
    dn_y = []

    prev_chg_ts = recs[0][tas_rec.timestamp]
    prev_price  = recs[0][tas_rec.price]

    for rec in recs:

        ts      = rec[tas_rec.timestamp]
        price   = rec[tas_rec.price]
        chg     = price - prev_price

        if chg < 0:

            dn_x.append(ts)
            dn_y.append((ts - prev_chg_ts) / 1e6)

            prev_chg_ts = ts

        elif chg > 0:

            up_x.append(ts)
            up_y.append((ts - prev_chg_ts) / 1e6)

            prev_chg_ts = ts

        prev_price = price

    up_y = Series(up_y).ewm_mean(span = EWMA_LEN)
    dn_y = Series(dn_y).ewm_mean(span = EWMA_LEN)

    return dn_x, dn_y, up_x, up_y


def get_series(recs: List):

    x           = []
    y           = []
    z           = []
    prev_price  = recs[0][tas_rec.price]
    cum_qty     = recs[0][tas_rec.qty]

    for rec in recs:

        ts      = rec[tas_rec.timestamp]
        price   = rec[tas_rec.price]
        qty     = rec[tas_rec.qty]

        if price == prev_price:

            cum_qty += qty
        
        else:

            x.append(ts)
            y.append(price)
            z.append(cum_qty)

            prev_price  = price
            cum_qty     = qty
        
    # add final trade

    x.append(ts)
    y.append(price)
    z.append(cum_qty)

    ewma = Series(z).ewm_mean(span = EWMA_LEN)

    return ( x, y, z, ewma )


if __name__ == "__main__":

    contract_id = argv[1]
    title       = argv[1].split(".")[0] if "." in argv[1] else argv[1].split("_")[0]
    multiplier  = float(argv[2])
    start       = argv[3] if len(argv) > 3 else None
    end         = argv[4] if len(argv) > 4 else None

    recs = get_tas(contract_id, multiplier, None, start, end)

    if not recs:

        print("no records matched")

        exit()

    bid_trades  = [ rec for rec in recs if not rec[tas_rec.side] ]
    ask_trades  = [ rec for rec in recs if rec[tas_rec.side] ]

    bid_x, bid_y, bid_z, bid_liq_ewma = get_series(bid_trades)
    ask_x, ask_y, ask_z, ask_liq_ewma = get_series(ask_trades)

    vbp = get_vbp(recs)
    
    twap_x, twap_y = get_twap(recs)

    bid_x   = [ ts_to_ds(val, FMT) for val in bid_x ]
    ask_x   = [ ts_to_ds(val, FMT) for val in ask_x ]
    twap_x  = [ ts_to_ds(val, FMT) for val in twap_x ]

    liq_x, liq_y = get_liq_by_price(bid_y, bid_z, ask_y, ask_z)

    dn_tick_time_x, dn_tick_time_y, up_tick_time_x, up_tick_time_y = get_tick_time(recs)

    dn_tick_time_x = [ ts_to_ds(ts, FMT) for ts in dn_tick_time_x ]
    up_tick_time_x = [ ts_to_ds(ts, FMT) for ts in up_tick_time_x ]

    fig = make_subplots(
        rows                = 3,
        cols                = 3,
        row_heights         = [ 0.7, 0.15, 0.15 ],
        column_widths       = [ 0.1, 0.8, 0.1 ],
        shared_xaxes        = True,
        shared_yaxes        = True,
        vertical_spacing    = 0.0225,
        horizontal_spacing  = 0.0225,
        subplot_titles      = ( title, "" )
    )

    for trace in [
        ( bid_x, bid_y, bid_z, bid_liq_ewma, up_tick_time_x, up_tick_time_y, "bid", "#FF0000", "#0000FF" ),
        ( ask_x, ask_y, ask_z, ask_liq_ewma, dn_tick_time_x, dn_tick_time_y, "ask", "#0000FF", "#FF0000" )
    ]:
        
        fig.add_trace(
            go.Scattergl(
                {
                    "name":         trace[6],
                    "x":            trace[0],
                    "y":            trace[1],
                    "mode":         "markers",
                    "marker_size":  trace[2],
                    "marker":       {
                                        "color":    trace[7],
                                        "sizemode": "area",
                                        "sizeref":  2. * max(trace[2]) / (40.**2),
                                        "sizemin":  4
                                    },
                    "text":         trace[2]
                }
            ),
            row = 1,
            col = 2
        )

        # liq

        fig.add_trace(
            go.Scattergl(
                {
                    "name": f"{trace[6]} liq[{EWMA_LEN}]",
                    "x":    trace[0],
                    "y":    trace[3],
                    "line": { "color": trace[8] }
                }
            ),
            row = 2,
            col = 2
        )

        # tick time

        fig.add_trace(
            go.Scattergl(
                {
                    "name": "up_tick_time" if trace[6] == "bid" else "dn_tick_time",
                    "x":    trace[4],
                    "y":    trace[5],
                    "line": { "color": trace[8] }
                }
            ),
            row = 3,
            col = 2
        )

    fig.add_trace(
        go.Histogram(
            {
                "name":     "vbp",
                "y":        vbp,
                "nbinsy":   len(set(vbp)),
                "opacity":  0.5
            }
        ),
        row = 1,
        col = 1
    )

    fig.add_trace(
        go.Scattergl(
            x               = twap_x,
            y               = twap_y,
            marker_color    = "#CCCCCC",
            name            = "twap"
        ),
        row = 1,
        col = 2
    )

    fig.add_trace(
        go.Bar(
            x               = liq_y,
            y               = liq_x,
            text            = [ f"{val:0.1f}" for val in liq_y ] ,
            marker_color    = "#cccccc",
            name            = "combined liq",
            orientation     = "h"
        ),
        row = 1,
        col = 3
    )

    fig.show()