from    bisect                  import  bisect_left
import  plotly.graph_objects    as      go
from    sys                     import  argv, path

path.append(".")

from util.aggregations          import tick_series
from util.contract_settings     import get_settings
from util.rec_tools             import get_tas, get_precision
from util.sc_dt                 import ts_to_ds


FMT = "%Y-%m-%dT%H:%M:%S.%f"


# python research/sweeps/tts.py ESM24_FUT_CME 5 500 2024-04-30T06 2024-04-30T13:00:00


if __name__ == "__main__":

    contract_id             = argv[1]
    min_offset              = int(argv[2])
    t_lag                   = int(argv[3])
    start                   = argv[4] if len(argv) > 4 else None
    end                     = argv[5] if len(argv) > 5 else None
    multiplier, tick_size   = get_settings(contract_id)
    precision               = get_precision(str(tick_size))
    recs                    = get_tas(contract_id, multiplier, None, start, end)
    x, y, z, t, _           = tick_series(recs)
    fig                     = go.Figure()
    
    offsets     = []
    prev_offset = 0
    up_cross    = 0
    dn_cross    = 0
    t           = [ t_[0] // 1000 for t_ in t ]

    for i in range(len(t)):

        t_          = t[i] - t_lag
        lag         = bisect_left(t, t_)
        y_cur       = y[i]
        y_lag       = y[lag]
        cur_offset  = y - y_lag
        
        offsets.append(cur_offset)

        if cur_offset <= -min_offset and prev_offset > -min_offset:

            dn_cross += 1

        elif cur_offset >= min_offset and prev_offset < min_offset:

            up_cross += 1

    print(f"up_cross: {up_cross}")
    print(f"dn_cross: {dn_cross}")

    fig.add_trace(
        go.Scattergl(
            {
                "x":        [ i for i in range(len(offsets))],
                "y":        offsets,
                "text":     [ f"{ts_to_ds(t[i], FMT)}<br>{y[i]}" for i in range(len(t)) ],
                "mode":     "lines",
                "marker":   { "color": "#0000FF" },
                "name":     f"offset"
            }
        )
    )

    fig.add_hline(y = min_offset)
    fig.add_hline(y = -min_offset)

    fig.show()

    pass