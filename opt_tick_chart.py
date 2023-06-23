import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    typing                  import  List
from    util.aggregations       import  split_tick_series, vbp
from    util.contract_settings  import  get_settings
from    util.features           import  ewma, twap
from    util.parsers            import  tas_rec
from    util.rec_tools          import  get_tas
from    util.sc_dt              import  ts_to_ds


EWMA_LEN    = 50
FMT         = "%Y-%m-%dT%H:%M:%S.%f"


# usage:
#
#   python opt_tick_chart.py "LON23 P6000.FUT_OPT.NYMEX" CLN23_FUT_CME 2023-06-01 2023-06-02


def add_chart(
    title:      str,
    recs:       List,
    fig:        go.Figure,
    row:        int,
    add_liq:    bool
):

    bid_trades  = [ rec for rec in recs if not rec[tas_rec.side] ]
    ask_trades  = [ rec for rec in recs if rec[tas_rec.side] ]

    bid_x, bid_y, bid_z = split_tick_series(bid_trades)
    ask_x, ask_y, ask_z = split_tick_series(ask_trades)

    vbp_hist        = vbp(recs)
    twap_x, twap_y  = twap(recs)

    bid_x   = [ ts_to_ds(val, FMT) for val in bid_x ]
    ask_x   = [ ts_to_ds(val, FMT) for val in ask_x ]
    twap_x  = [ ts_to_ds(val, FMT) for val in twap_x ]

    bid_liq_ewma = ewma(bid_z, EWMA_LEN)
    ask_liq_ewma = ewma(ask_z, EWMA_LEN)

    # trades

    for trace in [
        ( bid_x, bid_y, bid_z, bid_liq_ewma, "bid", "#FF0000", "#0000FF" ),
        ( ask_x, ask_y, ask_z, ask_liq_ewma, "ask", "#0000FF", "#FF0000" )
    ]:
        
        max_trade = max(max(bid_z), max(ask_z))

        fig.add_trace(
            go.Scattergl(
                {
                    "name":         f"{title} {trace[4]}",
                    "x":            trace[0],
                    "y":            trace[1],
                    "mode":         "markers",
                    "marker_size":  trace[2],
                    "marker":       {
                                        "color":    trace[5],
                                        "sizemode": "area",
                                        "sizeref":  2. * max_trade / (40.**2),
                                        "sizemin":  4
                                    },
                    "text":         trace[2]
                }
            ),
            row = row,
            col = 2
        )

        if add_liq:

            fig.add_trace(
                go.Scattergl(
                    {
                        "name": f"{title} {trace[4]} liq[{EWMA_LEN}]",
                        "x":    trace[0],
                        "y":    trace[3],
                        "line": { "color": trace[6] }
                    }
                ),
                row = row + 1,
                col = 2
            )

    # vbp

    fig.add_trace(
        go.Histogram(
            {
                "name":     f"{title} vbp",
                "y":        vbp_hist,
                "nbinsy":   len(set(vbp_hist)),
                "opacity":  0.5   
            }
        ),
        row = row,
        col = 1
    )

    # twap

    fig.add_trace(
        go.Scattergl(
            x               = twap_x,
            y               = twap_y,
            marker_color    = "#CCCCCC",
            name            = f"{title} twap"
        ),
        row = row,
        col = 2
    )


if __name__ == "__main__":

    opt_id          = argv[1]
    und_id          = argv[2]
    title           = f"{und_id}\t{opt_id}"
    multiplier, _   = get_settings(opt_id)  # assumes options and future have same tick size
    start           = argv[4] if len(argv) > 4 else None
    end             = argv[5] if len(argv) > 5 else None
    opt_recs        = get_tas(opt_id, multiplier, None, start, end)
    und_recs        = get_tas(und_id, multiplier, None, start, end)

    if not opt_recs or not und_recs:

        print("no records matched")

        exit()

    und_bid_trades = [ rec for rec in und_recs if not rec[tas_rec.side] ]
    und_ask_trades = [ rec for rec in und_recs if rec[tas_rec.side] ]
    
    opt_bid_trades = [ rec for rec in opt_recs if not rec[tas_rec.side] ]
    opt_ask_trades = [ rec for rec in opt_recs if rec[tas_rec.side] ]

    fig = make_subplots(
        rows                = 3,
        cols                = 2,
        row_heights         = [ 0.45, 0.1, 0.45 ],
        column_widths       = [ 0.1, 0.9 ],
        shared_xaxes        = True,
        shared_yaxes        = True,
        vertical_spacing    = 0.0225,
        horizontal_spacing  = 0.0225,
        subplot_titles      = ( title, "" )   
    )

    add_chart("und", und_recs, fig, 1, True)
    add_chart("opt", opt_recs, fig, 3, False)

    fig.show()