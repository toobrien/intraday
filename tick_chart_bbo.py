import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    util.contract_settings  import  get_settings
from    util.plotting           import  get_title
from    util.parsers            import  depth_cmd, depth_rec, tas_rec
from    util.rec_tools          import  intraday_tas_and_depth


# usage: python tick_chart.py CLN23_FUT_CME 0 2023-05-21


FMT = "%Y-%m-%dT%H:%M:%S.%f"


if __name__ == "__main__":

    contract_id     = argv[1]
    title           = get_title(contract_id)
    multiplier, _   = get_settings(contract_id)
    start           = argv[3]
    end             = argv[4] if len(argv) > 4 else None
    recs            = intraday_tas_and_depth(contract_id, multiplier, FMT, start, end)

    if not recs:

        print("no records matched")

        exit()

    fig = go.Figure()

    bid_series      = []
    ask_series      = []
    bids            = {}
    asks            = {}
    best_bid        = float("-inf")
    best_ask        = float("inf")
    x               = []
    y               = []
    sizes           = []
    hist_y          = []
    txt             = []
    clr             = []
    delta           = []
    delta_          = 0
    i               = 0
    marker_i        = 0
    prev_price      = recs[0][tas_rec.price]
    prev_side       = recs[0][tas_rec.side]
    marker_start    = recs[0][tas_rec.timestamp]
    prev_ts         = recs[0][tas_rec.timestamp]
    size            = 0
    prices          = set()

    for rec in recs:

        if len(rec) == len(tas_rec):

            parts   = rec[tas_rec.timestamp].split("T")
            date    = parts[0]
            time    = parts[1]
            price   = rec[tas_rec.price]
            qty     = rec[tas_rec.qty]
            side    = rec[tas_rec.side]

            if price != prev_price or side != prev_side:

                # ticks

                marker_text = f"{date}<br>{time}<br>{size}" if i - 1 == marker_i else f"{date}<br>{marker_start}<br>{prev_ts}<br>{size}"

                x.append(rec[tas_rec.timestamp])
                y.append(prev_price)
                sizes.append(size)
                txt.append(marker_text)
                clr.append("#0000FF" if prev_side else "#FF0000")

                # delta

                delta_ += size if prev_side else -size
                delta.append(delta_)

                prev_side       = side
                prev_price      = price
                size            = qty
                marker_i        = i
                marker_start    = time

            else:

                prev_ts =  time
                size    += qty

            i += 1

            # profile

            prices.add(price)
            hist_y += ([ price ] * qty)
        
        else:

            # depth rec

            ds          = rec[depth_rec.timestamp]
            cmd         = rec[depth_rec.command]
            lvl         = rec[depth_rec.price]
            lots        = rec[depth_rec.quantity]

            if cmd == depth_cmd.add_bid_lvl:

                bids[lvl] = lots

            elif cmd == depth_cmd.del_bid_lvl:

                del bids[lvl]

            elif cmd == depth_cmd.add_ask_lvl:

                asks[lvl] = lots
            
            elif cmd == depth_cmd.del_ask_lvl:

                del asks[lvl]

            if bids:
            
                cur_best_bid = max(bids.keys())
            
                if cur_best_bid != best_bid:

                    best_bid = cur_best_bid

                    bid_series.append(
                        (
                            ds,
                            best_bid,
                            bids[cur_best_bid]
                        )
                    )

            if asks:
                
                cur_best_ask = min(asks.keys())

                if cur_best_ask != best_ask:

                    best_ask = cur_best_ask

                    ask_series.append(
                        (
                            ds,
                            best_ask,
                            asks[cur_best_ask]
                        )
                    )

            pass

    # add final trade
    
    x.append(i)
    y.append(prev_price)
    sizes.append(size)
    txt.append(marker_text)
    clr.append("#0000FF" if prev_side else "#FF0000")
    delta.append(delta_)


    fig = make_subplots(
        rows                = 2,
        cols                = 1,
        row_heights         = [ 0.8, 0.2 ],
        shared_xaxes        = True,
        vertical_spacing    = 0.025,
        subplot_titles = (title, "")
    )

    fig.add_trace(
        go.Scattergl(
            {
                "name":         title,
                "x":            x,
                "y":            y,
                "text":         txt,
                "mode":         "markers",
                "marker_size":  sizes,
                "marker": {
                    "color":    clr,
                    "sizemode": "area",
                    "sizeref":  2. * max(sizes) / (40.**2),
                    "sizemin":  4
                }
            }
        ),
        row = 1,
        col = 1
    )

    fig.add_trace(
        go.Histogram(
            {
                "name":     "vap",
                "y":        hist_y,
                "nbinsy":    len(prices),
                "opacity":  0.3
            }
        ),
        row = 1,
        col = 1
    )

    fig.add_trace(
        go.Scattergl(
            {
                "name":     "bid",
                "x":        [ rec[0] for rec in bid_series ],
                "y":        [ rec[1] for rec in bid_series ],
                "text":     [ rec[2] for rec in bid_series ],
                "line":     { "shape": "hv", "width": 1 },
                "marker":   { "color": "#0000FF" }
            }
        ),
        row = 1,
        col = 1
    )
    
    fig.add_trace(
        go.Scattergl(
            {
                "name":     "ask",
                "x":        [ rec[0] for rec in ask_series ],
                "y":        [ rec[1] for rec in ask_series ],
                "text":     [ rec[2] for rec in ask_series ],
                "line":     { "shape": "hv", "width": 1 },
                "marker":   { "color": "#FF0000" }
            }
        ),
        row = 1,
        col = 1
    )

    fig.add_trace(
        go.Scatter(
            {
                "name": "delta",
                "x":    x,
                "y":    delta,
                "line": { "color": "#0000FF" }
            }
        ),
        row = 2,
        col = 1
    )

    fig.show()