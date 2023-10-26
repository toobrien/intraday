from    operator                import  itemgetter
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv, path

path.append(".")

from    util.aggregations       import  multi_tick_series
from    util.contract_settings  import  get_settings
from    util.aggregations       import  vbp
from    util.rec_tools          import  get_tas, get_precision
from    util.sc_dt              import  ts_to_ds


# python charts/multi_tick_log.py HO###_FUT_CME:Z23:H24:M24:U24:Z24 2023-10-25


FMT = "%Y-%m-%dT%H:%M:%S.%f"


if __name__ == "__main__":

    contract_ids            = argv[1].split(":")
    contract_ids            = [ contract_ids[0].replace("###", MYY) for MYY in contract_ids[1:] ]
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

    fig = make_subplots(
            rows                = 2,
            cols                = 1,
            vertical_spacing    = 0.05,
            shared_xaxes        = True
        )
    
    fig.update_layout(title_text = title)

    for contract_id in contract_ids:

        x, y, z, t, c, log = itemgetter("x", "y", "z", "t", "c", "log")(recs[contract_id])

        diff = [ log[i] - log[0] for i in range(len(log)) ]

        text = [
            f"{ts_to_ds(t[i], FMT)}<br>{log[i]:0.4f}<br>{y[i]:0.{precision}f}<br>{z[i]}"
            for i in range(len(t))
        ]

        fig.add_trace(
            go.Scattergl(
                {
                    "x":            x,
                    "y":            diff,
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
            ),
            row = 2 if contract_id != contract_ids[0] else 1,
            col = 1
        )

    fig.show()