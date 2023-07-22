import  plotly.graph_objects    as      go
from    plotly.subplots         import  make_subplots
from    statistics              import  mean
from    sys                     import  argv, path
path.append(".")
from    util.bar_tools          import  bar_rec, get_bars, get_sessions
from    util.contract_settings  import  get_settings
from    util.rec_tools          import  get_precision


# python research/fly_seq.py ZCU23_FUT_CME 11:19:00 17.17:15 2023-03-01 2023-07-14


if __name__ == "__main__":

    contract_id     = argv[1]
    prev_close      = argv[2]
    open_range      = argv[3].split(".")
    start           = f"{argv[4]}T0" if len(argv) > 4 else None
    end             = f"{argv[5]}T0" if len(argv) > 5 else None
    _, tick_size    = get_settings(contract_id)
    precision       = get_precision(str(tick_size))
    bars            = get_bars(contract_id, start, end)
    title           = f"{contract_id} {open_range[0]} - {open_range[1]}"

    if not bars:

        print("no bars matched")
        
        exit()

    idx = get_sessions(bars, open_range[0], open_range[1])
    
    for date, bars in idx.items():

        pass