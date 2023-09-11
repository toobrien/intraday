from datetime   import datetime
from numpy      import datetime64, timedelta64
from sys        import path

path.append(".")

from config     import CONFIG


UTC_OFFSET_US   = timedelta64(int(CONFIG["utc_offset"] * 3.6e9), "us")
SC_EPOCH        = datetime64("1899-12-30") + UTC_OFFSET_US


def ts_to_ds(ts, fmt):

    return (SC_EPOCH + timedelta64(ts, "us")).astype(datetime).strftime(fmt)


def ds_to_ts(ds):

    return (datetime64(ds) - (timedelta64(0, "us") + SC_EPOCH)).astype("int64")
    