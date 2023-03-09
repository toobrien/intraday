import plotly.graph_objects as go

from fileinput      import input
from util.parsers   import tas_rec
from util.sc_dt     import ts_to_ds
from sys            import argv


# pipe input from read_tas.py

if __name__ == "__main__":

    fig = go.Figure()

    x   = []
    y   = []
    txt = []
    clr = []
    
    i = 0

    for line in input():

        parts = line.split()

        date    = parts[0]
        time    = parts[1]
        price   = parts[2]
        qty     = parts[3]
        side    = parts[4]

        x.append(i)
        y.append(float(price))
        txt.append(f"{date}<br>{time}<br>{qty}")
        clr.append("#FF0000" if side == "bid" else "#0000FF")

        i += 1

    fig.add_trace(
        go.Scatter(
            {
                "x":    x,
                "y":    y,
                "text": txt,
                "mode": "markers",
                "marker": {
                    "color": clr
                }
            }
        )
    )

    fig.show()
        
