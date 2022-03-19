import time
from typing import Dict, List

import pandas as pd
from dotenv import dotenv_values
from ib_insync.flexreport import FlexReport
from pydantic import BaseModel

from finx_ib_reports.adapters import ReportOutputAdapterCSV, ReportOutputAdapterDiscord
from finx_ib_reports.custom_flex_report import CustomFlexReport


def process_report(report: CustomFlexReport):
    for account_id in report.account_ids():
        output_adapter = ReportOutputAdapterCSV(
            data_folder="data", account_id=account_id, report=report
        )
        output_adapter.put_all()


def process_report_discord(report: CustomFlexReport, discord_webhook_url: str):
    for account_id in report.account_ids():
        output_adapter = ReportOutputAdapterDiscord(
            account_id=account_id,
            report=report,
            discord_webhook_url=discord_webhook_url,
        )
        output_adapter.put_notifications()


def fetch_report(
    flex_token: int, query_id: int, cache_report_on_disk: bool = False
) -> CustomFlexReport:
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


def load_report(xml_file_path: str) -> CustomFlexReport:
    """Load CustomFlexReport from provided file path

    Args:
        xml_file_path (str): file path to the cached XML file

    Returns:
        CustomFlexReport: report
    """
    report = CustomFlexReport()
    report.load(xml_file_path)
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


def get_discord_webhook_url(configs: Dict) -> str:
    """Returns the discord portfolios webhook

    Args:
        configs (Dict): env file contents

    Returns:
        str: discord webhook url
    """
    return configs["PORTFOLIOS_DISCORD_WEBHOOK_URL"]


def execute(report_name: str, cache: bool = False, file_name: str = ".env"):
    """Execute the trades dowload process

    Args:
        report_name (str): report name as it exists in the env file. Eg, report_name=xyz, in env file=IB_REPORT_ID_XYZ
        cache (bool): cache XML
        file_name (str): env file name. Defaults to ".env".

    """
    configs = get_config(file_name)
    flex_token = get_flex_token(configs)
    query_id = get_query_id_for_report_name(configs, report_name)

    report = fetch_report(flex_token, query_id, cache_report_on_disk=cache)
    process_report(report)


def execute_discord(report_name: str, cache: bool = False, file_name: str = ".env"):
    configs = get_config(file_name)
    flex_token = get_flex_token(configs)
    discord_webhook_url = get_discord_webhook_url(configs)
    query_id = get_query_id_for_report_name(configs, report_name)

    report = fetch_report(flex_token, query_id, cache_report_on_disk=cache)
    process_report_discord(report, discord_webhook_url=discord_webhook_url)
