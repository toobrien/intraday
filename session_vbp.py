from    bisect                  import  bisect_left
import  plotly.graph_objects    as      go
from    sys                     import  argv
from    util.aggregations       import  vbp
from    util.contract_settings  import  get_settings
from    util.plotting           import  get_title
from    util.rec_tools          import  get_tas, date_index, tas_rec


# usage: python session_vbp.py CLN23_FUT_CME 2023-06-08 2023-06-09 00.03 03.06 06.11:20 11:20.11:30 11:30.15 15.23:59:59

# (maximum 10 sessions)


FMT = "%Y-%m-%dT%H:%M:%S"
SESSION_COLORS = [
    "#3b719f",
    "#4f7fa9", 
    "#628db2", 
    "#769cbc",
    "#89aac5",
    "#9db8cf",
    "#b1c6d9",
    "#c4d4e2",
    "#d8e3ec",
    "#ebf1f5",
]


if __name__ == "__main__":

    contract_id     = argv[1]
    title           = get_title(contract_id)
    multiplier, _   = get_settings(contract_id)
    start           = argv[2]
    end             = argv[3]
    sessions        = argv[4:]
    recs            = get_tas(contract_id, multiplier, FMT, start, end)

    if not recs:

        print("no records matched")

        exit()

    comp    = lambda r: r[tas_rec.timestamp]
    traces  = []
    clr_i   = 0
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
                    go.Violin(
                        {
                            "y":            vbp_y,
                            "name":         f"{date:15}{session_rng[0]:15}{session_rng[1]:15}",
                            "orientation":  "v",
                            "side":         "positive",
                            "scalemode":    "count",
                            "marker":       { "color": SESSION_COLORS[clr_i % len(sessions)] },
                            "points":       False
                        }
                    )
                )
            
            clr_i += 1

    fig = go.Figure()

    for trace in traces:

        fig.add_trace(trace)

    fig.update_layout(title = title)
    fig.update_traces(width = 5)

    fig.show()

    

