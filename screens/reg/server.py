from flask                  import Flask, render_template
from math                   import log
from bisect                 import bisect_left
from numpy                  import arange, array
from polars                 import read_csv
from sklearn.linear_model   import LinearRegression


app = Flask(__name__)


def regression_model(
    x:          str,
    y:          str,
    ts:         str,
    date:       str,
    start_t:    str,
    end_t:      str
):
    
    i       = bisect_left(ts, f"{date}T{start_t}")
    j       = bisect_left(ts, f"{date}T{end_t}")
    ts      = ts[i:j]
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


@app.route("/")
def index():

    return render_template("index.html")


if __name__ == "__main__":

    app.run(debug = False, port = "8081")

    pass
