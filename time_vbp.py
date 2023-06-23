import  plotly.graph_objects    as      go
from    sys                     import  argv
from    util.aggregations       import  ohlcv, ohlcv_rec, vbp
from    util.contract_settings  import  get_settings
from    util.plotting           import  get_title
from    util.rec_tools          import  get_tas, tas_rec
from    util.sc_dt              import  ts_to_ds


# usage: python period_vbp.py CLN23_FUT_CME 0.01 1:H 2023-06-16


MIN = 10 # sometimes a few trades print during a break... ignore these
FMT = "%Y-%m-%d %H:%M:%S"


if __name__ == "__main__":

    contract_id     = argv[1]
    title           = get_title(contract_id)
    multiplier, _   = get_settings(contract_id)
    resolution      = argv[3]
    start           = argv[4] if len(argv) > 4 else None
    end             = argv[5] if len(argv) > 5 else None
    recs            = get_tas(contract_id, multiplier, None, start, end)
    bars            = ohlcv(recs, resolution)
    fig             = go.Figure()

    if not recs:

        print("no records matched")

        exit()

    for bar in bars:

        selected = recs[bar[ohlcv_rec.i] : bar[ohlcv_rec.j]]

        if len(selected) > MIN:

            start_ds    = ts_to_ds(selected[0][tas_rec.timestamp], FMT)
            name        = f"{start_ds}"
            vbp_y       = vbp(selected)

            fig.add_trace(
                go.Violin(
                    {
                        "y":                vbp_y,
                        "opacity":          0.5,
                        "orientation":      "v",
                        "side":             "positive",
                        "points":           False,
                        "marker":           { "color": "#FF00FF" },
                        "name":             name
                    }
                )
            )

    fig.show()