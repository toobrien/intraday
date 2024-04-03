import  plotly.graph_objects    as      go
from    sys                     import  argv, path
from    time                    import  time

path.append(".")

from    util.aggregations       import  tick_series
from    util.contract_settings  import  get_settings
from    util.plotting           import  get_title
from    util.rec_tools          import  get_tas, get_precision, tas_rec
from    util.sc_dt              import  ts_to_ds


# python charts/sweep.py ESM24_FUT_CME 5 2024-03-27 2024-03-28


FMT = "%Y-%m-%dT%H:%M:%S.%f"


if __name__ == "__main__":

    t0                      = time()
    contract_id             = argv[1]
    min_len                 = int(argv[2])
    multiplier, tick_size   = get_settings(contract_id)
    precision               = get_precision(str(tick_size))
    title                   = get_title(contract_id)
    start                   = argv[3] if len(argv) > 3 else None
    end                     = argv[4] if len(argv) > 4 else None
    recs                    = get_tas(contract_id, multiplier, None, start, end)
    title                   = f"{title} {start} - {end}"
    groups                  = {}
    x, y, z, t, _           = tick_series(recs)
    traces                  = []
    xs                      = {}
    i                       = 0
    prev_price              = recs[0][tas_rec.price]
    prev_side               = recs[0][tas_rec.side]
    fig                     = go.Figure()

    for rec in recs:

        ts      = str(rec[tas_rec.timestamp])[:-3]
        price   = rec[tas_rec.price]
        side    = rec[tas_rec.side]

        if ts not in groups:

            groups[ts]  = []
            xs[ts]      = []

        groups[ts].append(rec)
        xs[ts].append(i)

        if price != prev_price or side != prev_side:

            prev_price  = price
            prev_side   = side
        
            i += 1


    for ts, group in groups.items():

        prices      = [ rec[tas_rec.price] for rec in group ]
        min_price   = min(prices)
        max_price   = max(prices)
        ticks       = (max_price - min_price) / tick_size

        if ticks >= min_len:

            text    = [ ts_to_ds(rec[tas_rec.timestamp], FMT) for rec in group ]
            qty     = sum([ rec[tas_rec.qty] for rec in group ])
            ts_full = ts_to_ds(group[0][tas_rec.timestamp], FMT)

            traces.append(
                {
                    "x":        xs[ts],
                    "y":        prices,
                    "text":     text,
                    "name":     ts_full,
                    "color":    "#FF00FF",
                    "mode":     "lines+markers"
                }
            )

            print(ts_full, f"{min_price:10}", f"{max_price:10}", f"{int(ticks):10}", f"{qty:10}")

    traces.append(
        {
            "x":    [ i for i in range(len(x)) ],
            "y":    y,
            "text": t,
            "name": contract_id,
            "color": "#0000FF",
            "mode": "lines"    
        }
    )

    for trace in traces:

        fig.add_trace(
            go.Scattergl(
                {
                    "x":        trace["x"],
                    "y":        trace["y"],
                    "text":     trace["text"],
                    "name":     trace["name"],
                    "marker":   { "color": trace["color"] },
                    "mode":     trace["mode"]
                }
            )
        )

    fig.update_layout(title_text = title)

    fig.show()

    print(f"{time() - t0:0.1f}s")

    pass