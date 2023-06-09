import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    util.features           import  vbp
from    util.rec_tools          import  get_tas, ohlcv, ohlcv_rec, tas_rec
from    util.sc_dt              import  ts_to_ds


# usage: python period_vbp.py CLN23_FUT_CME 0.01 1:H 2023-06-08


MIN = 10 # sometimes a few trades print during a break... ignore these
FMT = "%Y-%m-%d %H:%M:%S"


if __name__ == "__main__":

    contract_id = argv[1]
    title       = argv[1].split(".")[0] if "." in argv[1] else argv[1].split("_")[0]
    multiplier  = float(argv[2])
    resolution  = argv[3]
    start       = argv[4] if len(argv) > 4 else None
    end         = argv[5] if len(argv) > 5 else None
    recs        = get_tas(contract_id, multiplier, None, start, end)
    bars        = ohlcv(recs, resolution)

    if not recs:

        print("no records matched")

        exit()

    traces  = []
    col     = 1

    for bar in bars:

        selected = recs[bar[ohlcv_rec.i] : bar[ohlcv_rec.j]]

        if len(selected) > MIN:

            start_ds    = ts_to_ds(selected[0][tas_rec.timestamp], FMT)
            name        = f"{start_ds}"
            vbp_y       = vbp(selected)

            traces.append(
                (
                    go.Histogram(
                        {
                            "y":            vbp_y,
                            "nbinsy":       len(set(vbp_y)),
                            "name":         name,
                            "marker_color": "#FF00FF",
                            "opacity":      0.5
                        },
                    ),
                    col
                )
            )

            col += 1

    fig = make_subplots(
        rows                = 1,
        cols                = col - 1,
        shared_yaxes        = True,
        horizontal_spacing  = 0.0,
        subplot_titles      = ( title, )
    )

    for trace in traces:

        fig.add_trace(
            trace[0],
            row = 1,
            col = trace[1]
        )

    fig.show()