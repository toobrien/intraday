from    bisect                  import  bisect_left
import  plotly.graph_objects    as      go
from    sys                     import  argv
from    util.aggregations       import  vbp
from    util.contract_settings  import  get_settings
from    util.plotting           import  get_title
from    util.rec_tools          import  get_tas, tas_rec


# usage: python custom_vbp.py CLQ23_FUT_CME 2023-06-12:2023-06-12T15 2023-06-12T15


FMT = "%Y-%m-%dT%H:%M:%S"


if __name__ == "__main__":

    contract_id     = argv[1]
    title           = get_title(contract_id)
    multiplier, _   = get_settings(contract_id)
    rngs            = argv[2:]

    for i in range(len(rngs)):

        rng = rngs[i]

        if ":" in rng:

            rngs[i] = tuple(rng.split(":"))
        
        else:

            rngs[i] = ( rng, None )

    start   = rngs[0][0]
    end     = rngs[-1][1]
    recs    = get_tas(contract_id, multiplier, FMT, start, None)
    comp    = lambda r: r[tas_rec.timestamp]
    fig     = go.Figure()

    if not recs:

        print("no records matched")

        exit()

    for rng in rngs:

        i = bisect_left(recs, rng[0], key = comp)
        j = bisect_left(recs, rng[1], key = comp) if rng[1] else len(recs)

        selected = recs[i:j]

        if selected:

    
            y = vbp(selected)

            fig.add_trace(
                go.Histogram(
                    {
                        "y":        y,
                        "nbinsy":   len(set(y)),
                        "name":     f"{rng[0]} - {rng[1] if rng[1] else 'end'}",
                        "opacity":  0.5
                    },
                )
            )

    fig.show()