import time
import warnings

from loguru import logger

from ngv_ibkr_reports.adapters import (
    ReportOutputAdapterCSV,
    ReportOutputAdapterDiscord,
)
from ngv_ibkr_reports.config_helpers import (
    get_config,
    get_ib_json,
    get_discord_webhook_url,
)
from ngv_ibkr_reports.custom_flex_report import CustomFlexReport


def process_report_discord(report: CustomFlexReport, discord_webhook_url: str):
    """
    Process report through discord output adapter
    """
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
    """
    Fetch report. Optionally save to disk (helpful for debugging)

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
        logger.debug(f"save file to disk {report_path}")
        report.save(report_path)

    return report


def load_report(xml_file_path: str) -> CustomFlexReport:
    """
    Load CustomFlexReport from provided file path

    Args:
        xml_file_path (str): file path to the cached XML file

    Returns:
        CustomFlexReport: report
    """
    report = CustomFlexReport()
    report.load(xml_file_path)
    return report


def execute_csv_for_accounts(
    report_name: str, cache: bool = False, file_name: str = ".env"
):
    """
    Execute the trades dowload process for accounts

    Args:
        report_name (str): report name as it exists in the env file. Eg, report_name=xyz, in env file=IB_REPORT_ID_XYZ
        cache (bool): cache XML
        file_name (str): env file name. Defaults to ".env".

    """
    configs = get_config(file_name)
    data = get_ib_json(configs)

    if "accounts" not in data:
        return None

    for account in data["accounts"]:
        query_id = int(account[report_name.lower()])
        if query_id <= 0:
            logger.warning(f"{account['name']} does not have a {report_name} query_id")
            continue
        flex_token = account["flex_token"]
        report = fetch_report(flex_token, query_id, cache_report_on_disk=cache)
        output_adapter = ReportOutputAdapterCSV(data_folder="data", report=report)
        output_adapter.process_accounts()


def execute_discord_for_accounts(
    report_name: str, cache: bool = False, file_name: str = ".env"
) -> None:
    """
    Execute the discord notifications process for accounts

    .. deprecated::
        This function is deprecated and will be removed in a future version.

    Args:
        report_name (str): the report to execute. Expected options: daily, weekly, annual
        cache (bool, optional): save FlexReport XML to disk. Defaults to False.
        file_name (str, optional): env file name. Defaults to ".env".
    """
    warnings.warn(
        "execute_discord_for_accounts is deprecated and will be removed in a future version.",
        DeprecationWarning,
        stacklevel=2,
    )
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
