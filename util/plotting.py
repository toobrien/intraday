import  plotly.graph_objects    as      go
from    numpy                   import  arange, array
from    scipy.stats             import  norm


def gaussian_vscatter(
    mu:         float,
    sigma:      float,
    tick_size:  float,
    mu_count:   int,
    name:       str,
    color:      str = "#ff66ff",
    stdevs:     float = 4
):

    y       = arange(mu - stdevs * sigma, mu + stdevs * sigma, tick_size)
    x       = norm.pdf(y, loc = mu, scale = sigma)
    scale   = mu_count / norm.pdf(mu)

    trace = go.Scatter(
        {
            "x":        x * scale,
            "y":        y,
            "marker":   { "color": color },
            "name":     name
        }
    )

    return trace
