import  plotly.graph_objects    as      go
from    statistics              import  mean, stdev
from    sys                     import  argv, path

path.append(".")

from    util.bar_tools          import  bar_rec, get_bars, get_sessions


# python charts/volume.py CL.c.0 2024-01-04


if __name__ == "__main__":

    contract_id     = argv[1]
    start           = f"{argv[4]}T0" if len(argv) > 4 else None
    end             = f"{argv[5]}T0" if len(argv) > 5 else None
    bars            = get_bars(contract_id, start, end)
    sessions        = get_sessions(bars, "00:00:00", "23:59:00")
    data            = {}

    for _, bars in sessions.items():

        for bar in bars:

            t = bar[bar_rec.time]

            if t not in data:

                data[t] = []
            
            data[t].append(bar[bar_rec.volume])

    for t, volumes in data.items():

        data[t] = mean(volumes)
    
    x = list(data.keys())
    y = list(data.values())

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            {
                "x": x,
                "y": y,
                "name": f"{contract_id} {start} - {end}"
            }
        )
    )

    fig.show()

    pass