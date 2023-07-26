from math           import e, log
from numpy          import arange
from scipy.stats    import norm


def fly(
    cur_price:  float,
    mid:        float,  # middle strike
    width:      float,  # mid strike -> wing
    f_sigma:    float,  # log return forward stdev
    step:       float   # number of samples for pricing
):

    upper   = log((mid + width) / cur_price)
    lower   = log((mid - width) / cur_price)

    a = min(upper, lower) / f_sigma
    b = max(upper, lower) / f_sigma

    x   = arange(a, b, step)
    y   = norm.pdf(x)
    y_  = sum([ (width - abs((cur_price * e**(x[i] * f_sigma) - mid))) * y[i] * step for i in range(len(x)) ])

    pass


if __name__ == "__main__":

    fly(4553.50, 4550.0, 5.0, 0.00065, 0.01)
