import polars as pl


def strptime(
    df:         pl.DataFrame,
    from_col:   str,
    to_col:     str, 
    FMT:        str, 
    utc_offset: int
) -> pl.DataFrame:
    
    df = df.with_columns(
        pl.col(
            from_col
        ).dt.offset_by(
            f"{utc_offset}h"
        ).dt.strftime(
            FMT
        ).alias(
            to_col
        )
    )

    return df