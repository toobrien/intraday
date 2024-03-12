import polars as pl


def strptime(
    df:         pl.DataFrame,
    from_col:   str,
    to_col:     str, 
    FMT:        str, 
    tz:         str
) -> pl.DataFrame:

    if df[from_col].dtype == pl.String:

        df = df.with_columns(
            pl.col(
                from_col
            ).map_elements(
                lambda dt: f"{dt[0:10]}T{dt[10:]}+0000" if " " in dt else dt # hack, fix serialization in dbn.get_csv
            ).cast(
                pl.Datetime
            ).dt.convert_time_zone(
                tz
            ).dt.strftime(
                FMT
            ).alias(
                to_col
            )
        )
    
    else:

        # datetime

        df = df.with_columns(
            pl.col(
                from_col
            ).dt.convert_time_zone(
                tz
            ).dt.strftime(
                FMT
            ).alias(
                to_col
            )
        )

    return df