import  plotly.graph_objects    as      go
from    statistics              import  mode
from    sys                     import  argv
from    util.features           import  vbp
from    util.rec_tools          import  get_tas, tas_rec


# usage: python auto_vbp.py CLQ23_FUT_CME 0.01 0.20 1000 2023-06-16

FMT     = "%Y-%m-%dT%H:%M:%S"

if __name__ == "__main__":

    contract_id = argv[1]
    title       = argv[1].split(".")[0] if "." in argv[1] else argv[1].split("_")[0]
    multiplier  = float(argv[2])
    max_std     = float(argv[3])
    interval    = int(argv[4])
    start       = argv[5] if len(argv) > 5 else None
    end         = argv[6] if len(argv) > 6 else None
    recs        = get_tas(contract_id, multiplier, FMT, start, end)
    fig         = go.Figure()
    prev_poc    = None
    i           = 0
    j           = interval
    values      = []

    if not recs:

        print("no records matched")

        exit()

    while j < len(recs):

        hist    = vbp(recs[i:j])
        poc     = mode(hist)

        if not prev_poc:

            prev_poc = poc
        
        elif abs(poc - prev_poc) > max_std:

            # new value, record old

            values.append((i, j))

            i = j
        
        # else: continue adding records to current value

        j += interval
    
    # add most recent

    values.append((i, len(recs)))

    for value in values:

        i, j    = value
        hist    = vbp(recs[i:j])
        start   = recs[i][tas_rec.timestamp]
        end     = recs[j - 1][tas_rec.timestamp]

        fig.add_trace(
            go.Violin(
                {
                    "y":            hist,
                    "opacity":      0.5,
                    "orientation":  "v",
                    "side":         "positive",
                    "points":       False,
                    "marker":       { "color": "#0000FF" },
                    "name":         f"{start} - {end}"
                }
            )
        )
    
    fig.show()