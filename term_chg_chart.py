from    math                    import  log
import  plotly.graph_objects    as      go
from    sys                     import  argv
from    util.tas_tools          import  get_ohlcv, get_precision, get_terms, ohlcv_rec



# usage: python term_chg_chart.py NGM23 0.001 6 2023-03-27T00:00:00 2023-03-28T00:00:00 1:H 1


FMT = "%Y-%m-%dT%H:%M:%S.%f"


if __name__ == "__main__":

    init_symbol             = argv[1]
    multiplier              = argv[2]
    precision               = get_precision(multiplier)
    multiplier              = float(multiplier)
    n_months                = int(argv[3])
    start                   = argv[4]
    end                     = argv[5]
    resolution              = argv[6]
    trim_empty              = int(argv[7])

    terms = get_terms(
                init_symbol, 
                multiplier, 
                n_months,
                None,       # dont use datestrings when getting bar data
                start, 
                end
            )

    fig = go.Figure()

    for contract_id, recs in terms.items():

        bars = get_ohlcv(
                recs, 
                resolution,
                start,
                end,
                FMT, 
                trim_empty
            )

        y = [ 0 for _ in bars ]

        for i in range(1, len(bars)):

            y[i] = log(bars[i][ohlcv_rec.c] / bars[i - 1][ohlcv_rec.c]) * 100
            y[i] = y[i] + y[i - 1]

        x       = [ bar[ohlcv_rec.ts] for bar in bars ]
        text    = [ bar[ohlcv_rec.v]  for bar in bars ]

        fig.add_trace(
            go.Scattergl(
                {
                    "name":         contract_id,
                    "x":            x,
                    "y":            y,
                    "text":         text,
                    "yhoverformat": "0.2f",
                    "connectgaps":  False if trim_empty else True # doesn't work, need to keep bars but set value to NaN
                }
            )
        )

    fig.show()


