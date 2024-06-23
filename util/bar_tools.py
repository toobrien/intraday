from    bisect          import  bisect_left, bisect_right
from    enum            import  IntEnum
import  polars          as      pl
from    sys             import  path
from    typing          import  List

path.append(".")

from    util.dbn_util   import  strptime
from    config          import  CONFIG


SC_ROOT     = CONFIG["sc_root"]
FRD_ROOT    = CONFIG["frd_root"]
DBN_ROOT    = CONFIG["dbn_root"]
FMT         = "%Y-%m-%dT%H:%M:%S.%f"
UTC_OFFSET  = CONFIG["utc_offset"]
TZ          = CONFIG["tz"]


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


def trim_range(df, start: str, end: str):

    if start:

        start   = start.split("T")
        df      = df.filter(
                    (pl.col("Date") > start[0]) |
                    ((pl.col("Date") == start[0]) & (pl.col(" Time") > start[1]))
                )

    if end:

        end = end.split("T")
        df  = df.filter(
                (pl.col("Date") < end[0]) |
                ((pl.col("Date") == end[0]) & (pl.col(" Time") < end[1]))
            )

    return df


def get_bars(
    contract_id:    str, 
    start:          str     = None, 
    end:            str     = None,
    give_df:        bool    = False
):

    df = None

    if ":" in contract_id:

        parts       = contract_id.split(":")
        contract_id = parts[0]
        resolution  = parts[1]

        df = get_frd_bars(contract_id, resolution, start, end)

    elif ".c." in contract_id:

        df = get_dbn_bars(contract_id, start, end)

    else:

        df = get_sc_bars(contract_id, start, end)

    return df if give_df else df.rows()


def get_sc_bars(
    contract_id:    str,
    start:          str = None,
    end:            str = None
):
    
    from io import StringIO

    extension   = ".scid_BarData.txt" if ".dly" not in contract_id else ".dly_BarData.txt"
    fn          = f"{SC_ROOT}/Data/{contract_id}{extension}"
    
    # polars 0.20.10 has issues reading the file directly from my VM for ??? reason
    # so, this...

    io          = StringIO(open(fn, "r", encoding="utf-8").read())
    df          = pl.read_csv(
                        io,
                        dtypes = [
                            pl.Utf8,
                            pl.Utf8,
                            pl.Float64,
                            pl.Float64,
                            pl.Float64,
                            pl.Float64,
                            pl.Int32,
                            pl.Int32,
                            pl.Int32,
                            pl.Int32
                        ]
                    ).with_columns(
                        [
                            pl.col("Date").str.to_datetime("%Y/%m/%d").dt.strftime("%Y-%m-%d"),
                            pl.col(" Time").str.replace_all(" ", "")
                        ]
                    ) # standardize date format and drop whitespace from time col

    df = trim_range(df, start, end)

    return df


# for ohlc from firstratedata
# naming convention: <symbol>_<resolution>.csv


def get_frd_bars(
    symbol:     str,
    resolution: str,
    start:      str = None,
    end:        str = None
):
    
    fn = f"{FRD_ROOT}/{symbol}/{symbol}_{resolution}.csv"
    df = pl.read_csv(fn)

    df = df.with_columns(
        pl.col("datetime").str.slice(0, 10).alias("Date"),
        pl.col("datetime").str.slice(11).alias(" Time")
    ).select(
        pl.col("Date"),
        pl.col(" Time"),
        pl.col("open"),
        pl.col("high"),
        pl.col("low"),
        pl.col("close")
    )

    df = trim_range(df, start, end)

    return df


# for ohlc from databento
# naming convention: <symbol>.c.<month>.csv

def get_dbn_bars(
    symbol:     str,
    start:      str     = None,
    end:        str     = None
):
    
    fn = f"{DBN_ROOT}/csvs/{symbol}.csv"
    df = pl.read_csv(
            fn,
            dtypes = [
                pl.Datetime,
                pl.Int16,
                pl.Int16,
                pl.Int32,
                pl.Float64,
                pl.Float64,
                pl.Float64,
                pl.Float64,
                pl.Int64,
                pl.Utf8
            ]
        )

    df = strptime(
            df,
            from_col    = "ts_event",
            to_col      = "ts", 
            FMT         = FMT, 
            tz          = TZ
        )
    
    df = df.with_columns(
        pl.col("ts").str.slice(0, 10).alias("Date"),
        pl.col("ts").str.slice(11, 19).alias(" Time")
    ).select(
        pl.col("Date"),
        pl.col(" Time"),
        pl.col("open"),
        pl.col("high"),
        pl.col("low"),
        pl.col("close"),
        pl.col("volume")
    )

    df = trim_range(df, start, end)

    return df


def get_sessions(
    bars: List, 
    start: str, 
    end: str
):

    res         = {}
    date_key    = lambda b: b[bar_rec.date]
    time_key    = lambda b: b[bar_rec.time]
    dates       = sorted(list(set([ bar[bar_rec.date] for bar in bars ])))

    for date in dates:

        i = bisect_left(bars, date, key = date_key)
        j = bisect_right(bars, date, key = date_key)

        selected = bars[i : j]

        if selected:

            i = bisect_left(selected, start, key = time_key)
            j = bisect_right(selected, end, key = time_key)

            session = selected[i : j]

            if session:

                res[date] = session
    
    return res