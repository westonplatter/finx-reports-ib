from datetime import datetime, timedelta

from loguru import logger
import pandas as pd
import requests
from pydantic import BaseModel
from pytz import timezone

from finx_ib_reports.custom_flex_report import CustomFlexReport, parse_date_series

# class ReportOutputAdapterShell(BaseModel):
#     class Config:
#         arbitrary_types_allowed = True
#     report: CustomFlexReport
#     def confirm_sections(self):
#         expected_sections = ["Trades"]
#         for section in expected_sections:
#           # do confirmation work here


class ReportOutputAdapterCSV(BaseModel):
    """Adapter responsible for writing Report Sections to disk."""

    class Config:
        arbitrary_types_allowed = True

    data_folder: str = "data"
    report: CustomFlexReport

    def process_accounts(self):
        for account_id in self.report.account_ids():
            logger.info(f"CSV output adapter for {account_id}")
            self.put_all(aid=account_id)

    def put_all(self, aid: str):
        self.put_trades(aid)
        self.put_close_trades(aid)
        self.put_open_positions(aid)

    def _gen_file_name(self, aid: str, name: str) -> str:
        return f"{self.data_folder}/{aid}_{name}.csv"

    def _put_df(self, aid: str, df: pd.DataFrame, section: str) -> None:
        fn = self._gen_file_name(aid, section)
        df.to_csv(fn)

    def put_trades(self, aid):
        df = self.report.trades_by_account_id(aid)
        if df is None:
            logger.warning(
                f"AccountId={aid}. Unable to get trades data from report. "
                "Does the Flex Report have Trades turned on?"
            )
            return
        self._put_df(aid, df, "trades")

    def put_close_trades(self, aid):
        df = self.report.closed_trades_by_account_id(aid)
        if df is None:
            logger.warning(
                f"AccountId={aid}. Unable to get trades data from report. "
                "Does the Flex Report have Trades turned on?"
            )
            return
        self._put_df(aid, df, "close_trades")

    def put_open_positions(self, aid):
        df = self.report.open_positions_by_account_id(aid)
        if df is None:
            logger.warning(
                f"AccountId={aid}. Unable to get positions data from report. "
                "Does the Flex Report have Positions turned on?"
            )
            return
        self._put_df(aid, df, "open_positions")


class ReportOutputAdapterDiscord(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    account_id: str
    report: CustomFlexReport
    discord_webhook_url: str
    expiring_positions_within_x_days: int = 4

    @property
    def public_account_id(self):
        """Only publish the first 3 digits of account"""
        return self.account_id[0:4]

    def put_notifications(self):
        """Main method called. Calls into specific functions"""
        self.put_expiry_notifications()

    def put_expiry_notifications(self):
        """Notify discord with expiring positions in X days"""
        expiring_positions = self._get_expiring_positions(
            within_x_days=self.expiring_positions_within_x_days
        )

        # gen message
        content = f"Portfolio {self.public_account_id}"
        for _, row in expiring_positions.iterrows():
            content += f"\n> {self.public_account_id} | {row.remainingDays.days}d | {row.symbol}"

        # send message if there are positions
        if not expiring_positions.empty:
            content = (
                f".\n{len(expiring_positions.index)} positions to roll in {content}"
            )
        else:
            content = f".\n{self.public_account_id} - nothing to roll"

        data = {"content": content}
        requests.post(self.discord_webhook_url, json=data)

    def _get_expiring_positions(self, within_x_days: int) -> pd.DataFrame:
        """Among open positions, get expiring positions within X days"""
        df = self.report.open_positions_by_account_id(self.account_id)

        # get latest positions
        dt = datetime.now(tz=timezone("US/Eastern"))
        while True:
            if len(df[df["reportDate"] == dt.date()].index) > 0:
                break
            dt = dt - timedelta(days=1)
        xdf = df[df["reportDate"] == dt.date()].copy()

        # slim down to expiry specific data
        xdf = (
            xdf.groupby(["symbol", "assetCategory", "accountId", "expiry"])
            .agg({"fifoPnlUnrealized": "sum", "position": "sum"})
            .reset_index()
        )

        # get positions expiring within X days
        mask = xdf["expiry"] != ""
        xdf.loc[~mask, "expiry"] = None
        xdf.loc[mask, "remainingDays"] = (
            parse_date_series(xdf.loc[mask, "expiry"]) - dt.date()
        )
        expiring_positions = xdf[
            xdf["remainingDays"] <= timedelta(days=within_x_days)
        ].copy()
        return expiring_positions
