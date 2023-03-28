import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    util.parsers            import  tas_rec
from    util.tas_tools          import  get_tas


FMT = "%Y-%m-%dT%H:%M:%S.%f"

# start/end time are %Y-%m-%d

if __name__ == "__main__":

    contract_id = argv[1]
    multiplier  = float(argv[2])
    start       = argv[3] if len(argv) > 3 else None
    end         = argv[4] if len(argv) > 4 else None

    recs = get_tas(contract_id, FMT, multiplier, start, end)

    if not recs:

        print("no records matched")

        exit()

    fig = go.Figure()

    x           = []
    y           = []
    hist_y      = []
    txt         = []
    clr         = []
    clr_delta   = []
    delta       = []
    delta_      = 0
    i           = 0
    prices      = set()

    for rec in recs:

        parts   = rec[tas_rec.timestamp].split("T")
        date    = parts[0]
        time    = parts[1]
        price   = rec[tas_rec.price]
        qty     = rec[tas_rec.qty]
        side    = rec[tas_rec.side]

        x.append(i)
        y.append(price)
        txt.append(f"{date}<br>{time}<br>{qty}")
        clr.append("#0000FF" if side else "#FF0000")

        prices.add(price)
        hist_y += ([ price ] * qty)

        delta_ += qty if side else -qty
        delta.append(delta_)
        clr_delta.append("#FF0000" if delta_ <= 0 else "#0000FF")

        i += 1

    fig = make_subplots(
        rows                = 2,
        cols                = 1,
        row_heights         = [ 0.8, 0.2 ],
        shared_xaxes        = True,
        vertical_spacing    = 0.025
    )

    fig.add_trace(
        go.Scattergl(
            {
                "name":    "ticks",
                "x":        x,
                "y":        y,
                "text":     txt,
                "mode":     "markers",
                "marker": {
                    "color": clr
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