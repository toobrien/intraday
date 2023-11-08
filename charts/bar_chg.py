from    math                    import  log
import  plotly.graph_objects    as      go
from    sys                     import  argv, path

path.append(".")

from    util.bar_tools         import   bar_rec, get_bars


# python charts/bar_chg.py HOZ23_FUT_CME:RBZ23_FUT_CME:CLZ23_FUT_CME 2023-11-08T0


if __name__ == "__main__":

    contract_ids    = argv[1].split(":")
    start           = argv[2] if len(argv) > 2 else None
    end             = argv[3] if len(argv) > 3 else None
    recs            = { 
                        contract_id: get_bars(contract_id, start, end)
                        for contract_id in contract_ids
                    }
    fig             = go.Figure()

    fig.update_layout(title = "\t".join(contract_ids) + f"\t{start} - {end}")

    for contract_id in contract_ids:

        bars    = recs[contract_id]
        p0      = log(bars[0][bar_rec.last])
        y       = [ log(bar[bar_rec.last]) - p0 for bar in bars ]
        x       = [ f"{bar[bar_rec.date]}T{bar[bar_rec.time]}" for bar in bars ]
        t       = [ str(bar[bar_rec.last]) for bar in bars ]

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    x,
                    "y":    y,
                    "text": t,
                    "name": contract_id
                }
            )
        )

    fig.show()