from    polars                  import  Series
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    typing                  import  List
from    util.parsers            import  tas_rec
from    util.rec_tools          import  get_tas


# usage: python split_tick_chart.py CLN23_FUT_CME 0.01 2023-05-21 2023-05-22


EWMA_LEN    = 50
FMT         = "%Y-%m-%dT%H:%M:%S.%f"


def get_vbp(recs: List):

    prices = []

    for rec in recs:

        prices += ([ rec[tas_rec.price] ] * rec[tas_rec.qty])
    
    return prices


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

    recs = get_tas(contract_id, multiplier, FMT, start, end)

    if not recs:

        print("no records matched")

        exit()

    bid_trades  = [ rec for rec in recs if not rec[tas_rec.side] ]
    ask_trades  = [ rec for rec in recs if rec[tas_rec.side] ]

    bid_x, bid_y, bid_z, bid_ewma = get_series(bid_trades)
    ask_x, ask_y, ask_z, ask_ewma = get_series(ask_trades)

    vbp = get_vbp(recs)

    fig = make_subplots(
        rows                = 2,
        cols                = 2,
        row_heights         = [ 0.8, 0.2 ],
        column_widths       = [ 0.1, 0.9 ],
        shared_xaxes        = True,
        shared_yaxes        = True,
        vertical_spacing    = 0.0225,
        horizontal_spacing  = 0.0225,
        subplot_titles      = ( title, "" )
    )

    for trace in [
        ( bid_x, bid_y, bid_z, bid_ewma, "bid", "#FF0000" ),
        ( ask_x, ask_y, ask_z, ask_ewma, "ask", "#0000FF" )
    ]:
        
        fig.add_trace(
            go.Scattergl(
                {
                    "name":         trace[4],
                    "x":            trace[0],
                    "y":            trace[1],
                    "mode":         "markers",
                    "marker_size":  trace[2],
                    "marker":       {
                                        "color":    trace[5],
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

        fig.add_trace(
            go.Scattergl(
                {
                    "name": f"{trace[4]} liq",
                    "x":    trace[0],
                    "y":    trace[3],
                    "line": { "color": trace[5] }
                }
            ),
            row = 2,
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

    fig.show()

    pass