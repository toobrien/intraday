from    math        import  e, log
import  numpy       as      np
from    scipy.stats import  norm


SIG_BOUND   = 5                                             # max stdevs for pricing
DEF_STEP    = 0.20                                          # increment for sampling pdf
X           = np.arange(-SIG_BOUND, SIG_BOUND, DEF_STEP)
Y           = norm.pdf(X)


# vectorized version of pricing.py

# example: fly(4552.50, 4550.00, 5.00, 0.0006, 0.01)

def fly(
    cur_price:  np.ndarray,
    mid:        np.ndarray,     # middle strike
    width:      float,          # mid strike -> wing
    f_sigma:    np.ndarray,     # est. stdev of forward price distribution (as log return)
) -> np.ndarray:

    vals = None

    if np.all(f_sigma == 0):

        # expiration

        vals = np.maximum(0, width - abs(cur_price - mid))
    
    else:

        vals = np.sum([ np.maximum(0, width - abs((cur_price * e**(X[i] * f_sigma) - mid))) * Y[i] for i in range(len(X)) ], axis = 0) * DEF_STEP

    return vals


def iron_fly(
    cur_price:  np.ndarray,
    mid:        np.ndarray, # middle strike
    width:      float,      # mid strike -> wing
    f_sigma:    np.ndarray  # est. stdev of forward price distribution (as log return)
) -> np.ndarray:
    
    vals = None

    if f_sigma == 0:

        vals = np.minimum(width, abs(cur_price - mid))

    else:

        vals = np.sum([ ( np.minimum(width, abs((cur_price * e**(X[i] * f_sigma) - mid))) ) * Y[i] for i in range(len(X)) ], axis = 0) * DEF_STEP

    return vals


def call_vertical(
    cur_price:  np.ndarray,
    lo_strike:  np.ndarray,          
    width:      float,      # high strike -> low strike          
    f_sigma:    np.ndarray  # est. stdev of forward price distribution (as log return)
) -> np.ndarray:
    
    vals = None

    if np.all(f_sigma == 0):

        vals = np.minimum(np.maximum(0, cur_price - lo_strike), width)

    else:

        vals = np.sum([ np.minimum(np.maximum(0, cur_price * e**(X[i] * f_sigma) - lo_strike), width) * Y[i] for i in range(len(X)) ], axis = 0) * DEF_STEP

    return vals


def put_vertical(
    cur_price:  np.ndarray,
    hi_strike:  np.ndarray,          
    width:      float,      # high strike -> low strike          
    f_sigma:    np.ndarray  # est. stdev of forward price distribution (as log return)
) -> np.ndarray:
    
    vals = None

    if np.all(f_sigma == 0):

        vals = np.minimum(np.maximum(0, hi_strike - cur_price), width)

    else:

        vals = np.sum([ np.minimum(np.maximum(0, hi_strike - cur_price * e**(X[i] * f_sigma)), width) * Y[i] for i in range(len(X)) ], axis = 0) * DEF_STEP

    return vals


def straddle(
    cur_price:  np.ndarray,
    mid_strike: np.ndarray,
    f_sigma:    np.ndarray  # est. stdev of forward price distribution (as log return)
) -> np.ndarray:
    
    vals = None

    if f_sigma == 0:

        vals = abs(cur_price - mid_strike)
    
    else:

        vals = np.sum([ abs(cur_price * e**(X[i] * f_sigma) - mid_strike) * Y[i] for i in range(len(X)) ], axis = 0) * DEF_STEP
    
    return vals


def put(
    cur_price:  np.ndarray,
    strike:     np.ndarray,          
    f_sigma:    np.ndarray  # est. stdev of forward price distribution (as log return)
) -> np.ndarray:
    
    vals = None

    if np.all(f_sigma == 0):

        vals = np.maximum(0, strike - cur_price)

    else:

        vals = np.sum([ np.maximum(0, strike - cur_price * e**(X[i] * f_sigma)) * Y[i] for i in range(len(X)) ], axis = 0) * DEF_STEP

    return vals


def call(
    cur_price:  np.ndarray,
    strike:     np.ndarray,          
    f_sigma:    float       # est. stdev of forward price distribution (as log return)
) -> np.ndarray:
    
    vals = None

    if np.all(f_sigma == 0):

        vals = np.maximum(0, cur_price - strike)

    else:

        vals = np.sum([ np.maximum(0, cur_price * e**(X[i] * f_sigma) - strike) * Y[i] for i in range(len(X)) ], axis = 0) * DEF_STEP

    return vals