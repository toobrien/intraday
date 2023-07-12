from    bisect                  import  bisect_left
import  plotly.graph_objects    as      go
from    sys                     import  argv
from    util.aggregations       import  ohlcv, ohlcv_rec
from    util.contract_settings  import  get_settings
from    util.rec_tools          import  date_index, get_tas, n_days_ago, tas_rec
from    util.sc_dt              import  ds_to_ts


# python season.py ESU23_FUT_CME 30 1:M 12.13:00:02


FMT = "%Y-%m-%dT%H:%M:%S"


if __name__ == "__main__":

    contract_id     = argv[1]
    days_ago        = int(argv[2])
    resolution      = argv[3]
    season          = argv[4].split(".")
    multiplier, _   = get_settings(contract_id)
    start           = n_days_ago(days_ago)
    recs            = get_tas(contract_id, multiplier, FMT, start)

    if not recs:

        print("no records matched")

        exit()

    idx     = date_index(contract_id, recs)
    comp    = lambda r: r[tas_rec.timestamp]
    fig     = go.Figure()

    for date, rng in idx.items():

        selected        = recs[rng[0] : rng[1]]
        season_start    = f"{date}T{season[0]}"
        season_end      = f"{date}T{season[1]}"
        i               = bisect_left(selected, season_start, key = comp)
        j               = bisect_left(selected, season_end, key = comp)
        recs_           = [ 
                            (
                                ds_to_ts(rec[tas_rec.timestamp]),
                                rec[tas_rec.price],
                                rec[tas_rec.qty],
                                rec[tas_rec.side]
                            ) 
                            for rec in selected[i : j]
                        ] # ohlcv requires ts, but date_index requires ds... need to rewrite this whole thing to use bar data txt file
 
        if recs_:

            base = recs_[0][tas_rec.price]
            bars = ohlcv(recs_, resolution, FMT)

            fig.add_trace(
                go.Scattergl(
                    {
                        "x":    [ bar[ohlcv_rec.ts].split("T")[1] for bar in bars ],
                        "y":    [ bar[ohlcv_rec.c] - base for bar in bars ],
                        "name": date
                    }
                )
            )

    fig.show()