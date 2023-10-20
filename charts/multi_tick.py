from    math                    import  log
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv, path

path.append(".")

from    util.contract_settings  import  get_settings
from    util.parsers            import  tas_rec
from    util.aggregations       import  vbp
from    util.rec_tools          import  get_tas, get_precision
from    util.sc_dt              import  ts_to_ds


# python charts/multi_tick.py HOZ23_FUT_CME:HOZ24_FUT_CME 2023-10-19


FMT = "%Y-%m-%dT%H:%M:%S.%f"


if __name__ == "__main__":

    contract_ids            = argv[1].split(":")
    multiplier, tick_size   = get_settings(contract_ids[0])
    precision               = get_precision(str(tick_size))
    start                   = argv[2] if len(argv) > 2 else None
    end                     = argv[3] if len(argv) > 3 else None
    title                   = f"{'    '.join(contract_ids)}    {start} - {end}"
    
    recs = [ 
            get_tas(contract_id, multiplier, None, start, end)
            for contract_id in contract_ids
        ]
    
    recs = [
        [ list(rec) for rec in recs[i] ]
        for i in range(len(recs))
    ]

    for i in range(len(recs)):

        series      = recs[i]
        contract_id = contract_ids[i]

        for j in range(len(series)):

            series[j].append(contract_id)

    recs = [
        rec
        for series in recs
        for rec in series
    ]

    prev_m1 = recs[0][tas_rec.price]

    recs = sorted(recs, key = lambda r: r[tas_rec.timestamp])

    agg_recs = []
    tick     = recs[0][tas_rec.qty]
    prev_rec = [ val for val in recs[0] ]
    prev_rec.append(tick)

    for next_rec in recs[1:]:

        if  next_rec[tas_rec.price] == prev_rec[tas_rec.price]  and \
            next_rec[tas_rec.side]  == prev_rec[tas_rec.side]   and \
            next_rec[-1]            == prev_rec[-2]:            # contract_id

            prev_rec[tas_rec.qty]   += next_rec[tas_rec.qty]
        
        else:

            agg_recs.append(prev_rec)

            prev_rec = [ val for val in next_rec ]
            
            prev_rec.append(tick)
            
        tick            += next_rec[tas_rec.qty]
        prev_rec[-1]    =  tick

    agg_recs.append(prev_rec)

    for rec in agg_recs:
    
        if rec[-2] == contract_ids[0]:

            prev_m1 = rec[tas_rec.price]

        else:

            rec.append(log(rec[tas_rec.price] / prev_m1))

    recs = [
        [ 
            rec
            for rec in agg_recs
            if contract_id in rec
        ]
        for contract_id in contract_ids
    ]

    primary_row_height      = 1 / len(contract_ids)
    sub_row_height          = primary_row_height * 0.25
    secondary_row_height    = primary_row_height - sub_row_height
    row_heights             = [ primary_row_height ]
    titles                  = [ "", contract_ids[0] ]
    row                     = 1

    for contract_id in contract_ids[1:]:

        row_heights.append(secondary_row_height)
        row_heights.append(sub_row_height)

        titles.append("")
        titles.append(contract_id)
        titles.append("")

    fig = make_subplots(
        rows                = 2 * len(contract_ids) - 1,
        cols                = 2,
        column_widths       = [ 0.1, 0.9 ],
        horizontal_spacing  = 0.03,
        vertical_spacing    = 0.03,
        row_heights         = row_heights,
        shared_xaxes        = True,
        shared_yaxes        = True,
        subplot_titles      = tuple(titles)
    )

    size_norm = 2. * max([ rec[tas_rec.qty] for rec in recs[0] ]) / (40.**2)

    for i in range(len(contract_ids)):

        trace_recs  = recs[i]
        tick_idx    = -1 if i == 0 else -2
        x           = [ rec[tick_idx] for rec in trace_recs ]
        size        = [ rec[tas_rec.qty] for rec in trace_recs ]
        color       = [ "#FF0000" if rec[tas_rec.side] == 0 else "#0000FF" for rec in trace_recs ]
        text        = [ ts_to_ds(rec[tas_rec.timestamp], FMT) for rec in trace_recs ]

        fig.add_trace(
            go.Scattergl(
                {
                    "name":         contract_ids[i],
                    "x":            x,
                    "y":            [ rec[tas_rec.price] for rec in trace_recs ],
                    "text":         text,
                    "marker_size":  size,
                    "mode":         "markers",
                    "marker":       {
                                        "color":    color,
                                        "sizemode": "area",
                                        "sizeref":  size_norm,
                                        "sizemin":  4 
                                    }
                }
            ),
            row = row,
            col = 2
        )

        vbp_y = vbp(trace_recs, precision)

        fig.add_trace(
            go.Histogram(
                {
                    "y":            vbp_y,
                    "nbinsy":       int((max(vbp_y) - min(vbp_y)) / tick_size) + 1, 
                    "name":         contract_ids[i],
                    "opacity":      0.5,
                    "marker_color": "#0000FF"
                }
            ),
            row = row,
            col = 1
        ) 

        row += 1

        if i != 0:

            fig.add_trace(
                go.Scattergl(
                    {
                        "name":     f"{contract_ids[i]} log",
                        "x":        [ rec[tick_idx] for rec in trace_recs ],
                        "y":        [ rec[-1] for rec in trace_recs ],
                        "text":     text,
                        "mode":     "markers",
                        "marker":   { "color": "#0000FF" }
                    }
                ),
                row = row,
                col = 2
            )

            row += 1

    fig.show()

    pass