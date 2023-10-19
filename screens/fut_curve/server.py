from json       import dumps
from flask      import Flask, Response
from flask_cors import CORS
from sys        import argv


# python screens/fut_curve/server.py HO 0:12


APP = Flask(
        __name__,
        static_folder   = "",
        static_url_path = ""
    )

APP.config["CACHE_TYPE"] = "null"

CORS(APP)

CONFIG = {}


@APP.route("/config", methods = [ "GET" ])
def get_config():

    return Response(dumps(CONFIG))


@APP.route("/fc_app")
def index():

    # not sure why this is necessary, but it do

    return APP.send_static_file("./fc_app.html")


if __name__ == "__main__":

    CONFIG["symbol"]        = argv[1]
    CONFIG["start_month"]   = argv[2].split(":")[0]
    CONFIG["end_month"]     = argv[2].split(":")[1]

    APP.run(host = "localhost", port = 8080)