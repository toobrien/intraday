from datetime       import datetime
from json           import loads
from numpy          import datetime64, timedelta64

CONFIG          = loads(open("./config.json", "r").read())
UTC_OFFSET_US   = timedelta64(int(CONFIG["utc_offset"] * 3.6e9), "us")
SC_EPOCH        = datetime64("1899-12-30") + UTC_OFFSET_US


def ts_to_ds(ts, fmt):

    return (SC_EPOCH + timedelta64(ts, "us")).astype(datetime).strftime(fmt)


# only millisecond precision

def ds_to_ts(ds):

    since_unix      = datetime64(ds)
    unix_epoch_us   = timedelta64(0, "us")
    adjusted        = unix_epoch_us + SC_EPOCH
    final           = since_unix - adjusted
    final_int       = final.astype("int64")

    return final_int