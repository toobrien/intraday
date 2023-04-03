from    sys                     import  argv
from    util.parsers            import  tas_rec
from    util.tas_tools          import  get_ohlcv, get_terms


if __name__ == "__main__":

    init_symbol             = argv[1]
    multiplier              = argv[2]
    precision               = len(multiplier.split(".")[1]) if "." in multiplier else len(multiplier)
    multiplier              = float(multiplier)
    n_months                = int(argv[3])
    start                   = argv[4]
    end                     = argv[5]


    recs = get_terms(
                init_symbol, 
                multiplier, 
                n_months,
                None,       # dont use datestrings when getting bar data
                start, 
                end
            )

    bars = get_ohlcv(recs, "1:M")
        
    for bar in bars[0:10]:

        print(bar)