from math           import e, log
from numpy          import arange
from scipy.stats    import norm


# example: fly(4552.50, 4550.00, 5.00, 0.0006, 0.01)

def fly(
    cur_price:  float,
    mid:        float,          # middle strike
    width:      float,          # mid strike -> wing
    f_sigma:    float,          # est. stdev of forward price distribution (as log return)
    step:       float = 0.01    # sample increment for pricing
):

    upper   = log((mid + width) / cur_price)
    lower   = log((mid - width) / cur_price)

    a       = min(upper, lower) / f_sigma
    b       = max(upper, lower) / f_sigma

    x       = arange(a, b, step)
    y       = norm.pdf(x)

    val     = sum([ (width - abs((cur_price * e**(x[i] * f_sigma) - mid))) * y[i] for i in range(len(x)) ]) * step

    return val


IRON_FLY_SCALE = 5 # num sigmas for pricing iron fly

def iron_fly(
    cur_price:  float,
    mid:        float,          # middle strike
    width:      float,          # mid strike -> wing
    f_sigma:    float,          # est. stdev of forward price distribution (as log return)
    step:       float = 0.1     # sample increment for pricing
):
    
    x       = arange(-IRON_FLY_SCALE, IRON_FLY_SCALE, step)
    y       = norm.pdf(x)

    val     = sum([ ( min(abs((cur_price * e**(x[i] * f_sigma) - mid)), width) ) * y[i] for i in range(len(x)) ]) * step

    return val