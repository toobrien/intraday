from json       import dumps
from flask      import Flask, Response
from flask_cors import CORS
from sys        import argv, path
from time       import time

path.append(".")

from md_model               import model
from util.contract_settings import get_settings
from util.rec_tools         import get_precision


#                                   type    sym     res exps     strat  mode   hist_start hist_end   time_idx       offsets model_inc true_inc  params
# python screens/md_strat/server.py FUT     ZC      1m  20231214 -fly   FIN    2018-01-01 2024-01-01 now,2023-09-28 -50:51  2         10        10
# python screens/md_strat/server.py IND     SPX     1m  -        -fly   FIN    2023-06-01 2023-10-01 now,2023-09-24 -25:26  1         5         5
# python screens/md_strat/server.py STK     AAPL    1m  -        -fly   FIN    2023-06-01 2024-01-01 now,2023-09-24 -3:3    0.1       2.5       2.5


# type:             FUT, IND, or STK
# sym:              underlying symbol
# res:              ohlc resolution (only minutes supported--must match source data)
# exps:             underlying expiration date (futs only)
# strat:            see options in util.v_pricing
# hist_start/end:   date range for model inputs
# time_idx:         "now" or YYYY-MM-DD, or YYYY-MM-DDTHH:MM:SS. modelling will start
#                   from first timestamp; subsequent timestamps are for expirations.
#                   separate with commas. if timestamp is ommitted from expirations, the 
#                   default expiration time as defined in util.opts.OPT_DEFS will be used.
# offsets:          strike range for modelling and quoting
# model_inc:        strike increment for modeling (arbitrary)
# true_inc:         point increment of real option strikes
# params:           strategy specific -- see util.v_pricing; the last parameter is the strike (rather than point) width for width-based strategies


APP     = Flask(__name__, static_folder = "", static_url_path = "")
CONFIG  = {
            "host": "localhost",
            "port": 8080
        }

APP.config["CACHE_TYPE"] = "null"
CORS(APP)


@APP.route("/config", methods = [ "GET" ])
def get_config():

    return Response(dumps(CONFIG))


@APP.route("/md_strat")
def index():

    return APP.send_static_file("./md_strat.html")


if __name__ == "__main__":

    t0 = time()

    CONFIG["ul_type"]       = argv[1]
    CONFIG["ul_sym"]        = argv[2]
    CONFIG["resolution"]    = argv[3]
    CONFIG["ul_exps"]       = argv[4].split(",")
    CONFIG["strat"]         = argv[5][1:]
    CONFIG["side"]          = argv[5][0]
    CONFIG["mode"]          = argv[6]
    CONFIG["hist_start"]    = argv[7]
    CONFIG["hist_end"]      = argv[8]
    CONFIG["time_idx"]      = argv[9].split(",")
    CONFIG["offsets"]       = [ float(val) for val in argv[10].split(":") ]
    CONFIG["model_inc"]     = float(argv[11])         
    CONFIG["true_inc"]      = float(argv[12])
    CONFIG["params"]        = [ float(val) for val in argv[13:] ]
    CONFIG["precision"]     = get_precision(str(get_settings(CONFIG["ul_sym"])[1]))

    ul_sym      = CONFIG["ul_sym"]
    ul_type     = CONFIG["ul_type"]
    resolution  = CONFIG["resolution"]
    model_sym   = CONFIG["ul_sym"]

    if ul_type == "IND":

        model_sym = f"{ul_sym}:{resolution}"

    elif ul_type == "STK":

        model_sym = f"{ul_sym}-NQTV"


    index, rows = model(
                    model_sym,
                    CONFIG["strat"][1:],
                    CONFIG["mode"],
                    CONFIG["hist_start"],
                    CONFIG["hist_end"],
                    CONFIG["time_idx"],
                    CONFIG["offsets"],
                    CONFIG["model_inc"],
                    CONFIG["params"],
                    CONFIG["precision"]
                )
    
    CONFIG["opt_exps"]  = [ int(ts.split("T")[0]) for ts in CONFIG["time_idx"][1:] ]
    CONFIG["index"]     = index
    CONFIG["rows"]      = rows

    print(f"server ready: {time() - t0:0.1f}")

    APP.run(
        host = CONFIG["host"],
        port = CONFIG["port"]
    )