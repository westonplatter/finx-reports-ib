import time
from typing import Dict, List

import pandas as pd
from dotenv import dotenv_values
from ib_insync.flexreport import FlexReport
from pydantic import BaseModel


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


class CustomFlexReport(FlexReport):
    COL_ACCOUNT_ID = "accountId"

    def account_ids(self) -> List[str]:
        account_ids = self.df("AccountInformation")[self.COL_ACCOUNT_ID].values.tolist()
        return list(set(account_ids))

    def open_positions_by_account_id(self, account_id: str) -> pd.DataFrame:
        df = (
            self.df("OpenPosition")
            .query(f"{self.COL_ACCOUNT_ID} == @account_id")
            .copy()
        )
        df = df.query("levelOfDetail == 'LOT'").copy()
        df.openDateTime = parse_datetime_series(df.openDateTime)
        df.holdingPeriodDateTime = parse_datetime_series(df.holdingPeriodDateTime)
        df.reportDate = parse_date_series(df.reportDate)
        return df

    def trades_by_account_id(self, account_id: str) -> pd.DataFrame:
        df = self.df("Trade")
        if df is None:
            return
        df = df.query(f"{self.COL_ACCOUNT_ID} == @account_id").copy()
        df.dateTime = parse_datetime_series(df.dateTime)
        df.orderTime = parse_datetime_series(df.orderTime)
        df.tradeDate = parse_date_series(df.tradeDate)
        return df

    def closed_trades_by_account_id(self, account_id: str) -> pd.DataFrame:
        df = self.trades_by_account_id(account_id)
        if df is None:
            return
        return df.query("openCloseIndicator == 'C'").copy()

    def orders_by_account_id(self, account_id: str) -> pd.DataFrame:
        return self.df("Order").query(f"{self.COL_ACCOUNT_ID} == @account_id").copy()

    def change_in_nav_by_account_id(self, account_id: str) -> pd.DataFrame:
        return (
            self.df("ChangeInNAV").query(f"{self.COL_ACCOUNT_ID} == account_id").copy()
        )
