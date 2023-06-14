from    collections             import  Counter
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    typing                  import  List
from    util.features           import  vbp
from    util.rec_tools          import  get_tas, tas_rec


# usage: python trailing_vbp.py CLQ23_FUT_CME 0.01 1000 5000 2023-06-13 


COLOR   = "#CCCCCC"
FMT     = "%Y-%m-%dT%H:%M:%S"
VAL_HI  = 0.85
VAL_LO  = 0.15


def calc_value(recs: List):

    if len(recs) > 1:

        y       = sorted(vbp(recs))
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
        val_hi  = y[int(len(y) * VAL_HI)]
        val_lo  = y[int(len(y) * VAL_LO)]

        return {
            "high":     high,
            "low":      low,
            "lvn":      lvn,
            "poc":      poc,
            "end":      end,
            "val_hi":   val_hi,
            "val_lo":   val_lo
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
    val_hi      = []
    val_lo      = []
    end         = []
    fig         = make_subplots(
        rows                = 1,
        cols                = 2,
        column_widths       = [ 0.1, 0.9 ],
        shared_yaxes        = True,
        horizontal_spacing  = 0.0,
        subplot_titles      = ( "", f"{title} {interval}:{lookback}" ) 
    )

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
        val_hi.append(res["val_hi"])
        val_lo.append(res["val_lo"])
        
        i = min(i + interval, len(recs))

    # add final value

    res = calc_value(recs[i - lookback : i])

    high.append(res["high"])
    low.append(res["low"])
    lvn.append(res["lvn"])
    poc.append(res["poc"])
    val_hi.append(res["val_hi"])
    val_lo.append(res["val_lo"])
    end.append(res["end"])

    vbp_y = vbp(recs)

    fig.add_trace(
        go.Histogram(
            {
                "name":     "vbp",
                "y":        vbp_y,
                "nbinsy":   len(set(vbp_y)),
                "opacity":  0.3
            }
        ),
        row = 1,
        col = 1
    ) 

    for trace in [
        { 
            "x":        end,
            "y":        high,
            "line":     { "shape": "hv" }, 
            "marker":   { "color": "#CCCCCC" },
            "name":     "high"
        },
        {
            "x":        end,
            "y":        low,
            "fill":     "tonexty",
            "line":     { "shape": "hv" },
            "marker":   { "color": "#CCCCCC" },
            "name":     "low"
        },
        { 
            "x":        end,
            "y":        val_hi,
            "line":     { "shape": "hv" }, 
            "marker":   { "color": "#5A5A5A" },
            "name":     "val_hi"
        },
        {
            "x":        end,
            "y":        val_lo,
            "fill":     "tonexty",
            "line":     { "shape": "hv" },
            "marker":   { "color": "#5A5A5A" },
            "name":     "val_lo"
        },
        {
            "x":        end,
            "y":        poc,
            "line":     { "shape": "hv" },
            "marker":   { "color": "#FF00FF" },
            "name":     "poc"
        }
    ]:
        
        fig.add_trace(
            go.Scatter(trace),
            row = 1,
            col = 2
        )

    fig.show()