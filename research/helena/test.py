import  polars          as      pl
from    sys             import  path

path.append(".")

from    util.bar_tools  import bar_rec, get_bars, get_sessions


if __name__ == "__main__":

    ts_event    = "05:29:00"
    start       = "05:00:00"
    end         = "14:00:00"
    limit       = 12
    es          = get_bars("ES.c.0", give_df = True)
    es          = es.with_columns(es[" Time"].str.slice(0,8).alias(" Time"))
    es          = es.rows()
    sessions    = get_sessions(es, start, end)
    cpi         = pl.read_csv("./research/helena/cpi.csv")[-limit:]

    for row in cpi.iter_rows():

        date    = row[0]
        bars    = sessions[date]
        ts      = [ bar[bar_rec.time] for bar in bars ]
        closes  = [ bar[bar_rec.last] for bar in bars ]
        highs   = [ bar[bar_rec.high] for bar in bars ]
        low     = [ bar[bar_rec.low]  for bar in bars ]
        i       = ts.index(ts_event)
        last    = closes[i]
        up      = max(highs[i + 1:])
        dn      = min(low[i + 1:])
        
        pass

    pass