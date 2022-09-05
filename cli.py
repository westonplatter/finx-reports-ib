import click
from loguru import logger

from finx_reports_ib.download_trades import execute_csv_for_accounts


@click.group()
def core():
    pass


@core.command()
@click.option(
    "--report-name",
    default="annual",
    help="Report name use in the env file. Eg, 'IB_REPORT_ID_[report_name]'",
)
@click.option("--cache", default=False, is_flag=True, help="Cache XML file on disk")
def download(report_name: str, cache: bool):
    logger.info(f"Fetching IB Report (name={report_name})")
    execute_csv_for_accounts(report_name, cache=cache)


if __name__ == "__main__":
    core()
