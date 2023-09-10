from    math                    import  log
import  plotly.graph_objects    as      go
from    sys                     import  argv, path

path.append(".")

from    util.contract_settings  import  get_settings
from    util.aggregations       import  ohlcv, ohlcv_rec
from    util.rec_tools          import  get_precision
from    util.term_structure     import  get_terms


# python charts/term_chg_chart.py NGM23 6 2023-03-27T00:00:00 2023-03-28T00:00:00 1:H 1


FMT = "%Y-%m-%dT%H:%M:%S.%f"


if __name__ == "__main__":

    init_symbol     = argv[1]
    multiplier, _   = get_settings(init_symbol)
    precision       = get_precision(multiplier)
    multiplier      = float(multiplier)
    n_months        = int(argv[2])
    start           = argv[3]
    end             = argv[4]
    resolution      = argv[5]
    trim_empty      = int(argv[6])

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

        bars = ohlcv(
                recs, 
                resolution,
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


