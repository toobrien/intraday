from math               import log, sqrt
from numpy              import array
from bisect             import bisect_left, bisect_right
from scipy.stats        import gaussian_kde
from sklearn.cluster    import KMeans
from sklearn.mixture    import GaussianMixture
from statistics         import mean, mode, stdev
from typing             import List


# hist: aggregations.vbp

def vbp_kde(hist: List, bandwidth = None):

    prices          = sorted(list(set(hist)))
    hvn             = mode(hist)       
    max_volume      = hist.count(hvn)
    kernel          = gaussian_kde(hist)
    minima          = []
    maxima          = []

    if bandwidth:
    
        kernel.set_bandwidth(bw_method = bandwidth)

    estimate        = kernel.evaluate(prices)
    scale_factor    = max_volume / kernel.evaluate(hvn)[0]

    for i in range(1, len(estimate) - 1):

        prev = estimate[i - 1]
        cur  = estimate[i]
        next = estimate[i + 1]

        if prev < cur and next < cur:

            maxima.append(prices[i])
        
        elif cur < prev and cur < next:

            minima.append(prices[i])

    return prices, estimate, scale_factor, maxima, minima


# maxima, minima:   modelling.vbp_kde
# hist:             aggregations.vbp

def gaussian_estimates(
    maxima: List,
    minima: List,
    hist:   List
):

    maxima  = list(reversed(maxima))
    minima  = list(reversed(minima))
    hist    = sorted(hist)
    pairs   = []
    res     = {}

    # maxima and minima come from vbp_kde: len(maxima) == len(minima) + 1
    # they are paired sequentially--first hvn with first lvn, or lowest price in hist

    for i in range(len(maxima)):

        pairs.append(( maxima[i], minima[i] if i < len(minima) else hist[0] ))
    
    for pair in pairs:

        hi          = pair[0] # hvn
        lo          = pair[1] # lvn or lowest price in hist

        # mirror histogram

        selected    = hist[bisect_left(hist, lo) : bisect_right(hist, hi)]
        j           = bisect_left(selected, hi)
        left        = selected[0:j]
        right       = [ 0 ] * len(left)

        for i in range(len(left)):

            right[i] = hi + (hi - left[i])

        # sample pdf

        x       = selected + right
        mu      = mean(x)
        sigma   = stdev(x)
        
        res[f"{mu:0.2f} hvn"] = { "mu": mu, "sigma": sigma }

    return res


# x (tick / contract #):    aggregations.tick_series
# y (price):                aggregations.tick_series

def kmeans(
    x:              List, 
    y:              List, 
    thresh:         float   = 0.10,
    min_clusters:   int     = 1,
    max_clusters:   int     = 25
):

    km              = None
    prev_inertia    = None
    arr             = array([ [ x[i], y[i] ] for i in range(len(x)) ])
    i               = 2

    while i < min_clusters + 1:

        km = KMeans(
            n_clusters  = i,
            n_init      = "auto"
        ).fit(arr)
        
        if prev_inertia:

            if log(prev_inertia / km.inertia_) < thresh:

                # improvement below threshold, finished

                break

        prev_inertia    =  km.inertia_
        i               += 1

    print(f"features.kmeans: fitting finished with {min(i, max_clusters)} clusters")

    return km.cluster_centers_, km.labels_


# y:        rec_tools.tick_series -- sequenced price series for labelling
# vbp_hist: features.vbp

def vbp_gmm(
    y:              List,
    hist:           List,
    thresh:         0.015,
    min_components: int = 1,
    max_components: int = 10
):
    
    Y       = array(y).reshape(-1, 1)
    X       = array(hist).reshape(-1, 1)
    i       = min_components
    models  = []
    aics    = []

    for i in range(min_components, max_components + 1):

        m = GaussianMixture(n_components = i).fit(X)
        
        models.append(m)
        aics.append(m.aic(X))

    chgs = [ log(aics[i] / aics[i - 1]) for i in range(1, len(aics)) ]

    i   = aics.index(min(aics))
    m   = models[i]

    means   = [ mu[0] for mu in m.means_ ]
    sigmas  = [ sqrt(cov[0]) for cov in m.covariances_ ]
    labels  = m.predict(Y)

    print(f"features.gaussian_mixture: fitting finished; found {min_components + i} components")

    return means, sigmas, labels