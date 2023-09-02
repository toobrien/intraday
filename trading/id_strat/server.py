from json       import dumps
from flask      import Flask, Response
from flask_cors import CORS
from sys        import argv, path
from time       import time

path.append(".")

from research.id_strat_txt import run


# python trading/id_strat/server.py SPX:1m fly 15:30:00 15:59:00 15:59:00 1 2023-06-01 2023-10-01 EWMA_FIN 0 -10:11 1.0 5.0 20230905
# (same as research/id_strat_txt.py, except with expiry as the last arg)


APP                         = Flask(
                                __name__,
                                static_folder   = "./trading/id_strat",
                                static_url_path = "",
                            )
APP.config["CACHE_TYPE"]    = "null"
CORS(APP)


CONFIG = {
    "expiry":   None,
    "host":     "localhost",
    "offsets":  None,
    "port":     8080,
    "rows":     None,
    "strategy": None,
    "ul_sym":   None    
}


@APP.route("/config", methods = [ "GET" ])
def get_config():

    return Response(dumps(CONFIG))


def get_ul_sym(raw_sym: str):

    # convert local sym to IBKR searchable version... not fully implemented

    return raw_sym.split(":")[0]


if __name__ == "__main__":

    t0 = time()

    CONFIG["expiry"]      = argv[-1]
    CONFIG["offsets"]     = [ int(i) for i in argv[11].split(":") ]
    CONFIG["rows"]        = run(argv[0:-1])

    print(f"id_strat_txt: {time() - t0:0.1f}s")

    if not CONFIG["rows"]:

        print("no rows retrieved")

        exit()

    CONFIG["strategy"]    = argv[2]
    CONFIG["ul_sym"]      = get_ul_sym(argv[1])

    print(f"server ready: {time() - t0:0.1f}s")

    print(f"app root: {APP.root_path}")

    APP.run(
        host = CONFIG["host"],
        port = CONFIG["port"]
    )

    pass