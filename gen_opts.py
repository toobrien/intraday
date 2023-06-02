from sys import argv


# usage: python gen_opts.py LON23 NYMEX 6000 8000 50


def get_opts(
    opt_id:     str,
    exchange:   str,
    lo_strike:  int,
    hi_strike:  int,
    increment:  int
):
    
    opts = []

    for type in ["P", "C"]:

        for i in range(lo_strike, hi_strike + increment, increment):

            opts.append(f"{opt_id} {type}{i}.FUT_OPT.{exchange}")
    
    return opts


if __name__ == "__main__":

    opt_id      = argv[1]
    exchange    = argv[2]
    lo_strike   = int(argv[3])
    hi_strike   = int(argv[4])
    increment   = int(argv[5])

    opts = get_opts(opt_id, exchange, lo_strike, hi_strike, increment)

    for opt in opts:

        print(opt)