from    collections             import  Counter
import  plotly.graph_objects    as      go
from    sys                     import  argv
from    typing                  import  List
from    util.features           import  vbp
from    util.rec_tools          import  get_tas, tas_rec


# usage: python trailing_vbp.py CLQ23_FUT_CME 0.01 1000 5000 2023-06-13 


COLOR   = "#CCCCCC"
FMT     = "%Y-%m-%dT%H:%M:%S"


def calc_value(recs: List):

    if len(recs) > 1:

        y       = vbp(recs)
        end     = recs[-1][tas_rec.timestamp]
        counts  = Counter(y)
        prices  = list(counts.keys())
        vals    = list(counts.values())
        lvn_qty = min(vals)
        poc_qty = max(vals)
        poc     = prices[vals.index(poc_qty)]
        lvn     = prices[vals.index(lvn_qty)]
        high    = max(prices)
        low     = min(prices)

        return {
            "high": high,
            "low":  low,
            "lvn":  lvn,
            "poc":  poc,
            "end":  end
        }


if __name__ == "__main__":

    contract_id = argv[1]
    title       = argv[1].split(".")[0] if "." in argv[1] else argv[1].split("_")[0]
    multiplier  = float(argv[2])
    interval    = int(argv[3])
    lookback    = int(argv[4])
    start       = argv[5] if len(argv) > 5 else None
    end         = argv[6] if len(argv) > 6 else None
    recs        = get_tas(contract_id, multiplier, FMT, start, end)
    i           = lookback
    high        = []
    low         = []
    lvn         = []
    poc         = []
    end         = []
    fig         = go.Figure()


    if not recs:

        print("no records matched")

        exit()

    while(i < len(recs)):

        selected = recs[i - lookback : i]
    
        res = calc_value(selected)

        high.append(res["high"])
        low.append(res["low"])
        lvn.append(res["lvn"])
        poc.append(res["poc"])
        end.append(res["end"])
        
        i = min(i + interval, len(recs))

    # add final value

    res = calc_value(recs[i - lookback : i])

    high.append(res["high"])
    low.append(res["low"])
    lvn.append(res["lvn"])
    poc.append(res["poc"])
    end.append(res["end"])

    for trace in [
        ( high, "#0000FF", "high" ),
        ( low, "#FF0000", "low" ),
        #( lvn, "#CCCCCC", "lvn" ),
        ( poc, "#FF00FF", "poc" ),
    ]:
        
        fig.add_trace(
            go.Scatter(
                {
                    "x":        end,
                    "y":        trace[0],
                    "line":     { "shape": "hv" },
                    "marker":   { "color": trace[1] },
                    "name":     trace[2]
                }
            )
        )

    fig.show()