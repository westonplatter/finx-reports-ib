import time
from typing import Dict, List

import pandas as pd
from dotenv import dotenv_values
from ib_insync.flexreport import FlexReport
from pydantic import BaseModel


class CustomFlexReport(FlexReport):
    def account_ids(self) -> List[str]:
        account_ids = self.df("AccountInformation")["accountId"].values.tolist()
        return list(set(account_ids))

    def open_positions_by_account_id(self, account_id: str) -> pd.DataFrame:
        return self.df("OpenPosition").query("accountId == @account_id").copy()

    def trades_by_account_id(self, account_id: str) -> pd.DataFrame:
        return self.df("Trade").query("accountId == @account_id").copy()

    def closed_trades_by_account_id(self, account_id: str) -> pd.DataFrame:
        return self.trades_by_account_id(account_id).query("openCloseIndicator == 'C'").copy()

    def orders_by_account_id(self, account_id: str) -> pd.DataFrame:
        return self.df("Order").query("accountId == @account_id").copy()


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


def process_report(report: CustomFlexReport):
    for account_id in report.account_ids():
        output_adapter = ReportOutputAdapterCSV(data_folder="data", account_id=account_id, report=report)
        output_adapter.put_all()


def fetch_report(flex_token: int, query_id: int, cache_report_on_disk: bool = False) -> CustomFlexReport:
    """Fetch report. Optionally save to disk (helpful for debugging)

    Args:
        flex_token (int): IB Flex Token
        query_id (int): IB Report Query Id
        cache_report_on_disk (bool, optional): Cache XML content on disk. Helpful for debugging. Defaults to False.

    Returns:
        CustomFlexReport: [description]
    """
    report = CustomFlexReport(token=flex_token, queryId=query_id)

    # save report
    if cache_report_on_disk:
        epoch_time = int(time.time())
        report_path = f"data/flex_report_{epoch_time}.xml"
        report.save(report_path)

    return report


def get_config(file_name: str) -> Dict:
    """Returns `file_name` lines as Dict. Uses dotenv

    Args:
        file_name (str): env file name. Default = .env

    Returns:
        Dict:
    """
    return dotenv_values(file_name)


def get_query_id_for_report_name(configs: Dict, report_name: str) -> int:
    """Returns query id for "IB_REPORT_ID_{report_name}"

    Args:
        configs (Dict): env file contents
        report_name (str): IB_REPORT_ID_{this}

    Returns:
        int: IB report query id
    """
    key = f"IB_REPORT_ID_{report_name.upper()}"
    assert key in configs, f".env config file did not contain key={key}"
    return int(configs[key])


def get_flex_token(configs: Dict) -> int:
    """Returns the IB Flex Token value

    Args:
        configs (Dict): env file contents

    Returns:
        int: IB Flex token
    """
    return int(configs["IB_FLEX_TOKEN"])


def execute(report_name: str, file_name: str = ".env"):
    """Execute the trades dowload process

    Args:
        report_name (str): report name as it exists in the env file. Eg, report_name=xyz, in env file=IB_REPORT_ID_XYZ
        file_name (str): env file name. Defaults to ".env".

    """
    configs = get_config(file_name)
    flex_token = get_flex_token(configs)
    query_id = get_query_id_for_report_name(configs, report_name)

    report = fetch_report(flex_token, query_id)
    process_report(report)
