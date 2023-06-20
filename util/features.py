from bisect         import bisect_left, bisect_right
from numpy          import arange
from polars         import Series
from scipy.stats    import gaussian_kde, norm
from statistics     import mean, mode, stdev
from typing         import List
from util.rec_tools import tas_rec


def delta(recs: List):

    delta       = 0
    prev_price  = recs[0][tas_rec.price]
    prev_side   = recs[0][tas_rec.side]
    deltas      = []

    for rec in recs:

        price   = rec[tas_rec.price]
        qty     = rec[tas_rec.qty]
        side    = rec[tas_rec.side]

        delta += qty if side else -qty

        if price != prev_price or side != prev_side:

            deltas.append(delta)

        prev_price  = price
        prev_side   = side

    # last trade

    deltas.append(delta)

    return deltas


def ewma(recs: List, window: int):

    return Series(recs).ewm_mean(span = window)


def liq_by_price(
    bid_prices: List, 
    bid_trades: List, 
    ask_prices: List, 
    ask_trades: List
):

    prices  = set(bid_prices + ask_prices)
    liq     = { price: [] for price in prices }

    for pair in [ 
        ( bid_prices, bid_trades ),
        ( ask_prices, ask_trades )
    ]:
        
        prices = pair[0]
        trades = pair[1]

        for i in range(len(prices)):

            price   = prices[i]
            qty     = trades[i]

            liq[price].append(qty)
        
    for price, qtys in liq.items():

        liq[price] = mean(qtys)

    liq_x = sorted(list(liq.keys()))
    liq_y = [ liq[price] for price in liq_x ]

    return liq_x, liq_y


def tick_time(recs: List, window: int):

    up_x = []
    up_y = []
    dn_x = []
    dn_y = []

    prev_chg_ts = recs[0][tas_rec.timestamp]
    prev_price  = recs[0][tas_rec.price]

    for rec in recs:

        ts          = rec[tas_rec.timestamp]
        price       = rec[tas_rec.price]
        p_chg       = price - prev_price
        t_chg       = (ts - prev_chg_ts) / 1e6
        prev_price  = price

        if (t_chg > 3600):

            # skip session/daily breaks and extremely long trades

            prev_chg_ts = ts

        elif p_chg < 0:

            dn_x.append(ts)
            dn_y.append(t_chg)

            prev_chg_ts = ts

        elif p_chg > 0:

            up_x.append(ts)
            up_y.append((t_chg))

            prev_chg_ts = ts

    up_y = Series(up_y).ewm_mean(span = window)
    dn_y = Series(dn_y).ewm_mean(span = window)

    return dn_x, dn_y, up_x, up_y



def twap(recs: List):

    x           = []
    y           = []
    prev_price  = recs[0][tas_rec.price]
    prev_ts     = recs[0][tas_rec.timestamp]
    dur         = 0
    cum_dur     = 0
    twap        = 0

    for rec in recs[1:]:

        ts      =   rec[tas_rec.timestamp]
        price   =   rec[tas_rec.price]
        dur     +=  ts - prev_ts

        if price == prev_price:

            prev_ts = ts

            continue

        if cum_dur:

            twap *= cum_dur / (cum_dur + dur)
        
        cum_dur = cum_dur + dur

        twap += (dur * prev_price) / cum_dur

        x.append(ts)
        y.append(twap)

        dur         = 0
        prev_ts     = ts
        prev_price  = price

    return x, y


def vbp(recs: List):

    hist = []

    for rec in recs:

        hist += ([ rec[tas_rec.price] ] * rec[tas_rec.qty])
    
    return hist


def vbp_kde(hist: List, bandwidth = None):

    prices          = sorted(list(set(hist)))
    max_volume      = hist.count(mode(hist))
    kernel          = gaussian_kde(hist)
    minima          = []
    maxima          = []

    if bandwidth:
    
        kernel.set_bandwidth(bw_method = bandwidth)

    estimate = kernel.evaluate(prices)

    for i in range(1, len(estimate) - 1):

        prev = estimate[i - 1]
        cur  = estimate[i]
        next = estimate[i + 1]

        if prev < cur and next < cur:

            maxima.append(prices[i])
        
        elif cur < prev and cur < next:

            minima.append(prices[i])

    return prices, estimate, max_volume, maxima, minima


def gaussian_estimates(
    maxima: List,
    minima: List,
    hist:   List,
    stdevs: int = 3
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
        tick_size   = selected[j] - selected[j - 1] # assumes continuous trading one tick from poc!
        left        = selected[0:j]
        hvn_count   = selected.count(mode(selected))
        right       = [ 0 ] * len(left)

        for i in range(len(left)):

            right[i] = hi + (hi - left[i])

        # sample pdf

        x       = selected + right
        mu      = mean(x)
        sigma   = stdev(x)
        y       = arange(mu - stdevs * sigma, mu + stdevs * sigma, tick_size)
        x       = norm.pdf(y, loc = mu, scale = sigma)

        res[f"{mu:0.2f} hvn"] = {
            "y": y,
            "x": x,
            "mu": mu,
            "sigma": sigma,
            "scale_factor": hvn_count / norm.pdf(mu, mu, sigma)
        }

    return res


