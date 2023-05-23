import  plotly.graph_objects    as      go
from    statistics              import  mean
from    sys                     import  argv
from    typing                  import  List
from    util.parsers            import  tas_rec
from    util.rec_tools          import  get_tas


# usage: python liquidity_chart.py CLN23_FUT_CME 0.01 2023-05-22


FMT = "%Y-%m-%dT%H:%M:%S.%f"


def get_liq(recs: List):

    liq = {}

    prev_price = recs[0][tas_rec.price]

    for rec in recs:

        price   = rec[tas_rec.price]
        qty     = rec[tas_rec.qty]

        if price not in liq:

            liq[price] = []

        if price == prev_price:

            liq[price][-1] += qty
        
        else:

            liq[price].append(qty)
            
            prev_price = price

    pass

    return liq


def add_traces(fig: go.Figure, row = None, col = None):

    pass


if __name__ == "__main__":

    contract_id = argv[1]
    fig_title   = argv[1].split(".") if "." in argv[1] else argv[1].split("_")[0]
    multiplier  = float(argv[2])
    start       = argv[3] if len(argv) > 3 else None
    end         = argv[4] if len(argv) > 4 else None

    recs = get_tas(contract_id, multiplier, FMT, start, end)

    if not recs:

        print("no records matched")
        
        exit()

    bid_trades  = [ rec for rec in recs if not rec[tas_rec.side] ]
    ask_trades  = [ rec for rec in recs if rec[tas_rec.side] ]
    bid_liq     = get_liq(bid_trades)
    ask_liq     = get_liq(ask_trades)
    combined    = {}

    for price in bid_liq:

        try:
        
            combined[price] = bid_liq[price] + ask_liq[price]

        except:

            pass

    fig = go.Figure()
    
    fig.update_layout(
        barmode     = "stack",
        title       = { "text": fig_title }
    )

    for trace_data in [ 
        ( bid_liq,  "bid_liq",  "#0000FF" ), 
        ( ask_liq,  "ask_liq",  "#FF0000" ),
        ( combined, "combined", "#cccccc")
    ]:

        liq     = trace_data[0]
        title   = trace_data[1]
        color   = trace_data[2]

        x = sorted(list(liq.keys()))
        y = [ mean(liq[price]) for price in liq ]

        fig.add_trace(
            go.Bar(
                x               = x,
                y               = y,
                text            = [ f"{val:0.1f}" for val in y ],
                name            = title,
                marker_color    = color
            )
        )

    fig.show()