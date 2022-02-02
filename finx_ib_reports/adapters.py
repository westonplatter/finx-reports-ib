import pandas as pd
from pydantic import BaseModel

from finx_ib_reports.custom_flex_report import CustomFlexReport


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
