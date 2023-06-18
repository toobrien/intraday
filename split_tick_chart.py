import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    util.features           import  ewma, liq_by_price, tick_time, twap, vbp, vbp_kde
from    util.parsers            import  tas_rec
from    util.rec_tools          import  get_tas, split_tick_series
from    util.sc_dt              import  ts_to_ds


# usage: python split_tick_chart.py CLN23_FUT_CME 0.01 2023-05-21 2023-05-22

BANDWIDTH   = None
EWMA_LEN    = 50
FMT         = "%Y-%m-%dT%H:%M:%S.%f"

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

    bid_x, bid_y, bid_z = split_tick_series(bid_trades)
    ask_x, ask_y, ask_z = split_tick_series(ask_trades)

    bid_liq_ewma = ewma(bid_z, EWMA_LEN)
    ask_liq_ewma = ewma(ask_z, EWMA_LEN)

    vbp_hist                = vbp(recs)
    twap_x, twap_y          = twap(recs)
    vbp_y, vbp_x, max_vol   = vbp_kde(vbp_hist, BANDWIDTH)

    bid_x   = [ ts_to_ds(val, FMT) for val in bid_x ]
    ask_x   = [ ts_to_ds(val, FMT) for val in ask_x ]
    twap_x  = [ ts_to_ds(val, FMT) for val in twap_x ]

    liq_x, liq_y = liq_by_price(bid_y, bid_z, ask_y, ask_z)

    dn_tick_time_x, dn_tick_time_y, up_tick_time_x, up_tick_time_y = tick_time(recs, EWMA_LEN)

    dn_tick_time_x = [ ts_to_ds(ts, FMT) for ts in dn_tick_time_x ]
    up_tick_time_x = [ ts_to_ds(ts, FMT) for ts in up_tick_time_x ]

    max_trade = max(max(bid_z), max(ask_z))

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
                                        "sizeref":  2. * max_trade / (40.**2),
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
                    "name": f"up_tick_time[{EWMA_LEN}]" if trace[6] == "bid" else f"dn_tick_time[{EWMA_LEN}]",
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
                "name":         "vbp",
                "y":            vbp_hist,
                "nbinsy":       len(set(vbp_hist)),
                "opacity":      0.5,
                "marker_color": "#0000FF"
            }
        ),
        row = 1,
        col = 1
    )

    fig.add_trace(
        go.Scatter(
            {
                "x":        [ val * max_vol for val in vbp_x ],
                "y":        vbp_y,
                "name":     "vbp_kde",
                "marker":   { "color": "#FF0000" }
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