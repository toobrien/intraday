from json           import loads
from util.rec_tools import get_tas, tas_rec
from sys            import argv


# usage: python read_tas.py HEK24_FUT_CME 0.001 2023-01-01 2023-06-01


CONFIG  = loads(open("./config.json").read())
FMT     = "%Y-%m-%dT%H:%M:%S.%f"

if __name__ == "__main__":

    fn          = argv[1]
    price_adj   = float(argv[2])
    precision   = len(argv[2].split(".")[1]) if "." in argv[2] else len(argv[2])
    start       = argv[3]
    end         = argv[4]

    recs = get_tas(fn, price_adj, FMT, start, end)

    for r in recs:

        print(
            r[tas_rec.timestamp],
            f"{r[tas_rec.price]: 10.{precision}f}",
            f"{r[tas_rec.qty]: 10d}",
            "bid".rjust(10) if r[tas_rec.side] == 0 else "ask".rjust(10),
        )