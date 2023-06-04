from gen_opts       import get_opts
from json           import loads
from os             import listdir
from sys            import argv
from typing         import List
from util.parsers   import tas_rec
from util.rec_tools import get_tas


# usage: python read_opt_trades.py LON23 0.01 50 2023-06-02T11:00:00
#
# use gen_opts.py to build a list of option symbols for the intraday file update list


SC_ROOT = loads(open("./config.json", "r").read())["sc_root"]
FMT     = "%Y-%m-%dT%H:%M:%S.%f"


def filter_trades(recs: List, opt_id: str, min_qty: int):

    ts          = recs[0][tas_rec.timestamp]
    prev_price  = recs[0][tas_rec.price]
    prev_side   = recs[0][tas_rec.side]
    trade_qty   = recs[0][tas_rec.qty]
    filtered    = []

    for rec in recs[1:]:

        ts      = rec[tas_rec.timestamp]
        price   = rec[tas_rec.price]
        side    = rec[tas_rec.side]
        qty     = rec[tas_rec.qty]

        if price == prev_price and side == prev_side:

            trade_qty += qty
        
        else:

            if trade_qty >= min_qty:

                filtered.append(
                    ( 
                        opt_id,
                        ts,
                        prev_price, 
                        "ask" if prev_side else "bid", 
                        trade_qty
                    )
                )

            prev_price  = price
            prev_side   = side
            trade_qty   = qty

    # append final trade if necessary
    
    if trade_qty >= min_qty:

        filtered.append(
            ( 
                opt_id,
                ts,
                prev_price,
                "ask" if prev_side else "bid", 
                trade_qty
            )
        )
    
    return filtered


def print_opt_trades(
    opt_class:  str,
    multiplier: float,
    min_qty:   int,
    start:      str,
    end:        str
):
    
    all_trades  = []
    fns         = [
        fn[:-5] for fn in
        listdir(f"{SC_ROOT}/Data")
        if opt_class in fn and ".scid" in fn
    ]

    for fn in fns:

        opt_id      = fn.split(".")[0]
        recs        = get_tas(fn, multiplier, FMT, start, end)
        
        # sc includes option "trades" with 0 volume for some reason... 
        # filter these out before grouping

        recs = [ rec for rec in recs if rec[tas_rec.qty] != 0 ]
        
        if recs:
        
            filtered = filter_trades(recs, opt_id, min_qty)

            if filtered:

                all_trades.append(filtered)

    # sort by timestamp

    all_trades = sorted(all_trades, key = lambda r: r[1])

    for trade in all_trades:

        print("\t".join([ str(val) for val in trade ]))


if __name__ == "__main__":

    opt_class   = argv[1]
    multiplier  = float(argv[2])
    min_qty     = int(argv[3])
    start       = argv[4] if len(argv) > 4 else None
    end         = argv[5] if len(argv) > 5 else None

    print_opt_trades(opt_class, multiplier, min_qty, start, end)