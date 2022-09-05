import re

import pandas as pd


def parse_datetime_series(raw_series: pd.Series) -> pd.Series:
    FORMAT = "%Y-%m-%d;%H%M%S"
    raw_series = raw_series.replace(r"", pd.NaT)
    series = pd.to_datetime(raw_series, errors="raise", format=FORMAT)
    series = series.dt.tz_localize(tz="US/Eastern")
    return series


def parse_date_series(raw_series: pd.Series) -> pd.Series:
    FORMAT = "%Y-%m-%d"
    raw_series = raw_series.replace(r"", pd.NaT)
    series = pd.to_datetime(raw_series, errors="raise", format=FORMAT).dt.date
    return series


class Mutations:
    @classmethod
    def columns_to_snake_case(cls, df) -> None:
        def camel_to_snake(name):
            name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
            return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

        snake_case_cols = {}
        for col in df.columns:
            snake_case_cols[col] = camel_to_snake(col)
        df.rename(columns=snake_case_cols, inplace=True)


class Transforms:
    @classmethod
    def add_strike(cls, df) -> None:
        ddf = df.query('asset_category.isin(["OPT", "FOP"])').description.str.split(
            " ", expand=True
        )
        df["strike"] = pd.to_numeric(ddf[2])

    @classmethod
    def convert_date_time(cls, df) -> None:
        df.dateTime = parse_datetime_series(df.dateTime)

    @classmethod
    def convert_open_date_time(cls, df) -> None:
        df.openDateTime = parse_datetime_series(df.openDateTime)

    @classmethod
    def convert_holding_period_date_time(cls, df) -> None:
        df.holdingPeriodDateTime = parse_datetime_series(df.holdingPeriodDateTime)

    @classmethod
    def convert_report_date(cls, df) -> None:
        df.reportDate = parse_date_series(df.reportDate)
