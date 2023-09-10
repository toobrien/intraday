from util.rec_tools import get_tas


MONTHS = [ "F", "G", "H", "J", "K", "M", "N", "Q", "U", "V", "X", "Z"]


def get_term_ids(init_symbol: str, n_months: int):

    symbol      = init_symbol[:-3]
    first_month = init_symbol[-3]
    year        = int(init_symbol[-2:])
    
    results = []
    
    i = MONTHS.index(first_month)

    while n_months > 0:

        results.append(f"{symbol}{MONTHS[i]}{year}")

        year        =  year if i != 11 else year + 1
        i           =  (i + 1) % 12
        n_months    -= 1
    
    return results


def get_terms(
    init_symbol:    str,
    multiplier:     float,
    n_months:       int,
    fmt:            str = None,
    start:          str = None,
    end:            str = None
):

    term_ids    = get_term_ids(init_symbol, n_months)
    results     = {}

    for term_id in term_ids:

        try:

            recs = get_tas(f"{term_id}_FUT_CME", multiplier, fmt, start, end)

            if recs:

                results[term_id] = recs

        except Exception as e:

            # print exception and keep going on file not found
            # (for non-serial contracts)

            print(e)
    
    return results