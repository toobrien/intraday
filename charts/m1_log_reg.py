from    operator                import  itemgetter
from    math                    import  e, log
import  plotly.graph_objects    as      go
from    sys                     import  argv, path

path.append(".")

from    util.aggregations       import  multi_tick_series
from    util.contract_settings  import  get_settings
from    util.rec_tools          import  get_tas, get_precision
from    util.sc_dt              import  ts_to_ds


# python charts/m1_log_reg.py HOZ23_FUT_CME:HOH24_FUT_CME:HOM24_FUT_CME:HOU24_FUT_CME:HOZ24_FUT_CME 2023-10-23


FMT = "%Y-%m-%dT%H:%M:%S.%f"


if __name__ == "__main__":

    contract_ids            = argv[1].split(":")
    multiplier, tick_size   = get_settings(contract_ids[0])
    precision               = get_precision(str(tick_size))
    start                   = argv[2] if len(argv) > 2 else None
    end                     = argv[3] if len(argv) > 3 else None
    title                   = f"{contract_ids[0]}    {start} - {end}"
    
    recs = [ 
            get_tas(contract_id, multiplier, None, start, end)
            for contract_id in contract_ids
        ]
    
    recs = multi_tick_series(recs, contract_ids)

    size_norm = 2. * max(recs[contract_ids[0]]["z"]) / (40.**2)

    m1_id   = contract_ids[0]
    m1_0    = recs[m1_id]["y"][0]

    fig = go.Figure()

    fig.update_layout(title_text = title)

    for contract_id in contract_ids[1:]:

        y, z, t, c, logs    = itemgetter("y", "z", "t", "c", "log")(recs[contract_id])
        text                = [ f"{ts_to_ds(t[i], FMT)}<br>{y[i]:0.{precision}f}" for i in range(len(t)) ]
        y_                  = [ log(y_ / m1_0) for y_ in y ]
        m1_y                = [ y[i] / e**logs[i] for i in range(len(logs)) ]
        x_                  = [ log(m1_i / m1_0) for m1_i in m1_y ]

        fig.add_trace(
            go.Scattergl(
                {
                    "x":            x_,
                    "y":            y_,
                    "text":         text,
                    "mode":         "markers",
                    "marker_size":  z,
                    "marker":       {
                                        "sizemode": "area",
                                        "sizeref":  size_norm,
                                        "sizemin":  4
                                    },
                    "name":         contract_id
                }
            )
        )

    fig.show()