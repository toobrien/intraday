import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    util.parsers            import  tas_rec
from    util.tas_tools          import  get_tas


FMT         = "%Y-%m-%dT%H:%M:%S.%f"

# start/end time are %Y-%m-%d

if __name__ == "__main__":

    contract_id = argv[1]
    title       = argv[1].split(".")[0] if "." in argv[1] else argv[1].split("_")[0]
    multiplier  = float(argv[2])
    start       = argv[3] if len(argv) > 3 else None
    end         = argv[4] if len(argv) > 4 else None

    recs = get_tas(contract_id, FMT, multiplier, start, end)

    if not recs:

        print("no records matched")

        exit()

    fig = go.Figure()

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

        parts   = rec[tas_rec.timestamp].split("T")
        date    = parts[0]
        time    = parts[1]
        price   = rec[tas_rec.price]
        qty     = rec[tas_rec.qty]
        side    = rec[tas_rec.side]

        if price != prev_price or side != prev_side:

            # ticks

            marker_text = f"{date}<br>{time}<br>{size}" if i - 1 == marker_i else f"{date}<br>{marker_start}<br>{prev_ts}<br>{size}"

            x.append(i)
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