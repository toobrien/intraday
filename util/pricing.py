from math           import e, log
from numpy          import arange
from scipy.stats    import norm


SIG_BOUND   = 5                                         # max stdevs for pricing
DEF_STEP    = 0.20                                      # increment for sampling pdf
X           = arange(-SIG_BOUND, SIG_BOUND, DEF_STEP)
Y           = norm.pdf(X)


# example: fly(4552.50, 4550.00, 5.00, 0.0006, 0.01)

def fly(
    cur_price:  float,
    mid:        float,          # middle strike
    width:      float,          # mid strike -> wing
    f_sigma:    float,          # est. stdev of forward price distribution (as log return)
):

    val = None

    if f_sigma == 0:

        # expiration

        val = max(0, width - abs(cur_price - mid))
    
    else:

        val     = sum([ max(0, width - abs((cur_price * e**(X[i] * f_sigma) - mid))) * Y[i] for i in range(len(X)) ]) * DEF_STEP

    return val


def iron_fly(
    cur_price:  float,
    mid:        float,  # middle strike
    width:      float,  # mid strike -> wing
    f_sigma:    float   # est. stdev of forward price distribution (as log return)
):
    val = None

    if f_sigma == 0:

        val = min(width, abs(cur_price - mid))

    else:

        val = sum([ ( min(width, abs((cur_price * e**(X[i] * f_sigma) - mid))) ) * Y[i] for i in range(len(X)) ]) * DEF_STEP

    return val


def call_vertical(
    cur_price:  float,
    lo_strike:  float,          
    width:      float,  # high strike -> low strike          
    f_sigma:    float   # est. stdev of forward price distribution (as log return)
):
    
    val = None

    if f_sigma == 0:

        val = min(max(0, cur_price - lo_strike), width)

    else:

        val = sum([ min(max(0, cur_price * e**(X[i] * f_sigma) - lo_strike), width) * Y[i] for i in range(len(X)) ]) * DEF_STEP

    return val


def put_vertical(
    cur_price:  float,
    hi_strike:  float,          
    width:      float,  # high strike -> low strike          
    f_sigma:    float   # est. stdev of forward price distribution (as log return)
):
    
    val = None

    if f_sigma == 0:

        val = min(max(0, hi_strike - cur_price), width)

    else:

        val = sum([ min(max(0, hi_strike - cur_price * e**(X[i] * f_sigma)), width) * Y[i] for i in range(len(X)) ]) * DEF_STEP

    return val


def straddle(
    cur_price:  float,
    mid_strike: float,
    f_sigma:    float   # est. stdev of forward price distribution (as log return)
):
    
    val = None

    if f_sigma == 0:

        val = abs(cur_price - mid_strike)
    
    else:

        val = sum([ abs(cur_price * e**(X[i] * f_sigma) - mid_strike) * Y[i] for i in range(len(X)) ]) * DEF_STEP
    
    return val


def put(
    cur_price:  float,
    strike:     float,          
    f_sigma:    float   # est. stdev of forward price distribution (as log return)
):
    
    val = None

    if f_sigma == 0:

        val = max(0, strike - cur_price)

    else:

        val = sum([ max(0, strike - cur_price * e**(X[i] * f_sigma)) * Y[i] for i in range(len(X)) ]) * DEF_STEP

    return val


def call(
    cur_price:  float,
    strike:     float,          
    f_sigma:    float   # est. stdev of forward price distribution (as log return)
):
    
    val = None

    if f_sigma == 0:

        val = max(0, cur_price - strike)

    else:

        val = sum([ max(0, cur_price * e**(X[i] * f_sigma) - strike) * Y[i] for i in range(len(X)) ]) * DEF_STEP

    return val