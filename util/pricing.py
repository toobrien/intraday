from math           import e, log
from numpy          import arange
from scipy.stats    import norm


SIG_BOUND = 5 # max stdevs for pricing


# example: fly(4552.50, 4550.00, 5.00, 0.0006, 0.01)

def fly(
    cur_price:  float,
    mid:        float,          # middle strike
    width:      float,          # mid strike -> wing
    f_sigma:    float,          # est. stdev of forward price distribution (as log return)
    step:       float = 0.01    # sample increment for pricing
):

    val = None

    if f_sigma == 0:

        # expiration

        val = max(0, width - abs(cur_price - mid))
    
    else:

        upper   = log((mid + width) / cur_price)
        lower   = log((mid - width) / cur_price)

        a       = min(upper, lower) / f_sigma
        b       = max(upper, lower) / f_sigma

        x       = arange(a, b, step)
        y       = norm.pdf(x)

        val     = sum([ (width - abs((cur_price * e**(x[i] * f_sigma) - mid))) * y[i] for i in range(len(x)) ]) * step

    return val


def iron_fly(
    cur_price:  float,
    mid:        float,          # middle strike
    width:      float,          # mid strike -> wing
    f_sigma:    float,          # est. stdev of forward price distribution (as log return)
    step:       float = 0.1     # sample increment for pricing
):
    val = None

    if f_sigma == 0:

        val = min(width, abs(cur_price - mid))

    else:

        x   = arange(-SIG_BOUND, SIG_BOUND, step)
        y   = norm.pdf(x)

        val = sum([ ( min(width, abs((cur_price * e**(x[i] * f_sigma) - mid))) ) * y[i] for i in range(len(x)) ]) * step

    return val