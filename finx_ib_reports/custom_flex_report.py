import time
from typing import Dict, List

import pandas as pd
from dotenv import dotenv_values
from ib_insync.flexreport import FlexReport
from pydantic import BaseModel


def parse_datetime_series(raw_series: pd.Series) -> pd.Series:
    """Transform pd.Series of strings into a pd.Series of datetimes"""
    DATETIME_FORMAT = "%Y-%m-%d;%H%M%S"
    raw_series = raw_series.replace(r"", pd.NaT)
    series = pd.to_datetime(raw_series, errors="raise", format=DATETIME_FORMAT)
    series = series.dt.tz_localize(tz="US/Eastern")
    return series


def parse_date_series(raw_series: pd.Series) -> pd.Series:
    """
    Transform pd.Series of strings into a pd.Series of dates

    NOTE - has different format than parse_datetime_series
    """
    DATE_FORMAT = "%Y-%m-%d"
    raw_series = raw_series.replace(r"", pd.NaT)
    series = pd.to_datetime(raw_series, errors="raise", format=DATE_FORMAT)
    series = series.dt.tz_localize(tz="US/Eastern")
    return series.dt.date


class CustomFlexReport(FlexReport):
    def account_ids(self) -> List[str]:
        account_ids = self.df("AccountInformation")["accountId"].values.tolist()
        return list(set(account_ids))

    def open_positions_by_account_id(self, account_id: str) -> pd.DataFrame:
        """Returns df of option positions.

        NOTE - levelOfDetail = 'LOT'

        Args:
            account_id (str): _description_

        Returns:
            pd.DataFrame: _description_
        """
        df = (self.df("OpenPosition").query("accountId == @account_id").query("levelOfDetail == 'LOT'")).copy()
        # transform datetime columns from string to datetime
        df.loc[:, "openDateTime"] = parse_datetime_series(df.openDateTime)
        df.loc[:, "holdingPeriodDateTime"] = parse_datetime_series(df.holdingPeriodDateTime)
        df.loc[:, "reportDate"] = parse_date_series(df.reportDate)
        return df

    def trades_by_account_id(self, account_id: str) -> pd.DataFrame:
        """Return df of trades

        Args:
            account_id (str): _description_

        Returns:
            pd.DataFrame: _description_
        """
        df = (self.df("Trade").query("accountId == @account_id")).copy()
        # transform datetime columns from string to datetime
        df.loc[:, "dateTime"] = parse_datetime_series(df.dateTime)
        df.loc[:, "orderTime"] = parse_datetime_series(df.orderTime)
        return df

    def closed_trades_by_account_id(self, account_id: str) -> pd.DataFrame:
        """Returns df of closed trades account (subset of `trades_by_account_id`"""
        df = (self.trades_by_account_id(account_id).query("openCloseIndicator == 'C'")).copy()
        return df

    def orders_by_account_id(self, account_id: str) -> pd.DataFrame:
        """Returns df of orders by account"""
        df = (self.df("Order").query("accountId == @account_id")).copy()
        return df

    def change_in_nav_by_account_id(self, account_id: str) -> pd.DataFrame:
        """Returns df of NAV by account id"""
        df = (self.df("ChangeInNAV").query("accountId == account_id")).copy()
        return df
