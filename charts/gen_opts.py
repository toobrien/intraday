from sys import argv


# usage: python charts/gen_opts.py LON23 NYMEX 6000 8000 50 0


def get_opts(
    opt_id:     str,
    exchange:   str,
    lo_strike:  int,
    hi_strike:  int,
    increment:  int,
    fill_width: int
):
    
    opts = []

    for type in [ "C", "P" ]:

        for i in range(lo_strike, hi_strike + increment, increment):

            opts.append(f"{opt_id} {type}{str(i).rjust(fill_width, '0')}.FUT_OPT.{exchange}")
    
    return opts


if __name__ == "__main__":

    opt_id      = argv[1]
    exchange    = argv[2]
    lo_strike   = int(argv[3])
    hi_strike   = int(argv[4])
    increment   = int(argv[5])
    fill_width  = int(argv[6])

    opts = get_opts(opt_id, exchange, lo_strike, hi_strike, increment, fill_width)

    for opt in opts:

        print(opt)