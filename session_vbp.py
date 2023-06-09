from    bisect                  import  bisect_left
import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    sys                     import  argv
from    util.features           import  delta, vbp
from    util.rec_tools          import  get_tas, date_index, tas_rec
from    util.sc_dt              import  ts_to_ds


# usage: python session_vbp.py CLN23_FUT_CME 0.01 2023-06-08 2023-06-09 00.03 03.06 06.11:30 11:30.15 15.23:59:59


FMT = "%Y-%m-%dT%H:%M:%S"


if __name__ == "__main__":

    contract_id = argv[1]
    title       = argv[1].split(".")[0] if "." in argv[1] else argv[1].split("_")[0]
    multiplier  = float(argv[2])
    start       = argv[3]
    end         = argv[4]
    sessions    = argv[5:]
    recs        = get_tas(contract_id, multiplier, FMT, start, end)

    if not recs:

        print("no records matched")

        exit()

    comp    = lambda r: r[tas_rec.timestamp]
    traces  = []
    col     = 1
    idx     = date_index(contract_id, recs)

    for date, day_rng in idx.items():

        selected = recs[day_rng[0] : day_rng[1]]

        for session in sessions:

            session_rng = session.split(".")

            session_start   = f"{date}T{session_rng[0]}"
            session_end     = f"{date}T{session_rng[1]}"
            session_i       = bisect_left(selected, session_start, key = comp)
            session_j       = bisect_left(selected, session_end, key = comp)
            session_recs    = selected[session_i : session_j]

            if session_recs:

                vbp_y = vbp(session_recs)

                traces.append(
                    (
                        go.Histogram(
                            {
                                "y":        vbp_y,
                                "nbinsy":   len(set(vbp_y)),
                                "name":     f"{session_start} - {session_end}",
                                "opacity":  0.3
                            },
                        ),
                        col
                    )
                )

                col += 1

    fig = make_subplots(
        rows                = 1,
        cols                = col - 1,
        shared_yaxes        = True,
        horizontal_spacing  = 0.0,
        vertical_spacing    = 0.025,
        subplot_titles      = ( title, "" )
    )

    for trace in traces:

        fig.add_trace(
            trace[0],
            row = 1,
            col = trace[1]
        )

    fig.show()

    

