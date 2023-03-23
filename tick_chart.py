from    fileinput               import  input
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots

# pipe input from read_tas.py

# e.g.: 
#       python read_tas.py RBJ23-HOJ23.FUT_SPREAD.CME 0.0001 0 0 | python tick_chart.py
#       python read_tas.py HON23-HOQ23.FUT_SPREAD.CME 0.0001 0 0 | grep 2023-03-08 | python tick_chart.py

if __name__ == "__main__":

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

    for line in input():

        parts = line.split()

        date    = parts[0]
        time    = parts[1]
        price   = float(parts[2])
        qty     = int(parts[3])
        side    = parts[4]

        x.append(i)
        y.append(price)
        txt.append(f"{date}<br>{time}<br>{qty}")
        clr.append("#FF0000" if side == "bid" else "#0000FF")

        prices.add(price)
        hist_y += ([ price ] * qty)

        delta_ += qty * -1 if side == "bid" else qty
        delta.append(delta_)
        clr_delta.append("#FF0000" if delta_ <= 0 else "#0000FF")

        i += 1

    fig = make_subplots(
        rows                = 2,
        cols                = 1,
        row_heights         = [ 0.8, 0.2 ],
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