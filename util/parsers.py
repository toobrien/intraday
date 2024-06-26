from    enum        import  IntEnum
from    numpy       import  array, datetime64, int64
from    os          import  fstat
import  pyarrow     as      pa
from    util.sc_dt  import  ts_to_ds
from    struct      import  calcsize, Struct, unpack_from
from    sys         import  argv
from    time        import  time
from    typing      import  BinaryIO, List


SC_EPOCH = datetime64("1899-12-30")


# TIME AND SALES
# NOTE: sc must be configured to store tick data: 
# https://www.sierrachart.com/index.php?page=doc/TickbyTickDataConfiguration.php


class intraday_rec(IntEnum):

    timestamp   = 0
    open        = 1
    high        = 2
    low         = 3
    close       = 4
    num_trades  = 5
    total_vol   = 6
    bid_vol     = 7
    ask_vol     = 8


class tas_rec(IntEnum):

    timestamp   = 0
    price       = 1
    qty         = 2
    side        = 3


# format string spec:   https://docs.python.org/3/library/struct.html#struct.unpack
# file spec:            https://www.sierrachart.com/index.php?page=doc/IntradayDataFileFormat.html

INTRADAY_HEADER_FMT  = "4cIIHHI36c"
INTRADAY_HEADER_LEN  = calcsize(INTRADAY_HEADER_FMT)

INTRADAY_REC_FMT    = "q4f4I"
INTRADAY_REC_LEN    = calcsize(INTRADAY_REC_FMT)
INTRADAY_REC_UNPACK = Struct(INTRADAY_REC_FMT).unpack_from


def parse_tas_header(fd: BinaryIO) -> tuple:
    
    header_bytes    = fd.read(INTRADAY_HEADER_LEN)
    header          = Struct(INTRADAY_HEADER_FMT).unpack_from(header_bytes)

    return header


def parse_tas(fd: BinaryIO, checkpoint: int) -> List:

    fstat(fd.fileno())

    tas_recs = []

    if checkpoint:
    
        fd.seek(INTRADAY_HEADER_LEN + checkpoint * INTRADAY_REC_LEN)

    while intraday_rec_bytes := fd.read(INTRADAY_REC_LEN):

        ir = INTRADAY_REC_UNPACK(intraday_rec_bytes)

        if ir[intraday_rec.total_vol] == 0:

            # for some reason many options records have 0 trades...
            
            continue

        tas_rec = (
            ir[intraday_rec.timestamp],
            ir[intraday_rec.close],
            ir[intraday_rec.bid_vol] if ir[intraday_rec.bid_vol] else ir[intraday_rec.ask_vol],
            0 if ir[intraday_rec.bid_vol] > 0 else 1
        )

        tas_recs.append(tas_rec)

    return tas_recs


def bulk_parse_tas(fd: BinaryIO, checkpoint: int) -> List:

    buf         = fd.read()
    ptr         = checkpoint * INTRADAY_REC_LEN
    tas_recs    = []
    struct      = Struct(INTRADAY_REC_FMT)

    while ptr < len(buf):

        ir = struct.unpack_from(buf, ptr)

        ptr += INTRADAY_REC_LEN

        if ir[intraday_rec.total_vol] == 0:

            # for some reason many options records have 0 trades...

            continue

        tas_recs.append(
            (
                ir[intraday_rec.timestamp],
                ir[intraday_rec.close],
                ir[intraday_rec.bid_vol] if ir[intraday_rec.bid_vol] else ir[intraday_rec.ask_vol],
                0 if ir[intraday_rec.bid_vol] > 0 else 1
            )
        )

    return tas_recs


# use when record indices are known

def tas_slice(
    fd:         BinaryIO,
    multiplier: float,
    ts_fmt:     str = None,
    start_rec:  int = 0, 
    end_rec:    int = None
) -> List:
    
    fd.seek(INTRADAY_HEADER_LEN + start_rec * INTRADAY_REC_LEN)
    
    if end_rec:

        buf = fd.read(INTRADAY_REC_LEN * (end_rec - start_rec))
    
    else:

        buf = fd.read()
    
    i           = 0
    struct      = Struct(INTRADAY_REC_FMT)
    tas_recs    = []

    while i < len(buf):

        ir = struct.unpack_from(buf, i)

        tas_recs.append(
            (
                ir[intraday_rec.timestamp] if not ts_fmt else ts_to_ds(ir[intraday_rec.timestamp], ts_fmt),
                ir[intraday_rec.close] * multiplier,
                ir[intraday_rec.bid_vol] if ir[intraday_rec.bid_vol] else ir[intraday_rec.ask_vol],
                0 if ir[intraday_rec.bid_vol] > 0 else 1
            )
        )
    
        i += INTRADAY_REC_LEN

    return tas_recs


def transform_tas(rs: List, price_adj: float, fmt: str = None):

    # - truncate record-count suffixed int64 to millisecond datestring (optional -- change schema to TEXT type)
    # - adjust price using "real-time price multiplier"

    return [
        (
            r[tas_rec.timestamp] if not fmt else ts_to_ds(r[tas_rec.timestamp], fmt),
            r[tas_rec.price] * price_adj,
            r[tas_rec.qty],
            r[tas_rec.side]
        )
        for r in rs
    ]


def tas_to_pq(fd: BinaryIO, multiplier: int):

    parse_tas_header(fd)

    buf     = fd.read()
    ptr     = 0
    struct  = Struct(INTRADAY_REC_FMT)

    ts      = []
    close   = []
    qty     = []
    side    = []

    while ptr < len(buf):

        ir = struct.unpack_from(buf, ptr)

        ptr += INTRADAY_REC_LEN

        ts.append(ir[intraday_rec.timestamp])
        close.append(ir[intraday_rec.close] * multiplier)
        qty.append(intraday_rec.bid_vol if ir[intraday_rec.bid_vol] else ir[intraday_rec.ask_vol])
        side.append(0 if ir[intraday_rec.bid_vol] > 0 else 1)
    
    ts      = pa.array(ts, type = pa.int64())
    close   = pa.array(close, type = pa.float32())
    qty     = pa.array(qty, type = pa.int32())
    side    = pa.array(side, type = pa.int8())

    table   = pa.table(
                        [ ts, close, qty, side],
                        names = [ "ts", "close", "qty", "side" ]
                    )

    return table


# MARKET DEPTH
# NOTE: sc must be configured to record market depth data:
# https://www.sierrachart.com/index.php?page=doc/StudiesReference.php&ID=375#DownloadingOfHistoricalMarketDepthData

# NOTE: sierra chart provides 30 days of historical market data: https://www.sierrachart.com/SupportBoard.php?PostID=279457#P279457


class depth_rec(IntEnum):

    timestamp   = 0
    command     = 1
    flags       = 2
    num_orders  = 3
    price       = 4
    quantity    = 5
    reserved    = 6


class depth_cmd(IntEnum):

    none        = 0
    clear_book  = 1
    add_bid_lvl = 2
    add_ask_lvl = 3
    mod_bid_lvl = 4
    mod_ask_lvl = 5
    del_bid_lvl = 6
    del_ask_lvl = 7


DEPTH_HEADER_FMT  = "4I48c"
DEPTH_HEADER_LEN  = calcsize(DEPTH_HEADER_FMT)

DEPTH_REC_FMT    = "qBBHfII"
DEPTH_REC_LEN    = calcsize(DEPTH_REC_FMT)
DEPTH_REC_UNPACK = Struct(DEPTH_REC_FMT).unpack_from


def parse_depth_header(fd: BinaryIO)->tuple:
    
    header_bytes    = fd.read(DEPTH_HEADER_LEN)
    header          = Struct(DEPTH_HEADER_FMT).unpack_from(header_bytes)

    return header


def parse_depth(fd: BinaryIO, checkpoint: int) -> List:

    # format string spec:   https://docs.python.org/3/library/struct.html#struct.unpack
    # file spec:            https://www.sierrachart.com/index.php?page=doc/MarketDepthDataFileFormat.html

    '''
    if !checkpoint:
    
        header_bytes    = fd.read(HEADER_LEN)
        header          = Struct(HEADER_FMT).unpack_from(header_bytes)
    '''

    fstat(fd.fileno())

    if checkpoint:
    
        fd.seek(DEPTH_HEADER_LEN + checkpoint * DEPTH_REC_LEN)

    depth_recs = []

    while depth_rec_bytes := fd.read(DEPTH_REC_LEN):

        dr = DEPTH_REC_UNPACK(depth_rec_bytes)

        depth_recs.append(dr)

    return depth_recs


def transform_depth(rs: List, price_adj: float, fmt: str = None):

    # - replace timestamp with datestring if "fmt"
    # - adjust price using "real-time price multiplier"
    # - delete "reserved" value from record

    return [
        (
            r[depth_rec.timestamp] if not fmt else ts_to_ds(r[depth_rec.timestamp], fmt),
            r[depth_rec.command],
            r[depth_rec.flags],
            r[depth_rec.num_orders],
            r[depth_rec.price] * price_adj,
            r[depth_rec.quantity]
        )
        for r in rs
    ]


if __name__ == "__main__":

    # benchmark program

    start = time()

    mode = argv[1]

    if mode == "tas":

        sc_root     = argv[2]
        contract    = argv[3]
        checkpoint  = int(argv[4])
        fn          = f"{sc_root}/Data/{contract}.scid"

        with open(fn, "rb") as fd:
        
            parse_tas_header(fd)
            rs = parse_tas(fd, checkpoint)

            print(f"num_recs: {len(rs)}")


    elif mode == "depth":

        sc_root     = argv[2]
        contract    = argv[3]
        date        = argv[4]
        checkpoint  = int(argv[5])
        fn          = f"{sc_root}/Data/MarketDepthData/{contract}.{date}.depth"

        with open(fn, "rb") as fd:

            parse_depth_header(fd)
            rs = parse_depth(fd, checkpoint)

            print(f"num_recs: {len(rs)}")

    print(f"finished: {time() - start:0.1f}s")