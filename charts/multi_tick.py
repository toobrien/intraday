import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv, path

path.append(".")

from    util.aggregations       import  multi_tick_series
from    util.contract_settings  import  get_settings
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
    
    recs = multi_tick_series(recs, contract_ids)

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
        horizontal_spacing  = 0.05,
        vertical_spacing    = 0.05,
        row_heights         = row_heights,
        shared_yaxes        = True,
        subplot_titles      = tuple(titles)
    )

    fig.update_layout(height = 500 * len(contract_ids))

    size_norm = 2. * max(recs[contract_ids[0]]["z"]) / (40.**2)

    for i in range(len(contract_ids)):

        trace_recs = recs[contract_ids[i]]
        text       = [ f"{ts_to_ds(trace_recs['t'][i], FMT)}<br>{trace_recs['z'][i]}" for i in range(len(trace_recs["t"])) ]

        fig.add_trace(
            go.Scattergl(
                {
                    "name":         contract_ids[i],
                    "x":            trace_recs["x"],
                    "y":            trace_recs["y"],
                    "text":         text,
                    "marker_size":  trace_recs["z"],
                    "mode":         "markers",
                    "marker":       {
                                        "color":    trace_recs["c"],
                                        "sizemode": "area",
                                        "sizeref":  size_norm,
                                        "sizemin":  4 
                                    }
                }
            ),
            row = row,
            col = 2
        )

        hist = zip([ None for rec in trace_recs["y"] ], trace_recs["y"], trace_recs["z"])

        vbp_y = vbp(hist, precision)

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
                        "x":        trace_recs["x"],
                        "y":        trace_recs["log"],
                        "text":     text,
                        "mode":     "markers",
                        "marker":   { "color": "#0000FF" }
                    }
                ),
                row = row,
                col = 2
            )

            vbp_y = vbp(zip([ None for rec in trace_recs["y"] ], trace_recs["log"], trace_recs["z"]), 3)

            fig.add_trace(
                go.Histogram(
                    {
                        "y":            vbp_y,
                        "nbinsy":       int((max(vbp_y) - min(vbp_y)) / tick_size) + 1, 
                        "name":         f"{contract_ids[i]} log hist",
                        "opacity":      0.5,
                        "marker_color": "#0000FF"
                    }
                ),
                row = row,
                col = 1
            )

            row += 1

    fig.update_xaxes(matches = "x2", row = 1, col = 2)

    for i in range(1, len(contract_ids)):

        fig.update_xaxes(matches = "x2", row = 2 * i, col = 2)
        fig.update_xaxes(matches = "x2", row = 2 * i + 1, col = 2)

    fig.show()