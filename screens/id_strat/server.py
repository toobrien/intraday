from json       import dumps
from flask      import Flask, Response
from flask_cors import CORS
from sys        import argv, path
from time       import time

path.append(".")

from research.id_strat_txt import run


#                                   sym    start_t  end_t    exp_t    date_start date_end   mode offsets model_inc width def_inc expiry   lo_str hi_str
# python screens/id_strat/server.py SPX:1m 14:50:00 15:59:00 15:59:00 2024-10-01 2025-01-01 FIN  -15:16  1.0       5.0   1       20241201 6000   6100


APP                         = Flask(
                                __name__,
                                static_folder   = "",
                                static_url_path = ""
                            )
APP.config["CACHE_TYPE"]    = "null"
CORS(APP)


CONFIG = {
    "expiry":       None,
    "host":         "localhost",
    "increment":    None,
    "offsets":      None,
    "port":         8080,
    "rows":         None,
    "strategy":     None,
    "ul_sym":       None,
    "hi_strike":    None,
    "lo_strike":    None,
    "width":        None,
    "def_inc":      None
}


@APP.route("/config", methods = [ "GET" ])
def get_config():

    return Response(dumps(CONFIG))


@APP.route("/idx_fly")
def index():

    # not sure why this is necessary, but it do

    return APP.send_static_file("./idx_fly.html")


def get_ul_sym(raw_sym: str):

    # convert local sym to IBKR searchable version... not fully implemented

    return raw_sym.split(":")[0]


if __name__ == "__main__":

    t0 = time()

    CONFIG["offsets"]   = [ int(i) for i in argv[8].split(":") ]
    CONFIG["model_inc"] = float(argv[9])
    CONFIG["width"]     = float(argv[10])
    CONFIG["def_inc"]   = int(argv[11])
    CONFIG["expiry"]    = argv[12]
    CONFIG["lo_strike"] = int(argv[13])
    CONFIG["hi_strike"] = int(argv[14])
    CONFIG["rows"]      = run(
                            [
                                None,       # program
                                argv[1],    # sym
                                "fly",      # strat
                                argv[2],    # session_start
                                argv[3],    # session_end
                                argv[4],    # expiration
                                1,          # session inc
                                argv[5],    # date_start
                                argv[6],    # date_end
                                argv[7],    # mode
                                0,          # plot
                                argv[8],    # offset_rng
                                argv[9],    # strike_inc 
                                argv[10]    # width
                            ]
                        )

    print(f"id_strat_txt: {time() - t0:0.1f}s")

    if not CONFIG["rows"]:

        print("no rows retrieved")

        exit()

    CONFIG["strategy"]    = argv[2]
    CONFIG["ul_sym"]      = get_ul_sym(argv[1])

    print(f"server ready:       {time() - t0:0.1f}s")

    APP.run(
        host = CONFIG["host"],
        port = CONFIG["port"]
    )
