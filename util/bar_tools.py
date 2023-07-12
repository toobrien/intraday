from    bisect  import  bisect_left, bisect_right
from    enum    import  IntEnum
from    json    import  loads
import  polars  as      pl
from    typing  import  List


# note: files must be manually updated from the chart, as far as i know: 
# 
#   Edit >> Export Bar Data to Text File


SC_ROOT = loads(open("./config.json", "r").read())["sc_root"]


class bar_rec(IntEnum):

    date    = 0
    time    = 1
    open    = 2
    high    = 3
    low     = 4
    last    = 5
    volume  = 6
    trades  = 7
    bid_vol = 8
    ask_vol = 9


# start, end format: YYYY-MM-DDTHH:MM:SS

def get_bars(
    contract_id:    str, 
    start:          str = None, 
    end:            str = None
):

    start   = start.split("T")
    end     = end.split("T")
    fn      = f"{SC_ROOT}/data/{contract_id}.scid_BarData.txt"
    df      = pl.read_csv(fn).with_columns(
                [
                    pl.col("Date").str.to_datetime("%Y/%m/%d").dt.strftime("%Y-%m-%d"),
                    pl.col(" Time").str.replace_all(" ", "")
                ]
            ) # standardize date format and drop whitespace from time col

    if start:
    
        df =    df.filter(
                    (pl.col("Date") > start[0]) |
                    ((pl.col("Date") == start[0]) & (pl.col(" Time") > start[1]))
                )

    if end:

        df =    df.filter(
                    (pl.col("Date") < end[0]) |
                    ((pl.col("Date") == end[0]) & (pl.col(" Time") < end[1]))
                )

    return df.rows()


def get_sessions(
    bars: List, 
    start: str, 
    end: str
):

    res         = {}
    date_key    = lambda b: b[bar_rec.date]
    time_key    = lambda b: b[bar_rec.time]
    dates   = sorted(List(set([ bar[bar_rec.date] for bar in bars ])))

    for date in dates:

        i = bisect_left(bars, date, key = date_key)
        j = bisect_right(bars, date, key = date_key)

        selected = bars[i : j]

        if selected:

            i = bisect_left(selected, start, time_key)
            j = bisect_right(selected, end, time_key)

            session = selected[i : j]

            if session:

                res[date] = session
    
    return res

