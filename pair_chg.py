from    json                    import  loads
from    math                    import  log
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List
from    util.rec_tools          import  get_ohlcv, get_tas, ohlcv_rec, tas_rec


SC_ROOT = loads(open("./config.json").read())["sc_root"]
FMT     = "%Y-%m-%dT%H:%M:%S.%f"


# sample usage: python pair_chg.py 2023-04-21T00:00:00.000000 2023-04-22T00:00:00.000000 ESM23_FUT_CME:0.01 NQM23_FUT_CME:0.01 tick
#               python pair_chg.py 2023-04-17 2023-04-22 ESM23_FUT_CME:0.01 NQM23_FUT_CME:0.01 ohlc-1:M-10
#
#               ohlc-1:M-10 -> 1 minute bars, window of 10 bars for lead-lag regression


def tick(
    recs_a: List,
    recs_b: List,
    id_a:   str,
    id_b:   str
):

    a_0 = recs_a[0][tas_rec.price]
    b_0 = recs_b[0][tas_rec.price]

    a_x = [ rec[tas_rec.timestamp] for rec in recs_a ]
    a_y = [ log(rec[tas_rec.price] / a_0) for rec in recs_a ]

    b_x = [ rec[tas_rec.timestamp] for rec in recs_b ]
    b_y = [ log(rec[tas_rec.price] / b_0) for rec in recs_b ]

    fig = go.Figure()

    for trace in [ (a_x, a_y, id_a), (b_x, b_y, id_b) ]:

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    trace[0],
                    "y":    trace[1],
                    "name": trace[2]
                }
            )
        )

    fig.show()


def ohlc(
    recs_a: List,
    recs_b: List,
    id_a:   str,
    id_b:   str,
    res:    str,
    window: int
):

    bars_a = get_ohlcv(recs_a, res, start, end, FMT, True)
    bars_b = get_ohlcv(recs_b, res, start, end, FMT, True)

    a_0 = bars_a[0][ohlcv_rec.c]
    b_0 = bars_b[0][ohlcv_rec.c]
 
    rng = range(0, min(len(bars_a), len(bars_b)))

    x   = [ bars_a[i][ohlcv_rec.ts] for i in rng ]
    a_y = [ log(bars_a[i][ohlcv_rec.c] / a_0) * 100 for i in rng ]
    b_y = [ log(bars_b[i][ohlcv_rec.c] / b_0) * 100 for i in rng ]
    c_y = [ a_y[i] - b_y[i] for i in rng ]

    fig = make_subplots(rows = 2, cols = 1)

    for trace in [
        (a_y, id_a),
        (b_y, id_b),
        (c_y, "diff")
    ]:

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    x,
                    "y":    trace[0],
                    "name": trace[1],
                    "hovertemplate": "%{y:0.2f}"
                }
            ),
            row = 1,
            col = 1
        )

    x  = [ c_y[i] - c_y[i - window] for i in range(window, len(c_y), window) ]
    y  = x[1:]

    fig.add_trace(
        go.Scatter(
            x           = x,
            y           = y,
            name        = f"period_ret_vs_next[{window}]",
            mode        = "markers"
        ),
        row = 2,
        col = 1
    )

    fig.show()



if __name__ == "__main__":

    t0 = time()

    start           = argv[1]
    end             = argv[2]
    id_a, mult_a    = argv[3].split(":")
    id_b, mult_b    = argv[4].split(":")
    mode            = argv[5]

    mult_a = float(mult_a)
    mult_b = float(mult_b)


    if mode == "tick":

        recs_a = get_tas(id_a, mult_a, FMT, start, end)
        recs_b = get_tas(id_b, mult_b, FMT, start, end)

        tick(recs_a, recs_b, id_a, id_b)

    elif "ohlc" in mode:

        recs_a = get_tas(id_a, mult_a, None, start, end)
        recs_b = get_tas(id_b, mult_b, None, start, end)

        res     = mode.split("-")[1]
        window  = int(mode.split("-")[2])

        ohlc(recs_a, recs_b, id_a, id_b, res, window)

    print(f"{time() - t0:0.1f}s")