from enum import Enum
from typing import List

import pandas as pd
from ib_insync.flexreport import FlexReport

from finx_ib_reports.transforms import parse_date_series, parse_datetime_series


class CustomFlexReport(FlexReport):
    def account_ids(self) -> List[str]:
        account_ids = self.df("AccountInformation")["accountId"].values.tolist()
        return list(set(account_ids))

    def open_positions_by_account_id(self, account_id: str) -> pd.DataFrame:
        df = self.df("OpenPosition").query("accountId == @account_id").copy()
        df = df.query("levelOfDetail == 'LOT'").copy()
        df.openDateTime = parse_datetime_series(df.openDateTime)
        df.holdingPeriodDateTime = parse_datetime_series(df.holdingPeriodDateTime)
        df.reportDate = parse_date_series(df.reportDate)
        return df

    def trades_by_account_id(self, account_id: str) -> pd.DataFrame:
        df = self.df("Trade")
        if df is None:
            return
        df = df.query("accountId == @account_id").copy()
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
        return self.df("Order").query("accountId == @account_id").copy()

    def change_in_nav_by_account_id(self, account_id: str) -> pd.DataFrame:
        return self.df("ChangeInNAV").query("accountId == account_id").copy()
