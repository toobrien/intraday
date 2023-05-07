from    enum                    import  IntEnum
from    json                    import  loads
import  plotly.graph_objects    as      go
from    util.parsers            import  tas_rec
from    util.tas_tools          import  get_tas
from    sys                     import  argv
from    time                    import  time
from    typing                  import  List


# usage: python rotation.py ESM23_FUT_CME 8 0.25 0.01 2023-05-05T06:30:00.000000 2023-05-05T13:00:00.000000


class r_rot(IntEnum):

    side    = 0
    start   = 1
    length  = 2
    delta   = 3
    volume  = 4


CONFIG          = loads(open("./config.json").read())
SC_ROOT         = CONFIG["sc_root"]
SLEEP_INT       = CONFIG["sleep_int"]

ROTATION_SIDE       = 0
ROTATION_HIGH       = -float('inf')
ROTATION_LOW        = float('inf')
ROTATION_LENGTH     = 0
UP_ROTATION_DELTA   = 0
DN_ROTATION_DELTA   = 0
UP_ROTATION_VOLUME  = 0
DN_ROTATION_VOLUME  = 0


def get_rotations(
    recs:           List,
    min_rotation:   int,
    tick_size:      float
):

    global ROTATION_SIDE
    global ROTATION_HIGH
    global ROTATION_LOW
    global ROTATION_LENGTH
    global UP_ROTATION_DELTA
    global DN_ROTATION_DELTA
    global UP_ROTATION_VOLUME
    global DN_ROTATION_VOLUME

    res           = []
    prev_rotation = [ 0, "", 0, 0, 0 ]

    for rec in recs:

        price = rec[tas_rec.price]
        qty   = rec[tas_rec.qty]
        side  = rec[tas_rec.side]

        prev_rotation[r_rot.side]   = "up" if ROTATION_SIDE == 1 else "dn"
        prev_rotation[r_rot.start]  = ROTATION_LOW if ROTATION_SIDE == 1 else ROTATION_HIGH
        prev_rotation[r_rot.length] = ROTATION_LENGTH
        prev_rotation[r_rot.delta]  = UP_ROTATION_DELTA if ROTATION_SIDE == 1 else DN_ROTATION_DELTA
        prev_rotation[r_rot.volume] = UP_ROTATION_VOLUME if ROTATION_SIDE == 1 else DN_ROTATION_VOLUME

        if (price > ROTATION_HIGH):

            ROTATION_HIGH       = price
            DN_ROTATION_DELTA   = 0
            DN_ROTATION_VOLUME  = 0

        if (price < ROTATION_LOW):

            ROTATION_LOW        = price
            UP_ROTATION_DELTA   = 0
            UP_ROTATION_VOLUME  = 0

        signed_volume = -qty if side == 0 else qty
        
        UP_ROTATION_DELTA   += signed_volume
        DN_ROTATION_DELTA   += signed_volume
        UP_ROTATION_VOLUME  += qty
        DN_ROTATION_VOLUME  += qty

        from_rotation_high  = (ROTATION_HIGH - price) / tick_size
        from_rotation_low   = (price - ROTATION_LOW) / tick_size

        if (from_rotation_high >= min_rotation):

            # in down rotation

            if (ROTATION_SIDE > -1):

                # from up rotation

                res.append(
                    (
                        prev_rotation[r_rot.side],
                        prev_rotation[r_rot.start],
                        prev_rotation[r_rot.length],
                        prev_rotation[r_rot.delta],
                        prev_rotation[r_rot.volume]
                    )
                )

                ROTATION_SIDE   = -1
                ROTATION_LOW    = price
                ROTATION_LENGTH = from_rotation_high

                continue

            else:

                # continuing down rotation

                ROTATION_LENGTH = max(from_rotation_high, ROTATION_LENGTH)

        if (from_rotation_low >= min_rotation):

            # in up rotation

            if (ROTATION_SIDE < 1):

                # from down rotation

                res.append(
                    (
                        prev_rotation[r_rot.side],
                        prev_rotation[r_rot.start],
                        prev_rotation[r_rot.length],
                        prev_rotation[r_rot.delta],
                        prev_rotation[r_rot.volume]
                    )
                )

                ROTATION_SIDE   = 1
                ROTATION_HIGH   = price
                ROTATION_LENGTH = from_rotation_low

            else:

                # continuing up rotation

                ROTATION_LENGTH = max(from_rotation_low, ROTATION_LENGTH)

    return res


if __name__ == "__main__":

    t0 = time()

    fn              = argv[1]
    rotation_ticks  = int(argv[2])
    tick_size       = float(argv[3])
    multiplier      = float(argv[4])
    start           = argv[5] if len(argv) > 5 else None
    end             = argv[6] if len(argv) > 6 else None

    recs        = get_tas(fn, multiplier, None, start, end)
    rotations   = get_rotations(recs, rotation_ticks, tick_size)
    
    # display

    lengths = sorted(
        [ 
            r[r_rot.length] for r in rotations
            if r[r_rot.length] > 0 
        ]
    )

    open    = []
    high    = []
    low     = []
    close   = []

    for i in range(1, len(rotations)):

        rot = rotations[i]

        if rot[r_rot.side] == "up":

            c = rot[r_rot.start] + rot[r_rot.length] * tick_size
            low.append(rot[r_rot.start])
            high.append(c)
            close.append(c)
        
        else:

            c = rot[r_rot.start] - rot[r_rot.length] * tick_size
            low.append(c)
            high.append(rot[r_rot.start])
            close.append(c)

        open.append(rot[r_rot.start])
    
    fig = go.Figure()
    
    fig.update(layout_xaxis_rangeslider_visible = False)

    fig.add_trace(
        go.Ohlc(
            {
                "open":     open,
                "high":     high,
                "low":      low,
                "close":    close
            }
        )
    )

    fig.show()

    print(f"{'50%:':20}{int(lengths[int(len(lengths) * 0.5)])}")
    print(f"{'70%:':20}{int(lengths[int(len(lengths) * 0.75)])}")
    print(f"{'95%:':20}{int(lengths[int(len(lengths) * 0.95)])}")

    print(f"{'recs:':20}{len(recs)}")
    print(f"{'rotations:':20}{len(rotations)}")
    print(f"{'elapsed:':20}{time() - t0:0.2f}")
