from json                   import loads
from sys                    import argv, path

path.append(".")

from util.contract_settings import get_settings
from util.rec_tools         import get_precision, get_tas, tas_rec


# python charts/read_tas.py HEK24_FUT_CME 2023-01-01 2023-06-01


FMT = "%Y-%m-%dT%H:%M:%S.%f"


if __name__ == "__main__":

    contract_id     = argv[1]
    multiplier, _   = get_settings(contract_id)
    precision       = get_precision(float(multiplier))
    start           = argv[2] if len(argv) > 2 else None
    end             = argv[3] if len(argv) > 3 else None

    recs = get_tas(contract_id, multiplier, FMT, start, end)

    for r in recs:

        print(
            r[tas_rec.timestamp],
            f"{r[tas_rec.price]: 10.{precision}f}",
            f"{r[tas_rec.qty]: 10d}",
            "bid".rjust(10) if r[tas_rec.side] == 0 else "ask".rjust(10),
        )