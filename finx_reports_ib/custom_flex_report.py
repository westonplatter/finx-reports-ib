from typing import List

import pandas as pd
from ib_insync.flexreport import FlexReport

from finx_reports_ib.transforms import parse_date_series, parse_datetime_series


def filter_df_by_account_id(df: pd.DataFrame, account_id: str) -> pd.DataFrame:
    """Return df with rows for account_id."""
    return df[df.accountId == account_id].copy()


def df_none_or_empty(df: pd.DataFrame) -> bool:
    """Return True if df is not None and not empty."""
    if df is None or df.empty:
        return True
    else:
        return False


class CustomFlexReport(FlexReport):
    def account_ids(self) -> List[str]:
        return list(self.df("AccountInformation")["accountId"].unique())

    def open_positions_by_account_id(self, account_id: str) -> pd.DataFrame:
        df = self.df("OpenPosition")
        
        if df_none_or_empty(df):
            return None

        df = filter_df_by_account_id(df, account_id)

        if df_none_or_empty(df):
            return None

        # only return LOT level rows (ie, disregard aggregate rows)
        df = df.query("levelOfDetail == 'LOT'").copy()
        
        # parse datetime columns
        df.openDateTime = parse_datetime_series(df.openDateTime)
        df.holdingPeriodDateTime = parse_datetime_series(df.holdingPeriodDateTime)
        df.reportDate = parse_date_series(df.reportDate)

        return df

    def trades_by_account_id(self, account_id: str) -> pd.DataFrame:
        """
        See `expected_columns` variable in source code for column names.

        Returns:
            pd.DataFrame: df of executed trades for a specific account.
        """
        df = self.df("Trade")

        if df_none_or_empty(df):
            return None

        df = filter_df_by_account_id(df, account_id)

        if df_none_or_empty(df):
            return None
        
        # ensure the expected columns come through
        expected_columns = [
            "accountId",
            "acctAlias",
            "model",
            "currency",
            "fxRateToBase",
            "assetCategory",
            "symbol",
            "description",
            "conid",
            "securityID",
            "securityIDType",
            "cusip",
            "isin",
            "listingExchange",
            "underlyingConid",
            "underlyingSymbol",
            "underlyingSecurityID",
            "underlyingListingExchange",
            "issuer",
            "multiplier",
            "strike",
            "expiry",
            "tradeID",
            'putCall',
            "reportDate",
            "principalAdjustFactor",
            "dateTime",
            "tradeDate",
            "settleDateTarget",
            "transactionType",
            "exchange",
            "quantity",
            "tradePrice",
            "tradeMoney",
            "proceeds",
            "taxes",
            "ibCommission",
            "ibCommissionCurrency",
            "netCash",
            "closePrice",
            "openCloseIndicator",
            "notes",
            "cost",
            "fifoPnlRealized",
            "fxPnl",
            "mtmPnl",
            "origTradePrice",
            "origTradeDate",
            "origTradeID",
            "origOrderID",
            "clearingFirmID",
            "transactionID",
            "buySell",
            "ibOrderID",
            "ibExecID",
            "brokerageOrderID",
            "orderReference",
            "volatilityOrderLink",
            "exchOrderId",
            "extExecID",
            "orderTime",
            "openDateTime",
            "holdingPeriodDateTime",
            "whenRealized",
            "whenReopened",
            "levelOfDetail",
            "changeInPrice",
            "changeInQuantity",
            "orderType",
            "traderID",
            "isAPIOrder",
            "accruedInt",
        ]
        df = df[expected_columns].copy()

        # parse datetime columns
        df.dateTime = parse_datetime_series(df.dateTime)
        df.orderTime = parse_datetime_series(df.orderTime)
        df.tradeDate = parse_date_series(df.tradeDate)
        
        # final df
        return df

    def closed_trades_by_account_id(self, account_id: str) -> pd.DataFrame:
        df = self.trades_by_account_id(account_id)

        if df_none_or_empty(df):
            return None

        # only get closed trades
        df = df.query("openCloseIndicator == 'C'").copy()

        return df

    def orders_by_account_id(self, account_id: str) -> pd.DataFrame:
        df = self.df("Order")
        df = filter_df_by_account_id(df, account_id)
        return df

    def change_in_nav_by_account_id(self, account_id: str) -> pd.DataFrame:
        df = self.df("ChangeInNAV")
        df = filter_df_by_account_id(df, account_id)
        return df
