from pyarrow        import parquet
from util.parsers   import tas_to_pq
from sys            import argv, path

path.append(".")

from config         import CONFIG


if __name__ == "__main__":
    
    fn          = argv[1]
    multiplier  = float(argv[2])
    output      = argv[3]

    with open(f"{CONFIG['sc_root']}/Data/{fn}.scid", "rb") as fd:

        table = tas_to_pq(fd, multiplier)

        parquet.write_table(table, f"{output}.parquet")
