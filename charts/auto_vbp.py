import  plotly.graph_objects    as      go
from    statistics              import  mode
from    sys                     import  argv, path

path.append(".")

from    util.aggregations       import  vbp
from    util.contract_settings  import  get_settings
from    util.plotting           import  get_title
from    util.rec_tools          import  get_tas, tas_rec


# usage: python charts/auto_vbp.py CLQ23_FUT_CME 0.20 1000 2023-06-16

FMT     = "%Y-%m-%dT%H:%M:%S"

if __name__ == "__main__":

    contract_id     = argv[1]
    title           = get_title(contract_id)
    multiplier, _   = get_settings(contract_id)
    max_std         = float(argv[2])
    interval        = int(argv[3])
    start           = argv[4] if len(argv) > 4 else None
    end             = argv[5] if len(argv) > 5 else None
    recs            = get_tas(contract_id, multiplier, FMT, start, end)
    fig             = go.Figure()
    long_poc        = None
    short_poc       = None
    i               = 0
    j               = interval
    values          = []

    if not recs:

        print("no records matched")

        exit()

    while j < len(recs):

        long_hist   = vbp(recs[i:j])
        short_hist  = vbp(recs[j - interval: j])
        long_poc    = mode(long_hist)
        short_poc   = mode(short_hist)


        if abs(short_poc - long_poc) > max_std:

            # new value, record old

            values.append((i, j - interval))

            i = j - interval
        
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