from flask                  import Flask, jsonify, request
from flask_cors             import CORS
from math                   import log
from bisect                 import bisect_left
from numpy                  import arange, array
from polars                 import read_csv
from sklearn.linear_model   import LinearRegression
from sys                    import argv


# python server.py ES EMD 2024-07-03 06-15


APP                         = Flask(
                                __name__,
                                static_folder   = "",
                                static_url_path = ""
                            )
APP.config["CACHE_TYPE"]    = "null"
CORS(APP)


def regression_model(
    x:          str,
    y:          str
):
    
    model   = LinearRegression()
    x0      = x[0]
    y0      = y[0]
    x_      = array([ log(i / x0) for i in x ])
    y_      = array([ log(i / y0) for i in y ])

    model.fit(x_.reshape(-1, 1), y_)

    X           = arange(min(x_), max(x_), step = 0.00001)
    Y           = model.predict(X.reshape(-1, 1))
    b           = model.coef_[0]
    a           = model.intercept_
    residuals   = y_ - model.predict(x_.reshape(-1, 1))
    res         = {
        "alpha":        a,
        "beta":         b,
        "model_x":      X,
        "model_y":      Y,
        "residuals":    residuals,
    }

    return res


@APP.route("/get_model", methods = [ "POST" ])
def get_model():

    data    = request.get_json()
    x       = data["x"]
    y       = data["y"]

    res = regression_model(x, y)

    return jsonify(res)


@APP.route("/get_config")
def get_config():

    return jsonify(CONFIG)


@APP.route("/")
def index():

    return APP.send_static_file("./index.html")


if __name__ == "__main__":

    x_sym           = argv[1]
    y_sym           = argv[2]
    date            = argv[3]
    start_t, end_t  = argv[4].split("-") 
    df              = read_csv(f"./csvs/{date}.csv")
    ts              = list(df["ts"])
    i               = bisect_left(ts, f"{date}T{start_t}")
    j               = bisect_left(ts, f"{date}T{end_t}")
    ts              = ts[i:j]
    x               = list(df[x_sym])[i:j]
    y               = list(df[y_sym])[i:j]
    CONFIG          = {
                        "date":     date,
                        "x_sym":    x_sym,
                        "y_sym":    y_sym,
                        "ts":       ts,
                        "x":        x,
                        "y":        y,
                    }

    APP.run(debug = False, port = "8081")

    pass
