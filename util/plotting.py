import  plotly.graph_objects    as      go
from    numpy                   import  arange, array
from    scipy.stats             import  norm


def gaussian_vscatter(
    mu:         float,
    sigma:      float,
    tick_size:  float,
    scale:      int,
    name:       str,
    color:      str = "#ff66ff",
    stdevs:     float = 3
):

    y = arange(mu - stdevs * sigma, mu + stdevs * sigma, tick_size)
    x = norm.pdf(y, loc = mu, scale = sigma)

    trace = go.Scatter(
        {
            "x":        x * scale,
            "y":        y,
            "marker":   { "color": color },
            "name":     name
        }
    )

    return trace
