

# add more using:
#
#   Global Settings >> Symbol Settings >> Real-Time Price Multiplier
#                                         Tick Size  


CONTRACT_SETTINGS = {

            # multiplier    # tick size

    "CL":   ( 0.01,         0.01,           ),
    "LO":   ( 0.01,         0.01,           ),
    "LO1":  ( 0.01,         0.01,           ),
    "LO2":  ( 0.01,         0.01,           ),
    "LO3":  ( 0.01,         0.01,           ),
    "LO4":  ( 0.01,         0.01,           ),
    "RB":   ( 0.0001,       0.0001,         ),
    "HO":   ( 0.0001,       0.0001,         ),
    "OH":   ( 0.0001,       0.0001,         ),
    "NG":   ( 0.001,        0.001,          ),
    "LNE":  ( 0.001,        0.001,          ),
    "ZC":   ( 1,            0.25,           ),
    "OCD":  ( 1,            0.125,          ),
    "ZR":   ( 0.001,        0.001,          ),
    "ZS":   ( 1,            0.25,           ),
    "ZM":   ( 0.01,         0.10,           ),
    "ZL":   ( 0.01,         0.01,           ),
    "ZW":   ( 1,            0.25,           ),
    "OZW":  ( 1,            0.125,          ),
    "KE":   ( 1,            0.25,           ),
    "ZO":   ( 1,            0.25,           ),
    "HE":   ( 0.001,        0.001,          ),
    "LE":   ( 0.001,        0.001,          ),
    "GF":   ( 0.001,        0.001,          ),
    "KE":   ( 1,            0.25,           ),
    "GC":   ( 0.01,         0.01,           ),
    "SI":   ( 0.001,        0.005,          ),
    "HG":   ( 0.0001,       0.0005,         ),
    "VX":   ( 1,            50,             ),
    "ES":   ( 0.01,         0.25,           ),
    "YM":   ( 1,            1.0,            ),
    "NQ":   ( 0.01,         0.25,           ),
    "RTY":  ( 0.01,         0.10,           ),
    "ZB":   ( 1,            1 / 32,         ),
    "ZN":   ( 1,            1 / 64,         ),
    "ZF":   ( 1,            1 / 128,        ),
    "ZT":   ( 1,            1 / 256,        ),
    "SR1":  ( 0.01,         0.0025,         ),
    "SR3":  ( 0.01,         0.0025,         ),
    "6E":   ( 0.0001,       0.000050,       ),
    "6B":   ( 0.0001,       0.000100,       ),
    "6J":   ( 0.000001,     0.0000005,      ),
    "6M":   ( 0.000001,     0.000010,       ),
    "SPX":  ( 1,            0.01            )

}


# janky but what are you gonna do...

def get_settings(fn: str):

    not_stock   = True
    settings    = None
    sym         = None

    if ":" in fn:

        # frd file

        sym = fn.split(":")[0]

    elif "NQTV" in fn:

        # stock

        sym         = fn.split("-")[0]
        not_stock   = False

    elif "." not in fn:

        # single

        if "_" in fn:

            # CME or VX spread
        
            if "CME" in fn:

                sym = fn.split("_")[0][0:-3]
            
            elif "CFE" in fn:

                sym = fn.split("-")[0][0:-3]
        
        elif "-" in fn:

            # VX single or ...?

            sym = fn.split("-")[0][0:-3]

        elif len(fn) > 3:

            # ??? possibly like "HON23"

            sym = fn[0:-3]

        else:

            # unqualified future symbol -- not file name

            sym = fn

    elif "FUT_SPREAD" in fn:

        # spread

        con_id = fn.split(".")[0]

        if "~" in con_id:

            # butterfly, etc.

            sym = con_id.split("~")[0]

        else:

            # calendar, or some weird stuff...

            sym = con_id.split("-")[0][0:-3]
        
    elif "FUT_OPT" in fn:

        sym = fn.split()[0][0:-3]

    if sym:

        if not_stock:

            settings = CONTRACT_SETTINGS[sym]
        
        else:

            settings = ( 0.01, 0.01 )
    
    return settings



