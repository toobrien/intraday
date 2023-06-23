import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    time                    import  time
from    util.aggregations       import  ohlcv, ohlcv_rec, tick_series, vbp, intraday_ranges
from    util.contract_settings  import  get_settings
from    util.modelling          import  gaussian_estimates, vbp_gmm, kmeans, vbp_kde
from    util.plotting           import  gaussian_vscatter
from    util.rec_tools          import  date_index, get_precision, get_tas, tas_rec
from    util.sc_dt              import  ts_to_ds


FMT = "%Y-%m-%dT%H:%M:%S"


def test_date_index():

    recs    = get_tas("CLN23_FUT_CME", 0.01, FMT, "2023-06-01T00:00:00", "2023-06-08T00:00:00")
    idx     = date_index("CLN23_FUT_CME", recs)

    for date, rng in idx.items():

        days_recs = recs[rng[0] : rng[1]]

        print(f"{date}: {days_recs[0][tas_rec.timestamp]}\t{days_recs[-1][tas_rec.timestamp]}")


def test_intraday_ranges():

    recs    = get_tas("CLN23_FUT_CME", 0.01, FMT, "2023-06-01T00:00:00", "2023-06-08T00:00:00")
    ir_rngs = intraday_ranges("CLN23_FUT_CME", recs, "11:20", "11:30")

    for date, rng in ir_rngs.items():

        rng_recs = recs[rng[0] : rng[1]]

        if rng_recs:

            print(f"{date}: {rng_recs[0][tas_rec.timestamp]}\t{rng_recs[-1][tas_rec.timestamp]}")
        
        else:

            print(f"{date}: no range matched")


def ohlcv_test():

    recs = get_tas("CLN23_FUT_CME", 0.01, None, "2023-06-08")
    bars = ohlcv(recs, "1:H")

    for bar in bars:

        first   = recs[bar[ohlcv_rec.i]]
        last    = recs[bar[ohlcv_rec.j]]
        start   = ts_to_ds(first[tas_rec.timestamp], FMT)
        end     = ts_to_ds(last[tas_rec.timestamp], FMT)

        print(f"{start} - {end}")

    pass


def vbp_kde_test():

    recs = get_tas("CLQ23_FUT_CME", 0.01, None, "2023-06-16")
    hist = vbp(recs)

    y, x, max_vol, maxima, minima = vbp_kde(hist)

    x = [ val * max_vol for val in x ]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            {
                "x": x,
                "y": y
            }
        )
    )

    fig.show()


def gaussian_estimates_test():

    recs = get_tas("CLQ23_FUT_CME", 0.01, None, "2023-06-18")
    hist = vbp(recs)
    _, _, _, maxima, minima = vbp_kde(hist)

    res = gaussian_estimates(maxima, minima, hist)

    pass


def kmeans_test():

    recs            = get_tas("CLQ23_FUT_CME", 0.01, None, "2023-06-21")
    x, y, z, _, _   = tick_series(recs)
    fig             = make_subplots(rows = 2, cols = 2)

    for params in [ 
        (0.8, 1, 1), 
        (0.5, 1, 2),
        (0.3, 2, 1),
        (0.1, 2, 2)
    ]:

        thresh          = params[0]
        r               = params[1]
        c               = params[2]
        centers, labels = kmeans(x, y, thresh)

        fig.add_trace(
            go.Scatter(
                {
                    "x":        x,
                    "y":        y,
                    "mode":     "markers",
                    "marker":   {
                        "color": labels,
                        "sizemode": "area",
                        "sizeref":  2. * max(z) / (40.**2),
                        "sizemin":  4
                    }
                }
            ),
            row = r,
            col = c
        )

    fig.show()


def vbp_gmm_test():

    contract_id             = "CLQ23_FUT_CME"
    multiplier, tick_size   = get_settings(contract_id)
    date                    = "2023-06-22"
    precision               = get_precision(str(multiplier))
    recs                    = get_tas(contract_id, multiplier, None, date)
    hist                    = vbp(recs)
    x, y, z, _, _           = tick_series(recs)
    fig                     = make_subplots(
        rows                = 1, 
        cols                = 2, 
        shared_yaxes        = True,
        horizontal_spacing  = 0.025,
    )

    means, covariances, labels = vbp_gmm(y, hist)

    fig.add_trace(
        go.Scatter(
            {
                "x":        x,
                "y":        y,
                "marker":   { "color": labels },
                "name": contract_id
            }
        ),
        row = 1,
        col = 2
    )

    fig.add_trace(
        go.Histogram(
            {
                "y":            hist,
                "nbinsy":       len(set(hist)),
                "opacity":      0.5,
                "marker_color": "#0000FF",
                "name":         "vbp"
            }
        ),
        row = 1,
        col = 1
    )

    for i in range(len(means)):

        mu      = round(float(means[i]), precision)
        sigma   = round(float(covariances[i]), precision)

        fig.add_trace(
            gaussian_vscatter(
                mu,
                sigma,
                hist,
                tick_size,
                f"c-{i} [{mu:0.2f}, {sigma:0.2f}]"
            ),
            row = 1,
            col = 1
        )
        

    fig.show()


TESTS = {
    0: test_date_index,
    1: test_intraday_ranges,
    2: ohlcv_test,
    3: vbp_kde_test,
    4: gaussian_estimates_test,
    5: kmeans_test,
    6: vbp_gmm_test
}


if __name__ == "__main__":

    t0 = time()

    TESTS[int(argv[1])]()

    print(f"{time() - t0:0.1f}s elapsed")

