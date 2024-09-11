from    bisect                  import  bisect_left
import  polars                  as      pl
import  plotly.graph_objects    as      go
import  numpy                   as      np
from    sys                     import  argv, path
from    time                    import  time
from    typing                  import  List

path.append("./screens/reg/")

from    util        import  get_dfs


pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_rows(-1)


# python screens/reg/test.py rty_emd - RTY:1 EMD:1 06-14 0


def daily_demeaned(dfs: List[pl.DataFrame]):

    fig = go.Figure()

    for date, df in dfs.items():

        ts          = np.array(df["ts"])
        i           = bisect_left(ts, f"{date}T{i_ts}")
        j           = bisect_left(ts, f"{date}T{j_ts}")
        ts          = ts[i:j]
        x           = np.array(df[x_sym])[i:j]
        y           = np.array(df[y_sym])[i:j]
        spread      = y * float(y_mult) - x * float(x_mult)
        demeaned    = spread - np.mean(spread)
        ts          = [ t.split("T")[1] for t in ts ]

        fig.add_trace(
            go.Scattergl(
                {
                    "x":    ts,
                    "y":    demeaned,
                    "name": date,
                    "text": [ f"{i:0.2f}" for i in spread ]
                }
            )
        )        

    fig.add_hline(y = 0, line_color = "#FF0000")
    fig.show()


def continuous(dfs: List[pl.DataFrame]):

    fig         = go.Figure()
    interval    = 60
    Y           = []
    T           = []
    i_          = 0

    for date, df in dfs.items():

        ts          = df["ts"]
        i           = bisect_left(ts, f"{date}T{i_ts}")
        j           = bisect_left(ts, f"{date}T{j_ts}")
        ts          = ts[i:j]
        x           = np.array(df[x_sym])[i:j]
        y           = np.array(df[y_sym])[i:j]
        spread      = y * float(y_mult) - x * float(x_mult)
        rng         = range(0, len(spread), interval)
        spread      = [ spread[i] for i in rng ]
        text        = [ ts[i] for i in rng ]
        i_          = i_ + len(spread)
        
        fig.add_vline(
            x               = i_, 
            annotation_text = ts[0].split("T")[0], 
            line            = { "color": "rgba(255, 0, 255, 0.5)" }
        )

        Y.extend(spread)
        T.extend(text)

    X = [ i for i in range(len(Y)) ]

    fig.add_trace(
        go.Scattergl(
            {
                "x":    X,
                "y":    Y,
                "name": "spread",
                "text": T
            }
        )
    )

    fig.show()


if __name__ == "__main__":

    t0              = time()
    folder          = argv[1]
    limit           = -int(argv[2]) if argv[2] != "-" else 0
    x_sym, x_mult   = argv[3].split(":")
    y_sym, y_mult   = argv[4].split(":")
    i_ts, j_ts      = argv[5].split("-")
    mode            = int(argv[6])
    dfs             = get_dfs(folder, limit, True)
    
    modes = {
        0: daily_demeaned,
        1: continuous
    }

    modes[mode](dfs)

    print(f"{time() - t0:0.1f}s")