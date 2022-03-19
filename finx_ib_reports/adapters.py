from datetime import timedelta, datetime
import pandas as pd
from pydantic import BaseModel
from pytz import timezone
import requests

from finx_ib_reports.custom_flex_report import CustomFlexReport
from finx_ib_reports.custom_flex_report import parse_date_series


class ReportOutputAdapterCSV(BaseModel):
    """Adapter responsible for writting Report Sections to disk."""

    class Config:
        arbitrary_types_allowed = True

    data_folder: str = "data"
    account_id: str
    report: CustomFlexReport

    def gen_file_name(self, name: str) -> str:
        return f"{self.data_folder}/{self.account_id}_{name}.csv"

    def _put_df(self, df: pd.DataFrame, section: str) -> None:
        fn = self.gen_file_name(section)
        df.to_csv(fn)

    def put_all(self):
        self.put_trades()
        self.put_close_trades()
        self.put_open_positions()

    def put_trades(self):
        df = self.report.trades_by_account_id(self.account_id)
        self._put_df(df, "trades")

    def put_close_trades(self):
        df = self.report.closed_trades_by_account_id(self.account_id)
        self._put_df(df, "close_trades")

    def put_open_positions(self):
        df = self.report.open_positions_by_account_id(self.account_id)
        self._put_df(df, "open_positions")


class ReportOutputAdapterDiscord(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    account_id: str
    report: CustomFlexReport
    discord_webhook_url: str
    expiring_positions_within_x_days: int = 10

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
