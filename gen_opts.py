from sys import argv


# usage: python gen_opts.py LON23 NYMEX 6000 8000 50


if __name__ == "__main__":

    opt_id      = argv[1]
    exchange    = argv[2]
    lo_strike   = int(argv[3])
    hi_strike   = int(argv[4])
    increment   = int(argv[5])

    for type in ["P", "C"]:

        for i in range(lo_strike, hi_strike + increment, increment):

            print(f"{opt_id} {type}{i}.FUT_OPT.{exchange}")