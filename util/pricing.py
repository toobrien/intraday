from math           import e, log
from numpy          import arange
from scipy.stats    import norm


def fly(
    cur_price:  float,
    mid:        float,  # middle strike
    width:      float,  # mid strike -> wing
    f_sigma:    float,  # est. stdev of forward price distribution (as log return)
    step:       float   # number of samples for pricing
):

    upper   = log((mid + width) / cur_price)
    lower   = log((mid - width) / cur_price)

    a = min(upper, lower) / f_sigma
    b = max(upper, lower) / f_sigma

    x   = arange(a, b, step)
    y   = norm.pdf(x)
    val = sum([ (width - abs((cur_price * e**(x[i] * f_sigma) - mid))) * y[i] * step for i in range(len(x)) ])

    return val


if __name__ == "__main__":

    # example

    fly(4552.50, 4550.00, 5.00, 0.0006, 0.01)