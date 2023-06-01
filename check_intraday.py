from json           import loads
from os             import fstat
from struct         import Struct
from sys            import argv
from util.parsers   import parse_tas_header, INTRADAY_REC_FMT, INTRADAY_REC_LEN


SC_ROOT = loads(open("./config.json", "r").read())["sc_root"]


if __name__ == "__main__":

    fn = argv[1]

    with open(f"{SC_ROOT}/Data/{fn}.scid", "rb") as fd:

        fstat(fd.fileno())

        ptr         = 0
        _           = parse_tas_header(fd)
        buf         = fd.read()
        struct      = Struct(INTRADAY_REC_FMT)

        while ptr < len(buf):

            ir = struct.unpack_from(buf, ptr)

            ptr += INTRADAY_REC_LEN

            print("\t\t".join([ str(field) for field in ir ]))

