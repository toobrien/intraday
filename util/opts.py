from    bisect                  import  bisect_left, bisect_right
from    datetime                import  datetime
from    enum                    import  IntEnum
from    pandas                  import  bdate_range, date_range, DateOffset, Timestamp, Timedelta
from    pandas.tseries.holiday  import  USFederalHolidayCalendar
from    pandas.tseries.offsets  import  BDay, MonthBegin, MonthEnd
from    sys                     import  path
from    typing                  import  List

path.append(".")

from    util.bar_tools          import bar_rec, get_bars
from    util.cat_df             import cat_df


DATE_FMT    = "%Y-%m-%d"
DT_FMT      = "%Y-%m-%dT%H:%M:%S"
OPT_DEFS    = {


    # bounds on ul_map are:
    #
    #   - relative to month in which underlying future *expires* (e.g. august for CL U)
    #   - start:    inclusive weekly exps from monthly exp, exclusive monthly exp
    #   - end:      inclusive weekly until monthly exp, inclusive monthly exp

    "6E": {
        "monthly_sym":  "EUU",
        "weekly_syms":  [ "MO*", "TU*", "WE*", "SU*", "*EU" ],
        "wk_on_month":  False,
        "exp_rule":     "BOM+2FRI<3WED",
        "exp_time":     "07:00:00",
        "ul_map":       {
            "H": (-4, 0),
            "M": (-4, 0),
            "U": (-4, 0),
            "Z": (-4, 0)
        },
        "m_sym_offset": 0
    },
    "6J": {
        "monthly_sym":  "JPU",
        "weekly_syms":  [ "MJ*", "TJ*", "WJ*", "SJ*", "*JY" ],
        "wk_on_month":  False,
        "exp_rule":     "BOM+2FRI<3WED",
        "exp_time":     "07:00:00",
        "ul_map":       {
            "H": (-4, 0),
            "M": (-4, 0),
            "U": (-4, 0),
            "Z": (-4, 0)
        },
        "m_sym_offset": 0
    },
    "HG": {
        "monthly_sym":  "HXE",
        "weekly_syms":  [ "H*M", None, "H*W", None, "H*E" ],
        "wk_on_month":  False,
        "exp_rule":     "EOM-(4|5)BD",
        "exp_time":     "14:00:00",
        "ul_map": {
            "H": (-5, -1),
            "K": (-4, -1),
            "N": (-4, -1),
            "U": (-4, -1),
            "Z": (-5, -1)
        },
        "m_sym_offset": 1
    },
    "SI": {
        "monthly_sym":  "SO",
        "weekly_syms":  [ "M*S", None, "W*S", None, "SO*" ],
        "wk_on_month":  False,
        "exp_rule":     "EOM-(4|5)BD",
        "exp_time":     "14:00:00",
        "ul_map": {
            "H": (-5, -1),
            "K": (-4, -1),
            "N": (-4, -1),
            "U": (-4, -1),
            "Z": (-5, -1)
        },
        "m_sym_offset": 1
    },
    "GC": {
        "monthly_sym":  "OG",
        "weekly_syms":  [ "G*M", None, "G*W", None, "OG*" ],
        "wk_on_month":  False,
        "exp_rule":     "EOM-(4|5)BD",
        "exp_time":     "14:00:00",
        "ul_map": {
            "G": (-4, -1),
            "J": (-4, -1),
            "M": (-4, -1),
            "Q": (-4, -1),
            "V": (-4, -1),
            "Z": (-4, -1)
        },
        "m_sym_offset": 1
    },
    "GF": {
        "monthly_sym":  "GF",
        "weekly_syms":  [ None, None, None, None, None ],
        "wk_on_month":  False,
        "exp_rule":     "EOM-(1|2)THU",
        "exp_time":     "11:05:00",
        "ul_map":       {
            "F": (-1, 0),
            "H": (-1, 0),
            "J": (-1, 0),
            "K": (-1, 0),
            "Q": (-1, 0),
            "U": (-1, 0),
            "V": (-1, 0),
            "X": (-1, 0)
        },
        "m_sym_offset": 0
    },
    "LE": {
        "monthly_sym":  "LE",
        "weekly_syms":  [ None, None, None, None, None ],
        "wk_on_month":  False,
        "exp_rule":     "BOM+1FRI",
        "exp_time":     "11:05:00",
        "ul_map":       {
            "G": (-3, 0),
            "J": (-3, 0),
            "M": (-3, 0),
            "Q": (-3, 0),
            "V": (-3, 0),
            "Z": (-3, 0)
        },
        "m_sym_offset": 0
    },
    "HE": {
        "monthly_sym":  "HE",
        "weekly_syms":  [ None, None, None, None, None ],
        "wk_on_month":  False,
        "exp_rule":     "BOM+10BD",
        "exp_time":     "11:05:00",
        "ul_map":       {
            "G": (-1, 0),
            "J": (-1, 0),
            "K": (-1, 0),
            "M": (-1, 0),
            "N": (-1, 0),
            "Q": (-1, 0),
            "V": (-1, 0),
            "Z": (-1, 0)
        },
        "m_sym_offset": 0
    },
    "ZL": {
        "monthly_sym":  "OZL",
        "weekly_syms":  [ None, None, None, None, None ],   # not tradeable on IBKR
        "wk_on_month":  False,
        "exp_rule":     "EOM-2BD-1FRI",
        "exp_time":     "11:20:00",
        "ul_map":       {
            "F": (-3, -1),
            "H": (-4, -1),
            "K": (-4, -1),
            "N": (-4, -1),
            "Q": (-3, -1),
            "U": (-3, -1),
            "V": (-3, -1),
            "Z": (-4, -1)
        },
        "m_sym_offset": 1
    },
    "ZM": {
        "monthly_sym":  "OZM",
        "weekly_syms":  [ None, None, None, None, None ],   # not tradeable on IBKR
        "wk_on_month":  False,
        "exp_rule":     "EOM-2BD-1FRI",
        "exp_time":     "11:20:00",
        "ul_map":       {
            "F": (-3, -1),
            "H": (-4, -1),
            "K": (-4, -1),
            "N": (-4, -1),
            "Q": (-3, -1),
            "U": (-3, -1),
            "V": (-3, -1),
            "Z": (-4, -1)
        },
        "m_sym_offset": 1
    },
    "ZS": {
        "monthly_sym":  "OZS",
        "weekly_syms":  [ None, None, None, None, "ZS*" ],
        "wk_on_month":  False,
        "exp_rule":     "EOM-2BD-1FRI",
        "exp_time":     "11:20:00",
        "ul_map":       {
            "F": (-3, -1),
            "H": (-4, -1),
            "K": (-4, -1),
            "N": (-4, -1),
            "Q": (-3, -1),
            "U": (-3, -1),
            "X": (-4, -1)
        },
        "m_sym_offset": 1
    },
    "ZW": {
        "monthly_sym":  "OZW",
        "weekly_syms":  [ None, None, None, None, "ZW*" ],
        "wk_on_month":  False,
        "exp_rule":     "EOM-2BD-1FRI",
        "exp_time":     "11:20:00",
        "ul_map":       {
            "H": (-5, -1),
            "K": (-4, -1),
            "N": (-4, -1),
            "U": (-4, -1),
            "Z": (-5, -1)
        },
        "m_sym_offset": 1
    },
    "ZC": {
        "monthly_sym":  "OZC",
        "weekly_syms":  [ None, None, None, None, "ZC*" ],
        "wk_on_month":  False,
        "exp_rule":     "EOM-2BD-1FRI",
        "exp_time":     "11:20:00",
        "ul_map":       {
            "H": (-5, -1),
            "K": (-4, -1),
            "N": (-4, -1),
            "U": (-4, -1),
            "Z": (-5, -1)
        },
        "m_sym_offset": 1
    },
    "ZB": {
        "monthly_sym":  "OZB",
        "weekly_syms":  [ None, None, "WB*", None, "ZB*" ],
        "wk_on_month":  False,
        "exp_rule":     "EOM-2BD-1FRI",
        "exp_time":     "14:00:00",
        "ul_map":       {
            "H": (-4, 0),
            "M": (-4, 0),
            "U": (-4, 0),
            "Z": (-4, 0)
        },
        "m_sym_offset": 1
    },
    "ZN": {
        "monthly_sym":  "OZN",
        "weekly_syms":  [ None, None, "WY*", None, "ZN*" ],
        "wk_on_month":  False,
        "exp_rule":     "EOM-2BD-1FRI",
        "exp_time":     "14:00:00",
        "ul_map":       {
            "H": (-4, 0),
            "M": (-4, 0),
            "U": (-4, 0),
            "Z": (-4, 0)
        },
        "m_sym_offset": 1
    },
    "RB": {
        "monthly_sym":  "OB",
        "weekly_syms":  [ None, None, None, None, None ],
        "wk_on_month":  False,
        "exp_rule":     "EOM-4BD",
        "exp_time":     "14:00:00",
        "ul_map":       {
            "F": (-1, 0),
            "G": (-1, 0),
            "H": (-1, 0),
            "J": (-1, 0),
            "K": (-1, 0),
            "M": (-1, 0),
            "N": (-1, 0),
            "Q": (-1, 0),
            "U": (-1, 0),
            "V": (-1, 0),
            "X": (-1, 0),
            "Z": (-1, 0),
        },
        "m_sym_offset": 1
    },
    "HO": {
        "monthly_sym":  "OH",
        "weekly_syms":  [ None, None, None, None, None ],
        "wk_on_month":  False,
        "exp_rule":     "EOM-4BD",
        "exp_time":     "14:00:00",
        "ul_map":       {
            "F": (-1, 0),
            "G": (-1, 0),
            "H": (-1, 0),
            "J": (-1, 0),
            "K": (-1, 0),
            "M": (-1, 0),
            "N": (-1, 0),
            "Q": (-1, 0),
            "U": (-1, 0),
            "V": (-1, 0),
            "X": (-1, 0),
            "Z": (-1, 0),
        },
        "m_sym_offset": 1
    },
    "CL": {
        "monthly_sym":  "LO",
        "weekly_syms":  [ "ML*", None, "WL*", None, "LO*" ],
        "wk_on_month":  True,
        "exp_rule":     "25TH-(6|7)BD",
        "exp_time":     "14:00:00",
        "ul_map":       {
            "F": (-2, 0),
            "G": (-2, 0),
            "H": (-2, 0),
            "J": (-2, 0),
            "K": (-2, 0),
            "M": (-2, 0),
            "N": (-2, 0),
            "Q": (-2, 0),
            "U": (-2, 0),
            "V": (-2, 0),
            "X": (-2, 0),
            "Z": (-2, 0),
        },
        "m_sym_offset": 1
    },
    "NG": {
        "monthly_sym":  "LNE",
        "weekly_syms":  [ None, None, None, None, None ],   # not enough volume / liquidity to trade
        "wk_on_month":  False,
        "exp_rule":     "EOM-4BD",
        "exp_time":     "14:00:00",
        "ul_map":       {
            "F": (-1, 0),
            "G": (-1, 0),
            "H": (-1, 0),
            "J": (-1, 0),
            "K": (-1, 0),
            "M": (-1, 0),
            "N": (-1, 0),
            "Q": (-1, 0),
            "U": (-1, 0),
            "V": (-1, 0),
            "X": (-1, 0),
            "Z": (-1, 0),
        },
        "m_sym_offset": 1
    }

}
MONTHS      = {
    1:  "F",
    2:  "G",
    3:  "H",
    4:  "J",
    5:  "K",
    6:  "M",
    7:  "N",
    8:  "Q",
    9:  "U",
    10: "V",
    11: "X",
    12: "Z"
}
DAYS_OF_WEEK = {
    0: "MON",
    1: "TUE",
    2: "WED",
    3: "THU",
    4: "FRI"
}
#HOLIDAYS = USFederalHolidayCalendar().holidays(start = "1900-01-01", end = "2100-01-01")


class base_rec(IntEnum):

    date    = 0
    month   = 1
    year    = 2
    settle  = 3
    dte     = 4 


def get_expirations(
    sym:    str,
    recs:   List[base_rec]
):

    res         = []
    dfn         = OPT_DEFS[sym]
    rule        = dfn["exp_rule"]
    exp_time    = dfn["exp_time"]
    monthly_sym = dfn["monthly_sym"]
    weekly_syms = dfn["weekly_syms"]
    wk_on_month = dfn["wk_on_month"]
    year        = str(recs[0][base_rec.year])[-1]
    offset      = dfn["m_sym_offset"]
    ul_exp      = Timestamp(recs[0][base_rec.date]) + DateOffset(days = recs[0][base_rec.dte])
    ul_sym      = recs[0][base_rec.month] + str(recs[0][base_rec.year][-1])
    ul_month    = recs[0][base_rec.month]

    if ul_month not in dfn["ul_map"]:
        
        # some futures have contracts with no options, such as GC
        
        return res

    months_ts   = [ ul_exp + MonthBegin(i) for i in range(*dfn["ul_map"][ul_month]) ]
    monthly_exp = None
    weekly_exp  = None

    for bom in months_ts:

        # MONTHLY EXPIRATION

        eom = bom + MonthEnd(1)

        if rule == "EOM-4BD":
            
            # fourth last business day of the month

            monthly_exp = bdate_range(bom, eom, freq = "C")[-4]
        
        elif rule == "EOM-2BD-1FRI":

            # first friday prior to the second last business day of the month;
            # if this is not a business day, then the day prior

            cutoff      = bdate_range(bom, eom)[-3]
            fri         = date_range(bom, cutoff, freq = "W-FRI")[-1]
            monthly_exp = fri if BDay().is_on_offset(fri) else fri - BDay()

        elif rule == "25TH-(6|7)BD":

            # 3 business days prior to the underlying futures' expiration date

            ref         = bom + DateOffset(days = 24)
            monthly_exp = ref - 6 * BDay() if BDay().is_on_offset(ref) else ref - 7 * BDay()

        elif rule == "BOM+10BD":

            # tenth business day of the month

            monthly_exp = bdate_range(bom, eom, freq = "C")[9]

        elif rule == "BOM+1FRI":

            # first friday of month

            monthly_exp = date_range(bom, eom, freq = "W-FRI")[0]

        elif rule == "EOM-(1|2)THU":

            # last thursday of month if business day; else 2nd last thursday

            rng         = date_range(bom, eom, freq = "W-THU")
            monthly_exp = rng[-1] if BDay().is_on_offset(rng[-1]) else rng[-2]

        elif rule == "EOM-(4|5)BD":

            # 4th last business day of the month, unless friday (or holiday); else 5th last business day of month

            monthly_exp = bdate_range(bom, eom, freq = "C")[-4]
            monthly_exp = monthly_exp if monthly_exp.day_of_week != 4 else monthly_exp - BDay()

        elif rule == "BOM+2FRI<3WED":

            # 2nd friday of the month prior to the 3rd wednesday of the month

            third_wed   = date_range(bom, eom, freq = "W-WED")[2]
            monthly_exp = date_range(bom, third_wed, freq = "W-FRI")[-2]
        
        elif rule == "3FRI":

            monthly_exp = date_range(bom, eom, freq = "W-FRI")[2]

        # exclude first monthly expiration (it was for the previous underlying)
        # unless it is the only monthly expiration

        if bom != months_ts[0] or len(months_ts) == 1:

            monthly_str     = f'{monthly_exp.strftime(DATE_FMT)}T{exp_time}'
            adj_month       = monthly_exp.month + offset
            sym_month       = adj_month if adj_month <= 12 else adj_month - 12
            monthly_sym_    = monthly_sym + MONTHS[sym_month] + (year if adj_month <= 12 else str((int(year) + 1) % 10))
            
            res.append(
                ( 
                    monthly_str, 
                    "M", 
                    monthly_sym_,
                    ul_sym
                )
            )

        # WEEKLY EXPIRATIONS

        # valid expirations:
        #
        # first month:  from expiration -> eom
        # last month:   from bom -> expiration
        # other months: all days in month

        i           = bom
        j           = eom if bom != months_ts[-1] else monthly_exp

        for k in range(len(weekly_syms)):

            weekly_sym  = weekly_syms[k]

            if weekly_sym:

                day_of_week = DAYS_OF_WEEK[k]
                rng         = date_range(i, j, freq = f"W-{day_of_week}")

                for l in range(len(rng)):

                    weekly_exp = rng[l]

                    # check validity of weekly expiration (assume business day; no holidays implemented yet)

                    if bom == months_ts[0]:
                        
                        if wk_on_month:

                            if weekly_exp < monthly_exp:

                                continue

                        else:

                            if weekly_exp <= monthly_exp:

                                continue
                    
                    elif bom == months_ts[-1]:

                        if weekly_exp >= monthly_exp:

                            continue

                    # valid expiration
                    # assumption: weekly month codes are not offset (i.e. always equal to the month in which they expire)

                    weekly_str      = f'{weekly_exp.strftime(DATE_FMT)}T{exp_time}'
                    week_of_month   = str(l + 1)
                    weekly_sym_     = weekly_sym.replace("*", week_of_month) + MONTHS[monthly_exp.month] + year

                    res.append(
                        (
                            weekly_str,
                            "W",
                            weekly_sym_,
                            ul_sym
                        )
                    )

    res = sorted(res, key = lambda r: r[0])

    return res


def get_records_by_contract(
    symbol: str, 
    start:  str, 
    end:    str,
    trim:   bool = True         # trim most contracts without expiried options 
):

    recs = cat_df(
            "futs",
            symbol, 
            start, 
            end
        ).select(
            [
                "date",
                "month",
                "year",
                "settle",
                "dte"
            ]
        ).rows()

    cutoff = None

    if trim:

        cutoff = str(datetime.now().year)[2:]

    res = {}

    for rec in recs:

        contract_id = ( rec[base_rec.month],  rec[base_rec.year][2:] )

        if contract_id not in res:

            res[contract_id] = []

        res[contract_id].append(rec)

    if cutoff:

        tmp = {}

        for contract_id, recs in res.items():

            if  contract_id[1] <= cutoff:

                tmp[contract_id] = recs

        res = tmp

    return res


def get_indexed_opt_series(
    symbol:     str,            # e.g. "ZC"
    cur_dt:     str,            # or start for window of interest ( YYYY-MM-DDTHH:MM:SS )
    exp_dt:     str,            # for option of interest (no time, only date)
    start_date: str,            # use data between "start_date" and "end_date" for historical valuation
    end_date:   str,                
    trim:       bool = True,    # trim most contracts without expiried options
    inc_stl:    bool = True     # appends the settlement on expiration day as 0 index. set "False" if not valuing until expiration.
):

    max_index   = int(Timedelta(Timestamp(exp_dt) - Timestamp(cur_dt)).total_seconds() / 60)
    index       = {}

    # obtain settlements from daily data
    
    records_by_contract = get_records_by_contract(symbol, start_date, end_date, trim)

    # build index headers

    for id, rows in records_by_contract.items():

        date_idx    = [ row[0] for row in rows ]
        ul_conid    = f"{symbol}{id[0]}{id[1]}_FUT_CME"
        ul_bars     = get_bars(ul_conid)
        ul_dts      = [ f"{bar[bar_rec.date]}T{bar[bar_rec.time]}" for bar in ul_bars ]
        ul_last     = [ bar[bar_rec.last] for bar in ul_bars ]
        exps        = get_expirations(symbol, rows)

        for exp in exps:
            
            try:

                exp_dt      = exp[0]                    # re-assign, no need for original
                exp_date    = exp_dt.split("T")[0]
                i           = date_idx.index(exp_date)
                settle      = rows[i][3]
                header      = (
                                ul_conid,
                                exp[2],
                                exp[0],
                                settle   
                            )
                exp_ts      = Timestamp(exp_dt)
                min_dt      = (exp_ts - Timedelta(minutes = max_index)).strftime(DT_FMT)
                
                i = bisect_left(ul_dts, min_dt)
                j = bisect_right(ul_dts, exp_dt)

                x   = ul_dts[i:j]
                idx = [ int(Timedelta(exp_ts - Timestamp(dt)).total_seconds() / 60) for dt in x ]
                y   = ul_last[i:j]

                if inc_stl:

                    # append settlement at 0 index

                    x.append(exp_dt)
                    idx.append(0)
                    y.append(settle)

                index[header] = {
                                    "x":    x,
                                    "idx":  idx,
                                    "y":    y
                                }

            except ValueError:

                # no settlement found for this expiration, skip

                continue

    return index