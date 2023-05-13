from json           import loads
from util.parsers   import parse_tas, parse_tas_header, transform_tas, tas_rec
from util.sc_dt     import ts_to_ds
from sys            import argv
from time           import sleep


# usage: python read_tas.py HEK24_FUT_CME 0.001 0 0


CONFIG      = loads(open("./config.json").read())
SC_ROOT     = CONFIG["sc_root"]
SLEEP_INT_S = CONFIG["sleep_int"]


if __name__ == "__main__":

    fn          = argv[1]
    price_adj   = float(argv[2])
    precision   = len(argv[2].split(".")[1]) if "." in argv[2] else len(argv[2])
    loop        = int(argv[3])
    to_seek     = int(argv[4])

    with open(f"{SC_ROOT}/Data/{fn}.scid", "rb") as fd:

        _ = parse_tas_header(fd)

        while True:

            res = parse_tas(fd, to_seek)

            recs = transform_tas(res, price_adj)

            for r in recs:

                print(
                    ts_to_ds(r[tas_rec.timestamp], "%Y-%m-%d %H:%M:%S.%f"),
                    f"{r[tas_rec.price]: 10.{precision}f}",
                    f"{r[tas_rec.qty]: 10d}",
                    "bid".rjust(10) if r[tas_rec.side] == 0 else "ask".rjust(10),
                )

            if loop:

                sleep(SLEEP_INT_S)

                to_seek = 0
            
            else:

                break
