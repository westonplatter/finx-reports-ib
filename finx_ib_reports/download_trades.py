import json
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


def get_ib_json(configs: Dict) -> Dict:
    """Returns the IB json value as dict

    Args:
        configs (Dict): env file contents

    Returns:
        dict: IB json as dict
    """
    return json.loads(configs["IB_JSON"])


def get_discord_webhook_url(configs: Dict) -> str:
    """Returns the discord portfolios webhook

    Args:
        configs (Dict): env file contents

    Returns:
        str: discord webhook url
    """
    return configs["PORTFOLIOS_DISCORD_WEBHOOK_URL"]


# TODO - refactor this to work with execute_discord_for_accounts
# def execute(report_name: str, cache: bool = False, file_name: str = ".env"):
#     """Execute the trades dowload process

#     Args:
#         report_name (str): report name as it exists in the env file. Eg, report_name=xyz, in env file=IB_REPORT_ID_XYZ
#         cache (bool): cache XML
#         file_name (str): env file name. Defaults to ".env".

#     """
#     configs = get_config(file_name)
#     flex_token = get_flex_token(configs)
#     query_id = get_query_id_for_report_name(configs, report_name)

#     report = fetch_report(flex_token, query_id, cache_report_on_disk=cache)
#     process_report(report)


# TODO - execute_discord_for_accounts
# def execute_discord(report_name: str, cache: bool = False, file_name: str = ".env"):
#     configs = get_config(file_name)
#     flex_token = get_flex_token(configs)
#     discord_webhook_url = get_discord_webhook_url(configs)
#     query_id = get_query_id_for_report_name(configs, report_name)

#     report = fetch_report(flex_token, query_id, cache_report_on_disk=cache)
#     process_report_discord(report, discord_webhook_url=discord_webhook_url)


def execute_discord_for_accounts(
    report_name: str, cache: bool = False, file_name: str = ".env"
):
    configs = get_config(file_name)
    data = get_ib_json(configs)

    if "accounts" not in data:
        return None

    for account in data["accounts"]:
        # ensure the account is setup for the report, if not skip
        query_id = int(account[report_name.lower()])
        if query_id <= 0:
            continue

        flex_token = account["flex_token"]
        discord_webhook_url = get_discord_webhook_url(configs)

        # get report
        report = fetch_report(flex_token, query_id, cache_report_on_disk=cache)

        # send notifications
        process_report_discord(report, discord_webhook_url=discord_webhook_url)
