import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    util.aggregations       import  vbp
from    util.rec_tools          import  get_tas, tas_rec


# usage:
#
#   - python trade_vbp.py CLQ23_FUT_CME 0.01 1000 2023-06-15


FMT     = "%Y-%m-%dT%H:%M:%S"

if __name__ == "__main__":

    contract_id = argv[1]
    title       = argv[1].split(".")[0] if "." in argv[1] else argv[1].split("_")[0]
    multiplier  = float(argv[2])
    interval    = int(argv[3])
    start       = argv[4] if len(argv) > 4 else None
    end         = argv[5] if len(argv) > 5 else None
    recs        = get_tas(contract_id, multiplier, FMT, start, end)
    fig         = make_subplots(
        rows                = 1,
        cols                = 2,
        column_widths       = [ 0.1, 0.9 ],
        shared_yaxes        = True,
        horizontal_spacing  = 0.0,
        subplot_titles      = ( "", f"{title} {interval}" ) 
    )

    if not recs:

        print("no records matched")

        exit()

    i = interval

    while(i < len(recs)):

        selected    = recs[i - interval : i]
        vbp_y       = vbp(selected)
        start       = selected[0][tas_rec.timestamp]
        end         = selected[-1][tas_rec.timestamp]

        fig.add_trace(
            go.Violin(
                {
                    "y":            vbp_y,
                    "opacity":      0.5,
                    "orientation":  "v",
                    "side":         "positive",
                    "points":       False,
                    "marker":       { "color": "#0000FF" },
                    "width":        1.5,
                    "name":     f"{start} - {end}"
                }
            ),
            row = 1,
            col = 2
        )
    
        i += interval

    # add final value

    i           -= interval
    selected    =  recs[i:]
    vbp_y       =  vbp(selected)
    start       =  selected[0][tas_rec.timestamp]
    end         =  selected[-1][tas_rec.timestamp]

    fig.add_trace(
        go.Violin(
            {
                "y":            vbp_y,
                "opacity":      0.5,
                "orientation":  "v",
                "side":         "positive",
                "points":       False,
                "marker":       { "color": "#FF0000" },
                "width":        1.5,
                "name":         f"{start} - {end}"
            }
        ),
        row = 1,
        col = 2
    )
    
    vbp_y = vbp(recs)

    fig.add_trace(
        go.Violin(
            {
                "y":            vbp_y,
                "orientation":  "v",
                "side":         "positive",
                "points":       False,
                "opacity":      0.5,
                "name":         "vbp",
            }
        )
    )

    fig.show()