import  plotly.graph_objects    as      go
from    sys                     import  argv, path

path.append(".")

from    config                  import  CONFIG
from    util.contract_settings  import  get_settings
from    util.parsers            import  parse_tas, parse_tas_header, tas_rec
from    util.rec_tools          import  get_precision
from    util.sc_dt              import  ts_to_ds
from    typing                  import  List


IMBALANCE_DATA  = {}
ACTIVE_SERIES   = []
CLOSED_SERIES   = []


def get_figure(precision: float):

    fig = go.Figure()

    for series in CLOSED_SERIES:

        fig.add_trace(
            go.Scatter(
                {
                    "name": f"{series['date']} {series['time']} {series['start_price']: 0.{precision}f}",
                    "x":    series["x"],
                    "y":    series["y"],
                    "mode": "markers",
                    "marker": {
                        "color": series["color"]
                    }
                }
            )
        )

    return fig


def generate_series(
    recs:               List,
    price_adj:          float,
    vol_thresh:         int,
    delta_thresh:       float,
    cooldown_thresh:    float,
    finish_thresh:      float,
):

    global ACTIVE_SERIES

    for rec in recs:

        ds = ts_to_ds(rec[tas_rec.timestamp], "%Y-%m-%d %H:%M:%S").split()
        
        date    = ds[0] 
        time    = ds[1]
        price   = rec[tas_rec.price] * price_adj
        qty     = rec[tas_rec.qty] * -1 if not rec[tas_rec.side] else rec[tas_rec.qty]

        # initialize price data

        if price not in IMBALANCE_DATA:

            IMBALANCE_DATA[price] = {
                "last_trade_date":  date,
                "last_trade_time":  time,
                "imbalance":        0,
                "session_volume":   0,
                "cooldown":         False
            }

        price_data = IMBALANCE_DATA[price]

        if price_data["last_trade_date"] != date:

            # new session, clear data

            price_data["last_trade_date"]   = date
            price_data["imbalance"]         = 0
            price_data["session_volume"]    = 0
            price_data["cooldown"]          = False
        
        # update price data

        price_data["last_trade_time"]   =   time
        price_data["imbalance"]         +=  qty
        price_data["session_volume"]    +=  abs(qty)

        # check for imbalance via delta ratio; start new series if necessary

        delta_ratio = abs(price_data["imbalance"] / price_data["session_volume"])

        if  delta_ratio >= delta_thresh                 and \
            price_data["session_volume"] > vol_thresh   and \
            not price_data["cooldown"]:

            price_data["cooldown"] = True

            ACTIVE_SERIES.append( 
                {
                    "start_price":  price,
                    "date":         price_data["last_trade_date"],
                    "time":         price_data["last_trade_time"],
                    "x":            [],
                    "y":            [],
                    "color":        "#FF0000" if price_data["imbalance"] < 0 else "#0000FF",
                    "finished":     False
                }
            )

        elif delta_ratio <= cooldown_thresh and price_data["cooldown"]:

            price_data["cooldown"] = False

        # update active series

        for series in ACTIVE_SERIES:

            series["x"].append(len(series["x"]))
            series["y"].append(price - series["start_price"])

            if abs(series["y"][-1]) >= finish_thresh:

                series["finished"] = True
                
                CLOSED_SERIES.append(series)

        # prune closed series from active list

        ACTIVE_SERIES = [ 
            series 
            for series in ACTIVE_SERIES
            if not series["finished"]
        ]


if __name__ == "__main__":

    fn              = argv[1]
    multiplier, _   = get_settings(fn)
    precision       = get_precision(str(float))
    vol_thresh      = int(argv[2])
    delta_thresh    = float(argv[3])
    cooldown_thresh = float(argv[4])
    finish_thresh   = float(argv[5])

    with open(f"{CONFIG['sc_root']}/Data/{fn}.scid", "rb") as fd:

        parse_tas_header(fd)

        recs = parse_tas(fd, 0)

        generate_series(
            recs,
            multiplier,
            vol_thresh,
            delta_thresh,
            cooldown_thresh,
            finish_thresh
        )

        fig = get_figure(precision)

        fig.show()