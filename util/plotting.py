from    bisect                  import  bisect_left
import  plotly.graph_objects    as      go
from    numpy                   import  arange
from    scipy.stats             import  norm
from    typing                  import  List


def get_title(con_fn: str):

    return con_fn.split(".")[0] if "." in con_fn else con_fn.split("_")[0]


# hist: aggregations.vbp (assume sorted)

def gaussian_vscatter(
    mu:         float,
    sigma:      float,
    hist:       List,
    tick_size:  float,
    name:       str,
    color:      str     = "#ff66ff",
    stdevs:     float   = 4
):
    
    mu_count    = hist.count(hist[bisect_left(hist, mu)])
    y           = arange(mu - stdevs * sigma, mu + stdevs * sigma, tick_size)
    x           = norm.pdf(y, loc = mu, scale = sigma)
    p_mu        = norm.pdf(mu, loc = mu, scale = sigma)
    scale       = mu_count / p_mu

    trace = go.Scatter(
        {
            "x":        x * scale,
            "y":        y,
            "marker":   { "color": color },
            "name":     name
        }
    )

    return trace
