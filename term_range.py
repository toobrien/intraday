from    math                    import  log
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    util.rec_tools          import  get_precision, get_terms, n_days_ago, tas_rec


# usage: 
#           python term_range.py HOM23 0.0001 6 2023-04-01 2023-05-01
#           python term_range.py HEM23 0.001 8 30


def report(
    init_symbol:    str,
    multiplier:     float,
    n_terms:        int,
    start:          str = None,
    end:            str = None
):

    terms = get_terms(
        init_symbol,
        multiplier,
        n_terms,
        None,
        start,
        end
    )

    o       = []
    h       = []
    l       = []
    c       = []
    change  = []

    for _, recs in terms.items():

        o.append(recs[0][tas_rec.price])
        c.append(recs[-1][tas_rec.price])
        change.append(log(c[-1] / o[-1]) * 100)

        high    = float("-inf")
        low     = float("inf")

        for rec in recs:

            price   = rec[tas_rec.price]
            high    = price if price > high else high
            low     = price if price < low else low
        
        h.append(high)
        l.append(low)

    terms = list(terms.keys())

    fig = make_subplots(rows = 2, cols = 1)

    fig.update_layout( title = { "text": f"{init_symbol[:-3]} {start} - {end}" })

    traces = [
        ( o, "open", "#ca2c92", 1, "markers" ),
        ( h, "high", "#0000FF", 1, "markers+lines" ),
        ( l, "low", "#FF0000", 1, "markers+lines" ),
        ( c, "close", "#ca2c92", 1, "markers+lines" ),
        ( change, "change", "#808080", 2, "markers+lines" )
    ]

    for trace in traces:

        fig.add_trace(
            go.Scatter(
                {
                    "x":        terms,
                    "y":        trace[0],
                    "mode":     trace[4],
                    "marker":   { "color": trace[2] },
                    "name":     trace[1]
                }
            ),
            row = trace[3],
            col = 1
        )

    fig.show()


if __name__ == "__main__":

    init_symbol = argv[1]
    multiplier  = argv[2]
    n_terms     = int(argv[3])

    if len(argv) == 5:

        start   = n_days_ago(int(argv[4]))
        end     = n_days_ago(-1)
    
    else:

        start       = argv[4]
        end         = argv[5]

    report(
        init_symbol,
        float(multiplier),
        n_terms,
        start,
        end
    )