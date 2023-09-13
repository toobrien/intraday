from    ast         import  literal_eval
from    pandas      import  Timestamp
import  polars      as      pl
from    sys         import  argv, path
from    time        import  time

path.append(".")

from    util.opts   import  get_fut_expirations, get_records_by_contract, get_indexed_opt_series
from    util.cat_df import  cat_df


def get_rec_test(
    symbol: str,
    start:  str,
    end:    str
):
    
    recs = get_records_by_contract(symbol, start, end)

    pass


def get_expirations_test(
    symbol: str,
    start:  str,
    end:    str,
    kind:   str,
    rule:   str
):

    res     = get_records_by_contract(symbol, start, end)
    rule    = literal_eval(rule)

    print(rule)
    
    for id, recs in res.items():

        exps = get_fut_expirations(recs, kind, rule)

        print(f"{id}: {' '.join(exps)}")

    pass


# note: futures only; no reference data for stock or index options

def check_expirations(
    start:      str,
    end:        str,
    ul_symbol:  str,
    opt_class:  str     = None,
    ref_db:     bool    = False
):

    if ref_db:

        df = cat_df("opts", ul_symbol, start, end)

        if opt_class:

            df = df.filter(pl.col("name") == opt_class)
        
        rows = sorted(df.unique(["name", "expiry"]).rows(), key = lambda r: r[0])

        for row in rows:

            print(f"{row[0]}\t{row[1]}\t{Timestamp(row[0]).day_of_week}")

        print()

    cons = get_records_by_contract(ul_symbol, start, end)
    exps = []

    for _, recs in cons.items():

        expirations = get_fut_expirations(ul_symbol, recs)

        if opt_class:

            expirations = [ e for e in expirations if opt_class in e[2] ]

        exps.extend(expirations)

    exps = sorted(exps, key = lambda r: r[0])

    for exp in exps:

        print(f"{exp[0]}\t{exp[2]}\t{Timestamp(exp[0]).day_of_week}\t{exp[3]}")

    pass


def check_indexed_opt_series(
    symbol:     str,
    cur_dt:     str,
    exp_dt:     str,
    start_date: str,
    end_date:   str,
    trim:       str = "True",
    inc_stl:    str = "True"
    
):
    
    res = get_indexed_opt_series(
            symbol, 
            cur_dt, 
            exp_dt, 
            start_date, 
            end_date, 
            trim    != "False", 
            inc_stl != "False"
        )

    pass


TESTS = {
    "get_rec":                  get_rec_test,
    "get_expirations":          get_expirations_test,
    "check_expirations":        check_expirations,
    "check_indexed_opt_series": check_indexed_opt_series
}


if __name__ == "__main__":

    t0      = time()
    test    = argv[1]
    args    = argv[2:]

    TESTS[test](*args)

    print(f"elapsed: {time() - t0:0.1f}")