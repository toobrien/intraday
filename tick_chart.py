import plotly.graph_objects as go

from fileinput      import input
from util.parsers   import tas_rec
from util.sc_dt     import ts_to_ds
from sys            import argv


# pipe input from read_tas.py

if __name__ == "__main__":

    fig = go.Figure()

    x       = []
    y       = []
    hist_y  = []
    txt     = []
    clr     = []
    i       = 0
    prices  = set()

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

        i += 1

    fig.add_trace(
        go.Scatter(
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
        )
    )

    fig.add_trace(
        go.Histogram(
            {
                "name":     "vap",
                "y":        hist_y,
                "nbinsy":    len(prices),
                "opacity":  0.3
            }
        )
    )

    fig.show()
        
